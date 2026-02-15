"""
Integration tests for test-coveritem associations during import and merge.
"""
import os
import tempfile
import pytest
from ucis.sqlite import SqliteUCIS
from ucis.history_node_kind import HistoryNodeKind


def test_vltcov_import_creates_test_associations():
    """Test that importing a vltcov file creates test associations."""
    # Get the real verilator coverage file from the examples
    vltcov_file = os.path.join(
        os.path.dirname(__file__),
        "..", "examples", "verilator", "coverage", "coverage.dat"
    )
    
    if not os.path.exists(vltcov_file):
        pytest.skip(f"Verilator coverage file not found: {vltcov_file}")
    
    # Create a temporary SQLite database
    with tempfile.NamedTemporaryFile(suffix=".cdb", delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # Import the vltcov file directly to SQLite
        target_db = SqliteUCIS(tmp_path)
        
        # Use the format interface to import
        from ucis.rgy.format_rgy import FormatRgy
        rgy = FormatRgy.inst()
        fmt_if = rgy.getDatabaseDesc('vltcov').fmt_if()
        
        # Read into MemUCIS first, then merge to SQLite using SqliteMerger
        mem_db = fmt_if.read(vltcov_file)
        
        # Use SqliteMerger instead of DbMerger to preserve history nodes
        from ucis.sqlite.sqlite_merge import SqliteMerger
        merger = SqliteMerger(target_db)
        merger.merge(mem_db, create_history=True, squash_history=False)
        # SqliteMerger auto-commits, no need to call commit()
        
        # Check that a history node was created
        history_nodes = list(target_db.historyNodes(HistoryNodeKind.TEST))
        assert len(history_nodes) > 0, "No history nodes created"
        
        # Check that test associations were recorded
        test_cov_api = target_db.get_test_coverage_api()
        
        # Get the first test
        test = history_nodes[0]
        
        # Get coveritems for this test
        coveritems = test_cov_api.get_coveritems_for_test(test.history_id)
        
        # Should have some coveritems associated
        assert len(coveritems) > 0, "No coveritems associated with test"
        
        # coveritems is a list of IDs, so just verify we have some
        assert all(isinstance(cid, int) for cid in coveritems[:5]), "Coveritem IDs should be integers"
        
        target_db.close()
    finally:
        # Clean up
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_merge_preserves_test_associations():
    """Test that merging databases preserves test associations."""
    # Get the real verilator coverage file
    vltcov_file = os.path.join(
        os.path.dirname(__file__),
        "..", "examples", "verilator", "coverage", "coverage.dat"
    )
    
    if not os.path.exists(vltcov_file):
        pytest.skip(f"Verilator coverage file not found: {vltcov_file}")
    
    # Create two temporary databases
    with tempfile.NamedTemporaryFile(suffix=".cdb", delete=False) as tmp1:
        db1_path = tmp1.name
    with tempfile.NamedTemporaryFile(suffix=".cdb", delete=False) as tmp2:
        db2_path = tmp2.name
    with tempfile.NamedTemporaryFile(suffix=".cdb", delete=False) as tmp3:
        merged_path = tmp3.name
    
    try:
        # Create first database with test associations
        db1 = SqliteUCIS(db1_path)
        from ucis.rgy.format_rgy import FormatRgy
        rgy = FormatRgy.inst()
        fmt_if = rgy.getDatabaseDesc('vltcov').fmt_if()
        
        mem_db = fmt_if.read(vltcov_file)
        from ucis.sqlite.sqlite_merge import SqliteMerger
        merger = SqliteMerger(db1)
        merger.merge(mem_db, create_history=True, squash_history=False)
        # SqliteMerger auto-commits
        db1.close()
        
        # Create second database with same coverage (simulating second test run)
        db2 = SqliteUCIS(db2_path)
        mem_db2 = fmt_if.read(vltcov_file)
        merger2 = SqliteMerger(db2)
        merger2.merge(mem_db2, create_history=True, squash_history=False)
        # SqliteMerger auto-commits
        db2.close()
        
        # Merge them
        from ucis.sqlite.sqlite_merge import merge_databases
        merge_databases(db1_path, [db2_path], output_path=merged_path, squash_history=False)
        
        # Open merged database and check
        merged = SqliteUCIS.open_readonly(merged_path)
        
        # Should have 1 test history node (same test imported twice)
        history_nodes = list(merged.historyNodes(HistoryNodeKind.TEST))
        assert len(history_nodes) == 1, f"Expected 1 test (same test merged twice), got {len(history_nodes)}"
        
        # Test should have coveritem associations
        test_cov_api = merged.get_test_coverage_api()
        
        for test in history_nodes:
            coveritems = test_cov_api.get_coveritems_for_test(test.history_id)
            assert len(coveritems) > 0, f"Test {test.getLogicalName()} has no coveritems"
        
        # Check that we can query which tests hit a specific coveritem
        # Get first coveritem - merged IS the root scope
        first_cover_id = None
        for scope in merged.scopes(-1):
            for cover in scope.coverItems(-1):
                first_cover_id = cover.cover_id if hasattr(cover, 'cover_id') else None
                break
            if first_cover_id:
                break
        
        if first_cover_id:
            tests_for_item = test_cov_api.get_tests_for_coveritem(first_cover_id)
            # Same test merged twice, should show once
            assert len(tests_for_item) == 1, f"Expected 1 test for coveritem, got {len(tests_for_item)}"
        
        merged.close()
    finally:
        # Clean up
        for path in [db1_path, db2_path, merged_path]:
            if os.path.exists(path):
                os.unlink(path)


def test_test_contribution_calculation():
    """Test that we can calculate test contribution metrics after import."""
    vltcov_file = os.path.join(
        os.path.dirname(__file__),
        "..", "examples", "verilator", "coverage", "coverage.dat"
    )
    
    if not os.path.exists(vltcov_file):
        pytest.skip(f"Verilator coverage file not found: {vltcov_file}")
    
    with tempfile.NamedTemporaryFile(suffix=".cdb", delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # Import coverage
        db = SqliteUCIS(tmp_path)
        from ucis.rgy.format_rgy import FormatRgy
        rgy = FormatRgy.inst()
        fmt_if = rgy.getDatabaseDesc('vltcov').fmt_if()
        
        mem_db = fmt_if.read(vltcov_file)
        from ucis.sqlite.sqlite_merge import SqliteMerger
        merger = SqliteMerger(db)
        merger.merge(mem_db, create_history=True, squash_history=False)
        # SqliteMerger auto-commits
        
        # Get test contribution
        test_cov_api = db.get_test_coverage_api()
        history_nodes = list(db.historyNodes(HistoryNodeKind.TEST))
        
        assert len(history_nodes) > 0, "No tests found"
        test = history_nodes[0]
        
        contribution = test_cov_api.get_test_contribution(test.history_id)
        
        # Verify contribution data
        assert contribution is not None
        assert contribution.history_id == test.history_id
        assert contribution.test_name == test.getLogicalName()
        assert contribution.total_items > 0
        assert contribution.total_contribution > 0
        assert 0 <= contribution.coverage_percent <= 100
        
        db.close()
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
