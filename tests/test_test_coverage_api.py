"""
Tests for test-coverage query API
"""
import pytest
import os
import tempfile
from ucis.sqlite.sqlite_ucis import SqliteUCIS
from ucis.history_node_kind import HistoryNodeKind
from ucis.test_status_t import TestStatusT
from ucis.test_data import TestData
from ucis.scope_type_t import ScopeTypeT
from ucis.source_t import SourceT
from ucis.cover_type_t import CoverTypeT
from ucis.cover_data import CoverData


def create_test_database():
    """Create a test database with test-coveritem associations."""
    # Create temporary database
    db = SqliteUCIS()
    
    # Directly insert coveritems into database (simpler than using full API)
    # Create a parent scope first
    cursor = db.conn.execute("""
        INSERT INTO scopes (parent_id, scope_type, scope_name, scope_flags, weight, goal)
        VALUES (?, 0, 'test_scope', 0, 1, 100)
    """, (db.scope_id,))
    scope_id = cursor.lastrowid
    
    # Create 15 coveritems
    coveritem_ids = []
    for i in range(15):
        cursor = db.conn.execute("""
            INSERT INTO coveritems (scope_id, cover_index, cover_type, cover_name, cover_data, goal)
            VALUES (?, ?, ?, ?, 0, 1)
        """, (scope_id, i, CoverTypeT.STMTBIN.value if i < 10 else CoverTypeT.BRANCHBIN.value, f"item_{i}"))
        coveritem_ids.append(cursor.lastrowid)
    
    # Create test history nodes
    test1_id = db.conn.execute("""
        INSERT INTO history_nodes (history_kind, logical_name, physical_name, test_status, date)
        VALUES (1, 'test_basic', '/tests/test_basic.cdb', ?, '2024-01-15')
    """, (TestStatusT.OK.value,)).lastrowid
    
    test2_id = db.conn.execute("""
        INSERT INTO history_nodes (history_kind, logical_name, physical_name, test_status, date)
        VALUES (1, 'test_advanced', '/tests/test_advanced.cdb', ?, '2024-01-16')
    """, (TestStatusT.OK.value,)).lastrowid
    
    test3_id = db.conn.execute("""
        INSERT INTO history_nodes (history_kind, logical_name, physical_name, test_status, date)
        VALUES (1, 'test_edge_cases', '/tests/test_edge.cdb', ?, '2024-01-17')
    """, (TestStatusT.OK.value,)).lastrowid
    
    db.conn.commit()
    
    # Get test coverage API
    test_cov = db.get_test_coverage_api()
    
    # Simulate test1 hitting items 0-5 (6 items)
    for i in range(6):
        test_cov.record_test_association(coveritem_ids[i], test1_id, contribution=5)
    
    # Simulate test2 hitting items 3-10 (8 items, overlap with test1)
    for i in range(3, 11):
        test_cov.record_test_association(coveritem_ids[i], test2_id, contribution=7)
    
    # Simulate test3 hitting items 10-14 (5 items, no overlap with test1)
    for i in range(10, 15):
        test_cov.record_test_association(coveritem_ids[i], test3_id, contribution=3)
    
    db.conn.commit()
    
    # Create simple objects to hold IDs for tests
    class CoverItem:
        def __init__(self, cid):
            self.coveritem_id = cid
    
    class TestNode:
        def __init__(self, hid):
            self.history_id = hid
    
    coveritems = [CoverItem(cid) for cid in coveritem_ids]
    test1 = TestNode(test1_id)
    test2 = TestNode(test2_id)
    test3 = TestNode(test3_id)
    
    return db, coveritems, (test1, test2, test3)


def test_record_test_association():
    """Test recording test-coveritem associations."""
    db, coveritems, (test1, test2, test3) = create_test_database()
    test_cov = db.get_test_coverage_api()
    
    # Check that associations were recorded
    assert test_cov.has_test_associations()
    
    # Verify count
    cursor = db.conn.execute("SELECT COUNT(*) FROM coveritem_tests")
    count = cursor.fetchone()[0]
    assert count == 6 + 8 + 5  # test1 + test2 + test3
    
    db.close()


def test_get_tests_for_coveritem():
    """Test querying which tests hit a coveritem."""
    db, coveritems, (test1, test2, test3) = create_test_database()
    test_cov = db.get_test_coverage_api()
    
    # Item 0: hit only by test1
    info = test_cov.get_tests_for_coveritem(coveritems[0].coveritem_id)
    assert info.total_hits == 5
    assert len(info.tests) == 1
    assert info.tests[0][1] == "test_basic"
    assert info.tests[0][2] == 5
    
    # Item 5: hit by test1 and test2
    info = test_cov.get_tests_for_coveritem(coveritems[5].coveritem_id)
    assert info.total_hits == 12  # 5 + 7
    assert len(info.tests) == 2
    test_names = {t[1] for t in info.tests}
    assert "test_basic" in test_names
    assert "test_advanced" in test_names
    
    # Item 12: hit only by test3
    info = test_cov.get_tests_for_coveritem(coveritems[12].coveritem_id)
    assert info.total_hits == 3
    assert len(info.tests) == 1
    assert info.tests[0][1] == "test_edge_cases"
    
    db.close()


def test_get_coveritems_for_test():
    """Test getting all coveritems hit by a test."""
    db, coveritems, (test1, test2, test3) = create_test_database()
    test_cov = db.get_test_coverage_api()
    
    # test1 hits items 0-5
    items = test_cov.get_coveritems_for_test(test1.history_id)
    assert len(items) == 6
    expected_ids = {coveritems[i].coveritem_id for i in range(6)}
    assert set(items) == expected_ids
    
    # test2 hits items 3-10
    items = test_cov.get_coveritems_for_test(test2.history_id)
    assert len(items) == 8
    expected_ids = {coveritems[i].coveritem_id for i in range(3, 11)}
    assert set(items) == expected_ids
    
    # test3 hits items 10-14
    items = test_cov.get_coveritems_for_test(test3.history_id)
    assert len(items) == 5
    expected_ids = {coveritems[i].coveritem_id for i in range(10, 15)}
    assert set(items) == expected_ids
    
    db.close()


def test_get_unique_coveritems():
    """Test identifying coveritems hit only by one test."""
    db, coveritems, (test1, test2, test3) = create_test_database()
    test_cov = db.get_test_coverage_api()
    
    # test1 unique: items 0, 1, 2 (not hit by test2)
    unique = test_cov.get_unique_coveritems(test1.history_id)
    assert len(unique) == 3
    expected_ids = {coveritems[i].coveritem_id for i in range(3)}
    assert set(unique) == expected_ids
    
    # test2 unique: items 6, 7, 8, 9 (10 is shared with test3)
    unique = test_cov.get_unique_coveritems(test2.history_id)
    assert len(unique) == 4
    expected_ids = {coveritems[i].coveritem_id for i in range(6, 10)}
    assert set(unique) == expected_ids
    
    # test3 unique: items 11, 12, 13, 14 (10 is shared with test2)
    unique = test_cov.get_unique_coveritems(test3.history_id)
    assert len(unique) == 4
    expected_ids = {coveritems[i].coveritem_id for i in range(11, 15)}
    assert set(unique) == expected_ids
    
    db.close()


def test_get_test_contribution():
    """Test calculating test contribution metrics."""
    db, coveritems, (test1, test2, test3) = create_test_database()
    test_cov = db.get_test_coverage_api()
    
    # test1 contribution
    info = test_cov.get_test_contribution(test1.history_id)
    assert info is not None
    assert info.test_name == "test_basic"
    assert info.total_items == 6
    assert info.unique_items == 3
    assert info.total_contribution == 30  # 6 items * 5 contribution each
    assert info.coverage_percent == pytest.approx(40.0)  # 6/15 items
    
    # test2 contribution
    info = test_cov.get_test_contribution(test2.history_id)
    assert info is not None
    assert info.test_name == "test_advanced"
    assert info.total_items == 8
    assert info.unique_items == 4
    assert info.total_contribution == 56  # 8 items * 7 contribution each
    assert info.coverage_percent == pytest.approx(53.33, rel=0.01)  # 8/15 items
    
    # test3 contribution
    info = test_cov.get_test_contribution(test3.history_id)
    assert info is not None
    assert info.test_name == "test_edge_cases"
    assert info.total_items == 5
    assert info.unique_items == 4
    assert info.total_contribution == 15  # 5 items * 3 contribution each
    assert info.coverage_percent == pytest.approx(33.33, rel=0.01)  # 5/15 items
    
    db.close()


def test_get_all_test_contributions():
    """Test getting contribution for all tests."""
    db, coveritems, (test1, test2, test3) = create_test_database()
    test_cov = db.get_test_coverage_api()
    
    contributions = test_cov.get_all_test_contributions()
    
    # Should have 3 tests
    assert len(contributions) == 3
    
    # Should be sorted by total items (descending)
    assert contributions[0].total_items >= contributions[1].total_items
    assert contributions[1].total_items >= contributions[2].total_items
    
    # test2 should be first (8 items)
    assert contributions[0].test_name == "test_advanced"
    assert contributions[0].total_items == 8
    
    # test1 should be second (6 items)
    assert contributions[1].test_name == "test_basic"
    assert contributions[1].total_items == 6
    
    # test3 should be third (5 items)
    assert contributions[2].test_name == "test_edge_cases"
    assert contributions[2].total_items == 5
    
    db.close()


def test_get_coverage_timeline():
    """Test chronological coverage accumulation."""
    db, coveritems, (test1, test2, test3) = create_test_database()
    test_cov = db.get_test_coverage_api()
    
    timeline = test_cov.get_coverage_timeline()
    
    # Should have 3 entries (one per test)
    assert len(timeline) == 3
    
    # Should be in date order
    dates = [t[0] for t in timeline]
    assert dates == ["2024-01-15", "2024-01-16", "2024-01-17"]
    
    # First test (test1): 6 new items, 6 cumulative
    assert timeline[0][1] == "test_basic"
    assert timeline[0][2] == 6  # new items
    assert timeline[0][3] == 6  # cumulative
    assert timeline[0][4] == pytest.approx(40.0)  # 6/15
    
    # Second test (test2): 5 new items (3-5 overlap), 11 cumulative
    assert timeline[1][1] == "test_advanced"
    assert timeline[1][2] == 5  # new items (6,7,8,9,10)
    assert timeline[1][3] == 11  # cumulative
    assert timeline[1][4] == pytest.approx(73.33, rel=0.01)  # 11/15
    
    # Third test (test3): 4 new items (10 overlaps), 15 cumulative
    assert timeline[2][1] == "test_edge_cases"
    assert timeline[2][2] == 4  # new items (11,12,13,14)
    assert timeline[2][3] == 15  # cumulative
    assert timeline[2][4] == pytest.approx(100.0)  # 15/15
    
    db.close()


def test_optimize_test_set_greedy():
    """Test greedy test set optimization."""
    db, coveritems, (test1, test2, test3) = create_test_database()
    test_cov = db.get_test_coverage_api()
    
    # Find minimum set for 80% coverage (12 out of 15 items)
    optimal = test_cov.optimize_test_set_greedy(target_percent=80.0)
    
    # Should select test2 first (8 items), then test1 (3 unique = 11 total)
    # That gets us to 73%, so need test3 too (4 unique = 15 total)
    # Or it might select test2 (8), then test3 (4 unique = 12 total) = 80%
    
    assert len(optimal) >= 2  # Need at least 2 tests
    assert len(optimal) <= 3  # Should not need all 3 for 80%
    
    # First test should be the one with most coverage (test2 with 8 items)
    assert optimal[0][0] == "test_advanced"
    assert optimal[0][1] == 8
    
    # Total coverage should be >= 80%
    total_coverage = sum(items for _, items in optimal)
    assert total_coverage >= 12  # 80% of 15
    
    db.close()


def test_has_test_associations():
    """Test checking if database has test associations."""
    # Empty database
    db = SqliteUCIS()
    test_cov = db.get_test_coverage_api()
    assert not test_cov.has_test_associations()
    db.close()
    
    # Database with associations
    db, _, _ = create_test_database()
    test_cov = db.get_test_coverage_api()
    assert test_cov.has_test_associations()
    db.close()


def test_ensure_indexes():
    """Test that performance indexes are created."""
    db = SqliteUCIS()
    test_cov = db.get_test_coverage_api()
    
    # Check that indexes exist
    cursor = db.conn.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='index' AND name LIKE 'idx_coveritem_tests%'
    """)
    indexes = [row[0] for row in cursor.fetchall()]
    
    assert "idx_coveritem_tests_cover" in indexes
    assert "idx_coveritem_tests_history" in indexes
    
    db.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
