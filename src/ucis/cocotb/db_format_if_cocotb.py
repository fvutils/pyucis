"""cocotb-coverage format interface for PyUCIS format registry."""

from typing import Union, BinaryIO
from ucis.rgy.format_if_db import FormatIfDb, FormatDescDb, FormatDbFlags, FormatCapabilities
from ucis.mem.mem_ucis import MemUCIS
from ucis import UCIS

from .cocotb_xml_reader import CocotbXmlReader
from .cocotb_xml_writer import CocotbXmlWriter
from .cocotb_yaml_reader import CocotbYamlReader
from .cocotb_yaml_writer import CocotbYamlWriter


class DbFormatIfCocotbXml(FormatIfDb):
    """cocotb-coverage XML format interface.
    
    Supports reading and writing cocotb-coverage XML export format.
    """
    
    def read(self, file_or_filename: Union[str, BinaryIO]) -> UCIS:
        if isinstance(file_or_filename, str):
            filename = file_or_filename
        else:
            filename = getattr(file_or_filename, 'name', 'coverage.xml')
            file_or_filename.close()
        
        db = MemUCIS()
        CocotbXmlReader().read(filename, db)
        return db
    
    def write(self, db: UCIS, file_or_filename: Union[str, BinaryIO], ctx=None):
        """Write UCIS database to cocotb-coverage XML format."""
        filename = file_or_filename if isinstance(file_or_filename, str) else file_or_filename.name
        CocotbXmlWriter().write(db, filename, ctx)
    
    @staticmethod
    def register(rgy):
        rgy.addDatabaseFormat(FormatDescDb(
            DbFormatIfCocotbXml,
            "cocotb-xml",
            FormatDbFlags.Read | FormatDbFlags.Write,
            "cocotb-coverage XML export format",
            capabilities=FormatCapabilities(
                can_read=True, can_write=True,
                functional_coverage=True, cross_coverage=True,
                ignore_illegal_bins=False, code_coverage=False,
                toggle_coverage=False, fsm_coverage=False,
                assertions=False, history_nodes=False,
                design_hierarchy=False, lossless=False,
            )))


class DbFormatIfCocotbYaml(FormatIfDb):
    """cocotb-coverage YAML format interface.
    
    Supports reading and writing cocotb-coverage YAML export format.
    """
    
    def read(self, file_or_filename: Union[str, BinaryIO]) -> UCIS:
        if isinstance(file_or_filename, str):
            filename = file_or_filename
        else:
            filename = getattr(file_or_filename, 'name', 'coverage.yml')
            file_or_filename.close()
        
        db = MemUCIS()
        CocotbYamlReader().read(filename, db)
        return db
    
    def write(self, db: UCIS, file_or_filename: Union[str, BinaryIO], ctx=None):
        """Write UCIS database to cocotb-coverage YAML format."""
        filename = file_or_filename if isinstance(file_or_filename, str) else file_or_filename.name
        CocotbYamlWriter().write(db, filename, ctx)
    
    @staticmethod
    def register(rgy):
        rgy.addDatabaseFormat(FormatDescDb(
            DbFormatIfCocotbYaml,
            "cocotb-yaml",
            FormatDbFlags.Read | FormatDbFlags.Write,
            "cocotb-coverage YAML export format",
            capabilities=FormatCapabilities(
                can_read=True, can_write=True,
                functional_coverage=True, cross_coverage=True,
                ignore_illegal_bins=False, code_coverage=False,
                toggle_coverage=False, fsm_coverage=False,
                assertions=False, history_nodes=False,
                design_hierarchy=False, lossless=False,
            )))
