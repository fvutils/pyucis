"""``pyucis history`` CLI subcommands.

Subcommands
-----------
query   Display history records for a specific test name.
stats   Show aggregate statistics (top-failing, top-flaky, or named test).
"""

from __future__ import annotations

import json
import sys
import time


def _open_ncdb(path: str):
    from ucis.ncdb.ncdb_ucis import NcdbUCIS
    return NcdbUCIS(path)


def _ts(ts_arg: str) -> int:
    """Parse an ISO date string or integer unix timestamp."""
    if ts_arg is None:
        return None
    try:
        return int(ts_arg)
    except ValueError:
        import datetime
        dt = datetime.datetime.fromisoformat(ts_arg)
        return int(dt.timestamp())


# ---------------------------------------------------------------------------
# history query
# ---------------------------------------------------------------------------

def cmd_history_query(args) -> None:
    """Execute ``pyucis history query``."""
    db = _open_ncdb(args.db)
    ts_from = _ts(getattr(args, "from_", None))
    ts_to = _ts(getattr(args, "to", None))

    records = db.query_test_history(args.test_name, ts_from=ts_from, ts_to=ts_to)

    fmt = getattr(args, "output_format", "text")
    out = open(args.out, "w") if getattr(args, "out", None) else sys.stdout

    try:
        if fmt == "json":
            data = [
                {
                    "ts": r.ts,
                    "date": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(r.ts)),
                    "status": "pass" if r.status == 0 else "fail",
                    "seed_id": r.seed_id,
                }
                for r in records
            ]
            out.write(json.dumps(data, indent=2) + "\n")
        else:
            out.write(
                f"{'Date':<20} {'Status':<8} {'Seed':>12}\n"
            )
            out.write("-" * 42 + "\n")
            for r in records:
                date = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(r.ts))
                status = "pass" if r.status == 0 else "fail"
                out.write(f"{date:<20} {status:<8} {r.seed_id:>12}\n")
            out.write(f"\nTotal records: {len(records)}\n")
    finally:
        if out is not sys.stdout:
            out.close()


# ---------------------------------------------------------------------------
# history stats
# ---------------------------------------------------------------------------

def cmd_history_stats(args) -> None:
    """Execute ``pyucis history stats``."""
    db = _open_ncdb(args.db)
    fmt = getattr(args, "output_format", "text")
    out = open(args.out, "w") if getattr(args, "out", None) else sys.stdout

    try:
        top_flaky = getattr(args, "top_flaky", None)
        top_failing = getattr(args, "top_failing", None)
        test_name = getattr(args, "test_name", None)

        if test_name:
            stats = db.get_test_stats(test_name)
            if stats is None:
                out.write(f"No stats found for test '{test_name}'\n")
                return
            if fmt == "json":
                d = {
                    "name": test_name,
                    "total_runs": stats.total_runs,
                    "pass_count": stats.pass_count,
                    "fail_count": stats.fail_count,
                    "flake_score": stats.flake_score,
                    "mean_cpu_time": stats.mean_cpu_time,
                    "grade_score": stats.grade_score,
                    "last_status": stats.last_status,
                }
                out.write(json.dumps(d, indent=2) + "\n")
            else:
                out.write(f"Test: {test_name}\n")
                out.write(f"  Total runs:  {stats.total_runs}\n")
                out.write(f"  Pass:        {stats.pass_count}\n")
                out.write(f"  Fail:        {stats.fail_count}\n")
                out.write(f"  Flake score: {stats.flake_score:.3f}\n")
                out.write(f"  Mean CPU:    {stats.mean_cpu_time:.2f}s\n")
                out.write(f"  Grade score: {stats.grade_score:.3f}\n")
            return

        rows = []
        if top_flaky:
            rows = db.top_flaky_tests(n=top_flaky)
            title = f"Top {top_flaky} flaky tests"
        elif top_failing:
            rows = db.top_failing_tests(n=top_failing)
            title = f"Top {top_failing} failing tests"
        else:
            rows = db.top_flaky_tests(n=20)
            title = "Top 20 flaky tests"

        if fmt == "json":
            out.write(json.dumps(rows, indent=2) + "\n")
        else:
            out.write(f"{title}\n")
            out.write("-" * 60 + "\n")
            col = max((len(r[0]) for r in rows), default=10) + 2 if rows else 30
            out.write(f"{'Test':<{col}} {'Score':>8} {'Pass':>7} {'Fail':>7}\n")
            out.write("-" * (col + 26) + "\n")
            for name, score, pc, fc in rows:
                out.write(f"{name:<{col}} {score:>8.3f} {pc:>7} {fc:>7}\n")
    finally:
        if out is not sys.stdout:
            out.close()
