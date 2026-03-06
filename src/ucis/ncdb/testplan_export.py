"""CI/CD export utilities for testplan closure results.

Provides three output formats:

* **JUnit XML** — standard ``<testsuite>`` / ``<testcase>`` format for CI
  systems (Jenkins, GitHub Actions, GitLab CI, etc.)
* **GitHub Annotations** — ``::error::`` / ``::warning::`` lines written to
  stdout for GitHub Actions step annotations.
* **Summary Markdown** — GitHub Actions ``$GITHUB_STEP_SUMMARY`` compatible
  markdown table with stage gate verdict.
"""

from __future__ import annotations

import json
import sys
import time
from typing import List, Optional
from xml.etree import ElementTree as ET

from ucis.ncdb.testplan_closure import TPStatus, TestpointResult
from ucis.ncdb.reports import (
    ClosureSummary,
    StageGateReport,
    report_testpoint_closure,
    _STATUS_LABEL,
    _pct,
    _STAGE_ORDER,
)


# ---------------------------------------------------------------------------
# JUnit XML export
# ---------------------------------------------------------------------------

def export_junit_xml(
    results: List[TestpointResult],
    output_path: str,
    suite_name: str = "testplan_closure",
) -> None:
    """Write closure results as a JUnit XML file.

    Each testpoint becomes a ``<testcase>``.  Testpoints with status
    FAILING or PARTIAL get a ``<failure>`` element; NOT_RUN gets a
    ``<skipped>`` element; CLOSED is a plain pass.

    Args:
        results: Output of
            :func:`~ucis.ncdb.testplan_closure.compute_closure`.
        output_path: Destination ``.xml`` file path.
        suite_name: Value of the ``name`` attribute on ``<testsuite>``.

    Example::

        from ucis.ncdb.testplan_export import export_junit_xml
        export_junit_xml(results, "closure_results.xml")
    """
    failures = sum(
        1 for r in results if r.status in (TPStatus.FAILING, TPStatus.PARTIAL)
    )
    skipped = sum(1 for r in results if r.status == TPStatus.NOT_RUN)
    total = len(results)

    suite = ET.Element(
        "testsuite",
        name=suite_name,
        tests=str(total),
        failures=str(failures),
        skipped=str(skipped),
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
    )

    for r in results:
        classname = r.testpoint.stage or "unknown"
        tc = ET.SubElement(
            suite,
            "testcase",
            name=r.testpoint.name,
            classname=classname,
        )
        if r.testpoint.desc:
            ET.SubElement(tc, "system-out").text = r.testpoint.desc

        if r.status == TPStatus.FAILING:
            ET.SubElement(
                tc,
                "failure",
                message=f"Testpoint FAILING: "
                        f"pass={r.pass_count} fail={r.fail_count}",
                type="TestpointFailure",
            ).text = (
                f"Matched tests: {', '.join(r.matched_tests) or 'none'}\n"
                f"Pass: {r.pass_count}  Fail: {r.fail_count}"
            )
        elif r.status == TPStatus.PARTIAL:
            ET.SubElement(
                tc,
                "failure",
                message=f"Testpoint PARTIAL: "
                        f"pass={r.pass_count} fail={r.fail_count}",
                type="TestpointPartial",
            ).text = (
                f"Matched tests: {', '.join(r.matched_tests) or 'none'}\n"
                f"Pass: {r.pass_count}  Fail: {r.fail_count}"
            )
        elif r.status == TPStatus.NOT_RUN:
            ET.SubElement(tc, "skipped", message="Testpoint not run")

    tree = ET.ElementTree(suite)
    ET.indent(tree, space="  ")
    tree.write(output_path, encoding="utf-8", xml_declaration=True)


# ---------------------------------------------------------------------------
# GitHub Annotations export
# ---------------------------------------------------------------------------

def export_github_annotations(
    results: List[TestpointResult],
    file: str = "testplan",
    *,
    output=None,
) -> None:
    """Write GitHub Actions workflow command annotations to *output*.

    FAILING testpoints emit ``::error::`` lines; PARTIAL and NOT_RUN emit
    ``::warning::`` lines.  CLOSED and N/A produce no output.

    Args:
        results: Output of
            :func:`~ucis.ncdb.testplan_closure.compute_closure`.
        file: Value used in the ``file=`` annotation field (defaults to
            ``"testplan"``).
        output: File-like object to write to (defaults to ``sys.stdout``).

    Example::

        from ucis.ncdb.testplan_export import export_github_annotations
        export_github_annotations(results)  # writes to stdout
    """
    if output is None:
        output = sys.stdout

    for r in results:
        if r.status == TPStatus.CLOSED or r.status == TPStatus.NA:
            continue
        title = f"[{r.testpoint.stage}] {r.testpoint.name}"
        msg = (
            f"status={_STATUS_LABEL[r.status]} "
            f"pass={r.pass_count} fail={r.fail_count}"
        )
        if r.status == TPStatus.FAILING:
            output.write(
                f"::error file={file},title={title}::{msg}\n"
            )
        else:
            output.write(
                f"::warning file={file},title={title}::{msg}\n"
            )


# ---------------------------------------------------------------------------
# Markdown summary export
# ---------------------------------------------------------------------------

def export_summary_markdown(
    results: List[TestpointResult],
    stage_gate: Optional[StageGateReport] = None,
    history_db=None,
) -> str:
    """Generate a GitHub Actions Job Summary–compatible markdown string.

    Args:
        results: Output of
            :func:`~ucis.ncdb.testplan_closure.compute_closure`.
        stage_gate: Optional :class:`~ucis.ncdb.reports.StageGateReport`
            to include a gate verdict section.
        history_db: Unused; reserved for future trend lines.

    Returns:
        A markdown string suitable for appending to
        ``$GITHUB_STEP_SUMMARY``.

    Example::

        from ucis.ncdb.testplan_export import export_summary_markdown
        md = export_summary_markdown(results, stage_gate=gate)
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write(md)
    """
    summary = report_testpoint_closure(results)
    lines: List[str] = []

    # Headline
    total = summary.total
    closed = summary.total_closed
    na = summary.total_na
    lines.append("## Testplan Closure Report\n")
    lines.append(
        f"**{closed}/{total}** testpoints closed "
        f"({na} N/A, {total - closed - na} open)\n"
    )

    # Stage gate verdict
    if stage_gate is not None:
        verdict = "✅ PASS" if stage_gate.passed else "❌ FAIL"
        lines.append(f"**Stage gate [{stage_gate.stage}]:** {verdict}\n")

    # Stage roll-up table
    ordered_stages = sorted(
        summary.by_stage.items(),
        key=lambda kv: _STAGE_ORDER.get(kv[0], 999),
    )
    if ordered_stages:
        lines.append("### By stage\n")
        lines.append("| Stage | Closed | Total | % |")
        lines.append("|-------|-------:|------:|--:|")
        for stage, entry in ordered_stages:
            lines.append(
                f"| {stage} | {entry['closed']} | {entry['total']} "
                f"| {entry['pct']:.1f}% |"
            )
        lines.append("")

    # Testpoint detail table — only non-N/A
    visible = [r for r in results if r.status not in (TPStatus.NA, TPStatus.UNIMPLEMENTED)]
    if visible:
        lines.append("### Testpoints\n")
        lines.append("| Testpoint | Stage | Status | Pass | Fail |")
        lines.append("|-----------|-------|--------|-----:|-----:|")
        _EMOJI = {
            TPStatus.CLOSED: "✅",
            TPStatus.PARTIAL: "⚠️",
            TPStatus.FAILING: "❌",
            TPStatus.NOT_RUN: "⬜",
        }
        for r in visible:
            emoji = _EMOJI.get(r.status, "")
            lines.append(
                f"| {r.testpoint.name} | {r.testpoint.stage or '?'} "
                f"| {emoji} {_STATUS_LABEL[r.status]} "
                f"| {r.pass_count} | {r.fail_count} |"
            )
        lines.append("")

    # Blocking testpoints
    if stage_gate is not None and stage_gate.blocking:
        lines.append("### Blocking testpoints\n")
        for r in stage_gate.blocking:
            lines.append(
                f"- ❌ **[{r.testpoint.stage}] {r.testpoint.name}** "
                f"— {_STATUS_LABEL[r.status]}"
            )
        lines.append("")

    return "\n".join(lines)
