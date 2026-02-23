"""
Unit tests for toggle coverage display in HierarchyView.

Regression test for: toggle coverage was missing from hierarchy view
because _build_hierarchy_sql() only queried CVGBIN (functional coverage)
and only assigned stats to COVERPOINT nodes.  TOGGLE scope nodes were
left with total=0/covered=0 so no toggle data appeared in the tree.
"""
import sqlite3
import pytest
from unittest.mock import Mock

from ucis.sqlite.schema_manager import create_schema
from ucis.cover_type_t import CoverTypeT
from ucis.scope_type_t import ScopeTypeT


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_toggle_db():
    """
    Build an in-memory SQLite database with a minimal toggle-coverage hierarchy:

        root (scope_type=0)
        └── top  (INSTANCE)
            ├── clk  (TOGGLE)  -- both 0->1 and 1->0 covered
            └── rst  (TOGGLE)  -- neither transition covered
    """
    conn = sqlite3.connect(":memory:")
    create_schema(conn)

    TOGGLE  = int(ScopeTypeT.TOGGLE)
    INSTANCE = int(ScopeTypeT.INSTANCE)
    TBIN     = int(CoverTypeT.TOGGLEBIN)

    conn.executescript(f"""
        INSERT INTO scopes (scope_id, parent_id, scope_type, scope_name)
            VALUES (1, NULL,  0,        'root');
        INSERT INTO scopes (scope_id, parent_id, scope_type, scope_name)
            VALUES (2, 1, {INSTANCE}, 'top');
        INSERT INTO scopes (scope_id, parent_id, scope_type, scope_name)
            VALUES (3, 2, {TOGGLE},   'clk');
        INSERT INTO scopes (scope_id, parent_id, scope_type, scope_name)
            VALUES (4, 2, {TOGGLE},   'rst');

        INSERT INTO coveritems (cover_id, scope_id, cover_type, cover_name, cover_index, cover_data)
            VALUES (1, 3, {TBIN}, '0->1', 0, 5);
        INSERT INTO coveritems (cover_id, scope_id, cover_type, cover_name, cover_index, cover_data)
            VALUES (2, 3, {TBIN}, '1->0', 1, 3);
        INSERT INTO coveritems (cover_id, scope_id, cover_type, cover_name, cover_index, cover_data)
            VALUES (3, 4, {TBIN}, '0->1', 0, 0);
        INSERT INTO coveritems (cover_id, scope_id, cover_type, cover_name, cover_index, cover_data)
            VALUES (4, 4, {TBIN}, '1->0', 1, 0);
    """)
    conn.commit()
    return conn


def _make_view(conn):
    """Wrap *conn* in mock app/model objects and return a HierarchyView."""
    from ucis.tui.views.hierarchy_view import HierarchyView

    mock_db = Mock()
    mock_db.conn = conn

    mock_model = Mock()
    mock_model.db = mock_db
    mock_model.db_path = ":memory:"
    mock_model.get_test_filter.return_value = None

    mock_app = Mock()
    mock_app.console.height = 40
    mock_app.coverage_model = mock_model   # BaseView accesses app.coverage_model

    return HierarchyView(mock_app)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestHierarchyToggleCoverage:
    """Toggle coverage must appear in hierarchy nodes (regression)."""

    def test_toggle_nodes_have_nonzero_totals(self):
        """TOGGLE scope nodes must report total > 0 after build."""
        view = _make_view(_make_toggle_db())
        toggle_nodes = [n for n in view._all_nodes
                        if n.scope_type == int(ScopeTypeT.TOGGLE)]
        assert toggle_nodes, "Expected TOGGLE scope nodes in hierarchy"
        for node in toggle_nodes:
            assert node.total > 0, (
                f"TOGGLE node '{node.name}' has total=0; "
                "toggle coverage bins are not being counted"
            )

    def test_covered_toggle_node_reports_correct_counts(self):
        """A fully-covered toggle signal (clk) reports covered == total."""
        view = _make_view(_make_toggle_db())
        by_name = {n.name: n for n in view._all_nodes}
        clk = by_name["clk"]
        assert clk.total == 2, f"Expected 2 bins for clk, got {clk.total}"
        assert clk.covered == 2, f"Expected clk fully covered, got {clk.covered}"

    def test_uncovered_toggle_node_reports_zero_covered(self):
        """An uncovered toggle signal (rst) reports covered == 0."""
        view = _make_view(_make_toggle_db())
        by_name = {n.name: n for n in view._all_nodes}
        rst = by_name["rst"]
        assert rst.total == 2,   f"Expected 2 bins for rst, got {rst.total}"
        assert rst.covered == 0, f"Expected rst uncovered, got {rst.covered}"

    def test_rollup_propagates_toggle_to_parent(self):
        """INSTANCE parent of toggle nodes must roll up their coverage."""
        view = _make_view(_make_toggle_db())
        by_name = {n.name: n for n in view._all_nodes}
        top = by_name["top"]
        # clk: 2 covered, rst: 0 covered → total 4, covered 2
        assert top.total   == 4, f"Expected 4 total in 'top', got {top.total}"
        assert top.covered == 2, f"Expected 2 covered in 'top', got {top.covered}"

    def test_coverage_percent_matches_data(self):
        """Coverage percentage on toggle nodes must be consistent."""
        view = _make_view(_make_toggle_db())
        by_name = {n.name: n for n in view._all_nodes}
        assert by_name["clk"].get_coverage_percent() == pytest.approx(100.0)
        assert by_name["rst"].get_coverage_percent() == pytest.approx(0.0)
        assert by_name["top"].get_coverage_percent() == pytest.approx(50.0)
