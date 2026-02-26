"""
Tests for PropertiesWriter / PropertiesReader round-trip.
"""

import tempfile
import os

import pytest

from ucis.mem.mem_ucis import MemUCIS
from ucis.source_t import SourceT
from ucis.scope_type_t import ScopeTypeT
from ucis.cover_data import CoverData
from ucis.cover_type_t import CoverTypeT
from ucis.history_node_kind import HistoryNodeKind
from ucis.str_property import StrProperty

from ucis.ncdb.properties import PropertiesWriter, PropertiesReader
from ucis.ncdb.dfs_util import dfs_scope_list
from ucis.ncdb.ncdb_writer import NcdbWriter
from ucis.ncdb.ncdb_reader import NcdbReader


def _make_db_with_comment(comment="hello"):
    db = MemUCIS()
    db.createHistoryNode(None, "t1", None, HistoryNodeKind.TEST)
    blk = db.createScope("top", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    cd = CoverData(CoverTypeT.STMTBIN, 0)
    cd.data = 1
    blk.createNextCover("s0", cd, None)
    blk.setStringProperty(-1, StrProperty.COMMENT, comment)
    return db


# ── PropertiesWriter unit tests ────────────────────────────────────────────

def test_no_properties_returns_empty():
    """DB with no string properties → empty bytes."""
    db = MemUCIS()
    db.createScope("top", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    result = PropertiesWriter().serialize(db)
    assert result == b""


def test_single_comment_serializes():
    """A scope with COMMENT → non-empty JSON."""
    db = _make_db_with_comment("my comment")
    result = PropertiesWriter().serialize(db)
    assert result != b""
    import json
    payload = json.loads(result)
    assert payload["version"] == 1
    assert len(payload["entries"]) == 1
    entry = payload["entries"][0]
    assert entry["kind"] == "scope"
    assert entry["key"] == int(StrProperty.COMMENT)
    assert entry["type"] == "str"
    assert entry["value"] == "my comment"


def test_multiple_scopes_multiple_comments():
    """Two scopes with different comments."""
    db = MemUCIS()
    s1 = db.createScope("a", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    s2 = db.createScope("b", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    s1.setStringProperty(-1, StrProperty.COMMENT, "comment A")
    s2.setStringProperty(-1, StrProperty.COMMENT, "comment B")
    result = PropertiesWriter().serialize(db)
    import json
    payload = json.loads(result)
    assert len(payload["entries"]) == 2
    values = {e["idx"]: e["value"] for e in payload["entries"]}
    # DFS order: a=0, b=1
    assert values[0] == "comment A"
    assert values[1] == "comment B"


# ── Round-trip via apply() ─────────────────────────────────────────────────

def test_properties_round_trip_via_apply():
    """serialize + apply restores COMMENT on the scope."""
    db_src = _make_db_with_comment("test comment")
    data = PropertiesWriter().serialize(db_src)

    # New empty DB with same scope structure
    db_dst = MemUCIS()
    db_dst.createScope("top", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)

    PropertiesReader().apply(db_dst, data)

    scopes = dfs_scope_list(db_dst)
    val = scopes[0].getStringProperty(-1, StrProperty.COMMENT)
    assert val == "test comment"


def test_apply_empty_bytes_is_noop():
    """apply() with empty bytes does nothing."""
    db = MemUCIS()
    db.createScope("top", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    PropertiesReader().apply(db, b"")  # must not raise


def test_apply_out_of_range_index_ignored():
    """apply() silently ignores entries whose idx > scope count."""
    import json
    payload = {"version": 1, "entries": [
        {"kind": "scope", "idx": 9999, "key": int(StrProperty.COMMENT),
         "type": "str", "value": "x"}
    ]}
    db = MemUCIS()
    db.createScope("top", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    PropertiesReader().apply(db, json.dumps(payload).encode())  # must not raise


# ── Full NCDB round-trip ───────────────────────────────────────────────────

def test_ncdb_round_trip_preserves_comment():
    """NcdbWriter → NcdbReader preserves COMMENT string property."""
    db = _make_db_with_comment("round-trip comment")
    with tempfile.NamedTemporaryFile(suffix=".cdb", delete=False) as f:
        path = f.name
    try:
        NcdbWriter().write(db, path)
        rt = NcdbReader().read(path)
        scopes = dfs_scope_list(rt)
        val = scopes[0].getStringProperty(-1, StrProperty.COMMENT)
        assert val == "round-trip comment"
    finally:
        os.unlink(path)


def test_ncdb_round_trip_no_properties_member_when_empty():
    """NcdbWriter doesn't add properties.json when there are no properties."""
    import zipfile
    from ucis.ncdb.constants import MEMBER_PROPERTIES
    db = MemUCIS()
    db.createScope("top", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    with tempfile.NamedTemporaryFile(suffix=".cdb", delete=False) as f:
        path = f.name
    try:
        NcdbWriter().write(db, path)
        with zipfile.ZipFile(path) as zf:
            assert MEMBER_PROPERTIES not in zf.namelist()
    finally:
        os.unlink(path)


def test_ncdb_round_trip_properties_member_present_when_set():
    """NcdbWriter writes properties.json when a scope has a comment."""
    import zipfile
    from ucis.ncdb.constants import MEMBER_PROPERTIES
    db = _make_db_with_comment("x")
    with tempfile.NamedTemporaryFile(suffix=".cdb", delete=False) as f:
        path = f.name
    try:
        NcdbWriter().write(db, path)
        with zipfile.ZipFile(path) as zf:
            assert MEMBER_PROPERTIES in zf.namelist()
    finally:
        os.unlink(path)
