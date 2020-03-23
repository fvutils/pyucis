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
Created on Jan 8, 2020

@author: ballance
'''

from pyucis import IntProperty
from pyucis.flags_t import FlagsT
from pyucis.mem.mem_obj import MemObj
from pyucis.scope import Scope
from pyucis.scope_type_t import ScopeTypeT
from pyucis.source_info import SourceInfo
from pyucis.source_t import SourceT
from pyucis.toggle_dir_t import ToggleDirT
from pyucis.toggle_metric_t import ToggleMetricT
from pyucis.toggle_type_t import ToggleTypeT
from pyucis.unimpl_error import UnimplError
from typing import Iterator

from pyucis.mem.mem_scope_iterator import MemScopeIterator


class MemScope(MemObj,Scope):
    
    def __init__(self,
                 parent : 'MemScope',
                 name : str,
                 srcinfo : SourceInfo,
                 weight : int,
                 source : SourceT,
                 type : ScopeTypeT,
                 flags : FlagsT):
        super().__init__()
        self.m_parent = parent
        self.m_name = name
        self.m_srcinfo = srcinfo if srcinfo is not None else SourceInfo(None, -1, -1)
        self.m_weight = weight
        self.m_source = source
        self.m_type = type
        self.m_flags = flags
        self.m_goal = -1
        self.m_source_type = 0
        self.m_is_under_du = 0
        self.m_children = []
        
    def addChild(self, c):
        self.m_children.append(c)
        
    def getWeight(self):
        return self.m_weight
    
    def setWeight(self, w):
        self.m_weight = w
        
    def getGoal(self)->int:
        return self.m_goal
    
    def setGoal(self, goal):
        self.m_goal = goal
        
    def getScopeType(self)->ScopeTypeT:
        return self.m_type
    
    def getScopeName(self)->str:
        return self.m_name
        
    def getSourceInfo(self)->SourceInfo:
        return self.m_srcinfo
        
    def getIntProperty(
            self, 
            coverindex : int,
            property : IntProperty
            )->int:
        if property == IntProperty.SCOPE_WEIGHT:
            return self.m_weight
        elif property == IntProperty.COVER_GOAL:
            return self.m_goal
        elif property == IntProperty.SCOPE_SOURCE_TYPE:
            return self.m_source_type
        elif property == IntProperty.SCOPE_IS_UNDER_DU:
            # TODO: need to detect
            return self.m_is_under_du
        else:
            return super().getIntProperty(coverindex, property)
    
    def setIntProperty(
            self,
            coverindex : int,
            property : IntProperty,
            value : int):
        if property == IntProperty.SCOPE_WEIGHT:
            self.m_weight = value
        elif property == IntProperty.COVER_GOAL:
            self.m_goal = value
        elif property == IntProperty.SCOPE_SOURCE_TYPE:
            self.m_source_type = value
        else:
            super().setIntProperty(coverindex, property, value)    
            
    def createCovergroup(self, 
        name:str, 
        srcinfo:SourceInfo, 
        weight:int, 
        source)->'Covergroup':
        from .mem_covergroup import MemCovergroup
        ret = MemCovergroup(
            self,
            name,
            srcinfo,
            weight,
            source)
        self.m_children.append(ret)
        return ret

    def createScope(self,
                name : str,
                srcinfo : SourceInfo,
                weight : int,
                source,
                type : ScopeTypeT,
                flags):
        # Creates a type scope and associates source information with it
        if ScopeTypeT.DU_ANY(type):
            ret = MemScope(self, name, srcinfo, weight,
                              source, type, flags)
        else:
            raise UnimplError()
        
        self.m_children.append(ret)
        
        return ret            
    
    def createInstance(self,
                    name : str,
                    fileinfo : SourceInfo,
                    weight : int,
                    source : SourceT,
                    type : ScopeTypeT,
                    du_scope : 'Scope',
                    flags : FlagsT) ->'Scope':
        # Create an instance of a type scope
        from pyucis.mem.mem_instance_scope import MemInstanceScope
        ret = MemInstanceScope(self, name, fileinfo, weight, source, type, du_scope, flags)
        self.m_children.append(ret)
        return ret
    
    def createToggle(self,
                    name : str,
                    canonical_name : str,
                    flags : FlagsT,
                    toggle_metric : ToggleMetricT,
                    toggle_type : ToggleTypeT,
                    toggle_dir : ToggleDirT) -> 'Scope':
        raise UnimplError()            
    
    def scopes(self, mask)->Iterator['Scope']:
        return MemScopeIterator(self.m_children, mask)
    