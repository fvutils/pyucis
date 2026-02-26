"""
Tests for ucis.ncdb.toggle — TOGGLE scope metadata round-trip via NCDB ZIP.
"""

import json
import os
import tempfile
import zipfile

import pytest

from ucis.cover_data import CoverData
from ucis.cover_type_t import CoverTypeT
from ucis.history_node_kind import HistoryNodeKind
from ucis.mem.mem_ucis import MemUCIS
from ucis.ncdb.constants import MEMBER_TOGGLE
from ucis.ncdb.ncdb_reader import NcdbReader
from ucis.ncdb.ncdb_writer import NcdbWriter
from ucis.ncdb.toggle import ToggleReader, ToggleWriter
from ucis.scope_type_t import ScopeTypeT
from ucis.source_t import SourceT
from ucis.toggle_dir_t import ToggleDirT
from ucis.toggle_metric_t import ToggleMetricT
from ucis.toggle_type_t import ToggleTypeT


# ── Helpers ───────────────────────────────────────────────────────────────

def _make_toggle_db(canonical, metric, ttype, tdir):
    db = MemUCIS()
    db.createHistoryNode(None, "t", None, HistoryNodeKind.TEST)
    t = db.createToggle("sig", canonical, 0, metric, ttype, tdir)
    cd = CoverData(CoverTypeT.TOGGLEBIN, 0); cd.data = 3
    t.createNextCover("0->1", cd, None)
    cd2 = CoverData(CoverTypeT.TOGGLEBIN, 0); cd2.data = 2
    t.createNextCover("1->0", cd2, None)
    return db, t


def _write_read(db):
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "out.cdb")
        NcdbWriter().write(db, path)
        return NcdbReader().read(path), path


# ── Unit tests: ToggleWriter / ToggleReader ───────────────────────────────

def test_toggle_writer_empty_when_defaults():
    """No toggle metadata when all values are defaults — returns empty bytes."""
    db, _ = _make_toggle_db(
        "sig",                  # canonical == scope name → omitted
        ToggleMetricT._2STOGGLE,  # default
        ToggleTypeT.NET,          # default
        ToggleDirT.INTERNAL,      # default
    )
    data = ToggleWriter().serialize(db)
    assert data == b""


def test_toggle_writer_captures_canonical():
    """Non-default canonical name is included in entry."""
    db, _ = _make_toggle_db(
        "tb.dut.sig",
        ToggleMetricT._2STOGGLE,
        ToggleTypeT.NET,
        ToggleDirT.INTERNAL,
    )
    data = ToggleWriter().serialize(db)
    payload = json.loads(data)
    assert payload["version"] == 1
    assert len(payload["entries"]) == 1
    assert payload["entries"][0]["canonical"] == "tb.dut.sig"


def test_toggle_writer_captures_type():
    """Non-default toggle type is included."""
    db, _ = _make_toggle_db(
        "sig",
        ToggleMetricT._2STOGGLE,
        ToggleTypeT.REG,           # non-default (default is NET)
        ToggleDirT.INTERNAL,
    )
    data = ToggleWriter().serialize(db)
    payload = json.loads(data)
    assert payload["entries"][0]["type"] == int(ToggleTypeT.REG)


def test_toggle_writer_captures_dir():
    """Non-default toggle direction is included."""
    db, _ = _make_toggle_db(
        "sig",
        ToggleMetricT._2STOGGLE,
        ToggleTypeT.NET,
        ToggleDirT.IN,             # non-default (default is INTERNAL)
    )
    data = ToggleWriter().serialize(db)
    payload = json.loads(data)
    assert payload["entries"][0]["dir"] == int(ToggleDirT.IN)


def test_toggle_reader_restores_canonical():
    """ToggleReader must set canonical name back on scope."""
    db, _ = _make_toggle_db("tb.dut.sig", ToggleMetricT._2STOGGLE,
                             ToggleTypeT.NET, ToggleDirT.INTERNAL)
    data = ToggleWriter().serialize(db)

    db2 = MemUCIS()
    t2 = db2.createToggle("sig", "sig", 0, ToggleMetricT._2STOGGLE,
                           ToggleTypeT.NET, ToggleDirT.INTERNAL)
    ToggleReader().apply(db2, data)
    assert t2.getCanonicalName() == "tb.dut.sig"


def test_toggle_reader_empty_data():
    """Empty bytes must not raise."""
    db = MemUCIS()
    ToggleReader().apply(db, b"")


# ── Integration: NCDB round-trip ─────────────────────────────────────────

def test_toggle_canonical_round_trip():
    """Canonical name survives NCDB write → read."""
    db, _ = _make_toggle_db("tb.dut.my_signal", ToggleMetricT._2STOGGLE,
                             ToggleTypeT.NET, ToggleDirT.INTERNAL)
    rdb, _ = _write_read(db)
    t = list(rdb.scopes(ScopeTypeT.TOGGLE))[0]
    assert t.getCanonicalName() == "tb.dut.my_signal"


def test_toggle_type_round_trip():
    """Toggle type survives NCDB write → read."""
    db, _ = _make_toggle_db("sig", ToggleMetricT._2STOGGLE,
                             ToggleTypeT.REG, ToggleDirT.INTERNAL)
    rdb, _ = _write_read(db)
    t = list(rdb.scopes(ScopeTypeT.TOGGLE))[0]
    assert t.getToggleType() == ToggleTypeT.REG


def test_toggle_dir_round_trip():
    """Toggle direction survives NCDB write → read."""
    db, _ = _make_toggle_db("sig", ToggleMetricT._2STOGGLE,
                             ToggleTypeT.NET, ToggleDirT.OUT)
    rdb, _ = _write_read(db)
    t = list(rdb.scopes(ScopeTypeT.TOGGLE))[0]
    assert t.getToggleDir() == ToggleDirT.OUT


def test_toggle_default_values_no_zip_member():
    """All-default toggle values → toggle.json absent from ZIP."""
    db, _ = _make_toggle_db("sig", ToggleMetricT._2STOGGLE,
                             ToggleTypeT.NET, ToggleDirT.INTERNAL)
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "out.cdb")
        NcdbWriter().write(db, path)
        with zipfile.ZipFile(path) as zf:
            assert MEMBER_TOGGLE not in zf.namelist()


def test_toggle_present_in_zip_when_canonical_differs():
    """Non-default canonical → toggle.json present in ZIP."""
    db, _ = _make_toggle_db("tb.dut.sig", ToggleMetricT._2STOGGLE,
                             ToggleTypeT.NET, ToggleDirT.INTERNAL)
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "out.cdb")
        NcdbWriter().write(db, path)
        with zipfile.ZipFile(path) as zf:
            assert MEMBER_TOGGLE in zf.namelist()


def test_toggle_counts_preserved():
    """Toggle hit counts are unaffected by toggle metadata serialization."""
    db, _ = _make_toggle_db("tb.sig", ToggleMetricT._2STOGGLE,
                             ToggleTypeT.NET, ToggleDirT.IN)
    rdb, _ = _write_read(db)
    t = list(rdb.scopes(ScopeTypeT.TOGGLE))[0]
    items = list(t.coverItems(CoverTypeT.ALL))
    counts = [ci.getCoverData().data for ci in items]
    assert counts == [3, 2]


def test_multiple_toggle_scopes():
    """Multiple TOGGLE scopes each preserve their own metadata."""
    db = MemUCIS()
    db.createHistoryNode(None, "t", None, HistoryNodeKind.TEST)

    sigs = [
        ("sig_a", "tb.a", ToggleDirT.IN),
        ("sig_b", "tb.b", ToggleDirT.OUT),
        ("sig_c", "tb.c", ToggleDirT.INOUT),
    ]
    for name, canon, tdir in sigs:
        t = db.createToggle(name, canon, 0, ToggleMetricT._2STOGGLE,
                            ToggleTypeT.NET, tdir)
        cd = CoverData(CoverTypeT.TOGGLEBIN, 0); cd.data = 1
        t.createNextCover("0->1", cd, None)
        cd2 = CoverData(CoverTypeT.TOGGLEBIN, 0); cd2.data = 0
        t.createNextCover("1->0", cd2, None)

    rdb, _ = _write_read(db)
    toggles = {s.getScopeName(): s
               for s in rdb.scopes(ScopeTypeT.TOGGLE)}
    assert toggles["sig_a"].getCanonicalName() == "tb.a"
    assert toggles["sig_a"].getToggleDir() == ToggleDirT.IN
    assert toggles["sig_b"].getCanonicalName() == "tb.b"
    assert toggles["sig_b"].getToggleDir() == ToggleDirT.OUT
    assert toggles["sig_c"].getCanonicalName() == "tb.c"
    assert toggles["sig_c"].getToggleDir() == ToggleDirT.INOUT
