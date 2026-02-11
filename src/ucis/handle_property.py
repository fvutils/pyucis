
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


class HandleProperty(IntEnum):
    """Handle property identifiers for UCIS objects.
    
    Defines property identifiers for accessing handle-valued (object reference)
    properties on UCIS objects via getHandleProperty() and setHandleProperty()
    methods.
    
    Handle properties store references to other UCIS objects, enabling
    relationships and links between different parts of the database. For
    example, an instance scope might have a handle property referencing
    its design unit definition.
    
    Note:
        Currently only a placeholder property 'd' is defined. Additional
        handle properties may be added in future versions as the UCIS
        standard evolves and implementation requirements emerge.
        
    Example:
        >>> # Access handle property on an object
        >>> handle = obj.getHandleProperty(coverindex=-1, 
        ...                                property=HandleProperty.d)
        >>> if handle:
        ...     print(f"Referenced object: {handle.getName()}")
        >>>
        >>> # Set handle property
        >>> obj.setHandleProperty(coverindex=-1, 
        ...                       property=HandleProperty.d,
        ...                       value=referenced_obj)
        
    See Also:
        Obj.getHandleProperty(): Get handle property value
        Obj.setHandleProperty(): Set handle property value
        IntProperty: Integer property identifiers
        StrProperty: String property identifiers
        RealProperty: Real property identifiers
        UCIS LRM Section 8.16 "Property Management"
    """
    
    d = 0
    """Placeholder handle property (currently unused)."""
