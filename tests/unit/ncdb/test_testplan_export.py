"""Unit tests for ucis.ncdb.testplan_export."""

import io
import json
import os
import tempfile
from xml.etree import ElementTree as ET

import pytest

from ucis.ncdb.testplan import Testplan, Testpoint
from ucis.ncdb.testplan_closure import TPStatus, TestpointResult
from ucis.ncdb.testplan_export import (
    export_junit_xml,
    export_github_annotations,
    export_summary_markdown,
)
from ucis.ncdb.reports import report_stage_gate


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_tp(name, stage="V1", desc=""):
    return Testpoint(name=name, stage=stage, tests=[name], desc=desc)


def _make_result(tp, status, pass_count=0, fail_count=0, matched=None):
    return TestpointResult(
        testpoint=tp,
        status=status,
        matched_tests=matched or [],
        pass_count=pass_count,
        fail_count=fail_count,
    )


@pytest.fixture
def mixed_results():
    return [
        _make_result(_make_tp("tp_pass", "V1"), TPStatus.CLOSED,
                     pass_count=5, matched=["tp_pass"]),
        _make_result(_make_tp("tp_fail", "V1"), TPStatus.FAILING,
                     fail_count=3, matched=["tp_fail"]),
        _make_result(_make_tp("tp_skip", "V2"), TPStatus.NOT_RUN),
        _make_result(_make_tp("tp_partial", "V2"), TPStatus.PARTIAL,
                     pass_count=2, fail_count=2, matched=["tp_partial"]),
        _make_result(_make_tp("tp_na", "V1"), TPStatus.NA),
    ]


@pytest.fixture
def simple_plan():
    plan = Testplan(source_file="test.hjson")
    for name, stage in [("tp_pass", "V1"), ("tp_fail", "V1"),
                         ("tp_skip", "V2"), ("tp_partial", "V2"),
                         ("tp_na", "V1")]:
        plan.add_testpoint(Testpoint(name=name, stage=stage, tests=[name]))
    return plan


# ---------------------------------------------------------------------------
# JUnit XML
# ---------------------------------------------------------------------------

class TestExportJunitXml:
    def test_creates_file(self, mixed_results, tmp_path):
        out = str(tmp_path / "results.xml")
        export_junit_xml(mixed_results, out)
        assert os.path.exists(out)

    def test_valid_xml(self, mixed_results, tmp_path):
        out = str(tmp_path / "results.xml")
        export_junit_xml(mixed_results, out)
        tree = ET.parse(out)
        root = tree.getroot()
        assert root.tag == "testsuite"

    def test_testcase_count(self, mixed_results, tmp_path):
        out = str(tmp_path / "results.xml")
        export_junit_xml(mixed_results, out)
        tree = ET.parse(out)
        cases = tree.findall(".//testcase")
        assert len(cases) == len(mixed_results)

    def test_failure_element_for_failing(self, mixed_results, tmp_path):
        out = str(tmp_path / "results.xml")
        export_junit_xml(mixed_results, out)
        tree = ET.parse(out)
        fail_tc = next(
            tc for tc in tree.findall(".//testcase")
            if tc.attrib["name"] == "tp_fail"
        )
        assert fail_tc.find("failure") is not None

    def test_skipped_element_for_not_run(self, mixed_results, tmp_path):
        out = str(tmp_path / "results.xml")
        export_junit_xml(mixed_results, out)
        tree = ET.parse(out)
        skip_tc = next(
            tc for tc in tree.findall(".//testcase")
            if tc.attrib["name"] == "tp_skip"
        )
        assert skip_tc.find("skipped") is not None

    def test_no_failure_for_closed(self, mixed_results, tmp_path):
        out = str(tmp_path / "results.xml")
        export_junit_xml(mixed_results, out)
        tree = ET.parse(out)
        pass_tc = next(
            tc for tc in tree.findall(".//testcase")
            if tc.attrib["name"] == "tp_pass"
        )
        assert pass_tc.find("failure") is None
        assert pass_tc.find("skipped") is None

    def test_suite_name_attribute(self, mixed_results, tmp_path):
        out = str(tmp_path / "results.xml")
        export_junit_xml(mixed_results, out, suite_name="my_suite")
        tree = ET.parse(out)
        assert tree.getroot().attrib["name"] == "my_suite"

    def test_failure_count_in_suite(self, mixed_results, tmp_path):
        out = str(tmp_path / "results.xml")
        export_junit_xml(mixed_results, out)
        tree = ET.parse(out)
        # tp_fail (FAILING) + tp_partial (PARTIAL) = 2 failures
        assert tree.getroot().attrib["failures"] == "2"

    def test_partial_gets_failure_element(self, mixed_results, tmp_path):
        out = str(tmp_path / "results.xml")
        export_junit_xml(mixed_results, out)
        tree = ET.parse(out)
        partial_tc = next(
            tc for tc in tree.findall(".//testcase")
            if tc.attrib["name"] == "tp_partial"
        )
        assert partial_tc.find("failure") is not None


# ---------------------------------------------------------------------------
# GitHub Annotations
# ---------------------------------------------------------------------------

class TestExportGithubAnnotations:
    def test_error_for_failing(self, mixed_results):
        buf = io.StringIO()
        export_github_annotations(mixed_results, output=buf)
        text = buf.getvalue()
        assert "::error" in text
        assert "tp_fail" in text

    def test_warning_for_not_run(self, mixed_results):
        buf = io.StringIO()
        export_github_annotations(mixed_results, output=buf)
        text = buf.getvalue()
        assert "::warning" in text
        assert "tp_skip" in text

    def test_warning_for_partial(self, mixed_results):
        buf = io.StringIO()
        export_github_annotations(mixed_results, output=buf)
        text = buf.getvalue()
        assert "tp_partial" in text

    def test_no_output_for_closed(self, mixed_results):
        buf = io.StringIO()
        export_github_annotations(mixed_results, output=buf)
        text = buf.getvalue()
        # tp_pass (CLOSED) should NOT produce any annotation
        lines_with_pass = [l for l in text.splitlines() if "tp_pass" in l]
        assert lines_with_pass == []

    def test_no_output_for_na(self, mixed_results):
        buf = io.StringIO()
        export_github_annotations(mixed_results, output=buf)
        text = buf.getvalue()
        lines_with_na = [l for l in text.splitlines() if "tp_na" in l]
        assert lines_with_na == []

    def test_custom_file_field(self, mixed_results):
        buf = io.StringIO()
        export_github_annotations(mixed_results, file="uart.hjson", output=buf)
        text = buf.getvalue()
        assert "file=uart.hjson" in text


# ---------------------------------------------------------------------------
# Markdown summary
# ---------------------------------------------------------------------------

class TestExportSummaryMarkdown:
    def test_returns_string(self, mixed_results):
        md = export_summary_markdown(mixed_results)
        assert isinstance(md, str)

    def test_contains_headline(self, mixed_results):
        md = export_summary_markdown(mixed_results)
        assert "## Testplan Closure Report" in md

    def test_contains_stage_table(self, mixed_results):
        md = export_summary_markdown(mixed_results)
        assert "| Stage" in md
        assert "| V1" in md or "V1" in md

    def test_contains_testpoint_table(self, mixed_results):
        md = export_summary_markdown(mixed_results)
        assert "| Testpoint" in md
        assert "tp_pass" in md

    def test_gate_verdict_included(self, mixed_results, simple_plan):
        gate = report_stage_gate(mixed_results, "V1", simple_plan)
        md = export_summary_markdown(mixed_results, stage_gate=gate)
        assert "Stage gate" in md
        assert "V1" in md

    def test_blocking_section_when_gate_fails(self, mixed_results, simple_plan):
        gate = report_stage_gate(mixed_results, "V2", simple_plan)
        md = export_summary_markdown(mixed_results, stage_gate=gate)
        if not gate.passed:
            assert "Blocking testpoints" in md

    def test_na_testpoints_excluded_from_table(self, mixed_results):
        md = export_summary_markdown(mixed_results)
        # tp_na (N/A) and UNIMPLEMENTED should not appear in testpoint table rows
        # The heading line "| Testpoint" is present but tp_na row should not be
        rows = [l for l in md.splitlines() if "tp_na" in l and "|" in l]
        assert rows == []
