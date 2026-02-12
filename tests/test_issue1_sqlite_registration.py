#!/usr/bin/env python3
"""
Issue 1 — SQLite format registered as instance instead of class.

The `DbFormatIfSqlite.register()` method passes `cls()` (an instance) to
`FormatDescDb(fmt_if=...)`.  Downstream code calls `desc.fmt_if()` expecting
a class (callable), which fails with:

    TypeError: 'DbFormatIfSqlite' object is not callable

Reproduce:
    python tests/test_issue1_sqlite_registration.py

Expected:  fmt_if() returns a DbFormatIfSqlite instance without error.
Actual:    TypeError is raised.
"""

import sys
import traceback


def test_sqlite_format_callable():
    from ucis.rgy.format_rgy import FormatRgy

    rgy = FormatRgy.inst()
    assert rgy.hasDatabaseFormat("sqlite"), "sqlite format not registered"

    desc = rgy.getDatabaseDesc("sqlite")

    # This is exactly what cmd_convert.py and cmd_merge.py do:
    try:
        fmt_if = desc.fmt_if()
    except TypeError as exc:
        print("FAIL — Issue 1 reproduced:")
        traceback.print_exc()
        return False

    print(f"PASS — fmt_if() returned {type(fmt_if).__name__}")
    return True


def test_cli_convert_sqlite_output(tmp_path="/tmp"):
    """End-to-end: Verify format interface instantiation works like in cmd_convert.py"""
    import os
    import tempfile
    from ucis.mem.mem_ucis import MemUCIS
    from ucis.source_info import SourceInfo
    from ucis.source_t import SourceT
    from ucis.scope_type_t import ScopeTypeT
    from ucis.cover_data import CoverData
    from ucis.cover_type_t import CoverTypeT
    from ucis.flags_t import FlagsT
    from ucis.xml.xml_factory import XmlFactory
    from ucis.rgy.format_rgy import FormatRgy

    db = MemUCIS()
    fh = db.createFileHandle("test.sv", os.getcwd())
    si = SourceInfo(fh, 1, 0)
    du = db.createScope("tb", si, 1, SourceT.NONE, ScopeTypeT.DU_MODULE, FlagsT(0))
    inst = db.createInstance("tb", si, 1, SourceT.NONE,
                            ScopeTypeT.INSTANCE, du, FlagsT(0))

    xml_path = os.path.join(tmp_path, "issue1_test.xml")
    XmlFactory.write(db, xml_path)

    # This simulates exactly what cmd_convert.py does
    rgy = FormatRgy.inst()
    input_desc = rgy.getDatabaseDesc("xml")
    output_desc = rgy.getDatabaseDesc("sqlite")
    
    # These lines were causing TypeError before the fix
    try:
        input_if = input_desc.fmt_if()
        output_if = output_desc.fmt_if()
    except TypeError as exc:
        print(f"FAIL — fmt_if() calls failed: {exc}")
        traceback.print_exc()
        return False

    # Verify we can read and create databases
    try:
        in_db = input_if.read(xml_path)
        out_db = output_if.create()
        
        # Verify we can access basic data
        assert in_db is not None
        assert out_db is not None
        
        in_db.close()
        out_db.close()
        
        # Clean up
        if os.path.exists(xml_path):
            os.unlink(xml_path)
            
        print("PASS — format interface instantiation works correctly")
        return True
    except Exception as exc:
        print(f"FAIL — Error working with databases: {exc}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    ok = True
    ok = test_sqlite_format_callable() and ok
    ok = test_cli_convert_sqlite_output() and ok
    sys.exit(0 if ok else 1)
