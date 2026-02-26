"""
format_detect.py — CDB file format discrimination.

Detects whether a .cdb file is a SQLite database or an NCDB ZIP archive.
"""

import zipfile
import json

from .constants import SQLITE_MAGIC, ZIP_SIGNATURES, NCDB_FORMAT, MEMBER_MANIFEST


def detect_cdb_format(path: str) -> str:
    """Return 'sqlite', 'ncdb', or 'unknown' for the file at *path*.

    Detection algorithm:
    1. Read first 16 bytes.
    2. If bytes[0:16] == SQLITE_MAGIC → 'sqlite'
    3. If bytes[0:4] in ZIP_SIGNATURES:
         open as ZIP, look for manifest.json with "format": "NCDB" → 'ncdb'
    4. Otherwise → 'unknown'
    """
    try:
        with open(path, "rb") as f:
            header = f.read(16)
    except OSError:
        return "unknown"

    if len(header) >= 16 and header[:16] == SQLITE_MAGIC:
        return "sqlite"

    if len(header) >= 4 and header[:4] in ZIP_SIGNATURES:
        try:
            with zipfile.ZipFile(path, "r") as zf:
                with zf.open(MEMBER_MANIFEST) as mf:
                    manifest = json.load(mf)
                    if manifest.get("format") == NCDB_FORMAT:
                        return "ncdb"
        except (zipfile.BadZipFile, KeyError, json.JSONDecodeError, Exception):
            pass

    return "unknown"
