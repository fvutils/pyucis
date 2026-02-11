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

from ucis.func_cov_scope import FuncCovScope
from ucis.int_property import IntProperty
from ucis.str_property import StrProperty


class CvgScope(FuncCovScope):
    """Base class for coverage group scopes (coverpoints and crosses).
    
    CvgScope provides common options and behaviors for functional coverage
    scopes including coverpoints and crosses. It defines the configuration
    options that control how bins are created and how coverage is measured.
    
    CvgScope extends FuncCovScope and adds options specific to SystemVerilog
    covergroup semantics:
    - **at_least**: Minimum hit count for a bin to be considered covered
    - **auto_bin_max**: Maximum number of automatically generated bins
    - **detect_overlap**: Whether to detect overlapping bin ranges
    - **strobe**: Whether to use strobe sampling
    - **comment**: Descriptive comment text
    
    These options typically mirror SystemVerilog covergroup/coverpoint options
    and affect how coverage tools process the coverage data.
    
    Subclasses:
        - Coverpoint: Individual coverage variable with bins
        - Cross: Cross-product coverage of multiple coverpoints
        - Covergroup: Container for coverpoints and crosses (via inheritance)
    
    Example:
        >>> # Configure coverpoint options
        >>> cp.setAtLeast(10)  # Each bin needs 10+ hits
        >>> cp.setAutoBinMax(64)  # Max 64 auto-generated bins
        >>> cp.setDetectOverlap(True)  # Warn on overlapping bins
        >>> cp.setComment("Address bus coverage")
        >>>
        >>> # Query options
        >>> threshold = cp.getAtLeast()
        >>> print(f"Coverage threshold: {threshold}")
        
    See Also:
        Coverpoint: Coverpoint with bins
        Cross: Cross-product coverage
        Covergroup: Covergroup container
        FuncCovScope: Base functional coverage class
        UCIS LRM Section 6.4.3 "Functional Coverage"
    """
    
    def __init__(self):
        super().__init__()
        self.setAtLeast(1)
        self.setAutoBinMax(64)
        self.setDetectOverlap(False)
        self.setStrobe(False)

    def getAtLeast(self)->int:
        """Get the minimum hit count for bins to be considered covered.
        
        Returns the at_least threshold, which specifies how many times a bin
        must be hit before it counts as covered. This is the default goal for
        all bins in this scope unless overridden per-bin.
        
        Returns:
            Minimum hit count threshold (typically 1 or more).
            
        Example:
            >>> threshold = cp.getAtLeast()
            >>> print(f"Bins need {threshold}+ hits to be covered")
            
        See Also:
            setAtLeast(): Set the threshold
            IntProperty.CVG_ATLEAST: Underlying property
        """
        raise NotImplementedError()
    
    def setAtLeast(self, atleast):
        """Set the minimum hit count for bins to be considered covered.
        
        Sets the at_least threshold for all bins in this scope. Bins with
        hit counts below this threshold are not considered covered.
        
        Args:
            atleast: Minimum hit count (typically 1 or more). Use 1 for
                "hit at least once" semantics.
                
        Example:
            >>> # Standard: bins need 1+ hits
            >>> cp.setAtLeast(1)
            >>>
            >>> # Require multiple hits for confidence
            >>> cp.setAtLeast(10)
            
        See Also:
            getAtLeast(): Query current threshold
        """
        raise NotImplementedError()
    
    def getAutoBinMax(self)->int:
        """Get the maximum number of automatically generated bins.
        
        Returns the limit on how many bins can be automatically generated
        for this scope. Applies to auto-generated bins when explicit bins
        are not specified.
        
        Returns:
            Maximum number of auto bins (e.g., 64, 128).
            
        Example:
            >>> max_bins = cp.getAutoBinMax()
            >>> print(f"Auto-bin limit: {max_bins}")
            
        See Also:
            setAutoBinMax(): Set the limit
            IntProperty.CVG_AUTOBINMAX: Underlying property
        """
        raise NotImplementedError()
    
    def setAutoBinMax(self, auto_max):
        """Set the maximum number of automatically generated bins.
        
        Sets the limit on automatic bin generation. When a coverpoint uses
        auto bins, this controls how many bins are created.
        
        Args:
            auto_max: Maximum number of auto bins (e.g., 64, 128).
            
        Example:
            >>> # Allow up to 64 auto bins
            >>> cp.setAutoBinMax(64)
            >>>
            >>> # Increase limit for wide value ranges
            >>> cp.setAutoBinMax(256)
            
        See Also:
            getAutoBinMax(): Query current limit
        """
        raise NotImplementedError()    
    
    def getDetectOverlap(self)->bool:
        """Query whether overlapping bin detection is enabled.
        
        Returns whether the tool should detect and warn about overlapping
        bin ranges in this scope. Overlapping bins can lead to double-counting.
        
        Returns:
            True if overlap detection is enabled, False otherwise.
            
        Example:
            >>> if cp.getDetectOverlap():
            ...     print("Overlap detection enabled")
            
        See Also:
            setDetectOverlap(): Enable/disable overlap detection
            IntProperty.CVG_DETECTOVERLAP: Underlying property
        """
        raise NotImplementedError()
    
    def setDetectOverlap(self, detect:bool):
        """Enable or disable overlapping bin detection.
        
        Controls whether the tool should detect and warn about overlapping
        bin ranges. Useful for catching bin definition errors.
        
        Args:
            detect: True to enable overlap detection, False to disable.
            
        Example:
            >>> # Enable overlap checking
            >>> cp.setDetectOverlap(True)
            
        See Also:
            getDetectOverlap(): Query current setting
        """
        raise NotImplementedError()
    
    def getStrobe(self)->bool:
        """Query whether strobe sampling is enabled.
        
        Returns whether this scope uses strobe (end-of-timestep) sampling
        instead of immediate sampling.
        
        Returns:
            True if strobe sampling is enabled, False for immediate sampling.
            
        Example:
            >>> if cp.getStrobe():
            ...     print("Using strobe sampling")
            
        See Also:
            setStrobe(): Configure sampling mode
            IntProperty.CVG_STROBE: Underlying property
        """
        raise NotImplementedError()
    
    def setStrobe(self, s : bool):
        """Enable or disable strobe sampling.
        
        Controls whether sampling occurs immediately or at end-of-timestep
        (strobe). Strobe sampling can avoid race conditions.
        
        Args:
            s: True for strobe (end-of-timestep) sampling, False for immediate.
            
        Example:
            >>> # Use strobe sampling to avoid races
            >>> cp.setStrobe(True)
            
        See Also:
            getStrobe(): Query sampling mode
        """
        raise NotImplementedError()
    
    def getComment(self)->str:
        """Get the comment text for this scope.
        
        Returns descriptive comment text associated with this coverage scope.
        
        Returns:
            Comment string, or empty string if none.
            
        Example:
            >>> comment = cp.getComment()
            >>> print(f"Description: {comment}")
            
        See Also:
            setComment(): Set comment text
            StrProperty.COMMENT: Underlying property
        """
        raise NotImplementedError()
    
    def setComment(self, c:str):
        """Set the comment text for this scope.
        
        Associates descriptive comment text with this coverage scope for
        documentation purposes.
        
        Args:
            c: Comment string (can be empty).
            
        Example:
            >>> cp.setComment("Measures address bus values")
            
        See Also:
            getComment(): Query comment text
        """
        raise NotImplementedError()
    
    
    def getIntProperty(
        self, 
        coverindex:int, 
        property:IntProperty)->int:
        if property == IntProperty.CVG_ATLEAST:
            return self.getAtLeast()
        elif property == IntProperty.CVG_AUTOBINMAX:
            return self.getAutoBinMax()
        elif property == IntProperty.CVG_DETECTOVERLAP:
            return 1 if self.getDetectOverlap() else 0
        elif property == IntProperty.CVG_STROBE:
            return self.getStrobe()
        else:
            return super().getIntProperty(coverindex, property)
        
    def setIntProperty(
        self, 
        coverindex:int, 
        property:IntProperty, 
        value:int):
        if property == IntProperty.CVG_ATLEAST:
            self.setAtLeast(value)
        elif property == IntProperty.CVG_AUTOBINMAX:
            self.setAutoBinMax(value)
        elif property == IntProperty.CVG_DETECTOVERLAP:
            self.setDetectOverlap(value==1)
        elif property == IntProperty.CVG_STROBE:
            self.setStrobe(value)
        else:
            super().setIntProperty(coverindex, property, value)
            
    def getStringProperty(
        self, 
        coverindex:int, 
        property:StrProperty)->str:
        if property == StrProperty.COMMENT:
            return self.getComment()
        else:
            return super().getStringProperty(coverindex, property)
        
    def setStringProperty(
        self, 
        coverindex:int, 
        property:StrProperty, 
        value:str):
        if property == StrProperty.COMMENT:
            self.setComment(value)
        else:
            super().setStringProperty(coverindex, property, value)

