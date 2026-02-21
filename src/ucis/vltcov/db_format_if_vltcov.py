"""Verilator coverage format interface for PyUCIS."""

from typing import Union, BinaryIO
from ucis.rgy.format_if_db import FormatIfDb, FormatDescDb, FormatDbFlags, FormatCapabilities
from ucis.mem.mem_ucis import MemUCIS
from ucis import UCIS

from .vlt_parser import VltParser
from .vlt_to_ucis_mapper import VltToUcisMapper
from .vlt_writer import VltCovWriter


class DbFormatIfVltCov(FormatIfDb):
    """Verilator coverage format interface.
    
    Supports reading and writing Verilator's SystemC::Coverage-3 format (.dat files).
    """
    
    def read(self, file_or_filename: Union[str, BinaryIO]) -> UCIS:
        if isinstance(file_or_filename, str):
            filename = file_or_filename
        else:
            filename = getattr(file_or_filename, 'name', 'coverage.dat')
            file_or_filename.close()
        
        parser = VltParser()
        items = parser.parse_file(filename)
        db = MemUCIS()
        VltToUcisMapper(db, source_file=filename).map_items(items)
        return db
    
    def write(self, db: UCIS, file_or_filename: Union[str, BinaryIO], ctx=None):
        """Write UCIS database to Verilator .dat format."""
        filename = file_or_filename if isinstance(file_or_filename, str) else file_or_filename.name
        VltCovWriter().write(db, filename, ctx)
    
    @staticmethod
    def register(rgy):
        rgy.addDatabaseFormat(FormatDescDb(
            DbFormatIfVltCov,
            "vltcov",
            FormatDbFlags.Read | FormatDbFlags.Write,
            "Verilator coverage format (SystemC::Coverage-3)",
            capabilities=FormatCapabilities(
                can_read=True, can_write=True,
                functional_coverage=False, cross_coverage=False,
                ignore_illegal_bins=False, code_coverage=True,
                toggle_coverage=True, fsm_coverage=False,
                assertions=False, history_nodes=False,
                design_hierarchy=True, lossless=False,
            )))
