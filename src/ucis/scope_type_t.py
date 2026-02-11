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
Created on Jan 11, 2020

@author: ballance
'''
from enum import IntFlag

class ScopeTypeT(IntFlag):
    """Scope type identifiers for UCIS hierarchical objects.
    
    Defines the enumeration of scope types in the UCIS coverage model. Scopes
    represent hierarchical containers that organize coverage data and design
    structure. Each scope has a unique type that determines its purpose and
    the operations that can be performed on it.
    
    The scope type is one of the two components (along with name) that forms
    the primary key for UCIS objects. Types are implemented as bit flags to
    support efficient type checking and categorization.
    
    Scope types fall into several categories:
    - **HDL Hierarchy**: INSTANCE, PROCESS, BLOCK, FUNCTION, etc.
    - **Design Units**: DU_MODULE, DU_ARCH, DU_PACKAGE, DU_PROGRAM, DU_INTERFACE
    - **Functional Coverage**: COVERGROUP, COVERINSTANCE, COVERPOINT, CROSS
    - **Code Coverage**: TOGGLE, BRANCH, EXPR, COND, BLOCK
    - **Assertions**: ASSERT, COVER
    - **FSM Coverage**: FSM, FSM_STATES, FSM_TRANS
    
    Note:
        Types are mutually exclusive - each scope has exactly one type.
        The IntFlag base enables bitwise operations for type masks.
        
    See Also:
        Scope.getType(): Get the type of a scope
        UCIS LRM Section 5.1.1 "Scopes or hierarchical nodes"
        UCIS LRM Section 5.2 "Primary key design"
    """
    
    # Code coverage scope types
    TOGGLE = 0x0000000000000001
    """Toggle coverage scope tracking signal transitions."""
    
    BRANCH = 0x0000000000000002
    """Branch coverage scope for conditional statements."""
    
    EXPR = 0x0000000000000004
    """Expression coverage scope for complex expressions."""
    
    COND = 0x0000000000000008
    """Condition coverage scope for boolean sub-expressions."""
    
    # HDL hierarchy scope types
    INSTANCE = 0x0000000000000010
    """Design hierarchy instance (module/entity instantiation)."""
    
    PROCESS = 0x0000000000000020
    """HDL process scope (VHDL process, Verilog always block)."""
    
    BLOCK = 0x0000000000000040
    """HDL block scope (VHDL block, Verilog begin-end)."""
    
    FUNCTION = 0x0000000000000080
    """Function scope in HDL code."""
    
    FORKJOIN = 0x0000000000000100
    """Verilog fork-join parallel block."""
    
    GENERATE = 0x0000000000000200
    """HDL generate block (parametric hierarchy)."""
    
    GENERIC = 0x0000000000000400
    """Generic scope type for unclassified scopes."""
    
    CLASS = 0x0000000000000800
    """Object-oriented class type scope (SystemVerilog)."""
    
    # Functional coverage scope types
    COVERGROUP = 0x0000000000001000
    """Covergroup type definition scope (SystemVerilog)."""
    
    COVERINSTANCE = 0x0000000000002000
    """Covergroup instance scope (per-instance coverage)."""
    
    COVERPOINT = 0x0000000000004000
    """Coverpoint scope within a covergroup."""
    
    CROSS = 0x0000000000008000
    """Cross coverage scope crossing multiple coverpoints."""
    
    # Assertion coverage scope types
    COVER = 0x0000000000010000
    """Assertion cover directive (SVA/PSL cover statement)."""
    
    ASSERT = 0x0000000000020000
    """Assertion directive (SVA/PSL assert statement)."""
    
    # Additional HDL scope types
    PROGRAM = 0x0000000000040000
    """SystemVerilog program instance."""
    
    PACKAGE = 0x0000000000080000
    """Package scope (SystemVerilog/VHDL package)."""
    
    TASK = 0x0000000000100000
    """Task scope in HDL code."""
    
    INTERFACE = 0x0000000000200000
    """SystemVerilog interface instance."""
    
    # FSM coverage scope types
    FSM = 0x0000000000400000
    """Finite state machine coverage scope."""
    
    # Design unit scope types (templates for instances)
    DU_MODULE = 0x0000000001000000
    """Design unit for module/entity definition."""
    
    DU_ARCH = 0x0000000002000000
    """Design unit for VHDL architecture."""
    
    DU_PACKAGE = 0x0000000004000000
    """Design unit for package definition."""
    
    DU_PROGRAM = 0x0000000008000000
    """Design unit for SystemVerilog program."""
    
    DU_INTERFACE = 0x0000000010000000
    """Design unit for SystemVerilog interface."""
    
    # Additional FSM coverage scope types
    FSM_STATES = 0x0000000020000000
    """FSM state coverage scope."""
    
    FSM_TRANS = 0x0000000040000000
    """FSM transition coverage scope."""
    
    # Additional coverage scope types
    COVBLOCK = 0x0000000080000000
    """Block coverage scope."""
    
    CVGBINSCOPE = 0x0000000100000000
    """SystemVerilog normal bin scope."""
    
    ILLEGALBINSCOPE = 0x0000000200000000
    """SystemVerilog illegal bin scope."""
    
    IGNOREBINSCOPE = 0x0000000400000000
    """SystemVerilog ignore bin scope."""
    
    # Reserved and utility values
    RESERVEDSCOPE = 0xFF00000000000000
    """Reserved for future use."""
    
    SCOPE_ERROR = 0x0000000000000000
    """Error return code indicating invalid scope type."""
    
    ALL = 0x0000FFFFFFFFFFFF
    """Mask for all valid scope types."""
    
    @staticmethod
    def DU_ANY(t):
        """Check if a scope type is any design unit type.
        
        Helper function to test whether a scope type represents a design
        unit (DU_MODULE, DU_ARCH, DU_PACKAGE, DU_PROGRAM, or DU_INTERFACE).
        
        Args:
            t: Scope type value to test (ScopeTypeT).
            
        Returns:
            True if the type is any design unit type, False otherwise.
            
        Example:
            >>> if ScopeTypeT.DU_ANY(scope.getType()):
            ...     print("This is a design unit")
        """
        return (t & (ScopeTypeT.DU_MODULE|ScopeTypeT.DU_ARCH|ScopeTypeT.DU_PACKAGE|ScopeTypeT.DU_PROGRAM|ScopeTypeT.DU_INTERFACE)) != 0

    