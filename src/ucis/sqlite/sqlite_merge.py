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

    def merge(self, source_ucis, create_history: bool = True, squash_history: bool = False):
        """
        Merge source database into target database
        
        Args:
            source_ucis: Source SqliteUCIS to merge from
            create_history: Whether to create merge history node
            squash_history: If True, collapse per-test history into a summary node
            
        Returns:
            MergeStats object with merge statistics
        """
        self.stats = MergeStats()
        
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
            
            # Pre-load scope trees for fast traversal (Fix 1)
            self._src_tree, src_root = self._load_scope_tree(source_ucis)
            if self._tgt_tree is None:
                self._tgt_tree, tgt_root = self._load_scope_tree(self.target)
            else:
                tgt_root = self._tgt_root

            self._tgt_root = tgt_root

            # Merge scopes recursively using cached trees
            self._merge_scope_recursive_fast(source_ucis, src_root, tgt_root)
            
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

    def merge_fast(self, source_paths, squash_history=False):
        """Merge multiple source databases using optimised read pattern.

        Opens each source with raw sqlite3.connect, reads all coveritem
        data in a single JOIN query, maps to target via cached dicts,
        and writes via executemany.  Eliminates per-scope query overhead.

        Args:
            source_paths: List of file paths to source .cdb databases.
            squash_history: If True, collapse history into summary node.

        Returns:
            MergeStats with accumulated statistics.
        """
        # 1. Build target lookup maps (once)
        scope_map = {}     # (scope_name, scope_type) -> tgt_scope_id
        for r in self.target.conn.execute(
            "SELECT scope_id, scope_name, scope_type FROM scopes"
        ):
            scope_map[(r[0] if isinstance(r, (list, tuple)) else r['scope_name'],
                        r[1] if isinstance(r, (list, tuple)) else r['scope_type'])] = (
                r[0] if isinstance(r, (list, tuple)) else r['scope_id']
            )
        # Rebuild with proper indexing using raw cursor
        scope_map = {}
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

        # Check if source scope_ids match target (Step 3b optimisation)
        source_ids_match = None

        # Accumulate deltas across ALL sources (Step 3c)
        all_deltas = {}    # cover_id -> total_delta
        all_inserts = []   # rows needing insert

        # 2. Process each source
        self.target.begin_transaction()
        try:
            for src_path in source_paths:
                # 2a. Read source data
                sc = sqlite3.connect(src_path)

                if source_ids_match is None:
                    # First source: check if scope_ids match target
                    src_scopes = {}
                    for sr in sc.execute(
                        "SELECT scope_id, scope_name, scope_type FROM scopes"
                    ):
                        src_scopes[(sr[1], sr[2])] = sr[0]
                    source_ids_match = all(
                        src_scopes.get(k) == v
                        for k, v in scope_map.items()
                        if k[0]  # skip root with empty name
                    ) and len(src_scopes) == len(scope_map)

                if source_ids_match:
                    # Direct scope_id lookup — skip JOIN (Step 3b)
                    rows = sc.execute(
                        "SELECT scope_id, cover_index, cover_data FROM coveritems"
                    ).fetchall()
                    sc.close()

                    for row in rows:
                        src_sid, cidx, cdata = row[0], row[1], row[2]
                        tgt_cid = ci_map.get((src_sid, cidx))
                        if tgt_cid is not None:
                            all_deltas[tgt_cid] = all_deltas.get(tgt_cid, 0) + cdata
                            self.stats.coveritems_matched += 1
                            self.stats.total_hits_added += cdata
                else:
                    # Use minimal 4-column read with JOIN (Step 3a)
                    rows = sc.execute("""
                        SELECT ss.scope_name, ss.scope_type,
                               ci.cover_index, ci.cover_data
                        FROM coveritems ci
                        INNER JOIN scopes ss ON ci.scope_id = ss.scope_id
                    """).fetchall()
                    sc.close()

                    for row in rows:
                        sname, stype = row[0], row[1]
                        cidx, cdata = row[2], row[3]
                        tgt_sid = scope_map.get((sname, stype))
                        if tgt_sid is None:
                            continue

                        tgt_cid = ci_map.get((tgt_sid, cidx))
                        if tgt_cid is not None:
                            all_deltas[tgt_cid] = all_deltas.get(tgt_cid, 0) + cdata
                            self.stats.coveritems_matched += 1
                            self.stats.total_hits_added += cdata

                # 2b. Handle history
                if not squash_history:
                    self._create_test_history_from_path(src_path)

                self.stats.tests_merged += 1

            # 3. Single batch UPDATE for ALL sources (Step 3c)
            if all_deltas:
                self.target.conn.executemany(
                    "UPDATE coveritems SET cover_data = cover_data + ? WHERE cover_id = ?",
                    [(delta, cid) for cid, delta in all_deltas.items()]
                )

            # 4. Squash history summary if requested
            if squash_history:
                self._create_squash_summary(len(source_paths))

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
    
    def _get_scope_path(self, scope):
        """Get hierarchical path for a scope"""
        if scope.scope_id in self._scope_path_cache:
            return self._scope_path_cache[scope.scope_id]
        
        parts = []
        current = scope
        
        # Walk up the hierarchy
        while current is not None:
            name = current.getScopeName()
            scope_type = current.getScopeType()
            
            if name:  # Skip root with empty name
                parts.append((name, scope_type))
            
            # Get parent
            current._ensure_loaded()
            if current._parent_id is not None:
                from ucis.sqlite.sqlite_scope import SqliteScope
                current = SqliteScope(current.ucis_db, current._parent_id)
            else:
                current = None
        
        # Reverse to get root-to-leaf path
        path = tuple(reversed(parts))
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
                    None,     # source_file_id (skip cross-DB file refs)
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
                inserts.append((
                    tgt_scope_id, next_index,
                    row[1], row[2], src_count,
                    row[4], row[5], row[6], row[7], row[8],
                    None, row[10], row[11],
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
