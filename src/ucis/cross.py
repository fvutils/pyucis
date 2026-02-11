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
Created on Dec 22, 2019

@author: ballance
'''

from ucis.coverpoint import Coverpoint


class Cross(Coverpoint):
    """Cross-product coverage of multiple coverpoints.
    
    Cross represents a SystemVerilog/SystemC/e cross, which measures coverage
    of combinations of values from multiple coverpoints. A cross automatically
    generates bins for the Cartesian product of the crossed coverpoints' bins.
    
    For example, crossing a 2-bin address coverpoint with a 3-bin data
    coverpoint creates 2×3=6 cross bins, one for each combination.
    
    Cross extends Coverpoint, so it inherits bin management methods, but its
    bins represent multi-dimensional combinations rather than single values.
    
    The cross tracks:
    - **Crossed coverpoints**: List of constituent coverpoints
    - **Cross bins**: Automatically or manually generated combination bins
    - **Options**: Inherited from CvgScope (at_least, etc.)
    
    Example:
        >>> # Create two coverpoints
        >>> cp_addr = cg.createCoverpoint("cp_addr", src_info, 1, SourceT.SV)
        >>> cp_addr.createBin("low", src_info, 1, 0, "[0:255]")
        >>> cp_addr.createBin("high", src_info, 1, 0, "[256:1023]")
        >>>
        >>> cp_data = cg.createCoverpoint("cp_data", src_info, 1, SourceT.SV)
        >>> cp_data.createBin("zero", src_info, 1, 0, "0")
        >>> cp_data.createBin("nonzero", src_info, 1, 0, "[1:$]")
        >>>
        >>> # Create cross (generates 2×2=4 bins automatically)
        >>> cross = cg.createCross("addr_x_data", src_info, weight=2,
        ...                        source=SourceT.SV, 
        ...                        points_l=[cp_addr, cp_data])
        >>>
        >>> # Query crossed coverpoints
        >>> num = cross.getNumCrossedCoverpoints()  # Returns 2
        >>> cp0 = cross.getIthCrossedCoverpoint(0)  # Returns cp_addr
        
    Note:
        Cross bins are named based on the constituent bin names, typically
        using a separator like "×" or ":". For example: "low×zero", "high×nonzero".
        
    See Also:
        Coverpoint: Base class for bin management
        Covergroup.createCross(): Create cross coverage
        CvgScope: Coverage scope with options
        IntProperty.NUM_CROSSED_CVPS: Number of crossed coverpoints property
        UCIS LRM Section 6.4.3.4 "UCIS_CROSS"
    """
    
    def __init__(self):
        pass
    
    def getNumCrossedCoverpoints(self)->int:
        """Get the number of coverpoints crossed by this cross.
        
        Returns how many coverpoints were crossed to form this cross coverage.
        This is the dimensionality of the cross (e.g., 2 for a 2-way cross).
        
        Returns:
            Number of coverpoints in the cross (≥ 2).
            
        Example:
            >>> cross = cg.createCross("addr_x_data_x_mode", src_info, 1,
            ...                        SourceT.SV, [cp_addr, cp_data, cp_mode])
            >>> num = cross.getNumCrossedCoverpoints()  # Returns 3
            >>> print(f"This is a {num}-way cross")
            
        See Also:
            getIthCrossedCoverpoint(): Get specific crossed coverpoint
            IntProperty.NUM_CROSSED_CVPS: Underlying property
        """
        raise NotImplementedError()
    
    def getIthCrossedCoverpoint(self, index)->'Coverpoint':
        """Get the i-th coverpoint crossed by this cross.
        
        Returns one of the coverpoints that were crossed to form this cross
        coverage, indexed by position in the cross definition.
        
        Args:
            index: Zero-based index of the coverpoint (0 to N-1, where N is
                the number of crossed coverpoints).
                
        Returns:
            Coverpoint object at the specified index.
            
        Example:
            >>> # Iterate all crossed coverpoints
            >>> num = cross.getNumCrossedCoverpoints()
            >>> for i in range(num):
            ...     cp = cross.getIthCrossedCoverpoint(i)
            ...     print(f"Crossed coverpoint {i}: {cp.getName()}")
            
        See Also:
            getNumCrossedCoverpoints(): Get total number of coverpoints
            Covergroup.createCross(): Specify crossed coverpoints
        """
        raise NotImplementedError()
    
    