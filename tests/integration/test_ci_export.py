"""Integration tests for Phase 3: reports, exports, and CI helpers."""

from __future__ import annotations

import io
import json
import os
import shutil
import tempfile
from xml.etree import ElementTree as ET

import pytest

from ucis.ncdb.constants import HIST_STATUS_FAIL, HIST_STATUS_OK
from ucis.ncdb.ncdb_ucis import NcdbUCIS
from ucis.ncdb.ncdb_writer import NcdbWriter
from ucis.ncdb.testplan import CovergroupEntry, Testplan, Testpoint
from ucis.ncdb.testplan_closure import TPStatus, compute_closure
from ucis.ncdb.testplan_export import (
    export_github_annotations,
    export_junit_xml,
    export_summary_markdown,
)
from ucis.ncdb.reports import (
    report_testpoint_closure,
    report_stage_gate,
    report_regression_delta,
    format_testpoint_closure,
    format_stage_gate,
    format_regression_delta,
)


# ── helpers ───────────────────────────────────────────────────────────────────

@pytest.fixture()
def tmpdir_path():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


def _make_db(path: str, runs: list) -> NcdbUCIS:
    """Create an NcdbUCIS at *path* with v2 history from *runs*.

    Each element of *runs* is (test_name, status) where status is
    HIST_STATUS_OK or HIST_STATUS_FAIL.
    """
    from ucis.mem.mem_ucis import MemUCIS
    NcdbWriter().write(MemUCIS(), path)
    db = NcdbUCIS(path)
    import time
    ts = int(time.time()) - len(runs) * 60
    for name, status in runs:
        db.add_test_run(
            name=name,
            seed=1,
            status=status,
            ts=ts,
        )
        ts += 60
    return db


def _make_plan() -> Testplan:
    plan = Testplan(source_file="uart.hjson")
    plan.add_testpoint(
        Testpoint(name="uart_reset", stage="V1", tests=["uart_smoke"])
    )
    plan.add_testpoint(
        Testpoint(name="uart_loopback", stage="V2", tests=["uart_loopback"])
    )
    plan.add_testpoint(
        Testpoint(name="uart_na", stage="V2", na=True)
    )
    plan.covergroups.append(CovergroupEntry(name="cg_reset"))
    return plan


def _save_and_reopen(db: NcdbUCIS, path: str) -> NcdbUCIS:
    tmp = path + ".tmp"
    NcdbWriter().write(db, tmp)
    os.replace(tmp, path)
    return NcdbUCIS(path)


# ── JUnit XML export ──────────────────────────────────────────────────────────

class TestExportJunitXml:
    def test_creates_valid_junit_xml(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "cov.cdb")
        db = _make_db(path, [
            ("uart_smoke", HIST_STATUS_OK),
            ("uart_loopback", HIST_STATUS_FAIL),
        ])
        plan = _make_plan()
        results = compute_closure(plan, db)

        xml_path = os.path.join(tmpdir_path, "results.xml")
        export_junit_xml(results, xml_path)

        assert os.path.exists(xml_path)
        tree = ET.parse(xml_path)
        root = tree.getroot()
        assert root.tag == "testsuite"
        cases = root.findall("testcase")
        assert len(cases) == len(results)

    def test_closed_testpoint_has_no_failure(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "cov.cdb")
        db = _make_db(path, [("uart_smoke", HIST_STATUS_OK)])
        plan = _make_plan()
        results = compute_closure(plan, db)

        xml_path = os.path.join(tmpdir_path, "results.xml")
        export_junit_xml(results, xml_path)

        tree = ET.parse(xml_path)
        reset_tc = next(
            tc for tc in tree.findall(".//testcase")
            if tc.attrib["name"] == "uart_reset"
        )
        assert reset_tc.find("failure") is None

    def test_failing_testpoint_has_failure_element(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "cov.cdb")
        db = _make_db(path, [("uart_loopback", HIST_STATUS_FAIL)])
        plan = _make_plan()
        results = compute_closure(plan, db)

        xml_path = os.path.join(tmpdir_path, "results.xml")
        export_junit_xml(results, xml_path)

        tree = ET.parse(xml_path)
        loop_tc = next(
            tc for tc in tree.findall(".//testcase")
            if tc.attrib["name"] == "uart_loopback"
        )
        assert loop_tc.find("failure") is not None

    def test_testpoint_names_appear_as_testcases(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "cov.cdb")
        db = _make_db(path, [("uart_smoke", HIST_STATUS_OK)])
        plan = _make_plan()
        results = compute_closure(plan, db)

        xml_path = os.path.join(tmpdir_path, "results.xml")
        export_junit_xml(results, xml_path)

        tree = ET.parse(xml_path)
        names = {tc.attrib["name"] for tc in tree.findall(".//testcase")}
        assert "uart_reset" in names
        assert "uart_loopback" in names
        assert "uart_na" in names


# ── GitHub Annotations export ─────────────────────────────────────────────────

class TestExportGithubAnnotations:
    def test_error_lines_for_failing(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "cov.cdb")
        db = _make_db(path, [("uart_loopback", HIST_STATUS_FAIL)])
        plan = _make_plan()
        results = compute_closure(plan, db)

        buf = io.StringIO()
        export_github_annotations(results, output=buf)
        lines = buf.getvalue().splitlines()

        error_lines = [l for l in lines if l.startswith("::error")]
        assert len(error_lines) >= 1
        assert any("uart_loopback" in l for l in error_lines)

    def test_warning_for_not_run_testpoint(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "cov.cdb")
        # No runs at all → uart_loopback NOT_RUN → warning
        db = _make_db(path, [])
        plan = _make_plan()
        plan2 = Testplan(source_file="test.hjson")
        plan2.add_testpoint(Testpoint(name="tp_not_run", stage="V1",
                                       tests=["tp_not_run"]))
        results = compute_closure(plan2, db)

        buf = io.StringIO()
        export_github_annotations(results, output=buf)
        lines = buf.getvalue().splitlines()

        warning_lines = [l for l in lines if l.startswith("::warning")]
        assert len(warning_lines) >= 1

    def test_no_output_for_closed(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "cov.cdb")
        db = _make_db(path, [("uart_smoke", HIST_STATUS_OK)])
        plan = Testplan(source_file="test.hjson")
        plan.add_testpoint(
            Testpoint(name="uart_reset", stage="V1", tests=["uart_smoke"])
        )
        results = compute_closure(plan, db)

        buf = io.StringIO()
        export_github_annotations(results, output=buf)
        text = buf.getvalue()
        assert text.strip() == ""


# ── Markdown summary ──────────────────────────────────────────────────────────

class TestExportSummaryMarkdown:
    def test_returns_valid_markdown(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "cov.cdb")
        db = _make_db(path, [
            ("uart_smoke", HIST_STATUS_OK),
            ("uart_loopback", HIST_STATUS_FAIL),
        ])
        plan = _make_plan()
        results = compute_closure(plan, db)

        md = export_summary_markdown(results)
        assert "## Testplan Closure Report" in md
        assert "uart_reset" in md

    def test_stage_gate_in_markdown(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "cov.cdb")
        db = _make_db(path, [("uart_smoke", HIST_STATUS_OK)])
        plan = _make_plan()
        results = compute_closure(plan, db)

        gate = report_stage_gate(results, "V1", plan)
        md = export_summary_markdown(results, stage_gate=gate)
        assert "Stage gate" in md
        assert "V1" in md


# ── Structured reports end-to-end ────────────────────────────────────────────

class TestReportsEndToEnd:
    def test_closure_report_all_closed(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "cov.cdb")
        db = _make_db(path, [
            ("uart_smoke", HIST_STATUS_OK),
            ("uart_loopback", HIST_STATUS_OK),
        ])
        plan = _make_plan()
        results = compute_closure(plan, db)
        summary = report_testpoint_closure(results)

        assert summary.total == 3
        assert summary.total_na == 1
        # uart_reset (closed) + uart_loopback (closed) + uart_na (N/A)
        assert summary.total_closed == 2

    def test_stage_gate_v1_passes_when_closed(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "cov.cdb")
        db = _make_db(path, [("uart_smoke", HIST_STATUS_OK)])
        plan = _make_plan()
        results = compute_closure(plan, db)

        gate = report_stage_gate(results, "V1", plan)
        assert gate.passed is True
        text = format_stage_gate(gate)
        assert "PASS" in text

    def test_stage_gate_v2_fails_when_loopback_not_run(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "cov.cdb")
        # Only uart_smoke runs, no uart_loopback
        db = _make_db(path, [("uart_smoke", HIST_STATUS_OK)])
        plan = _make_plan()
        results = compute_closure(plan, db)

        gate = report_stage_gate(results, "V2", plan)
        assert gate.passed is False
        blocking_names = [r.testpoint.name for r in gate.blocking]
        assert "uart_loopback" in blocking_names

    def test_regression_delta_detects_newly_closed(self, tmpdir_path):
        path_old = os.path.join(tmpdir_path, "old.cdb")
        path_new = os.path.join(tmpdir_path, "new.cdb")
        plan = _make_plan()

        db_old = _make_db(path_old, [])  # nothing passes
        db_new = _make_db(path_new, [
            ("uart_smoke", HIST_STATUS_OK),
        ])

        results_old = compute_closure(plan, db_old)
        results_new = compute_closure(plan, db_new)
        delta = report_regression_delta(results_new, results_old)

        newly_closed_names = [r.testpoint.name for r in delta.newly_closed]
        assert "uart_reset" in newly_closed_names

    def test_closure_to_json_roundtrip(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "cov.cdb")
        db = _make_db(path, [("uart_smoke", HIST_STATUS_OK)])
        plan = _make_plan()
        results = compute_closure(plan, db)
        summary = report_testpoint_closure(results)

        d = json.loads(summary.to_json())
        assert d["total"] == 3
        assert any(r["name"] == "uart_reset" for r in d["testpoints"])

    def test_format_closure_text_output(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "cov.cdb")
        db = _make_db(path, [("uart_smoke", HIST_STATUS_OK)])
        plan = _make_plan()
        results = compute_closure(plan, db)
        summary = report_testpoint_closure(results)

        text = format_testpoint_closure(summary)
        assert "uart_reset" in text
        assert "CLOSED" in text
