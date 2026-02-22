'''
Created on Jun 11, 2022

@author: mballance
'''
from dataclasses import dataclass, field
from ucis.ucis import UCIS
from enum import IntFlag, auto

class FormatDbFlags(IntFlag):
    Create = auto()
    Read = auto()
    Write = auto()


@dataclass
class FormatCapabilities:
    """Documents what UCIS data model features a format can represent.

    Attributes:
        can_read: Format has a reader (``<Format> → UCIS``).
        can_write: Format has a writer (``UCIS → <Format>``).
        functional_coverage: Supports covergroups, coverpoints, bins.
        cross_coverage: Supports cross coverage.
        ignore_illegal_bins: Supports ignore/illegal bin types.
        code_coverage: Supports statement, branch, expression, condition.
        toggle_coverage: Supports toggle coverage.
        fsm_coverage: Supports FSM state/transition coverage.
        assertions: Supports SVA cover/assert directives.
        history_nodes: Supports test history / merge metadata.
        design_hierarchy: Supports DU + instance scope hierarchy.
        lossless: True only when the format is a complete UCIS representation
            (currently XML and SQLite).
    """
    can_read: bool = False
    can_write: bool = False
    functional_coverage: bool = False
    cross_coverage: bool = False
    ignore_illegal_bins: bool = False
    code_coverage: bool = False
    toggle_coverage: bool = False
    fsm_coverage: bool = False
    assertions: bool = False
    history_nodes: bool = False
    design_hierarchy: bool = False
    lossless: bool = False


class FormatDescDb(object):
    
    def __init__(self,
                 fmt_if: 'FormatIfDb',
                 name: str,
                 flags: FormatDbFlags,
                 description: str,
                 capabilities: FormatCapabilities = None):
        self._fmt_if = fmt_if
        self._name = name
        self._flags = flags
        self._description = description
        self._capabilities = capabilities or FormatCapabilities()
        
    @property
    def fmt_if(self):
        return self._fmt_if
    
    @property
    def name(self):
        return self._name
    
    @property
    def flags(self):
        return self._flags
    
    @property
    def description(self):
        return self._description

    @property
    def capabilities(self) -> FormatCapabilities:
        return self._capabilities


class FormatIfDb(object):
    
    def init(self, options):
        raise NotImplementedError("DbFormatIf.init not implemented by %s" % str(type(self)))
    
    def create(self, filename=None) -> UCIS:
        """
        Creates a new UCIS database.
        If filename is None, the database will be created in memory. Some database
        backends can take advantage of the filename to write directly to disk instead
        of later copying to disk. Databases that can write directly to disk will
        overwrite any existing file on creation.
        """
        raise NotImplementedError("DbFormatIf.create not implemented by %s" % str(type(self)))
    
    def read(self, file_or_filename) -> UCIS:
        """
        Read a UCIS database from a file
        """
        raise NotImplementedError("DbFormatIf.read not implemented by %s" % str(type(self)))

    def write(self, db: UCIS, file_or_filename) -> None:
        """
        Write a UCIS database to a file.  Raises NotImplementedError for read-only formats.
        """
        raise NotImplementedError("DbFormatIf.write not implemented by %s" % str(type(self)))
    
