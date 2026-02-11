
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
Created on Jan 9, 2020

@author: ballance
'''
from enum import IntEnum


class RealProperty(IntEnum):
    """Real-valued (floating-point) property identifiers.
    
    Defines property identifiers for accessing real (double-precision
    floating-point) properties on UCIS objects via getRealProperty() and
    setRealProperty() methods.
    
    Real properties are used for floating-point data such as percentages,
    ratios, or measurements that require fractional precision.
    
    Note:
        Currently only a placeholder property 'b' is defined. Additional
        real-valued properties may be added in future versions as needed
        by the UCIS standard or tool implementations.
        
    Example:
        >>> # Access real property on an object
        >>> value = obj.getRealProperty(coverindex=-1, property=RealProperty.b)
        >>> obj.setRealProperty(coverindex=-1, property=RealProperty.b, 
        ...                     value=0.95)
        
    See Also:
        Obj.getRealProperty(): Get real property value
        Obj.setRealProperty(): Set real property value
        IntProperty: Integer property identifiers
        StrProperty: String property identifiers
        UCIS LRM Section 8.16 "Property Management"
    """
    b = 0
    """Placeholder real property (currently unused)."""