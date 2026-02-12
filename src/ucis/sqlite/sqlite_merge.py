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
            
            # Merge scopes recursively starting from root
            self._merge_scope_recursive(source_ucis, self.target)
            
            # Commit transaction
            self.target.commit()
            
            return self.stats
            
        except Exception as e:
            # Rollback on error
            self.target.rollback()
            raise Exception(f"Merge failed: {e}") from e
    
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
    
    total_stats = MergeStats()
    
    # Merge each source
    for src_path in source_paths:
        source = SqliteUCIS.open_readonly(src_path)
        
        stats = merger.merge(source, squash_history=squash_history)
        
        # Accumulate statistics
        total_stats.scopes_matched += stats.scopes_matched
        total_stats.scopes_added += stats.scopes_added
        total_stats.coveritems_matched += stats.coveritems_matched
        total_stats.coveritems_added += stats.coveritems_added
        total_stats.total_hits_added += stats.total_hits_added
        total_stats.tests_merged += stats.tests_merged
        total_stats.conflicts.extend(stats.conflicts)
        
        source.close()
    
    target.close()
    
    return total_stats
