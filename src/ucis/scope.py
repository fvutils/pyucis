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
from typing import Iterator
from ucis.cover_index import CoverIndex
from ucis.cover_type_t import CoverTypeT
from ucis.unimpl_error import UnimplError

'''
Created on Dec 22, 2019

@author: ballance
'''

from ucis.source_info import SourceInfo
from ucis.obj import Obj
from ucis.int_property import IntProperty
from ucis.scope_type_t import ScopeTypeT
from ucis.flags_t import FlagsT
from ucis.source_t import SourceT
from ucis.cover_data import CoverData
from ucis.toggle_metric_t import ToggleMetricT
from ucis.toggle_type_t import ToggleTypeT
from ucis.toggle_dir_t import ToggleDirT

class Scope(Obj):
    """Base class for all UCIS scope objects.
    
    A Scope represents a hierarchical container in the UCIS coverage model,
    organizing coverage data and design structure in a tree hierarchy. Scopes
    can contain child scopes (forming the hierarchy) and cover items (leaf-level
    coverage measurements).
    
    The scope hierarchy mirrors both the design hierarchy (modules, instances,
    blocks, functions) and the functional coverage structure (covergroups,
    coverpoints, crosses). Each scope has a unique type (from ScopeTypeT) that
    determines its purpose and allowed operations.
    
    Key scope capabilities:
    - **Hierarchy Management**: Create child scopes, navigate parent/child relationships
    - **Coverage Organization**: Group related cover items under scopes
    - **Metadata Storage**: Source location, weights, goals, flags
    - **Iteration**: Traverse child scopes and cover items
    - **Property Access**: Get/set scope-specific properties
    
    Scopes form the backbone of the UCIS data model. The primary key for scope
    identity is the combination of (name, type) which must be unique among siblings.
    
    Note:
        This is an abstract base class. Concrete implementations include
        InstanceScope, Covergroup, Coverpoint, and others. Use factory methods
        like createScope(), createInstance(), createCovergroup() to create scopes.
        
    Attributes:
        name (str): Local name of this scope (unique within parent)
        type (ScopeTypeT): Scope type identifier
        weight (int): Relative importance for coverage computation (default: 1)
        goal (int): Target coverage percentage (0-100, default: 100)
        source (SourceT): HDL source language type
        flags (FlagsT): Behavior flags (enablement, exclusion, etc.)
        
    See Also:
        UCIS: Root database scope
        UCIS LRM Section 5.1 "Scope Objects" 
        UCIS LRM Section 8.5 "Scope Functions"
    """
    
    def __init__(self):
        self.setGoal(100)

    def createScope(self,
                    name : str,
                    srcinfo : SourceInfo,
                    weight : int,
                    source,
                    type,
                    flags):
        """Create a child scope within this scope.
        
        Creates a new scope as a child of the current scope. The type of scope
        created depends on the 'type' parameter. Scopes form a hierarchical tree
        structure representing the design hierarchy or coverage organization.
        
        The combination of (name, type) forms the primary key and must be unique
        among all children of this scope. Use createInstance() for INSTANCE-type
        scopes, as it provides additional design unit association.
        
        Args:
            name: Unique local name for this scope within its parent. Must not
                contain path separator characters.
            srcinfo: Source file location where scope is defined (file, line, column),
                or None if not applicable or unknown.
            weight: Relative weight for coverage computation. Use 1 for normal
                weight, >1 for higher importance, or -1 to omit weighting.
            source: HDL source language type (SourceT enum: VLOG, VHDL, SV, etc.).
            type: Type of scope to create (ScopeTypeT enum: BLOCK, FUNCTION,
                COVERGROUP, etc.). Determines scope semantics and allowed children.
            flags: Bitwise OR of scope flags (FlagsT) controlling behavior such as
                coverage enablement, exclusion, etc.
                
        Returns:
            Newly created Scope object of the appropriate subclass based on type.
            
        Raises:
            NotImplementedError: If this scope type does not support child scopes.
            ValueError: If name is invalid or (name, type) combination already exists.
            TypeError: If parent scope type doesn't allow this child type.
            
        Example:
            >>> # Create a function scope
            >>> func = parent.createScope(
            ...     "my_function", 
            ...     SourceInfo(file_h, 42, 0),
            ...     1,
            ...     SourceT.SV,
            ...     ScopeTypeT.FUNCTION,
            ...     0)
            
        Note:
            For INSTANCE or COVERINSTANCE scopes, use createInstance() instead,
            which properly associates the instance with its design unit.
            
        See Also:
            createInstance(): Create instance scopes with design unit association
            createCovergroup(): Convenience method for covergroups
            UCIS LRM Section 8.5.2 "ucis_CreateScope"
        """
        raise NotImplementedError()
    
    def createInstance(self,
                    name : str,
                    fileinfo : SourceInfo,
                    weight : int,
                    source : SourceT,
                    type : ScopeTypeT,
                    du_scope : 'Scope',
                    flags : FlagsT) ->'Scope':
        """Create an instance scope with design unit association.
        
        Creates a new instance scope as a child of the current scope, establishing
        a link to its design unit (module/entity definition). Instances represent
        the instantiation of a design unit within the design hierarchy.
        
        The design unit scope (du_scope) contains the template/definition, while
        the instance represents a specific use. This separation enables:
        - Single definition, multiple instantiations
        - Instance-specific vs. design-unit-wide coverage
        - Proper hierarchical naming and navigation
        
        Args:
            name: Unique local name for this instance within its parent.
            fileinfo: Source location of the instantiation statement, or None.
            weight: Relative weight for coverage computation (typically 1).
            source: HDL source language type (SourceT.VLOG, SourceT.VHDL, etc.).
            type: Must be ScopeTypeT.INSTANCE or ScopeTypeT.COVERINSTANCE.
            du_scope: Reference to the design unit scope that this instance
                instantiates. The design unit should have a DU_* scope type
                (DU_MODULE, DU_ARCH, DU_PROGRAM, etc.).
            flags: Bitwise OR of scope flags (FlagsT). Common flags include
                INST_ONCE (single instantiation) and coverage enablement flags.
                
        Returns:
            Newly created instance Scope object.
            
        Raises:
            NotImplementedError: If instances cannot be created under this scope.
            ValueError: If name is invalid or du_scope is not a design unit.
            TypeError: If type is not INSTANCE or COVERINSTANCE.
            
        Example:
            >>> # Create design unit
            >>> du = db.createScope("adder", None, 1, SourceT.SV,
            ...                     ScopeTypeT.DU_MODULE, 0)
            >>> # Create instance of the design unit
            >>> inst = top.createInstance(
            ...     "adder_inst",
            ...     SourceInfo(file_h, 100, 0),
            ...     1,
            ...     SourceT.SV,
            ...     ScopeTypeT.INSTANCE,
            ...     du,
            ...     FlagsT.ENABLED_STMT | FlagsT.ENABLED_BRANCH)
            
        Note:
            The du_scope parameter links instance to definition, enabling
            coverage aggregation across multiple instances of the same module.
            
        See Also:
            createScope(): Create non-instance scopes
            ScopeTypeT.DU_ANY(): Check if scope is a design unit
            UCIS LRM Section 8.5.7 "ucis_CreateInstance"
        """
        raise NotImplementedError()
    
    def createToggle(self,
                    name : str,
                    canonical_name : str,
                    flags : FlagsT,
                    toggle_metric : ToggleMetricT,
                    toggle_type : ToggleTypeT,
                    toggle_dir : ToggleDirT) -> 'Scope':
        """Create a toggle coverage scope for signal transition tracking.
        
        Creates a toggle coverage scope to track signal transitions (0->1, 1->0).
        Toggle coverage measures whether signals change value during simulation,
        detecting stuck-at faults and exercising signal paths.
        
        Args:
            name: Local name for the toggle scope (signal identifier).
            canonical_name: Fully qualified hierarchical name of the signal.
            flags: Bitwise OR of scope flags (FlagsT.ENABLED_TOGGLE typically set).
            toggle_metric: Toggle metric type (ToggleMetricT) specifying what
                transitions are measured (single-bit, vector, etc.).
            toggle_type: Toggle type (ToggleTypeT) indicating signal category
                (register, net, port, etc.).
            toggle_dir: Toggle direction (ToggleDirT) specifying which transitions
                are tracked (UP: 0->1, DOWN: 1->0, BOTH, INTERNAL).
                
        Returns:
            Newly created toggle Scope object.
            
        Raises:
            NotImplementedError: If toggle coverage is not supported.
            ValueError: If parameters are invalid or incompatible.
            
        Example:
            >>> # Create toggle coverage for a signal
            >>> toggle = scope.createToggle(
            ...     "data_valid",
            ...     "/top/dut/data_valid",
            ...     FlagsT.ENABLED_TOGGLE,
            ...     ToggleMetricT.SCALAR,
            ...     ToggleTypeT.REG,
            ...     ToggleDirT.BOTH)
            
        Note:
            Toggle coverage is typically generated automatically by coverage
            tools. This method is used when constructing or modifying databases.
            
        See Also:
            ToggleMetricT: Toggle measurement types
            ToggleTypeT: Signal type classification  
            ToggleDirT: Transition direction
            UCIS LRM Section 6.4 "Toggle Coverage"
        """
        raise NotImplementedError()
    
    def createCovergroup(self,
                    name : str,
                    srcinfo : SourceInfo,
                    weight : int,
                    source) -> 'Covergroup':
        """Create a SystemVerilog covergroup scope.
        
        Convenience method to create a covergroup scope for functional coverage.
        Covergroups contain coverpoints and crosses that define coverage bins
        for tracking design stimulus and state space.
        
        This method creates a scope with type COVERGROUP or COVERINSTANCE depending
        on context. Covergroups can be defined at design unit level (type) or
        instance level (per-instance coverage).
        
        Args:
            name: Unique name for the covergroup within its parent.
            srcinfo: Source location where covergroup is declared (file, line, column),
                or None if not available.
            weight: Relative weight for coverage computation (typically 1).
            source: HDL source language, typically SourceT.SV (SystemVerilog).
                
        Returns:
            Newly created Covergroup scope object.
            
        Raises:
            NotImplementedError: If covergroups cannot be created in this context.
            ValueError: If name is invalid or already exists.
            
        Example:
            >>> # Create a covergroup
            >>> cg = instance.createCovergroup(
            ...     "addr_cg",
            ...     SourceInfo(file_h, 50, 0),
            ...     1,
            ...     SourceT.SV)
            >>> # Add coverpoints to the covergroup
            >>> cp = cg.createCoverpoint("addr", src_info, 1, SourceT.SV)
            
        Note:
            Use Covergroup.setPerInstance() to control whether coverage is
            collected per-instance or aggregated at design unit level.
            
        See Also:
            Covergroup: Covergroup-specific operations
            Coverpoint: Coverpoint creation within covergroups
            UCIS LRM Section 6.3 "Functional Coverage"
        """
        raise NotImplementedError()
    
    def createNextCover(self,
                        name : str,
                        data : CoverData,
                        sourceinfo : SourceInfo) -> CoverIndex:
        """Create a coverage bin (cover item) within this scope.
        
        Adds a new cover item (bin) to this scope's collection of coverage
        measurements. Cover items are leaf nodes that track actual coverage
        data such as hit counts, goals, and weights.
        
        The cover item type is determined by the scope type:
        - COVERPOINT scope: Creates CVGBIN cover items
        - BRANCH scope: Creates BRANCHBIN cover items  
        - TOGGLE scope: Creates TOGGLEBIN cover items
        - etc.
        
        Args:
            name: Name for this cover item (e.g., bin name, branch ID).
            data: Coverage data including goal, weight, hit count (data), and
                limit. The CoverData object encapsulates all measurement values.
            sourceinfo: Source location associated with this cover item, or None.
                For code coverage, this is typically the line being measured.
                
        Returns:
            CoverIndex reference to the newly created cover item. The index
            can be used with property methods to access/modify cover item data.
            
        Raises:
            NotImplementedError: If this scope type doesn't support cover items.
            ValueError: If name is invalid or data is inconsistent.
            
        Example:
            >>> # Create a coverpoint bin
            >>> data = CoverData(goal=1, weight=1, data=0, limit=1)
            >>> idx = coverpoint.createNextCover(
            ...     "bin_low",
            ...     data,
            ...     SourceInfo(file_h, 60, 0))
            >>> # Later, increment the bin
            >>> coverpoint.setIntProperty(idx, IntProperty.COVER_DATA, 5)
            
        Note:
            The term "NextCover" indicates appending to the cover item collection.
            Cover items are indexed sequentially starting from 0.
            
        See Also:
            CoverData: Coverage data structure
            CoverIndex: Cover item reference
            UCIS LRM Section 8.11.1 "ucis_CreateNextCover"
        """
        raise NotImplementedError()

    def createNextTransition(self, from_state_name: str, to_state_name: str,
                             data: 'CoverData' = None,
                             srcinfo: 'SourceInfo' = None) -> CoverIndex:
        """Create an FSM transition cover item between two named states.

        This is the standard API for creating FSM transitions, analogous to
        ucis_CreateNextTransition in the UCIS C API. If the named states do
        not yet exist in this FSM scope they are created automatically.

        Args:
            from_state_name: Name of the source state.
            to_state_name:   Name of the destination state.
            data:            Initial CoverData (FSMBIN type), or None.
            srcinfo:         Source location, or None.

        Returns:
            CoverIndex for the new transition cover item.

        Raises:
            UnimplError: If the scope type does not support FSM transitions.

        See Also:
            UCIS LRM ucis_CreateNextTransition
        """
        raise UnimplError()

    def getWeight(self):
        """Get the weight of this scope.
        
        Retrieves the relative weight used in coverage computation. Weights
        determine the contribution of this scope to parent scope coverage
        percentages. Higher weights make this scope more important.
        
        Returns:
            Integer weight value. Typically 1 for normal importance, >1 for
            higher importance, or -1 if weight is not applicable.
            
        Raises:
            NotImplementedError: If weight is not supported for this scope type.
            
        See Also:
            setWeight(): Modify scope weight
            IntProperty.SCOPE_WEIGHT: Weight property identifier
        """
        raise NotImplementedError()
    
    def setWeight(self, w):
        """Set the weight of this scope.
        
        Modifies the relative weight used in coverage computation. This affects
        how much this scope contributes to its parent's coverage percentage.
        
        Args:
            w: New weight value. Use 1 for normal importance, >1 for higher
                importance, or -1 to indicate no weight.
                
        Raises:
            NotImplementedError: If weight is not supported for this scope type.
            ValueError: If weight value is invalid.
            
        See Also:
            getWeight(): Retrieve current weight
        """
        raise NotImplementedError()
    
    def getGoal(self)->int:
        """Get the coverage goal for this scope.
        
        Retrieves the target coverage percentage (0-100) for this scope.
        Goals define the threshold for considering coverage "complete".
        
        Returns:
            Integer coverage goal as a percentage (0-100). Default is typically 100.
            
        Raises:
            NotImplementedError: If goals are not supported for this scope type.
            
        Example:
            >>> goal = scope.getGoal()
            >>> if goal == 100:
            ...     print("Full coverage required")
            
        See Also:
            setGoal(): Modify coverage goal
            IntProperty.SCOPE_GOAL: Goal property identifier
        """
        raise NotImplementedError()
    
    def setGoal(self,goal)->int:
        """Set the coverage goal for this scope.
        
        Modifies the target coverage percentage (0-100) for this scope.
        Setting a goal below 100 indicates that partial coverage is acceptable.
        
        Args:
            goal: Target coverage percentage (0-100).
                
        Returns:
            The goal value that was set.
            
        Raises:
            NotImplementedError: If goals are not supported for this scope type.
            ValueError: If goal is not in range 0-100.
            
        Example:
            >>> scope.setGoal(95)  # 95% coverage is sufficient
            
        See Also:
            getGoal(): Retrieve current goal
        """
        raise NotImplementedError()
    
    def getFlags(self)->FlagsT:
        """Get the flags for this scope.
        
        Retrieves the bitwise flags that control scope behavior. Flags indicate
        enablement of coverage types, exclusion status, and other properties.
        
        Returns:
            FlagsT bitwise flags. Test individual flags using bitwise AND.
            
        Raises:
            NotImplementedError: If flags are not supported for this scope type.
            
        Example:
            >>> flags = scope.getFlags()
            >>> if flags & FlagsT.ENABLED_STMT:
            ...     print("Statement coverage enabled")
            >>> if flags & FlagsT.SCOPE_EXCLUDED:
            ...     print("Scope is excluded from coverage")
            
        See Also:
            FlagsT: Flag definitions
            UCIS LRM Section 8.5.21 "ucis_GetScopeFlags"
        """
        raise NotImplementedError()
    
    def getScopeType(self)->ScopeTypeT:
        """Get the type of this scope.
        
        Retrieves the scope type which determines the scope's semantics and
        allowed operations. The type is one of the ScopeTypeT enum values.
        
        Returns:
            ScopeTypeT enum value indicating scope type (INSTANCE, COVERGROUP,
            FUNCTION, TOGGLE, etc.).
            
        Raises:
            NotImplementedError: If scope type cannot be determined.
            
        Example:
            >>> scope_type = scope.getScopeType()
            >>> if scope_type == ScopeTypeT.COVERGROUP:
            ...     print("This is a covergroup")
            >>> if ScopeTypeT.DU_ANY(scope_type):
            ...     print("This is a design unit")
            
        See Also:
            ScopeTypeT: Scope type enumeration
            UCIS LRM Section 8.5.24 "ucis_GetScopeType"
        """
        raise NotImplementedError()
    
    def getScopeName(self)->str:
        """Get the local name of this scope.
        
        Retrieves the local name (not the full hierarchical path) of this scope.
        The name is unique among siblings with the same type.
        
        Returns:
            String local name of the scope.
            
        Raises:
            NotImplementedError: If name cannot be retrieved.
            
        Example:
            >>> name = scope.getScopeName()
            >>> print(f"Scope name: {name}")
            
        Note:
            To get the full hierarchical path, use the path separator and
            traverse parents, or use database path methods if available.
            
        See Also:
            UCIS LRM Section 8.5.27 "ucis_GetScopeName"
        """
        raise NotImplementedError()
    
    def getSourceInfo(self)->SourceInfo:
        """Get the source location information for this scope.
        
        Retrieves the source file, line number, and column where this scope
        is defined in the HDL source code.
        
        Returns:
            SourceInfo object containing file handle, line, and column, or
            None if source location is not available.
            
        Raises:
            NotImplementedError: If source info is not supported.
            
        Example:
            >>> src = scope.getSourceInfo()
            >>> if src:
            ...     print(f"Defined at line {src.line}")
            
        See Also:
            SourceInfo: Source location data structure
            UCIS LRM Section 8.5.23 "ucis_GetScopeSourceInfo"
        """
        raise NotImplementedError()
    
    def scopes(self, mask : ScopeTypeT) -> Iterator['Scope']:
        """Iterate over child scopes of this scope.
        
        Returns an iterator over immediate child scopes, optionally filtered
        by scope type. This enables hierarchical traversal of the scope tree.
        
        Args:
            mask: Scope type mask (ScopeTypeT) to filter results. Only scopes
                whose type matches the mask are returned. Use ScopeTypeT.ALL
                to iterate all children.
                
        Yields:
            Scope objects that are children of this scope and match the type mask.
            
        Raises:
            NotImplementedError: If iteration is not supported.
            
        Example:
            >>> # Iterate all child scopes
            >>> for child in scope.scopes(ScopeTypeT.ALL):
            ...     print(f"Child: {child.getScopeName()}")
            >>> 
            >>> # Iterate only covergroups
            >>> for cg in scope.scopes(ScopeTypeT.COVERGROUP):
            ...     print(f"Covergroup: {cg.getScopeName()}")
            
        See Also:
            coverItems(): Iterate cover items within this scope
            UCIS LRM Section 8.6.1 "ucis_ScopeIterate"
        """
        raise NotImplementedError()
    
    def coverItems(self, mask : CoverTypeT)-> Iterator['CoverIndex']:
        """Iterate over cover items (bins) in this scope.
        
        Returns an iterator over cover items contained in this scope, optionally
        filtered by coverage type. Cover items are the leaf-level measurements.
        
        Args:
            mask: Coverage type mask (CoverTypeT) to filter results. Only cover
                items whose type matches the mask are returned. Use appropriate
                mask for the scope type (e.g., CoverTypeT.CVGBIN for coverpoints).
                
        Yields:
            CoverIndex references to cover items in this scope that match the
            type mask. Use the index with property methods to access cover data.
            
        Raises:
            NotImplementedError: If cover item iteration is not supported.
            
        Example:
            >>> # Iterate all bins in a coverpoint
            >>> for idx in coverpoint.coverItems(CoverTypeT.CVGBIN):
            ...     name = coverpoint.getStringProperty(idx, StrProperty.NAME)
            ...     count = coverpoint.getIntProperty(idx, IntProperty.COVER_DATA)
            ...     print(f"Bin {name}: {count} hits")
            
        See Also:
            scopes(): Iterate child scopes
            createNextCover(): Create cover items
            UCIS LRM Section 8.7.1 "ucis_CoverIterate"
        """
        raise NotImplementedError()
    
    def getIntProperty(
        self, 
        coverindex:int, 
        property:IntProperty)-> int:
        """Get an integer property value from this scope or a cover item.
        
        Overrides Obj.getIntProperty() to provide scope-specific property handling.
        Automatically maps SCOPE_GOAL to the goal accessor method for convenience.
        
        Args:
            coverindex: Index of cover item, or -1 for scope-level properties.
            property: Integer property identifier (IntProperty enum).
            
        Returns:
            Integer value of the requested property.
            
        Raises:
            NotImplementedError: If property is not supported.
            
        Example:
            >>> # Get scope goal using property interface
            >>> goal = scope.getIntProperty(-1, IntProperty.SCOPE_GOAL)
            >>> # Get weight of first cover item
            >>> weight = scope.getIntProperty(0, IntProperty.COVER_WEIGHT)
            
        See Also:
            Obj.getIntProperty(): Base implementation
            getGoal(): Direct goal accessor
        """
        if property == IntProperty.SCOPE_GOAL:
            return self.getGoal()
        else:
            return super().getIntProperty(coverindex, property)
        
    def setIntProperty(
        self, 
        coverindex:int, 
        property:IntProperty, 
        value:int):
        """Set an integer property value on this scope or a cover item.
        
        Overrides Obj.setIntProperty() to provide scope-specific property handling.
        Automatically maps SCOPE_GOAL to the goal mutator method for convenience.
        
        Args:
            coverindex: Index of cover item, or -1 for scope-level properties.
            property: Integer property identifier (IntProperty enum).
            value: New integer value for the property.
            
        Raises:
            NotImplementedError: If property is not supported or read-only.
            
        Example:
            >>> # Set scope goal using property interface
            >>> scope.setIntProperty(-1, IntProperty.SCOPE_GOAL, 95)
            >>> # Set weight of first cover item
            >>> scope.setIntProperty(0, IntProperty.COVER_WEIGHT, 10)
            
        See Also:
            Obj.setIntProperty(): Base implementation
            setGoal(): Direct goal mutator
        """
        if property == IntProperty.SCOPE_GOAL:
            return self.setGoal(value)
        else:
            super().setIntProperty(coverindex, property, value)
            
    
