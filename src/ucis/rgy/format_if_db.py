'''
Created on Jun 11, 2022

@author: mballance
'''
from ucis.ucis import UCIS
from enum import IntFlag, auto

class FormatDbFlags(IntFlag):
    Create = auto()
    Read = auto()
    Write = auto()
    
class FormatDescDb(object):
    
    def __init__(self, 
                 fmt_if : 'FormatIfDb',
                 name : str,
                 flags : FormatDbFlags,
                 description : str):
        self._fmt_if = fmt_if
        self._name = name
        self._flags = flags
        self._description = description
        
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


class FormatIfDb(object):
    
    def init(self, options):
        raise NotImplementedError("DbFormatIf.init not implemented by %s" % str(type(self)))
    
    def create(self) -> UCIS:
        raise NotImplementedError("DbFormatIf.create not implemented by %s" % str(type(self)))
    
    def read(self, file_or_filename) -> UCIS:
        raise NotImplementedError("DbFormatIf.read not implemented by %s" % str(type(self)))
    
    def write(self, db : UCIS, file_or_filename):
        raise NotImplementedError("DbFormatIf.write not implemented by %s" % str(type(self)))
    