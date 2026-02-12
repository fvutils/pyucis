"""
Tests for native SQL-based SQLite merge
"""
import pytest
import tempfile
import os
from pathlib import Path

from ucis.sqlite.sqlite_ucis import SqliteUCIS
from ucis.sqlite.sqlite_native_merge import SqliteNativeMerger, merge_databases_native
from ucis.sqlite.sqlite_merge import SqliteMerger
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
