"""
Layer 1: CoverageModel unit tests.

These tests verify that every public method of CoverageModel returns values
that agree with the raw UCIS API (the ground truth).  Both the API/XML path
and the SQLite fast path are exercised through the parametrized fixtures in
tui_fixtures.py.
"""
import pytest
from ucis.cover_type_t import CoverTypeT
from ucis.scope_type_t import ScopeTypeT

from tests.tui_fixtures import (
    partial_coverage, zero_coverage, full_coverage, multi_test, vlt_model,
)


# ---------------------------------------------------------------------------
# get_summary()
# ---------------------------------------------------------------------------

class TestGetSummary:

    def test_total_bins(self, partial_coverage):
        model, expected = partial_coverage
        summary = model.get_summary()
        assert summary["total_bins"] == expected["total_bins"], (
            f"total_bins: got {summary['total_bins']}, want {expected['total_bins']}"
        )

    def test_covered_bins(self, partial_coverage):
        model, expected = partial_coverage
        summary = model.get_summary()
        assert summary["covered_bins"] == expected["covered_bins"]

    def test_overall_coverage_percentage(self, partial_coverage):
        model, expected = partial_coverage
        summary = model.get_summary()
        assert abs(summary["overall_coverage"] - expected["overall_coverage"]) < 0.01

    def test_covergroup_count(self, partial_coverage):
        model, expected = partial_coverage
        summary = model.get_summary()
        assert summary["covergroups"] == expected["covergroups"]

    def test_summary_zero_coverage(self, zero_coverage):
        model, expected = zero_coverage
        summary = model.get_summary()
        assert summary["covered_bins"] == 0
        assert summary["overall_coverage"] == 0.0
        assert summary["total_bins"] == expected["total_bins"]

    def test_summary_full_coverage(self, full_coverage):
        model, expected = full_coverage
        summary = model.get_summary()
        assert summary["covered_bins"] == expected["covered_bins"]
        assert abs(summary["overall_coverage"] - 100.0) < 0.01

    def test_summary_is_cached(self, partial_coverage):
        model, _ = partial_coverage
        s1 = model.get_summary()
        s2 = model.get_summary()
        assert s1 is s2, "get_summary() should return the cached object on repeated calls"


# ---------------------------------------------------------------------------
# get_coverage_types()
# ---------------------------------------------------------------------------

class TestGetCoverageTypes:

    def test_cvgbin_present_in_partial(self, partial_coverage):
        model, _ = partial_coverage
        types = model.get_coverage_types()
        assert CoverTypeT.CVGBIN in types

    def test_types_non_empty(self, partial_coverage):
        model, _ = partial_coverage
        assert len(model.get_coverage_types()) >= 1

    def test_types_cached(self, partial_coverage):
        model, _ = partial_coverage
        t1 = model.get_coverage_types()
        t2 = model.get_coverage_types()
        assert t1 is t2


# ---------------------------------------------------------------------------
# get_coverage_by_type()
# ---------------------------------------------------------------------------

class TestGetCoverageByType:

    def test_cvgbin_totals_match_summary(self, partial_coverage):
        model, expected = partial_coverage
        result = model.get_coverage_by_type(CoverTypeT.CVGBIN)
        assert result["total"]   == expected["total_bins"]
        assert result["covered"] == expected["covered_bins"]

    def test_coverage_percentage_derived_correctly(self, partial_coverage):
        model, _ = partial_coverage
        result = model.get_coverage_by_type(CoverTypeT.CVGBIN)
        if result["total"] > 0:
            expected_pct = result["covered"] / result["total"] * 100
            assert abs(result["coverage"] - expected_pct) < 0.01

    def test_zero_coverage(self, zero_coverage):
        model, _ = zero_coverage
        result = model.get_coverage_by_type(CoverTypeT.CVGBIN)
        assert result["covered"] == 0
        assert result["coverage"] == 0.0

    def test_full_coverage(self, full_coverage):
        model, _ = full_coverage
        result = model.get_coverage_by_type(CoverTypeT.CVGBIN)
        assert result["covered"] == result["total"]
        assert abs(result["coverage"] - 100.0) < 0.01

    def test_result_cached(self, partial_coverage):
        model, _ = partial_coverage
        r1 = model.get_coverage_by_type(CoverTypeT.CVGBIN)
        r2 = model.get_coverage_by_type(CoverTypeT.CVGBIN)
        assert r1 is r2


# ---------------------------------------------------------------------------
# get_all_tests()
# ---------------------------------------------------------------------------

class TestGetAllTests:

    def test_test_count(self, partial_coverage):
        """Partial-coverage fixture has exactly one test."""
        model, _ = partial_coverage
        tests = model.get_all_tests()
        assert len(tests) == 1

    def test_test_name(self, partial_coverage):
        model, _ = partial_coverage
        tests = model.get_all_tests()
        assert tests[0]["name"] == "test1"

    def test_multi_test_count(self, multi_test):
        model, expected = multi_test
        tests = model.get_all_tests()
        assert len(tests) == len(expected["test_names"])

    def test_multi_test_names_present(self, multi_test):
        model, expected = multi_test
        tests = model.get_all_tests()
        found_names = {t["name"] for t in tests}
        for name in expected["test_names"]:
            assert name in found_names, f"Expected test '{name}' not in {found_names}"

    def test_tests_cached(self, partial_coverage):
        model, _ = partial_coverage
        t1 = model.get_all_tests()
        t2 = model.get_all_tests()
        assert t1 is t2


# ---------------------------------------------------------------------------
# get_database_info()
# ---------------------------------------------------------------------------

class TestGetDatabaseInfo:

    def test_path_preserved(self, partial_coverage):
        model, _ = partial_coverage
        info = model.get_database_info()
        assert info["path"] == model.db_path

    def test_test_count_matches(self, partial_coverage):
        model, _ = partial_coverage
        info = model.get_database_info()
        assert info["test_count"] == 1

    def test_multi_test_count(self, multi_test):
        model, expected = multi_test
        info = model.get_database_info()
        assert info["test_count"] == len(expected["test_names"])


# ---------------------------------------------------------------------------
# Test filter / cache invalidation
# ---------------------------------------------------------------------------

class TestTestFilter:

    def test_set_and_get_filter(self, partial_coverage):
        model, _ = partial_coverage
        assert model.get_test_filter() is None
        model.set_test_filter("test1")
        assert model.get_test_filter() == "test1"

    def test_clear_filter(self, partial_coverage):
        model, _ = partial_coverage
        model.set_test_filter("test1")
        model.clear_test_filter()
        assert model.get_test_filter() is None

    def test_filter_invalidates_code_coverage_cache(self, partial_coverage):
        """Setting a filter must bust the code_coverage_summary cache."""
        model, _ = partial_coverage
        _ = model.get_summary()              # populate cache
        model.set_test_filter("test1")
        # code_coverage_summary cache key must be gone after filter change
        assert "code_coverage_summary" not in model._cache

    def test_unfiltered_and_filtered_differ_when_partial(self, multi_test):
        """With a test filter the per-type count should be <= the unfiltered total.
        (Exact values are SQLite-only; for XML we just check the invariant.)
        """
        model, expected = multi_test
        unfiltered = model.get_coverage_by_type(CoverTypeT.CVGBIN, filtered=False)
        # Filtering is only meaningful for the SQLite backend; skip for XML
        if not hasattr(model.db, "conn"):
            pytest.skip("filter-by-test is SQLite-only")
        model.set_test_filter(expected["test_names"][0])
        filtered = model.get_coverage_by_type(CoverTypeT.CVGBIN, filtered=True)
        assert filtered["covered"] <= unfiltered["covered"]


# ---------------------------------------------------------------------------
# Regression: real VLT SQLite database
# ---------------------------------------------------------------------------

class TestVltModel:

    def test_summary_non_empty(self, vlt_model):
        summary = vlt_model.get_summary()
        assert summary["total_bins"] > 0

    def test_coverage_types_non_empty(self, vlt_model):
        types = vlt_model.get_coverage_types()
        assert len(types) > 0

    def test_database_info_has_path(self, vlt_model):
        info = vlt_model.get_database_info()
        assert info["path"] != ""
