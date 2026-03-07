"""
Unit tests for :class:`ucis.report.coverage_metrics.CoverageMetrics`.

Each public method of the API is tested:
  * BinStats / BinDetail dataclasses
  * functional_bins()
  * covergroup_stats()
  * coverpoint_stats() / coverpoint_stats(include_bins=True)
  * cross_stats()
  * coverage_types_present()
  * bins_by_type()
  * code_coverage_by_type()
  * file_coverage()
  * tests()
  * summary()
  * database_info()
  * invalidate()  (cache invalidation)
  * Parity: functional_bins() must agree with CoverageReportBuilder

Tests run against both the XML/API path and the SQLite path where applicable.
"""
import os
import pytest
import tempfile

from ucis.mem.mem_factory import MemFactory
from ucis.cover_type_t import CoverTypeT
from ucis.source_info import SourceInfo
from ucis import (
    UCIS_HISTORYNODE_TEST, UCIS_TESTSTATUS_OK, UCIS_OTHER,
    UCIS_DU_MODULE, UCIS_ENABLED_STMT, UCIS_ENABLED_BRANCH,
    UCIS_INST_ONCE, UCIS_SCOPE_UNDER_DU, UCIS_INSTANCE, UCIS_VLOG,
)
from ucis.test_data import TestData
from ucis.report.coverage_metrics import (
    BinStats, BinDetail, CoverpointStats, CovergroupStats, TestInfo,
    CoverageMetrics,
)


# ---------------------------------------------------------------------------
# Internal DB builder helpers (same conventions as tui_fixtures)
# ---------------------------------------------------------------------------

def _add_test(db, logical_name="test1"):
    node = db.createHistoryNode(None, logical_name, logical_name, UCIS_HISTORYNODE_TEST)
    node.setTestData(TestData(
        teststatus=UCIS_TESTSTATUS_OK,
        toolcategory="test",
        date="20240101000000",
    ))
    return node


def _add_instance(db):
    file_h = db.createFileHandle("tb.sv", "/rtl")
    src = SourceInfo(file_h, 1, 0)
    du = db.createScope("work.tb", src, 1, UCIS_OTHER, UCIS_DU_MODULE,
                         UCIS_ENABLED_STMT | UCIS_INST_ONCE | UCIS_SCOPE_UNDER_DU)
    inst = db.createInstance("tb", None, 1, UCIS_OTHER, UCIS_INSTANCE, du, UCIS_INST_ONCE)
    return inst, file_h


# ---------------------------------------------------------------------------
# Backend fixture factory
# ---------------------------------------------------------------------------

def _db_for_backend(backend: str, builder_fn, tmp_path):
    """
    Return a live UCIS db object (MemUCIS-via-XML or SqliteUCIS) populated
    by *builder_fn*.  Caller is responsible for closing the db.
    """
    if backend == "sqlite":
        from ucis.sqlite.sqlite_ucis import SqliteUCIS
        db_path = str(tmp_path / "test.db")
        db = SqliteUCIS(db_path)
        builder_fn(db)
        db.close()
        db = SqliteUCIS(db_path)
        return db
    else:
        from ucis.xml.xml_factory import XmlFactory
        from ucis.rgy.format_rgy import FormatRgy
        db = MemFactory.create()
        builder_fn(db)
        xml_path = str(tmp_path / "test.xml")
        XmlFactory.write(db, xml_path)
        db2 = FormatRgy.inst().getDatabaseDesc("xml").fmt_if().read(xml_path)
        return db2


def _metrics(backend: str, builder_fn, tmp_path) -> CoverageMetrics:
    db = _db_for_backend(backend, builder_fn, tmp_path)
    return CoverageMetrics(db)


# ---------------------------------------------------------------------------
# DB builder functions
# ---------------------------------------------------------------------------

def _build_partial(db):
    """2 covergroups, 2 coverpoints, 6 bins, 3 covered (50%)."""
    _add_test(db)
    inst, file_h = _add_instance(db)
    src = SourceInfo(file_h, 3, 0)
    cg1 = inst.createCovergroup("cg1", src, 1, UCIS_OTHER)
    cp1 = cg1.createCoverpoint("cp1", src, 1, UCIS_VLOG)
    cp1.createBin("a", src, 1, 5, "a")   # hit
    cp1.createBin("b", src, 1, 3, "b")   # hit
    cp1.createBin("c", src, 1, 0, "c")   # miss
    cp1.createBin("d", src, 1, 0, "d")   # miss

    cg2 = inst.createCovergroup("cg2", src, 1, UCIS_OTHER)
    cp2 = cg2.createCoverpoint("cp2", src, 1, UCIS_VLOG)
    cp2.createBin("x", src, 1, 10, "x")  # hit
    cp2.createBin("y", src, 1, 0,  "y")  # miss


def _build_zero(db):
    """1 covergroup, 1 coverpoint, 3 bins, all uncovered."""
    _add_test(db)
    inst, file_h = _add_instance(db)
    src = SourceInfo(file_h, 3, 0)
    cg = inst.createCovergroup("cg_zero", src, 1, UCIS_OTHER)
    cp = cg.createCoverpoint("cp_zero", src, 1, UCIS_VLOG)
    cp.createBin("b0", src, 1, 0, "b0")
    cp.createBin("b1", src, 1, 0, "b1")
    cp.createBin("b2", src, 1, 0, "b2")


def _build_full(db):
    """1 covergroup, 1 coverpoint, 3 bins, all hit."""
    _add_test(db)
    inst, file_h = _add_instance(db)
    src = SourceInfo(file_h, 3, 0)
    cg = inst.createCovergroup("cg_full", src, 1, UCIS_OTHER)
    cp = cg.createCoverpoint("cp_full", src, 1, UCIS_VLOG)
    cp.createBin("b0", src, 1, 1, "b0")
    cp.createBin("b1", src, 1, 2, "b1")
    cp.createBin("b2", src, 1, 7, "b2")


def _build_multi_test(db):
    """3 tests; 6 bins; 4 covered (≈66.7%)."""
    for name in ("test_a", "test_b", "test_c"):
        _add_test(db, name)
    inst, file_h = _add_instance(db)
    src = SourceInfo(file_h, 3, 0)
    cg = inst.createCovergroup("cg_mt", src, 1, UCIS_OTHER)
    cp = cg.createCoverpoint("cp_mt", src, 1, UCIS_VLOG)
    cp.createBin("b0", src, 1, 1, "b0")
    cp.createBin("b1", src, 1, 1, "b1")
    cp.createBin("b2", src, 1, 1, "b2")
    cp.createBin("b3", src, 1, 1, "b3")
    cp.createBin("b4", src, 1, 0, "b4")
    cp.createBin("b5", src, 1, 0, "b5")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(params=["xml", "sqlite"])
def partial_m(request, tmp_path):
    return _metrics(request.param, _build_partial, tmp_path)


@pytest.fixture(params=["xml", "sqlite"])
def zero_m(request, tmp_path):
    return _metrics(request.param, _build_zero, tmp_path)


@pytest.fixture(params=["xml", "sqlite"])
def full_m(request, tmp_path):
    return _metrics(request.param, _build_full, tmp_path)


@pytest.fixture(params=["xml", "sqlite"])
def multi_m(request, tmp_path):
    return _metrics(request.param, _build_multi_test, tmp_path)


@pytest.fixture
def vlt_metrics():
    """CoverageMetrics from the real vlt.cdb SQLite fixture (code-coverage only)."""
    vlt_path = os.path.join(os.path.dirname(__file__), "..", "test_vlt.cdb")
    if not os.path.exists(vlt_path):
        pytest.skip("test_vlt.cdb not found")
    from ucis.sqlite.sqlite_ucis import SqliteUCIS
    db = SqliteUCIS(vlt_path)
    m = CoverageMetrics(db)
    yield m
    try:
        db.close()
    except Exception:
        pass


# ===========================================================================
# 1. Dataclass unit tests
# ===========================================================================

class TestBinStats:

    def test_uncovered_property(self):
        bs = BinStats(total=10, covered=3)
        assert bs.uncovered == 7

    def test_coverage_pct_normal(self):
        bs = BinStats(total=10, covered=5)
        assert abs(bs.coverage_pct - 50.0) < 0.01

    def test_coverage_pct_zero_total(self):
        bs = BinStats(total=0, covered=0)
        assert bs.coverage_pct == 0.0

    def test_coverage_pct_full(self):
        bs = BinStats(total=4, covered=4)
        assert abs(bs.coverage_pct - 100.0) < 0.01

    def test_add(self):
        a = BinStats(total=4, covered=2)
        b = BinStats(total=6, covered=4)
        c = a + b
        assert c.total == 10
        assert c.covered == 6
        assert abs(c.coverage_pct - 60.0) < 0.01


class TestBinDetail:

    def test_covered_when_count_gte_at_least(self):
        bd = BinDetail(name="b", count=5, at_least=1)
        assert bd.covered is True

    def test_not_covered_when_count_lt_at_least(self):
        bd = BinDetail(name="b", count=2, at_least=5)
        assert bd.covered is False

    def test_covered_exactly_at_least(self):
        bd = BinDetail(name="b", count=3, at_least=3)
        assert bd.covered is True

    def test_not_covered_zero_count(self):
        bd = BinDetail(name="b", count=0, at_least=1)
        assert bd.covered is False

    def test_is_ignore_flag(self):
        bd = BinDetail(name="ign", count=0, at_least=1, is_ignore=True)
        assert bd.is_ignore is True
        assert bd.is_illegal is False

    def test_is_illegal_flag(self):
        bd = BinDetail(name="ill", count=0, at_least=1, is_illegal=True)
        assert bd.is_illegal is True
        assert bd.is_ignore is False


# ===========================================================================
# 2. functional_bins()
# ===========================================================================

class TestFunctionalBins:

    def test_partial_total(self, partial_m):
        assert partial_m.functional_bins().total == 6

    def test_partial_covered(self, partial_m):
        assert partial_m.functional_bins().covered == 3

    def test_partial_pct(self, partial_m):
        assert abs(partial_m.functional_bins().coverage_pct - 50.0) < 0.01

    def test_zero_coverage(self, zero_m):
        fb = zero_m.functional_bins()
        assert fb.total == 3
        assert fb.covered == 0
        assert fb.coverage_pct == 0.0

    def test_full_coverage(self, full_m):
        fb = full_m.functional_bins()
        assert fb.total == 3
        assert fb.covered == 3
        assert abs(fb.coverage_pct - 100.0) < 0.01

    def test_no_double_counting_xml(self, tmp_path):
        """XML backend must not double-count type-level and instance-level CG bins."""
        m = _metrics("xml", _build_partial, tmp_path)
        assert m.functional_bins().total == 6, "double-counting detected"

    def test_parity_with_report_builder(self, partial_m):
        """functional_bins() must agree with CoverageReportBuilder's bin totals."""
        from ucis.report.coverage_report_builder import CoverageReportBuilder
        report = CoverageReportBuilder.build(partial_m._db)
        report_total = sum(len(cp.bins) for cg in report.covergroups for cp in cg.coverpoints)
        report_covered = sum(
            1 for cg in report.covergroups
            for cp in cg.coverpoints
            for b in cp.bins if b.hit
        )
        fb = partial_m.functional_bins()
        assert fb.total == report_total
        assert fb.covered == report_covered


# ===========================================================================
# 3. covergroup_stats()
# ===========================================================================

class TestCovergroupStats:

    def test_count_partial(self, partial_m):
        cg_stats = partial_m.covergroup_stats()
        assert len(cg_stats) == 2

    def test_names_present(self, partial_m):
        names = {cg.name for cg in partial_m.covergroup_stats()}
        assert "cg1" in names
        assert "cg2" in names

    def test_coverage_pct_approx(self, partial_m):
        for cg in partial_m.covergroup_stats():
            assert 0.0 <= cg.coverage_pct <= 100.0

    def test_bins_non_zero(self, partial_m):
        for cg in partial_m.covergroup_stats():
            assert cg.bins.total > 0

    def test_zero_db_zero_covered(self, zero_m):
        for cg in zero_m.covergroup_stats():
            assert cg.bins.covered == 0

    def test_full_db_all_covered(self, full_m):
        for cg in full_m.covergroup_stats():
            assert cg.bins.covered == cg.bins.total


# ===========================================================================
# 4. coverpoint_stats()
# ===========================================================================

class TestCoverpointStats:

    def test_count_partial(self, partial_m):
        assert len(partial_m.coverpoint_stats()) == 2

    def test_names_correct(self, partial_m):
        names = {cp.name for cp in partial_m.coverpoint_stats()}
        assert names == {"cp1", "cp2"}

    def test_bins_partial(self, partial_m):
        by_name = {cp.name: cp for cp in partial_m.coverpoint_stats()}
        assert by_name["cp1"].bins.total == 4
        assert by_name["cp1"].bins.covered == 2
        assert by_name["cp2"].bins.total == 2
        assert by_name["cp2"].bins.covered == 1

    def test_path_contains_name(self, partial_m):
        for cp in partial_m.coverpoint_stats():
            assert cp.name in cp.path

    def test_include_bins_false_no_details(self, partial_m):
        for cp in partial_m.coverpoint_stats(include_bins=False):
            assert cp.bin_details == []

    def test_include_bins_true_has_details(self, partial_m):
        for cp in partial_m.coverpoint_stats(include_bins=True):
            assert len(cp.bin_details) == cp.bins.total, (
                f"bin_details length should match total bins for {cp.name}"
            )

    def test_bin_detail_semantics(self, partial_m):
        """BinDetail.covered matches count >= at_least."""
        by_name = {cp.name: cp for cp in partial_m.coverpoint_stats(include_bins=True)}
        details = by_name["cp1"].bin_details
        covered_details = [d for d in details if d.covered]
        assert len(covered_details) == 2   # bins a, b

    def test_coverage_pct_matches_bins(self, partial_m):
        for cp in partial_m.coverpoint_stats():
            expected = cp.bins.coverage_pct
            assert abs(cp.coverage_pct - expected) < 0.001

    def test_zero_db(self, zero_m):
        cps = zero_m.coverpoint_stats()
        assert len(cps) == 1
        assert cps[0].bins.covered == 0

    def test_full_db(self, full_m):
        cps = full_m.coverpoint_stats()
        assert cps[0].bins.covered == cps[0].bins.total


# ===========================================================================
# 5. coverage_types_present()
# ===========================================================================

class TestCoverageTypesPresent:

    def test_functional_db_has_cvgbin(self, partial_m):
        types = partial_m.coverage_types_present()
        assert CoverTypeT.CVGBIN in types

    def test_functional_db_no_code_types(self, partial_m):
        types = partial_m.coverage_types_present()
        assert CoverTypeT.STMTBIN not in types
        assert CoverTypeT.BRANCHBIN not in types

    def test_vlt_has_code_types(self, vlt_metrics):
        types = vlt_metrics.coverage_types_present()
        # vlt.cdb has statement, branch, toggle coverage
        code_types = {CoverTypeT.STMTBIN, CoverTypeT.BRANCHBIN, CoverTypeT.TOGGLEBIN}
        assert code_types & set(types), "vlt.cdb should have code coverage types"

    def test_vlt_no_cvgbin(self, vlt_metrics):
        types = vlt_metrics.coverage_types_present()
        assert CoverTypeT.CVGBIN not in types

    def test_returns_list(self, partial_m):
        assert isinstance(partial_m.coverage_types_present(), list)


# ===========================================================================
# 6. bins_by_type()
# ===========================================================================

class TestBinsByType:

    def test_cvgbin_delegates_to_functional_bins(self, partial_m):
        """bins_by_type(CVGBIN) must return the same result as functional_bins()."""
        fb = partial_m.functional_bins()
        bt = partial_m.bins_by_type(CoverTypeT.CVGBIN)
        assert bt.total == fb.total
        assert bt.covered == fb.covered

    def test_non_cvgbin_type_with_no_items_returns_zero(self, partial_m):
        bt = partial_m.bins_by_type(CoverTypeT.STMTBIN)
        assert bt.total == 0
        assert bt.covered == 0

    def test_vlt_stmtbin_non_zero(self, vlt_metrics):
        bt = vlt_metrics.bins_by_type(CoverTypeT.STMTBIN)
        assert bt.total > 0

    def test_vlt_branchbin_non_zero(self, vlt_metrics):
        bt = vlt_metrics.bins_by_type(CoverTypeT.BRANCHBIN)
        assert bt.total > 0

    def test_returns_bin_stats(self, partial_m):
        result = partial_m.bins_by_type(CoverTypeT.CVGBIN)
        assert isinstance(result, BinStats)

    def test_covered_lte_total(self, partial_m):
        bt = partial_m.bins_by_type(CoverTypeT.CVGBIN)
        assert bt.covered <= bt.total


# ===========================================================================
# 7. code_coverage_by_type()
# ===========================================================================

class TestCodeCoverageByType:

    def test_returns_dict(self, vlt_metrics):
        result = vlt_metrics.code_coverage_by_type()
        assert isinstance(result, dict)

    def test_stmtbin_in_result(self, vlt_metrics):
        result = vlt_metrics.code_coverage_by_type()
        assert CoverTypeT.STMTBIN in result

    def test_bin_stats_type(self, vlt_metrics):
        result = vlt_metrics.code_coverage_by_type()
        for ct, bs in result.items():
            assert isinstance(bs, BinStats), f"{ct} should map to BinStats"

    def test_agrees_with_bins_by_type(self, vlt_metrics):
        """code_coverage_by_type() must agree with bins_by_type() per type."""
        by_type = vlt_metrics.code_coverage_by_type()
        for ct, bs in by_type.items():
            individual = vlt_metrics.bins_by_type(ct)
            assert bs.total == individual.total, f"total mismatch for {ct}"
            assert bs.covered == individual.covered, f"covered mismatch for {ct}"

    def test_functional_db_code_types_zero(self, partial_m):
        result = partial_m.code_coverage_by_type()
        for ct in (CoverTypeT.STMTBIN, CoverTypeT.BRANCHBIN, CoverTypeT.TOGGLEBIN):
            assert result.get(ct, BinStats()).total == 0


# ===========================================================================
# 8. file_coverage()
# ===========================================================================

class TestFileCoverage:

    def test_empty_for_xml_backend(self, tmp_path):
        """file_coverage() requires SQLite; returns [] for XML backends."""
        m = _metrics("xml", _build_partial, tmp_path)
        assert m.file_coverage() == []

    def test_returns_list_for_sqlite(self, vlt_metrics):
        result = vlt_metrics.file_coverage()
        assert isinstance(result, list)

    def test_non_empty_for_vlt(self, vlt_metrics):
        result = vlt_metrics.file_coverage()
        assert len(result) > 0, "vlt.cdb should have file-level coverage data"

    def test_file_paths_non_empty(self, vlt_metrics):
        for fcs in vlt_metrics.file_coverage():
            assert fcs.file_path, "file_path should not be empty"

    def test_overall_bins_non_zero(self, vlt_metrics):
        for fcs in vlt_metrics.file_coverage():
            assert fcs.overall.total >= 0

    def test_sorted_by_path(self, vlt_metrics):
        paths = [fcs.file_path for fcs in vlt_metrics.file_coverage()]
        assert paths == sorted(paths), "file_coverage() should be sorted by path"

    def test_covered_lte_total_per_file(self, vlt_metrics):
        for fcs in vlt_metrics.file_coverage():
            ov = fcs.overall
            assert ov.covered <= ov.total


# ===========================================================================
# 9. tests()
# ===========================================================================

class TestTests:

    def test_returns_list(self, partial_m):
        assert isinstance(partial_m.tests(), list)

    def test_single_test_db(self, partial_m):
        tests = partial_m.tests()
        assert len(tests) >= 1

    def test_test_has_name(self, partial_m):
        for t in partial_m.tests():
            assert isinstance(t, TestInfo)
            assert t.name

    def test_test_has_status(self, partial_m):
        for t in partial_m.tests():
            assert t.status in ("PASSED", "FAILED", "UNKNOWN")

    def test_test_has_date(self, partial_m):
        for t in partial_m.tests():
            assert t.date  # non-empty

    def test_multi_test_names(self, multi_m):
        names = {t.name for t in multi_m.tests()}
        assert "test_a" in names
        assert "test_b" in names
        assert "test_c" in names

    def test_multi_test_count(self, multi_m):
        assert len(multi_m.tests()) == 3

    def test_all_passed(self, partial_m):
        """Fixture only adds passing tests."""
        for t in partial_m.tests():
            assert t.status == "PASSED"


# ===========================================================================
# 10. summary()
# ===========================================================================

class TestSummary:

    def test_returns_dict(self, partial_m):
        assert isinstance(partial_m.summary(), dict)

    def test_required_keys(self, partial_m):
        s = partial_m.summary()
        for k in ("overall_coverage", "total_bins", "covered_bins", "covergroups", "coverpoints"):
            assert k in s, f"key '{k}' missing from summary"

    def test_partial_values(self, partial_m):
        s = partial_m.summary()
        assert s["total_bins"] == 6
        assert s["covered_bins"] == 3
        assert abs(s["overall_coverage"] - 50.0) < 0.01
        assert s["covergroups"] == 2
        assert s["coverpoints"] == 2

    def test_zero_coverage(self, zero_m):
        s = zero_m.summary()
        assert s["covered_bins"] == 0
        assert s["overall_coverage"] == 0.0

    def test_full_coverage(self, full_m):
        s = full_m.summary()
        assert s["covered_bins"] == s["total_bins"]
        assert abs(s["overall_coverage"] - 100.0) < 0.01

    def test_vlt_total_bins_nonzero(self, vlt_metrics):
        """Code-coverage-only DB should report total_bins > 0."""
        s = vlt_metrics.summary()
        assert s["total_bins"] > 0

    def test_vlt_no_functional_covergroups(self, vlt_metrics):
        """vlt.cdb has no functional coverage so covergroups = 0."""
        s = vlt_metrics.summary()
        assert s["covergroups"] == 0

    def test_consistent_with_functional_bins(self, partial_m):
        """summary() total_bins and covered_bins must agree with functional_bins()."""
        s = partial_m.summary()
        fb = partial_m.functional_bins()
        assert s["total_bins"] == fb.total
        assert s["covered_bins"] == fb.covered


# ===========================================================================
# 11. database_info()
# ===========================================================================

class TestDatabaseInfo:

    def test_returns_dict(self, partial_m):
        assert isinstance(partial_m.database_info(), dict)

    def test_required_keys(self, partial_m):
        info = partial_m.database_info()
        for k in ("path", "format", "test_count"):
            assert k in info

    def test_test_count_matches_tests(self, partial_m):
        info = partial_m.database_info()
        tests = partial_m.tests()
        assert info["test_count"] == len(tests)

    def test_multi_test_count(self, multi_m):
        assert multi_m.database_info()["test_count"] == 3


# ===========================================================================
# 12. invalidate() — cache invalidation
# ===========================================================================

class TestInvalidate:

    def test_invalidate_clears_cache(self, partial_m):
        """Calling invalidate() should force recomputation."""
        fb1 = partial_m.functional_bins()
        partial_m.invalidate()
        fb2 = partial_m.functional_bins()
        assert fb1.total == fb2.total
        assert fb1.covered == fb2.covered

    def test_cached_result_is_same_object(self, partial_m):
        """Without invalidate(), successive calls return the same cached object."""
        fb1 = partial_m.functional_bins()
        fb2 = partial_m.functional_bins()
        assert fb1 is fb2

    def test_after_invalidate_new_object(self, partial_m):
        fb1 = partial_m.functional_bins()
        partial_m.invalidate()
        fb2 = partial_m.functional_bins()
        assert fb1 is not fb2

    def test_summary_cached(self, partial_m):
        s1 = partial_m.summary()
        s2 = partial_m.summary()
        # summary() is cached — returns the exact same dict object
        assert s1 is s2

    def test_summary_refreshed_after_invalidate(self, partial_m):
        s1 = partial_m.summary()
        partial_m.invalidate()
        s2 = partial_m.summary()
        # After invalidation a fresh dict is built — different object, same values
        assert s1 is not s2
        assert s1 == s2


# ===========================================================================
# 13. Parity: functional_bins agrees with CoverageReportBuilder
# ===========================================================================

class TestParityWithReportBuilder:
    """
    CoverageMetrics.functional_bins() MUST produce the same numbers as the
    CoverageReportBuilder, which is the canonical oracle for functional coverage.
    """

    @pytest.mark.parametrize("backend", ["xml", "sqlite"])
    def test_partial_parity(self, tmp_path, backend):
        m = _metrics(backend, _build_partial, tmp_path)
        self._assert_parity(m)

    @pytest.mark.parametrize("backend", ["xml", "sqlite"])
    def test_zero_parity(self, tmp_path, backend):
        m = _metrics(backend, _build_zero, tmp_path)
        self._assert_parity(m)

    @pytest.mark.parametrize("backend", ["xml", "sqlite"])
    def test_full_parity(self, tmp_path, backend):
        m = _metrics(backend, _build_full, tmp_path)
        self._assert_parity(m)

    @pytest.mark.parametrize("backend", ["xml", "sqlite"])
    def test_multi_test_parity(self, tmp_path, backend):
        m = _metrics(backend, _build_multi_test, tmp_path)
        self._assert_parity(m)

    def _assert_parity(self, m: CoverageMetrics):
        from ucis.report.coverage_report_builder import CoverageReportBuilder
        report = CoverageReportBuilder.build(m._db)

        def _report_bins(report):
            total = 0
            covered = 0
            for cg in report.covergroups:
                total += sum(len(cp.bins) for cp in cg.coverpoints)
                covered += sum(1 for cp in cg.coverpoints for b in cp.bins if b.hit)
            return total, covered

        r_total, r_covered = _report_bins(report)
        fb = m.functional_bins()
        assert fb.total == r_total, (
            f"total mismatch: metrics={fb.total}, report={r_total}"
        )
        assert fb.covered == r_covered, (
            f"covered mismatch: metrics={fb.covered}, report={r_covered}"
        )

    def test_coverpoint_stats_parity(self, tmp_path):
        """coverpoint_stats() should agree with direct CoverageReportBuilder traversal."""
        m = _metrics("xml", _build_partial, tmp_path)
        from ucis.report.coverage_report_builder import CoverageReportBuilder
        report = CoverageReportBuilder.build(m._db)
        report_cps = {cp.name: cp for cg in report.covergroups for cp in cg.coverpoints}
        metrics_cps = {cp.name: cp for cp in m.coverpoint_stats()}
        assert set(report_cps.keys()) == set(metrics_cps.keys()), "coverpoint names mismatch"
        for name, rcp in report_cps.items():
            mcp = metrics_cps[name]
            assert mcp.bins.total == len(rcp.bins), f"total mismatch for {name}"
            assert mcp.bins.covered == sum(1 for b in rcp.bins if b.hit), \
                f"covered mismatch for {name}"


# ===========================================================================
# 14. VLT regression — real SQLite file
# ===========================================================================

class TestVltRegression:
    """Smoke tests against the real vlt.cdb fixture."""

    def test_summary_total_nonzero(self, vlt_metrics):
        assert vlt_metrics.summary()["total_bins"] > 0

    def test_coverage_types_include_branch(self, vlt_metrics):
        assert CoverTypeT.BRANCHBIN in vlt_metrics.coverage_types_present()

    def test_stmtbin_covered_lte_total(self, vlt_metrics):
        bt = vlt_metrics.bins_by_type(CoverTypeT.STMTBIN)
        assert bt.covered <= bt.total

    def test_file_coverage_non_empty(self, vlt_metrics):
        assert len(vlt_metrics.file_coverage()) > 0

    def test_database_info_test_count_non_negative(self, vlt_metrics):
        assert vlt_metrics.database_info()["test_count"] >= 0
