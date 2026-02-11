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
from typing import List
from ucis.coverpoint import Coverpoint
from ucis.source_t import SourceT
'''
Created on Dec 22, 2019

@author: ballance
'''

from ucis.cover_type import CoverType
from ucis.cvg_scope import CvgScope
from ucis.int_property import IntProperty
from ucis.scope import Scope
from ucis.source_info import SourceInfo


class Covergroup(CvgScope):
    """SystemVerilog/SystemC covergroup for functional coverage.
    
    Covergroup represents a SystemVerilog/SystemC/e covergroup, which is a
    collection of coverpoints and crosses that measure functional coverage.
    Covergroups can be defined at the module/class level or instantiated
    multiple times within a design.
    
    A covergroup contains:
    - **Coverpoints**: Individual coverage variables with bins
    - **Crosses**: Cross-product coverage of multiple coverpoints
    - **Options**: Configuration like per-instance mode, merge behavior
    
    Covergroups support two modes:
    1. **Type-level**: Single coverage for all instances (merge_instances=True)
    2. **Per-instance**: Separate coverage per instance (per_instance=True)
    
    The scope type is COVERGROUP for covergroup types or COVERINSTANCE for
    covergroup instances.
    
    Attributes:
        Inherited from CvgScope: at_least, auto_bin_max, detect_overlap, 
            strobe, comment
        
    Example:
        >>> # Create covergroup type
        >>> cg = design.createCovergroup("cg_bus_transaction", src_info, 
        ...                              weight=10, source=SourceT.SV)
        >>> cg.setPerInstance(False)  # Type-level coverage
        >>> cg.setMergeInstances(True)  # Merge across instances
        >>>
        >>> # Add coverpoint for address
        >>> cp = cg.createCoverpoint("cp_addr", src_info, weight=1, 
        ...                          source=SourceT.SV)
        >>>
        >>> # Add cross coverage
        >>> cross = cg.createCross("addr_x_data", src_info, weight=1,
        ...                        source=SourceT.SV, points_l=[cp_addr, cp_data])
        
    See Also:
        CvgScope: Base class for coverage scopes
        Coverpoint: Individual coverage variable
        Cross: Cross-product coverage
        ScopeTypeT.COVERGROUP: Scope type for covergroup types
        ScopeTypeT.COVERINSTANCE: Scope type for covergroup instances
        UCIS LRM Section 6.4.3.1 "UCIS_COVERGROUP"
    """
    
    def __init__(self):
        super().__init__()
        # Call set-attr methods to establish defaults
        self.setPerInstance(False)
        self.setMergeInstances(True)
        self.setGetInstCoverage(False)
        # Comment doesn't seem valid on a CvgScope standalone
        self.setComment("")
        pass
    

    def getPerInstance(self)->bool:
        """Query whether this covergroup collects per-instance coverage.
        
        Returns whether coverage is collected separately for each instance
        of this covergroup (per-instance mode) or merged across all instances
        (type-level mode).
        
        Returns:
            True if per-instance coverage is enabled, False for type-level.
            
        Example:
            >>> if cg.getPerInstance():
            ...     print("Per-instance coverage enabled")
            ... else:
            ...     print("Type-level coverage (merged)")
            
        See Also:
            setPerInstance(): Configure per-instance mode
            IntProperty.CVG_PERINSTANCE: Underlying property
        """
        raise NotImplementedError()
    
    def setPerInstance(self, perinst):
        """Configure whether this covergroup collects per-instance coverage.
        
        Sets whether coverage should be collected separately for each instance
        of this covergroup. In per-instance mode, each instantiation gets its
        own coverage data. In type-level mode (default), coverage from all
        instances is merged.
        
        Args:
            perinst: True for per-instance coverage, False for type-level.
            
        Example:
            >>> # Type-level coverage (merge all instances)
            >>> cg.setPerInstance(False)
            >>> cg.setMergeInstances(True)
            >>>
            >>> # Per-instance coverage (track separately)
            >>> cg.setPerInstance(True)
            >>> cg.setMergeInstances(False)
            
        See Also:
            getPerInstance(): Query per-instance mode
            setMergeInstances(): Control instance merging
        """
        raise NotImplementedError()
    
    def getGetInstCoverage(self) -> bool:
        """Query whether instance coverage should be retrieved.
        
        Returns whether the tool should retrieve coverage from individual
        instances when collecting coverage data.
        
        Returns:
            True if instance coverage retrieval is enabled, False otherwise.
            
        See Also:
            setGetInstCoverage(): Configure instance coverage retrieval
        """
        raise NotImplementedError()
    
    def setGetInstCoverage(self, s : bool):
        """Configure whether instance coverage should be retrieved.
        
        Sets whether the tool should retrieve coverage from individual
        instances when collecting coverage data.
        
        Args:
            s: True to enable instance coverage retrieval, False to disable.
            
        See Also:
            getGetInstCoverage(): Query setting
        """
        raise NotImplementedError()
    
    def getMergeInstances(self)->bool:
        """Query whether coverage from multiple instances should be merged.
        
        Returns whether coverage data from multiple instantiations of this
        covergroup should be merged together (type-level) or kept separate
        (per-instance).
        
        Returns:
            True if instances are merged, False if kept separate.
            
        Example:
            >>> if cg.getMergeInstances():
            ...     print("Coverage merged across instances")
            
        See Also:
            setMergeInstances(): Configure merging behavior
            IntProperty.CVG_MERGEINSTANCES: Underlying property
        """
        raise NotImplementedError()
    
    def setMergeInstances(self, m:bool):
        """Configure whether coverage from multiple instances should be merged.
        
        Sets whether coverage data from multiple instantiations of this
        covergroup should be merged together. When True (default), all instances
        contribute to a single set of coverage data. When False, each instance
        maintains separate coverage.
        
        Args:
            m: True to merge instances (type-level), False to keep separate.
            
        Example:
            >>> # Type-level: merge all instances
            >>> cg.setMergeInstances(True)
            >>> cg.setPerInstance(False)
            >>>
            >>> # Per-instance: keep separate
            >>> cg.setMergeInstances(False)
            >>> cg.setPerInstance(True)
            
        See Also:
            getMergeInstances(): Query merge setting
            setPerInstance(): Configure per-instance mode
        """
        raise NotImplementedError()
    
        

    def createCoverpoint(self,
                         name : str,
                         srcinfo : SourceInfo,
                         weight : int,
                         source) -> CoverType:
        """Create a coverpoint within this covergroup.
        
        Creates a new coverpoint (coverage variable with bins) as a child
        of this covergroup. The coverpoint will measure coverage of a single
        variable or expression.
        
        Args:
            name: Coverpoint name (e.g., "cp_addr", "my_coverpoint").
            srcinfo: Source location where coverpoint is defined.
            weight: Relative weight for coverage calculations. Use -1 for no weight.
            source: Source language (e.g., SourceT.SV for SystemVerilog).
            
        Returns:
            Newly created Coverpoint object.
            
        Example:
            >>> cp_addr = cg.createCoverpoint("cp_addr", src_info, 
            ...                               weight=1, source=SourceT.SV)
            >>> # Add bins to coverpoint
            >>> cp_addr.createBin("low", src_info, at_least=1, count=0, 
            ...                   rhs="[0:255]")
            
        See Also:
            Coverpoint: Coverpoint class
            createCross(): Create cross coverage
            UCIS LRM Section 6.4.3.3 "UCIS_COVERPOINT"
        """
        raise NotImplementedError()
    
    def createCross(self, 
                    name : str, 
                    srcinfo : SourceInfo,
                    weight : int,
                    source : SourceT, 
                    points_l : List['Coverpoint']) -> CoverType:
        """Create a cross (cross-product coverage) within this covergroup.
        
        Creates a new cross that measures cross-product coverage of multiple
        coverpoints. A cross automatically generates bins for combinations of
        the crossed coverpoint bins.
        
        Args:
            name: Cross name (e.g., "addr_x_data", "mode_cross").
            srcinfo: Source location where cross is defined.
            weight: Relative weight for coverage calculations. Use -1 for no weight.
            source: Source language (e.g., SourceT.SV for SystemVerilog).
            points_l: List of Coverpoint objects to cross.
            
        Returns:
            Newly created Cross object.
            
        Example:
            >>> # Create two coverpoints
            >>> cp_addr = cg.createCoverpoint("cp_addr", src_info, 1, SourceT.SV)
            >>> cp_data = cg.createCoverpoint("cp_data", src_info, 1, SourceT.SV)
            >>>
            >>> # Create cross of the two coverpoints
            >>> cross = cg.createCross("addr_x_data", src_info, weight=2,
            ...                        source=SourceT.SV, 
            ...                        points_l=[cp_addr, cp_data])
            
        See Also:
            Cross: Cross coverage class
            createCoverpoint(): Create individual coverpoint
            UCIS LRM Section 6.4.3.4 "UCIS_CROSS"
        """
        raise NotImplementedError()
    
    def createCoverInstance(
            self,
            name:str,
            srcinfo:SourceInfo,
            weight:int,
            source)->'Covergroup':
        """Create a covergroup instance under this covergroup type.
        
        Creates a new COVERINSTANCE scope representing a specific instantiation
        of this covergroup type. Used when per-instance coverage is enabled to
        track coverage separately for each instance.
        
        Args:
            name: Instance name identifying this instantiation.
            srcinfo: Source location of the instance.
            weight: Relative weight for this instance.
            source: Source language.
            
        Returns:
            Newly created Covergroup object representing the instance.
            
        Example:
            >>> # Covergroup type (per-instance enabled)
            >>> cg_type = module.createCovergroup("cg_transaction", src_info, 
            ...                                   weight=10, source=SourceT.SV)
            >>> cg_type.setPerInstance(True)
            >>>
            >>> # Create instances
            >>> inst1 = cg_type.createCoverInstance("inst_0", src_info, 1, SourceT.SV)
            >>> inst2 = cg_type.createCoverInstance("inst_1", src_info, 1, SourceT.SV)
            
        See Also:
            setPerInstance(): Enable per-instance coverage
            ScopeTypeT.COVERINSTANCE: Instance scope type
        """
        raise NotImplementedError()
    
    def getIntProperty(
        self, 
        coverindex:int, 
        property:IntProperty)->int:
        if property == IntProperty.CVG_PERINSTANCE:
            return 1 if self.getPerInstance() else 0
        elif property == IntProperty.CVG_MERGEINSTANCES:
            return 1 if self.getMergeInstances() else 0
        else:
            return super().getIntProperty(coverindex, property)

    def setIntProperty(
        self, 
        coverindex:int, 
        property:IntProperty, 
        value:int):
        if property == IntProperty.CVG_PERINSTANCE:
            self.setPerInstance(value==1)
        elif property == IntProperty.CVG_MERGEINSTANCES:
            self.setMergeInstances(value==1)
        else:
            super().setIntProperty(coverindex, property, value)

        
    