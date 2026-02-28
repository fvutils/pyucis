"""Tests for design_units.py serialization and round-trip."""

import io
import os
import tempfile
import zipfile

import pytest

from ucis.mem.mem_ucis import MemUCIS
from ucis.scope_type_t import ScopeTypeT

from ucis.ncdb.design_units import DesignUnitsWriter, DesignUnitsReader
from ucis.ncdb.ncdb_writer import NcdbWriter
from ucis.ncdb.ncdb_reader import NcdbReader


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_db_with_dus():
    """Build a MemUCIS with several design units."""
    db = MemUCIS()
    db.createScope("pkg_a",  None, 1, None, ScopeTypeT.DU_PACKAGE,   0)
    db.createScope("mod_b",  None, 1, None, ScopeTypeT.DU_MODULE,    0)
    db.createScope("ifc_c",  None, 1, None, ScopeTypeT.DU_INTERFACE, 0)
    return db


# ── serialize / deserialize ───────────────────────────────────────────────────

def test_serialize_produces_bytes():
    db = _make_db_with_dus()
    data = DesignUnitsWriter().serialize(db)
    assert isinstance(data, bytes)
    assert len(data) > 0


def test_serialize_empty_when_no_dus():
    db = MemUCIS()
    data = DesignUnitsWriter().serialize(db)
    assert data == b""


def test_round_trip_names():
    db = _make_db_with_dus()
    data = DesignUnitsWriter().serialize(db)
    index = DesignUnitsReader().build_index(data, db)
    assert set(index.keys()) == {"pkg_a", "mod_b", "ifc_c"}


def test_round_trip_scope_objects():
    db = _make_db_with_dus()
    data = DesignUnitsWriter().serialize(db)
    index = DesignUnitsReader().build_index(data, db)
    for name, scope in index.items():
        assert scope.getScopeName() == name
        assert ScopeTypeT.DU_ANY(scope.getScopeType())


def test_fallback_when_empty_data():
    """build_index returns a usable index even without serialized data."""
    db = _make_db_with_dus()
    index = DesignUnitsReader().build_index(b"", db)
    assert set(index.keys()) == {"pkg_a", "mod_b", "ifc_c"}


def test_fallback_matches_serialized():
    db = _make_db_with_dus()
    data = DesignUnitsWriter().serialize(db)
    idx_from_data  = DesignUnitsReader().build_index(data, db)
    idx_from_scan  = DesignUnitsReader().build_index(b"",  db)
    assert set(idx_from_data.keys()) == set(idx_from_scan.keys())


# ── full NCDB round-trip ──────────────────────────────────────────────────────

def test_ncdb_round_trip():
    db = _make_db_with_dus()
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".cdb", delete=False) as f:
        path = f.name
    try:
        NcdbWriter().write(db, path)
        db2 = NcdbReader().read(path)
        assert hasattr(db2, "_du_index")
        assert set(db2._du_index.keys()) == {"pkg_a", "mod_b", "ifc_c"}
    finally:
        os.unlink(path)


def test_ncdb_round_trip_du_type():
    db = _make_db_with_dus()
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".cdb", delete=False) as f:
        path = f.name
    try:
        NcdbWriter().write(db, path)
        db2 = NcdbReader().read(path)
        mod = db2._du_index.get("mod_b")
        assert mod is not None
        assert mod.getScopeType() == ScopeTypeT.DU_MODULE
    finally:
        os.unlink(path)


# ── merged.cdb regression ─────────────────────────────────────────────────────

_MERGED_CDB = os.path.join(os.path.dirname(__file__), "..", "..", "merged.cdb")


@pytest.mark.skipif(not os.path.exists(_MERGED_CDB), reason="merged.cdb not found")
def test_merged_cdb_du_index():
    from ucis.sqlite.sqlite_ucis import SqliteUCIS
    sqlite_db = SqliteUCIS(_MERGED_CDB)
    with tempfile.NamedTemporaryFile(suffix=".cdb", delete=False) as f:
        ncdb_path = f.name
    try:
        NcdbWriter().write(sqlite_db, ncdb_path)
        sqlite_db.close()
        db = NcdbReader().read(ncdb_path)
        assert hasattr(db, "_du_index")
        assert len(db._du_index) > 0
    finally:
        os.unlink(ncdb_path)


@pytest.mark.skipif(not os.path.exists(_MERGED_CDB), reason="merged.cdb not found")
def test_merged_cdb_du_are_du_any():
    from ucis.sqlite.sqlite_ucis import SqliteUCIS
    sqlite_db = SqliteUCIS(_MERGED_CDB)
    with tempfile.NamedTemporaryFile(suffix=".cdb", delete=False) as f:
        ncdb_path = f.name
    try:
        NcdbWriter().write(sqlite_db, ncdb_path)
        sqlite_db.close()
        db = NcdbReader().read(ncdb_path)
        for scope in db._du_index.values():
            assert ScopeTypeT.DU_ANY(scope.getScopeType())
    finally:
        os.unlink(ncdb_path)
