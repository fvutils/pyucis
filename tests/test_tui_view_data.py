"""
Layer 2: View data-fidelity tests (headless).

Each view is instantiated with a real CoverageModel but without any
terminal I/O or Rich rendering.  We inspect the Python data structures
that the view would use to render, asserting their correctness without
triggering any display code.
"""
import pytest
from unittest.mock import MagicMock

from tests.tui_fixtures import (
    StubApp,
    partial_coverage, zero_coverage, full_coverage, multi_test, vlt_model,
)


# ---------------------------------------------------------------------------
# GapsView
# ---------------------------------------------------------------------------

class TestGapsViewData:

    def test_all_gaps_below_threshold(self, partial_coverage):
        """Every GapItem must have coverage < threshold."""
        from ucis.tui.views.gaps_view import GapsView
        model, _ = partial_coverage
        view = GapsView(StubApp(model))
        for gap in view.gaps:
            assert gap.coverage < view.threshold, (
                f"Gap '{gap.name}' has {gap.coverage}% which is >= threshold {view.threshold}%"
            )

    def test_gap_count_matches_uncovered_coverpoints(self, partial_coverage):
        """There are 2 coverpoints in the partial fixture, both at 50 % → 2 gaps."""
        from ucis.tui.views.gaps_view import GapsView
        model, expected = partial_coverage
        view = GapsView(StubApp(model))
        assert len(view.gaps) == len(expected["gaps"]), (
            f"Expected {len(expected['gaps'])} gaps, got {len(view.gaps)}"
        )

    def test_gaps_sorted_ascending(self, partial_coverage):
        """GapsView sorts by coverage ascending."""
        from ucis.tui.views.gaps_view import GapsView
        model, _ = partial_coverage
        view = GapsView(StubApp(model))
        coverages = [g.coverage for g in view.gaps]
        assert coverages == sorted(coverages), f"Gaps not sorted: {coverages}"

    def test_gap_hits_and_goal_consistent(self, partial_coverage):
        """gap.coverage should equal hits/goal * 100."""
        from ucis.tui.views.gaps_view import GapsView
        model, _ = partial_coverage
        view = GapsView(StubApp(model))
        for gap in view.gaps:
            if gap.goal > 0:
                expected_pct = gap.hits / gap.goal * 100
                assert abs(gap.coverage - expected_pct) < 0.01, (
                    f"Gap '{gap.name}': coverage={gap.coverage} but hits/goal={expected_pct}"
                )

    def test_no_gaps_when_fully_covered(self, full_coverage):
        """A fully-covered database should have zero gaps."""
        from ucis.tui.views.gaps_view import GapsView
        model, _ = full_coverage
        view = GapsView(StubApp(model))
        assert len(view.gaps) == 0, f"Expected 0 gaps but got {len(view.gaps)}"

    def test_all_bins_are_gaps_when_zero_coverage(self, zero_coverage):
        """With zero coverage every coverpoint is a gap."""
        from ucis.tui.views.gaps_view import GapsView
        model, _ = zero_coverage
        view = GapsView(StubApp(model))
        assert len(view.gaps) >= 1
        for gap in view.gaps:
            assert gap.coverage == 0.0

    def test_gaps_coverage_values_correct(self, partial_coverage):
        """Coverage percentages must match what the text report would show."""
        from ucis.tui.views.gaps_view import GapsView
        from ucis.report.coverage_report_builder import CoverageReportBuilder
        model, _ = partial_coverage
        view = GapsView(StubApp(model))

        # Build oracle from same underlying db
        report = CoverageReportBuilder.build(model.db)
        report_coverages = {}
        for cg in report.covergroups:
            _collect_coverpoint_coverages(cg, report_coverages)

        for gap in view.gaps:
            if gap.name in report_coverages:
                oracle_pct = report_coverages[gap.name]
                assert abs(gap.coverage - oracle_pct) < 0.01, (
                    f"Gap '{gap.name}': TUI={gap.coverage:.2f}%, report={oracle_pct:.2f}%"
                )

    def test_gap_navigation_keys(self, partial_coverage):
        """Arrow keys must update selected_index correctly."""
        from ucis.tui.views.gaps_view import GapsView
        model, _ = partial_coverage
        view = GapsView(StubApp(model))
        if not view.gaps:
            pytest.skip("No gaps to navigate")
        view.selected_index = 0
        view.handle_key("down")
        assert view.selected_index == 1
        view.handle_key("up")
        assert view.selected_index == 0

    def test_gap_navigation_does_not_go_negative(self, partial_coverage):
        from ucis.tui.views.gaps_view import GapsView
        model, _ = partial_coverage
        view = GapsView(StubApp(model))
        view.selected_index = 0
        view.handle_key("up")
        assert view.selected_index == 0


# ---------------------------------------------------------------------------
# HierarchyView
# ---------------------------------------------------------------------------

class TestHierarchyViewData:

    def test_root_nodes_non_empty(self, partial_coverage):
        from ucis.tui.views.hierarchy_view import HierarchyView
        model, _ = partial_coverage
        view = HierarchyView(StubApp(model))
        assert len(view.root_nodes) >= 1

    def test_selected_node_is_set(self, partial_coverage):
        from ucis.tui.views.hierarchy_view import HierarchyView
        model, _ = partial_coverage
        view = HierarchyView(StubApp(model))
        assert view.selected_node is not None

    def test_all_nodes_list_non_empty(self, partial_coverage):
        from ucis.tui.views.hierarchy_view import HierarchyView
        model, _ = partial_coverage
        view = HierarchyView(StubApp(model))
        assert len(view._all_nodes) >= 1

    def test_node_coverage_total_non_negative(self, partial_coverage):
        """Every node's total count must be >= 0."""
        from ucis.tui.views.hierarchy_view import HierarchyView
        model, _ = partial_coverage
        view = HierarchyView(StubApp(model))
        for node in view._all_nodes:
            assert node.total >= 0
            assert node.covered >= 0

    def test_node_covered_lte_total(self, partial_coverage):
        from ucis.tui.views.hierarchy_view import HierarchyView
        model, _ = partial_coverage
        view = HierarchyView(StubApp(model))
        for node in view._all_nodes:
            assert node.covered <= node.total, (
                f"Node '{node.name}': covered={node.covered} > total={node.total}"
            )

    def test_coverage_percent_calculation(self, partial_coverage):
        from ucis.tui.views.hierarchy_view import HierarchyView
        model, _ = partial_coverage
        view = HierarchyView(StubApp(model))
        for node in view._all_nodes:
            pct = node.get_coverage_percent()
            if node.total == 0:
                assert pct == 0.0
            else:
                expected = node.covered / node.total * 100
                assert abs(pct - expected) < 0.01

    def test_down_navigation_changes_selection(self, partial_coverage):
        from ucis.tui.views.hierarchy_view import HierarchyView
        model, _ = partial_coverage
        view = HierarchyView(StubApp(model))
        initial = view.selected_node
        view.handle_key("down")
        assert view.selected_node != initial or len(view._all_nodes) == 1

    def test_up_after_down_returns_to_original(self, partial_coverage):
        from ucis.tui.views.hierarchy_view import HierarchyView
        model, _ = partial_coverage
        view = HierarchyView(StubApp(model))
        initial = view.selected_node
        view.handle_key("down")
        view.handle_key("up")
        assert view.selected_node == initial


# ---------------------------------------------------------------------------
# MetricsView
# ---------------------------------------------------------------------------

class TestMetricsViewData:

    def test_covergroup_count(self, partial_coverage):
        from ucis.tui.views.metrics_view import MetricsView
        model, expected = partial_coverage
        view = MetricsView(StubApp(model))
        assert view.metrics["total_covergroups"] == expected["covergroups"]

    def test_coverpoint_count(self, partial_coverage):
        from ucis.tui.views.metrics_view import MetricsView
        model, expected = partial_coverage
        view = MetricsView(StubApp(model))
        assert view.metrics["total_coverpoints"] == expected["coverpoints"]

    def test_total_bins(self, partial_coverage):
        from ucis.tui.views.metrics_view import MetricsView
        model, expected = partial_coverage
        view = MetricsView(StubApp(model))
        assert view.metrics["total_bins"] == expected["total_bins"]

    def test_covered_bins(self, partial_coverage):
        from ucis.tui.views.metrics_view import MetricsView
        model, expected = partial_coverage
        view = MetricsView(StubApp(model))
        assert view.metrics["covered_bins"] == expected["covered_bins"]

    def test_bin_distribution_sums_to_total(self, partial_coverage):
        """The four histogram buckets must sum to total_bins."""
        from ucis.tui.views.metrics_view import MetricsView
        model, expected = partial_coverage
        view = MetricsView(StubApp(model))
        dist = view.metrics["bin_hit_distribution"]
        bucket_total = sum(dist.values())
        assert bucket_total == expected["total_bins"], (
            f"Distribution sum {bucket_total} != total_bins {expected['total_bins']}: {dist}"
        )

    def test_zero_hit_bucket_correct(self, partial_coverage):
        """Partial fixture: 3 uncovered bins → bucket '0' must be 3."""
        from ucis.tui.views.metrics_view import MetricsView
        model, expected = partial_coverage
        view = MetricsView(StubApp(model))
        uncovered = expected["total_bins"] - expected["covered_bins"]
        assert view.metrics["bin_hit_distribution"]["0"] == uncovered

    def test_zero_coverage_all_in_zero_bucket(self, zero_coverage):
        from ucis.tui.views.metrics_view import MetricsView
        model, expected = zero_coverage
        view = MetricsView(StubApp(model))
        assert view.metrics["bin_hit_distribution"]["0"] == expected["total_bins"]

    def test_full_coverage_zero_in_zero_bucket(self, full_coverage):
        from ucis.tui.views.metrics_view import MetricsView
        model, _ = full_coverage
        view = MetricsView(StubApp(model))
        assert view.metrics["bin_hit_distribution"]["0"] == 0


# ---------------------------------------------------------------------------
# TestHistoryView
# ---------------------------------------------------------------------------

class TestTestHistoryViewData:

    def _make_view(self, model):
        from ucis.tui.views.test_history_view import TestHistoryView
        view = TestHistoryView(StubApp(model))
        view.on_enter()   # triggers _load_tests()
        return view

    def test_test_count(self, partial_coverage):
        model, _ = partial_coverage
        view = self._make_view(model)
        assert len(view.tests) == 1

    def test_test_name(self, partial_coverage):
        model, _ = partial_coverage
        view = self._make_view(model)
        assert view.tests[0]["name"] == "test1"

    def test_multi_test_count(self, multi_test):
        model, expected = multi_test
        view = self._make_view(model)
        assert len(view.tests) == len(expected["test_names"])

    def test_all_multi_test_names_present(self, multi_test):
        model, expected = multi_test
        view = self._make_view(model)
        names = {t["name"] for t in view.tests}
        for name in expected["test_names"]:
            assert name in names

    def test_sort_by_name_ascending(self, multi_test):
        model, _ = multi_test
        view = self._make_view(model)
        view.handle_key("d")   # switch to date sort first
        view.handle_key("n")   # switch back to name → ascending
        names = [t["name"] for t in view.tests]
        assert names == sorted(names)

    def test_sort_by_name_toggle_descending(self, multi_test):
        model, _ = multi_test
        view = self._make_view(model)
        view.handle_key("d")   # switch to date sort first
        view.handle_key("n")   # sort by name ascending
        view.handle_key("n")   # toggle → descending
        names = [t["name"] for t in view.tests]
        assert names == sorted(names, reverse=True)

    def test_navigation_changes_selection(self, multi_test):
        model, _ = multi_test
        view = self._make_view(model)
        view.selected_index = 0
        view.handle_key("down")
        assert view.selected_index == 1

    def test_navigation_clamped_at_zero(self, multi_test):
        model, _ = multi_test
        view = self._make_view(model)
        view.selected_index = 0
        view.handle_key("up")
        assert view.selected_index == 0

    def test_filter_by_test_sets_model_filter(self, multi_test):
        """Pressing 'f' should set the model test filter."""
        model, expected = multi_test
        view = self._make_view(model)
        view.selected_index = 0
        selected_name = view.tests[0]["name"]
        view.handle_key("f")
        assert model.get_test_filter() == selected_name


# ---------------------------------------------------------------------------
# CodeCoverageView
# ---------------------------------------------------------------------------

class TestCodeCoverageViewData:

    def test_file_coverage_list_type(self, vlt_model):
        """file_coverage must be a list (possibly empty for non-code dbs)."""
        from ucis.tui.views.code_coverage_view import CodeCoverageView
        view = CodeCoverageView(StubApp(vlt_model))
        assert isinstance(view.file_coverage, list)

    def test_covered_lte_total_per_file(self, vlt_model):
        """For every file, line_covered <= line_total."""
        from ucis.tui.views.code_coverage_view import CodeCoverageView
        view = CodeCoverageView(StubApp(vlt_model))
        for fi in view.file_coverage:
            assert fi.line_covered <= fi.line_total, (
                f"{fi.file_path}: covered={fi.line_covered} > total={fi.line_total}"
            )

    def test_coverage_percentage_property(self, vlt_model):
        """line_coverage property must be arithmetically correct."""
        from ucis.tui.views.code_coverage_view import CodeCoverageView
        view = CodeCoverageView(StubApp(vlt_model))
        for fi in view.file_coverage:
            if fi.line_total > 0:
                expected = fi.line_covered / fi.line_total * 100
                assert abs(fi.line_coverage - expected) < 0.01


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _collect_coverpoint_coverages(cg_node, result: dict):
    """Recursively collect {coverpoint_name: coverage_pct} from a Covergroup."""
    for cp in cg_node.coverpoints:
        result[cp.name] = cp.coverage
    for sub in getattr(cg_node, "covergroups", []):
        _collect_coverpoint_coverages(sub, result)
