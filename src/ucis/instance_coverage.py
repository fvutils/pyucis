
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
from ucis.name_value import NameValue
from ucis.unimpl_error import UnimplError
from ucis.statement_id import StatementId

class InstanceCoverage():
    """Instance-specific coverage information.
    
    InstanceCoverage provides coverage metadata specific to a design instance,
    including design parameters and statement identifiers. Used for tracking
    coverage with instance-specific context.
    
    This class helps associate coverage data with specific instantiations
    and their parameterization, enabling analysis based on design parameters.
    
    Example:
        >>> # Create instance coverage
        >>> inst_cov = InstanceCoverage()
        >>>
        >>> # Add design parameters
        >>> inst_cov.addDesignParameter(NameValue("WIDTH", "32"))
        >>> inst_cov.addDesignParameter(NameValue("DEPTH", "1024"))
        >>>
        >>> # Query parameters
        >>> params = inst_cov.getDesignParameters()
        >>> for p in params:
        ...     print(f"{p.getName()} = {p.getValue()}")
        >>>
        >>> # Get statement ID
        >>> stmt_id = inst_cov.getId()
        
    See Also:
        NameValue: Name-value pair for parameters
        StatementId: Statement location identifier
        InstanceScope: Design instance scope
    """
    
    def __init__(self):
        pass
    
    
    def getDesignParameters(self) -> [NameValue]:
        """Get design parameters for this instance.
        
        Returns:
            List of NameValue objects representing design parameters.
            
        Raises:
            UnimplError: Not implemented in base class.
        """
        raise UnimplError()
    
    def addDesignParameter(self, p : NameValue):
        """Add a design parameter.
        
        Args:
            p: NameValue object with parameter name and value.
            
        Raises:
            UnimplError: Not implemented in base class.
        """
        raise UnimplError()
    
    def getId(self) -> StatementId:
        """Get the statement identifier.
        
        Returns:
            StatementId object locating this instance in source.
            
        Raises:
            UnimplError: Not implemented in base class.
        """
        raise UnimplError()
    
    def getName(self) -> str:
        """Get the instance name.
        
        Returns:
            Name string.
            
        Raises:
            UnimplError: Not implemented in base class.
        """
        raise UnimplError()
    
    def getKey(self) -> str:
        """Get the instance key identifier.
        
        Returns:
            Key string uniquely identifying this instance.
            
        Raises:
            UnimplError: Not implemented in base class.
        """
        raise UnimplError()
    
    