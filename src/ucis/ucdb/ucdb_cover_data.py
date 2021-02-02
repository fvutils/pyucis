'''
Created on Jan 11, 2020

@author: ballance
'''
from _ctypes import Structure, Union
from ctypes import c_int, c_ulonglong, c_uint, c_wchar_p, c_ulong
from builtins import staticmethod
from ucis.cover_data import CoverData
from ucis.cover_flags_t import CoverFlagsT

class UcdbCoverDataValue(Union):
    _fields_ = [
        ("int64", c_ulonglong),
        ("int32", c_uint),
        ("bytevector", c_wchar_p)
        ]
    
class UcdbCoverData(Structure):
    
    _fields_ = [
        ("type", c_ulonglong),
        ("flags", c_int),
        ("data", UcdbCoverDataValue),
        ("goal", c_int),
        ("weight", c_int),
        ("limit", c_int),
        ("bitlen", c_int)
        ]
    
    @staticmethod
    def ctor(covdata : CoverData):
        data = UcdbCoverDataValue()
        if (covdata.flags & CoverFlagsT.IS_32BIT) != 0:
            data.int32 = covdata.data
        elif (covdata.flags & CoverFlagsT.IS_64BIT) != 0:
            data.int64 = covdata.data
        elif covdata.flags & CoverFlagsT.IS_VECTOR:
            data.bytevector = covdata.data
        else:
            raise Exception("data format not specified")

        ret = UcdbCoverData(
            covdata.type, 
            covdata.flags, 
            data,
            covdata.goal,
            covdata.weight,
            covdata.limit,
            covdata.bitlen)
        
        return ret
            
    