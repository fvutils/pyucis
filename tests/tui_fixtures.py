"""
Shared fixtures and database builders for TUI automated tests.

Every fixture exposes:
  - db        : UCIS database object (API-path or SQLite-path)
  - expected  : dict of known-correct values for assertions
  - model     : CoverageModel wrapping the database

The StubApp bridges BaseView.__init__ without requiring a real TUI.
"""
import os
import pytest
from unittest.mock import MagicMock

from ucis import (
    UCIS_HISTORYNODE_TEST, UCIS_TESTSTATUS_OK, UCIS_OTHER,
    UCIS_DU_MODULE, UCIS_ENABLED_STMT, UCIS_ENABLED_BRANCH,
    UCIS_INST_ONCE, UCIS_SCOPE_UNDER_DU, UCIS_INSTANCE, UCIS_VLOG,
)
from ucis.mem.mem_factory import MemFactory
from ucis.source_info import SourceInfo
from ucis.test_data import TestData
from ucis.tui.models.coverage_model import CoverageModel


# ---------------------------------------------------------------------------
# StubApp – minimal app object required by BaseView
# ---------------------------------------------------------------------------

class StubApp:
    """Minimal app stub for instantiating views without a running TUI."""

    def __init__(self, model: CoverageModel):
        self.coverage_model = model
        self.status_bar = MagicMock()
        self.controller = MagicMock()


# ---------------------------------------------------------------------------
# Low-level database builders
# ---------------------------------------------------------------------------

def _add_test(db, logical_name="test1"):
    """Add a passing test history node to *db*."""
    node = db.createHistoryNode(None, logical_name, logical_name, UCIS_HISTORYNODE_TEST)
    node.setTestData(TestData(
        teststatus=UCIS_TESTSTATUS_OK,
        toolcategory="UCIS:simulator",
        date="20240101000000",
    ))
    return node


def _add_instance(db):
    """Add a minimal DU + instance and return the instance scope."""
    file_h = db.createFileHandle("design.sv", "/rtl")
    du = db.createScope(
        "work.top", SourceInfo(file_h, 1, 0), 1,
        UCIS_OTHER, UCIS_DU_MODULE,
        UCIS_ENABLED_STMT | UCIS_ENABLED_BRANCH | UCIS_INST_ONCE | UCIS_SCOPE_UNDER_DU,
    )
    inst = db.createInstance(
        "tb", None, 1, UCIS_OTHER, UCIS_INSTANCE, du, UCIS_INST_ONCE
    )
    return inst, file_h


def _make_partial_coverage_db(db):
    """
    Build a database with known 50 % functional coverage.

    Structure
    ---------
    tb (instance)
      cg1 (covergroup)
        cp1 (coverpoint)  bins: a(hit), b(hit), c(miss), d(miss) → 2/4 = 50 %
      cg2 (covergroup)
        cp2 (coverpoint)  bins: x(hit), y(miss) → 1/2 = 50 %

    Overall: 3 covered / 6 total = 50 %
    """
    _add_test(db)
    inst, file_h = _add_instance(db)
    src = SourceInfo(file_h, 3, 0)

    cg1 = inst.createCovergroup("cg1", src, 1, UCIS_OTHER)
    cp1 = cg1.createCoverpoint("cp1", src, 1, UCIS_VLOG)
    cp1.createBin("a", src, 1, 5, "a")   # hit  (5 >= 1)
    cp1.createBin("b", src, 1, 3, "b")   # hit  (3 >= 1)
    cp1.createBin("c", src, 1, 0, "c")   # miss
    cp1.createBin("d", src, 1, 0, "d")   # miss

    cg2 = inst.createCovergroup("cg2", src, 1, UCIS_OTHER)
    cp2 = cg2.createCoverpoint("cp2", src, 1, UCIS_VLOG)
    cp2.createBin("x", src, 1, 10, "x")  # hit
    cp2.createBin("y", src, 1, 0,  "y")  # miss

    expected = {
        "total_bins": 6,
        "covered_bins": 3,
        "overall_coverage": 50.0,
        "covergroups": 2,
        "coverpoints": 2,
        "gaps": [
            # (name, coverage_pct)
            ("cp1", 50.0),
            ("cp2", 50.0),
        ],
    }
    return expected


def _make_zero_coverage_db(db):
    """Database where no bins have been hit."""
    _add_test(db)
    inst, file_h = _add_instance(db)
    src = SourceInfo(file_h, 3, 0)

    cg = inst.createCovergroup("cg_zero", src, 1, UCIS_OTHER)
    cp = cg.createCoverpoint("cp_zero", src, 1, UCIS_VLOG)
    cp.createBin("b0", src, 1, 0, "b0")
    cp.createBin("b1", src, 1, 0, "b1")
    cp.createBin("b2", src, 1, 0, "b2")

    expected = {
        "total_bins": 3,
        "covered_bins": 0,
        "overall_coverage": 0.0,
        "covergroups": 1,
        "coverpoints": 1,
    }
    return expected


def _make_full_coverage_db(db):
    """Database where every bin has been hit."""
    _add_test(db)
    inst, file_h = _add_instance(db)
    src = SourceInfo(file_h, 3, 0)

    cg = inst.createCovergroup("cg_full", src, 1, UCIS_OTHER)
    cp = cg.createCoverpoint("cp_full", src, 1, UCIS_VLOG)
    cp.createBin("b0", src, 1, 1, "b0")
    cp.createBin("b1", src, 1, 2, "b1")
    cp.createBin("b2", src, 1, 7, "b2")

    expected = {
        "total_bins": 3,
        "covered_bins": 3,
        "overall_coverage": 100.0,
        "covergroups": 1,
        "coverpoints": 1,
    }
    return expected


def _make_multi_test_db(db):
    """
    Three tests each contributing unique bins.

    tb / cg_mt / cp_mt  bins b0..b5
      test_a hits b0, b1
      test_b hits b2, b3
      test_c hits b4, b5  (not added → miss)

    Overall: 4 covered / 6 total  ≈ 66.7 %
    """
    for name in ("test_a", "test_b", "test_c"):
        _add_test(db, name)
    inst, file_h = _add_instance(db)
    src = SourceInfo(file_h, 3, 0)

    cg = inst.createCovergroup("cg_mt", src, 1, UCIS_OTHER)
    cp = cg.createCoverpoint("cp_mt", src, 1, UCIS_VLOG)
    cp.createBin("b0", src, 1, 1, "b0")
    cp.createBin("b1", src, 1, 1, "b1")
    cp.createBin("b2", src, 1, 1, "b2")
    cp.createBin("b3", src, 1, 1, "b3")
    cp.createBin("b4", src, 1, 0, "b4")
    cp.createBin("b5", src, 1, 0, "b5")

    expected = {
        "total_bins": 6,
        "covered_bins": 4,
        "covergroups": 1,
        "coverpoints": 1,
        "test_names": ["test_a", "test_b", "test_c"],
    }
    return expected


# ---------------------------------------------------------------------------
# CoverageModel factory helpers (API path via XML, SQLite path)
# ---------------------------------------------------------------------------

def _model_from_mem_db(db, tmp_path):
    """Write *db* to XML then load via CoverageModel (exercises API/XML path)."""
    from ucis.xml.xml_factory import XmlFactory
    xml_path = str(tmp_path / "test.xml")
    XmlFactory.write(db, xml_path)
    return CoverageModel(xml_path)


def _model_from_sqlite(builder_fn, tmp_path):
    """Create a fresh SQLiteUCIS, populate it, return CoverageModel (exercises SQLite path)."""
    from ucis.sqlite.sqlite_ucis import SqliteUCIS
    db_path = str(tmp_path / "test.db")
    db = SqliteUCIS(db_path)
    expected = builder_fn(db)
    db.close()
    model = CoverageModel(db_path)
    return model, expected


# ---------------------------------------------------------------------------
# Pytest fixtures
# ---------------------------------------------------------------------------

# Parametrize over (backend_label, builder_fn, extra_info) pairs so the same
# test body exercises both the UCIS-API path (XML) and the SQLite fast path.

PARTIAL_BUILDERS = [
    pytest.param("xml",    _make_partial_coverage_db, id="xml"),
    pytest.param("sqlite", _make_partial_coverage_db, id="sqlite"),
]

ZERO_BUILDERS = [
    pytest.param("xml",    _make_zero_coverage_db, id="xml"),
    pytest.param("sqlite", _make_zero_coverage_db, id="sqlite"),
]

FULL_BUILDERS = [
    pytest.param("xml",    _make_full_coverage_db, id="xml"),
    pytest.param("sqlite", _make_full_coverage_db, id="sqlite"),
]

MULTI_TEST_BUILDERS = [
    pytest.param("xml",    _make_multi_test_db, id="xml"),
    pytest.param("sqlite", _make_multi_test_db, id="sqlite"),
]


def make_model_and_expected(backend: str, builder_fn, tmp_path):
    """Create (CoverageModel, expected_dict) for the given backend and builder."""
    if backend == "sqlite":
        return _model_from_sqlite(builder_fn, tmp_path)
    else:  # xml / mem
        db = MemFactory.create()
        expected = builder_fn(db)
        model = _model_from_mem_db(db, tmp_path)
        return model, expected


@pytest.fixture(params=["xml", "sqlite"])
def partial_coverage(request, tmp_path):
    """(model, expected) for a 50% coverage database."""
    model, expected = make_model_and_expected(
        request.param, _make_partial_coverage_db, tmp_path
    )
    yield model, expected
    model.close()


@pytest.fixture(params=["xml", "sqlite"])
def zero_coverage(request, tmp_path):
    """(model, expected) for a zero-coverage database."""
    model, expected = make_model_and_expected(
        request.param, _make_zero_coverage_db, tmp_path
    )
    yield model, expected
    model.close()


@pytest.fixture(params=["xml", "sqlite"])
def full_coverage(request, tmp_path):
    """(model, expected) for a 100% coverage database."""
    model, expected = make_model_and_expected(
        request.param, _make_full_coverage_db, tmp_path
    )
    yield model, expected
    model.close()


@pytest.fixture(params=["xml", "sqlite"])
def multi_test(request, tmp_path):
    """(model, expected) for a multi-test database."""
    model, expected = make_model_and_expected(
        request.param, _make_multi_test_db, tmp_path
    )
    yield model, expected
    model.close()


# File-based regression fixture (uses the committed test_vlt.cdb SQLite file)
VLT_CDB = os.path.join(os.path.dirname(__file__), "..", "test_vlt.cdb")


@pytest.fixture
def vlt_model():
    """CoverageModel loaded from the committed test_vlt.cdb SQLite fixture."""
    if not os.path.exists(VLT_CDB):
        pytest.skip(f"test_vlt.cdb not found at {VLT_CDB}")
    model = CoverageModel(VLT_CDB)
    yield model
    model.close()
