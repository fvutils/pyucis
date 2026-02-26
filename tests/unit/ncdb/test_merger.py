"""
Tests for ucis.ncdb.ncdb_merger — same-schema and cross-schema merge.
"""

import os
import tempfile
import pytest

from ucis.ncdb.ncdb_writer import NcdbWriter
from ucis.ncdb.ncdb_reader import NcdbReader
from ucis.ncdb.ncdb_merger import NcdbMerger
from ucis.ncdb.manifest import Manifest
from ucis.cover_type_t import CoverTypeT
from ucis.scope_type_t import ScopeTypeT
from ucis.history_node_kind import HistoryNodeKind
from ucis.mem.mem_ucis import MemUCIS
from ucis.source_t import SourceT
from ucis.cover_data import CoverData


# ── Helper: build a simple UCIS DB ────────────────────────────────────────

def _make_simple_db(counts, name="test1"):
    """Build a MemUCIS with a single BLOCK scope containing STMTBIN items."""
    db = MemUCIS()
    hn = db.createHistoryNode(None, name, None, HistoryNodeKind.TEST)
    block = db.createScope("top", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    for i, c in enumerate(counts):
        cd = CoverData(CoverTypeT.STMTBIN, 0)
        cd.data = c
        block.createNextCover(f"stmt_{i}", cd, None)
    return db


def _write_ncdb(db, path):
    NcdbWriter().write(db, path)


def _collect_counts(db):
    counts = []
    def _walk(scope):
        for ci in scope.coverItems(CoverTypeT.ALL):
            counts.append(ci.getCoverData().data)
        for child in scope.scopes(ScopeTypeT.ALL):
            _walk(child)
    for top in db.scopes(ScopeTypeT.ALL):
        _walk(top)
    return counts


# ── Same-schema merge ─────────────────────────────────────────────────────

def test_same_schema_merge_counts():
    """Merged counts must equal element-wise sum of sources."""
    counts_a = [1, 0, 3, 0, 5]
    counts_b = [0, 2, 0, 4, 0]
    expected  = [1, 2, 3, 4, 5]

    with tempfile.TemporaryDirectory() as d:
        pa = os.path.join(d, "a.cdb")
        pb = os.path.join(d, "b.cdb")
        pm = os.path.join(d, "merged.cdb")

        _write_ncdb(_make_simple_db(counts_a, "test_a"), pa)
        _write_ncdb(_make_simple_db(counts_b, "test_b"), pb)

        NcdbMerger().merge([pa, pb], pm)

        merged_db = NcdbReader().read(pm)
        result = _collect_counts(merged_db)
        assert result == expected


def test_same_schema_merge_item_count():
    """Merged database must have same number of items as each source."""
    counts = [10, 20, 30]
    with tempfile.TemporaryDirectory() as d:
        pa = os.path.join(d, "a.cdb")
        pb = os.path.join(d, "b.cdb")
        pm = os.path.join(d, "merged.cdb")
        _write_ncdb(_make_simple_db(counts, "a"), pa)
        _write_ncdb(_make_simple_db(counts, "b"), pb)
        NcdbMerger().merge([pa, pb], pm)
        merged_db = NcdbReader().read(pm)
        result = _collect_counts(merged_db)
        assert len(result) == len(counts)


def test_multi_source_merge():
    """Merge 4 sources: result counts == sum of all."""
    import random
    rng = random.Random(42)
    N = 20
    source_counts = [[rng.randint(0, 10) for _ in range(N)] for _ in range(4)]
    expected = [sum(source_counts[j][i] for j in range(4)) for i in range(N)]

    with tempfile.TemporaryDirectory() as d:
        paths = []
        for k, cnts in enumerate(source_counts):
            p = os.path.join(d, f"src_{k}.cdb")
            _write_ncdb(_make_simple_db(cnts, f"t{k}"), p)
            paths.append(p)
        pm = os.path.join(d, "merged.cdb")
        NcdbMerger().merge(paths, pm)
        merged_db = NcdbReader().read(pm)
        assert _collect_counts(merged_db) == expected


def test_same_schema_preserves_schema_hash():
    """Same-schema merge output should share the schema_hash of sources."""
    with tempfile.TemporaryDirectory() as d:
        pa = os.path.join(d, "a.cdb")
        pb = os.path.join(d, "b.cdb")
        pm = os.path.join(d, "merged.cdb")
        db = _make_simple_db([1, 2, 3], "t")
        _write_ncdb(db, pa)
        _write_ncdb(db, pb)
        NcdbMerger().merge([pa, pb], pm)

        import zipfile, json
        with zipfile.ZipFile(pa) as zf:
            mf_a = json.loads(zf.read("manifest.json"))
        with zipfile.ZipFile(pm) as zf:
            mf_m = json.loads(zf.read("manifest.json"))
        assert mf_a["schema_hash"] == mf_m["schema_hash"]


# ── History accumulation ──────────────────────────────────────────────────

def test_merge_history_accumulation():
    """All source TEST history nodes must appear in merged output."""
    with tempfile.TemporaryDirectory() as d:
        pa = os.path.join(d, "a.cdb")
        pb = os.path.join(d, "b.cdb")
        pm = os.path.join(d, "merged.cdb")
        _write_ncdb(_make_simple_db([1], "test_alpha"), pa)
        _write_ncdb(_make_simple_db([2], "test_beta"), pb)
        NcdbMerger().merge([pa, pb], pm)
        merged_db = NcdbReader().read(pm)
        names = {n.getLogicalName()
                 for n in merged_db.historyNodes(HistoryNodeKind.TEST)}
        assert "test_alpha" in names
        assert "test_beta" in names


def test_merge_adds_merge_history_node():
    """A MERGE HistoryNode should be present in the merged output."""
    with tempfile.TemporaryDirectory() as d:
        pa = os.path.join(d, "a.cdb")
        pb = os.path.join(d, "b.cdb")
        pm = os.path.join(d, "merged.cdb")
        _write_ncdb(_make_simple_db([1], "t1"), pa)
        _write_ncdb(_make_simple_db([1], "t2"), pb)
        NcdbMerger().merge([pa, pb], pm)
        merged_db = NcdbReader().read(pm)
        merge_nodes = list(merged_db.historyNodes(HistoryNodeKind.MERGE))
        assert len(merge_nodes) >= 1


# ── Nested INSTANCE merge (DbMerger recursive walk) ──────────────────────

def _make_nested_db(counts, hist_name):
    """DB with top -> mid -> leaf nested INSTANCE hierarchy; leaf has a BLOCK
    scope containing STMTBIN items whose hit counts are *counts*."""
    db = MemUCIS()
    db.createHistoryNode(None, hist_name, None, HistoryNodeKind.TEST)

    def _make_level(parent, inst_name):
        du = parent.createScope(inst_name, None, 1, SourceT.SV, ScopeTypeT.DU_MODULE, 0)
        return parent.createInstance(inst_name, None, 1, SourceT.SV,
                                     ScopeTypeT.INSTANCE, du, 0)

    top  = _make_level(db,  "top")
    mid  = _make_level(top, "mid")
    leaf = _make_level(mid, "leaf")

    block = leaf.createScope("blk", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    for i, c in enumerate(counts):
        cd = CoverData(CoverTypeT.STMTBIN, 0)
        cd.data = c
        block.createNextCover(f"stmt_{i}", cd, None)
    return db


def test_nested_instance_merge_structure():
    """Merged DB must contain the same nested INSTANCE hierarchy."""
    from ucis.mem.mem_ucis import MemUCIS
    from ucis.merge.db_merger import DbMerger

    db_a = _make_nested_db([1, 2, 3], "a")
    db_b = _make_nested_db([4, 5, 6], "b")

    dst = MemUCIS()
    DbMerger().merge(dst, [db_a, db_b])

    # Navigate top -> mid -> leaf
    tops = list(dst.scopes(ScopeTypeT.INSTANCE))
    assert len(tops) == 1 and tops[0].getScopeName() == "top"
    mids = list(tops[0].scopes(ScopeTypeT.INSTANCE))
    assert len(mids) == 1 and mids[0].getScopeName() == "mid"
    leafs = list(mids[0].scopes(ScopeTypeT.INSTANCE))
    assert len(leafs) == 1 and leafs[0].getScopeName() == "leaf"


def test_nested_instance_merge_counts():
    """Coverage counts in nested INSTANCE must be summed."""
    from ucis.mem.mem_ucis import MemUCIS
    from ucis.merge.db_merger import DbMerger

    counts_a = [1, 2, 3]
    counts_b = [10, 20, 30]
    expected  = [11, 22, 33]

    db_a = _make_nested_db(counts_a, "a")
    db_b = _make_nested_db(counts_b, "b")

    dst = MemUCIS()
    DbMerger().merge(dst, [db_a, db_b])

    tops  = list(dst.scopes(ScopeTypeT.INSTANCE))
    mids  = list(tops[0].scopes(ScopeTypeT.INSTANCE))
    leafs = list(mids[0].scopes(ScopeTypeT.INSTANCE))
    blocks = list(leafs[0].scopes(ScopeTypeT.BLOCK))
    result = [ci.getCoverData().data
              for ci in blocks[0].coverItems(CoverTypeT.ALL)]
    assert result == expected


def test_nested_instance_merge_history():
    """Both source history nodes must appear in merged DB."""
    from ucis.mem.mem_ucis import MemUCIS
    from ucis.merge.db_merger import DbMerger

    dst = MemUCIS()
    DbMerger().merge(dst, [
        _make_nested_db([1], "test_alpha"),
        _make_nested_db([2], "test_beta"),
    ])
    names = {n.getLogicalName()
             for n in dst.historyNodes(HistoryNodeKind.TEST)}
    assert "test_alpha" in names
    assert "test_beta" in names


# ── Cross-schema merge ────────────────────────────────────────────────────

def _make_db_with_scope(scope_name, bin_count, hist_name):
    """DB with a BLOCK scope under a INSTANCE->DU structure."""
    from ucis.mem.mem_ucis import MemUCIS
    db = MemUCIS()
    db.createHistoryNode(None, hist_name, None, HistoryNodeKind.TEST)
    # Create a DU + INSTANCE to satisfy DbMerger's INSTANCE-based walk
    du = db.createScope(scope_name, None, 1, SourceT.SV, ScopeTypeT.DU_MODULE, 0)
    inst = db.createInstance(scope_name, None, 1, SourceT.SV,
                             ScopeTypeT.INSTANCE, du, 0)
    block = inst.createScope("blk", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    for i in range(bin_count):
        cd = CoverData(CoverTypeT.STMTBIN, 0)
        cd.data = i + 1
        block.createNextCover(f"stmt_{i}", cd, None)
    return db


def test_cross_schema_merge_union():
    """Cross-schema merge should contain bins from both sources."""
    with tempfile.TemporaryDirectory() as d:
        pa = os.path.join(d, "a.cdb")
        pb = os.path.join(d, "b.cdb")
        pm = os.path.join(d, "merged.cdb")
        _write_ncdb(_make_db_with_scope("module_A", 3, "test_a"), pa)
        _write_ncdb(_make_db_with_scope("module_B", 4, "test_b"), pb)
        NcdbMerger().merge([pa, pb], pm)
        merged_db = NcdbReader().read(pm)

        def _count_all(db):
            total = 0
            def _walk(scope):
                nonlocal total
                total += sum(1 for _ in scope.coverItems(CoverTypeT.ALL))
                for child in scope.scopes(ScopeTypeT.ALL):
                    _walk(child)
            for top in db.scopes(ScopeTypeT.ALL):
                _walk(top)
            return total

        # module_A has 3 bins, module_B has 4 bins; union must have at least 7
        assert _count_all(merged_db) >= 7


# ── Idempotency: merge of single source ──────────────────────────────────

def test_single_source_merge_is_identity():
    """Merging a single NCDB into itself should preserve counts exactly."""
    counts = [5, 0, 3, 7, 1]
    with tempfile.TemporaryDirectory() as d:
        pa = os.path.join(d, "a.cdb")
        pm = os.path.join(d, "merged.cdb")
        _write_ncdb(_make_simple_db(counts, "only"), pa)
        NcdbMerger().merge([pa], pm)
        merged_db = NcdbReader().read(pm)
        assert _collect_counts(merged_db) == counts


# ── merged.cdb round-trip via NCDB merge ─────────────────────────────────

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MERGED_CDB = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "merged.cdb"))

needs_merged_cdb = pytest.mark.skipif(
    not os.path.exists(MERGED_CDB),
    reason="merged.cdb not present in tests/",
)


@needs_merged_cdb
def test_merge_merged_cdb_same_schema():
    """Merging merged.cdb with itself should double all counts."""
    from ucis.sqlite.sqlite_ucis import SqliteUCIS

    sqlite_db = SqliteUCIS(MERGED_CDB)
    with tempfile.TemporaryDirectory() as d:
        p1 = os.path.join(d, "copy1.cdb")
        p2 = os.path.join(d, "copy2.cdb")
        pm = os.path.join(d, "double.cdb")
        NcdbWriter().write(sqlite_db, p1)
        NcdbWriter().write(sqlite_db, p2)
        NcdbMerger().merge([p1, p2], pm)

        merged = NcdbReader().read(pm)
        orig_counts = _collect_counts(NcdbReader().read(p1))
        merged_counts = _collect_counts(merged)

        assert len(orig_counts) == len(merged_counts)
        for o, m in zip(orig_counts, merged_counts):
            assert m == o * 2, f"Expected {o*2}, got {m}"
    sqlite_db.close()
