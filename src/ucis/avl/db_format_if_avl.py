"""AVL (Apheleia Verification Library) format interface for PyUCIS format registry."""

from typing import Union, BinaryIO
from ucis.rgy.format_if_db import FormatIfDb, FormatDescDb, FormatDbFlags, FormatCapabilities
from ucis.mem.mem_ucis import MemUCIS
from ucis import UCIS

from .avl_json_reader import AvlJsonReader
from .avl_json_writer import AvlJsonWriter


class DbFormatIfAvlJson(FormatIfDb):
    """AVL JSON format interface.
    
    Supports reading and writing AVL JSON export format.
    """
    
    def read(self, file_or_filename: Union[str, BinaryIO]) -> UCIS:
        if isinstance(file_or_filename, str):
            filename = file_or_filename
        else:
            filename = getattr(file_or_filename, 'name', 'coverage.json')
            file_or_filename.close()
        
        db = MemUCIS()
        AvlJsonReader().read(filename, db)
        return db
    
    def write(self, db: UCIS, file_or_filename: Union[str, BinaryIO], ctx=None):
        """Write UCIS database to AVL JSON format."""
        filename = file_or_filename if isinstance(file_or_filename, str) else file_or_filename.name
        AvlJsonWriter().write(db, filename, ctx)
    
    @staticmethod
    def register(rgy):
        rgy.addDatabaseFormat(FormatDescDb(
            DbFormatIfAvlJson,
            "avl-json",
            FormatDbFlags.Read | FormatDbFlags.Write,
            "AVL (Apheleia Verification Library) JSON export format",
            capabilities=FormatCapabilities(
                can_read=True, can_write=True,
                functional_coverage=True, cross_coverage=False,
                ignore_illegal_bins=False, code_coverage=False,
                toggle_coverage=False, fsm_coverage=False,
                assertions=False, history_nodes=False,
                design_hierarchy=False, lossless=False,
            )))
