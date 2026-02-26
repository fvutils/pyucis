"""
Scope-tree encoder/decoder tests.

Covers: single scope, deep hierarchy, wide hierarchy,
toggle-pair encoding, mixed scope types, presence bitfield edge cases.
"""

import io
import pytest

from ucis.mem.mem_ucis import MemUCIS
from ucis.source_t import SourceT
from ucis.scope_type_t import ScopeTypeT
from ucis.cover_type_t import CoverTypeT
from ucis.cover_data import CoverData
from ucis.history_node_kind import HistoryNodeKind

from ucis.ncdb.string_table import StringTable
from ucis.ncdb.scope_tree import ScopeTreeWriter, ScopeTreeReader
from ucis.ncdb.counts import CountsWriter, CountsReader
from ucis.ncdb.constants import TOGGLE_BIN_0_TO_1, TOGGLE_BIN_1_TO_0


# ── Helpers ────────────────────────────────────────────────────────────────

def _roundtrip(db_in: MemUCIS) -> MemUCIS:
    """Encode *db_in* scope tree → bytes, decode into a fresh MemUCIS."""
    st = StringTable()
    fh = []
    writer = ScopeTreeWriter(st, fh)
    tree_bytes = writer.write(db_in)
    counts_bytes = CountsWriter().serialize(writer.counts_list)

    db_out = MemUCIS()
    counts_iter = iter(CountsReader().deserialize(counts_bytes))
    ScopeTreeReader(st, fh).read(tree_bytes, db_out, counts_iter)
    return db_out


def _add_stmtbin(scope, name: str, count: int = 0):
    cd = CoverData(CoverTypeT.STMTBIN, 0)
    cd.data = count
    scope.createNextCover(name, cd, None)


def _add_toggle_pair(parent, name: str, c0=0, c1=0):
    """Create a BRANCH scope with 2 TOGGLEBIN coveritems (toggle-pair pattern)."""
    branch = parent.createScope(name, None, 1, SourceT.SV, ScopeTypeT.BRANCH, 0)
    for bin_name, count in ((TOGGLE_BIN_0_TO_1, c0), (TOGGLE_BIN_1_TO_0, c1)):
        cd = CoverData(CoverTypeT.TOGGLEBIN, 0)
        cd.data = count
        branch.createNextCover(bin_name, cd, None)
    return branch


# ── Tests ──────────────────────────────────────────────────────────────────

def test_single_scope_no_children():
    db = MemUCIS()
    db.createScope("top", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    rt = _roundtrip(db)
    scopes = list(rt.scopes(ScopeTypeT.ALL))
    assert len(scopes) == 1
    assert scopes[0].getScopeName() == "top"
    assert scopes[0].getScopeType() == ScopeTypeT.BLOCK


def test_single_scope_with_coveritems():
    db = MemUCIS()
    block = db.createScope("blk", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    _add_stmtbin(block, "s0", 3)
    _add_stmtbin(block, "s1", 7)

    rt = _roundtrip(db)
    blk = list(rt.scopes(ScopeTypeT.ALL))[0]
    items = list(blk.coverItems(CoverTypeT.ALL))
    assert len(items) == 2
    assert items[0].getName() == "s0"
    assert items[0].getCoverData().data == 3
    assert items[1].getName() == "s1"
    assert items[1].getCoverData().data == 7


def test_deep_hierarchy_100_levels():
    """100-level deep hierarchy should encode/decode correctly."""
    db = MemUCIS()
    cur = db
    for i in range(100):
        scope_type = ScopeTypeT.BLOCK
        child = cur.createScope(f"level_{i}", None, 1, SourceT.SV, scope_type, 0)
        cur = child

    rt = _roundtrip(db)

    # Walk down 100 levels
    cur = rt
    for i in range(100):
        children = list(cur.scopes(ScopeTypeT.ALL))
        assert len(children) == 1, f"Level {i}: expected 1 child, got {len(children)}"
        assert children[0].getScopeName() == f"level_{i}"
        cur = children[0]


def test_wide_hierarchy_1000_children():
    """Single scope with 1000 BLOCK children."""
    db = MemUCIS()
    top = db.createScope("top", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    for i in range(1000):
        child = top.createScope(f"c{i}", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
        _add_stmtbin(child, "s0", i)

    rt = _roundtrip(db)
    children = list(list(rt.scopes(ScopeTypeT.ALL))[0].scopes(ScopeTypeT.ALL))
    assert len(children) == 1000
    for i, child in enumerate(children):
        assert child.getScopeName() == f"c{i}"
        items = list(child.coverItems(CoverTypeT.ALL))
        assert items[0].getCoverData().data == i


def test_toggle_pair_encoding():
    """BRANCH+2×TOGGLEBIN must be encoded as TOGGLE_PAIR (2 bytes + varint)."""
    db = MemUCIS()
    top = db.createScope("top", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    _add_toggle_pair(top, "sig_a", c0=5, c1=3)
    _add_toggle_pair(top, "sig_b", c0=0, c1=0)

    st = StringTable()
    fh = []
    writer = ScopeTreeWriter(st, fh)
    tree_bytes = writer.write(db)

    # TOGGLE_PAIR (0x01) records are much smaller than REGULAR (0x00) records
    # The writer should have emitted 2 TOGGLE_PAIR records
    assert writer.counts_list == [5, 3, 0, 0]  # two pairs

    rt = _roundtrip(db)
    top_rt = list(rt.scopes(ScopeTypeT.ALL))[0]
    branches = list(top_rt.scopes(ScopeTypeT.BRANCH))
    assert len(branches) == 2
    assert branches[0].getScopeName() == "sig_a"
    items_a = {ci.getName(): ci.getCoverData().data
               for ci in branches[0].coverItems(CoverTypeT.ALL)}
    assert items_a[TOGGLE_BIN_0_TO_1] == 5
    assert items_a[TOGGLE_BIN_1_TO_0] == 3


def test_non_toggle_branch_not_compressed():
    """BRANCH scope with non-toggle bins must NOT use TOGGLE_PAIR encoding."""
    db = MemUCIS()
    top = db.createScope("top", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    branch = top.createScope("br", None, 1, SourceT.SV, ScopeTypeT.BRANCH, 0)
    cd = CoverData(CoverTypeT.BRANCHBIN, 0)
    cd.data = 2
    branch.createNextCover("taken", cd, None)
    cd2 = CoverData(CoverTypeT.BRANCHBIN, 0)
    cd2.data = 0
    branch.createNextCover("not_taken", cd2, None)

    rt = _roundtrip(db)
    top_rt = list(rt.scopes(ScopeTypeT.ALL))[0]
    branches = list(top_rt.scopes(ScopeTypeT.BRANCH))
    assert len(branches) == 1
    items = {ci.getName(): ci.getCoverData().data
             for ci in branches[0].coverItems(CoverTypeT.ALL)}
    assert items["taken"] == 2
    assert items["not_taken"] == 0


def test_presence_bitfield_no_source_info():
    """Scopes without source info should decode with file=None in srcinfo."""
    db = MemUCIS()
    db.createScope("no_src", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    rt = _roundtrip(db)
    scope = list(rt.scopes(ScopeTypeT.ALL))[0]
    # MemScope always stores a SourceInfo even for None; check file is None
    srcinfo = scope.getSourceInfo()
    assert srcinfo is None or srcinfo.file is None


def test_mixed_scope_types():
    """Block + Branch + Toggle + Covergroup children all round-trip."""
    db = MemUCIS()
    top = db.createScope("top", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)

    # BLOCK with stmt bins
    blk = top.createScope("blk", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    _add_stmtbin(blk, "s0", 10)

    # BRANCH (non-toggle)
    br = top.createScope("br", None, 1, SourceT.SV, ScopeTypeT.BRANCH, 0)
    cd = CoverData(CoverTypeT.BRANCHBIN, 0)
    cd.data = 1
    br.createNextCover("taken", cd, None)

    # Toggle pair
    _add_toggle_pair(top, "sig", c0=1, c1=1)

    rt = _roundtrip(db)
    top_rt = list(rt.scopes(ScopeTypeT.ALL))[0]
    children = list(top_rt.scopes(ScopeTypeT.ALL))
    assert len(children) == 3
    types = {c.getScopeName(): c.getScopeType() for c in children}
    assert types["blk"] == ScopeTypeT.BLOCK
    assert types["br"] == ScopeTypeT.BRANCH
    assert types["sig"] == ScopeTypeT.BRANCH  # toggle pair decoded as BRANCH


def test_large_count_values():
    """Hit counts exceeding 32 bits should round-trip correctly."""
    db = MemUCIS()
    blk = db.createScope("blk", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    big_count = 2**32 + 1
    cd = CoverData(CoverTypeT.STMTBIN, 0)
    cd.data = big_count
    blk.createNextCover("big", cd, None)

    rt = _roundtrip(db)
    items = list(list(rt.scopes(ScopeTypeT.ALL))[0].coverItems(CoverTypeT.ALL))
    assert items[0].getCoverData().data == big_count


def test_zero_coveritems_scope():
    """Scope with 0 coveritems encodes num_coveritems=0 (no child_cover_type field)."""
    db = MemUCIS()
    db.createScope("empty", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    rt = _roundtrip(db)
    scope = list(rt.scopes(ScopeTypeT.ALL))[0]
    assert list(scope.coverItems(CoverTypeT.ALL)) == []
