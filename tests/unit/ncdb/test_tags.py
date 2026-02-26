"""
Tests for ucis.ncdb.tags — scope tag round-trip via NCDB ZIP.
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
from ucis.ncdb.constants import MEMBER_TAGS
from ucis.ncdb.ncdb_reader import NcdbReader
from ucis.ncdb.ncdb_writer import NcdbWriter
from ucis.ncdb.tags import TagsReader, TagsWriter
from ucis.scope_type_t import ScopeTypeT
from ucis.source_t import SourceT


# ── Helpers ───────────────────────────────────────────────────────────────

def _make_db_with_tags(tag_set):
    """Build a MemUCIS with one BLOCK scope tagged with *tag_set*."""
    db = MemUCIS()
    db.createHistoryNode(None, "t", None, HistoryNodeKind.TEST)
    block = db.createScope("blk", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    cd = CoverData(CoverTypeT.STMTBIN, 0)
    cd.data = 1
    block.createNextCover("s0", cd, None)
    for tag in tag_set:
        block.addTag(tag)
    return db, block


def _write_read(db):
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "out.cdb")
        NcdbWriter().write(db, path)
        return NcdbReader().read(path), path


# ── Unit tests: TagsWriter / TagsReader ───────────────────────────────────

def test_tags_writer_empty():
    """No tags → empty entries list."""
    db = MemUCIS()
    db.createScope("blk", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    data = TagsWriter().serialize(db)
    payload = json.loads(data)
    assert payload["version"] == 1
    assert payload["entries"] == []


def test_tags_writer_single():
    """One tag on one scope → one entry."""
    db, _ = _make_db_with_tags({"critical"})
    data = TagsWriter().serialize(db)
    payload = json.loads(data)
    assert len(payload["entries"]) == 1
    assert "critical" in payload["entries"][0]["tags"]


def test_tags_writer_multiple():
    """Multiple tags on one scope → all present."""
    tags = {"a", "b", "c"}
    db, _ = _make_db_with_tags(tags)
    data = TagsWriter().serialize(db)
    payload = json.loads(data)
    assert set(payload["entries"][0]["tags"]) == tags


def test_tags_reader_applies_tags():
    """TagsReader must restore tags on scopes."""
    db, block = _make_db_with_tags({"important"})
    data = TagsWriter().serialize(db)

    db2 = MemUCIS()
    block2 = db2.createScope("blk", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    TagsReader().deserialize(data, db2)
    assert block2.hasTag("important")


def test_tags_reader_empty_data():
    """Empty bytes must not raise."""
    db = MemUCIS()
    TagsReader().deserialize(b'', db)


# ── Integration: NCDB round-trip ─────────────────────────────────────────

def test_tags_round_trip_single():
    """Single tag survives NCDB write → read."""
    db, _ = _make_db_with_tags({"regression"})
    rdb, _ = _write_read(db)
    blocks = list(rdb.scopes(ScopeTypeT.BLOCK))
    assert blocks[0].hasTag("regression")


def test_tags_round_trip_multiple():
    """Multiple tags all survive round-trip."""
    tags = {"tag1", "tag2", "tag3"}
    db, _ = _make_db_with_tags(tags)
    rdb, _ = _write_read(db)
    block = list(rdb.scopes(ScopeTypeT.BLOCK))[0]
    for t in tags:
        assert block.hasTag(t), f"tag '{t}' missing after round-trip"


def test_tags_absent_from_zip_when_empty():
    """No tags → tags member must be absent from ZIP."""
    db = MemUCIS()
    db.createHistoryNode(None, "t", None, HistoryNodeKind.TEST)
    db.createScope("blk", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "out.cdb")
        NcdbWriter().write(db, path)
        with zipfile.ZipFile(path) as zf:
            assert MEMBER_TAGS not in zf.namelist()


def test_tags_present_in_zip_when_set():
    """If any tag is set, tags member must appear in ZIP."""
    db, _ = _make_db_with_tags({"check"})
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "out.cdb")
        NcdbWriter().write(db, path)
        with zipfile.ZipFile(path) as zf:
            assert MEMBER_TAGS in zf.namelist()


def test_tags_hasTag_false_for_unset():
    """hasTag must return False for a tag that was never set."""
    db, _ = _make_db_with_tags({"present"})
    rdb, _ = _write_read(db)
    block = list(rdb.scopes(ScopeTypeT.BLOCK))[0]
    assert not block.hasTag("absent")
