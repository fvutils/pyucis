"""
MemTestCoverage — in-memory per-test contribution query API.

Mirrors the SqliteTestCoverage interface so callers can work with either
backend identically.  Operates on MemUCIS._per_test_data which maps
history_idx → {bin_index → count}.
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass, field

from ucis.history_node_kind import HistoryNodeKind


@dataclass
class TestCoverageInfo:
    """Information about a test's coverage contribution."""
    history_idx: int
    test_name: str
    total_items: int
    unique_items: int
    total_contribution: int
    coverage_percent: float


@dataclass
class CoverItemTestInfo:
    """Information about which tests hit a coveritem bin."""
    bin_index: int
    total_hits: int
    tests: List[Tuple[int, str, int]] = field(default_factory=list)  # (history_idx, name, count)


class MemTestCoverage:
    """Query interface for per-test contributions stored in MemUCIS.

    Example::

        db = NcdbReader().read("output.cdb")
        api = db.get_test_coverage_api()
        for info in api.get_all_test_contributions():
            print(f"{info.test_name}: {info.coverage_percent:.1f}%")
    """

    def __init__(self, db):
        self._db = db

    # ── Helpers ───────────────────────────────────────────────────────────

    def _history_name(self, history_idx: int) -> Optional[str]:
        nodes = self._db.m_history_node_l
        if 0 <= history_idx < len(nodes):
            return nodes[history_idx].getLogicalName()
        return None

    def _total_bins(self) -> int:
        """Count total bins across all scopes (same order as counts.bin)."""
        from ucis.ncdb.dfs_util import dfs_scope_list
        from ucis.cover_type_t import CoverTypeT
        total = 0
        for scope in dfs_scope_list(self._db):
            total += len(list(scope.coverItems(CoverTypeT.ALL)))
        return total

    # ── Public API ────────────────────────────────────────────────────────

    def has_test_associations(self) -> bool:
        """Return True if any per-test data has been recorded."""
        return bool(self._db._per_test_data)

    def get_tests_for_coveritem(self, bin_index: int) -> CoverItemTestInfo:
        """Find all tests that contributed to *bin_index*."""
        tests = []
        total_hits = 0
        for hist_idx, bin_counts in self._db._per_test_data.items():
            count = bin_counts.get(bin_index, 0)
            if count:
                name = self._history_name(hist_idx) or str(hist_idx)
                tests.append((hist_idx, name, count))
                total_hits += count
        tests.sort(key=lambda t: t[2], reverse=True)
        return CoverItemTestInfo(bin_index=bin_index, total_hits=total_hits, tests=tests)

    def get_coveritems_for_test(self, history_idx: int) -> List[int]:
        """Return all bin indices hit by the test at *history_idx*."""
        return sorted(self._db._per_test_data.get(history_idx, {}).keys())

    def get_unique_coveritems(self, history_idx: int) -> List[int]:
        """Return bin indices hit ONLY by *history_idx* (not any other test)."""
        my_bins = set(self._db._per_test_data.get(history_idx, {}).keys())
        other_bins: set = set()
        for idx, bin_counts in self._db._per_test_data.items():
            if idx != history_idx:
                other_bins.update(bin_counts.keys())
        return sorted(my_bins - other_bins)

    def get_test_contribution(self, history_idx: int) -> Optional[TestCoverageInfo]:
        """Calculate contribution metrics for *history_idx*."""
        name = self._history_name(history_idx)
        if name is None:
            return None
        bin_counts = self._db._per_test_data.get(history_idx, {})
        total_items = len(bin_counts)
        total_contribution = sum(bin_counts.values())
        unique_items = len(self.get_unique_coveritems(history_idx))
        total_bins = self._total_bins()
        coverage_percent = (total_items / total_bins * 100) if total_bins > 0 else 0.0
        return TestCoverageInfo(
            history_idx=history_idx,
            test_name=name,
            total_items=total_items,
            unique_items=unique_items,
            total_contribution=total_contribution,
            coverage_percent=coverage_percent,
        )

    def get_all_test_contributions(self) -> List[TestCoverageInfo]:
        """Return contribution metrics for all tests, sorted by total items (desc)."""
        results = []
        for hist_idx in self._db._per_test_data:
            info = self.get_test_contribution(hist_idx)
            if info and info.total_items > 0:
                results.append(info)
        results.sort(key=lambda x: x.total_items, reverse=True)
        return results
