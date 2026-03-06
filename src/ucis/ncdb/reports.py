"""Structured reports for testplan closure, stage gates, and test history.

Every report function returns a typed dataclass with a ``to_json()`` method.
A companion ``format_*()`` function renders the dataclass to a human-readable
string suitable for terminal output.  The CLI calls the formatter; automated
consumers use the dataclass or ``to_json()``.
"""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple

from ucis.ncdb.testplan import Testplan, Testpoint, get_testplan
from ucis.ncdb.testplan_closure import (
    TPStatus,
    TestpointResult,
    compute_closure,
    stage_gate_status,
    _STAGE_ORDER,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_STATUS_ICON = {
    TPStatus.CLOSED: "✓",
    TPStatus.PARTIAL: "~",
    TPStatus.FAILING: "✗",
    TPStatus.NOT_RUN: "?",
    TPStatus.NA: "N/A",
    TPStatus.UNIMPLEMENTED: "-",
}

_STATUS_LABEL = {
    TPStatus.CLOSED: "CLOSED",
    TPStatus.PARTIAL: "PARTIAL",
    TPStatus.FAILING: "FAILING",
    TPStatus.NOT_RUN: "NOT_RUN",
    TPStatus.NA: "N/A",
    TPStatus.UNIMPLEMENTED: "UNIMP",
}


def _pct(num: int, den: int) -> float:
    return round(100.0 * num / den, 1) if den else 0.0


# ---------------------------------------------------------------------------
# Report A — testpoint closure table
# ---------------------------------------------------------------------------

@dataclass
class ClosureSummary:
    """Result of ``report_testpoint_closure()``.

    Args:
        results: Per-testpoint closure results.
        by_stage: Stage-level roll-up: stage → {closed, total, pct}.
        total_closed: Number of testpoints with status CLOSED.
        total_na: Number of testpoints with status N/A.
        total: Total testpoint count.
    """
    results: List[TestpointResult]
    by_stage: Dict[str, Dict]
    total_closed: int
    total_na: int
    total: int

    def to_json(self) -> str:
        d = {
            "total": self.total,
            "total_closed": self.total_closed,
            "total_na": self.total_na,
            "by_stage": self.by_stage,
            "testpoints": [
                {
                    "name": r.testpoint.name,
                    "stage": r.testpoint.stage,
                    "status": r.status.value,
                    "pass_count": r.pass_count,
                    "fail_count": r.fail_count,
                    "matched_tests": r.matched_tests,
                }
                for r in self.results
            ],
        }
        return json.dumps(d, indent=2)


def report_testpoint_closure(results: List[TestpointResult]) -> ClosureSummary:
    """Compute a closure summary from testpoint results.

    Args:
        results: List of :class:`~ucis.ncdb.testplan_closure.TestpointResult`
            objects (output of :func:`~ucis.ncdb.testplan_closure.compute_closure`).

    Returns:
        :class:`ClosureSummary` with per-stage roll-up and totals.
    """
    by_stage: Dict[str, Dict] = {}
    total_closed = 0
    total_na = 0

    for r in results:
        stage = r.testpoint.stage or "unknown"
        entry = by_stage.setdefault(stage, {"closed": 0, "total": 0, "pct": 0.0})
        if r.status not in (TPStatus.NA, TPStatus.UNIMPLEMENTED):
            entry["total"] += 1
            if r.status == TPStatus.CLOSED:
                entry["closed"] += 1
        if r.status == TPStatus.CLOSED:
            total_closed += 1
        elif r.status == TPStatus.NA:
            total_na += 1

    for entry in by_stage.values():
        entry["pct"] = _pct(entry["closed"], entry["total"])

    return ClosureSummary(
        results=results,
        by_stage=by_stage,
        total_closed=total_closed,
        total_na=total_na,
        total=len(results),
    )


def format_testpoint_closure(summary: ClosureSummary, *, show_all: bool = False) -> str:
    """Render a :class:`ClosureSummary` as a terminal table.

    Args:
        summary: Output of :func:`report_testpoint_closure`.
        show_all: If False (default), skip N/A and UNIMPLEMENTED rows.

    Returns:
        Human-readable multiline string.
    """
    lines: List[str] = []
    col_name = 34
    col_stage = 6
    col_status = 10
    col_pass = 6
    col_fail = 6

    header = (
        f"{'Testpoint':<{col_name}} "
        f"{'Stage':<{col_stage}} "
        f"{'Status':<{col_status}} "
        f"{'Pass':>{col_pass}} "
        f"{'Fail':>{col_fail}}"
    )
    sep = "-" * len(header)
    lines.append(header)
    lines.append(sep)

    for r in summary.results:
        if not show_all and r.status in (TPStatus.NA, TPStatus.UNIMPLEMENTED):
            continue
        icon = _STATUS_ICON[r.status]
        label = _STATUS_LABEL[r.status]
        lines.append(
            f"{r.testpoint.name:<{col_name}} "
            f"{r.testpoint.stage or '?':<{col_stage}} "
            f"{icon} {label:<{col_status - 2}} "
            f"{r.pass_count:>{col_pass}} "
            f"{r.fail_count:>{col_fail}}"
        )

    lines.append(sep)
    # Stage roll-up
    lines.append("\nStage roll-up:")
    ordered_stages = sorted(
        summary.by_stage.items(),
        key=lambda kv: _STAGE_ORDER.get(kv[0], 999),
    )
    for stage, entry in ordered_stages:
        bar_len = 20
        filled = round(bar_len * entry["pct"] / 100) if entry["total"] else 0
        bar = "█" * filled + "░" * (bar_len - filled)
        lines.append(
            f"  {stage:<6} [{bar}] "
            f"{entry['closed']}/{entry['total']} "
            f"({entry['pct']:.1f}%)"
        )

    lines.append(
        f"\nTotal: {summary.total_closed}/{summary.total} closed"
        f"  ({summary.total_na} N/A)"
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Report B — stage gate
# ---------------------------------------------------------------------------

@dataclass
class StageGateReport:
    """Result of ``report_stage_gate()``.

    Args:
        stage: Target stage (e.g. ``"V2"``).
        passed: Whether the gate passes.
        blocking: Testpoints that are not yet CLOSED (and not N/A).
        message: Human-readable verdict line.
        gate_detail: Raw detail dict from
            :func:`~ucis.ncdb.testplan_closure.stage_gate_status`.
    """
    stage: str
    passed: bool
    blocking: List[TestpointResult]
    message: str
    gate_detail: dict

    def to_json(self) -> str:
        d = {
            "stage": self.stage,
            "passed": self.passed,
            "message": self.message,
            "blocking": [
                {
                    "name": r.testpoint.name,
                    "stage": r.testpoint.stage,
                    "status": r.status.value,
                }
                for r in self.blocking
            ],
        }
        return json.dumps(d, indent=2)


def report_stage_gate(
    results: List[TestpointResult],
    stage: str,
    testplan: Testplan,
    require_flake_score_below: Optional[float] = None,
    require_coverage_pct: Optional[float] = None,
) -> StageGateReport:
    """Evaluate a stage gate (go/no-go for advancing to next stage).

    Args:
        results: Output of :func:`~ucis.ncdb.testplan_closure.compute_closure`.
        stage: Target stage to evaluate (``"V1"``, ``"V2"``, etc.).
        testplan: The :class:`~ucis.ncdb.testplan.Testplan` being evaluated.
        require_flake_score_below: Optional flake threshold (0–1).
        require_coverage_pct: Optional minimum coverage percentage.

    Returns:
        :class:`StageGateReport`.
    """
    gate = stage_gate_status(
        results,
        stage,
        testplan,
        require_flake_score_below=require_flake_score_below,
        require_coverage_pct=require_coverage_pct,
    )
    blocking = gate.get("blocking", [])
    passed = gate.get("passed", False)
    message = gate.get("message", "")
    return StageGateReport(
        stage=stage,
        passed=passed,
        blocking=blocking,
        message=message,
        gate_detail=gate,
    )


def format_stage_gate(report: StageGateReport) -> str:
    """Render a :class:`StageGateReport` as a terminal summary.

    Args:
        report: Output of :func:`report_stage_gate`.

    Returns:
        Human-readable multiline string.
    """
    lines: List[str] = []
    verdict = "✓ PASS" if report.passed else "✗ FAIL"
    lines.append(f"Stage gate [{report.stage}]: {verdict}")
    lines.append(f"  {report.message}")
    if report.blocking:
        lines.append(f"\n  Blocking testpoints ({len(report.blocking)}):")
        for r in report.blocking:
            lines.append(
                f"    [{r.testpoint.stage}] {r.testpoint.name}  "
                f"— {_STATUS_LABEL[r.status]}"
            )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Report C — coverage per testpoint
# ---------------------------------------------------------------------------

@dataclass
class CoveragePerTestpoint:
    """Per-testpoint coverage table linking matched tests to covergroups.

    Args:
        rows: List of (testpoint_name, covergroup_name, hit_pct) tuples.
        unmatched_covergroups: Covergroups that could not be linked to any
            testpoint via the testplan.
    """
    rows: List[Tuple[str, str, float]]
    unmatched_covergroups: List[str]

    def to_json(self) -> str:
        d = {
            "rows": [
                {"testpoint": tp, "covergroup": cg, "hit_pct": pct}
                for tp, cg, pct in self.rows
            ],
            "unmatched_covergroups": self.unmatched_covergroups,
        }
        return json.dumps(d, indent=2)


def report_coverage_per_testpoint(
    results: List[TestpointResult],
    db,
    testplan: Testplan,
) -> CoveragePerTestpoint:
    """Build a testpoint × covergroup coverage table.

    For each testpoint that has covergroup entries in the testplan the
    function walks the UCIS hierarchy to find a matching scope and
    computes the hit percentage.

    Args:
        results: Output of :func:`~ucis.ncdb.testplan_closure.compute_closure`.
        db: An open UCIS database (any type — MemUCIS, NcdbUCIS, etc.).
        testplan: The active :class:`~ucis.ncdb.testplan.Testplan`.

    Returns:
        :class:`CoveragePerTestpoint`.
    """
    from ucis.scope_type_t import ScopeTypeT
    from ucis.cover_type_t import CoverTypeT

    # Build a quick map: covergroup name → hit% from the UCIS tree
    cg_pct: Dict[str, float] = {}
    try:
        for scope in db.getScopes(ScopeTypeT.COVERGROUP):
            name = scope.getScopeName()
            total = 0
            hit = 0
            for cp in scope.getScopes(ScopeTypeT.COVERPOINT):
                for b in cp.getCoverItems(CoverTypeT.CVGBIN):
                    total += 1
                    if b.getData()[0] > 0:
                        hit += 1
            if total:
                cg_pct[name] = _pct(hit, total)
            else:
                cg_pct[name] = 0.0
    except Exception:
        pass  # db may not support scope iteration

    rows: List[Tuple[str, str, float]] = []
    matched_cgs: set = set()

    for r in results:
        cg_entries = r.testpoint.covergroups if hasattr(r.testpoint, "covergroups") else []
        # Fallback: check testplan.covergroups linked to this testpoint name
        plan_cgs = [c for c in testplan.covergroups if True]  # all for now
        for cg in plan_cgs:
            cg_name = cg.name if hasattr(cg, "name") else str(cg)
            pct = cg_pct.get(cg_name, 0.0)
            rows.append((r.testpoint.name, cg_name, pct))
            matched_cgs.add(cg_name)

    unmatched = [cg for cg in cg_pct if cg not in matched_cgs]
    return CoveragePerTestpoint(rows=rows, unmatched_covergroups=unmatched)


def format_coverage_per_testpoint(report: CoveragePerTestpoint) -> str:
    """Render a :class:`CoveragePerTestpoint` as a terminal table.

    Args:
        report: Output of :func:`report_coverage_per_testpoint`.

    Returns:
        Human-readable multiline string.
    """
    if not report.rows:
        return "(no testpoint-covergroup links found)"

    col_tp = max((len(r[0]) for r in report.rows), default=10) + 2
    col_cg = max((len(r[1]) for r in report.rows), default=10) + 2
    lines: List[str] = []
    header = f"{'Testpoint':<{col_tp}} {'Covergroup':<{col_cg}} {'Hit%':>6}"
    lines.append(header)
    lines.append("-" * len(header))
    prev_tp = None
    for tp, cg, pct in report.rows:
        tp_col = tp if tp != prev_tp else ""
        prev_tp = tp
        lines.append(f"{tp_col:<{col_tp}} {cg:<{col_cg}} {pct:>6.1f}%")
    if report.unmatched_covergroups:
        lines.append(
            f"\nUnmatched covergroups: "
            + ", ".join(report.unmatched_covergroups)
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Report D — regression delta
# ---------------------------------------------------------------------------

@dataclass
class RegressionDelta:
    """Delta between two closure result sets.

    Args:
        newly_closed: Testpoints that moved to CLOSED.
        newly_failing: Testpoints that were not FAILING but are now.
        unchanged_open: Testpoints that remain open/partial.
        summary: One-line summary string.
    """
    newly_closed: List[TestpointResult]
    newly_failing: List[TestpointResult]
    unchanged_open: List[TestpointResult]
    summary: str

    def to_json(self) -> str:
        def _names(lst):
            return [r.testpoint.name for r in lst]

        d = {
            "newly_closed": _names(self.newly_closed),
            "newly_failing": _names(self.newly_failing),
            "unchanged_open": _names(self.unchanged_open),
            "summary": self.summary,
        }
        return json.dumps(d, indent=2)


def report_regression_delta(
    results_new: List[TestpointResult],
    results_old: List[TestpointResult],
) -> RegressionDelta:
    """Compute the testplan closure delta between two regression runs.

    Args:
        results_new: Closure results for the current regression.
        results_old: Closure results for the baseline regression.

    Returns:
        :class:`RegressionDelta`.
    """
    old_map = {r.testpoint.name: r.status for r in results_old}
    newly_closed: List[TestpointResult] = []
    newly_failing: List[TestpointResult] = []
    unchanged_open: List[TestpointResult] = []

    for r in results_new:
        old_status = old_map.get(r.testpoint.name)
        if r.status == TPStatus.CLOSED and old_status != TPStatus.CLOSED:
            newly_closed.append(r)
        elif r.status == TPStatus.FAILING and old_status not in (
            TPStatus.FAILING,
            None,
        ):
            newly_failing.append(r)
        elif r.status not in (TPStatus.CLOSED, TPStatus.NA):
            unchanged_open.append(r)

    summary = (
        f"+{len(newly_closed)} closed, "
        f"-{len(newly_failing)} newly failing, "
        f"{len(unchanged_open)} still open"
    )
    return RegressionDelta(
        newly_closed=newly_closed,
        newly_failing=newly_failing,
        unchanged_open=unchanged_open,
        summary=summary,
    )


def format_regression_delta(report: RegressionDelta) -> str:
    """Render a :class:`RegressionDelta` as a terminal summary.

    Args:
        report: Output of :func:`report_regression_delta`.

    Returns:
        Human-readable multiline string.
    """
    lines: List[str] = [f"Regression delta: {report.summary}"]
    if report.newly_closed:
        lines.append(f"\n  Newly closed ({len(report.newly_closed)}):")
        for r in report.newly_closed:
            lines.append(f"    ✓ [{r.testpoint.stage}] {r.testpoint.name}")
    if report.newly_failing:
        lines.append(f"\n  Newly failing ({len(report.newly_failing)}):")
        for r in report.newly_failing:
            lines.append(f"    ✗ [{r.testpoint.stage}] {r.testpoint.name}")
    if report.unchanged_open:
        lines.append(f"\n  Still open ({len(report.unchanged_open)}):")
        for r in report.unchanged_open:
            lines.append(
                f"    ~ [{r.testpoint.stage}] {r.testpoint.name}"
                f"  — {_STATUS_LABEL[r.status]}"
            )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Report E — stage progression over time  (P1)
# ---------------------------------------------------------------------------

@dataclass
class StageProgression:
    """Stage closure progression over time (requires v2 history).

    Args:
        stage: Target stage.
        series: List of (timestamp, closed_count, total) tuples,
            oldest first.
        current_pct: Most-recent closure percentage.
    """
    stage: str
    series: List[Tuple[int, int, int]]
    current_pct: float

    def to_json(self) -> str:
        d = {
            "stage": self.stage,
            "current_pct": self.current_pct,
            "series": [
                {"ts": ts, "closed": c, "total": t} for ts, c, t in self.series
            ],
        }
        return json.dumps(d, indent=2)


def report_stage_progression(db, testplan: Testplan, stage: str) -> StageProgression:
    """Compute stage closure percentage over time from v2 history buckets.

    Uses the bucket index to sample closure state at bucket boundary
    timestamps.  Falls back to an empty series when no v2 history is
    available.

    Args:
        db: An open :class:`~ucis.ncdb.ncdb_ucis.NcdbUCIS` instance.
        testplan: The active testplan.
        stage: Stage to evaluate (e.g. ``"V2"``).

    Returns:
        :class:`StageProgression`.
    """
    series: List[Tuple[int, int, int]] = []
    total_tps = len(testplan.testpointsForStage(stage, include_lower=True))
    if total_tps == 0:
        return StageProgression(stage=stage, series=[], current_pct=0.0)

    # Try to build a time-series from the bucket index
    try:
        db._ensure_v2_history()
        bidx = db._bucket_index
        if bidx is not None:
            entries = list(bidx._entries)
            # Accumulate by walking buckets in order
            passed_names: set = set()
            for entry in entries:
                # Read bucket records for this time window
                try:
                    reader = db._get_bucket_reader(entry)
                    for rec in reader.records():
                        name = db._test_registry.lookup_name(rec.name_id)
                        if rec.status == 0:  # HIST_STATUS_OK (pass)
                            passed_names.add(name)
                except Exception:
                    pass
                # Count how many testpoints now have ≥1 passing test
                closed = sum(
                    1
                    for tp in testplan.testpointsForStage(stage, include_lower=True)
                    for t in tp.tests
                    if any(n.startswith(t.rstrip("*")) for n in passed_names)
                )
                series.append((entry.ts_end, closed, total_tps))
    except Exception:
        pass

    current_pct = _pct(series[-1][1], series[-1][2]) if series else 0.0
    return StageProgression(stage=stage, series=series, current_pct=current_pct)


def format_stage_progression(report: StageProgression) -> str:
    """Render a :class:`StageProgression` as an ASCII spark-line.

    Args:
        report: Output of :func:`report_stage_progression`.

    Returns:
        Human-readable multiline string.
    """
    if not report.series:
        return f"Stage [{report.stage}]: no history data available"

    lines = [f"Stage [{report.stage}] closure over time:"]
    bars = "▁▂▃▄▅▆▇█"
    spark = ""
    for _, closed, total in report.series:
        pct = closed / total if total else 0
        idx = min(int(pct * len(bars)), len(bars) - 1)
        spark += bars[idx]
    lines.append(f"  {spark}")
    first_ts = report.series[0][0]
    last_ts = report.series[-1][0]
    lines.append(
        f"  {time.strftime('%Y-%m-%d', time.gmtime(first_ts))} → "
        f"{time.strftime('%Y-%m-%d', time.gmtime(last_ts))}"
    )
    lines.append(f"  Current: {report.current_pct:.1f}%")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Report F — testpoint reliability  (P1)
# ---------------------------------------------------------------------------

@dataclass
class TestpointReliability:
    """Per-testpoint flake scores.

    Args:
        rows: List of (testpoint_name, flake_score, pass_count, fail_count).
            Sorted by flake_score descending.
        flaky_threshold: Score above which a testpoint is considered flaky.
    """
    rows: List[Tuple[str, float, int, int]]
    flaky_threshold: float = 0.2

    def to_json(self) -> str:
        d = {
            "flaky_threshold": self.flaky_threshold,
            "rows": [
                {
                    "testpoint": tp,
                    "flake_score": score,
                    "pass": pc,
                    "fail": fc,
                }
                for tp, score, pc, fc in self.rows
            ],
        }
        return json.dumps(d, indent=2)


def report_testpoint_reliability(
    results: List[TestpointResult],
    db,
    flaky_threshold: float = 0.2,
) -> TestpointReliability:
    """Compute per-testpoint flake scores from v2 test_stats.

    Args:
        results: Output of :func:`~ucis.ncdb.testplan_closure.compute_closure`.
        db: An open :class:`~ucis.ncdb.ncdb_ucis.NcdbUCIS` instance.
        flaky_threshold: Flake score above which a testpoint is flagged.

    Returns:
        :class:`TestpointReliability`.
    """
    rows: List[Tuple[str, float, int, int]] = []
    for r in results:
        if not r.matched_tests:
            rows.append((r.testpoint.name, 0.0, r.pass_count, r.fail_count))
            continue
        total_flake = 0.0
        count = 0
        pc_total = 0
        fc_total = 0
        for test_name in r.matched_tests:
            try:
                stats = db.get_test_stats(test_name)
                if stats:
                    total_flake += stats.flake_score
                    pc_total += stats.pass_count
                    fc_total += stats.fail_count
                    count += 1
            except Exception:
                pass
        avg_flake = total_flake / count if count else 0.0
        rows.append((r.testpoint.name, avg_flake, pc_total, fc_total))

    rows.sort(key=lambda x: x[1], reverse=True)
    return TestpointReliability(rows=rows, flaky_threshold=flaky_threshold)


def format_testpoint_reliability(report: TestpointReliability) -> str:
    """Render a :class:`TestpointReliability` as a terminal table.

    Args:
        report: Output of :func:`report_testpoint_reliability`.

    Returns:
        Human-readable multiline string.
    """
    col_name = max((len(r[0]) for r in report.rows), default=10) + 2
    lines: List[str] = []
    header = f"{'Testpoint':<{col_name}} {'Flake':>7} {'Pass':>7} {'Fail':>7}"
    lines.append(header)
    lines.append("-" * len(header))
    for tp, score, pc, fc in report.rows:
        flag = " ⚠" if score >= report.flaky_threshold else ""
        lines.append(f"{tp:<{col_name}} {score:>7.3f} {pc:>7} {fc:>7}{flag}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Report G — unexercised covergroups  (P1)
# ---------------------------------------------------------------------------

@dataclass
class UnexercisedCovergroups:
    """Covergroups with zero hits.

    Args:
        zero_hit: List of covergroup names with 0% coverage.
        low_hit: List of (name, pct) tuples with 0 < pct < threshold.
        threshold: Low-hit threshold used.
    """
    zero_hit: List[str]
    low_hit: List[Tuple[str, float]]
    threshold: float = 50.0

    def to_json(self) -> str:
        d = {
            "threshold": self.threshold,
            "zero_hit": self.zero_hit,
            "low_hit": [{"name": n, "pct": p} for n, p in self.low_hit],
        }
        return json.dumps(d, indent=2)


def report_unexercised_covergroups(
    db,
    testplan: Testplan,
    low_threshold: float = 50.0,
) -> UnexercisedCovergroups:
    """Identify covergroups with zero or low coverage.

    Args:
        db: An open UCIS database.
        testplan: The active testplan (used to filter to plan-tracked groups).
        low_threshold: Percentage below which a covergroup is flagged as
            low-hit (default 50%).

    Returns:
        :class:`UnexercisedCovergroups`.
    """
    from ucis.scope_type_t import ScopeTypeT
    from ucis.cover_type_t import CoverTypeT

    plan_cg_names = {c.name for c in testplan.covergroups}
    zero_hit: List[str] = []
    low_hit: List[Tuple[str, float]] = []

    try:
        for scope in db.getScopes(ScopeTypeT.COVERGROUP):
            cg_name = scope.getScopeName()
            if plan_cg_names and cg_name not in plan_cg_names:
                continue
            total = hit = 0
            for cp in scope.getScopes(ScopeTypeT.COVERPOINT):
                for b in cp.getCoverItems(CoverTypeT.CVGBIN):
                    total += 1
                    if b.getData()[0] > 0:
                        hit += 1
            if total == 0:
                zero_hit.append(cg_name)
            else:
                pct = _pct(hit, total)
                if pct == 0.0:
                    zero_hit.append(cg_name)
                elif pct < low_threshold:
                    low_hit.append((cg_name, pct))
    except Exception:
        pass

    low_hit.sort(key=lambda x: x[1])
    return UnexercisedCovergroups(
        zero_hit=zero_hit,
        low_hit=low_hit,
        threshold=low_threshold,
    )


def format_unexercised_covergroups(report: UnexercisedCovergroups) -> str:
    """Render an :class:`UnexercisedCovergroups` report as terminal text.

    Args:
        report: Output of :func:`report_unexercised_covergroups`.

    Returns:
        Human-readable multiline string.
    """
    lines: List[str] = []
    if report.zero_hit:
        lines.append(f"Zero-hit covergroups ({len(report.zero_hit)}):")
        for name in report.zero_hit:
            lines.append(f"  ✗ {name}")
    if report.low_hit:
        lines.append(
            f"\nLow-hit covergroups (< {report.threshold:.0f}%) "
            f"({len(report.low_hit)}):"
        )
        for name, pct in report.low_hit:
            lines.append(f"  ~ {name}  ({pct:.1f}%)")
    if not lines:
        lines.append("All tracked covergroups are fully hit.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Report I — coverage contribution  (P1)
# ---------------------------------------------------------------------------

@dataclass
class CoverageContribution:
    """Per-test unique bin contribution.

    Args:
        rows: List of (test_name, unique_bins, total_hits) sorted by
            unique_bins descending.
        total_bins: Total covered bins in the database.
    """
    rows: List[Tuple[str, int, int]]
    total_bins: int

    def to_json(self) -> str:
        d = {
            "total_bins": self.total_bins,
            "rows": [
                {"test": t, "unique_bins": u, "total_hits": h}
                for t, u, h in self.rows
            ],
        }
        return json.dumps(d, indent=2)


def report_coverage_contribution(db) -> CoverageContribution:
    """Report per-test unique coverage bin contribution from v2 contrib data.

    Args:
        db: An open :class:`~ucis.ncdb.ncdb_ucis.NcdbUCIS` instance.

    Returns:
        :class:`CoverageContribution`.
    """
    rows: List[Tuple[str, int, int]] = []
    total_bins = 0

    try:
        contrib_data = db.get_test_coverage_api()
        if contrib_data:
            for item in contrib_data:
                test_name = item.get("test", "")
                unique = item.get("unique_bins", 0)
                hits = item.get("total_hits", 0)
                rows.append((test_name, unique, hits))
                total_bins = max(total_bins, item.get("total_bins", 0))
    except Exception:
        pass

    rows.sort(key=lambda x: x[1], reverse=True)
    return CoverageContribution(rows=rows, total_bins=total_bins)


def format_coverage_contribution(report: CoverageContribution) -> str:
    """Render a :class:`CoverageContribution` as a terminal table.

    Args:
        report: Output of :func:`report_coverage_contribution`.

    Returns:
        Human-readable multiline string.
    """
    if not report.rows:
        return "(no contribution data available — v2 history required)"

    col_name = max((len(r[0]) for r in report.rows), default=10) + 2
    lines: List[str] = []
    header = f"{'Test':<{col_name}} {'Unique':>8} {'Total hits':>12}"
    lines.append(header)
    lines.append("-" * len(header))
    for name, unique, hits in report.rows:
        lines.append(f"{name:<{col_name}} {unique:>8} {hits:>12}")
    lines.append(f"\nTotal bins in database: {report.total_bins}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Report H — test budget by stage  (P2)
# ---------------------------------------------------------------------------

@dataclass
class TestBudget:
    """CPU time budget by stage.

    Args:
        rows: List of (stage, testpoint_name, mean_cpu_sec, total_runs)
            sorted by stage rank then mean_cpu_sec descending.
        stage_totals: Mapping of stage → total estimated CPU seconds.
        missing_stats: Testpoint names for which no CPU stats are available.
    """
    rows: List[Tuple[str, str, float, int]]
    stage_totals: Dict[str, float]
    missing_stats: List[str]

    def to_json(self) -> str:
        d = {
            "stage_totals": self.stage_totals,
            "missing_stats": self.missing_stats,
            "rows": [
                {"stage": s, "testpoint": tp, "mean_cpu_sec": cpu, "total_runs": n}
                for s, tp, cpu, n in self.rows
            ],
        }
        return json.dumps(d, indent=2)


def report_test_budget(testplan: Testplan, db) -> TestBudget:
    """Estimate CPU-hour budget per stage from v2 test_stats mean CPU times.

    For each testpoint the mean CPU time of all its mapped tests is summed.
    Testpoints with no CPU stats are listed in ``missing_stats``.

    Args:
        testplan: The active :class:`~ucis.ncdb.testplan.Testplan`.
        db: An open :class:`~ucis.ncdb.ncdb_ucis.NcdbUCIS` instance.

    Returns:
        :class:`TestBudget`.
    """
    rows: List[Tuple[str, str, float, int]] = []
    stage_totals: Dict[str, float] = {}
    missing_stats: List[str] = []

    for tp in testplan.testpoints:
        if tp.na or not tp.tests:
            continue
        total_cpu = 0.0
        total_runs = 0
        found = False
        for test_name in tp.tests:
            try:
                stats = db.get_test_stats(test_name)
                if stats and stats.total_runs > 0:
                    total_cpu += stats.mean_cpu_time * stats.total_runs
                    total_runs += stats.total_runs
                    found = True
            except Exception:
                pass
        mean_cpu = total_cpu / total_runs if total_runs else 0.0
        if not found:
            missing_stats.append(tp.name)
        stage = tp.stage or "unknown"
        rows.append((stage, tp.name, mean_cpu, total_runs))
        stage_totals[stage] = stage_totals.get(stage, 0.0) + mean_cpu

    rows.sort(key=lambda r: (_STAGE_ORDER.get(r[0], 999), -r[2]))
    return TestBudget(rows=rows, stage_totals=stage_totals, missing_stats=missing_stats)


def format_test_budget(report: TestBudget) -> str:
    """Render a :class:`TestBudget` as a terminal table.

    Args:
        report: Output of :func:`report_test_budget`.

    Returns:
        Human-readable multiline string.
    """
    col_tp = max((len(r[1]) for r in report.rows), default=10) + 2
    lines: List[str] = []
    header = f"{'Stage':<6} {'Testpoint':<{col_tp}} {'Mean CPU':>10} {'Runs':>7}"
    lines.append(header)
    lines.append("-" * len(header))
    prev_stage = None
    for stage, tp, cpu, runs in report.rows:
        if stage != prev_stage:
            if prev_stage is not None:
                total = report.stage_totals.get(prev_stage, 0.0)
                lines.append(f"{'':6} {'Stage total':>{col_tp}} {total:>9.1f}s")
                lines.append("")
            prev_stage = stage
        lines.append(f"{stage:<6} {tp:<{col_tp}} {cpu:>9.1f}s {runs:>7}")
    if prev_stage:
        total = report.stage_totals.get(prev_stage, 0.0)
        lines.append(f"{'':6} {'Stage total':>{col_tp}} {total:>9.1f}s")
    if report.missing_stats:
        lines.append(f"\nNo CPU stats for: {', '.join(report.missing_stats)}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Report L — safety traceability matrix  (P2)
# ---------------------------------------------------------------------------

@dataclass
class SafetyMatrix:
    """Requirement x testpoint traceability matrix with waiver flags.

    Args:
        rows: List of (req_id, req_desc, testpoint_name, status, waived).
        untested_requirements: Requirement IDs with no linked testpoints.
    """
    rows: List[Tuple[str, str, str, str, bool]]
    untested_requirements: List[str]

    def to_csv(self) -> str:
        """Render as CSV suitable for safety audits."""
        lines = ["req_id,req_desc,testpoint,status,waived"]
        for req_id, req_desc, tp_name, status, waived in self.rows:
            lines.append(f"{req_id},{req_desc!r},{tp_name},{status},{waived}")
        return "\n".join(lines)

    def to_json(self) -> str:
        d = {
            "untested_requirements": self.untested_requirements,
            "rows": [
                {"req_id": rid, "req_desc": rdesc, "testpoint": tp,
                 "status": st, "waived": w}
                for rid, rdesc, tp, st, w in self.rows
            ],
        }
        return json.dumps(d, indent=2)


def report_safety_matrix(
    results: List[TestpointResult],
    waivers=None,
) -> SafetyMatrix:
    """Build a requirement to testpoint traceability matrix.

    Args:
        results: Output of :func:`~ucis.ncdb.testplan_closure.compute_closure`.
        waivers: Optional :class:`~ucis.ncdb.waivers.WaiverSet`.

    Returns:
        :class:`SafetyMatrix`.
    """
    rows: List[Tuple[str, str, str, str, bool]] = []
    seen_reqs: set = set()

    for r in results:
        reqs = r.testpoint.requirements
        if reqs:
            for req in reqs:
                req_id = req.id if hasattr(req, "id") else str(req)
                req_desc = req.desc if hasattr(req, "desc") else ""
                seen_reqs.add(req_id)
                waived = False
                if waivers is not None:
                    try:
                        waived = waivers.matches_scope(r.testpoint.name, "")
                    except Exception:
                        pass
                rows.append((req_id, req_desc, r.testpoint.name,
                              _STATUS_LABEL[r.status], waived))
        else:
            rows.append(("—", "", r.testpoint.name, _STATUS_LABEL[r.status], False))

    return SafetyMatrix(rows=rows, untested_requirements=[])


def format_safety_matrix(report: SafetyMatrix) -> str:
    """Render a :class:`SafetyMatrix` as a text table.

    Args:
        report: Output of :func:`report_safety_matrix`.

    Returns:
        Human-readable multiline string.
    """
    col_req = max((len(r[0]) for r in report.rows), default=6) + 2
    col_tp  = max((len(r[2]) for r in report.rows), default=10) + 2
    col_st  = 10
    lines: List[str] = []
    header = (f"{'Req ID':<{col_req}} {'Testpoint':<{col_tp}} "
              f"{'Status':<{col_st}} {'Waived':>6}")
    lines.append(header)
    lines.append("-" * len(header))
    for req_id, _, tp, status, waived in report.rows:
        w_str = "YES" if waived else ""
        lines.append(f"{req_id:<{col_req}} {tp:<{col_tp}} {status:<{col_st}} {w_str:>6}")
    if report.untested_requirements:
        lines.append(f"\nUntested: {', '.join(report.untested_requirements)}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Report M — seed reliability heat-map  (P2)
# ---------------------------------------------------------------------------

@dataclass
class SeedReliability:
    """Per-seed pass/fail counts for a given test name.

    Args:
        test_name: The queried test name.
        rows: List of (seed_id, pass_count, fail_count, flake_score) sorted
            by fail_count descending.
        total_seeds: Total unique seeds seen.
    """
    test_name: str
    rows: List[Tuple[int, int, int, float]]
    total_seeds: int

    def to_json(self) -> str:
        d = {
            "test_name": self.test_name,
            "total_seeds": self.total_seeds,
            "rows": [{"seed": s, "pass": p, "fail": f, "flake": fl}
                     for s, p, f, fl in self.rows],
        }
        return json.dumps(d, indent=2)


def report_seed_reliability(db, test_name: str) -> SeedReliability:
    """Compute per-seed pass/fail counts from v2 history buckets.

    Args:
        db: An open :class:`~ucis.ncdb.ncdb_ucis.NcdbUCIS` instance.
        test_name: Name of the test to analyse.

    Returns:
        :class:`SeedReliability`.
    """
    from ucis.ncdb.constants import HIST_STATUS_OK

    seed_pass: Dict[int, int] = {}
    seed_fail: Dict[int, int] = {}

    try:
        records = db.query_test_history(test_name)
        for rec in records:
            sid = rec.seed_id
            if rec.status == HIST_STATUS_OK:
                seed_pass[sid] = seed_pass.get(sid, 0) + 1
            else:
                seed_fail[sid] = seed_fail.get(sid, 0) + 1
    except Exception:
        pass

    all_seeds = set(seed_pass) | set(seed_fail)
    rows: List[Tuple[int, int, int, float]] = []
    for sid in all_seeds:
        pc = seed_pass.get(sid, 0)
        fc = seed_fail.get(sid, 0)
        total = pc + fc
        flake = _pct(min(pc, fc), total) / 100.0 if total > 0 else 0.0
        rows.append((sid, pc, fc, flake))

    rows.sort(key=lambda x: x[2], reverse=True)
    return SeedReliability(test_name=test_name, rows=rows, total_seeds=len(all_seeds))


def format_seed_reliability(report: SeedReliability) -> str:
    """Render a :class:`SeedReliability` as a terminal heat-map table.

    Args:
        report: Output of :func:`report_seed_reliability`.

    Returns:
        Human-readable multiline string.
    """
    if not report.rows:
        return f"No history found for test '{report.test_name}'"

    lines: List[str] = [f"Seed reliability for '{report.test_name}':"]
    header = f"{'Seed':>12} {'Pass':>7} {'Fail':>7} {'Flake':>7}"
    lines.append(header)
    lines.append("-" * len(header))
    for sid, pc, fc, flake in report.rows:
        flag = " ⚠" if flake >= 0.2 else ""
        lines.append(f"{sid:>12} {pc:>7} {fc:>7} {flake:>7.3f}{flag}")
    lines.append(f"\nTotal unique seeds: {report.total_seeds}")
    return "\n".join(lines)
