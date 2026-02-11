
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
from ucis.cov_scope import CovScope

class FuncCovScope(CovScope):
    """Base class for functional coverage scopes.
    
    FuncCovScope serves as the base class for all functional coverage scope
    types including covergroups, coverpoints, and crosses. It extends CovScope
    to provide functional coverage-specific behaviors.
    
    Functional coverage scopes measure design functionality by tracking how
    well test stimulus exercises specified design features, as opposed to
    code coverage which measures structural code execution.
    
    This class is primarily a marker class in the hierarchy. Concrete
    functionality is provided by subclasses:
    - CvgScope: Coverpoint and cross options
    - Covergroup: Container for coverpoints and crosses
    - Coverpoint: Individual coverage variable
    - Cross: Cross-product coverage
    
    Example:
        >>> # FuncCovScope is not directly instantiated
        >>> # Use concrete subclasses instead:
        >>> cg = design.createCovergroup("cg_bus", src_info, 1, SourceT.SV)
        >>> cp = cg.createCoverpoint("cp_addr", src_info, 1, SourceT.SV)
        
    See Also:
        CovScope: Base coverage scope class
        CvgScope: Coverage scope with options
        Covergroup: Covergroup container
        Coverpoint: Coverpoint with bins
        UCIS LRM Section 6.4.3 "Functional Coverage"
    """
    
    def __init__(self):
        super().__init__()
        
        