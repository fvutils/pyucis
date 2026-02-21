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

from ucis.obj import Obj
from ucis.str_property import StrProperty


class MemObj(Obj):
    
    def __init__(self):
        Obj.__init__(self)
        self._str_properties = {}

    def getStringProperty(
            self,
            coverindex : int,
            property : StrProperty) -> str:
        if property == StrProperty.SCOPE_NAME:
            return getattr(self, 'm_name', None)
        if property == StrProperty.COMMENT:
            return getattr(self, 'm_comment', self._str_properties.get(property))
        return self._str_properties.get(property)
    
    def setStringProperty(
            self,
            coverindex : int,
            property : StrProperty,
            value : str):
        if property == StrProperty.COMMENT and hasattr(self, 'm_comment'):
            self.m_comment = value
        else:
            self._str_properties[property] = value
        
    