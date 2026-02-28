"""
Tests for ucis.ncdb.fsm — FSM scope metadata round-trip via NCDB ZIP.
"""

import json
import os
import tempfile
import zipfile

import pytest

from ucis.cover_data import CoverData
from ucis.cover_type_t import CoverTypeT
from ucis.history_node_kind import HistoryNodeKind
from ucis.mem.mem_fsm_scope import MemFSMScope
from ucis.mem.mem_ucis import MemUCIS
from ucis.ncdb.constants import MEMBER_FSM
from ucis.ncdb.fsm import FsmReader, FsmWriter
from ucis.ncdb.ncdb_reader import NcdbReader
from ucis.ncdb.ncdb_writer import NcdbWriter
from ucis.scope_type_t import ScopeTypeT
from ucis.source_t import SourceT


# ── Helpers ───────────────────────────────────────────────────────────────

def _make_fsm_db(state_data=None, transition_data=None):
    """
    Build a MemUCIS with one FSM scope.

    *state_data* is a list of (name, index, visit_count) triples.
    *transition_data* is a list of (from_name, to_name, count) triples.
    If None, defaults to IDLE(0,1) / RUN(1,2) with IDLE->RUN(1).
    """
    if state_data is None:
        state_data = [("IDLE", 0, 1), ("RUN", 1, 2)]
    if transition_data is None:
        transition_data = [("IDLE", "RUN", 1), ("RUN", "IDLE", 0)]

    db = MemUCIS()
    db.createHistoryNode(None, "t", None, HistoryNodeKind.TEST)
    du   = db.createScope("mod", None, 1, SourceT.SV, ScopeTypeT.DU_MODULE, 0)
    inst = db.createInstance("mod", None, 1, SourceT.SV, ScopeTypeT.INSTANCE, du, 0)

    fsm = MemFSMScope(inst, "fsm1", None, 1, SourceT.SV)
    inst.m_children.append(fsm)
    fsm.m_parent = inst

    states = {}
    for (name, idx, cnt) in state_data:
        s = fsm.createState(name, idx)
        s.visit_count = cnt
        # Update the matching cover item count
        for ci in fsm._states_scope.coverItems(CoverTypeT.ALL):
            if ci.getName() == name:
                ci.getCoverData().data = cnt
        states[name] = s

    for (from_name, to_name, cnt) in transition_data:
        t = fsm.createTransition(states[from_name], states[to_name])
        t.count = cnt
        for ci in fsm._trans_scope.coverItems(CoverTypeT.ALL):
            if ci.getName() == f"{from_name}->{to_name}":
                ci.getCoverData().data = cnt

    return db, fsm


def _write_read(db):
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "out.cdb")
        NcdbWriter().write(db, path)
        return NcdbReader().read(path), path


def _first_fsm(db):
    """Find the first FSM scope in DFS order."""
    def _walk(scope):
        if scope.getScopeType() == ScopeTypeT.FSM:
            return scope
        for child in scope.scopes(ScopeTypeT.ALL):
            result = _walk(child)
            if result:
                return result
        return None
    for s in db.scopes(ScopeTypeT.ALL):
        result = _walk(s)
        if result:
            return result
    return None


# ── Unit tests: FsmWriter ─────────────────────────────────────────────────

def test_fsm_writer_empty_when_sequential_indices():
    """Sequential 0,1,2,… state indices → empty bytes (no fsm.json needed)."""
    db, _ = _make_fsm_db()
    data = FsmWriter().serialize(db)
    assert data == b""


def test_fsm_writer_stores_nonsequential_index():
    """Non-sequential state index is captured in fsm.json."""
    db, _ = _make_fsm_db(
        state_data=[("IDLE", 0, 0), ("RUN", 5, 0)],  # index 5 != sequential 1
        transition_data=[("IDLE", "RUN", 0)],
    )
    data = FsmWriter().serialize(db)
    assert data != b""
    payload = json.loads(data)
    assert payload["version"] == 1
    entry = payload["entries"][0]
    names_to_idx = {s["name"]: s["index"] for s in entry["states"]}
    assert names_to_idx["RUN"] == 5
    assert "IDLE" not in names_to_idx  # IDLE index 0 == sequential → omitted


def test_fsm_reader_empty_data():
    """Empty bytes must not raise; still rebuilds dicts from cover items."""
    db, _ = _make_fsm_db()
    rdb, _ = _write_read(db)
    fsm = _first_fsm(rdb)
    assert fsm is not None
    # Dicts must be rebuilt even with empty fsm.json
    FsmReader().apply(rdb, b"")


# ── Integration: NCDB round-trip ─────────────────────────────────────────

def test_fsm_states_dict_rebuilt():
    """_states dict must be populated after NCDB round-trip."""
    db, _ = _make_fsm_db()
    rdb, _ = _write_read(db)
    fsm = _first_fsm(rdb)
    assert fsm is not None
    assert fsm.getNumStates() == 2
    assert "IDLE" in fsm._states
    assert "RUN" in fsm._states


def test_fsm_transitions_dict_rebuilt():
    """_transitions dict must be populated after NCDB round-trip."""
    db, _ = _make_fsm_db()
    rdb, _ = _write_read(db)
    fsm = _first_fsm(rdb)
    assert fsm.getNumTransitions() == 2
    assert ("IDLE", "RUN") in fsm._transitions
    assert ("RUN", "IDLE") in fsm._transitions


def test_fsm_state_visit_counts():
    """State visit counts survive NCDB round-trip."""
    db, _ = _make_fsm_db(
        state_data=[("IDLE", 0, 7), ("RUN", 1, 3)],
        transition_data=[("IDLE", "RUN", 4), ("RUN", "IDLE", 0)],
    )
    rdb, _ = _write_read(db)
    fsm = _first_fsm(rdb)
    assert fsm._states["IDLE"].visit_count == 7
    assert fsm._states["RUN"].visit_count == 3


def test_fsm_transition_counts():
    """Transition counts survive NCDB round-trip."""
    db, _ = _make_fsm_db(
        state_data=[("IDLE", 0, 0), ("RUN", 1, 0)],
        transition_data=[("IDLE", "RUN", 11), ("RUN", "IDLE", 5)],
    )
    rdb, _ = _write_read(db)
    fsm = _first_fsm(rdb)
    assert fsm._transitions[("IDLE", "RUN")].count == 11
    assert fsm._transitions[("RUN", "IDLE")].count == 5


def test_fsm_state_index_round_trip():
    """Non-sequential state index survives round-trip via fsm.json."""
    db, _ = _make_fsm_db(
        state_data=[("IDLE", 0, 0), ("RUN", 100, 0)],
        transition_data=[("IDLE", "RUN", 0)],
    )
    rdb, _ = _write_read(db)
    fsm = _first_fsm(rdb)
    assert fsm._states["RUN"].getIndex() == 100


def test_fsm_absent_from_zip_when_sequential():
    """Sequential indices → fsm.json must be absent from ZIP."""
    db, _ = _make_fsm_db()
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "out.cdb")
        NcdbWriter().write(db, path)
        with zipfile.ZipFile(path) as zf:
            assert MEMBER_FSM not in zf.namelist()


def test_fsm_present_in_zip_when_nonsequential():
    """Non-sequential index → fsm.json must appear in ZIP."""
    db, _ = _make_fsm_db(
        state_data=[("IDLE", 0, 0), ("RUN", 99, 0)],
        transition_data=[("IDLE", "RUN", 0)],
    )
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "out.cdb")
        NcdbWriter().write(db, path)
        with zipfile.ZipFile(path) as zf:
            assert MEMBER_FSM in zf.namelist()


def test_fsm_multiple_scopes():
    """Multiple FSM scopes in same DB each have dicts rebuilt."""
    db = MemUCIS()
    db.createHistoryNode(None, "t", None, HistoryNodeKind.TEST)

    for fname in ("fsm_a", "fsm_b", "fsm_c"):
        du   = db.createScope(fname, None, 1, SourceT.SV, ScopeTypeT.DU_MODULE, 0)
        inst = db.createInstance(fname, None, 1, SourceT.SV,
                                 ScopeTypeT.INSTANCE, du, 0)
        fsm = MemFSMScope(inst, fname, None, 1, SourceT.SV)
        inst.m_children.append(fsm)
        fsm.m_parent = inst
        s0 = fsm.createState("S0", 0)
        s1 = fsm.createState("S1", 1)
        fsm.createTransition(s0, s1)

    rdb, _ = _write_read(db)
    count = 0
    def _walk(scope):
        nonlocal count
        if scope.getScopeType() == ScopeTypeT.FSM:
            count += 1
            assert scope.getNumStates() == 2
            assert scope.getNumTransitions() == 1
        for child in scope.scopes(ScopeTypeT.ALL):
            _walk(child)
    for s in rdb.scopes(ScopeTypeT.ALL):
        _walk(s)
    assert count == 3


# ── Regression: merged.cdb FSM round-trip ────────────────────────────────

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MERGED_CDB = os.path.join(os.path.dirname(__file__), "..", "..", "merged.cdb")

needs_merged_cdb = pytest.mark.skipif(
    not os.path.exists(MERGED_CDB),
    reason="merged.cdb not present in tests/",
)


@needs_merged_cdb
def test_fsm_merged_cdb_states_transitions_intact():
    """FSM scopes from merged.cdb have correct state and transition counts."""
    import shutil
    from ucis.sqlite.sqlite_ucis import SqliteUCIS

    with tempfile.TemporaryDirectory() as d:
        cdb_copy = os.path.join(d, "merged_copy.cdb")
        shutil.copy2(MERGED_CDB, cdb_copy)
        sqlite_db = SqliteUCIS(cdb_copy)

        # Count total FSM states and transitions in SQLite
        sqlite_states = 0
        sqlite_trans  = 0

        def _count_sqlite(scope):
            nonlocal sqlite_states, sqlite_trans
            if scope.getScopeType() == ScopeTypeT.FSM:
                for child in scope.scopes(ScopeTypeT.ALL):
                    ct = child.getScopeType()
                    items = list(child.coverItems(CoverTypeT.ALL))
                    if ct == ScopeTypeT.FSM_STATES:
                        sqlite_states += len(items)
                    elif ct == ScopeTypeT.FSM_TRANS:
                        sqlite_trans += len(items)
                return
            for c in scope.scopes(ScopeTypeT.ALL):
                _count_sqlite(c)

        for s in sqlite_db.scopes(ScopeTypeT.ALL):
            _count_sqlite(s)
        sqlite_db.close()

        # Convert to NCDB and read back
        ncdb_path = os.path.join(d, "out.cdb")
        from ucis.sqlite.sqlite_ucis import SqliteUCIS as _SU
        sqlite_db2 = _SU(cdb_copy)
        NcdbWriter().write(sqlite_db2, ncdb_path)
        sqlite_db2.close()
        ncdb_db = NcdbReader().read(ncdb_path)

        ncdb_states = 0
        ncdb_trans  = 0

        def _count_ncdb(scope):
            nonlocal ncdb_states, ncdb_trans
            if scope.getScopeType() == ScopeTypeT.FSM:
                ncdb_states += scope.getNumStates()
                ncdb_trans  += scope.getNumTransitions()
                return
            for c in scope.scopes(ScopeTypeT.ALL):
                _count_ncdb(c)

        for s in ncdb_db.scopes(ScopeTypeT.ALL):
            _count_ncdb(s)

        assert ncdb_states == sqlite_states, (
            f"state count mismatch: ncdb={ncdb_states} sqlite={sqlite_states}")
        assert ncdb_trans == sqlite_trans, (
            f"transition count mismatch: ncdb={ncdb_trans} sqlite={sqlite_trans}")
