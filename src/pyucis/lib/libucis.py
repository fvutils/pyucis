
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
Created on Jan 10, 2020

@author: ballance
'''
from ctypes import *
import sys

# Global handle to the UCIS library
_lib = None

class FuncMap():
    
    def __init__(self):
        self.fmap = {}
        
    def add(self, fname, func):
        self.fmap[fname] = func
        
    def __getattr__(self, key):
        if key in self.fmap.keys():
            return self.fmap[key]
        else:
            raise Exception("No such function \"" + key + "\"")
        return None
    
_funcs = FuncMap()

fspec = {
    "ucis_Open" : (
        CFUNCTYPE(c_void_p, c_char_p),
        ((1,"file"),)),
    "ucis_Write" : (
        CFUNCTYPE(c_int, c_void_p, c_char_p, c_void_p, c_int, c_uint),
        ((1,"db"),(1,"file"),(1,"scope"),(1,"recurse"),(1,"covertype"))),
    "ucis_Close" : (
        CFUNCTYPE(c_int, c_void_p),
        ((1,"db"),)),
    "ucis_CreateHistoryNode" : (
        CFUNCTYPE(c_void_p, c_void_p, c_void_p, c_char_p, c_char_p, c_int),
        ((1,"db"),(1,"parent"),(1,"logicalname"),(1,"physicalname"),(1,"kind"))),
    "ucis_CreateScope" : (
        CFUNCTYPE(c_void_p, c_void_p, c_void_p, c_char_p, c_void_p, c_int, c_int, c_int, c_int),
        ((1,"db"),(1,"parent"),(1,"name"),(1,"sourceinfo"),(1,"weight"),(1,"source"),(1,"type"),(1,"flags"))),
    "ucis_CreateInstance" : (
        CFUNCTYPE(c_void_p, c_void_p, c_void_p, c_char_p, c_void_p, c_int, c_int, c_int, c_void_p, c_int),
        ((1,"db"),(1,"parent"),(1,"name"),(1,"fileinfo"),(1,"weight"),(1,"source"),(1,"type"),(1,"du_scope"),(1,"flags"))),
    "ucis_CreateNextCover" : (
        CFUNCTYPE(c_int, c_void_p, c_void_p, c_char_p, c_void_p, c_void_p),
        ((1,"db"),(1,"parent"),(1,"name"),(1,"data"),(1,"sourceinfo"))),
    "ucis_SetIntProperty" : (
        CFUNCTYPE(None, c_void_p, c_void_p, c_int, c_int, c_int),
        ((1,"db"),(1,"obj"),(1,"coverindex"),(1,"property"),(1,"value"))),
    "ucis_SetStringProperty" : (
        CFUNCTYPE(None, c_void_p, c_void_p, c_int, c_int, c_char_p),
        ((1,"db"),(1,"obj"),(1,"coverindex"),(1,"property"),(1,"value"))),
    "ucis_CreateFileHandle" : (
        CFUNCTYPE(c_void_p, c_void_p, c_char_p, c_char_p),
        ((1,"db"),(1,"filename"),(1,"workdir")))
    }

# Load the specified UCIS library
def load_ucis_library(lib):
    global _lib, _funcs
    
    _lib = CDLL(lib)
    for f in fspec.keys():
        fsig = fspec[f]
        proto = fsig[0]
        attr = fsig[1]
        func = proto((f, _lib), attr)
        print("Setting " + f + "=" + str(func))
        _funcs.add(f, func)
    
def get_ucis_library():
    return _lib

def get_lib():
    global _funcs
    return _funcs
    