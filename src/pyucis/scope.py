from pyucis.cover_data import CoverData

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
from pyucis.source_info import SourceInfo
from pyucis.unimpl_error import UnimplError
from pyucis.obj import Obj
from pyucis.int_property import IntProperty
from pyucis.scope_type_t import ScopeTypeT
from pyucis.flags_t import FlagsT
from pyucis.source_t import SourceT

class Scope(Obj):
    
    def __init__(self):
        pass
    
    def createScope(self,
                    name : str,
                    srcinfo : SourceInfo,
                    weight : int,
                    source,
                    type,
                    flags):
        raise UnimplError()
    
    def createInstance(self,
                    name : str,
                    fileinfo : SourceInfo,
                    weight : int,
                    source : SourceT,
                    type : ScopeTypeT,
                    du_scope : 'Scope',
                    flags : FlagsT) ->'Scope':
        raise UnimplError()
    
    def createCovergroup(self,
                    name : str,
                    srcinfo : SourceInfo,
                    weight : int,
                    source) -> 'Covergroup':
        raise UnimplError()
    
    def createNextCover(self,
                        name : str,
                        data : CoverData,
                        sourceinfo : SourceInfo) -> int:
        raise UnimplError()

    def getWeight(self, coverindex):
        return self.getIntProperty(coverindex, IntProperty.COVER_WEIGHT)
    
