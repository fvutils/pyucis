"""
CLI integration tests for NCDB format.

Tests `pyucis convert`, `pyucis merge`, and `pyucis show summary` commands
with NCDB input/output via subprocess so that auto-detect and format
registry paths are exercised end-to-end.
"""

import os
import json
import subprocess
import sys
import tempfile

import pytest

from ucis.ncdb.ncdb_writer import NcdbWriter
from ucis.ncdb.ncdb_reader import NcdbReader
from ucis.mem.mem_ucis import MemUCIS
from ucis.source_t import SourceT
from ucis.scope_type_t import ScopeTypeT
from ucis.cover_data import CoverData
from ucis.cover_type_t import CoverTypeT
from ucis.history_node_kind import HistoryNodeKind

_REPO_ROOT   = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_TESTS_ROOT  = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_SRC         = os.path.join(_REPO_ROOT, "src")
_PYTHON      = sys.executable

_SKIP_IF_NO_MERGED = pytest.mark.skipif(
    not os.path.exists(os.path.join(_TESTS_ROOT, "merged.cdb")),
    reason="merged.cdb not present",
)


def _run(*args, check=True, **kw):
    env = dict(os.environ)
    env["PYTHONPATH"] = _SRC
    return subprocess.run(
        [_PYTHON, "-m", "ucis"] + list(args),
        capture_output=True, text=True, env=env, **kw
    )


def _make_simple_ncdb(path: str, scope_name: str = "top",
                      bins: int = 3, test_name: str = "t1"):
    db = MemUCIS()
    db.createHistoryNode(None, test_name, None, HistoryNodeKind.TEST)
    blk = db.createScope(scope_name, None, 1, SourceT.SV, ScopeTypeT.BLOCK, 0)
    for i in range(bins):
        cd = CoverData(CoverTypeT.STMTBIN, 0)
        cd.data = i + 1
        blk.createNextCover(f"s{i}", cd, None)
    NcdbWriter().write(db, path)


# ── Tests ─────────────────────────────────────────────────────────────────

def test_convert_ncdb_to_ncdb():
    """convert --if ncdb --of ncdb → valid output file."""
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "src.cdb")
        dst = os.path.join(d, "dst.cdb")
        _make_simple_ncdb(src)
        r = _run("convert", "--input-format", "ncdb", "--output-format", "ncdb",
                 src, "-o", dst)
        assert r.returncode == 0, r.stderr
        assert os.path.exists(dst)
        rt = NcdbReader().read(dst)
        assert list(rt.scopes(ScopeTypeT.ALL))


def test_convert_ncdb_to_xml():
    """convert --if ncdb --of xml → non-empty XML file."""
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "src.cdb")
        dst = os.path.join(d, "out.xml")
        _make_simple_ncdb(src)
        r = _run("convert", "--input-format", "ncdb", "--output-format", "xml",
                 src, "-o", dst)
        assert r.returncode == 0, r.stderr
        assert os.path.exists(dst)
        assert os.path.getsize(dst) > 0


def test_merge_same_schema_ncdb():
    """merge --if ncdb --of ncdb → counts doubled."""
    with tempfile.TemporaryDirectory() as d:
        a  = os.path.join(d, "a.cdb")
        b  = os.path.join(d, "b.cdb")
        out = os.path.join(d, "merged.cdb")
        _make_simple_ncdb(a, bins=3)
        _make_simple_ncdb(b, bins=3)
        r = _run("merge", "--input-format", "ncdb", "--output-format", "ncdb",
                 a, b, "-o", out)
        assert r.returncode == 0, r.stderr
        merged = NcdbReader().read(out)
        scopes = list(merged.scopes(ScopeTypeT.ALL))
        assert scopes
        items = list(scopes[0].coverItems(CoverTypeT.ALL))
        assert items[0].getCoverData().data == 2   # 1+1
        assert items[1].getCoverData().data == 4   # 2+2
        assert items[2].getCoverData().data == 6   # 3+3


def test_show_summary_ncdb_auto_detect():
    """show summary with auto-detect should succeed for NCDB files."""
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "cov.cdb")
        _make_simple_ncdb(src)
        r = _run("show", "summary", src)
        assert r.returncode == 0, r.stderr
        # Output should be valid JSON
        out = r.stdout
        # Strip any preamble text before the JSON object
        start = out.find("{")
        if start >= 0:
            data = json.loads(out[start:])
            assert "overall_coverage" in data


def test_format_registry_ncdb():
    """DbFormatRgy must have 'ncdb' registered."""
    from ucis.db_format_rgy import DbFormatRgy
    rgy = DbFormatRgy.inst()
    assert rgy.hasFormatType("ncdb")
    fmt_if = rgy.getFormatIf("ncdb")
    assert fmt_if is not None


def test_format_registry_ncdb_rgy():
    """FormatRgy must have 'ncdb' registered."""
    from ucis.rgy.format_rgy import FormatRgy
    rgy = FormatRgy.inst()
    assert rgy.hasDatabaseFormat("ncdb")


@_SKIP_IF_NO_MERGED
def test_convert_sqlite_to_ncdb_cli():
    """CLI convert --if sqlite --of ncdb → smaller file than input."""
    merged = os.path.join(_TESTS_ROOT, "merged.cdb")
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "out.cdb")
        r = _run("convert", "--input-format", "sqlite",
                 "--output-format", "ncdb", merged, "-o", out)
        assert r.returncode == 0, r.stderr
        assert os.path.getsize(out) < os.path.getsize(merged) / 10
