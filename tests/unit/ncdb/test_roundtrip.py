"""
Round-trip test: SQLite merged.cdb → NCDB → compare.

Loads the existing merged.cdb SQLite database, writes it as NCDB,
reads it back, and validates that scope tree structure, coveritem
counts, and history are preserved.
"""

import os
import tempfile
import pytest

from ucis.ncdb.ncdb_writer import NcdbWriter
from ucis.ncdb.ncdb_reader import NcdbReader
from ucis.ncdb.format_detect import detect_cdb_format
from ucis.cover_type_t import CoverTypeT
from ucis.scope_type_t import ScopeTypeT
from ucis.history_node_kind import HistoryNodeKind

# Path to repo's merged.cdb SQLite file
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MERGED_CDB = os.path.join(_REPO_ROOT, "merged.cdb")

needs_merged_cdb = pytest.mark.skipif(
    not os.path.exists(MERGED_CDB),
    reason="merged.cdb not present in tests/",
)


def _load_sqlite(path):
    """Load the SQLite CDB via the SqliteUCIS backend."""
    from ucis.sqlite.sqlite_ucis import SqliteUCIS
    return SqliteUCIS(path)


def _collect_coveritems(db):
    """DFS collect all (scope_path, cover_name, count) tuples (ordered)."""
    results = []

    def _walk(scope, path):
        for ci in scope.coverItems(CoverTypeT.ALL):
            count = ci.getCoverData().data
            results.append((path, ci.getName(), count))
        for child in scope.scopes(ScopeTypeT.ALL):
            _walk(child, path + "/" + child.getScopeName())

    for top in db.scopes(ScopeTypeT.ALL):
        _walk(top, top.getScopeName())

    return results


@needs_merged_cdb
def test_format_detect_merged_cdb():
    assert detect_cdb_format(MERGED_CDB) == "sqlite"


@needs_merged_cdb
def test_round_trip_counts():
    """Hit counts must be identical after SQLite → NCDB → read back."""
    sqlite_db = _load_sqlite(MERGED_CDB)
    orig_items = _collect_coveritems(sqlite_db)

    with tempfile.NamedTemporaryFile(suffix=".cdb", delete=False) as tf:
        out_path = tf.name

    try:
        NcdbWriter().write(sqlite_db, out_path)
        assert detect_cdb_format(out_path) == "ncdb"

        ncdb_db = NcdbReader().read(out_path)
        rt_items = _collect_coveritems(ncdb_db)

        assert len(orig_items) == len(rt_items), (
            f"Item count mismatch: {len(orig_items)} → {len(rt_items)}")

        for i, ((op, on, oc), (rp, rn, rc)) in enumerate(zip(orig_items, rt_items)):
            assert op == rp, f"Path mismatch at index {i}: {op!r} vs {rp!r}"
            assert on == rn, f"Name mismatch at index {i}: {on!r} vs {rn!r}"
            assert oc == rc, (
                f"Count mismatch at index {i} ({op}/{on}): "
                f"expected {oc}, got {rc}")
    finally:
        os.unlink(out_path)
        sqlite_db.close()


@needs_merged_cdb
def test_round_trip_scope_structure():
    """Top-level scope names and types must be preserved."""
    sqlite_db = _load_sqlite(MERGED_CDB)
    orig_scopes = [(s.getScopeName(), s.getScopeType())
                   for s in sqlite_db.scopes(ScopeTypeT.ALL)]

    with tempfile.NamedTemporaryFile(suffix=".cdb", delete=False) as tf:
        out_path = tf.name
    try:
        NcdbWriter().write(sqlite_db, out_path)
        ncdb_db = NcdbReader().read(out_path)
        rt_scopes = [(s.getScopeName(), s.getScopeType())
                     for s in ncdb_db.scopes(ScopeTypeT.ALL)]
        assert orig_scopes == rt_scopes
    finally:
        os.unlink(out_path)
        sqlite_db.close()


@needs_merged_cdb
def test_round_trip_history():
    """History node logical names must be preserved."""
    sqlite_db = _load_sqlite(MERGED_CDB)
    orig_names = sorted(
        n.getLogicalName()
        for n in sqlite_db.historyNodes(HistoryNodeKind.TEST)
    )

    with tempfile.NamedTemporaryFile(suffix=".cdb", delete=False) as tf:
        out_path = tf.name
    try:
        NcdbWriter().write(sqlite_db, out_path)
        ncdb_db = NcdbReader().read(out_path)
        rt_names = sorted(
            n.getLogicalName()
            for n in ncdb_db.historyNodes(HistoryNodeKind.TEST)
        )
        assert orig_names == rt_names
    finally:
        os.unlink(out_path)
        sqlite_db.close()


@needs_merged_cdb
def test_ncdb_smaller_than_sqlite():
    """NCDB file should be substantially smaller than the SQLite original."""
    sqlite_size = os.path.getsize(MERGED_CDB)
    sqlite_db = _load_sqlite(MERGED_CDB)
    with tempfile.NamedTemporaryFile(suffix=".cdb", delete=False) as tf:
        out_path = tf.name
    try:
        NcdbWriter().write(sqlite_db, out_path)
        ncdb_size = os.path.getsize(out_path)
        # Expect at least 10× size reduction (design doc claims 73×)
        assert ncdb_size < sqlite_size / 10, (
            f"NCDB ({ncdb_size} B) not much smaller than SQLite ({sqlite_size} B)")
    finally:
        os.unlink(out_path)
        sqlite_db.close()


def _make_db_with_attrs_and_tags():
    """Build a MemUCIS with attributes and tags on some scopes."""
    from ucis.mem.mem_ucis import MemUCIS
    from ucis.source_t import SourceT
    from ucis.cover_data import CoverData
    from ucis.history_node_kind import HistoryNodeKind
    db = MemUCIS()
    db.createHistoryNode(None, "attrs_test", None, HistoryNodeKind.TEST)
    block = db.createScope("top", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    block.setAttribute("author", "tester")
    block.setAttribute("reviewed", "yes")
    block.addTag("important")
    block.addTag("regression")
    cd = CoverData(CoverTypeT.STMTBIN, 0)
    cd.data = 5
    block.createNextCover("stmt_0", cd, None)
    child = block.createScope("inner", None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    child.setAttribute("notes", "inner block")
    child.addTag("skip")
    return db


def test_attrs_round_trip():
    """User-defined attributes must be preserved across write/read."""
    db = _make_db_with_attrs_and_tags()
    with tempfile.NamedTemporaryFile(suffix=".cdb", delete=False) as tf:
        out_path = tf.name
    try:
        NcdbWriter().write(db, out_path)
        rt_db = NcdbReader().read(out_path)
        top = list(rt_db.scopes(ScopeTypeT.BLOCK))[0]
        assert top.getAttribute("author") == "tester"
        assert top.getAttribute("reviewed") == "yes"
        children = list(top.scopes(ScopeTypeT.BLOCK))
        inner = children[0]
        assert inner.getAttribute("notes") == "inner block"
    finally:
        os.unlink(out_path)


def test_tags_round_trip():
    """Scope tags must be preserved across write/read."""
    db = _make_db_with_attrs_and_tags()
    with tempfile.NamedTemporaryFile(suffix=".cdb", delete=False) as tf:
        out_path = tf.name
    try:
        NcdbWriter().write(db, out_path)
        rt_db = NcdbReader().read(out_path)
        top = list(rt_db.scopes(ScopeTypeT.BLOCK))[0]
        tags = set(top.getTags())
        assert "important" in tags
        assert "regression" in tags
        inner = list(top.scopes(ScopeTypeT.BLOCK))[0]
        assert "skip" in set(inner.getTags())
    finally:
        os.unlink(out_path)


@needs_merged_cdb
def test_ncdb_ucis_lazy_loading():
    """NcdbUCIS loads history without parsing scope tree, then loads scopes lazily."""
    import tempfile, os
    from ucis.db_format_rgy import DbFormatRgy
    from ucis.ncdb.ncdb_ucis import NcdbUCIS

    sqlite_db = _load_sqlite(MERGED_CDB)
    with tempfile.NamedTemporaryFile(suffix=".cdb", delete=False) as tf:
        out_path = tf.name
    try:
        NcdbWriter().write(sqlite_db, out_path)
        sqlite_db.close()

        lazy_db = NcdbUCIS(out_path)
        assert not lazy_db._loaded_scopes, "Scopes should not be loaded yet"

        # Read history without triggering scope load
        hn_names = [hn.getLogicalName()
                    for hn in lazy_db.historyNodes(HistoryNodeKind.TEST)]
        assert len(hn_names) > 0
        assert not lazy_db._loaded_scopes, "Scopes should still not be loaded"

        # Accessing scopes triggers scope load
        scope_list = list(lazy_db.scopes(ScopeTypeT.ALL))
        assert len(scope_list) > 0
        assert lazy_db._loaded_scopes

        # Coveritem count should match original
        rt_items = _collect_coveritems(lazy_db)
        assert len(rt_items) == 131923  # known count from merged.cdb
    finally:
        os.unlink(out_path)


# ─── Regression tests: FSM scope duplication and BRANCHBIN type ───────────

@needs_merged_cdb
def test_fsm_scope_counts_not_doubled():
    """MemFSMScope must not duplicate FSM_STATES/FSM_TRANS on NCDB round-trip.

    Regression for bug where createScope(FSM_STATES) on MemFSMScope created a
    second FSM_STATES child instead of returning the pre-existing one, doubling
    FSM_STATES and FSM_TRANS counts (16 → 32).
    """
    import shutil
    import tempfile
    from ucis.db_format_rgy import DbFormatRgy
    from ucis.ncdb.ncdb_writer import NcdbWriter
    from ucis.ncdb.ncdb_reader import NcdbReader

    def _count_type(db, scope_type):
        n = [0]
        def _walk(scope):
            for child in scope.scopes(ScopeTypeT.ALL):
                if child.getScopeType() == scope_type:
                    n[0] += 1
                _walk(child)
        for s in db.scopes(ScopeTypeT.ALL):
            if s.getScopeType() == scope_type:
                n[0] += 1
            _walk(s)
        return n[0]

    rgy = DbFormatRgy.inst()
    with tempfile.TemporaryDirectory() as d:
        src_copy = os.path.join(d, "src.cdb")
        out_path  = os.path.join(d, "out.cdb")
        shutil.copy2(MERGED_CDB, src_copy)
        src_db = rgy.getFormatIf('sqlite').read(src_copy)
        orig_states = _count_type(src_db, ScopeTypeT.FSM_STATES)
        orig_trans  = _count_type(src_db, ScopeTypeT.FSM_TRANS)
        orig_fsm    = _count_type(src_db, ScopeTypeT.FSM)
        NcdbWriter().write(src_db, out_path)
        rt = NcdbReader().read(out_path)
        assert _count_type(rt, ScopeTypeT.FSM)        == orig_fsm,    "FSM count mismatch"
        assert _count_type(rt, ScopeTypeT.FSM_STATES) == orig_states, "FSM_STATES doubled"
        assert _count_type(rt, ScopeTypeT.FSM_TRANS)  == orig_trans,  "FSM_TRANS doubled"


@needs_merged_cdb
def test_branchbin_not_mistyped_as_togglebin():
    """Non-toggle BRANCH scopes must keep BRANCHBIN type through NCDB round-trip.

    Regression for bug where SCOPE_TO_COVER_TYPE mapped BRANCH→TOGGLEBIN,
    causing BRANCHBIN cover items to be serialised and read back as TOGGLEBIN.
    """
    import shutil
    import tempfile
    from ucis.db_format_rgy import DbFormatRgy
    from ucis.ncdb.ncdb_writer import NcdbWriter
    from ucis.ncdb.ncdb_reader import NcdbReader
    from ucis.cover_type_t import CoverTypeT

    def _count_cover(db, cover_type):
        n = [0]
        def _walk(scope):
            for _ci in scope.coverItems(cover_type):
                n[0] += 1
            for child in scope.scopes(ScopeTypeT.ALL):
                _walk(child)
        for s in db.scopes(ScopeTypeT.ALL):
            _walk(s)
        return n[0]

    rgy = DbFormatRgy.inst()
    with tempfile.TemporaryDirectory() as d:
        src_copy = os.path.join(d, "src.cdb")
        out_path  = os.path.join(d, "out.cdb")
        shutil.copy2(MERGED_CDB, src_copy)
        src_db = rgy.getFormatIf('sqlite').read(src_copy)
        orig_branch = _count_cover(src_db, CoverTypeT.BRANCHBIN)
        assert orig_branch > 0, "merged.cdb should have BRANCHBIN items"
        NcdbWriter().write(src_db, out_path)
        rt = NcdbReader().read(out_path)
        assert _count_cover(rt, CoverTypeT.BRANCHBIN) == orig_branch, \
            "BRANCHBIN items were lost or mistyped as TOGGLEBIN"
