"""Integration tests for Phase 1 binary test history.

These tests exercise the full stack: NcdbUCIS API → NcdbWriter → NcdbReader
→ NcdbMerger, using temporary .cdb files on disk.
"""
from __future__ import annotations

import os
import shutil
import tempfile

import pytest

from ucis.mem.mem_ucis import MemUCIS
from ucis.ncdb.constants import HIST_STATUS_FAIL, HIST_STATUS_OK
from ucis.ncdb.ncdb_merger import NcdbMerger
from ucis.ncdb.ncdb_reader import NcdbReader
from ucis.ncdb.ncdb_ucis import NcdbUCIS
from ucis.ncdb.ncdb_writer import NcdbWriter


# ── helpers ──────────────────────────────────────────────────────────────────

def _write_v2_cdb(path: str, test_runs: list) -> None:
    """Create a v2 .cdb with the supplied test runs."""
    NcdbWriter().write(MemUCIS(), path)
    db = NcdbUCIS(path)
    for name, seed, status, ts in test_runs:
        db.add_test_run(
            name, seed=seed, status=status, ts=ts,
            has_coverage=(status == HIST_STATUS_OK),
        )
    tmp = path + ".tmp"
    NcdbWriter().write(db, tmp)
    os.replace(tmp, path)


@pytest.fixture()
def tmpdir_path():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


# ── tests ─────────────────────────────────────────────────────────────────────

class TestAddTestRunUpdatesStats:
    """add_test_run() must update test_stats immediately."""

    def test_single_pass_creates_entry(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "a.cdb")
        NcdbWriter().write(MemUCIS(), path)
        db = NcdbUCIS(path)
        db.add_test_run("my_test", seed="1", status=HIST_STATUS_OK,
                        ts=1700000000, has_coverage=True)
        entry = db.get_test_stats("my_test")
        assert entry is not None
        assert entry.total_runs == 1
        assert entry.pass_count == 1
        assert entry.fail_count == 0

    def test_pass_and_fail_accumulate(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "a.cdb")
        NcdbWriter().write(MemUCIS(), path)
        db = NcdbUCIS(path)
        for i, st in enumerate([HIST_STATUS_OK, HIST_STATUS_FAIL,
                                 HIST_STATUS_OK, HIST_STATUS_OK]):
            db.add_test_run("my_test", seed=str(i), status=st,
                            ts=1700000000 + i * 3600, has_coverage=(st == HIST_STATUS_OK))
        entry = db.get_test_stats("my_test")
        assert entry.total_runs == 4
        assert entry.pass_count == 3
        assert entry.fail_count == 1

    def test_unknown_test_returns_none(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "a.cdb")
        NcdbWriter().write(MemUCIS(), path)
        db = NcdbUCIS(path)
        assert db.get_test_stats("nonexistent") is None

    def test_run_id_monotonically_increments(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "a.cdb")
        NcdbWriter().write(MemUCIS(), path)
        db = NcdbUCIS(path)
        for i in range(5):
            db.add_test_run("t", seed=str(i), status=HIST_STATUS_OK,
                            ts=1700000000 + i)
        assert db._test_registry.next_run_id == 5


class TestQueryTestHistoryRange:
    """query_test_history() must filter by time range and return correct records."""

    def _build_db(self, path):
        NcdbWriter().write(MemUCIS(), path)
        db = NcdbUCIS(path)
        # Two tests, multiple runs spread over a day
        for i in range(6):
            db.add_test_run("alpha", seed=str(i),
                            status=HIST_STATUS_OK if i % 3 else HIST_STATUS_FAIL,
                            ts=1700000000 + i * 3600,
                            has_coverage=True)
        for i in range(3):
            db.add_test_run("beta", seed=str(i), status=HIST_STATUS_OK,
                            ts=1700000000 + i * 7200, has_coverage=True)
        return db

    def test_all_records_returned_without_filter(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "a.cdb")
        db = self._build_db(path)
        recs = db.query_test_history("alpha")
        assert len(recs) == 6

    def test_time_range_filter_lower_bound(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "a.cdb")
        db = self._build_db(path)
        # Request only the last 3 records (ts >= 1700000000 + 3*3600)
        ts_start = 1700000000 + 3 * 3600
        recs = db.query_test_history("alpha", ts_from=ts_start)
        assert all(r.ts >= ts_start for r in recs)
        assert len(recs) == 3

    def test_time_range_filter_upper_bound(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "a.cdb")
        db = self._build_db(path)
        ts_end = 1700000000 + 2 * 3600 + 1
        recs = db.query_test_history("alpha", ts_to=ts_end)
        assert all(r.ts <= ts_end for r in recs)
        assert len(recs) == 3

    def test_nonexistent_name_returns_empty(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "a.cdb")
        db = self._build_db(path)
        assert db.query_test_history("no_such_test") == []

    def test_separate_test_independent(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "a.cdb")
        db = self._build_db(path)
        recs = db.query_test_history("beta")
        assert len(recs) == 3


class TestRoundTripV2Cdb:
    """Write a v2 .cdb to disk, read it back, confirm state is preserved."""

    def test_stats_survive_roundtrip(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "rt.cdb")
        _write_v2_cdb(path, [
            ("foo", "1", HIST_STATUS_OK,   1700000000),
            ("foo", "2", HIST_STATUS_FAIL, 1700003600),
            ("bar", "1", HIST_STATUS_OK,   1700000100),
        ])
        db = NcdbReader().read(path)
        assert db._test_registry.num_names == 2
        foo_id = db._test_registry._name_to_id["foo"]
        foo_stats = db._test_stats.get(foo_id)
        assert foo_stats.total_runs == 2
        assert foo_stats.fail_count == 1
        bar_id = db._test_registry._name_to_id["bar"]
        bar_stats = db._test_stats.get(bar_id)
        assert bar_stats.total_runs == 1

    def test_bucket_data_survives_roundtrip(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "rt.cdb")
        _write_v2_cdb(path, [
            ("my_test", str(i), HIST_STATUS_OK, 1700000000 + i * 60)
            for i in range(10)
        ])
        db = NcdbReader().read(path)
        assert len(db._sealed_buckets) >= 1

    def test_manifest_history_format_is_v2(self, tmpdir_path):
        import zipfile, json
        path = os.path.join(tmpdir_path, "rt.cdb")
        _write_v2_cdb(path, [("t", "1", HIST_STATUS_OK, 1700000000)])
        with zipfile.ZipFile(path, "r") as zf:
            manifest_data = zf.read("manifest.json")
        manifest = json.loads(manifest_data)
        assert manifest.get("history_format") == "v2"

    def test_query_history_after_roundtrip(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "rt.cdb")
        _write_v2_cdb(path, [
            ("my_test", str(i), HIST_STATUS_OK if i % 2 == 0 else HIST_STATUS_FAIL,
             1700000000 + i * 3600)
            for i in range(8)
        ])
        db2 = NcdbUCIS(path)
        recs = db2.query_test_history("my_test")
        assert len(recs) == 8
        assert all(hasattr(r, "ts") for r in recs)


class TestMergeTwoV2Sources:
    """Merge two v2 .cdb files and verify the result is consistent."""

    def _make_src_a(self, d):
        path = os.path.join(d, "a.cdb")
        _write_v2_cdb(path, [
            ("uart_smoke", "1", HIST_STATUS_OK,   1700000000),
            ("uart_smoke", "2", HIST_STATUS_FAIL, 1700086400),
            ("uart_smoke", "3", HIST_STATUS_OK,   1700172800),
            ("gpio_test",  "1", HIST_STATUS_OK,   1700000100),
            ("gpio_test",  "2", HIST_STATUS_FAIL, 1700086500),
        ])
        return path

    def _make_src_b(self, d):
        path = os.path.join(d, "b.cdb")
        _write_v2_cdb(path, [
            ("uart_smoke", "4", HIST_STATUS_OK,   1700259200),
            ("uart_smoke", "5", HIST_STATUS_OK,   1700345600),
            ("spi_test",   "1", HIST_STATUS_OK,   1700259300),
        ])
        return path

    def test_merged_registry_contains_all_names(self, tmpdir_path):
        merged = os.path.join(tmpdir_path, "merged.cdb")
        NcdbMerger().merge([self._make_src_a(tmpdir_path),
                            self._make_src_b(tmpdir_path)], merged)
        db = NcdbReader().read(merged)
        assert db._test_registry.num_names == 3
        assert "uart_smoke" in db._test_registry._name_to_id
        assert "gpio_test"  in db._test_registry._name_to_id
        assert "spi_test"   in db._test_registry._name_to_id

    def test_merged_stats_are_combined(self, tmpdir_path):
        merged = os.path.join(tmpdir_path, "merged.cdb")
        NcdbMerger().merge([self._make_src_a(tmpdir_path),
                            self._make_src_b(tmpdir_path)], merged)
        db = NcdbReader().read(merged)
        uart_id = db._test_registry._name_to_id["uart_smoke"]
        uart_stats = db._test_stats.get(uart_id)
        assert uart_stats.total_runs == 5
        assert uart_stats.fail_count == 1

    def test_merged_run_id_is_sum(self, tmpdir_path):
        merged = os.path.join(tmpdir_path, "merged.cdb")
        NcdbMerger().merge([self._make_src_a(tmpdir_path),
                            self._make_src_b(tmpdir_path)], merged)
        db = NcdbReader().read(merged)
        # src_a has 5 runs, src_b has 3 → next_run_id = 8
        assert db._test_registry.next_run_id == 8

    def test_merged_history_queryable(self, tmpdir_path):
        merged = os.path.join(tmpdir_path, "merged.cdb")
        NcdbMerger().merge([self._make_src_a(tmpdir_path),
                            self._make_src_b(tmpdir_path)], merged)
        db2 = NcdbUCIS(merged)
        recs = db2.query_test_history("uart_smoke")
        assert len(recs) == 5

    def test_merged_buckets_present(self, tmpdir_path):
        merged = os.path.join(tmpdir_path, "merged.cdb")
        NcdbMerger().merge([self._make_src_a(tmpdir_path),
                            self._make_src_b(tmpdir_path)], merged)
        db = NcdbReader().read(merged)
        assert len(db._sealed_buckets) >= 2

    def test_top_flaky_after_merge(self, tmpdir_path):
        merged = os.path.join(tmpdir_path, "merged.cdb")
        NcdbMerger().merge([self._make_src_a(tmpdir_path),
                            self._make_src_b(tmpdir_path)], merged)
        db2 = NcdbUCIS(merged)
        flaky = db2.top_flaky_tests(5)
        # At least one test (gpio_test) has failures making it flaky
        assert len(flaky) > 0
