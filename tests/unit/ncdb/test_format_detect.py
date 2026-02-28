"""Unit tests for ucis.ncdb.format_detect."""

import os
import tempfile
import zipfile
import json
import pytest

from ucis.ncdb.format_detect import detect_cdb_format
from ucis.ncdb.constants import SQLITE_MAGIC, MEMBER_MANIFEST, NCDB_FORMAT


def _make_sqlite_file(path):
    with open(path, "wb") as f:
        f.write(SQLITE_MAGIC)
        f.write(b"\x00" * 100)


def _make_ncdb_file(path):
    with zipfile.ZipFile(path, "w") as zf:
        manifest = {"format": NCDB_FORMAT, "version": "1.0"}
        zf.writestr(MEMBER_MANIFEST, json.dumps(manifest))


def _make_plain_zip(path):
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("data.txt", "hello")


def test_detect_sqlite():
    with tempfile.NamedTemporaryFile(suffix=".cdb", delete=False) as f:
        _make_sqlite_file(f.name)
        path = f.name
    try:
        assert detect_cdb_format(path) == "sqlite"
    finally:
        os.unlink(path)


def test_detect_ncdb():
    with tempfile.NamedTemporaryFile(suffix=".cdb", delete=False) as f:
        path = f.name
    _make_ncdb_file(path)
    try:
        assert detect_cdb_format(path) == "ncdb"
    finally:
        os.unlink(path)


def test_detect_unknown_plain_zip():
    with tempfile.NamedTemporaryFile(suffix=".cdb", delete=False) as f:
        path = f.name
    _make_plain_zip(path)
    try:
        assert detect_cdb_format(path) == "unknown"
    finally:
        os.unlink(path)


def test_detect_nonexistent():
    assert detect_cdb_format("/no/such/file.cdb") == "unknown"


def test_detect_real_merged_cdb():
    """The repo's merged.cdb should be detected as SQLite."""
    repo_root = os.path.join(os.path.dirname(__file__), "..", "..")
    cdb_path = os.path.join(repo_root, "merged.cdb")
    if not os.path.exists(cdb_path):
        pytest.skip("merged.cdb not present")
    assert detect_cdb_format(cdb_path) == "sqlite"
