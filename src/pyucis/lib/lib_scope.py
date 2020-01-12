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

from _ctypes import byref
from pyucis.scope import Scope
from pyucis.unimpl_error import UnimplError

from pyucis.cover_data import CoverData
from pyucis.flags_t import FlagsT
from pyucis.lib.lib_cover_data import LibCoverData
from pyucis.lib.lib_obj import LibObj
from pyucis.lib.lib_source_info import LibSourceInfo
from pyucis.lib.libucis import get_lib
from pyucis.scope_type_t import ScopeTypeT
from pyucis.source_info import SourceInfo
from pyucis.source_t import SourceT
from pyucis.toggle_dir_t import ToggleDirT
from pyucis.toggle_metric_t import ToggleMetricT
from pyucis.toggle_type_t import ToggleTypeT


class LibScope(LibObj, Scope):
    
    def __init__(self, db, scope):
        super().__init__(db, scope)
        print("LibScope::init - db=" + str(self.db) + " " + str(self.obj))
        
    def createScope(self, 
        name:str, 
        srcinfo:SourceInfo, 
        weight:int, 
        source, 
        type, 
        flags):
        print("createScope: type=" + str(type))
        srcinfo_p = None if srcinfo is None else byref(LibSourceInfo.ctor(srcinfo))
        sh = get_lib().ucis_CreateScope(
            self.db,
            self.obj,
            None if name is None else str.encode(name),
            srcinfo_p,
            weight,
            source,
            type,
            flags)
        
        return LibScope(self.db, sh)
    
    def createInstance(self,
                    name : str,
                    fileinfo : SourceInfo,
                    weight : int,
                    source : SourceT,
                    type : ScopeTypeT,
                    du_scope : Scope,
                    flags : FlagsT):
        fileinfo_p = None if fileinfo is None else byref(LibSourceInfo.ctor(fileinfo))
        sh = get_lib().ucis_CreateInstance(
            self.db,
            self.obj,
            str.encode(name),
            fileinfo_p,
            weight,
            source,
            type,
            du_scope.obj,
            flags)
        
        if sh is None:
            raise Exception("ucis_CreateInstance failed")
        
        return LibScope(self.db, sh)
    
    def createToggle(self,
                    name : str,
                    canonical_name : str,
                    flags : FlagsT,
                    toggle_metric : ToggleMetricT,
                    toggle_type : ToggleTypeT,
                    toggle_dir : ToggleDirT) -> 'Scope':
        th = get_lib().ucis_CreateToggle(
            self.db,
            self.obj,
            str.encode(name),
            None if canonical_name is None else str.encode(canonical_name),
            flags,
            toggle_metric,
            toggle_type,
            toggle_dir)
        return LibScope(self.db, th)
    
    def createNextCover(self,
                        name : str,
                        data : CoverData,
                        sourceinfo : SourceInfo) -> int:
        sourceinfo_p = None if sourceinfo is None else byref(LibSourceInfo.ctor(sourceinfo))
        data_p = byref(LibCoverData.ctor(data))
        
        return get_lib().ucis_CreateNextCover(
            self.db,
            self.obj,
            str.encode(name),
            data_p,
            sourceinfo_p)
        
        