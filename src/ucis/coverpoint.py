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

#from ucis import UCIS_CVGBIN, UCIS_IS_32BIT, UCIS_HAS_GOAL, UCIS_HAS_WEIGHT
from ucis.cover_type_t import CoverTypeT
from ucis.cover_flags_t import CoverFlagsT
from ucis.cover_data import CoverData
from ucis.cover_index import CoverIndex
from ucis.cvg_scope import CvgScope
from ucis.source_info import SourceInfo


class Coverpoint(CvgScope):
    """Coverpoint measuring coverage of a single variable or expression.
    
    Coverpoint represents a SystemVerilog/SystemC/e coverpoint, which measures
    coverage of a single variable or expression by dividing its value space
    into discrete bins. Each bin tracks how many times values in that range
    were sampled.
    
    A coverpoint contains:
    - **Bins**: Coverage bins (CVGBIN) representing ranges or specific values
    - **Options**: Configuration inherited from CvgScope (at_least, auto_bin_max, etc.)
    - **Goal**: Optional coverpoint-level coverage goal
    
    Bin types include:
    - Regular bins (CVGBIN): Count hits
    - Ignore bins (IGNOREBIN): Don't count in coverage
    - Illegal bins (ILLEGALBIN): Flag as errors
    
    The coverpoint's coverage percentage is calculated based on how many bins
    have met their goals (at_least threshold).
    
    Example:
        >>> # Create coverpoint for an address bus
        >>> cp = cg.createCoverpoint("cp_addr", src_info, weight=1, 
        ...                          source=SourceT.SV)
        >>> cp.setAtLeast(1)  # Each bin needs 1+ hit
        >>>
        >>> # Add bins for address ranges
        >>> cp.createBin("low", src_info, at_least=1, count=0, 
        ...              rhs="[0:255]", kind=CoverTypeT.CVGBIN)
        >>> cp.createBin("mid", src_info, at_least=1, count=0, 
        ...              rhs="[256:511]", kind=CoverTypeT.CVGBIN)
        >>> cp.createBin("high", src_info, at_least=1, count=0, 
        ...              rhs="[512:1023]", kind=CoverTypeT.CVGBIN)
        >>>
        >>> # Query coverage
        >>> goal = cp.getScopeGoal()
        
    See Also:
        CvgScope: Base class with options (at_least, auto_bin_max, etc.)
        Covergroup: Parent covergroup container
        Cross: Cross-product coverage
        CoverTypeT.CVGBIN: Regular coverage bin type
        UCIS LRM Section 6.4.3.3 "UCIS_COVERPOINT"
    """
    
    def __init__(self):
        super().__init__()
        self.setComment("")

    def getScopeGoal(self) -> int:
        """Get the coverage goal for this coverpoint.
        
        Returns the target coverage percentage or count for this coverpoint
        as a whole. This is separate from individual bin goals.
        
        Returns:
            Coverage goal value (interpretation depends on configuration).
            
        Example:
            >>> goal = cp.getScopeGoal()
            >>> print(f"Coverpoint goal: {goal}")
            
        See Also:
            setScopeGoal(): Set coverpoint goal
            getAtLeast(): Get bin-level threshold
        """
        raise NotImplementedError("getScopeGoal in " + str(type(self)))
    
    def setScopeGoal(self, goal):
        """Set the coverage goal for this coverpoint.
        
        Sets the target coverage percentage or count for this coverpoint
        as a whole.
        
        Args:
            goal: Coverage goal value.
            
        Example:
            >>> cp.setScopeGoal(100)  # 100% coverage goal
            
        See Also:
            getScopeGoal(): Query coverpoint goal
            setAtLeast(): Set bin-level threshold
        """
        raise NotImplementedError("setScopeGoal in " + str(type(self)))
                
    def createBin(
            self,
            name : str,
            srcinfo : SourceInfo,
            at_least : int,
            count : int,
            rhs : str,
            kind = CoverTypeT.CVGBIN) -> CoverIndex:
        """Create a coverage bin within this coverpoint.
        
        Creates a new bin representing a range or set of values for this
        coverpoint. Bins are the coverage items that track hit counts.
        
        Args:
            name: Bin name (e.g., "low", "high", "auto[0]").
            srcinfo: Source location where bin is defined.
            at_least: Threshold count for bin to be considered covered.
            count: Initial hit count (typically 0).
            rhs: Right-hand side expression describing bin range (e.g., "[0:255]").
            kind: Bin type (CVGBIN, IGNOREBIN, ILLEGALBIN, DEFAULTBIN).
                Default is CVGBIN.
                
        Returns:
            CoverIndex reference to the created bin.
            
        Example:
            >>> # Regular coverage bins
            >>> low = cp.createBin("low", src_info, at_least=1, count=0,
            ...                    rhs="[0:255]", kind=CoverTypeT.CVGBIN)
            >>> high = cp.createBin("high", src_info, at_least=1, count=0,
            ...                     rhs="[256:1023]", kind=CoverTypeT.CVGBIN)
            >>>
            >>> # Illegal bin (flags errors)
            >>> illegal = cp.createBin("illegal", src_info, at_least=0, count=0,
            ...                        rhs="[1024:$]", kind=CoverTypeT.ILLEGALBIN)
            
        Note:
            The method automatically sets up CoverData with appropriate flags
            (IS_32BIT, HAS_GOAL, HAS_WEIGHT) and initializes goal=1, weight=1.
            
        See Also:
            CoverIndex: Reference to coverage items
            CoverData: Coverage measurement data
            CoverTypeT.CVGBIN: Regular bin type
            CoverTypeT.IGNOREBIN: Ignored bin type
            CoverTypeT.ILLEGALBIN: Illegal bin type
        """
        coverdata = CoverData(
            kind,
            (CoverFlagsT.IS_32BIT|CoverFlagsT.HAS_GOAL|CoverFlagsT.HAS_WEIGHT))
        coverdata.data = count
        coverdata.at_least = at_least
        coverdata.goal = 1
        # TODO: bring weight in via API?
        coverdata.weight = 1
        
        index = self.createNextCover(
            name, 
            coverdata,
            srcinfo)
        
        return index        
        