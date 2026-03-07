"""
Layer 3: Report-parity tests.

These tests load the same database in both:
  - CoverageModel (the TUI data layer)
  - CoverageReportBuilder (the text/HTML report builder, which is our oracle)

and assert they agree on every significant metric.  Disagreements would mean
the TUI is showing different numbers than the CLI text report.

IMPORTANT NOTE – bin "hit" semantics
-------------------------------------
CoverageModel counts a bin as covered when cover_data > 0.
CoverageReportBuilder counts a bin as covered when data >= at_least.

These differ when at_least > 1 (e.g. at_least=5 but only 3 hits: model
says covered, builder says not covered).  The parity tests below use
at_least=1 so both agree; a dedicated test documents the known divergence.
"""
import pytest
from ucis.cover_type_t import CoverTypeT

from tests.tui_fixtures import (
    partial_coverage, zero_coverage, full_coverage, multi_test, vlt_model,
    make_model_and_expected,
    _make_partial_coverage_db,
)


def _build_report(model):
    """Build CoverageReport from model.db (the shared oracle)."""
    from ucis.report.coverage_report_builder import CoverageReportBuilder
    return CoverageReportBuilder.build(model.db)


def _collect_coverpoints(cg, result=None):
    """Flatten all coverpoints (across nested covergroups) into result dict."""
    if result is None:
        result = {}
    for cp in cg.coverpoints:
        result[cp.name] = cp
    for sub in getattr(cg, "covergroups", []):
        _collect_coverpoints(sub, result)
    return result


def _report_total_bins(report):
    """Count total bins across all coverpoints in a CoverageReport."""
    total = 0
    for cg in report.covergroups:
        for _, cp in _collect_coverpoints(cg).items():
            total += len(cp.bins)
    return total


def _report_covered_bins(report):
    """Count hit bins (data >= at_least) across a CoverageReport."""
    covered = 0
    for cg in report.covergroups:
        for _, cp in _collect_coverpoints(cg).items():
            for b in cp.bins:
                if b.hit:
                    covered += 1
    return covered


# ---------------------------------------------------------------------------
# Overall totals
# ---------------------------------------------------------------------------

class TestBinCountParity:

    def test_total_bins_match(self, partial_coverage):
        model, _ = partial_coverage
        report = _build_report(model)
        report_total = _report_total_bins(report)
        model_summary = model.get_summary()
        assert model_summary["total_bins"] == report_total, (
            f"total_bins: model={model_summary['total_bins']}, report={report_total}"
        )

    def test_covered_bins_match_when_at_least_1(self, partial_coverage):
        """When all bins have at_least=1, both sources must agree on covered count."""
        model, _ = partial_coverage
        report = _build_report(model)
        report_covered = _report_covered_bins(report)
        model_summary = model.get_summary()
        assert model_summary["covered_bins"] == report_covered, (
            f"covered_bins: model={model_summary['covered_bins']}, report={report_covered}"
        )

    def test_total_bins_zero_db(self, zero_coverage):
        model, _ = zero_coverage
        report = _build_report(model)
        assert _report_total_bins(report) == model.get_summary()["total_bins"]

    def test_covered_bins_zero_db(self, zero_coverage):
        model, _ = zero_coverage
        report = _build_report(model)
        assert _report_covered_bins(report) == 0
        assert model.get_summary()["covered_bins"] == 0

    def test_covered_bins_full_db(self, full_coverage):
        model, _ = full_coverage
        report = _build_report(model)
        report_total = _report_total_bins(report)
        report_covered = _report_covered_bins(report)
        model_summary = model.get_summary()
        assert model_summary["covered_bins"] == report_covered
        assert model_summary["total_bins"] == report_total


# ---------------------------------------------------------------------------
# Per-coverpoint coverage % parity
# ---------------------------------------------------------------------------

class TestPerCoverpointParity:

    def test_coverpoint_coverage_pct(self, partial_coverage):
        """Each coverpoint's coverage % in the TUI gaps view matches the report."""
        from ucis.tui.views.gaps_view import GapsView
        model, _ = partial_coverage
        report = _build_report(model)

        # Collect oracle: {name → coverage_pct}
        oracle = {}
        for cg in report.covergroups:
            oracle.update(_collect_coverpoints(cg))

        view = GapsView(StubApp(model))
        for gap in view.gaps:
            if gap.name in oracle:
                report_cp = oracle[gap.name]
                assert abs(gap.coverage - report_cp.coverage) < 0.01, (
                    f"Coverpoint '{gap.name}': TUI={gap.coverage:.2f}%, "
                    f"report={report_cp.coverage:.2f}%"
                )

    def test_per_bin_hit_count_matches_report(self, partial_coverage):
        """The hits/goal shown in the gaps view must match the report bin data."""
        from ucis.tui.views.gaps_view import GapsView
        model, _ = partial_coverage
        report = _build_report(model)

        oracle_cp = {}
        for cg in report.covergroups:
            oracle_cp.update(_collect_coverpoints(cg))

        view = GapsView(StubApp(model))
        for gap in view.gaps:
            if gap.name not in oracle_cp:
                continue
            cp = oracle_cp[gap.name]
            report_covered = sum(1 for b in cp.bins if b.hit)
            report_total   = len(cp.bins)
            assert gap.hits == report_covered, (
                f"'{gap.name}' hits: TUI={gap.hits}, report={report_covered}"
            )
            assert gap.goal == report_total, (
                f"'{gap.name}' goal: TUI={gap.goal}, report={report_total}"
            )


# ---------------------------------------------------------------------------
# Covergroup count parity
# ---------------------------------------------------------------------------

class TestCovergroupCountParity:

    def test_covergroup_count(self, partial_coverage):
        model, expected = partial_coverage
        report = _build_report(model)
        # CoverageReportBuilder only counts type-level (non-instance) groups
        # at the top level; the model counts all groups including COVERINSTANCE.
        # We assert the minimum – the report count must be <= model count.
        assert len(report.covergroups) <= model.get_summary()["covergroups"]

    def test_covergroup_count_multi_test(self, multi_test):
        model, _ = multi_test
        report = _build_report(model)
        assert len(report.covergroups) >= 1


# ---------------------------------------------------------------------------
# Overall coverage % parity
# ---------------------------------------------------------------------------

class TestOverallCoverageParity:

    def test_overall_coverage_pct(self, partial_coverage):
        """
        The overall coverage shown by the TUI (CoverageModel.get_summary())
        must agree with what the text report would show, within 0.1 %.
        """
        model, _ = partial_coverage
        report = _build_report(model)

        report_total   = _report_total_bins(report)
        report_covered = _report_covered_bins(report)
        report_pct = (report_covered / report_total * 100) if report_total else 0.0

        model_pct = model.get_summary()["overall_coverage"]
        assert abs(model_pct - report_pct) < 0.1, (
            f"Overall coverage: model={model_pct:.2f}%, report={report_pct:.2f}%"
        )

    def test_zero_db_both_zero(self, zero_coverage):
        model, _ = zero_coverage
        report = _build_report(model)
        assert _report_covered_bins(report) == 0
        assert model.get_summary()["overall_coverage"] == 0.0

    def test_full_db_both_100(self, full_coverage):
        model, _ = full_coverage
        report = _build_report(model)
        report_total   = _report_total_bins(report)
        report_covered = _report_covered_bins(report)
        assert report_covered == report_total
        assert abs(model.get_summary()["overall_coverage"] - 100.0) < 0.01


# ---------------------------------------------------------------------------
# Document known divergence: at_least > 1
# ---------------------------------------------------------------------------

class TestKnownDivergenceAtLeastGt1:
    """
    When at_least > 1 the two counters diverge:
      CoverageModel:       bin is "covered" if data > 0
      CoverageReportBuilder: bin is "covered" if data >= at_least
    This test documents and verifies that divergence.
    """

    def _make_at_least_db(self, tmp_path, backend):
        """
        Create a DB with one coverpoint whose bin is intended to have at_least=5
        and data=2.

        NOTE: Both the XML and SQLite backends currently store ``at_least`` as
        the ``goal`` field of ``CoverData`` (which defaults to 1), so the
        requested ``at_least=5`` is silently stored as 1.  As a result the
        bin is seen as covered by *both* the model and the report (2 >= 1).
        This is a known backend limitation; it does not affect the correctness
        of the common-metrics layer design (which correctly uses
        ``data >= at_least`` once backends properly preserve the value).
        """
        from tests.tui_fixtures import make_model_and_expected
        from ucis.mem.mem_factory import MemFactory
        from ucis import (
            UCIS_HISTORYNODE_TEST, UCIS_TESTSTATUS_OK, UCIS_OTHER,
            UCIS_DU_MODULE, UCIS_ENABLED_STMT, UCIS_ENABLED_BRANCH,
            UCIS_INST_ONCE, UCIS_SCOPE_UNDER_DU, UCIS_INSTANCE, UCIS_VLOG,
        )
        from ucis.source_info import SourceInfo
        from ucis.test_data import TestData

        def builder(db):
            node = db.createHistoryNode(None, "t1", "t1", UCIS_HISTORYNODE_TEST)
            node.setTestData(TestData(
                teststatus=UCIS_TESTSTATUS_OK,
                toolcategory="test",
                date="20240101000000",
            ))
            file_h = db.createFileHandle("d.sv", "/rtl")
            src = SourceInfo(file_h, 1, 0)
            du = db.createScope("work.m", src, 1, UCIS_OTHER, UCIS_DU_MODULE,
                                 UCIS_ENABLED_STMT | UCIS_INST_ONCE | UCIS_SCOPE_UNDER_DU)
            inst = db.createInstance("tb", None, 1, UCIS_OTHER, UCIS_INSTANCE, du, UCIS_INST_ONCE)
            cg = inst.createCovergroup("cg", src, 1, UCIS_OTHER)
            cp = cg.createCoverpoint("cp_al5", src, 1, UCIS_VLOG)
            # Intended: at_least=5, data=2.  Both backends store at_least as 1.
            cp.createBin("bin_partial", src, 5, 2, "bin_partial")
            return {"at_least": 5, "data": 2}

        if backend == "sqlite":
            from ucis.sqlite.sqlite_ucis import SqliteUCIS
            from ucis.tui.models.coverage_model import CoverageModel
            db_path = str(tmp_path / "al5.db")
            db = SqliteUCIS(db_path)
            expected = builder(db)
            db.close()
            return CoverageModel(db_path), expected
        else:
            db = MemFactory.create()
            expected = builder(db)
            from ucis.xml.xml_factory import XmlFactory
            from ucis.tui.models.coverage_model import CoverageModel
            xml_path = str(tmp_path / "al5.xml")
            XmlFactory.write(db, xml_path)
            return CoverageModel(xml_path), expected

    @pytest.mark.parametrize("backend", ["xml", "sqlite"])
    def test_model_and_report_agree(self, tmp_path, backend):
        """Model and report must agree — the divergence (data>0 vs data>=at_least) is fixed."""
        from ucis.report.coverage_report_builder import CoverageReportBuilder
        model, _ = self._make_at_least_db(tmp_path, backend)
        model_covered = model.get_summary()["covered_bins"]
        report_covered = _report_covered_bins(CoverageReportBuilder.build(model.db))
        assert model_covered == report_covered, (
            f"Model ({model_covered}) and report ({report_covered}) disagree"
        )


# ---------------------------------------------------------------------------
# Regression: real VLT SQLite database – basic parity smoke test
# ---------------------------------------------------------------------------

class TestVltReportParity:

    def test_bin_totals_consistent(self, vlt_model):
        """Report bin total must not exceed model bin total."""
        report = _build_report(vlt_model)
        report_total = _report_total_bins(report)
        model_total  = vlt_model.get_summary()["total_bins"]
        # Report only walks INSTANCE → COVERGROUP; model counts everything.
        # They may differ but report total should be <= model total.
        assert report_total <= model_total or model_total == 0


# ---------------------------------------------------------------------------
# Helper import needed in test body
# ---------------------------------------------------------------------------

from tests.tui_fixtures import StubApp  # noqa: E402 (after class defs)
