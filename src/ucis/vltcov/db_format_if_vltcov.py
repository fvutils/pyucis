"""Verilator coverage format interface for PyUCIS."""

from typing import Union, BinaryIO
from ucis.rgy.format_if_db import FormatIfDb, FormatDescDb, FormatDbFlags
from ucis.mem.mem_ucis import MemUCIS
from ucis import UCIS

from .vlt_parser import VltParser
from .vlt_to_ucis_mapper import VltToUcisMapper


class DbFormatIfVltCov(FormatIfDb):
    """Verilator coverage format interface.
    
    Supports reading Verilator's SystemC::Coverage-3 format (.dat files).
    """
    
    def read(self, file_or_filename: Union[str, BinaryIO]) -> UCIS:
        """Read Verilator .dat file and return UCIS database.
        
        Args:
            file_or_filename: Path to .dat file or file object
            
        Returns:
            UCIS database populated with coverage data
        """
        # Handle file objects vs filenames
        if isinstance(file_or_filename, str):
            filename = file_or_filename
        else:
            # File object - get name if available
            filename = getattr(file_or_filename, 'name', 'coverage.dat')
            file_or_filename.close()  # We'll reopen by name
        
        # Parse Verilator coverage file
        parser = VltParser()
        items = parser.parse_file(filename)
        
        # Create UCIS database
        db = MemUCIS()
        
        # Map to UCIS structure
        mapper = VltToUcisMapper(db)
        mapper.map_items(items)
        
        return db
    
    def write(self, db: UCIS, file_or_filename: Union[str, BinaryIO]):
        """Write UCIS database to Verilator format.
        
        Not yet implemented.
        
        Args:
            db: UCIS database to write
            file_or_filename: Target file
            
        Raises:
            NotImplementedError: Writing not yet supported
        """
        raise NotImplementedError("Writing Verilator format not yet supported")
    
    @staticmethod
    def register(rgy):
        """Register Verilator format with PyUCIS format registry.
        
        Args:
            rgy: Format registry instance
        """
        rgy.addDatabaseFormat(FormatDescDb(
            DbFormatIfVltCov,
            "vltcov",
            FormatDbFlags.Read,  # Read-only for now
            "Verilator coverage format (SystemC::Coverage-3)"
        ))
