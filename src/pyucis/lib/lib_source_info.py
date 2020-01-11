'''
Created on Jan 11, 2020

@author: ballance
'''
from _ctypes import Structure
from ctypes import c_void_p, c_int
from pyucis.source_info import SourceInfo

class LibSourceInfo(Structure):
    """Ctypes description of a SourceInfoT data structure"""
    
    _fields_ = [
        ("filehandle",c_void_p),
        ("line", c_int),
        ("token", c_int)]
    
    @staticmethod
    def ctor(srcinfo : SourceInfo):
        return LibSourceInfo(
            srcinfo.file.fh,
            srcinfo.line,
            srcinfo.token)
        
        