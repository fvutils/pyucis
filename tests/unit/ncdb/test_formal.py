"""Tests for formal.py — formal verification data round-trip."""

import os
import tempfile

import pytest

from ucis.formal_status_t import FormalStatusT
from ucis.mem.mem_ucis import MemUCIS
from ucis.scope_type_t import ScopeTypeT
from ucis.history_node_kind import HistoryNodeKind

from ucis.ncdb.formal import FormalWriter, FormalReader
from ucis.ncdb.ncdb_writer import NcdbWriter
from ucis.ncdb.ncdb_reader import NcdbReader


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_db():
    db = MemUCIS()
    du = db.createScope("top", None, 1, None, ScopeTypeT.DU_MODULE, 0)
    cp = du.createScope("assert_cp", None, 1, None, ScopeTypeT.COVERPOINT, 0)
    cp.createBin("pass", None, 1, 0, "0")   # bin 0
    cp.createBin("fail", None, 1, 0, "1")   # bin 1
    cp.createBin("vacuous", None, 1, 0, "2") # bin 2
    return db


# ── FormalStatusT enum ────────────────────────────────────────────────────────

def test_formal_status_values():
    assert FormalStatusT.NONE         == 0
    assert FormalStatusT.FAILURE      == 1
    assert FormalStatusT.PROOF        == 2
    assert FormalStatusT.VACUOUS      == 3
    assert FormalStatusT.INCONCLUSIVE == 4
    assert FormalStatusT.ASSUMPTION   == 5
    assert FormalStatusT.CONFLICT     == 6


# ── MemUCIS formal API ────────────────────────────────────────────────────────

def test_set_formal_data_status():
    db = MemUCIS()
    db.set_formal_data(0, status=FormalStatusT.PROOF)
    assert db._formal_data[0]['status'] == FormalStatusT.PROOF


def test_set_formal_data_radius():
    db = MemUCIS()
    db.set_formal_data(5, radius=42)
    assert db._formal_data[5]['radius'] == 42


def test_set_formal_data_witness():
    db = MemUCIS()
    db.set_formal_data(3, witness="/tmp/wit.vcd")
    assert db._formal_data[3]['witness'] == "/tmp/wit.vcd"


def test_set_formal_data_all_fields():
    db = MemUCIS()
    db.set_formal_data(7, status=FormalStatusT.FAILURE, radius=10, witness="w.vcd")
    fd = db._formal_data[7]
    assert fd['status'] == FormalStatusT.FAILURE
    assert fd['radius'] == 10
    assert fd['witness'] == "w.vcd"


def test_get_formal_data_present():
    db = MemUCIS()
    db.set_formal_data(2, status=FormalStatusT.VACUOUS)
    fd = db.get_formal_data(2)
    assert fd is not None
    assert fd['status'] == FormalStatusT.VACUOUS


def test_get_formal_data_absent():
    db = MemUCIS()
    assert db.get_formal_data(99) is None


def test_set_formal_data_partial_update():
    """Multiple calls to set_formal_data merge fields."""
    db = MemUCIS()
    db.set_formal_data(1, status=FormalStatusT.PROOF)
    db.set_formal_data(1, radius=5)
    fd = db.get_formal_data(1)
    assert fd['status'] == FormalStatusT.PROOF
    assert fd['radius'] == 5


# ── FormalWriter / FormalReader ───────────────────────────────────────────────

def test_writer_empty_when_no_data():
    db = MemUCIS()
    assert FormalWriter().serialize(db) == b""


def test_writer_empty_when_all_default():
    """Entries with all-default values are not serialized."""
    db = MemUCIS()
    db.set_formal_data(0, status=FormalStatusT.NONE)
    assert FormalWriter().serialize(db) == b""


def test_writer_produces_bytes():
    db = MemUCIS()
    db.set_formal_data(0, status=FormalStatusT.PROOF)
    data = FormalWriter().serialize(db)
    assert len(data) > 0


def test_round_trip_status():
    db = MemUCIS()
    db.set_formal_data(4, status=FormalStatusT.INCONCLUSIVE)
    data = FormalWriter().serialize(db)

    db2 = MemUCIS()
    FormalReader().apply(db2, data)
    assert db2._formal_data[4]['status'] == FormalStatusT.INCONCLUSIVE


def test_round_trip_radius():
    db = MemUCIS()
    db.set_formal_data(3, radius=100)
    data = FormalWriter().serialize(db)

    db2 = MemUCIS()
    FormalReader().apply(db2, data)
    assert db2._formal_data[3]['radius'] == 100


def test_round_trip_witness():
    db = MemUCIS()
    db.set_formal_data(2, witness="/evidence/witness.vcd")
    data = FormalWriter().serialize(db)

    db2 = MemUCIS()
    FormalReader().apply(db2, data)
    assert db2._formal_data[2]['witness'] == "/evidence/witness.vcd"


def test_round_trip_multiple_entries():
    db = MemUCIS()
    db.set_formal_data(0, status=FormalStatusT.PROOF)
    db.set_formal_data(1, status=FormalStatusT.FAILURE, witness="fail.vcd")
    db.set_formal_data(5, status=FormalStatusT.VACUOUS, radius=3)
    data = FormalWriter().serialize(db)

    db2 = MemUCIS()
    FormalReader().apply(db2, data)
    assert db2._formal_data[0]['status'] == FormalStatusT.PROOF
    assert db2._formal_data[1]['witness'] == "fail.vcd"
    assert db2._formal_data[5]['radius'] == 3


def test_reader_noop_on_empty():
    db = MemUCIS()
    FormalReader().apply(db, b"")
    assert db._formal_data == {}


def test_all_status_values_round_trip():
    db = MemUCIS()
    for i, st in enumerate(FormalStatusT):
        if st != FormalStatusT.NONE:
            db.set_formal_data(i, status=st)
    data = FormalWriter().serialize(db)

    db2 = MemUCIS()
    FormalReader().apply(db2, data)
    for i, st in enumerate(FormalStatusT):
        if st != FormalStatusT.NONE:
            assert db2._formal_data[i]['status'] == int(st)


# ── Full NCDB round-trip ──────────────────────────────────────────────────────

def _write_read(db):
    with tempfile.NamedTemporaryFile(suffix=".cdb", delete=False) as f:
        path = f.name
    try:
        NcdbWriter().write(db, path)
        return NcdbReader().read(path)
    finally:
        os.unlink(path)


def test_ncdb_round_trip_no_formal():
    db = _make_db()
    db2 = _write_read(db)
    assert db2._formal_data == {}


def test_ncdb_round_trip_with_formal():
    db = _make_db()
    db.set_formal_data(0, status=FormalStatusT.PROOF)
    db.set_formal_data(1, status=FormalStatusT.FAILURE, witness="fail.vcd")

    db2 = _write_read(db)
    assert db2.get_formal_data(0)['status'] == FormalStatusT.PROOF
    assert db2.get_formal_data(1)['witness'] == "fail.vcd"


def test_ncdb_round_trip_formal_not_present_for_unset():
    db = _make_db()
    db.set_formal_data(0, status=FormalStatusT.VACUOUS)

    db2 = _write_read(db)
    assert db2.get_formal_data(1) is None
    assert db2.get_formal_data(2) is None
