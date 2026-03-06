"""
src/ucis/ncdb/testplan_closure.py — Testpoint closure computation.

Given a :class:`~ucis.ncdb.testplan.Testplan` and a UCIS database this module
computes the pass/fail *closure* status for each testpoint and evaluates
stage-level gate conditions.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from .testplan import Testplan, Testpoint


class TPStatus(Enum):
    """Closure status of one testpoint."""
    CLOSED        = "CLOSED"         # all mapped tests passed
    PARTIAL       = "PARTIAL"        # some passed, some failed
    FAILING       = "FAILING"        # all mapped tests ran and failed
    NOT_RUN       = "NOT_RUN"        # none of the mapped tests appear in the DB
    NA            = "N/A"            # testpoint intentionally unmapped (na=True)
    UNIMPLEMENTED = "UNIMPLEMENTED"  # tests list is empty


# Standard stage ordering for gate evaluation
_STAGE_ORDER = {"V1": 0, "V2": 1, "V2S": 2, "V3": 3}


@dataclass
class TestpointResult:
    """Closure result for one testpoint."""
    testpoint:     Testpoint
    status:        TPStatus
    matched_tests: List[str]
    pass_count:    int = 0
    fail_count:    int = 0


def compute_closure(testplan: Testplan, db,
                    waivers=None) -> List[TestpointResult]:
    """Compute pass/fail closure for every testpoint against *db*.

    Args:
        testplan: The testplan to evaluate.
        db:       Any UCIS database object (must expose ``historyNodes()``).
        waivers:  Optional :class:`~ucis.ncdb.waivers.WaiverSet`; reserved
                  for future use (currently ignored).

    Returns:
        One :class:`TestpointResult` per testpoint, in testplan order.
    """
    # Build test-name → (pass_count, fail_count) from test history if available
    test_pass: Dict[str, int] = {}
    test_fail: Dict[str, int] = {}

    # Trigger lazy v2 history load for NcdbUCIS
    if hasattr(db, '_ensure_v2_history'):
        db._ensure_v2_history()

    # Try v2 binary history first (NcdbUCIS or MemUCIS with _test_registry attached)
    if getattr(db, '_test_registry', None) is not None:
        reg = db._test_registry
        stats = db._test_stats
        for nid, name in enumerate(reg._names):
            entry = stats.get(nid)
            if entry is not None:
                test_pass[name] = entry.pass_count
                test_fail[name] = entry.fail_count
    else:
        # Fall back to UCIS history nodes
        try:
            from ucis.history_node_kind import HistoryNodeKind
            for node in db.historyNodes(HistoryNodeKind.TEST):
                name = node.getLogicalName()
                try:
                    from ucis.test_status_t import TestStatusT
                    if node.getTestStatus() == TestStatusT.OK:
                        test_pass[name] = test_pass.get(name, 0) + 1
                    else:
                        test_fail[name] = test_fail.get(name, 0) + 1
                except Exception:
                    test_pass[name] = test_pass.get(name, 0) + 1
        except Exception:
            pass

    results: List[TestpointResult] = []
    for tp in testplan.testpoints:
        if tp.na:
            results.append(TestpointResult(tp, TPStatus.NA, []))
            continue
        if not tp.tests:
            results.append(TestpointResult(tp, TPStatus.UNIMPLEMENTED, []))
            continue

        matched: List[str] = []
        passes = fails = 0

        for pattern in tp.tests:
            # Exact match
            if pattern in test_pass or pattern in test_fail:
                matched.append(pattern)
                passes += test_pass.get(pattern, 0)
                fails  += test_fail.get(pattern, 0)
                continue
            # Seed-suffix strip
            stripped = re.sub(r'_\d+$', '', pattern)
            if stripped != pattern and (stripped in test_pass or stripped in test_fail):
                matched.append(stripped)
                passes += test_pass.get(stripped, 0)
                fails  += test_fail.get(stripped, 0)
                continue
            # Wildcard prefix
            if pattern.endswith('_*'):
                prefix = pattern[:-1]
                for tname in list(test_pass) + [t for t in test_fail if t not in test_pass]:
                    if tname.startswith(prefix) and tname not in matched:
                        matched.append(tname)
                        passes += test_pass.get(tname, 0)
                        fails  += test_fail.get(tname, 0)

        if not matched:
            status = TPStatus.NOT_RUN
        elif fails == 0:
            status = TPStatus.CLOSED
        elif passes == 0:
            status = TPStatus.FAILING
        else:
            status = TPStatus.PARTIAL

        results.append(TestpointResult(tp, status, matched, passes, fails))

    return results


def stage_gate_status(results: List[TestpointResult],
                      stage: str,
                      testplan: Testplan,
                      require_flake_score_below: Optional[float] = None,
                      require_coverage_pct: Optional[float] = None) -> dict:
    """Determine whether the gate for *stage* is met.

    A stage gate passes when ALL testpoints at *stage* and all stages
    with a lower standard index are CLOSED (or N/A).

    Args:
        results:                   Output of :func:`compute_closure`.
        stage:                     Stage to evaluate (e.g. ``"V2"``).
        testplan:                  The testplan (used for stage ordering).
        require_flake_score_below: Reserved — flakiness threshold (future).
        require_coverage_pct:      Reserved — coverage threshold (future).

    Returns:
        Dict with keys ``passed`` (bool), ``stage``, ``blocking``
        (list of :class:`TestpointResult` that prevent the gate from passing),
        and ``message`` (human-readable summary string).
    """
    target_rank = _STAGE_ORDER.get(stage, 99)

    # Collect all stages that must pass (≤ target rank)
    stages_required = {s for s in testplan.stages()
                       if _STAGE_ORDER.get(s, 99) <= target_rank}

    # Index results by testpoint name
    result_map = {r.testpoint.name: r for r in results}

    blocking: List[TestpointResult] = []
    for r in results:
        if r.testpoint.stage not in stages_required:
            continue
        if r.status in (TPStatus.CLOSED, TPStatus.NA, TPStatus.UNIMPLEMENTED):
            continue
        blocking.append(r)

    passed = len(blocking) == 0
    if passed:
        message = f"Stage {stage} gate PASSED"
    else:
        names = ", ".join(r.testpoint.name for r in blocking[:5])
        extra = f" (+{len(blocking)-5} more)" if len(blocking) > 5 else ""
        message = f"Stage {stage} gate FAILED — blocking: {names}{extra}"

    return {
        "passed":   passed,
        "stage":    stage,
        "blocking": blocking,
        "message":  message,
    }
