#!/usr/bin/env python3
"""
Issue 3 — `SqliteMerger` rejects non-SQLite source databases.

`SqliteUCIS.merge(source)` delegates to `SqliteMerger`, which accesses
`scope.scope_id` on the source.  When the source is a `MemUCIS`, its
scopes are `MemScope` objects that lack `scope_id`, causing:

    AttributeError: 'MemScope' object has no attribute 'scope_id'

This prevents merging XML/YAML-loaded (in-memory) databases into SQLite.

Reproduce:
    python test_issue_reproduce.py

Expected:  SqliteUCIS.merge(mem_db) merges coverage data successfully.
Actual:    AttributeError is raised.
"""

import os
import sys
import tempfile
import traceback


def create_sample_mem_db():
    """Return a small MemUCIS with one covergroup/coverpoint/bin."""
    from ucis.mem.mem_ucis import MemUCIS
    from ucis.source_info import SourceInfo
    from ucis.source_t import SourceT
    from ucis.scope_type_t import ScopeTypeT
    from ucis.cover_data import CoverData
    from ucis.cover_type_t import CoverTypeT
    from ucis.flags_t import FlagsT

    db = MemUCIS()
    fh = db.createFileHandle("test.sv", os.getcwd())
    si = SourceInfo(fh, 1, 0)
    du = db.createScope("tb", si, 1, SourceT.NONE, ScopeTypeT.DU_MODULE, FlagsT(0))
    inst = db.createInstance("tb", si, 1, SourceT.NONE,
                            ScopeTypeT.INSTANCE, du, FlagsT(0))
    cg = inst.createCovergroup("cg", si, 1, SourceT.NONE)
    cp = cg.createScope("cp", si, 1, SourceT.NONE, ScopeTypeT.COVERPOINT, FlagsT(0))
    cd = CoverData(CoverTypeT.CVGBIN, 0)
    cd.data = 10
    cp.createNextCover("bin0", cd, si)
    return db


def test_sqlite_merge_from_mem():
    """SqliteUCIS.merge(MemUCIS) should succeed."""
    from ucis.sqlite.sqlite_ucis import SqliteUCIS

    src = create_sample_mem_db()

    with tempfile.NamedTemporaryFile(suffix=".ucisdb", delete=False) as f:
        dst_path = f.name

    try:
        dst = SqliteUCIS(dst_path)
        dst.merge(src)
        dst.close()
        print("PASS — SqliteUCIS.merge(MemUCIS) succeeded")
        return True
    except AttributeError as exc:
        if "scope_id" in str(exc):
            print("FAIL — Issue 3 reproduced:")
            traceback.print_exc()
            return False
        raise
    except Exception as exc:
        if "scope_id" in str(exc):
            print("FAIL — Issue 3 reproduced:")
            traceback.print_exc()
            return False
        raise
    finally:
        if os.path.exists(dst_path):
            os.remove(dst_path)


if __name__ == "__main__":
    ok = test_sqlite_merge_from_mem()
    sys.exit(0 if ok else 1)
