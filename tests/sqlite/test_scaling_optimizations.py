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
Tests for SQLite scaling optimizations
"""

import pytest
import os
import tempfile
import sqlite3
from ucis.sqlite import SqliteUCIS
from ucis.sqlite.sqlite_merge import SqliteMerger, merge_databases
from ucis.sqlite import schema_manager
from ucis.sqlite.schema_manager import get_schema_version, is_valid_sqlite_file, is_pyucis_database
from ucis.history_node_kind import HistoryNodeKind
from ucis.scope_type_t import ScopeTypeT
from ucis.cover_type_t import CoverTypeT
from ucis.cover_data import CoverData
from ucis.source_t import SourceT


class TestDatabaseValidation:
    """Test database identification and validation"""
    
    def test_valid_pyucis_database(self):
        """A newly created PyUCIS database should be valid"""
        with tempfile.NamedTemporaryFile(suffix='.cdb', delete=False) as f:
            db_path = f.name
        
        try:
            # Create a PyUCIS database
            db = SqliteUCIS(db_path)
            db.close()
            
            # Validate it
            is_valid, error = is_pyucis_database(db_path)
            assert is_valid, f"New database should be valid, got error: {error}"
            assert error is None
            
            # Check it's a valid SQLite file
            assert is_valid_sqlite_file(db_path)
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_database_has_pyucis_marker(self):
        """Database should have DATABASE_TYPE marker set to PYUCIS"""
        with tempfile.NamedTemporaryFile(suffix='.cdb', delete=False) as f:
            db_path = f.name
        
        try:
            db = SqliteUCIS(db_path)
            cursor = db.conn.execute(
                "SELECT value FROM db_metadata WHERE key = 'DATABASE_TYPE'"
            )
            row = cursor.fetchone()
            assert row is not None, "DATABASE_TYPE key should exist"
            assert row[0] == 'PYUCIS', "DATABASE_TYPE should be 'PYUCIS'"
            db.close()
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_non_sqlite_file_rejected(self):
        """Non-SQLite files should be rejected"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w') as f:
            f.write("This is not a SQLite file")
            txt_path = f.name
        
        try:
            assert not is_valid_sqlite_file(txt_path)
            
            is_valid, error = is_pyucis_database(txt_path)
            assert not is_valid
            assert "sqlite" in error.lower()
            
        finally:
            if os.path.exists(txt_path):
                os.unlink(txt_path)
    
    def test_sqlite_without_pyucis_marker_rejected(self):
        """SQLite database without PYUCIS marker should be rejected"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            # Create a generic SQLite database (not PyUCIS)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")
            cursor.execute("INSERT INTO test VALUES (1, 'hello')")
            conn.commit()
            conn.close()
            
            # Should be valid SQLite but not PyUCIS
            assert is_valid_sqlite_file(db_path)
            
            is_valid, error = is_pyucis_database(db_path)
            assert not is_valid
            assert "pyucis" in error.lower()
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_opening_non_pyucis_database_raises_error(self):
        """Opening a non-PyUCIS database should raise ValueError"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            # Create a generic SQLite database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE db_metadata (key TEXT, value TEXT)")
            cursor.execute("INSERT INTO db_metadata VALUES ('SOME_KEY', 'value')")
            cursor.execute("CREATE TABLE scopes (scope_id INTEGER PRIMARY KEY)")
            cursor.execute("CREATE TABLE coveritems (cover_id INTEGER PRIMARY KEY)")
            cursor.execute("CREATE TABLE history_nodes (history_id INTEGER PRIMARY KEY)")
            conn.commit()
            conn.close()
            
            # Try to open it - should fail validation
            with pytest.raises(ValueError) as exc_info:
                db = SqliteUCIS(db_path)
            
            assert "invalid pyucis database" in str(exc_info.value).lower()
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestSchemaVersion:
    """Test schema version tracking"""
    
    def test_new_database_has_v2_1_schema(self):
        """New databases should be created with v2.1 schema"""
        with tempfile.NamedTemporaryFile(suffix='.cdb', delete=False) as f:
            db_path = f.name
        
        try:
            db = SqliteUCIS(db_path)
            version = get_schema_version(db.conn)
            assert version == "2.1", f"Expected schema version 2.1, got {version}"
            
            # Verify reduced indexes exist
            cursor = db.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='scopes'"
            )
            scope_indexes = [row[0] for row in cursor.fetchall()]
            
            # Should have only these indexes
            assert 'idx_scopes_parent' in scope_indexes
            assert 'idx_scopes_parent_type_name' in scope_indexes
            
            # Should NOT have these removed indexes
            assert 'idx_scopes_type' not in scope_indexes
            assert 'idx_scopes_name' not in scope_indexes
            assert 'idx_scopes_parent_name' not in scope_indexes
            assert 'idx_scopes_source' not in scope_indexes
            
            # Check coveritems indexes
            cursor = db.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='coveritems'"
            )
            cover_indexes = [row[0] for row in cursor.fetchall()]
            
            assert 'idx_coveritems_scope_index' in cover_indexes
            
            # Should NOT have these
            assert 'idx_coveritems_scope' not in cover_indexes
            assert 'idx_coveritems_type' not in cover_indexes
            assert 'idx_coveritems_name' not in cover_indexes
            assert 'idx_coveritems_source' not in cover_indexes
            
            db.close()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_schema_version_mismatch_raises_error(self):
        """Opening a database with wrong schema version should raise an error"""
        with tempfile.NamedTemporaryFile(suffix='.cdb', delete=False) as f:
            db_path = f.name
        
        try:
            # Create a database and manually set wrong version
            db = SqliteUCIS(db_path)
            cursor = db.conn.cursor()
            cursor.execute(
                "UPDATE db_metadata SET value = '1.0' WHERE key = 'SCHEMA_VERSION'"
            )
            db.conn.commit()
            db.close()
            
            # Try to open it again - should raise error
            with pytest.raises(Exception) as exc_info:
                db = SqliteUCIS(db_path)
            
            assert "schema version mismatch" in str(exc_info.value).lower()
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestHistorySquashing:
    """Test optional history squashing feature"""
    
    def _create_test_db(self, path, num_bins=5, num_tests=1, test_name_prefix="test"):
        """Helper to create a test database with coverage"""
        db = SqliteUCIS(path)
        
        # Create design unit
        du = db.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        
        # Create covergroup
        cg = du.createCovergroup("cg1", None, 1, 0)
        
        # Create coverpoint with bins
        cp = cg.createCoverpoint("cp1", None, 1, 0)
        
        # Create bins with varying hit counts
        for i in range(num_bins):
            cover_data = CoverData(CoverTypeT.CVGBIN, 0)
            cover_data.data = i * 10  # 0, 10, 20, 30, 40
            cp.createNextCover(f"bin{i}", cover_data, None)
        
        # Create test history nodes
        for i in range(num_tests):
            test = db.createHistoryNode(
                None,
                f"{test_name_prefix}_{i}",
                f"{test_name_prefix}_{i}.exe",
                HistoryNodeKind.TEST
            )
            test.setSeed(f"{1000 + i}")
            test.setCmd(f"run_test {test_name_prefix}_{i}")
        
        db.close()
        return path
    
    def test_merge_without_squash_preserves_history(self):
        """Default merge behavior preserves per-test history"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source databases with unique test names
            db1 = self._create_test_db(os.path.join(tmpdir, 'test1.cdb'), num_tests=2, test_name_prefix="test1")
            db2 = self._create_test_db(os.path.join(tmpdir, 'test2.cdb'), num_tests=2, test_name_prefix="test2")
            
            # Merge without squashing
            target = SqliteUCIS(os.path.join(tmpdir, 'merged.cdb'))
            merger = SqliteMerger(target)
            
            src1 = SqliteUCIS(db1)
            merger.merge(src1, create_history=True, squash_history=False)
            src1.close()
            
            src2 = SqliteUCIS(db2)
            merger.merge(src2, create_history=True, squash_history=False)
            src2.close()
            
            # Check history nodes
            test_nodes = list(target.historyNodes(HistoryNodeKind.TEST))
            merge_nodes = list(target.historyNodes(HistoryNodeKind.MERGE))
            
            assert len(test_nodes) == 4, "Should have 4 test nodes (2 from each source)"
            assert len(merge_nodes) == 2, "Should have 2 merge nodes"
            
            target.close()
    
    def test_merge_with_squash_creates_summary(self):
        """Squashed merge creates a single summary history node"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source databases with unique test names
            db1 = self._create_test_db(os.path.join(tmpdir, 'test1.cdb'), num_tests=2, test_name_prefix="test1")
            db2 = self._create_test_db(os.path.join(tmpdir, 'test2.cdb'), num_tests=3, test_name_prefix="test2")
            
            # Merge with squashing
            target = SqliteUCIS(os.path.join(tmpdir, 'merged.cdb'))
            merger = SqliteMerger(target)
            
            src1 = SqliteUCIS(db1)
            merger.merge(src1, create_history=True, squash_history=True)
            src1.close()
            
            src2 = SqliteUCIS(db2)
            merger.merge(src2, create_history=True, squash_history=True)
            src2.close()
            
            # Check history nodes
            test_nodes = list(target.historyNodes(HistoryNodeKind.TEST))
            merge_nodes = list(target.historyNodes(HistoryNodeKind.MERGE))
            
            assert len(test_nodes) == 0, "Should have no test nodes when squashed"
            assert len(merge_nodes) == 1, "Should have exactly 1 summary merge node"
            
            # Verify it's the summary node
            summary = merge_nodes[0]
            assert summary.getLogicalName() == "merged_summary"
            
            # Verify test count is tracked
            cursor = target.conn.execute(
                "SELECT int_value FROM history_properties WHERE history_id = ? AND property_key = ?",
                (summary.history_id, hash("TESTS_MERGED") & 0x7FFFFFFF)
            )
            row = cursor.fetchone()
            assert row is not None
            assert row[0] == 5, "Should track 5 tests merged (2 + 3)"
            
            target.close()
    
    def test_incremental_squashed_merge(self):
        """Multiple squashed merges should reuse and update the summary node"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create target and source databases
            target_path = os.path.join(tmpdir, 'merged.cdb')
            target = SqliteUCIS(target_path)
            target.close()
            
            # First merge
            db1 = self._create_test_db(os.path.join(tmpdir, 'test1.cdb'), num_tests=2, test_name_prefix="test1")
            target = SqliteUCIS(target_path)
            merger = SqliteMerger(target)
            src1 = SqliteUCIS(db1)
            merger.merge(src1, create_history=True, squash_history=True)
            src1.close()
            target.close()
            
            # Second merge (incremental)
            db2 = self._create_test_db(os.path.join(tmpdir, 'test2.cdb'), num_tests=3, test_name_prefix="test2")
            target = SqliteUCIS(target_path)
            merger = SqliteMerger(target)
            src2 = SqliteUCIS(db2)
            merger.merge(src2, create_history=True, squash_history=True)
            src2.close()
            target.close()
            
            # Verify only one summary node
            target = SqliteUCIS(target_path)
            merge_nodes = list(target.historyNodes(HistoryNodeKind.MERGE))
            assert len(merge_nodes) == 1, "Should still have exactly 1 summary node"
            
            # Verify cumulative test count
            summary = merge_nodes[0]
            cursor = target.conn.execute(
                "SELECT int_value FROM history_properties WHERE history_id = ? AND property_key = ?",
                (summary.history_id, hash("TESTS_MERGED") & 0x7FFFFFFF)
            )
            row = cursor.fetchone()
            assert row[0] == 5, "Should track cumulative 5 tests (2 + 3)"
            
            target.close()
    
    def test_squashed_merge_preserves_coverage_accuracy(self):
        """Squashed merge should produce identical coverage to non-squashed"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source databases with specific coverage
            db1 = self._create_test_db(os.path.join(tmpdir, 'test1.cdb'), num_bins=3)
            db2 = self._create_test_db(os.path.join(tmpdir, 'test2.cdb'), num_bins=3)
            
            # Merge without squashing
            target_normal = SqliteUCIS(os.path.join(tmpdir, 'merged_normal.cdb'))
            merger_normal = SqliteMerger(target_normal)
            src1 = SqliteUCIS(db1)
            merger_normal.merge(src1, create_history=True, squash_history=False)
            src1.close()
            src2 = SqliteUCIS(db2)
            merger_normal.merge(src2, create_history=True, squash_history=False)
            src2.close()
            
            # Get coverage from normal merge
            normal_coverage = {}
            for cover in target_normal.coverItems(-1):
                normal_coverage[cover.getName()] = cover.getCoverData().data
            target_normal.close()
            
            # Merge with squashing
            target_squashed = SqliteUCIS(os.path.join(tmpdir, 'merged_squashed.cdb'))
            merger_squashed = SqliteMerger(target_squashed)
            src1 = SqliteUCIS(db1)
            merger_squashed.merge(src1, create_history=True, squash_history=True)
            src1.close()
            src2 = SqliteUCIS(db2)
            merger_squashed.merge(src2, create_history=True, squash_history=True)
            src2.close()
            
            # Get coverage from squashed merge
            squashed_coverage = {}
            for cover in target_squashed.coverItems(-1):
                squashed_coverage[cover.getName()] = cover.getCoverData().data
            target_squashed.close()
            
            # Verify identical coverage
            assert normal_coverage == squashed_coverage, \
                "Coverage should be identical regardless of history squashing"


class TestMergeScaling:
    """Test merge scaling characteristics"""
    
    def _create_design_db(self, path, num_coverpoints=3, num_bins_per_cp=10):
        """Create a database with realistic coverage structure"""
        db = SqliteUCIS(path)
        
        du = db.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        cg = du.createCovergroup("cg_main", None, 1, 0)
        
        for cp_idx in range(num_coverpoints):
            cp = cg.createCoverpoint(f"cp_{cp_idx}", None, 1, 0)
            
            # Create all bins (some with zero counts, some with hits)
            for bin_idx in range(num_bins_per_cp):
                cover_data = CoverData(CoverTypeT.CVGBIN, 0)
                # Randomize: some bins get hits, some stay at zero
                import random
                cover_data.data = random.randint(0, 100) if random.random() > 0.3 else 0
                cp.createNextCover(f"bin_{bin_idx}", cover_data, None)
        
        # Add test history
        test = db.createHistoryNode(None, "test_1", "test.exe", HistoryNodeKind.TEST)
        test.setSeed("12345")
        
        db.close()
        return path
    
    def test_coveritem_row_count_stays_constant(self):
        """Merging multiple databases should not increase coveritem count"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple source databases
            num_sources = 4
            sources = []
            for i in range(num_sources):
                path = os.path.join(tmpdir, f'test{i}.cdb')
                self._create_design_db(path, num_coverpoints=2, num_bins_per_cp=5)
                sources.append(path)
            
            # Expected total bins = 2 coverpoints * 5 bins = 10
            expected_bins = 10
            
            # Merge incrementally and check row count each time
            target_path = os.path.join(tmpdir, 'merged.cdb')
            target = SqliteUCIS(target_path)
            merger = SqliteMerger(target)
            
            for i, src_path in enumerate(sources):
                src = SqliteUCIS(src_path)
                merger.merge(src)
                src.close()
                
                # Check coveritem count
                cursor = target.conn.execute("SELECT COUNT(*) FROM coveritems")
                count = cursor.fetchone()[0]
                
                # After first merge, count should be at expected and stay there
                if i == 0:
                    initial_count = count
                    assert initial_count >= expected_bins, \
                        f"Should have at least {expected_bins} bins after first merge"
                else:
                    assert count == initial_count, \
                        f"Coveritem count should stay constant at {initial_count}, " \
                        f"but is {count} after merge {i+1}"
            
            target.close()
    
    def test_merge_with_merge_databases_function(self):
        """Test the convenience merge_databases function"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source databases
            sources = []
            for i in range(3):
                path = os.path.join(tmpdir, f'test{i}.cdb')
                self._create_design_db(path, num_coverpoints=1, num_bins_per_cp=5)
                sources.append(path)
            
            # Use first source as base
            target_path = sources[0]
            output_path = os.path.join(tmpdir, 'merged_output.cdb')
            
            # Merge with squash_history
            stats = merge_databases(
                target_path, 
                sources[1:],
                output_path,
                squash_history=True
            )
            
            # Verify merge succeeded
            assert stats.tests_merged > 0
            
            # Verify output exists and is valid
            db = SqliteUCIS(output_path)
            merge_nodes = list(db.historyNodes(HistoryNodeKind.MERGE))
            assert len(merge_nodes) == 1
            assert merge_nodes[0].getLogicalName() == "merged_summary"
            db.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
