
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
Created on Jan 5, 2020

@author: ballance
'''

class NameValue():
    """Name-value pair container.
    
    Simple data structure for storing name-value pairs, commonly used for
    design parameters, attributes, and other key-value metadata.
    
    Attributes:
        name (str): The name/key of the pair.
        value (str): The value associated with the name.
        
    Example:
        >>> # Create design parameter
        >>> param = NameValue("WIDTH", "32")
        >>> print(f"{param.getName()} = {param.getValue()}")
        >>>
        >>> # Use in parameter lists
        >>> params = [
        ...     NameValue("DATA_WIDTH", "64"),
        ...     NameValue("ADDR_WIDTH", "32"),
        ...     NameValue("DEPTH", "1024")
        ... ]
        
    See Also:
        InstanceCoverage.getDesignParameters(): Returns list of NameValue
        InstanceCoverage.addDesignParameter(): Accepts NameValue parameter
    """
    
    def __init__(self, name, value):
        """Create name-value pair.
        
        Args:
            name: Name/key string.
            value: Value string.
        """
        self.name = name
        self.value = value
        
    def getName(self) -> str:
        """Get the name/key.
        
        Returns:
            Name string.
        """
        return self.name
    
    def getValue(self) -> str:
        """Get the value.
        
        Returns:
            Value string.
        """
        return self.value