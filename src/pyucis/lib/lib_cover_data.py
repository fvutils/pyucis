'''
Created on Jan 11, 2020

@author: ballance
'''
from _ctypes import Structure, Union
from ctypes import c_int, c_ulonglong, c_uint, c_wchar_p, c_ulong
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
        ("type", c_ulonglong),
        ("flags", c_int),
        ("data", LibCoverDataValue),
        ("goal", c_int),
        ("weight", c_int),
        ("limit", c_int),
        ("bitlen", c_int)
        ]
    
    @staticmethod
    def ctor(covdata : CoverData):
        print("CoverData.ctor")
        data = LibCoverDataValue()
        if (covdata.flags & CoverFlagsT.IS_32BIT) != 0:
            data.int32 = covdata.data
            print("Count: " + str(data.int32))
        elif (covdata.flags & CoverFlagsT.IS_64BIT) != 0:
            data.int64 = covdata.data
            print("Count64: " + str(data.int64))
        elif covdata.flags & CoverFlagsT.IS_VECTOR:
            data.bytevector = covdata.data
        else:
            raise Exception("data format not specified")

        print("covdata.type=" + str(covdata.type) + " " + hex(covdata.type))        
        ret = LibCoverData(
            covdata.type, 
            covdata.flags, 
            data,
            covdata.goal,
            covdata.weight,
            covdata.limit,
            covdata.bitlen)
        
        return ret
            
    