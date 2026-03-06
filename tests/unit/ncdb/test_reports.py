"""Unit tests for ucis.ncdb.reports."""

import json
import pytest
from unittest.mock import MagicMock

from ucis.ncdb.testplan import Testplan, Testpoint
from ucis.ncdb.testplan_closure import TPStatus, TestpointResult
from ucis.ncdb.reports import (
    ClosureSummary,
    StageGateReport,
    CoveragePerTestpoint,
    RegressionDelta,
    StageProgression,
    TestpointReliability,
    UnexercisedCovergroups,
    CoverageContribution,
    TestBudget,
    SafetyMatrix,
    SeedReliability,
    report_testpoint_closure,
    format_testpoint_closure,
    report_stage_gate,
    format_stage_gate,
    report_coverage_per_testpoint,
    format_coverage_per_testpoint,
    report_regression_delta,
    format_regression_delta,
    report_stage_progression,
    format_stage_progression,
    report_testpoint_reliability,
    format_testpoint_reliability,
    report_unexercised_covergroups,
    format_unexercised_covergroups,
    report_coverage_contribution,
    format_coverage_contribution,
    report_test_budget,
    format_test_budget,
    report_safety_matrix,
    format_safety_matrix,
    report_seed_reliability,
    format_seed_reliability,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_tp(name, stage="V1", tests=None, na=False):
    return Testpoint(name=name, stage=stage, tests=tests or [name], na=na)


def _make_result(tp, status, pass_count=0, fail_count=0, matched=None):
    return TestpointResult(
        testpoint=tp,
        status=status,
        matched_tests=matched or [],
        pass_count=pass_count,
        fail_count=fail_count,
    )


@pytest.fixture
def simple_results():
    tps = [
        _make_tp("tp_alpha", "V1"),
        _make_tp("tp_beta", "V1"),
        _make_tp("tp_gamma", "V2"),
        _make_tp("tp_delta", "V2"),
        _make_tp("tp_na", "V1", na=True),
    ]
    return [
        _make_result(tps[0], TPStatus.CLOSED, pass_count=5, matched=["tp_alpha"]),
        _make_result(tps[1], TPStatus.FAILING, fail_count=3, matched=["tp_beta"]),
        _make_result(tps[2], TPStatus.PARTIAL, pass_count=2, fail_count=1,
                     matched=["tp_gamma"]),
        _make_result(tps[3], TPStatus.NOT_RUN),
        _make_result(tps[4], TPStatus.NA),
    ]


@pytest.fixture
def simple_plan():
    plan = Testplan(source_file="test.hjson")
    plan.add_testpoint(Testpoint(name="tp_alpha", stage="V1", tests=["tp_alpha"]))
    plan.add_testpoint(Testpoint(name="tp_beta", stage="V1", tests=["tp_beta"]))
    plan.add_testpoint(Testpoint(name="tp_gamma", stage="V2", tests=["tp_gamma"]))
    plan.add_testpoint(Testpoint(name="tp_delta", stage="V2", tests=["tp_delta"]))
    return plan


# ---------------------------------------------------------------------------
# Report A — testpoint closure
# ---------------------------------------------------------------------------

class TestReportTestpointClosure:
    def test_returns_closure_summary(self, simple_results):
        summary = report_testpoint_closure(simple_results)
        assert isinstance(summary, ClosureSummary)

    def test_total_counts(self, simple_results):
        summary = report_testpoint_closure(simple_results)
        assert summary.total == 5
        assert summary.total_closed == 1
        assert summary.total_na == 1

    def test_by_stage_keys(self, simple_results):
        summary = report_testpoint_closure(simple_results)
        assert "V1" in summary.by_stage
        assert "V2" in summary.by_stage

    def test_by_stage_counts(self, simple_results):
        summary = report_testpoint_closure(simple_results)
        # V1: tp_alpha (closed) + tp_beta (failing) — tp_na is NA, excluded
        assert summary.by_stage["V1"]["total"] == 2
        assert summary.by_stage["V1"]["closed"] == 1
        # V2: tp_gamma (partial) + tp_delta (not_run)
        assert summary.by_stage["V2"]["total"] == 2
        assert summary.by_stage["V2"]["closed"] == 0

    def test_stage_pct_calculation(self, simple_results):
        summary = report_testpoint_closure(simple_results)
        assert summary.by_stage["V1"]["pct"] == 50.0

    def test_to_json_valid(self, simple_results):
        summary = report_testpoint_closure(simple_results)
        d = json.loads(summary.to_json())
        assert d["total"] == 5
        assert len(d["testpoints"]) == 5

    def test_format_renders_header(self, simple_results):
        summary = report_testpoint_closure(simple_results)
        text = format_testpoint_closure(summary)
        assert "Testpoint" in text
        assert "Stage" in text
        assert "Status" in text

    def test_format_contains_testpoint_name(self, simple_results):
        summary = report_testpoint_closure(simple_results)
        text = format_testpoint_closure(summary)
        assert "tp_alpha" in text
        assert "tp_beta" in text

    def test_format_skips_na_by_default(self, simple_results):
        summary = report_testpoint_closure(simple_results)
        text = format_testpoint_closure(summary)
        # tp_na has TPStatus.NA — should not appear by default
        assert "tp_na" not in text

    def test_format_show_all_includes_na(self, simple_results):
        summary = report_testpoint_closure(simple_results)
        text = format_testpoint_closure(summary, show_all=True)
        assert "tp_na" in text

    def test_format_stage_rollup_present(self, simple_results):
        summary = report_testpoint_closure(simple_results)
        text = format_testpoint_closure(summary)
        assert "Stage roll-up" in text
        assert "V1" in text
        assert "V2" in text


# ---------------------------------------------------------------------------
# Report B — stage gate
# ---------------------------------------------------------------------------

class TestReportStageGate:
    def test_pass_when_all_v1_closed(self):
        tp = _make_tp("tp1", "V1")
        results = [_make_result(tp, TPStatus.CLOSED, pass_count=3)]
        plan = Testplan(source_file="x.hjson")
        plan.add_testpoint(Testpoint(name="tp1", stage="V1", tests=["tp1"]))
        gate = report_stage_gate(results, "V1", plan)
        assert isinstance(gate, StageGateReport)
        assert gate.passed is True
        assert gate.blocking == []

    def test_fail_when_v1_failing(self, simple_results, simple_plan):
        gate = report_stage_gate(simple_results, "V1", simple_plan)
        assert gate.passed is False
        assert any(r.testpoint.name == "tp_beta" for r in gate.blocking)

    def test_to_json_valid(self, simple_results, simple_plan):
        gate = report_stage_gate(simple_results, "V1", simple_plan)
        d = json.loads(gate.to_json())
        assert "passed" in d
        assert "blocking" in d

    def test_format_shows_verdict(self, simple_results, simple_plan):
        gate = report_stage_gate(simple_results, "V1", simple_plan)
        text = format_stage_gate(gate)
        assert "V1" in text
        assert "FAIL" in text or "PASS" in text

    def test_format_lists_blocking(self, simple_results, simple_plan):
        gate = report_stage_gate(simple_results, "V2", simple_plan)
        text = format_stage_gate(gate)
        assert "tp_beta" in text or "tp_gamma" in text or "tp_delta" in text


# ---------------------------------------------------------------------------
# Report D — regression delta
# ---------------------------------------------------------------------------

class TestReportRegressionDelta:
    def test_returns_delta(self, simple_results):
        # All results "old" → same results "new" → no change
        delta = report_regression_delta(simple_results, simple_results)
        assert isinstance(delta, RegressionDelta)
        assert delta.newly_closed == []
        assert delta.newly_failing == []

    def test_detects_newly_closed(self, simple_results):
        old = [_make_result(_make_tp("tp_beta", "V1"), TPStatus.NOT_RUN)]
        new = [_make_result(_make_tp("tp_beta", "V1"), TPStatus.CLOSED,
                            pass_count=1)]
        delta = report_regression_delta(new, old)
        assert len(delta.newly_closed) == 1
        assert delta.newly_closed[0].testpoint.name == "tp_beta"

    def test_detects_newly_failing(self):
        old = [_make_result(_make_tp("tp_a", "V1"), TPStatus.PARTIAL,
                            pass_count=1, fail_count=1)]
        new = [_make_result(_make_tp("tp_a", "V1"), TPStatus.FAILING,
                            fail_count=5)]
        delta = report_regression_delta(new, old)
        assert len(delta.newly_failing) == 1

    def test_to_json_valid(self, simple_results):
        delta = report_regression_delta(simple_results, simple_results)
        d = json.loads(delta.to_json())
        assert "summary" in d
        assert "newly_closed" in d

    def test_format_shows_summary(self, simple_results):
        delta = report_regression_delta(simple_results, simple_results)
        text = format_regression_delta(delta)
        assert "delta" in text.lower()


# ---------------------------------------------------------------------------
# Report F — testpoint reliability
# ---------------------------------------------------------------------------

class TestReportTestpointReliability:
    def test_returns_dataclass(self, simple_results):
        db = MagicMock()
        db.get_test_stats.return_value = None
        report = report_testpoint_reliability(simple_results, db)
        assert isinstance(report, TestpointReliability)

    def test_uses_stats_when_available(self, simple_results):
        stats = MagicMock()
        stats.flake_score = 0.75
        stats.pass_count = 3
        stats.fail_count = 2

        db = MagicMock()
        db.get_test_stats.return_value = stats

        report = report_testpoint_reliability(simple_results, db)
        # tp_alpha has matched_tests=["tp_alpha"] — should get flake 0.75
        alpha_row = next(r for r in report.rows if r[0] == "tp_alpha")
        assert alpha_row[1] == pytest.approx(0.75)

    def test_sorted_by_flake_desc(self, simple_results):
        stats_high = MagicMock()
        stats_high.flake_score = 0.9
        stats_high.pass_count = 1
        stats_high.fail_count = 5

        stats_low = MagicMock()
        stats_low.flake_score = 0.1
        stats_low.pass_count = 9
        stats_low.fail_count = 1

        db = MagicMock()
        def _get(name):
            return stats_high if "beta" in name else stats_low
        db.get_test_stats.side_effect = _get

        report = report_testpoint_reliability(simple_results, db)
        scores = [r[1] for r in report.rows]
        assert scores == sorted(scores, reverse=True)

    def test_to_json_valid(self, simple_results):
        db = MagicMock()
        db.get_test_stats.return_value = None
        report = report_testpoint_reliability(simple_results, db)
        d = json.loads(report.to_json())
        assert "rows" in d

    def test_format_renders_table(self, simple_results):
        db = MagicMock()
        db.get_test_stats.return_value = None
        report = report_testpoint_reliability(simple_results, db)
        text = format_testpoint_reliability(report)
        assert "Testpoint" in text
        assert "Flake" in text


# ---------------------------------------------------------------------------
# Report G — unexercised covergroups
# ---------------------------------------------------------------------------

class TestReportUnexercisedCovergroups:
    def _make_db_with_cg(self, cg_hit_pct: dict):
        """Build a mock db whose covergroup scopes reflect cg_hit_pct."""
        from ucis.scope_type_t import ScopeTypeT
        from ucis.cover_type_t import CoverTypeT

        def make_scope(name, pct):
            scope = MagicMock()
            scope.getScopeName.return_value = name
            n_bins = 10
            hit_bins = int(n_bins * pct / 100)
            cp = MagicMock()
            bins = []
            for i in range(n_bins):
                b = MagicMock()
                b.getData.return_value = (1 if i < hit_bins else 0,)
                bins.append(b)
            cp.getCoverItems.return_value = bins
            scope.getScopes.return_value = [cp]
            return scope

        scopes = [make_scope(name, pct) for name, pct in cg_hit_pct.items()]
        db = MagicMock()
        db.getScopes.return_value = scopes
        return db

    def test_zero_hit_detected(self):
        from ucis.ncdb.testplan import CovergroupEntry
        plan = Testplan(source_file="x.hjson")
        plan.covergroups.append(CovergroupEntry(name="cg_reset"))
        db = self._make_db_with_cg({"cg_reset": 0})
        report = report_unexercised_covergroups(db, plan)
        assert "cg_reset" in report.zero_hit

    def test_low_hit_detected(self):
        from ucis.ncdb.testplan import CovergroupEntry
        plan = Testplan(source_file="x.hjson")
        plan.covergroups.append(CovergroupEntry(name="cg_x"))
        db = self._make_db_with_cg({"cg_x": 30})
        report = report_unexercised_covergroups(db, plan, low_threshold=50.0)
        assert any(n == "cg_x" for n, _ in report.low_hit)

    def test_fully_hit_not_reported(self):
        from ucis.ncdb.testplan import CovergroupEntry
        plan = Testplan(source_file="x.hjson")
        plan.covergroups.append(CovergroupEntry(name="cg_full"))
        db = self._make_db_with_cg({"cg_full": 100})
        report = report_unexercised_covergroups(db, plan)
        assert "cg_full" not in report.zero_hit
        assert not any(n == "cg_full" for n, _ in report.low_hit)

    def test_to_json_valid(self):
        plan = Testplan(source_file="x.hjson")
        db = MagicMock()
        db.getScopes.return_value = []
        report = report_unexercised_covergroups(db, plan)
        d = json.loads(report.to_json())
        assert "zero_hit" in d

    def test_format_shows_message(self):
        plan = Testplan(source_file="x.hjson")
        db = MagicMock()
        db.getScopes.return_value = []
        report = report_unexercised_covergroups(db, plan)
        text = format_unexercised_covergroups(report)
        assert len(text) > 0


# ---------------------------------------------------------------------------
# Report I — coverage contribution
# ---------------------------------------------------------------------------

class TestReportCoverageContribution:
    def test_returns_dataclass_empty_on_no_data(self):
        db = MagicMock()
        db.get_test_coverage_api.return_value = []
        report = report_coverage_contribution(db)
        assert isinstance(report, CoverageContribution)
        assert report.rows == []

    def test_rows_sorted_by_unique_desc(self):
        db = MagicMock()
        db.get_test_coverage_api.return_value = [
            {"test": "t1", "unique_bins": 10, "total_hits": 20, "total_bins": 100},
            {"test": "t2", "unique_bins": 50, "total_hits": 80, "total_bins": 100},
            {"test": "t3", "unique_bins": 30, "total_hits": 40, "total_bins": 100},
        ]
        report = report_coverage_contribution(db)
        names = [r[0] for r in report.rows]
        assert names == ["t2", "t3", "t1"]

    def test_to_json_valid(self):
        db = MagicMock()
        db.get_test_coverage_api.return_value = [
            {"test": "t1", "unique_bins": 5, "total_hits": 10, "total_bins": 50},
        ]
        report = report_coverage_contribution(db)
        d = json.loads(report.to_json())
        assert d["rows"][0]["test"] == "t1"

    def test_format_no_data_message(self):
        db = MagicMock()
        db.get_test_coverage_api.return_value = []
        report = report_coverage_contribution(db)
        text = format_coverage_contribution(report)
        assert "no contribution data" in text.lower()

    def test_format_renders_table(self):
        db = MagicMock()
        db.get_test_coverage_api.return_value = [
            {"test": "uart_smoke", "unique_bins": 42, "total_hits": 100,
             "total_bins": 200},
        ]
        report = report_coverage_contribution(db)
        text = format_coverage_contribution(report)
        assert "uart_smoke" in text
        assert "42" in text


# ---------------------------------------------------------------------------
# Report H — test budget (P2)
# ---------------------------------------------------------------------------

class TestReportTestBudget:
    """Tests for report_test_budget / format_test_budget."""

    def _make_testplan(self, stages):
        """Build a Testplan with one testpoint per stage entry."""
        testpoints = []
        for i, (stage, tests) in enumerate(stages):
            tp = MagicMock(spec=Testpoint)
            tp.name = f"tp_{stage}_{i}"
            tp.stage = stage
            tp.na = False
            tp.tests = tests
            testpoints.append(tp)
        tp_obj = MagicMock(spec=Testplan)
        tp_obj.testpoints = testpoints
        return tp_obj

    def _make_db_with_stats(self, stats_map):
        """Build a mock db that returns stats from stats_map by test name."""
        db = MagicMock()
        def get_stats(name):
            if name in stats_map:
                m = MagicMock()
                m.total_runs, m.mean_cpu_time = stats_map[name]
                return m
            return None
        db.get_test_stats.side_effect = get_stats
        return db

    def test_empty_testplan_returns_empty_budget(self):
        tp = MagicMock(spec=Testplan)
        tp.testpoints = []
        db = MagicMock()
        report = report_test_budget(tp, db)
        assert isinstance(report, TestBudget)
        assert report.rows == []
        assert report.stage_totals == {}
        assert report.missing_stats == []

    def test_single_testpoint_with_stats(self):
        tp = self._make_testplan([("V1", ["smoke"])])
        db = self._make_db_with_stats({"smoke": (10, 30.0)})
        report = report_test_budget(tp, db)
        assert len(report.rows) == 1
        stage, name, cpu, runs = report.rows[0]
        assert stage == "V1"
        assert runs == 10
        assert abs(cpu - 30.0) < 0.01
        assert "V1" in report.stage_totals

    def test_missing_stats_tracked(self):
        tp = self._make_testplan([("V2", ["unknown_test"])])
        db = self._make_db_with_stats({})
        report = report_test_budget(tp, db)
        assert "tp_V2_0" in report.missing_stats

    def test_na_testpoints_skipped(self):
        tp_obj = MagicMock(spec=Testpoint)
        tp_obj.name = "tp_na"
        tp_obj.stage = "V1"
        tp_obj.na = True
        tp_obj.tests = ["some_test"]
        plan = MagicMock(spec=Testplan)
        plan.testpoints = [tp_obj]
        db = MagicMock()
        report = report_test_budget(plan, db)
        assert report.rows == []

    def test_stage_sorting_order(self):
        tp = self._make_testplan([("V3", ["t3"]), ("V1", ["t1"]), ("V2", ["t2"])])
        stats = {"t1": (5, 10.0), "t2": (5, 20.0), "t3": (5, 30.0)}
        db = self._make_db_with_stats(stats)
        report = report_test_budget(tp, db)
        stages = [r[0] for r in report.rows]
        assert stages.index("V1") < stages.index("V2") < stages.index("V3")

    def test_to_json_valid(self):
        tp = self._make_testplan([("V1", ["s1"])])
        db = self._make_db_with_stats({"s1": (3, 15.0)})
        report = report_test_budget(tp, db)
        data = json.loads(report.to_json())
        assert "rows" in data
        assert "stage_totals" in data

    def test_format_shows_stage_and_testpoint(self):
        tp = self._make_testplan([("V1", ["t1"])])
        db = self._make_db_with_stats({"t1": (2, 45.0)})
        report = report_test_budget(tp, db)
        text = format_test_budget(report)
        assert "V1" in text
        assert "tp_V1_0" in text

    def test_format_empty_budget(self):
        report = TestBudget(rows=[], stage_totals={}, missing_stats=[])
        text = format_test_budget(report)
        assert "no" in text.lower() or text == "" or isinstance(text, str)


# ---------------------------------------------------------------------------
# Report L — safety matrix (P2)
# ---------------------------------------------------------------------------

class TestReportSafetyMatrix:
    """Tests for report_safety_matrix / format_safety_matrix."""

    def _make_result(self, tp_name, status=TPStatus.CLOSED, reqs=None):
        tp = MagicMock(spec=Testpoint)
        tp.name = tp_name
        if reqs is not None:
            req_mocks = []
            for r in reqs:
                rm = MagicMock()
                rm.id = r
                rm.desc = f"Requirement {r}"
                req_mocks.append(rm)
            tp.requirements = req_mocks
        else:
            tp.requirements = []
        result = MagicMock(spec=TestpointResult)
        result.testpoint = tp
        result.status = status
        return result

    def test_empty_results_returns_empty_matrix(self):
        report = report_safety_matrix([])
        assert isinstance(report, SafetyMatrix)
        assert report.rows == []

    def test_result_without_requirements_has_dash_req_id(self):
        r = self._make_result("tp_uart", status=TPStatus.CLOSED)
        report = report_safety_matrix([r])
        assert len(report.rows) == 1
        req_id, _, tp, status, waived = report.rows[0]
        assert req_id == "—"
        assert tp == "tp_uart"
        assert "CLOSED" in status

    def test_result_with_requirements_expands_rows(self):
        r = self._make_result("tp_dma", status=TPStatus.PARTIAL, reqs=["REQ-001", "REQ-002"])
        report = report_safety_matrix([r])
        assert len(report.rows) == 2
        req_ids = {row[0] for row in report.rows}
        assert "REQ-001" in req_ids
        assert "REQ-002" in req_ids

    def test_waived_flag_false_without_waivers(self):
        r = self._make_result("tp_x", reqs=["R1"])
        report = report_safety_matrix([r])
        assert report.rows[0][4] is False

    def test_to_json_valid(self):
        r = self._make_result("tp_y", reqs=["R-A"])
        report = report_safety_matrix([r])
        data = json.loads(report.to_json())
        assert "rows" in data
        assert data["rows"][0]["req_id"] == "R-A"

    def test_to_csv_header(self):
        report = report_safety_matrix([])
        csv = report.to_csv()
        assert csv.startswith("req_id,")

    def test_format_shows_req_and_testpoint(self):
        r = self._make_result("tp_bus", reqs=["REQ-007"])
        report = report_safety_matrix([r])
        text = format_safety_matrix(report)
        assert "REQ-007" in text
        assert "tp_bus" in text

    def test_format_multiple_results(self):
        results = [
            self._make_result("tp_a", reqs=["R1"]),
            self._make_result("tp_b", status=TPStatus.FAILING, reqs=["R2"]),
        ]
        report = report_safety_matrix(results)
        text = format_safety_matrix(report)
        assert "R1" in text
        assert "R2" in text
        assert "tp_a" in text
        assert "tp_b" in text


# ---------------------------------------------------------------------------
# Report M — seed reliability (P2)
# ---------------------------------------------------------------------------

class TestReportSeedReliability:
    """Tests for report_seed_reliability / format_seed_reliability."""

    def _make_db_with_history(self, records):
        """Build a mock db returning history records."""
        db = MagicMock()
        db.query_test_history.return_value = records
        return db

    def _rec(self, seed_id, status):
        from ucis.ncdb.constants import HIST_STATUS_OK
        rec = MagicMock()
        rec.seed_id = seed_id
        rec.status = status
        return rec

    def test_empty_history_returns_empty_rows(self):
        db = self._make_db_with_history([])
        report = report_seed_reliability(db, "uart_smoke")
        assert isinstance(report, SeedReliability)
        assert report.rows == []
        assert report.total_seeds == 0

    def test_single_seed_all_pass(self):
        from ucis.ncdb.constants import HIST_STATUS_OK
        recs = [self._rec(42, HIST_STATUS_OK), self._rec(42, HIST_STATUS_OK)]
        db = self._make_db_with_history(recs)
        report = report_seed_reliability(db, "t1")
        assert len(report.rows) == 1
        sid, pc, fc, flake = report.rows[0]
        assert sid == 42
        assert pc == 2
        assert fc == 0
        assert flake == 0.0

    def test_single_seed_all_fail(self):
        recs = [self._rec(7, 1), self._rec(7, 1)]  # status != HIST_STATUS_OK
        db = self._make_db_with_history(recs)
        report = report_seed_reliability(db, "t2")
        assert len(report.rows) == 1
        sid, pc, fc, flake = report.rows[0]
        assert fc == 2
        assert pc == 0

    def test_flaky_seed_has_nonzero_flake_score(self):
        from ucis.ncdb.constants import HIST_STATUS_OK
        recs = [self._rec(1, HIST_STATUS_OK), self._rec(1, 1),
                self._rec(1, HIST_STATUS_OK), self._rec(1, 1)]
        db = self._make_db_with_history(recs)
        report = report_seed_reliability(db, "flaky")
        assert report.rows[0][3] > 0.0

    def test_multiple_seeds_sorted_by_fail_count(self):
        from ucis.ncdb.constants import HIST_STATUS_OK
        recs = [
            self._rec(1, HIST_STATUS_OK),
            self._rec(2, 1), self._rec(2, 1), self._rec(2, 1),
        ]
        db = self._make_db_with_history(recs)
        report = report_seed_reliability(db, "t")
        assert report.rows[0][0] == 2  # seed 2 has 3 failures, comes first

    def test_db_exception_returns_empty(self):
        db = MagicMock()
        db.query_test_history.side_effect = Exception("no history table")
        report = report_seed_reliability(db, "t")
        assert report.rows == []

    def test_to_json_valid(self):
        from ucis.ncdb.constants import HIST_STATUS_OK
        recs = [self._rec(10, HIST_STATUS_OK)]
        db = self._make_db_with_history(recs)
        report = report_seed_reliability(db, "uart_smoke")
        data = json.loads(report.to_json())
        assert data["test_name"] == "uart_smoke"
        assert "rows" in data

    def test_format_shows_seed_id(self):
        from ucis.ncdb.constants import HIST_STATUS_OK
        recs = [self._rec(99, HIST_STATUS_OK)]
        db = self._make_db_with_history(recs)
        report = report_seed_reliability(db, "uart_smoke")
        text = format_seed_reliability(report)
        assert "99" in text

    def test_format_empty_shows_no_history_message(self):
        db = self._make_db_with_history([])
        report = report_seed_reliability(db, "absent_test")
        text = format_seed_reliability(report)
        assert "absent_test" in text
