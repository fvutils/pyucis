
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
from ucis.cvg_scope import CvgScope

class IgnoreBinScope(CvgScope):
    """Scope for ignore bins in functional coverage.
    
    IgnoreBinScope represents bins that should be ignored in coverage
    calculations. Ignore bins are used in SystemVerilog covergroups to
    exclude certain value ranges or combinations from coverage metrics.
    
    Ignore bins:
    - Do not contribute to coverage percentage calculations
    - Are not counted as "covered" or "uncovered"
    - Serve to document intentionally uncovered cases
    - Help focus coverage on meaningful scenarios
    
    Ignore bins are typically created with the CoverTypeT.IGNOREBIN type
    and can be treated as specialized coverage scopes in some implementations.
    
    Example:
        >>> # Ignore bins are typically created on coverpoints
        >>> cp = cg.createCoverpoint("cp_addr", src_info, 1, SourceT.SV)
        >>>
        >>> # Create ignore bin for reserved address range
        >>> ignore_bin = cp.createBin(
        ...     "ignore_reserved",
        ...     src_info,
        ...     at_least=0,  # Not counted
        ...     count=0,
        ...     rhs="[1000:1023]",
        ...     kind=CoverTypeT.IGNOREBIN)
        
    Note:
        Most implementations treat ignore bins as cover items (CoverItem)
        rather than scopes. IgnoreBinScope exists for implementations that
        need scope-level representation of ignore bins.
        
    See Also:
        CvgScope: Base coverage scope class
        IllegalBinScope: Illegal bin scope
        CoverTypeT.IGNOREBIN: Ignore bin type
        Coverpoint.createBin(): Create bins including ignore bins
    """
    
    def __init__(self):
        super().__init__()
        