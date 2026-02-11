
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

class CovScope(Scope):
    """Base class for generic coverage scopes.
    
    CovScope is the base class for all coverage-related scopes in the UCIS
    hierarchy. It sits between the generic Scope class and more specialized
    coverage scope types like FuncCovScope (functional coverage) and code
    coverage scopes.
    
    CovScope provides common infrastructure for coverage scopes but adds
    minimal functionality beyond the base Scope class. It serves primarily
    as a structural marker in the type hierarchy to distinguish coverage
    scopes from non-coverage scopes (like pure structural scopes).
    
    Subclass hierarchy:
        Scope
        └── CovScope (this class)
            ├── FuncCovScope (functional coverage)
            │   └── CvgScope (covergroups/coverpoints)
            └── (Code coverage scopes)
    
    Note:
        CovScope is rarely instantiated directly. Use specific subclasses
        like Covergroup, Coverpoint, or code coverage scope types instead.
        
    Example:
        >>> # CovScope is not directly used; use subclasses instead
        >>> # For functional coverage:
        >>> cg = design.createCovergroup("cg_bus", src_info, 1, SourceT.SV)
        >>>
        >>> # For code coverage:
        >>> instance = design.createInstance("u_core", src_info, 1, SourceT.SV, "core")
        
    See Also:
        Scope: Base scope class
        FuncCovScope: Functional coverage base
        CvgScope: Covergroup scope base
        InstanceScope: Design instance scope
    """
    
    def __init__(self):
        
        pass
    
    
    