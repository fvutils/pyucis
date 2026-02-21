'''
Created on Jun 22, 2022

@author: mballance
'''
from typing import Dict
from .format_if_db import FormatDescDb
from ucis.rgy.format_if_rpt import FormatDescRpt
from ucis.report.format_rpt_text import FormatRptText
from ucis.report.format_rpt_json import FormatRptJson
from ucis.xml.db_format_if_xml import DbFormatIfXml
from ucis.lib.db_format_if_lib import DbFormatIfLib
from ucis.yaml.db_format_if_yaml import DbFormatIfYaml

class FormatRgy(object):
    """
    Registry for various format-support objects. Classes to access
    coverage databases and emit reports are registered here.
    """

    _in_inst = False    
    _inst = None
    
    def __init__(self):
        if not FormatRgy._in_inst:
            raise Exception("Obtain the FormatRgy singleton by calling FormatRgy.inst()")
        self._format_db_m : Dict[str, FormatDescDb] = {}
        self._format_rpt_m : Dict[str, FormatDescRpt] = {}
        pass
    
    def addDatabaseFormat(self, desc : FormatDescDb):
        self._format_db_m[desc._name] = desc
    
    def addReportFormat(self, desc : FormatDescRpt):
        self._format_rpt_m[desc._name] = desc
    
    def getDatabaseFormats(self):
        fmts = list(self._format_db_m.keys())
        fmts.sort()
        return fmts
    
    def hasDatabaseFormat(self, fmt):
        return fmt in self._format_db_m.keys()
    
    def hasReportFormat(self, fmt):
        return fmt in self._format_rpt_m.keys()
    
    def getReportFormats(self):
        fmts = list(self._format_rpt_m.keys())
        fmts.sort()
        return fmts
    
    def getDatabaseDesc(self, fmt):
        return self._format_db_m[fmt]
    
    def getReportDesc(self, fmt):
        return self._format_rpt_m[fmt]
    
    def getDefaultDatabase(self):
        return 'xml'
    
    def getDefaultReport(self):
        return 'txt'
    
    def detectDatabaseFormat(self, path):
        """
        Detect database format from file extension and content.
        
        Args:
            path: Path to the database file
            
        Returns:
            Format name (str) or None if cannot detect
        """
        import os
        from pathlib import Path
        
        if not os.path.exists(path):
            return None
        
        # Try extension-based detection first
        ext = Path(path).suffix.lower()
        if ext == '.xml':
            return 'xml'
        elif ext in ['.yaml', '.yml']:
            return 'yaml'
        elif ext in ['.cdb', '.db', '.sqlite', '.sqlite3']:
            return 'sqlite'
        elif ext == '.dat':
            return 'vltcov'
        
        # Try content-based detection
        try:
            with open(path, 'rb') as f:
                header = f.read(16)
                if header.startswith(b'SQLite format 3'):
                    return 'sqlite'
                elif header.startswith(b'<?xml'):
                    return 'xml'
                # For YAML, read a bit more
                f.seek(0)
                header = f.read(1024)
                if header.startswith(b'---') or b'ucis:' in header:
                    return 'yaml'
        except:
            pass
        
        return None
    
    def _init_rgy(self):
#        self.addDatabaseFormat(FormatDescDb(
#            fmt_if, name, flags, description))
        DbFormatIfXml.register(self)
        DbFormatIfLib.register(self)
        DbFormatIfYaml.register(self)
        
        # Register SQLite format
        from ucis.sqlite.db_format_if_sqlite import DbFormatIfSqlite
        DbFormatIfSqlite.register(self)
        
        # Register Verilator format
        from ucis.vltcov.db_format_if_vltcov import DbFormatIfVltCov
        DbFormatIfVltCov.register(self)
        
        # Register cocotb-coverage formats
        from ucis.cocotb.db_format_if_cocotb import DbFormatIfCocotbXml, DbFormatIfCocotbYaml
        DbFormatIfCocotbXml.register(self)
        DbFormatIfCocotbYaml.register(self)
        
        # Register AVL format
        from ucis.avl.db_format_if_avl import DbFormatIfAvlJson
        DbFormatIfAvlJson.register(self)

        # Register LCOV format
        from ucis.formatters.db_format_if_lcov import DbFormatIfLcov
        DbFormatIfLcov.register(self)
        
        FormatRptJson.register(self)
        FormatRptText.register(self)
        
        # Register HTML format
        from ucis.report.format_rpt_html import FormatRptHtml
        FormatRptHtml.register(self)
    
    @classmethod
    def inst(cls):
        if cls._inst is None:
            cls._in_inst = True
            cls._inst = cls()
            cls._in_inst = False
            cls._inst._init_rgy()
        return cls._inst
    
    