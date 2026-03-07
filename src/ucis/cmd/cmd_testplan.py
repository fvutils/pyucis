"""``pyucis testplan`` CLI subcommands.

Subcommands
-----------
import      Import an Hjson/JSON testplan and embed it in a .cdb file.
closure     Compute testpoint closure and display a report.
export-junit  Export closure results as JUnit XML.
"""

from __future__ import annotations

import json
import sys


def _open_ncdb(path: str):
    from ucis.ncdb.ncdb_ucis import NcdbUCIS
    return NcdbUCIS(path)


# ---------------------------------------------------------------------------
# testplan import
# ---------------------------------------------------------------------------

def cmd_testplan_import(args) -> None:
    """Execute ``pyucis testplan import``."""
    from ucis.ncdb.testplan_hjson import import_hjson
    from ucis.ncdb.ncdb_writer import NcdbWriter
    import os, tempfile

    # Parse substitutions: "key=val" pairs
    subs: dict = {}
    for s in getattr(args, "subs", []) or []:
        if "=" in s:
            k, _, v = s.partition("=")
            existing = subs.get(k)
            if existing is None:
                subs[k] = [v]
            else:
                existing.append(v)

    plan = import_hjson(args.hjson_path, substitutions=subs if subs else None)
    db = _open_ncdb(args.db)
    db.setTestplan(plan)

    # Write to a temp file then replace
    tmp = args.db + ".tmp"
    NcdbWriter().write(db, tmp)
    os.replace(tmp, args.db)

    print(
        f"Imported testplan from '{args.hjson_path}': "
        f"{len(plan.testpoints)} testpoints, "
        f"{len(plan.covergroups)} covergroups"
    )


# ---------------------------------------------------------------------------
# testplan closure
# ---------------------------------------------------------------------------

def cmd_testplan_closure(args) -> None:
    """Execute ``pyucis testplan closure``."""
    from ucis.ncdb.testplan import get_testplan, Testplan
    from ucis.ncdb.testplan_closure import compute_closure
    from ucis.ncdb.waivers import WaiverSet
    from ucis.ncdb.reports import (
        report_testpoint_closure,
        format_testpoint_closure,
        report_stage_gate,
        format_stage_gate,
    )

    db = _open_ncdb(args.db)

    # Load testplan
    testplan_path = getattr(args, "testplan", None)
    if testplan_path:
        plan = Testplan.load(testplan_path)
    else:
        plan = get_testplan(db)

    if plan is None:
        print(
            "Error: no testplan found. Embed one with "
            "'pyucis testplan import' or supply --testplan.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Load waivers
    waivers = None
    waivers_path = getattr(args, "waivers", None)
    if waivers_path:
        from ucis.ncdb.waivers import WaiverSet
        waivers = WaiverSet.load(waivers_path)
    elif hasattr(db, "getWaivers"):
        waivers = db.getWaivers()

    results = compute_closure(plan, db, waivers=waivers)

    fmt = getattr(args, "output_format", "text")
    out = open(args.out, "w") if getattr(args, "out", None) else sys.stdout

    try:
        if fmt == "json":
            summary = report_testpoint_closure(results)
            out.write(summary.to_json() + "\n")
        else:
            summary = report_testpoint_closure(results)
            out.write(format_testpoint_closure(summary) + "\n")

            # Stage gate (if requested)
            stage = getattr(args, "stage", None)
            if stage:
                gate = report_stage_gate(results, stage, plan)
                out.write("\n" + format_stage_gate(gate) + "\n")
    finally:
        if out is not sys.stdout:
            out.close()


# ---------------------------------------------------------------------------
# testplan export-junit
# ---------------------------------------------------------------------------

def cmd_testplan_export_junit(args) -> None:
    """Execute ``pyucis testplan export-junit``."""
    from ucis.ncdb.testplan import get_testplan, Testplan
    from ucis.ncdb.testplan_closure import compute_closure
    from ucis.ncdb.testplan_export import export_junit_xml

    db = _open_ncdb(args.db)

    testplan_path = getattr(args, "testplan", None)
    if testplan_path:
        plan = Testplan.load(testplan_path)
    else:
        plan = get_testplan(db)

    if plan is None:
        print(
            "Error: no testplan found. Embed one with "
            "'pyucis testplan import' or supply --testplan.",
            file=sys.stderr,
        )
        sys.exit(1)

    results = compute_closure(plan, db)
    output_path = getattr(args, "out", None) or "closure_results.xml"
    suite_name = getattr(args, "suite_name", None) or "testplan_closure"
    export_junit_xml(results, output_path, suite_name=suite_name)
    print(f"JUnit XML written to '{output_path}'")
