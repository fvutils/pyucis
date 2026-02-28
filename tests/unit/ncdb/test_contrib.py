"""Tests for contrib.py — per-test contribution round-trip."""

import os
import tempfile

import pytest

from ucis.mem.mem_ucis import MemUCIS
from ucis.scope_type_t import ScopeTypeT
from ucis.cover_type_t import CoverTypeT
from ucis.history_node_kind import HistoryNodeKind

from ucis.ncdb.contrib import ContribWriter, ContribReader
from ucis.ncdb.ncdb_writer import NcdbWriter
from ucis.ncdb.ncdb_reader import NcdbReader


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_db():
    """Build a MemUCIS with one covergroup/coverpoint/3 bins and 2 history nodes."""
    db = MemUCIS()
    cg_du = db.createScope("cg_du", None, 1, None, ScopeTypeT.DU_MODULE, 0)
    cp    = cg_du.createScope("cp", None, 1, None, ScopeTypeT.COVERPOINT, 0)
    cp.createBin("b0", None, 1, 0, "0")   # bin index 0
    cp.createBin("b1", None, 1, 0, "1")   # bin index 1
    cp.createBin("b2", None, 1, 0, "2")   # bin index 2

    db.createHistoryNode(None, "test_a", None, HistoryNodeKind.TEST)  # hist_idx 0
    db.createHistoryNode(None, "test_b", None, HistoryNodeKind.TEST)  # hist_idx 1
    return db


# ── MemUCIS API ───────────────────────────────────────────────────────────────

def test_record_test_association_basic():
    db = MemUCIS()
    db.record_test_association(0, 5, 3)
    assert db._per_test_data == {0: {5: 3}}


def test_record_test_association_accumulates():
    db = MemUCIS()
    db.record_test_association(0, 5, 2)
    db.record_test_association(0, 5, 3)
    assert db._per_test_data[0][5] == 5


def test_record_test_association_multiple_tests():
    db = MemUCIS()
    db.record_test_association(0, 1, 1)
    db.record_test_association(1, 2, 4)
    assert db._per_test_data[0] == {1: 1}
    assert db._per_test_data[1] == {2: 4}


def test_get_test_coverage_api_returns_instance():
    db = _make_db()
    api = db.get_test_coverage_api()
    assert api is not None
    assert api._db is db


def test_get_test_coverage_api_cached():
    db = _make_db()
    api1 = db.get_test_coverage_api()
    api2 = db.get_test_coverage_api()
    assert api1 is api2


# ── MemTestCoverage queries ───────────────────────────────────────────────────

def test_has_test_associations_false():
    db = _make_db()
    assert not db.get_test_coverage_api().has_test_associations()


def test_has_test_associations_true():
    db = _make_db()
    db.record_test_association(0, 0, 1)
    assert db.get_test_coverage_api().has_test_associations()


def test_get_tests_for_coveritem():
    db = _make_db()
    db.record_test_association(0, 1, 2)
    db.record_test_association(1, 1, 5)
    info = db.get_test_coverage_api().get_tests_for_coveritem(1)
    assert info.total_hits == 7
    names = {t[1] for t in info.tests}
    assert names == {"test_a", "test_b"}


def test_get_tests_for_coveritem_empty():
    db = _make_db()
    info = db.get_test_coverage_api().get_tests_for_coveritem(99)
    assert info.total_hits == 0
    assert info.tests == []


def test_get_coveritems_for_test():
    db = _make_db()
    db.record_test_association(0, 0, 1)
    db.record_test_association(0, 2, 3)
    bins = db.get_test_coverage_api().get_coveritems_for_test(0)
    assert bins == [0, 2]


def test_get_unique_coveritems():
    db = _make_db()
    db.record_test_association(0, 0, 1)
    db.record_test_association(0, 1, 1)
    db.record_test_association(1, 1, 1)
    unique = db.get_test_coverage_api().get_unique_coveritems(0)
    assert unique == [0]


def test_get_all_test_contributions():
    db = _make_db()
    db.record_test_association(0, 0, 1)
    db.record_test_association(0, 1, 1)
    db.record_test_association(1, 2, 1)
    contribs = db.get_test_coverage_api().get_all_test_contributions()
    assert len(contribs) == 2
    # Sorted by total_items descending → test_a (2 bins) first
    assert contribs[0].test_name == "test_a"
    assert contribs[0].total_items == 2


# ── ContribWriter / ContribReader round-trip ──────────────────────────────────

def test_contrib_writer_empty():
    db = MemUCIS()
    members = ContribWriter().serialize(db)
    assert members == {}


def test_contrib_writer_produces_members():
    db = MemUCIS()
    db.record_test_association(0, 10, 3)
    db.record_test_association(0, 20, 1)
    members = ContribWriter().serialize(db)
    assert "contrib/0.bin" in members
    assert len(members) == 1


def test_contrib_round_trip():
    db = MemUCIS()
    db.record_test_association(0, 5, 2)
    db.record_test_association(0, 15, 4)
    db.record_test_association(1, 7, 1)

    members = ContribWriter().serialize(db)

    db2 = MemUCIS()
    ContribReader().apply(db2, members)

    assert db2._per_test_data[0] == {5: 2, 15: 4}
    assert db2._per_test_data[1] == {7: 1}


def test_contrib_round_trip_large_indices():
    """Delta encoding should handle large sparse bin indices."""
    db = MemUCIS()
    db.record_test_association(0, 0, 1)
    db.record_test_association(0, 100_000, 99)

    members = ContribWriter().serialize(db)
    db2 = MemUCIS()
    ContribReader().apply(db2, members)

    assert db2._per_test_data[0] == {0: 1, 100_000: 99}


# ── Full NCDB round-trip ──────────────────────────────────────────────────────

def _write_read(db):
    with tempfile.NamedTemporaryFile(suffix=".cdb", delete=False) as f:
        path = f.name
    try:
        NcdbWriter().write(db, path)
        return NcdbReader().read(path)
    finally:
        os.unlink(path)


def test_ncdb_round_trip_no_contrib():
    db = _make_db()
    db2 = _write_read(db)
    assert db2._per_test_data == {}


def test_ncdb_round_trip_with_contrib():
    db = _make_db()
    db.record_test_association(0, 0, 1)
    db.record_test_association(0, 2, 3)
    db.record_test_association(1, 1, 2)

    db2 = _write_read(db)

    assert db2._per_test_data[0] == {0: 1, 2: 3}
    assert db2._per_test_data[1] == {1: 2}


def test_ncdb_round_trip_api_after_read():
    db = _make_db()
    db.record_test_association(0, 0, 5)
    db.record_test_association(1, 0, 3)

    db2 = _write_read(db)
    api = db2.get_test_coverage_api()

    info = api.get_tests_for_coveritem(0)
    assert info.total_hits == 8
    assert len(info.tests) == 2
