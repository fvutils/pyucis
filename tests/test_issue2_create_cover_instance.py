#!/usr/bin/env python3
"""
Issue 2 — `createCoverInstance` not implemented on SQLite covergroup.

The generic `DbMerger` calls `dst_cg.createCoverInstance(...)` when merging
covergroup data into the destination database.  The `SqliteCovergroup` class
does not override the base-class stub, which raises:

    NotImplementedError

This prevents `pyucis convert` and `pyucis merge` from writing to SQLite
via the standard merger pipeline.

Reproduce:
    python tests/test_issue2_create_cover_instance.py

Expected:  Merge into a SqliteUCIS succeeds via DbMerger.
Actual:    NotImplementedError is raised during merge.
"""

import os
import sys
import tempfile
import traceback


def create_sample_mem_db():
    """Return a MemUCIS via XML roundtrip so it has cover-instance structure."""
    from ucis.mem.mem_ucis import MemUCIS
    from ucis.source_info import SourceInfo
    from ucis.source_t import SourceT
    from ucis.scope_type_t import ScopeTypeT
    from ucis.cover_data import CoverData
    from ucis.cover_type_t import CoverTypeT
    from ucis.flags_t import FlagsT
    from ucis.xml.xml_factory import XmlFactory

    db = MemUCIS()
    fh = db.createFileHandle("test.sv", os.getcwd())
    si = SourceInfo(fh, 1, 0)
    du = db.createScope("tb", si, 1, SourceT.NONE, ScopeTypeT.DU_MODULE, FlagsT(0))
    inst = db.createInstance("tb", si, 1, SourceT.NONE,
                            ScopeTypeT.INSTANCE, du, FlagsT(0))
    cg = inst.createCovergroup("cg", si, 1, SourceT.NONE)
    cp = cg.createScope("cp", si, 1, SourceT.NONE, ScopeTypeT.COVERPOINT, FlagsT(0))
    cd = CoverData(CoverTypeT.CVGBIN, 0)
    cd.data = 42
    cd.goal = 1
    cp.createNextCover("bin0", cd, si)

    # Roundtrip through XML so the reader creates COVERINSTANCE scopes,
    # which is the structure DbMerger expects.
    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
        xml_path = f.name
    XmlFactory.write(db, xml_path)
    roundtripped = XmlFactory.read(xml_path)
    os.remove(xml_path)
    return roundtripped

def test_dbmerger_into_sqlite():
    """DbMerger.merge(SqliteUCIS, [MemUCIS]) should work."""
    from ucis.sqlite.sqlite_ucis import SqliteUCIS
    from ucis.merge.db_merger import DbMerger

    src = create_sample_mem_db()

    with tempfile.NamedTemporaryFile(suffix=".ucisdb", delete=False) as f:
        dst_path = f.name

    try:
        dst = SqliteUCIS(dst_path)
        merger = DbMerger()
        merger.merge(dst, [src])
        dst.close()
        print("PASS — DbMerger into SqliteUCIS succeeded")
        return True
    except NotImplementedError:
        print("FAIL — Issue 2 reproduced:")
        traceback.print_exc()
        return False
    finally:
        if os.path.exists(dst_path):
            os.remove(dst_path)


if __name__ == "__main__":
    ok = test_dbmerger_into_sqlite()
    sys.exit(0 if ok else 1)
