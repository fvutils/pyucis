"""
DbFormatIfNcdb — UCIS format registry interface for the NCDB backend.

Registers the 'ncdb' format so that existing pyucis CLI commands and
utilities can use NCDB files via -if ncdb / -of ncdb.
"""

from ucis.rgy.format_if_db import FormatIfDb, FormatDescDb, FormatDbFlags, FormatCapabilities
from ucis.ucis import UCIS


class DbFormatIfNcdb(FormatIfDb):
    """NCDB ZIP-based format interface."""

    def __init__(self):
        self.options = {}

    def init(self, options):
        self.options = options or {}

    def create(self, filename=None) -> UCIS:
        """Create a new NCDB database.

        Returns an in-memory MemUCIS that can later be written to disk
        via write().  If *filename* is given, the file is created on close().
        """
        from ucis.mem.mem_ucis import MemUCIS
        db = MemUCIS()
        db._ncdb_filename = filename  # stash for write()
        return db

    def read(self, file_or_filename) -> UCIS:
        """Read an NCDB .cdb file into a MemUCIS."""
        from .ncdb_reader import NcdbReader
        if isinstance(file_or_filename, str):
            path = file_or_filename
        elif hasattr(file_or_filename, 'name'):
            path = file_or_filename.name
        else:
            raise ValueError("NCDB format requires a file path")
        return NcdbReader().read(path)

    def write(self, db: UCIS, file_or_filename) -> None:
        """Write *db* to an NCDB .cdb file."""
        from .ncdb_writer import NcdbWriter
        if isinstance(file_or_filename, str):
            path = file_or_filename
        elif hasattr(file_or_filename, 'name'):
            path = file_or_filename.name
        else:
            raise ValueError("NCDB format requires a file path")
        NcdbWriter().write(db, path)

    @classmethod
    def register(cls, rgy):
        """Register NCDB format with the format registry."""
        rgy.addDatabaseFormat(FormatDescDb(
            fmt_if=cls,
            name='ncdb',
            flags=FormatDbFlags.Create | FormatDbFlags.Read | FormatDbFlags.Write,
            description='NCDB — Native Coverage Database (ZIP-based binary format)',
            capabilities=FormatCapabilities(
                can_read=True, can_write=True,
                functional_coverage=True, cross_coverage=True,
                ignore_illegal_bins=True, code_coverage=True,
                toggle_coverage=True, fsm_coverage=True,
                assertions=True, history_nodes=True,
                design_hierarchy=True, lossless=True,
            )))
