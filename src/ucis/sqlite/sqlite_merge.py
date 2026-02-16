# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Coverage merge functionality for SQLite UCIS databases
"""

import sqlite3
import array
import concurrent.futures
from datetime import datetime
from ucis.history_node_kind import HistoryNodeKind
from ucis.scope_type_t import ScopeTypeT


class MergeConflict:
    """Represents a merge conflict"""
    def __init__(self, path: str, reason: str):
        self.path = path
        self.reason = reason


class MergeStats:
    """Statistics from a merge operation"""
    def __init__(self):
        self.scopes_matched = 0
        self.scopes_added = 0
        self.coveritems_matched = 0
        self.coveritems_added = 0
        self.total_hits_added = 0
        self.conflicts = []
        self.tests_merged = 0


class SqliteMerger:
    """Handles merging of UCIS databases"""
    
    def __init__(self, target_ucis):
        """
        Initialize merger
        
        Args:
            target_ucis: The target SqliteUCIS database to merge into
        """
        self.target = target_ucis
        self.stats = MergeStats()
        self._scope_path_cache = {}  # Cache of scope paths
        self._scope_match_cache = {}  # Cache source->target scope mappings
        self._src_tree = None  # Cached source scope tree
        self._tgt_tree = None  # Cached target scope tree
        self._tgt_coveritems = {}  # scope_id -> {cover_index -> [cover_id, count]}
        self._file_mapping = {}  # Cache of src_file_id -> tgt_file_id mapping
    
    def _load_scope_tree(self, db):
        """Load entire scope tree into memory in a single query."""
        tree = {}       # scope_id -> {name, type, parent_id, children: [scope_id]}
        children = {}   # parent_id -> [scope_id]
        root_id = None

        for row in db.conn.execute(
            "SELECT scope_id, parent_id, scope_type, scope_name FROM scopes"
        ):
            sid, pid, stype, sname = row
            tree[sid] = {"name": sname, "type": stype, "parent_id": pid, "children": []}
            children.setdefault(pid, []).append(sid)
            if pid is None:
                root_id = sid

        for sid, info in tree.items():
            info["children"] = children.get(sid, [])

        return tree, root_id

    def _find_matching_scope_fast(self, tgt_parent_id, src_scope_id):
        """Find matching target scope using cached trees (dict lookup)."""
        src = self._src_tree[src_scope_id]
        for tgt_child_id in self._tgt_tree[tgt_parent_id]["children"]:
            tgt = self._tgt_tree[tgt_child_id]
            if tgt["name"] == src["name"] and tgt["type"] == src["type"]:
                return tgt_child_id
        return None

    def _get_tgt_coveritems(self, scope_id):
        """Get cached target coveritem map, loading on first access."""
        if scope_id not in self._tgt_coveritems:
            m = {}
            for row in self.target.conn.execute(
                "SELECT cover_id, cover_index, cover_data FROM coveritems WHERE scope_id=?",
                (scope_id,)
            ):
                m[row[1]] = [row[0], row[2]]  # mutable list for in-place update
            self._tgt_coveritems[scope_id] = m
        return self._tgt_coveritems[scope_id]
    
    def _merge_files(self, source_ucis):
        """
        Merge files from source database into target.
        Builds a mapping of src_file_id -> tgt_file_id for remapping coveritem references.
        
        Args:
            source_ucis: Source database
            
        Returns:
            Dictionary mapping src_file_id -> tgt_file_id
        """
        # Only applies to SQLite sources
        if not hasattr(source_ucis, 'conn'):
            return {}
        
        file_mapping = {}
        
        # Query all files from source
        for row in source_ucis.conn.execute("SELECT file_id, file_path, file_hash FROM files"):
            src_file_id, file_path, file_hash = row
            
            # Check if file already exists in target
            tgt_cursor = self.target.conn.execute(
                "SELECT file_id FROM files WHERE file_path = ?",
                (file_path,)
            )
            tgt_row = tgt_cursor.fetchone()
            
            if tgt_row:
                # File exists, map to existing ID
                file_mapping[src_file_id] = tgt_row[0]
            else:
                # File doesn't exist, insert it
                insert_cursor = self.target.conn.execute(
                    "INSERT INTO files (file_path, file_hash) VALUES (?, ?)",
                    (file_path, file_hash)
                )
                file_mapping[src_file_id] = insert_cursor.lastrowid
        
        return file_mapping

    def merge(self, source_ucis, create_history: bool = True, squash_history: bool = False):
        """
        Merge source database into target database
        
        Supports both SqliteUCIS and MemUCIS sources.
        
        Args:
            source_ucis: Source database to merge from (SqliteUCIS or MemUCIS)
            create_history: Whether to create merge history node
            squash_history: If True, collapse per-test history into a summary node
            
        Returns:
            MergeStats object with merge statistics
        """
        self.stats = MergeStats()
        
        # Detect source type
        is_sqlite_source = hasattr(source_ucis, 'conn')
        
        # Start transaction for atomicity
        self.target.begin_transaction()
        
        try:
            # Create merge history node or find summary node
            merge_node = None
            if create_history:
                if squash_history:
                    # Find or create summary history node
                    summary_node = None
                    for node in self.target.historyNodes(HistoryNodeKind.MERGE):
                        if node.getLogicalName() == "merged_summary":
                            summary_node = node
                            break
                    
                    if summary_node is None:
                        # Create new summary node
                        summary_node = self.target.createHistoryNode(
                            None,
                            "merged_summary",
                            None,
                            HistoryNodeKind.MERGE
                        )
                        summary_node.setDate(int(datetime.now().timestamp()))
                        # Initialize test counter
                        cursor = self.target.conn.cursor()
                        cursor.execute(
                            "INSERT INTO history_properties (history_id, property_key, property_type, int_value) VALUES (?, ?, ?, ?)",
                            (summary_node.history_id, hash("TESTS_MERGED") & 0x7FFFFFFF, 0, 0)
                        )
                    
                    merge_node = summary_node
                    
                    # Increment test count
                    test_count = len(list(source_ucis.historyNodes(HistoryNodeKind.TEST)))
                    cursor = self.target.conn.cursor()
                    cursor.execute(
                        "UPDATE history_properties SET int_value = int_value + ? WHERE history_id = ? AND property_key = ?",
                        (test_count, merge_node.history_id, hash("TESTS_MERGED") & 0x7FFFFFFF)
                    )
                    self.stats.tests_merged += test_count
                    
                else:
                    # Create regular merge node with test history
                    merge_node = self.target.createHistoryNode(
                        None,
                        f"merge_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        None,
                        HistoryNodeKind.MERGE
                    )
                    merge_node.setDate(int(datetime.now().timestamp()))
                    
                    # Copy test history nodes from source
                    for src_test in source_ucis.historyNodes(HistoryNodeKind.TEST):
                        self._copy_history_node(src_test, merge_node)
                        self.stats.tests_merged += 1
            
            # Merge files and build mapping (for SQLite sources)
            if is_sqlite_source:
                self._file_mapping = self._merge_files(source_ucis)
            else:
                self._file_mapping = {}
            
            # Choose merge strategy based on source type
            if is_sqlite_source:
                # Fast path: SQL-based merge for SQLite sources
                self._src_tree, src_root = self._load_scope_tree(source_ucis)
                if self._tgt_tree is None:
                    self._tgt_tree, tgt_root = self._load_scope_tree(self.target)
                else:
                    tgt_root = self._tgt_root

                self._tgt_root = tgt_root

                # Merge scopes recursively using cached trees
                self._merge_scope_recursive_fast(source_ucis, src_root, tgt_root)
            else:
                # Slow path: API-based merge for MemUCIS sources
                self._merge_from_memucs(source_ucis)
            
            # Merge test-coveritem associations if both databases support it
            if not squash_history:
                self._merge_test_associations(source_ucis, create_history)
            
            # Commit transaction
            self.target.commit()
            
            return self.stats
            
        except Exception as e:
            # Rollback on error
            self.target.rollback()
            raise Exception(f"Merge failed: {e}") from e
    
    def merge_many(self, sources, create_history: bool = True, squash_history: bool = False):
        """
        Merge multiple source databases in a single transaction.

        Source scope trees are loaded once from the first source and reused
        when subsequent sources share the same structure (Fix 3 + Fix 4).

        Args:
            sources: Iterable of (source_ucis, close_after) tuples or plain
                     source_ucis objects.
            create_history: Whether to create merge history nodes.
            squash_history: If True, collapse per-test history into summary.

        Returns:
            MergeStats with accumulated statistics.
        """
        total = MergeStats()
        self._tgt_tree, self._tgt_root = self._load_scope_tree(self.target)

        self.target.begin_transaction()
        try:
            src_tree = None
            for src in sources:
                stats = self._merge_one(
                    src, create_history, squash_history, reuse_src_tree=src_tree
                )
                if src_tree is None:
                    src_tree = self._src_tree
                total.scopes_matched += stats.scopes_matched
                total.scopes_added += stats.scopes_added
                total.coveritems_matched += stats.coveritems_matched
                total.coveritems_added += stats.coveritems_added
                total.total_hits_added += stats.total_hits_added
                total.tests_merged += stats.tests_merged
                total.conflicts.extend(stats.conflicts)

            self.target.commit()
        except Exception:
            self.target.rollback()
            raise

        return total

    def _read_source(self, src_path, source_ids_match, scope_map, ci_map):
        """Read coveritem data from a source .cdb file.
        
        Args:
            src_path: Path to source database file
            source_ids_match: Whether source scope_ids match target
            scope_map: Dict mapping (scope_name, scope_type) to target scope_id
            ci_map: Dict mapping (scope_id, cover_index) to cover_id
            
        Returns:
            Tuple of (rows, stats_dict) where rows is list of coveritem data
            and stats_dict contains matched count and total hits
        """
        conn = sqlite3.connect(src_path)
        stats = {'matched': 0, 'hits': 0}
        deltas = {}
        
        if source_ids_match:
            # Direct scope_id lookup — skip JOIN
            rows = conn.execute(
                "SELECT scope_id, cover_index, cover_data FROM coveritems"
            ).fetchall()
            
            for row in rows:
                src_sid, cidx, cdata = row[0], row[1], row[2]
                tgt_cid = ci_map.get((src_sid, cidx))
                if tgt_cid is not None:
                    deltas[tgt_cid] = deltas.get(tgt_cid, 0) + cdata
                    stats['matched'] += 1
                    stats['hits'] += cdata
        else:
            # Use minimal 4-column read with JOIN
            rows = conn.execute("""
                SELECT ss.scope_name, ss.scope_type,
                       ci.cover_index, ci.cover_data
                FROM coveritems ci
                INNER JOIN scopes ss ON ci.scope_id = ss.scope_id
            """).fetchall()
            
            for row in rows:
                sname, stype = row[0], row[1]
                cidx, cdata = row[2], row[3]
                tgt_sid = scope_map.get((sname, stype))
                if tgt_sid is None:
                    continue
                
                tgt_cid = ci_map.get((tgt_sid, cidx))
                if tgt_cid is not None:
                    deltas[tgt_cid] = deltas.get(tgt_cid, 0) + cdata
                    stats['matched'] += 1
                    stats['hits'] += cdata
        
        conn.close()
        return deltas, stats

    def merge_fast(self, source_paths, squash_history=False, workers=4):
        """Merge multiple source databases using parallel reads and optimised accumulation.

        Opens sources in parallel using ThreadPoolExecutor, reads coveritem
        data, accumulates deltas using array-based storage for performance,
        and writes once via executemany.

        Args:
            source_paths: List of file paths to source .cdb databases.
            squash_history: If True, collapse history into summary node.
            workers: Number of parallel reader threads (default: 4).

        Returns:
            MergeStats with accumulated statistics.
        """
        # 1. Build target lookup maps (once)
        scope_map = {}     # (scope_name, scope_type) -> tgt_scope_id
        raw_cur = self.target.conn.execute(
            "SELECT scope_id, scope_name, scope_type FROM scopes"
        )
        for r in raw_cur:
            sid = r[0] if isinstance(r, (list, tuple)) else r['scope_id']
            sname = r[1] if isinstance(r, (list, tuple)) else r['scope_name']
            stype = r[2] if isinstance(r, (list, tuple)) else r['scope_type']
            scope_map[(sname, stype)] = sid

        ci_map = {}        # (tgt_scope_id, cover_index) -> cover_id
        raw_cur = self.target.conn.execute(
            "SELECT cover_id, scope_id, cover_index FROM coveritems"
        )
        for r in raw_cur:
            cid = r[0] if isinstance(r, (list, tuple)) else r['cover_id']
            sid = r[1] if isinstance(r, (list, tuple)) else r['scope_id']
            cidx = r[2] if isinstance(r, (list, tuple)) else r['cover_index']
            ci_map[(sid, cidx)] = cid

        # 2. Check if source scope_ids match target (first source only)
        source_ids_match = False
        if source_paths:
            first_conn = sqlite3.connect(source_paths[0])
            src_scopes = {}
            for sr in first_conn.execute(
                "SELECT scope_id, scope_name, scope_type FROM scopes"
            ):
                src_scopes[(sr[1], sr[2])] = sr[0]
            source_ids_match = all(
                src_scopes.get(k) == v
                for k, v in scope_map.items()
                if k[0]  # skip root with empty name
            ) and len(src_scopes) == len(scope_map)
            first_conn.close()

        # 3. Read ALL sources in parallel using ThreadPoolExecutor
        self.target.begin_transaction()
        try:
            # Create partial function with fixed arguments for _read_source
            from functools import partial
            read_func = partial(
                self._read_source,
                source_ids_match=source_ids_match,
                scope_map=scope_map,
                ci_map=ci_map
            )
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
                results = list(pool.map(read_func, source_paths))

            # 4. Accumulate deltas using array for performance (Step 2)
            if ci_map:
                max_cid = max(ci_map.values()) + 1
                deltas = array.array('q', [0] * max_cid)  # signed int64
                
                for result_deltas, stats_dict in results:
                    for cid, delta in result_deltas.items():
                        deltas[cid] += delta
                    self.stats.coveritems_matched += stats_dict['matched']
                    self.stats.total_hits_added += stats_dict['hits']
                    self.stats.tests_merged += 1
                
                # 5. Single batch UPDATE with non-zero deltas
                updates = [(int(deltas[cid]), cid) for cid in range(max_cid) if deltas[cid] != 0]
                if updates:
                    self.target.conn.executemany(
                        "UPDATE coveritems SET cover_data = cover_data + ? WHERE cover_id = ?",
                        updates
                    )
            else:
                # Empty ci_map - just count tests
                for result_deltas, stats_dict in results:
                    self.stats.coveritems_matched += stats_dict['matched']
                    self.stats.total_hits_added += stats_dict['hits']
                    self.stats.tests_merged += 1

            # 6. Handle history
            if squash_history:
                self._create_squash_summary(len(source_paths))
            else:
                for src_path in source_paths:
                    self._create_test_history_from_path(src_path)

            self.target.commit()
        except:
            self.target.rollback()
            raise

        return self.stats

    def _create_test_history_from_path(self, src_path):
        """Create a merge history node for a source file path."""
        import os
        merge_node = self.target.createHistoryNode(
            None,
            f"merge_{os.path.basename(src_path)}",
            None,
            HistoryNodeKind.MERGE
        )
        merge_node.setDate(int(datetime.now().timestamp()))

    def _create_squash_summary(self, num_sources):
        """Create or update a squashed summary history node."""
        summary_node = None
        for node in self.target.historyNodes(HistoryNodeKind.MERGE):
            if node.getLogicalName() == "merged_summary":
                summary_node = node
                break

        if summary_node is None:
            summary_node = self.target.createHistoryNode(
                None, "merged_summary", None, HistoryNodeKind.MERGE
            )
            summary_node.setDate(int(datetime.now().timestamp()))
            self.target.conn.execute(
                "INSERT INTO history_properties (history_id, property_key, property_type, int_value) VALUES (?, ?, ?, ?)",
                (summary_node.history_id, hash("TESTS_MERGED") & 0x7FFFFFFF, 0, 0)
            )

        self.target.conn.execute(
            "UPDATE history_properties SET int_value = int_value + ? WHERE history_id = ? AND property_key = ?",
            (num_sources, summary_node.history_id, hash("TESTS_MERGED") & 0x7FFFFFFF)
        )

    def _merge_one(self, source_ucis, create_history, squash_history,
                   reuse_src_tree=None):
        """Merge a single source inside an existing transaction."""
        self.stats = MergeStats()

        # History handling
        if create_history:
            if squash_history:
                summary_node = None
                for node in self.target.historyNodes(HistoryNodeKind.MERGE):
                    if node.getLogicalName() == "merged_summary":
                        summary_node = node
                        break

                if summary_node is None:
                    summary_node = self.target.createHistoryNode(
                        None, "merged_summary", None, HistoryNodeKind.MERGE
                    )
                    summary_node.setDate(int(datetime.now().timestamp()))
                    cursor = self.target.conn.cursor()
                    cursor.execute(
                        "INSERT INTO history_properties (history_id, property_key, property_type, int_value) VALUES (?, ?, ?, ?)",
                        (summary_node.history_id, hash("TESTS_MERGED") & 0x7FFFFFFF, 0, 0)
                    )

                test_count = len(list(source_ucis.historyNodes(HistoryNodeKind.TEST)))
                cursor = self.target.conn.cursor()
                cursor.execute(
                    "UPDATE history_properties SET int_value = int_value + ? WHERE history_id = ? AND property_key = ?",
                    (test_count, summary_node.history_id, hash("TESTS_MERGED") & 0x7FFFFFFF)
                )
                self.stats.tests_merged += test_count
            else:
                merge_node = self.target.createHistoryNode(
                    None,
                    f"merge_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    None,
                    HistoryNodeKind.MERGE
                )
                merge_node.setDate(int(datetime.now().timestamp()))
                for src_test in source_ucis.historyNodes(HistoryNodeKind.TEST):
                    self._copy_history_node(src_test, merge_node)
                    self.stats.tests_merged += 1

        # Reuse source tree if provided (Fix 4)
        if reuse_src_tree is not None:
            self._src_tree = reuse_src_tree
            # Find root from the cached tree
            for sid, info in self._src_tree.items():
                if info["parent_id"] is None:
                    src_root = sid
                    break
        else:
            self._src_tree, src_root = self._load_scope_tree(source_ucis)

        tgt_root = self._tgt_root
        self._merge_scope_recursive_fast(source_ucis, src_root, tgt_root)
        
        # Merge test associations if not squashing history
        if not squash_history:
            self._merge_test_associations(source_ucis, create_history)

        return self.stats

    def _copy_history_node(self, src_node, merge_parent):
        """Copy a history node from source to target"""
        # Check if test already exists (by logical name)
        existing = None
        for tgt_test in self.target.historyNodes(HistoryNodeKind.TEST):
            if tgt_test.getLogicalName() == src_node.getLogicalName():
                existing = tgt_test
                break
        
        if existing:
            # Test already exists, just return it
            return existing
        
        # Create new test node
        new_node = self.target.createHistoryNode(
            merge_parent,
            src_node.getLogicalName(),
            src_node.getPhysicalName(),
            src_node.getKind()
        )
        
        # Copy metadata
        new_node.setTestStatus(src_node.getTestStatus())
        new_node.setSeed(src_node.getSeed())
        new_node.setCmd(src_node.getCmd())
        new_node.setCpuTime(src_node.getCpuTime())
        new_node.setDate(src_node.getDate())
        new_node.setUserName(src_node.getUserName())
        
        return new_node
    
    def _merge_from_memucs(self, source_ucis):
        """
        Merge from MemUCIS using UCIS API (not SQL).
        
        This is slower than SQL-based merge but works with MemUCIS sources.
        Uses the same approach as DbMerger but integrates into SqliteMerger.
        """
        from ucis.scope_type_t import ScopeTypeT
        
        # Iterate through instance scopes (top-level scopes)
        for src_iscope in source_ucis.scopes(ScopeTypeT.INSTANCE):
            # Find or create matching instance in target
            tgt_iscope = self._find_or_create_instance(src_iscope)
            
            # Merge the instance and its children
            self._merge_scope_recursive_api(src_iscope, tgt_iscope)
    
    def _find_or_create_instance(self, src_iscope):
        """
        Find or create an instance scope in the target database.
        
        Args:
            src_iscope: Source instance scope
            
        Returns:
            Target instance scope
        """
        from ucis.scope_type_t import ScopeTypeT
        
        # Look for matching instance in target
        src_name = src_iscope.getScopeName()
        for tgt_scope in self.target.scopes(ScopeTypeT.INSTANCE):
            if tgt_scope.getScopeName() == src_name:
                self.stats.scopes_matched += 1
                return tgt_scope
        
        # Create new instance with its design unit
        src_du = src_iscope.getInstanceDu()
        
        # Create design unit
        from ucis import UCIS_OTHER, UCIS_DU_MODULE, UCIS_INSTANCE, UCIS_INST_ONCE, UCIS_SCOPE_UNDER_DU
        from ucis import UCIS_ENABLED_STMT, UCIS_ENABLED_BRANCH, UCIS_ENABLED_TOGGLE
        
        tgt_du = self.target.createScope(
            src_du.getScopeName(),
            src_du.getSourceInfo(),
            src_du.getWeight(),
            UCIS_OTHER,
            UCIS_DU_MODULE,
            UCIS_ENABLED_STMT | UCIS_ENABLED_BRANCH | UCIS_ENABLED_TOGGLE | UCIS_INST_ONCE | UCIS_SCOPE_UNDER_DU
        )
        
        # Create instance
        tgt_iscope = self.target.createInstance(
            src_iscope.getScopeName(),
            src_iscope.getSourceInfo(),
            1,  # weight
            UCIS_OTHER,
            UCIS_INSTANCE,
            tgt_du,
            UCIS_INST_ONCE
        )
        
        self.stats.scopes_added += 2  # DU + Instance
        return tgt_iscope
    
    def _merge_scope_recursive_api(self, src_scope, tgt_scope):
        """
        Recursively merge scopes using UCIS API instead of SQL.
        
        Args:
            src_scope: Source scope (from MemUCIS)
            tgt_scope: Target scope (in SqliteUCIS)
        """
        # Merge coveritems at this level
        self._merge_coveritems_api(src_scope, tgt_scope)
        
        # Process child scopes - use scopes() method
        child_scopes = []
        if hasattr(src_scope, 'scopes'):
            # MemUCIS uses scopes(mask) - use -1 to get all
            child_scopes = list(src_scope.scopes(-1))
        elif hasattr(src_scope, 'getScopes'):
            child_scopes = list(src_scope.getScopes())
        
        for src_child in child_scopes:
            src_name = src_child.getScopeName()
            src_type = src_child.getScopeType()
            
            # Find or create matching child in target
            tgt_child = None
            tgt_children = []
            if hasattr(tgt_scope, 'scopes'):
                # SqliteUCIS also uses scopes(mask)
                tgt_children = list(tgt_scope.scopes(-1))
            elif hasattr(tgt_scope, 'getScopes'):
                tgt_children = list(tgt_scope.getScopes())
            
            for tgt_c in tgt_children:
                if tgt_c.getScopeName() == src_name and tgt_c.getScopeType() == src_type:
                    tgt_child = tgt_c
                    break
            
            if tgt_child is None:
                # Create new scope in target
                # Try to get flags, but default to 0 if not implemented
                flags = 0
                try:
                    if hasattr(src_child, 'getFlags'):
                        flags = src_child.getFlags()
                except NotImplementedError:
                    flags = 0
                
                # Try to get source type, default to 0 if not available
                source_type = 0
                try:
                    if hasattr(src_child, 'getSourceType'):
                        source_type = src_child.getSourceType()
                except (NotImplementedError, AttributeError):
                    source_type = 0
                
                # Create scope on parent (not passing parent as argument)
                tgt_child = tgt_scope.createScope(
                    src_name,
                    src_child.getSourceInfo(),
                    src_child.getWeight(),
                    source_type,
                    src_type,
                    flags
                )
                tgt_child.setGoal(src_child.getGoal())
                self.stats.scopes_added += 1
            else:
                self.stats.scopes_matched += 1
            
            # Recursively merge child scopes
            self._merge_scope_recursive_api(src_child, tgt_child)
    
    def _merge_coveritems_api(self, src_scope, tgt_scope):
        """
        Merge coverage items using UCIS API instead of SQL.
        
        Args:
            src_scope: Source scope (from MemUCIS)
            tgt_scope: Target scope (in SqliteUCIS)
        """
        # Build map of target coveritems by index
        tgt_map = {}  # cover_index -> (cover_id, cover_data)
        
        # For SqliteUCIS, we can use SQL for target lookup (it's always SQLite)
        if hasattr(tgt_scope, 'scope_id'):
            for row in self.target.conn.execute(
                """SELECT cover_id, cover_index, cover_data
                   FROM coveritems WHERE scope_id = ?""",
                (tgt_scope.scope_id,)
            ):
                tgt_map[row[1]] = (row[0], row[2])
        
        # Process source coveritems using API
        updates = []  # (new_count, cover_id)
        inserts = []  # (scope_id, cover_index, ...)
        next_index = max(tgt_map.keys(), default=-1) + 1
        
        # Get coveritems - try both methods
        src_items = []
        if hasattr(src_scope, 'coverItems'):
            # MemUCIS uses coverItems(mask) - use -1 to get all
            src_items = list(src_scope.coverItems(-1))
        elif hasattr(src_scope, 'getCoverage'):
            src_items = list(src_scope.getCoverage())
        
        for src_cover in src_items:
            # Get cover index - try different methods
            src_index = None
            if hasattr(src_cover, 'cover_index'):
                src_index = src_cover.cover_index
            elif hasattr(src_cover, 'getCoverIndex'):
                src_index = src_cover.getCoverIndex()
            
            # If no index, assign sequential
            if src_index is None:
                src_index = next_index
                next_index += 1
            
            # Get hit count
            cover_data = src_cover.getCoverData()
            src_count = cover_data.data if cover_data else 1
            
            if src_index in tgt_map:
                # Update existing
                tgt_id, tgt_count = tgt_map[src_index]
                updates.append((tgt_count + src_count, tgt_id))
                self.stats.coveritems_matched += 1
                self.stats.total_hits_added += src_count
            else:
                # Insert new - get attributes from CoverData when available
                cover_type = cover_data.type if cover_data else 0
                cover_flags = cover_data.flags if cover_data else 0
                at_least = cover_data.goal if (cover_data and hasattr(cover_data, 'goal')) else 1
                weight = cover_data.weight if (cover_data and hasattr(cover_data, 'weight')) else 1
                goal = cover_data.goal if (cover_data and hasattr(cover_data, 'goal')) else 100
                limit_val = cover_data.limit if (cover_data and hasattr(cover_data, 'limit')) else 0
                
                # Get source info if available
                source_file_id = None
                source_line = 0
                source_token = None
                if hasattr(src_cover, 'getSourceInfo'):
                    src_info = src_cover.getSourceInfo()
                    if src_info and src_info.file:
                        # Get file path and find/create in target
                        file_path = src_info.file.getFileName()
                        if file_path:
                            # Check if file exists in target
                            cursor = self.target.conn.execute(
                                "SELECT file_id FROM files WHERE file_path = ?",
                                (file_path,)
                            )
                            row = cursor.fetchone()
                            if row:
                                source_file_id = row[0]
                            else:
                                # Create file in target
                                cursor = self.target.conn.execute(
                                    "INSERT INTO files (file_path) VALUES (?)",
                                    (file_path,)
                                )
                                source_file_id = cursor.lastrowid
                        source_line = src_info.line if hasattr(src_info, 'line') else 0
                        source_token = src_info.token if hasattr(src_info, 'token') else 0
                
                inserts.append((
                    tgt_scope.scope_id,
                    src_index,
                    cover_type,
                    src_cover.getName(),
                    src_count,
                    cover_flags,
                    at_least,
                    weight,
                    goal,
                    limit_val,
                    source_file_id,
                    source_line,
                    source_token,
                ))
                self.stats.coveritems_added += 1
                self.stats.total_hits_added += src_count
        
        # Execute SQL updates/inserts
        if updates:
            self.target.conn.executemany(
                "UPDATE coveritems SET cover_data = ? WHERE cover_id = ?",
                updates
            )
        
        if inserts:
            self.target.conn.executemany(
                """INSERT INTO coveritems
                   (scope_id, cover_index, cover_type, cover_name,
                    cover_data, cover_flags, at_least, weight,
                    goal, limit_val, source_file_id, source_line,
                    source_token)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                inserts
            )
    
    def _get_scope_path(self, scope):
        """Get hierarchical path for a scope"""
        # Check if it's a SQLite scope with scope_id (cacheable)
        if hasattr(scope, 'scope_id') and scope.scope_id in self._scope_path_cache:
            return self._scope_path_cache[scope.scope_id]
        
        parts = []
        current = scope
        
        # Walk up the hierarchy
        while current is not None:
            name = current.getScopeName()
            scope_type = current.getScopeType()
            
            if name:  # Skip root with empty name
                parts.append((name, scope_type))
            
            # Get parent - different for SQLite vs MemUCIS
            if hasattr(current, '_ensure_loaded') and hasattr(current, '_parent_id'):
                # SQLite scope
                current._ensure_loaded()
                if current._parent_id is not None:
                    from ucis.sqlite.sqlite_scope import SqliteScope
                    current = SqliteScope(current.ucis_db, current._parent_id)
                else:
                    current = None
            elif hasattr(current, 'm_parent'):
                # MemUCIS scope
                current = current.m_parent
            else:
                # Root scope
                current = None
        
        # Reverse to get root-to-leaf path
        path = tuple(reversed(parts))
        
        # Only cache if it has scope_id (SQLite scopes)
        if hasattr(scope, 'scope_id'):
            self._scope_path_cache[scope.scope_id] = path
        
        return path
    
    def _find_matching_scope(self, target_parent, src_scope):
        """Find matching scope in target under given parent"""
        cache_key = (target_parent.scope_id, src_scope.scope_id)
        if cache_key in self._scope_match_cache:
            return self._scope_match_cache[cache_key]
        
        src_name = src_scope.getScopeName()
        src_type = src_scope.getScopeType()
        
        # Search for matching child
        for child in target_parent.scopes(-1):
            if (child.getScopeName() == src_name and 
                child.getScopeType() == src_type):
                self._scope_match_cache[cache_key] = child
                return child
        
        return None
    
    def _merge_scope_recursive(self, src_scope, tgt_scope):
        """Recursively merge scopes and coverage"""
        
        # Merge coverage items for this scope
        self._merge_coveritems(src_scope, tgt_scope)
        
        # Recursively merge child scopes
        for src_child in src_scope.scopes(-1):
            # Try to find matching child in target
            tgt_child = self._find_matching_scope(tgt_scope, src_child)
            
            if tgt_child is None:
                # No match found, create new scope
                tgt_child = self._copy_scope(src_child, tgt_scope)
                self.stats.scopes_added += 1
            else:
                self.stats.scopes_matched += 1
            
            # Recursively merge children
            self._merge_scope_recursive(src_child, tgt_child)

    def _merge_scope_recursive_fast(self, source_ucis, src_scope_id, tgt_scope_id):
        """Recursively merge scopes using cached trees (Fix 1)."""

        # Merge coverage items for this scope
        self._merge_coveritems_fast(source_ucis, src_scope_id, tgt_scope_id)

        # Recursively merge child scopes via dict lookups
        for src_child_id in self._src_tree[src_scope_id]["children"]:
            tgt_child_id = self._find_matching_scope_fast(tgt_scope_id, src_child_id)

            if tgt_child_id is None:
                # No match — create new scope in target DB and update cached tree
                tgt_child_id = self._copy_scope_fast(source_ucis, src_child_id, tgt_scope_id)
                self.stats.scopes_added += 1
            else:
                self.stats.scopes_matched += 1

            self._merge_scope_recursive_fast(source_ucis, src_child_id, tgt_child_id)
    
    def _copy_scope(self, src_scope, tgt_parent):
        """Create a copy of source scope under target parent"""
        return tgt_parent.createScope(
            src_scope.getScopeName(),
            src_scope.getSourceInfo(),
            src_scope.getWeight(),
            0,  # source
            src_scope.getScopeType(),
            src_scope.getFlags()
        )

    def _copy_scope_fast(self, source_ucis, src_scope_id, tgt_parent_id):
        """Create a copy of source scope under target parent using cached tree."""
        src = self._src_tree[src_scope_id]
        from ucis.sqlite.sqlite_scope import SqliteScope
        parent_scope = SqliteScope(self.target, tgt_parent_id)
        new_scope = parent_scope.createScope(
            src["name"], None, 1, 0, src["type"], 0
        )
        new_id = new_scope.scope_id
        # Update the target tree cache
        self._tgt_tree[new_id] = {
            "name": src["name"],
            "type": src["type"],
            "parent_id": tgt_parent_id,
            "children": [],
        }
        self._tgt_tree[tgt_parent_id]["children"].append(new_id)
        return new_id
    
    def _merge_coveritems(self, src_scope, tgt_scope):
        """Merge coverage items using bulk queries."""

        # 1. Bulk-fetch ALL target coveritems in one query
        tgt_map = {}  # cover_index → (cover_id, cover_data)
        for row in self.target.conn.execute(
            """SELECT cover_id, cover_index, cover_data
               FROM coveritems WHERE scope_id = ?""",
            (tgt_scope.scope_id,)
        ):
            tgt_map[row[1]] = (row[0], row[2])

        # 2. Bulk-fetch ALL source coveritems in one query
        src_rows = list(src_scope.ucis_db.conn.execute(
            """SELECT cover_index, cover_type, cover_name, cover_data,
                      cover_flags, at_least, weight, goal, limit_val,
                      source_file_id, source_line, source_token
               FROM coveritems WHERE scope_id = ?""",
            (src_scope.scope_id,)
        ))

        # 3. Separate into updates vs inserts
        updates = []   # (new_count, cover_id)
        inserts = []   # full row tuples for new items
        next_index = max(tgt_map.keys(), default=-1) + 1

        for row in src_rows:
            src_index = row[0]
            src_count = row[3]

            if src_index in tgt_map:
                tgt_id, tgt_count = tgt_map[src_index]
                updates.append((tgt_count + src_count, tgt_id))
                self.stats.coveritems_matched += 1
                self.stats.total_hits_added += src_count
            else:
                # Remap source_file_id if file mapping exists
                src_file_id = row[9]
                mapped_file_id = None
                if src_file_id is not None and src_file_id in self._file_mapping:
                    mapped_file_id = self._file_mapping[src_file_id]
                
                inserts.append((
                    tgt_scope.scope_id, next_index,
                    row[1],   # cover_type
                    row[2],   # cover_name
                    src_count, # cover_data
                    row[4],   # cover_flags
                    row[5],   # at_least
                    row[6],   # weight
                    row[7],   # goal
                    row[8],   # limit_val
                    mapped_file_id,  # source_file_id (remapped via file_mapping)
                    row[10],  # source_line
                    row[11],  # source_token
                ))
                next_index += 1
                self.stats.coveritems_added += 1
                self.stats.total_hits_added += src_count

        # 4. Batch UPDATE existing items
        if updates:
            self.target.conn.executemany(
                "UPDATE coveritems SET cover_data = ? WHERE cover_id = ?",
                updates
            )

        # 5. Batch INSERT new items
        if inserts:
            self.target.conn.executemany(
                """INSERT INTO coveritems
                   (scope_id, cover_index, cover_type, cover_name,
                    cover_data, cover_flags, at_least, weight,
                    goal, limit_val, source_file_id, source_line,
                    source_token)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                inserts
            )

    def _merge_coveritems_fast(self, source_ucis, src_scope_id, tgt_scope_id):
        """Merge coverage items using cached target map (Fix 2)."""

        # Get (or build on first access) cached target coveritems
        tgt_map = self._get_tgt_coveritems(tgt_scope_id)

        # Bulk-fetch source coveritems
        src_rows = list(source_ucis.conn.execute(
            """SELECT cover_index, cover_type, cover_name, cover_data,
                      cover_flags, at_least, weight, goal, limit_val,
                      source_file_id, source_line, source_token
               FROM coveritems WHERE scope_id = ?""",
            (src_scope_id,)
        ))

        updates = []   # (new_count, cover_id)
        inserts = []
        next_index = max(tgt_map.keys(), default=-1) + 1

        for row in src_rows:
            src_index = row[0]
            src_count = row[3]

            if src_index in tgt_map:
                tgt_entry = tgt_map[src_index]
                new_count = tgt_entry[1] + src_count
                updates.append((new_count, tgt_entry[0]))
                tgt_entry[1] = new_count  # update cache in-place
                self.stats.coveritems_matched += 1
                self.stats.total_hits_added += src_count
            else:
                # Remap source_file_id using file mapping
                src_file_id = row[9]
                mapped_file_id = None
                if src_file_id is not None and src_file_id in self._file_mapping:
                    mapped_file_id = self._file_mapping[src_file_id]
                
                inserts.append((
                    tgt_scope_id, next_index,
                    row[1], row[2], src_count,
                    row[4], row[5], row[6], row[7], row[8],
                    mapped_file_id, row[10], row[11],
                ))
                next_index += 1
                self.stats.coveritems_added += 1
                self.stats.total_hits_added += src_count

        if updates:
            self.target.conn.executemany(
                "UPDATE coveritems SET cover_data = ? WHERE cover_id = ?",
                updates
            )

        if inserts:
            cursor = self.target.conn.executemany(
                """INSERT INTO coveritems
                   (scope_id, cover_index, cover_type, cover_name,
                    cover_data, cover_flags, at_least, weight,
                    goal, limit_val, source_file_id, source_line,
                    source_token)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                inserts
            )
            # Update cache with newly inserted items
            for ins in inserts:
                # Re-query to get cover_id for newly inserted row
                row = self.target.conn.execute(
                    "SELECT cover_id FROM coveritems WHERE scope_id=? AND cover_index=?",
                    (tgt_scope_id, ins[1])
                ).fetchone()
                if row:
                    tgt_map[ins[1]] = [row[0], ins[4]]

    def _merge_coveritems_attached(self, source_ucis, scope_mapping):
        """
        Merge coveritems using ATTACH DATABASE for pure-SQL performance (Fix 5).
        
        Only works for file-based SQLite databases.
        """
        src_path = getattr(source_ucis, 'db_path', None)
        if not src_path or src_path == ":memory:":
            return False
        if self.target.db_path == ":memory:":
            return False

        self.target.conn.execute("ATTACH DATABASE ? AS merge_src", (src_path,))
        try:
            # Build temp scope mapping table
            self.target.conn.execute("""
                CREATE TEMP TABLE IF NOT EXISTS _merge_scope_map (
                    src_scope_id INTEGER PRIMARY KEY,
                    tgt_scope_id INTEGER NOT NULL
                )
            """)
            self.target.conn.execute("DELETE FROM _merge_scope_map")

            for src_id, tgt_id in scope_mapping.items():
                self.target.conn.execute(
                    "INSERT INTO _merge_scope_map VALUES (?,?)", (src_id, tgt_id)
                )

            # Update existing coveritems (accumulate counts)
            result = self.target.conn.execute("""
                UPDATE coveritems SET cover_data = cover_data + (
                    SELECT src_ci.cover_data
                    FROM merge_src.coveritems src_ci
                    INNER JOIN _merge_scope_map sm ON src_ci.scope_id = sm.src_scope_id
                    WHERE coveritems.scope_id = sm.tgt_scope_id
                      AND coveritems.cover_index = src_ci.cover_index
                )
                WHERE EXISTS (
                    SELECT 1 FROM merge_src.coveritems src_ci
                    INNER JOIN _merge_scope_map sm ON src_ci.scope_id = sm.src_scope_id
                    WHERE coveritems.scope_id = sm.tgt_scope_id
                      AND coveritems.cover_index = src_ci.cover_index
                )
            """)
            self.stats.coveritems_matched += result.rowcount

            # Insert new coveritems
            result = self.target.conn.execute("""
                INSERT INTO coveritems (
                    scope_id, cover_index, cover_type, cover_name,
                    cover_data, cover_flags, at_least, weight,
                    goal, limit_val, source_file_id, source_line, source_token
                )
                SELECT
                    sm.tgt_scope_id,
                    src_ci.cover_index,
                    src_ci.cover_type,
                    src_ci.cover_name,
                    src_ci.cover_data,
                    src_ci.cover_flags,
                    src_ci.at_least,
                    src_ci.weight,
                    src_ci.goal,
                    src_ci.limit_val,
                    src_ci.source_file_id,
                    src_ci.source_line,
                    src_ci.source_token
                FROM merge_src.coveritems src_ci
                INNER JOIN _merge_scope_map sm ON src_ci.scope_id = sm.src_scope_id
                WHERE NOT EXISTS (
                    SELECT 1 FROM coveritems tgt_ci
                    WHERE tgt_ci.scope_id = sm.tgt_scope_id
                      AND tgt_ci.cover_index = src_ci.cover_index
                )
            """)
            self.stats.coveritems_added += result.rowcount

            # Invalidate coveritem cache for affected scopes
            for tgt_id in scope_mapping.values():
                self._tgt_coveritems.pop(tgt_id, None)

            self.target.conn.execute("DROP TABLE IF EXISTS _merge_scope_map")
        finally:
            try:
                self.target.conn.execute("DETACH DATABASE merge_src")
            except Exception:
                pass

        return True

    def _merge_test_associations(self, source_ucis, create_history: bool):
        """
        Merge test-coveritem associations from source to target.
        
        For SQLite→SQLite: Copies associations from coveritem_tests table.
        For MemUCIS→SQLite: Automatically associates all coveritems with all tests 
                           (assumes each test covers everything it imports).
        
        Args:
            source_ucis: Source database with test associations
            create_history: Whether history nodes were created/copied during merge
        """
        # Only proceed if target is SQLite (has test coverage support)
        if not hasattr(self.target, 'conn'):
            return
        
        # Check if source is SQLite or MemUCIS
        is_source_sqlite = hasattr(source_ucis, 'conn')
        
        if is_source_sqlite:
            self._merge_test_associations_sqlite_to_sqlite(source_ucis, create_history)
        else:
            self._merge_test_associations_mem_to_sqlite(source_ucis, create_history)
    
    def _merge_test_associations_mem_to_sqlite(self, source_ucis, create_history: bool):
        """
        Create test associations when merging from MemUCIS to SQLite.
        
        Assumes all coveritems in the source were covered by all tests in the source,
        which is the typical case when importing coverage data.
        """
        # Get all test history nodes from source
        source_tests = list(source_ucis.historyNodes(HistoryNodeKind.TEST))
        if not source_tests:
            # No tests to associate
            return
        
        # Find matching tests in target by logical name
        target_tests = {}
        for src_test in source_tests:
            src_name = src_test.getLogicalName()
            for tgt_test in self.target.historyNodes(HistoryNodeKind.TEST):
                if tgt_test.getLogicalName() == src_name:
                    target_tests[src_name] = tgt_test.history_id
                    break
        
        if not target_tests:
            # No matching tests found
            return
        
        # Get all coveritems in target that were just merged
        # We need to find coveritems that match the source structure
        associations_to_insert = []
        
        # Iterate through source scopes and find matching target scopes
        def process_scope(src_scope):
            # Get scope path
            src_path = self._get_scope_path(src_scope)
            
            # Find matching target scope
            tgt_scope = self._find_scope_by_path(self.target, src_path)
            if not tgt_scope:
                return
            
            # Get coveritems from source - try both methods
            src_coveritems = []
            if hasattr(src_scope, 'coverItems'):
                src_coveritems = list(src_scope.coverItems(-1))  # -1 = all types
            elif hasattr(src_scope, 'getCoverage'):
                src_coveritems = list(src_scope.getCoverage())
            
            # For each coveritem in source scope, find matching in target
            for src_cover in src_coveritems:
                # Get source item name
                src_name = src_cover.getName()
                
                # Get target coveritems - try both methods
                tgt_coveritems = []
                if hasattr(tgt_scope, 'coverItems'):
                    tgt_coveritems = list(tgt_scope.coverItems(-1))  # -1 = all types
                elif hasattr(tgt_scope, 'getCoverage'):
                    tgt_coveritems = list(tgt_scope.getCoverage())
                
                # Find target coveritem by name (more reliable than cover_index for MemUCIS)
                tgt_cover = None
                for tc in tgt_coveritems:
                    if tc.getName() == src_name:
                        tgt_cover = tc
                        break
                
                if tgt_cover and hasattr(tgt_cover, 'cover_id'):
                    # Get hit count as contribution
                    cover_data = src_cover.getCoverData()
                    contribution = cover_data.data if cover_data else 1
                    
                    # Associate with all tests
                    for test_name, tgt_history_id in target_tests.items():
                        associations_to_insert.append((
                            tgt_cover.cover_id, 
                            tgt_history_id, 
                            contribution
                        ))
            
            # Process child scopes - try both methods
            child_scopes = []
            if hasattr(src_scope, 'scopes'):
                child_scopes = list(src_scope.scopes(-1))  # -1 = all types
            elif hasattr(src_scope, 'getScopes'):
                child_scopes = list(src_scope.getScopes())
            
            for child in child_scopes:
                process_scope(child)
        
        # Start from root - MemUCIS IS the root scope
        src_root = source_ucis
        if hasattr(source_ucis, 'getRoot'):
            src_root = source_ucis.getRoot()
        
        if src_root:
            process_scope(src_root)
        
        # Batch insert associations
        if associations_to_insert:
            # Remove duplicates and handle existing associations
            for cover_id, history_id, contribution in associations_to_insert:
                existing = self.target.conn.execute("""
                    SELECT count_contribution FROM coveritem_tests
                    WHERE cover_id = ? AND history_id = ?
                """, (cover_id, history_id)).fetchone()
                
                if existing:
                    # Update existing
                    new_count = existing[0] + contribution
                    self.target.conn.execute("""
                        UPDATE coveritem_tests
                        SET count_contribution = ?
                        WHERE cover_id = ? AND history_id = ?
                    """, (new_count, cover_id, history_id))
                else:
                    # Insert new
                    self.target.conn.execute("""
                        INSERT INTO coveritem_tests (cover_id, history_id, count_contribution)
                        VALUES (?, ?, ?)
                    """, (cover_id, history_id, contribution))
    
    def _merge_test_associations_sqlite_to_sqlite(self, source_ucis, create_history: bool):
        """
        Copy test associations when merging from SQLite to SQLite.
        """
        # Check if source has any test associations to copy
        src_assoc_count = source_ucis.conn.execute(
            "SELECT COUNT(*) FROM coveritem_tests"
        ).fetchone()[0]
        
        if src_assoc_count == 0:
            return
        
        # Build mapping from source history nodes to target history nodes
        # by matching on logical name (test name)
        history_map = {}  # src_history_id -> tgt_history_id
        
        for src_test in source_ucis.historyNodes(HistoryNodeKind.TEST):
            src_name = src_test.getLogicalName()
            # Find matching target test by name
            for tgt_test in self.target.historyNodes(HistoryNodeKind.TEST):
                if tgt_test.getLogicalName() == src_name:
                    history_map[src_test.history_id] = tgt_test.history_id
                    break
        
        if not history_map:
            # No matching tests found
            return
        
        # Build mapping from source coveritems to target coveritems
        # Format: (src_scope_id, src_cover_index) -> tgt_cover_id
        coveritem_map = {}
        
        # Get all source coveritems with their scope_id and cover_index
        src_coveritems = source_ucis.conn.execute("""
            SELECT cover_id, scope_id, cover_index
            FROM coveritems
        """).fetchall()
        
        for src_cover_id, src_scope_id, src_cover_index in src_coveritems:
            # Find the target scope that corresponds to this source scope
            # Create SqliteScope from scope_id
            from ucis.sqlite.sqlite_scope import SqliteScope
            src_scope = SqliteScope(source_ucis, src_scope_id)
            
            # Get the scope path
            src_path = self._get_scope_path(src_scope)
            
            # Find matching target scope by path
            tgt_scope = self._find_scope_by_path(self.target, src_path)
            if not tgt_scope:
                continue
            
            # Find target coveritem with same cover_index in target scope
            tgt_result = self.target.conn.execute("""
                SELECT cover_id FROM coveritems
                WHERE scope_id = ? AND cover_index = ?
            """, (tgt_scope.scope_id, src_cover_index)).fetchone()
            
            if tgt_result:
                coveritem_map[(src_scope_id, src_cover_index)] = tgt_result[0]
        
        if not coveritem_map:
            # No matching coveritems found
            return
        
        # Now copy the test associations with mapped IDs
        associations_to_insert = []
        
        src_associations = source_ucis.conn.execute("""
            SELECT cover_id, history_id, count_contribution
            FROM coveritem_tests
        """).fetchall()
        
        for src_cover_id, src_history_id, count_contrib in src_associations:
            # Map history ID
            if src_history_id not in history_map:
                continue
            tgt_history_id = history_map[src_history_id]
            
            # Map coveritem ID - need to find scope_id and cover_index first
            src_ci = source_ucis.conn.execute("""
                SELECT scope_id, cover_index
                FROM coveritems WHERE cover_id = ?
            """, (src_cover_id,)).fetchone()
            
            if not src_ci:
                continue
            
            src_scope_id, src_cover_index = src_ci
            key = (src_scope_id, src_cover_index)
            
            if key not in coveritem_map:
                continue
            tgt_cover_id = coveritem_map[key]
            
            # Check if association already exists
            existing = self.target.conn.execute("""
                SELECT count_contribution FROM coveritem_tests
                WHERE cover_id = ? AND history_id = ?
            """, (tgt_cover_id, tgt_history_id)).fetchone()
            
            if existing:
                # Update existing - add contribution counts
                new_count = existing[0] + count_contrib
                self.target.conn.execute("""
                    UPDATE coveritem_tests
                    SET count_contribution = ?
                    WHERE cover_id = ? AND history_id = ?
                """, (new_count, tgt_cover_id, tgt_history_id))
            else:
                # Insert new association
                associations_to_insert.append((
                    tgt_cover_id, tgt_history_id, count_contrib
                ))
        
        # Batch insert new associations
        if associations_to_insert:
            self.target.conn.executemany("""
                INSERT INTO coveritem_tests (cover_id, history_id, count_contribution)
                VALUES (?, ?, ?)
            """, associations_to_insert)
    
    def _find_scope_by_path(self, ucis, path):
        """Find a scope in the database by its hierarchical path."""
        if not path:
            # Return root - in PyUCIS, the database IS the root scope
            return ucis
        
        # Start from root - database IS the root
        current = ucis
        for name, scope_type in path:
            found = False
            # Get child scopes - use scopes() if available (SqliteUCIS)
            children = []
            if hasattr(current, 'scopes'):
                children = list(current.scopes(-1))
            elif hasattr(current, 'getScopes'):
                children = list(current.getScopes())
            
            for child in children:
                if child.getScopeName() == name and child.getScopeType() == scope_type:
                    current = child
                    found = True
                    break
            if not found:
                return None
        
        return current


def merge_databases(target_path: str, source_paths: list, 
                   output_path: str = None, squash_history: bool = False) -> MergeStats:
    """
    Convenience function to merge multiple databases
    
    Args:
        target_path: Path to target database (base)
        source_paths: List of paths to source databases to merge
        output_path: Optional output path (if None, modifies target in-place)
        squash_history: If True, collapse per-test history into a summary node
        
    Returns:
        MergeStats from the merge operation
    """
    from ucis.sqlite import SqliteUCIS
    import shutil
    
    # Copy target if output path specified
    if output_path and output_path != target_path:
        shutil.copy2(target_path, output_path)
        target_path = output_path
    
    # Open target
    target = SqliteUCIS(target_path)
    merger = SqliteMerger(target)
    
    # Open all sources and use merge_many for single-transaction merge
    sources = []
    try:
        for src_path in source_paths:
            sources.append(SqliteUCIS.open_readonly(src_path))
        
        total_stats = merger.merge_many(
            sources, squash_history=squash_history
        )
    finally:
        for src in sources:
            src.close()
        target.close()
    
    return total_stats
