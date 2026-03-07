"""Unit tests for src/ucis/ncdb/testplan_closure.py."""
from __future__ import annotations

import pytest

from ucis.ncdb.testplan import Testplan, Testpoint
from ucis.ncdb.testplan_closure import (
    TPStatus,
    TestpointResult,
    compute_closure,
    stage_gate_status,
)


# ── stub DB ───────────────────────────────────────────────────────────────────

class _FakeStats:
    def __init__(self, pass_count, fail_count):
        self.pass_count = pass_count
        self.fail_count = fail_count


class _FakeRegistry:
    def __init__(self, names):
        self._names = names


class _FakeDB:
    """Minimal NcdbUCIS-like db using the v2 history path."""

    def __init__(self, runs: dict):
        """runs: {name: (pass_count, fail_count)}"""
        names = list(runs.keys())
        self._test_registry = _FakeRegistry(names)
        self._test_stats = _FakeStatsTable(runs)

    def historyNodes(self, _kind):
        return []


class _FakeStatsTable:
    def __init__(self, runs):
        self._runs = runs
        self._names = list(runs.keys())

    def get(self, nid):
        name = self._names[nid]
        p, f = self._runs[name]
        return _FakeStats(p, f)


def _db_with(**kwargs):
    """Helper: _db_with(uart_smoke=(3,1)) → fake db."""
    return _FakeDB(kwargs)


# ── plan helpers ──────────────────────────────────────────────────────────────

def _make_plan(*testpoints) -> Testplan:
    plan = Testplan()
    for tp in testpoints:
        plan.add_testpoint(tp)
    return plan


# ── compute_closure ───────────────────────────────────────────────────────────

class TestComputeClosure:
    def test_closed_when_all_pass(self):
        plan = _make_plan(Testpoint(name="tp", stage="V1", tests=["uart_smoke"]))
        db = _db_with(uart_smoke=(5, 0))
        results = compute_closure(plan, db)
        assert results[0].status == TPStatus.CLOSED

    def test_failing_when_all_fail(self):
        plan = _make_plan(Testpoint(name="tp", stage="V1", tests=["t"]))
        db = _db_with(t=(0, 3))
        results = compute_closure(plan, db)
        assert results[0].status == TPStatus.FAILING

    def test_partial_when_mixed(self):
        plan = _make_plan(Testpoint(name="tp", stage="V1", tests=["t"]))
        db = _db_with(t=(2, 1))
        results = compute_closure(plan, db)
        assert results[0].status == TPStatus.PARTIAL

    def test_not_run_when_absent(self):
        plan = _make_plan(Testpoint(name="tp", stage="V1", tests=["t"]))
        db = _db_with()
        results = compute_closure(plan, db)
        assert results[0].status == TPStatus.NOT_RUN

    def test_na_testpoint(self):
        plan = _make_plan(Testpoint(name="tp", stage="V1", na=True))
        db = _db_with()
        results = compute_closure(plan, db)
        assert results[0].status == TPStatus.NA

    def test_unimplemented_empty_tests(self):
        plan = _make_plan(Testpoint(name="tp", stage="V1", tests=[]))
        db = _db_with()
        results = compute_closure(plan, db)
        assert results[0].status == TPStatus.UNIMPLEMENTED

    def test_wildcard_pattern_matches(self):
        plan = _make_plan(Testpoint(name="tp", stage="V1", tests=["uart_*"]))
        db = _db_with(uart_loopback=(3, 0), uart_reset=(2, 0))
        results = compute_closure(plan, db)
        assert results[0].status == TPStatus.CLOSED
        assert len(results[0].matched_tests) == 2

    def test_seed_strip_matches(self):
        plan = _make_plan(Testpoint(name="tp", stage="V1", tests=["uart_smoke_42"]))
        db = _db_with(uart_smoke=(4, 0))   # DB has stripped name
        results = compute_closure(plan, db)
        assert results[0].status == TPStatus.CLOSED

    def test_pass_fail_counts_accurate(self):
        plan = _make_plan(Testpoint(name="tp", stage="V1",
                                    tests=["a", "b"]))
        db = _db_with(a=(3, 1), b=(2, 2))
        results = compute_closure(plan, db)
        r = results[0]
        assert r.pass_count == 5
        assert r.fail_count == 3

    def test_multiple_testpoints_independent(self):
        plan = _make_plan(
            Testpoint(name="tp1", stage="V1", tests=["a"]),
            Testpoint(name="tp2", stage="V2", tests=["b"]),
        )
        db = _db_with(a=(5, 0), b=(0, 2))
        results = compute_closure(plan, db)
        assert results[0].status == TPStatus.CLOSED
        assert results[1].status == TPStatus.FAILING

    def test_result_order_matches_testplan(self):
        plan = _make_plan(
            Testpoint(name="first",  stage="V1", tests=["x"]),
            Testpoint(name="second", stage="V1", tests=["y"]),
        )
        db = _db_with(x=(1, 0), y=(1, 0))
        results = compute_closure(plan, db)
        assert results[0].testpoint.name == "first"
        assert results[1].testpoint.name == "second"


# ── stage_gate_status ─────────────────────────────────────────────────────────

class TestStageGateStatus:
    def _plan_and_results(self, statuses: dict) -> tuple:
        plan = Testplan()
        for name, (stage, st) in statuses.items():
            plan.add_testpoint(Testpoint(name=name, stage=stage,
                                         tests=["t"] if st != TPStatus.UNIMPLEMENTED else []))
        results = []
        for tp in plan.testpoints:
            st = statuses[tp.name][1]
            results.append(TestpointResult(tp, st, [], 1 if st == TPStatus.CLOSED else 0, 0))
        return plan, results

    def test_gate_passes_all_closed(self):
        plan, results = self._plan_and_results({
            "v1_tp": ("V1", TPStatus.CLOSED),
            "v2_tp": ("V2", TPStatus.CLOSED),
        })
        gate = stage_gate_status(results, "V2", plan)
        assert gate["passed"] is True
        assert gate["blocking"] == []

    def test_gate_fails_if_lower_stage_not_closed(self):
        plan, results = self._plan_and_results({
            "v1_tp": ("V1", TPStatus.FAILING),
            "v2_tp": ("V2", TPStatus.CLOSED),
        })
        gate = stage_gate_status(results, "V2", plan)
        assert gate["passed"] is False
        assert any(r.testpoint.name == "v1_tp" for r in gate["blocking"])

    def test_gate_passes_na_testpoints_ignored(self):
        plan, results = self._plan_and_results({
            "v1_tp": ("V1", TPStatus.CLOSED),
            "v1_na": ("V1", TPStatus.NA),
        })
        gate = stage_gate_status(results, "V1", plan)
        assert gate["passed"] is True

    def test_gate_ignores_higher_stage(self):
        plan, results = self._plan_and_results({
            "v1_tp": ("V1", TPStatus.CLOSED),
            "v3_tp": ("V3", TPStatus.FAILING),   # V3 not evaluated for V2 gate
        })
        gate = stage_gate_status(results, "V2", plan)
        assert gate["passed"] is True

    def test_message_includes_stage(self):
        plan, results = self._plan_and_results({
            "tp": ("V1", TPStatus.CLOSED),
        })
        gate = stage_gate_status(results, "V1", plan)
        assert "V1" in gate["message"]

    def test_gate_returns_stage_key(self):
        plan, results = self._plan_and_results({"tp": ("V1", TPStatus.CLOSED)})
        gate = stage_gate_status(results, "V1", plan)
        assert gate["stage"] == "V1"
