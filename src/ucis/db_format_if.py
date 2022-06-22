'''
Created on Jun 11, 2022

@author: mballance
'''
from ucis.ucis import UCIS
from enum import IntFlag, auto

class DbFormatFlags(IntFlag):
    Create = auto()
    Read = auto()
    Write = auto()

class DbFormatIf(object):
    
    def flags(self) -> DbFormatFlags:
        raise NotImplementedError("DbFormatIf.flags not implemented by %s" % str(type(self)))
    
    def init(self, options):
        raise NotImplementedError("DbFormatIf.init not implemented by %s" % str(type(self)))
    
    def create(self) -> UCIS:
        raise NotImplementedError("DbFormatIf.create not implemented by %s" % str(type(self)))
    
    def read(self, file_or_filename) -> UCIS:
        raise NotImplementedError("DbFormatIf.read not implemented by %s" % str(type(self)))
    
    def write(self, db : UCIS, file_or_filename):
        raise NotImplementedError("DbFormatIf.write not implemented by %s" % str(type(self)))
    