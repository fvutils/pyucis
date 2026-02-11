
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

class IllegalBinScope(CvgScope):
    """Scope for illegal bins in functional coverage.
    
    IllegalBinScope represents bins that should never be hit during normal
    operation. Illegal bins are used in SystemVerilog covergroups to flag
    error conditions, unexpected value combinations, or design violations.
    
    Illegal bins:
    - Should remain at zero hits during correct operation
    - Any hits typically indicate a design bug or incorrect stimulus
    - Are reported as errors or warnings by coverage tools
    - Do not contribute to coverage percentage calculations
    
    When an illegal bin is hit, coverage tools typically report it as a
    coverage violation, helping identify design or verification issues.
    
    Example:
        >>> # Illegal bins flag error conditions
        >>> cp = cg.createCoverpoint("cp_opcode", src_info, 1, SourceT.SV)
        >>>
        >>> # Create illegal bin for reserved opcodes
        >>> illegal_bin = cp.createBin(
        ...     "illegal_reserved",
        ...     src_info,
        ...     at_least=0,  # Should stay at 0
        ...     count=0,
        ...     rhs="[8'hF0:8'hFF]",  # Reserved range
        ...     kind=CoverTypeT.ILLEGALBIN)
        >>>
        >>> # Check for violations
        >>> data = illegal_bin.getCoverData()
        >>> if data.data > 0:
        ...     print(f"ERROR: Illegal bin hit {data.data} times!")
        
    Note:
        Most implementations treat illegal bins as cover items (CoverItem)
        rather than scopes. IllegalBinScope exists for implementations that
        need scope-level representation of illegal bins.
        
    See Also:
        CvgScope: Base coverage scope class
        IgnoreBinScope: Ignore bin scope
        CoverTypeT.ILLEGALBIN: Illegal bin type
        Coverpoint.createBin(): Create bins including illegal bins
    """
    
    def __init__(self):
        super().__init__()
        
        