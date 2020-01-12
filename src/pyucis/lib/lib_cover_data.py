'''
Created on Jan 11, 2020

@author: ballance
'''
from _ctypes import Structure, Union
from ctypes import c_int, c_ulonglong, c_uint, c_wchar_p
from builtins import staticmethod
from pyucis.cover_data import CoverData
from pyucis.cover_flags_t import CoverFlagsT

class LibCoverDataValue(Union):
    _fields_ = [
        ("int64", c_ulonglong),
        ("int32", c_uint),
        ("bytevector", c_wchar_p)
        ]
    
class LibCoverData(Structure):
    
    _fields_ = [
        ("type", c_int),
        ("flags", c_int),
        ("data", LibCoverDataValue),
        ("goal", c_int),
        ("weight", c_int),
        ("limit", c_int),
        ("bitlen", c_int)
        ]
    
    @staticmethod
    def ctor(covdata : CoverData):
        data = LibCoverDataValue()
        if covdata.flags & CoverFlagsT.IS_32BIT:
            data.int32 = covdata.data
        elif covdata.flags & CoverFlagsT.IS_64BIT:
            data.int64 = covdata.data
        elif covdata.flags & CoverFlagsT.IS_VECTOR:
            data.bytevector = covdata.data
        else:
            raise Exception("data format not specified")
        
        ret = LibCoverData(covdata.type, covdata.flags, data)
        
        return ret
            
    