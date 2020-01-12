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
from pyucis.str_property import StrProperty
'''
Created on Jan 8, 2020

@author: ballance
'''

from pyucis.unimpl_error import UnimplError

from pyucis.func_cov_scope import FuncCovScope
from pyucis.int_property import IntProperty


class CvgScope(FuncCovScope):
    
    def __init__(self):
        super().__init__()

    def getAtLeast(self)->int:
        raise UnimplError()
    
    def setAtLeast(self, atleast):
        raise UnimplError()
    
    def getAutoBinMax(self)->int:
        raise UnimplError()
    
    def setAutoBinMax(self, auto_max):
        raise UnimplError()
    
    def getDetectOverlap(self)->bool:
        raise UnimplError()
    
    def setDetectOverlap(self, detect:bool):
        raise UnimplError()
    
    def getStrobe(self)->int:
        raise UnimplError()
    
    def setStrobe(self, s):
        raise UnimplError()
    
    def getComment(self)->str:
        raise UnimplError()
    
    def setComment(self, c:str):
        raise UnimplError()
    
    
    def getIntProperty(
        self, 
        coverindex:int, 
        property:IntProperty)->int:
        if property == IntProperty.CVG_ATLEAST:
            return self.getAtLeast()
        elif property == IntProperty.CVG_AUTOBINMAX:
            return self.getAutoBinMax()
        elif property == IntProperty.CVG_DETECTOVERLAP:
            return 1 if self.getDetectOverlap() else 0
        elif property == IntProperty.CVG_STROBE:
            return self.getStrobe()
        else:
            return super().getIntProperty(coverindex, property)
        
    def setIntProperty(
        self, 
        coverindex:int, 
        property:IntProperty, 
        value:int):
        if property == IntProperty.CVG_ATLEAST:
            self.setAtLeast(value)
        elif property == IntProperty.CVG_AUTOBINMAX:
            self.setAutoBinMax(value)
        elif property == IntProperty.CVG_DETECTOVERLAP:
            self.setDetectOverlap(value==1)
        elif property == IntProperty.CVG_STROBE:
            self.setStrobe(value)
        else:
            super().setIntProperty(coverindex, property, value)
            
    def getStringProperty(
        self, 
        coverindex:int, 
        property:StrProperty)->str:
        if property == StrProperty.COMMENT:
            return self.getComment()
        else:
            return super().getStringProperty(coverindex, property)
        
    def setStringProperty(
        self, 
        coverindex:int, 
        property:StrProperty, 
        value:str):
        if property == StrProperty.COMMENT:
            self.setComment(value)
        else:
            super().setStringProperty(coverindex, property, value)

