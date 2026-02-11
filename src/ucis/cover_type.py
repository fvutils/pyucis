
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
from ucis.scope import Scope
from ucis.unimpl_error import UnimplError

class CoverType(Scope):
    """Base class for coverage type scopes with goal/limit/weight management.
    
    CoverType extends Scope to add coverage-specific attributes including
    coverage goal, limit, and weight. These attributes control how coverage
    is measured and reported.
    
    - **Goal**: Target count for coverage completion
    - **Limit**: Maximum count before saturation
    - **Weight**: Relative importance in coverage calculations
    
    This class serves as a base for coverage scopes that need these attributes,
    providing getter/setter methods that can be overridden by subclasses.
    
    Example:
        >>> # CoverType is typically not used directly
        >>> # Subclasses like Coverpoint inherit these methods
        >>> cp = cg.createCoverpoint("cp_addr", src_info, 1, SourceT.SV)
        >>> cp.setCoverGoal(100)
        >>> cp.setCoverWeight(10)
        >>> goal = cp.getCoverGoal()
        
    See Also:
        Scope: Base scope class
        Coverpoint: Subclass using goal/weight
        CoverData: Coverage data with goal/weight fields
    """
    
    def __init__(self):
        super().__init__()
        
    def setCoverGoal(self, goal : int):
        """Set the coverage goal.
        
        Args:
            goal: Target count for coverage completion.
            
        Raises:
            UnimplError: Not implemented in base class or specific backend.
        """
        raise UnimplError()
    
    def getCoverGoal(self)->int:
        """Get the coverage goal.
        
        Returns:
            Goal value.
            
        Raises:
            UnimplError: Not implemented in base class or specific backend.
        """
        raise UnimplError()
    
    def setCoverLimit(self, limit : int):
        """Set the coverage count limit (saturation point).
        
        Args:
            limit: Maximum count value.
            
        Raises:
            NotImplementedError: Not implemented in base class or specific backend.
        """
        raise NotImplementedError()
    
    def getCoverLimit(self) -> int:
        """Get the coverage count limit.
        
        Returns:
            Limit value.
            
        Raises:
            NotImplementedError: Not implemented in base class or specific backend.
        """
        raise NotImplementedError()
    
    def setCoverWeight(self, weight : int):
        """Set the coverage weight.
        
        Args:
            weight: Relative weight value.
            
        Raises:
            NotImplementedError: Not implemented in base class or specific backend.
        """
        raise NotImplementedError()
    
    def getCoverWeight(self) -> int:
        """Get the coverage weight.
        
        Returns:
            Weight value.
            
        Raises:
            NotImplementedError: Not implemented in base class or specific backend.
        """
        raise NotImplementedError()
    
        