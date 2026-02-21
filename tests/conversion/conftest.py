"""
Shared fixtures and helpers for conversion tests.
"""
import pytest
import tempfile
import os
from pathlib import Path
from typing import Optional

from ucis.mem.mem_ucis import MemUCIS
from ucis.sqlite.sqlite_ucis import SqliteUCIS
from ucis.ucis import UCIS
from ucis.conversion import ConversionContext


# ---------------------------------------------------------------------------
# DB factory helpers
# ---------------------------------------------------------------------------

def make_db(backend: str, path: Optional[Path] = None) -> UCIS:
    """Create a UCIS database of the given backend type.

    Args:
        backend: ``"mem"`` or ``"sqlite"``.
        path: File path for SQLite (ignored for mem).  If None, creates
              in-memory SQLite.

    Returns:
        A fresh, empty UCIS database.
    """
    if backend == "mem":
        return MemUCIS()
    elif backend == "sqlite":
        if path is None:
            return SqliteUCIS(":memory:")
        return SqliteUCIS(str(path))
    else:
        raise ValueError(f"Unknown backend: {backend!r}")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(params=["mem", "sqlite"], ids=["mem", "sqlite"])
def empty_src_db(request, tmp_path):
    """Empty source UCIS database, parametrized over mem/sqlite."""
    db = make_db(request.param, tmp_path / "src.db")
    yield db
    try:
        db.close()
    except Exception:
        pass


@pytest.fixture(params=["mem", "sqlite"], ids=["mem", "sqlite"])
def empty_dst_db(request, tmp_path):
    """Empty destination UCIS database, parametrized over mem/sqlite."""
    db = make_db(request.param, tmp_path / "dst.db")
    yield db
    try:
        db.close()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Format write helper
# ---------------------------------------------------------------------------

def write_format(db: UCIS, fmt_name: str, out_path: Path,
                 ctx: Optional[ConversionContext] = None) -> Path:
    """Write a UCIS database to *out_path* in the named format.

    Args:
        db: Source database.
        fmt_name: Registered format name (``"xml"``, ``"yaml"``, etc.).
        out_path: Destination file path (extension should match format).
        ctx: Optional ConversionContext for warning/progress tracking.

    Returns:
        The path that was written.

    Raises:
        NotImplementedError: If the format does not support writing.
    """
    from ucis.rgy.format_rgy import FormatRgy
    rgy = FormatRgy.inst()
    desc = rgy.getDatabaseDesc(fmt_name)
    fmt_if = desc.fmt_if()
    # Try format-specific write method first
    if hasattr(fmt_if, 'write'):
        fmt_if.write(db, str(out_path), ctx=ctx)
    else:
        db.write(str(out_path))
    return out_path
