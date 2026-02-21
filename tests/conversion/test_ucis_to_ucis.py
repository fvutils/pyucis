"""
Parameterized UCIS-to-UCIS round-trip tests.

Tests that each UCIS feature survives copying from one backend to another
via DbMerger.  Parameterized over:
  - 11 feature builders (FC, CC, SM categories)
  - 4 backend combinations: mem→mem, sqlite→sqlite, sqlite→mem, mem→sqlite

Total: 44 test cases.
"""

import pytest
from pathlib import Path
from typing import Callable

from ucis.mem.mem_ucis import MemUCIS
from ucis.sqlite.sqlite_ucis import SqliteUCIS
from ucis.merge.db_merger import DbMerger
from ucis.scope_type_t import ScopeTypeT

from .builders.ucis_builders import ALL_BUILDERS
from .conftest import make_db


# ---------------------------------------------------------------------------
# Parametrize
# ---------------------------------------------------------------------------

BACKEND_COMBOS = [
    ("mem",    "mem"),
    ("sqlite", "sqlite"),
    ("sqlite", "mem"),
    ("mem",    "sqlite"),
]


def _builder_id(builder_pair):
    build_fn, _ = builder_pair
    return build_fn.__name__.replace("build_", "")


def _combo_id(combo):
    return f"{combo[0]}-{combo[1]}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _count_covergroups(db):
    """Count covergroups in the database (across all instances)."""
    count = 0
    for inst in db.scopes(ScopeTypeT.INSTANCE):
        count += sum(1 for _ in inst.scopes(ScopeTypeT.COVERGROUP))
    return count


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("builder_pair", ALL_BUILDERS, ids=_builder_id)
@pytest.mark.parametrize("src_back,dst_back", BACKEND_COMBOS, ids=_combo_id)
def test_ucis_roundtrip(builder_pair, src_back, dst_back, tmp_path):
    """Build a UCIS DB in src_back, merge into dst_back, verify content."""
    build_fn, verify_fn = builder_pair

    src_db = make_db(src_back, tmp_path / "src.db")
    build_fn(src_db)

    dst_db = make_db(dst_back, tmp_path / "dst.db")
    merger = DbMerger()
    merger.merge(dst_db, [src_db])

    verify_fn(dst_db)

    src_db.close()
    dst_db.close()
