from enum import IntEnum, auto
from _ctypes import Structure, Union
from ctypes import c_int, c_longlong, c_double, c_float, c_char_p, c_void_p
from ucis.ucdb.ucis2ucdb_property_map import Ucis2UcdbPropertyMap

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

'''
Created on Jan 11, 2020

@author: ballance
'''
from ucis.obj import Obj
from ucis.int_property import IntProperty
from ucis.real_property import RealProperty
from ucis.str_property import StrProperty
from ucis.handle_property import HandleProperty
from ucis.ucdb.libucdb import get_lib

class UcdbAttrType(IntEnum):
    INT = 0
    FLOAT = auto()
    DOUBLE = auto()
    STRING = auto()
    MEMBLK = auto()
    INT64 = auto()
    HANDLE = auto()
    ARRAY = auto()
    
class UcdbAttrValueMS(Structure):
    _fields_ = [
        ("size", c_int),
        ("data", c_char_p)
        ]

class UcdbAttrValueU(Union):
    _fields_ = [
        ("i64value", c_longlong),
        ("ivalue", c_int),
        ("fvalue", c_float),
        ("dvalue", c_double),
        ("svalue", c_char_p),
        ("mvalue", UcdbAttrValueMS)
    ]
    
class UcdbAttrValue(Structure):
    _fields_ = [
        ("type", c_int),
        ("u", UcdbAttrValueU),
        ("attrhandle", c_void_p)
        ]

    @staticmethod    
    def ctor_int(v : int):
        u = UcdbAttrValueU()
        u.ivalue = v
        ret = UcdbAttrValue(
            UcdbAttrType.INT,
            u)
        ret.u.ivalue = v
        return ret

class UcdbObj(Obj):
    
    def __init__(self, db, obj):
        self.db = db
        self.obj = obj

    def getIntProperty(
            self, 
            coverindex : int,
            property : IntProperty
            )->int:
        raise NotImplementedError()
    
    def setIntProperty(
            self,
            coverindex : int,
            property : IntProperty,
            value : int):
        obj = self.db if self.obj is None else self.obj
        attr = Ucis2UcdbPropertyMap.int2attr(property)
        if attr is not None:
            print("Warning: Skipping attribute " + str(property) + " (" + attr + ")")
#            raise Exception("failed to set property " + str(property))
        else:
            print("Warning: Skipping attribute " + str(property))
#        get_lib().ucdb_AttrAdd(self.db, obj, coverindex, property, value)

    def getRealProperty(
            self,
            coverindex : int,
            property : RealProperty) -> float:
        raise NotImplementedError()
        
    def setRealProperty(
            self,
            coverindex : int,
            property : RealProperty,
            value : float):
        raise NotImplementedError()

    def getStringProperty(
            self,
            coverindex : int,
            property : StrProperty) -> str:
        raise NotImplementedError()
    
    def setStringProperty(
            self,
            coverindex : int,
            property : StrProperty,
            value : str):
        obj = self.db if self.obj is None else self.obj
        get_lib().ucis_SetStringProperty(
            self.db, 
            obj, 
            coverindex, 
            property, 
            str.encode(value))
        
    def getHandleProperty(
            self,
            coverindex : int,
            property : HandleProperty) -> 'Scope':
        raise NotImplementedError()
    
    def setHandleProperty(
            self,
            coverindex : int,
            property : HandleProperty,
            value : 'Scope'):
        raise NotImplementedError()        