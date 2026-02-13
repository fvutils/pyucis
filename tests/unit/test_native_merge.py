"""
Tests for native SQL-based SQLite merge
"""
import pytest
import tempfile
import os
from pathlib import Path

from ucis.sqlite.sqlite_ucis import SqliteUCIS
from ucis.sqlite.sqlite_native_merge import SqliteNativeMerger, merge_databases_native
from ucis.sqlite.sqlite_merge import SqliteMerger, merge_databases
from ucis.scope_type_t import ScopeTypeT
from ucis.source_t import SourceT
from ucis.cover_data import CoverData
from ucis.history_node_kind import HistoryNodeKind


class TestNativeMerge:
    """Test suite for native SQL merge operations"""
    
    def create_test_database(self, path: str, test_name: str, bin_counts: dict):
        """
        Helper to create a test database with coveritems
        
        Args:
            path: Database file path
            test_name: Test name for history node
            bin_counts: Dict of bin_name -> count
        """
        db = SqliteUCIS(path)
        
        # Create design hierarchy
        top = db.createScope(
            "top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0
        )
        
        dut = top.createScope(
            "dut", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0
        )
        
        # Create covergroup
        cg = dut.createScope(
            "cg1", None, 1, SourceT.NONE, ScopeTypeT.COVERGROUP, 0
        )
        
        # Create coverpoint
        cp = cg.createScope(
            "cp1", None, 1, SourceT.NONE, ScopeTypeT.COVERPOINT, 0
        )
        
        # Add bins with specified counts
        for bin_name, count in bin_counts.items():
            cover_data = CoverData(0x01, 0)  # CVGBIN type
            cover_data.data = count
            cp.createNextCover(bin_name, cover_data, None)
        
        # Create test history node
        test = db.createHistoryNode(
            None, test_name, f"{test_name}.sv", HistoryNodeKind.TEST
        )
        test.setSeed("12345")
        
        db.write(None)
        db.close()
        
        return path
    
    def test_native_merge_basic(self):
        """Test basic native merge functionality"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create two databases
            db1_path = os.path.join(tmpdir, "db1.ucisdb")
            db2_path = os.path.join(tmpdir, "db2.ucisdb")
            
            # DB1: bin1=10, bin2=5
            self.create_test_database(db1_path, "test1", {
                "bin1": 10,
                "bin2": 5
            })
            
            # DB2: bin1=3, bin2=7, bin3=2
            self.create_test_database(db2_path, "test2", {
                "bin1": 3,
                "bin2": 7,
                "bin3": 2
            })
            
            # Merge DB2 into DB1
            target = SqliteUCIS(db1_path)
            source = SqliteUCIS(db2_path)
            
            merger = SqliteNativeMerger(target)
            
            # Check if native merge is possible
            assert merger.can_merge_native(source), "Should be able to use native merge"
            
            # Perform merge
            stats = merger.merge(source, create_history=False)
            
            source.close()
            target.close()
            
            # Verify results
            assert stats.coveritems_matched == 2, "Should match bin1 and bin2"
            assert stats.coveritems_added == 1, "Should add bin3"
            assert stats.total_hits_added == 12, "Should add 3+7+2 hits"
            
            # Verify merged data
            result_db = SqliteUCIS(db1_path)
            
            # Navigate to coverpoint
            top = None
            for scope in result_db.scopes(-1):
                if scope.getScopeName() == "top":
                    top = scope
                    break
            
            assert top is not None
            
            dut = None
            for scope in top.scopes(-1):
                if scope.getScopeName() == "dut":
                    dut = scope
                    break
            
            assert dut is not None
            
            cg = None
            for scope in dut.scopes(-1):
                if scope.getScopeName() == "cg1":
                    cg = scope
                    break
            
            assert cg is not None
            
            cp = None
            for scope in cg.scopes(-1):
                if scope.getScopeName() == "cp1":
                    cp = scope
                    break
            
            assert cp is not None
            
            # Check bin counts
            bins = {}
            for cover in cp.coverItems(-1):
                bins[cover.getName()] = cover.getCoverData().data
            
            assert bins["bin1"] == 13, "bin1 should be 10+3=13"
            assert bins["bin2"] == 12, "bin2 should be 5+7=12"
            assert bins["bin3"] == 2, "bin3 should be 2"
            
            result_db.close()
    
    def test_native_vs_python_merge(self):
        """Compare native merge results with Python merge"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source databases
            src_path = os.path.join(tmpdir, "source.ucisdb")
            
            self.create_test_database(src_path, "test_src", {
                "bin_a": 5,
                "bin_b": 10,
                "bin_c": 3
            })
            
            # Create two identical targets
            tgt_native_path = os.path.join(tmpdir, "target_native.ucisdb")
            tgt_python_path = os.path.join(tmpdir, "target_python.ucisdb")
            
            self.create_test_database(tgt_native_path, "test_base", {
                "bin_a": 2,
                "bin_b": 4
            })
            
            self.create_test_database(tgt_python_path, "test_base", {
                "bin_a": 2,
                "bin_b": 4
            })
            
            # Perform native merge
            target_native = SqliteUCIS(tgt_native_path)
            source1 = SqliteUCIS(src_path)
            native_merger = SqliteNativeMerger(target_native)
            native_stats = native_merger.merge(source1, create_history=False)
            source1.close()
            target_native.close()
            
            # Perform Python merge
            target_python = SqliteUCIS(tgt_python_path)
            source2 = SqliteUCIS(src_path)
            python_merger = SqliteMerger(target_python)
            python_stats = python_merger.merge(source2, create_history=False)
            source2.close()
            target_python.close()
            
            # Compare statistics
            assert native_stats.coveritems_matched == python_stats.coveritems_matched
            assert native_stats.coveritems_added == python_stats.coveritems_added
            
            # Compare actual data
            db_native = SqliteUCIS(tgt_native_path)
            db_python = SqliteUCIS(tgt_python_path)
            
            # Get bin counts from both
            native_bins = self._get_all_bin_counts(db_native)
            python_bins = self._get_all_bin_counts(db_python)
            
            assert native_bins == python_bins, "Native and Python merge should produce identical results"
            
            db_native.close()
            db_python.close()
    
    def test_native_merge_performance(self):
        """Benchmark native vs Python merge performance"""
        import time
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create larger database
            src_path = os.path.join(tmpdir, "large_source.ucisdb")
            
            # Create database with many bins
            bins = {f"bin_{i}": i % 10 for i in range(100)}
            self.create_test_database(src_path, "large_test", bins)
            
            # Create targets
            tgt_native_path = os.path.join(tmpdir, "target_native.ucisdb")
            tgt_python_path = os.path.join(tmpdir, "target_python.ucisdb")
            
            base_bins = {f"bin_{i}": i % 5 for i in range(50)}
            self.create_test_database(tgt_native_path, "base", base_bins)
            self.create_test_database(tgt_python_path, "base", base_bins)
            
            # Time native merge
            target_native = SqliteUCIS(tgt_native_path)
            source1 = SqliteUCIS(src_path)
            native_merger = SqliteNativeMerger(target_native)
            
            start = time.time()
            native_stats = native_merger.merge(source1, create_history=False)
            native_time = time.time() - start
            
            source1.close()
            target_native.close()
            
            # Time Python merge
            target_python = SqliteUCIS(tgt_python_path)
            source2 = SqliteUCIS(src_path)
            python_merger = SqliteMerger(target_python)
            
            start = time.time()
            python_stats = python_merger.merge(source2, create_history=False)
            python_time = time.time() - start
            
            source2.close()
            target_python.close()
            
            # Calculate speedup
            speedup = python_time / native_time if native_time > 0 else 0
            
            print(f"\nPerformance comparison (100 bins):")
            print(f"  Native merge: {native_time*1000:.2f}ms")
            print(f"  Python merge: {python_time*1000:.2f}ms")
            print(f"  Speedup: {speedup:.1f}x")
            
            # Native should be faster (though with small datasets, overhead may dominate)
            # Just verify both complete successfully
            assert native_time > 0
            assert python_time > 0
    
    def test_cannot_merge_inmemory(self):
        """Test that in-memory databases cannot use native merge"""
        # Create in-memory databases
        target = SqliteUCIS()  # in-memory
        source = SqliteUCIS()  # in-memory
        
        merger = SqliteNativeMerger(target)
        
        # Should not be able to use native merge
        assert not merger.can_merge_native(source), \
            "Should not be able to native merge in-memory databases"
        
        target.close()
        source.close()
    
    def test_merge_databases_convenience(self):
        """Test the convenience function for merging multiple databases"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create target and multiple sources
            target_path = os.path.join(tmpdir, "target.ucisdb")
            src1_path = os.path.join(tmpdir, "src1.ucisdb")
            src2_path = os.path.join(tmpdir, "src2.ucisdb")
            
            self.create_test_database(target_path, "base", {"bin1": 5})
            self.create_test_database(src1_path, "test1", {"bin1": 3, "bin2": 7})
            self.create_test_database(src2_path, "test2", {"bin1": 2, "bin3": 4})
            
            # Merge multiple sources
            stats = merge_databases_native(
                target_path,
                [src1_path, src2_path],
                fallback_on_error=True
            )
            
            # Verify merged data
            db = SqliteUCIS(target_path)
            bins = self._get_all_bin_counts(db)
            
            assert bins["bin1"] == 10, "bin1: 5+3+2=10"
            assert bins["bin2"] == 7, "bin2: 0+7+0=7"
            assert bins["bin3"] == 4, "bin3: 0+0+4=4"
            
            db.close()
    
    def _get_all_bin_counts(self, db: SqliteUCIS) -> dict:
        """Helper to get all bin counts from a database"""
        bins = {}
        
        # Navigate hierarchy
        for scope1 in db.scopes(-1):
            for scope2 in scope1.scopes(-1):
                for scope3 in scope2.scopes(-1):
                    for scope4 in scope3.scopes(-1):
                        for cover in scope4.coverItems(-1):
                            bins[cover.getName()] = cover.getCoverData().data
        
        return bins


class TestMergeOptimizations:
    """Tests for merge performance optimizations (Fixes 1-5)"""

    def create_test_database(self, path, test_name, bin_counts):
        """Helper: create a DB with top > dut > cg1 > cp1 hierarchy + bins."""
        db = SqliteUCIS(path)
        top = db.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        dut = top.createScope("dut", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        cg = dut.createScope("cg1", None, 1, SourceT.NONE, ScopeTypeT.COVERGROUP, 0)
        cp = cg.createScope("cp1", None, 1, SourceT.NONE, ScopeTypeT.COVERPOINT, 0)

        for bin_name, count in bin_counts.items():
            cover_data = CoverData(0x01, 0)
            cover_data.data = count
            cp.createNextCover(bin_name, cover_data, None)

        test = db.createHistoryNode(None, test_name, f"{test_name}.sv", HistoryNodeKind.TEST)
        test.setSeed("12345")
        db.write(None)
        db.close()
        return path

    def _get_all_bin_counts(self, db):
        bins = {}
        for s1 in db.scopes(-1):
            for s2 in s1.scopes(-1):
                for s3 in s2.scopes(-1):
                    for s4 in s3.scopes(-1):
                        for cover in s4.coverItems(-1):
                            bins[cover.getName()] = cover.getCoverData().data
        return bins

    # --- Fix 1: Scope tree cache ---

    def test_scope_tree_cache_loads_correctly(self):
        """Verify _load_scope_tree returns correct structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "db.ucisdb")
            self.create_test_database(path, "t1", {"b1": 1})

            db = SqliteUCIS(path)
            merger = SqliteMerger(db)
            tree, root_id = merger._load_scope_tree(db)

            assert root_id is not None
            # Root has children
            assert len(tree[root_id]["children"]) > 0
            # All nodes have required keys
            for sid, info in tree.items():
                assert "name" in info
                assert "type" in info
                assert "parent_id" in info
                assert "children" in info
            db.close()

    def test_scope_tree_cache_reused_across_seeds(self):
        """Verify target tree is loaded once and reused across merge calls."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tgt_path = os.path.join(tmpdir, "target.ucisdb")
            src1_path = os.path.join(tmpdir, "src1.ucisdb")
            src2_path = os.path.join(tmpdir, "src2.ucisdb")

            self.create_test_database(tgt_path, "base", {"b1": 0})
            self.create_test_database(src1_path, "t1", {"b1": 5})
            self.create_test_database(src2_path, "t2", {"b1": 3})

            target = SqliteUCIS(tgt_path)
            merger = SqliteMerger(target)

            src1 = SqliteUCIS.open_readonly(src1_path)
            merger.merge(src1, create_history=False)
            src1.close()

            tree_after_first = merger._tgt_tree
            assert tree_after_first is not None

            src2 = SqliteUCIS.open_readonly(src2_path)
            merger.merge(src2, create_history=False)
            src2.close()

            # Target tree object should be the same reference (reused)
            assert merger._tgt_tree is tree_after_first
            target.close()

    # --- Fix 2: Coveritem cache ---

    def test_coveritem_cache_populated(self):
        """Verify coveritem cache is populated after merge."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tgt_path = os.path.join(tmpdir, "target.ucisdb")
            src_path = os.path.join(tmpdir, "source.ucisdb")

            self.create_test_database(tgt_path, "base", {"b1": 2, "b2": 3})
            self.create_test_database(src_path, "t1", {"b1": 5})

            target = SqliteUCIS(tgt_path)
            source = SqliteUCIS.open_readonly(src_path)
            merger = SqliteMerger(target)
            merger.merge(source, create_history=False)
            source.close()

            # Cache should have entries
            assert len(merger._tgt_coveritems) > 0
            target.close()

    def test_coveritem_cache_updates_in_place(self):
        """Verify cached counts are updated after multiple merges."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tgt_path = os.path.join(tmpdir, "target.ucisdb")
            src1_path = os.path.join(tmpdir, "s1.ucisdb")
            src2_path = os.path.join(tmpdir, "s2.ucisdb")

            self.create_test_database(tgt_path, "base", {"b1": 10})
            self.create_test_database(src1_path, "t1", {"b1": 5})
            self.create_test_database(src2_path, "t2", {"b1": 3})

            target = SqliteUCIS(tgt_path)
            merger = SqliteMerger(target)

            src1 = SqliteUCIS.open_readonly(src1_path)
            merger.merge(src1, create_history=False)
            src1.close()

            src2 = SqliteUCIS.open_readonly(src2_path)
            merger.merge(src2, create_history=False)
            src2.close()

            # Verify actual DB values are correct
            bins = self._get_all_bin_counts(target)
            assert bins["b1"] == 18, f"Expected 10+5+3=18, got {bins['b1']}"
            target.close()

    # --- Fix 3: merge_many single transaction ---

    def test_merge_many_basic(self):
        """Verify merge_many produces correct results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tgt_path = os.path.join(tmpdir, "target.ucisdb")
            src1_path = os.path.join(tmpdir, "s1.ucisdb")
            src2_path = os.path.join(tmpdir, "s2.ucisdb")
            src3_path = os.path.join(tmpdir, "s3.ucisdb")

            # All sources share the same bin structure (same indices)
            self.create_test_database(tgt_path, "base", {"b1": 5, "b2": 0, "b3": 0})
            self.create_test_database(src1_path, "t1", {"b1": 3, "b2": 7, "b3": 0})
            self.create_test_database(src2_path, "t2", {"b1": 2, "b2": 0, "b3": 4})
            self.create_test_database(src3_path, "t3", {"b1": 1, "b2": 1, "b3": 0})

            target = SqliteUCIS(tgt_path)
            merger = SqliteMerger(target)

            sources = [
                SqliteUCIS.open_readonly(src1_path),
                SqliteUCIS.open_readonly(src2_path),
                SqliteUCIS.open_readonly(src3_path),
            ]
            stats = merger.merge_many(sources, create_history=False)
            for s in sources:
                s.close()

            bins = self._get_all_bin_counts(target)
            assert bins["b1"] == 11, f"Expected 5+3+2+1=11, got {bins['b1']}"
            assert bins["b2"] == 8, f"Expected 0+7+0+1=8, got {bins['b2']}"
            assert bins["b3"] == 4, f"Expected 0+0+4+0=4, got {bins['b3']}"
            target.close()

    def test_merge_many_via_ucis(self):
        """Verify SqliteUCIS.merge_many() forwarding works."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tgt_path = os.path.join(tmpdir, "target.ucisdb")
            src_path = os.path.join(tmpdir, "src.ucisdb")

            self.create_test_database(tgt_path, "base", {"b1": 10})
            self.create_test_database(src_path, "t1", {"b1": 5})

            target = SqliteUCIS(tgt_path)
            source = SqliteUCIS.open_readonly(src_path)
            stats = target.merge_many([source], create_history=False)
            source.close()

            bins = self._get_all_bin_counts(target)
            assert bins["b1"] == 15
            assert stats.coveritems_matched >= 1
            target.close()

    def test_merge_many_stats_accumulation(self):
        """Verify stats are correctly accumulated across sources."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tgt_path = os.path.join(tmpdir, "target.ucisdb")
            src1_path = os.path.join(tmpdir, "s1.ucisdb")
            src2_path = os.path.join(tmpdir, "s2.ucisdb")

            self.create_test_database(tgt_path, "base", {"b1": 0})
            self.create_test_database(src1_path, "t1", {"b1": 1})
            self.create_test_database(src2_path, "t2", {"b1": 2, "b2": 3})

            target = SqliteUCIS(tgt_path)
            merger = SqliteMerger(target)
            sources = [
                SqliteUCIS.open_readonly(src1_path),
                SqliteUCIS.open_readonly(src2_path),
            ]
            stats = merger.merge_many(sources, create_history=False)
            for s in sources:
                s.close()

            assert stats.total_hits_added == 6  # 1+2+3
            assert stats.coveritems_matched >= 2
            assert stats.coveritems_added >= 1  # b2 is new
            target.close()

    # --- Fix 4: Source tree reuse ---

    def test_merge_many_reuses_source_tree(self):
        """Verify source tree is loaded once and reused in merge_many."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tgt_path = os.path.join(tmpdir, "target.ucisdb")
            paths = []
            for i in range(4):
                p = os.path.join(tmpdir, f"s{i}.ucisdb")
                self.create_test_database(p, f"t{i}", {"b1": i + 1})
                paths.append(p)

            target = SqliteUCIS(tgt_path)
            merger = SqliteMerger(target)

            sources = [SqliteUCIS.open_readonly(p) for p in paths]
            merger.merge_many(sources, create_history=False)
            for s in sources:
                s.close()

            bins = self._get_all_bin_counts(target)
            assert bins["b1"] == 10  # 1+2+3+4
            target.close()

    # --- Fix 5: ATTACH merge ---

    def test_attach_merge_basic(self):
        """Verify ATTACH-based coveritem merge works correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tgt_path = os.path.join(tmpdir, "target.ucisdb")
            src_path = os.path.join(tmpdir, "source.ucisdb")

            self.create_test_database(tgt_path, "base", {"b1": 10, "b2": 5})
            self.create_test_database(src_path, "t1", {"b1": 3, "b2": 7, "b3": 2})

            target = SqliteUCIS(tgt_path)
            source = SqliteUCIS.open_readonly(src_path)
            merger = SqliteMerger(target)

            # Build scope mapping manually
            merger._src_tree, src_root = merger._load_scope_tree(source)
            merger._tgt_tree, tgt_root = merger._load_scope_tree(target)
            merger._tgt_root = tgt_root

            # Walk trees to build scope_id mapping
            scope_mapping = {}
            self._build_mapping(merger, src_root, tgt_root, scope_mapping)

            target.begin_transaction()
            success = merger._merge_coveritems_attached(source, scope_mapping)
            target.commit()
            source.close()

            assert success, "ATTACH merge should succeed for file-based DBs"

            bins = self._get_all_bin_counts(target)
            assert bins["b1"] == 13
            assert bins["b2"] == 12
            assert bins["b3"] == 2
            target.close()

    def _build_mapping(self, merger, src_id, tgt_id, mapping):
        """Recursively build src->tgt scope ID mapping from trees."""
        mapping[src_id] = tgt_id
        for src_child_id in merger._src_tree[src_id]["children"]:
            tgt_child_id = merger._find_matching_scope_fast(tgt_id, src_child_id)
            if tgt_child_id is not None:
                self._build_mapping(merger, src_child_id, tgt_child_id, mapping)

    # --- merge_databases convenience function ---

    def test_merge_databases_uses_merge_many(self):
        """Verify merge_databases convenience function works with optimizations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tgt_path = os.path.join(tmpdir, "target.ucisdb")
            src1_path = os.path.join(tmpdir, "s1.ucisdb")
            src2_path = os.path.join(tmpdir, "s2.ucisdb")

            # All sources share the same bin structure
            self.create_test_database(tgt_path, "base", {"b1": 5, "b2": 0, "b3": 0})
            self.create_test_database(src1_path, "t1", {"b1": 3, "b2": 7, "b3": 0})
            self.create_test_database(src2_path, "t2", {"b1": 2, "b2": 0, "b3": 4})

            stats = merge_databases(tgt_path, [src1_path, src2_path])

            db = SqliteUCIS(tgt_path)
            bins = self._get_all_bin_counts(db)
            assert bins["b1"] == 10
            assert bins["b2"] == 7
            assert bins["b3"] == 4
            db.close()

    # --- Correctness: multi-seed identical structure ---

    def test_many_seeds_same_structure(self):
        """Simulate merging many seeds with identical scope structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tgt_path = os.path.join(tmpdir, "target.ucisdb")
            self.create_test_database(tgt_path, "base", {"b1": 0, "b2": 0, "b3": 0})

            n_seeds = 16
            sources = []
            for i in range(n_seeds):
                p = os.path.join(tmpdir, f"seed_{i}.ucisdb")
                self.create_test_database(p, f"seed_{i}", {
                    "b1": i,
                    "b2": (i * 2) % 5,
                    "b3": 1,
                })
                sources.append(SqliteUCIS.open_readonly(p))

            target = SqliteUCIS(tgt_path)
            merger = SqliteMerger(target)
            stats = merger.merge_many(sources, create_history=False)
            for s in sources:
                s.close()

            bins = self._get_all_bin_counts(target)
            assert bins["b1"] == sum(range(n_seeds))
            assert bins["b2"] == sum((i * 2) % 5 for i in range(n_seeds))
            assert bins["b3"] == n_seeds
            assert stats.coveritems_matched == n_seeds * 3
            target.close()

    def test_merge_many_rollback_on_error(self):
        """Verify merge_many rolls back on failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tgt_path = os.path.join(tmpdir, "target.ucisdb")
            src_path = os.path.join(tmpdir, "src.ucisdb")

            self.create_test_database(tgt_path, "base", {"b1": 10})
            self.create_test_database(src_path, "t1", {"b1": 5})

            target = SqliteUCIS(tgt_path)
            merger = SqliteMerger(target)

            # Corrupt the source by closing its connection
            source = SqliteUCIS.open_readonly(src_path)
            source.conn.close()

            with pytest.raises(Exception):
                merger.merge_many([source], create_history=False)

            # Target should be unchanged
            target2 = SqliteUCIS(tgt_path)
            bins = self._get_all_bin_counts(target2)
            assert bins["b1"] == 10, "Target should be unchanged after failed merge"
            target2.close()
