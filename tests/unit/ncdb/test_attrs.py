"""
Tests for ucis.ncdb.attrs — user-defined attribute round-trip via NCDB ZIP.
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
from ucis.ncdb.attrs import AttrsReader, AttrsWriter
from ucis.ncdb.constants import MEMBER_ATTRS
from ucis.ncdb.ncdb_reader import NcdbReader
from ucis.ncdb.ncdb_writer import NcdbWriter
from ucis.scope_type_t import ScopeTypeT
from ucis.source_t import SourceT


# ── Helpers ───────────────────────────────────────────────────────────────

def _make_db_with_attrs(attr_map):
    """Build a MemUCIS with a single BLOCK scope; apply *attr_map* to it."""
    db = MemUCIS()
    db.createHistoryNode(None, "t", None, HistoryNodeKind.TEST)
    block = db.createScope("blk", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    cd = CoverData(CoverTypeT.STMTBIN, 0)
    cd.data = 7
    block.createNextCover("s0", cd, None)
    for k, v in attr_map.items():
        block.setAttribute(k, v)
    return db, block


def _write_read(db):
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "out.cdb")
        NcdbWriter().write(db, path)
        return NcdbReader().read(path), path


# ── Unit tests: AttrsWriter / AttrsReader ─────────────────────────────────

def test_attrs_writer_empty():
    """No attrs → empty entries list."""
    db = MemUCIS()
    db.createScope("blk", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    data = AttrsWriter().serialize(db)
    payload = json.loads(data)
    assert payload["version"] == 2
    assert payload["scopes"] == []


def test_attrs_writer_single():
    """One scope with one attr → one entry."""
    db, block = _make_db_with_attrs({"author": "alice"})
    data = AttrsWriter().serialize(db)
    payload = json.loads(data)
    assert len(payload["scopes"]) == 1
    assert payload["scopes"][0]["attrs"] == {"author": "alice"}


def test_attrs_writer_multiple_keys():
    """Multiple attrs on one scope → all keys present."""
    db, block = _make_db_with_attrs({"k1": "v1", "k2": "v2", "k3": "v3"})
    data = AttrsWriter().serialize(db)
    payload = json.loads(data)
    assert payload["scopes"][0]["attrs"] == {"k1": "v1", "k2": "v2", "k3": "v3"}


def test_attrs_reader_applies_attrs():
    """AttrsReader must set attributes back onto scopes."""
    db, block = _make_db_with_attrs({"foo": "bar"})
    data = AttrsWriter().serialize(db)

    # Fresh DB, re-create same scope tree structure
    db2 = MemUCIS()
    block2 = db2.createScope("blk", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    AttrsReader().deserialize(data, db2)
    assert block2.getAttribute("foo") == "bar"


def test_attrs_reader_empty_data():
    """Empty bytes must not raise."""
    db = MemUCIS()
    AttrsReader().deserialize(b'', db)  # should not raise


# ── Integration: NCDB round-trip ─────────────────────────────────────────

def test_attrs_round_trip_single():
    """Attribute survives NCDB write → read."""
    db, _ = _make_db_with_attrs({"tool": "pytest"})
    rdb, _ = _write_read(db)
    blocks = list(rdb.scopes(ScopeTypeT.BLOCK))
    assert len(blocks) == 1
    assert blocks[0].getAttribute("tool") == "pytest"


def test_attrs_round_trip_multiple():
    """Multiple attributes all survive round-trip."""
    attrs = {"a": "1", "b": "hello world", "c": "true"}
    db, _ = _make_db_with_attrs(attrs)
    rdb, _ = _write_read(db)
    block = list(rdb.scopes(ScopeTypeT.BLOCK))[0]
    for k, v in attrs.items():
        assert block.getAttribute(k) == v, f"attr '{k}' mismatch"


def test_attrs_absent_from_zip_when_empty():
    """No attrs → attrs member must be absent from ZIP."""
    db = MemUCIS()
    db.createHistoryNode(None, "t", None, HistoryNodeKind.TEST)
    db.createScope("blk", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "out.cdb")
        NcdbWriter().write(db, path)
        with zipfile.ZipFile(path) as zf:
            assert MEMBER_ATTRS not in zf.namelist()


def test_attrs_present_in_zip_when_set():
    """If any attr is set, attrs member must appear in ZIP."""
    db, _ = _make_db_with_attrs({"x": "y"})
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "out.cdb")
        NcdbWriter().write(db, path)
        with zipfile.ZipFile(path) as zf:
            assert MEMBER_ATTRS in zf.namelist()
