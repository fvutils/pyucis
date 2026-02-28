"""
Tests for ucis.ncdb.cross — CROSS scope coverpoint link round-trip via NCDB ZIP.
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
from ucis.ncdb.constants import MEMBER_CROSS
from ucis.ncdb.cross import CrossReader, CrossWriter
from ucis.ncdb.ncdb_reader import NcdbReader
from ucis.ncdb.ncdb_writer import NcdbWriter
from ucis.scope_type_t import ScopeTypeT
from ucis.source_t import SourceT


# ── Helpers ───────────────────────────────────────────────────────────────

def _make_cross_db(num_bins=4):
    """Build a MemUCIS with a COVERGROUP → COVERINSTANCE → 2 COVERPOINTs + CROSS."""
    db = MemUCIS()
    db.createHistoryNode(None, "t", None, HistoryNodeKind.TEST)
    cg = db.createScope("cg", None, 1, SourceT.SV, ScopeTypeT.COVERGROUP, 0)
    ci = cg.createScope("cg", None, 1, SourceT.SV, ScopeTypeT.COVERINSTANCE, 0)

    cp1 = ci.createScope("cp_a", None, 1, SourceT.SV, ScopeTypeT.COVERPOINT, 0)
    cp2 = ci.createScope("cp_b", None, 1, SourceT.SV, ScopeTypeT.COVERPOINT, 0)

    for i in range(2):
        cd = CoverData(CoverTypeT.CVGBIN, 0); cd.data = i + 1
        cp1.createNextCover(f"a{i}", cd, None)
    for i in range(2):
        cd = CoverData(CoverTypeT.CVGBIN, 0); cd.data = i + 1
        cp2.createNextCover(f"b{i}", cd, None)

    cross = ci.createCross("cp_a X cp_b", None, 1, SourceT.SV, [cp1, cp2])
    for i in range(num_bins):
        cd = CoverData(CoverTypeT.DEFAULTBIN, 0); cd.data = i + 1
        cross.createNextCover(f"cross_{i}", cd, None)

    return db, cross, cp1, cp2


def _write_read(db):
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "out.cdb")
        NcdbWriter().write(db, path)
        return NcdbReader().read(path), path


def _first_cross(db):
    def _walk(scope):
        if scope.getScopeType() == ScopeTypeT.CROSS:
            return scope
        for c in scope.scopes(ScopeTypeT.ALL):
            r = _walk(c)
            if r:
                return r
        return None
    for s in db.scopes(ScopeTypeT.ALL):
        r = _walk(s)
        if r:
            return r
    return None


# ── Unit tests: CrossWriter / CrossReader ─────────────────────────────────

def test_cross_writer_empty_when_no_cross():
    """DB without CROSS scopes → empty bytes."""
    db = MemUCIS()
    db.createScope("blk", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    assert CrossWriter().serialize(db) == b""


def test_cross_writer_captures_crossed_names():
    """Writer must record crossed coverpoint names."""
    db, cross, cp1, cp2 = _make_cross_db()
    data = CrossWriter().serialize(db)
    payload = json.loads(data)
    assert payload["version"] == 1
    assert len(payload["entries"]) == 1
    crossed = payload["entries"][0]["crossed"]
    assert "cp_a" in crossed
    assert "cp_b" in crossed


def test_cross_reader_empty_data():
    """Empty bytes must not raise."""
    db = MemUCIS()
    CrossReader().apply(db, b"")


def test_cross_reader_restores_links():
    """CrossReader must populate coverpoints list on CROSS scope."""
    db, cross, cp1, cp2 = _make_cross_db()
    data = CrossWriter().serialize(db)

    # Simulate a freshly-deserialized cross scope with no coverpoints
    cross.coverpoints = []
    assert cross.getNumCrossedCoverpoints() == 0

    CrossReader().apply(db, data)
    assert cross.getNumCrossedCoverpoints() == 2


# ── Integration: NCDB round-trip ─────────────────────────────────────────

def test_cross_round_trip_num_crossed():
    """Number of crossed coverpoints survives NCDB write → read."""
    db, _, _, _ = _make_cross_db()
    rdb, _ = _write_read(db)
    cross = _first_cross(rdb)
    assert cross is not None
    assert cross.getNumCrossedCoverpoints() == 2


def test_cross_round_trip_crossed_names():
    """Crossed coverpoint names are correct after round-trip."""
    db, _, _, _ = _make_cross_db()
    rdb, _ = _write_read(db)
    cross = _first_cross(rdb)
    names = {cross.getIthCrossedCoverpoint(i).getScopeName()
             for i in range(cross.getNumCrossedCoverpoints())}
    assert names == {"cp_a", "cp_b"}


def test_cross_round_trip_bin_counts():
    """Cross bin counts survive round-trip."""
    db, _, _, _ = _make_cross_db(num_bins=4)
    rdb, _ = _write_read(db)
    cross = _first_cross(rdb)
    counts = [ci.getCoverData().data
              for ci in cross.coverItems(CoverTypeT.ALL)]
    assert counts == [1, 2, 3, 4]


def test_cross_absent_from_zip_when_no_cross():
    """No CROSS scopes → cross.json must be absent from ZIP."""
    db = MemUCIS()
    db.createHistoryNode(None, "t", None, HistoryNodeKind.TEST)
    db.createScope("blk", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "out.cdb")
        NcdbWriter().write(db, path)
        with zipfile.ZipFile(path) as zf:
            assert MEMBER_CROSS not in zf.namelist()


def test_cross_present_in_zip_when_cross_exists():
    """CROSS scope present → cross.json must appear in ZIP."""
    db, _, _, _ = _make_cross_db()
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "out.cdb")
        NcdbWriter().write(db, path)
        with zipfile.ZipFile(path) as zf:
            assert MEMBER_CROSS in zf.namelist()


def test_cross_coverpoints_are_actual_siblings():
    """Resolved coverpoints must be the same objects as the sibling scopes."""
    db, _, _, _ = _make_cross_db()
    rdb, _ = _write_read(db)
    cross = _first_cross(rdb)

    # Find the parent COVERINSTANCE
    parent = cross.m_parent
    sibling_names = {s.getScopeName(): s
                     for s in parent.scopes(ScopeTypeT.ALL)}

    for i in range(cross.getNumCrossedCoverpoints()):
        cp = cross.getIthCrossedCoverpoint(i)
        assert cp.getScopeName() in sibling_names
        assert cp is sibling_names[cp.getScopeName()]


def test_cross_three_way():
    """Three-way cross: all three coverpoints resolved."""
    db = MemUCIS()
    db.createHistoryNode(None, "t", None, HistoryNodeKind.TEST)
    cg = db.createScope("cg", None, 1, SourceT.SV, ScopeTypeT.COVERGROUP, 0)
    ci = cg.createScope("cg", None, 1, SourceT.SV, ScopeTypeT.COVERINSTANCE, 0)

    cps = []
    for letter in ("x", "y", "z"):
        cp = ci.createScope(f"cp_{letter}", None, 1, SourceT.SV,
                            ScopeTypeT.COVERPOINT, 0)
        cd = CoverData(CoverTypeT.CVGBIN, 0); cd.data = 1
        cp.createNextCover("b0", cd, None)
        cps.append(cp)

    cross = ci.createCross("x_y_z", None, 1, SourceT.SV, cps)
    for i in range(8):
        cd = CoverData(CoverTypeT.DEFAULTBIN, 0); cd.data = i
        cross.createNextCover(f"c{i}", cd, None)

    rdb, _ = _write_read(db)
    rcross = _first_cross(rdb)
    assert rcross.getNumCrossedCoverpoints() == 3
    names = {rcross.getIthCrossedCoverpoint(i).getScopeName()
             for i in range(3)}
    assert names == {"cp_x", "cp_y", "cp_z"}
