'''
Created on Jun 11, 2022

@author: mballance
'''
from ucis.xml.db_format_if_xml import DbFormatIfXml
from ucis.mem.db_format_if_mem import DbFormatIfMem
from ucis.yaml.db_format_if_yaml import DbFormatIfYaml
from ucis.lib.db_format_if_lib import DbFormatIfLib
from ucis.sqlite.db_format_if_sqlite import DbFormatIfSqlite
from ucis.ncdb.db_format_if_ncdb import DbFormatIfNcdb

class DbFormatRgy(object):
    """Database format registry.
    
    Registry for UCIS database backend formats. Manages available backend
    implementations (XML, SQLite, YAML, in-memory, native library) and
    provides access to format interfaces for reading/writing databases.
    
    Supported formats:
    - **mem**: In-memory backend (no persistence)
    - **xml**: XML file format
    - **yml/yaml**: YAML file format  
    - **sqlite**: SQLite database format
    - **lib**: Native library format
    
    This is a singleton registry accessed via DbFormatRgy.inst().
    
    Example:
        >>> # Get format registry
        >>> rgy = DbFormatRgy.inst()
        >>>
        >>> # Check available formats
        >>> formats = rgy.getFormats()
        >>> print(f"Available: {formats}")
        >>>
        >>> # Check if format supported
        >>> if rgy.hasFormatType("sqlite"):
        ...     fmt_if = rgy.getFormatIf("sqlite")
        >>>
        >>> # Use format to create database
        >>> sqlite_if = rgy.getFormatIf("sqlite")
        >>> db = sqlite_if.open("coverage.ucis")
        
    See Also:
        DB: Database factory (uses registry)
        UCIS: Root database class
    """
    
    _inst = None
    
    def __init__(self):
        """Initialize format registry (internal use)."""
        self._fmt_if_m = {}
        self._fmt_desc_m = {}
        
    def addFormatIf(self, name, fmt_if, desc):
        """Add a format interface to registry.
        
        Args:
            name: Format name string (e.g., "sqlite").
            fmt_if: Format interface class.
            desc: Description string.
        """
        self._fmt_if_m[name] = fmt_if
        
    def hasFormatType(self, name):
        """Check if format is supported.
        
        Args:
            name: Format name (e.g., "sqlite", "xml").
            
        Returns:
            True if format is registered, False otherwise.
        """
        return name in self._fmt_if_m.keys()
    
    def getFormats(self):
        """Get list of available format names.
        
        Returns:
            List of format name strings.
        """
        return list(self._fmt_if_m.keys())
    
    def getFormatIf(self, name):
        """Get format interface for specified format.
        
        Args:
            name: Format name (e.g., "sqlite").
            
        Returns:
            Format interface instance.
            
        Raises:
            Exception: If format is not supported.
        """
        if name not in self._fmt_if_m.keys():
            raise Exception("Format %s not supported" % name)
        return self._fmt_if_m[name]()
        
    def init(self):
        """Initialize registry with standard formats (internal use)."""
        self.addFormatIf("lib", DbFormatIfLib, "Native library format")
        self.addFormatIf("mem", DbFormatIfMem, "In-memory format")
        self.addFormatIf("xml", DbFormatIfXml, "XML format")
        self.addFormatIf("yml", DbFormatIfYaml, "YAML format")
        self.addFormatIf("sqlite", DbFormatIfSqlite, "SQLite database format")
        self.addFormatIf("ncdb", DbFormatIfNcdb, "NCDB ZIP-based binary format")
    
    @classmethod
    def inst(cls):
        """Get singleton registry instance.
        
        Returns:
            DbFormatRgy singleton.
        """
        if cls._inst is None:
            cls._inst = cls()
            cls._inst.init()
        return cls._inst