from ucis.unimpl_error import UnimplError

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

class CoverInstance(CvgScope):
    """Covergroup instance scope.
    
    CoverInstance represents a specific instance of a covergroup when
    per-instance coverage is enabled. It extends CvgScope to inherit
    covergroup options (at_least, auto_bin_max, etc.).
    
    When a covergroup has per_instance=True, each instantiation creates
    a COVERINSTANCE scope to track coverage separately. This enables
    analysis of which instances are contributing to overall coverage.
    
    Example:
        >>> # Covergroup with per-instance mode
        >>> cg = design.createCovergroup("cg_bus", src_info, 1, SourceT.SV)
        >>> cg.setPerInstance(True)
        >>>
        >>> # Create instances (CoverInstance objects)
        >>> inst1 = cg.createCoverInstance("inst_0", src_info, 1, SourceT.SV)
        >>> inst2 = cg.createCoverInstance("inst_1", src_info, 1, SourceT.SV)
        >>>
        >>> # Each instance has separate coverage
        >>> for cp in inst1.coverPoints():
        ...     data = cp.getCoverData()
        
    See Also:
        CvgScope: Base class with options
        Covergroup: Container for covergroup instances
        Covergroup.setPerInstance(): Enable per-instance mode
        ScopeTypeT.COVERINSTANCE: Instance scope type
        UCIS LRM Section 6.4.3.2 "Covergroup Instances"
    """
    
    def __init__(self):
        super().__init__()
        
    def getStmtIndex(self):
        """Get statement index (if applicable).
        
        Raises:
            UnimplError: Not typically used for cover instances.
        """
        raise UnimplError()
    
    def setStmtIndex(self, idx):
        """Set statement index (if applicable).
        
        Args:
            idx: Statement index.
            
        Raises:
            UnimplError: Not typically used for cover instances.
        """
        raise UnimplError()
