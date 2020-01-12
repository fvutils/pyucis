from pyucis.int_property import IntProperty

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
Created on Dec 22, 2019

@author: ballance
'''
from pyucis.scope import Scope
from pyucis.cover_type import CoverType
from pyucis.source_info import SourceInfo
from pyucis.unimpl_error import UnimplError
from pyucis.cvg_scope import CvgScope

class Covergroup(CvgScope):
    
    def __init__(self):
        pass
    
    def getPerInstance(self)->bool:
        raise UnimplError()
    
    def setPerInstance(self, perinst):
        raise UnimplError()
    
    def getMergeInstances(self)->bool:
        raise UnimplError()
    
    def setMergeInstances(self, m:bool):
        raise UnimplError()
        

    def createCoverpoint(self,
                         name : str,
                         srcinfo : SourceInfo,
                         weight : int,
                         source) -> CoverType:
        raise UnimplError()
    
    def createCross(self, 
                    name, 
                    srcinfo : SourceInfo,
                    weight : int,
                    source, 
                    points_l):
        pass
    
    def createCrossByName(self, name, fileinfo, weight, source, point_names_l):
        pass
    
    def getIntProperty(
        self, 
        coverindex:int, 
        property:IntProperty)->int:
        if property == IntProperty.CVG_PERINSTANCE:
            return 1 if self.getPerInstance() else 0
        elif property == IntProperty.CVG_MERGEINSTANCES:
            return 1 if self.getMergeInstances() else 0
        else:
            return super().getIntProperty(coverindex, property)

    def setIntProperty(
        self, 
        coverindex:int, 
        property:IntProperty, 
        value:int):
        if property == IntProperty.CVG_PERINSTANCE:
            self.setPerInstance(value==1)
        elif property == IntProperty.CVG_MERGEINSTANCES:
            self.setMergeInstances(value==1)
        else:
            super().setIntProperty(coverindex, property, value)

        
    