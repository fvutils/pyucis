
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
Created on Jan 9, 2020

@author: ballance
'''
from enum import IntEnum, auto


class IntProperty(IntEnum):
    """Integer property identifiers for UCIS objects.
    
    Defines the enumeration of integer-valued properties that can be retrieved
    or set on UCIS objects using getIntProperty() and setIntProperty(). These
    properties provide access to numeric attributes such as weights, goals, counts,
    flags, and configuration options.
    
    Properties apply to different object types (scopes, cover items, tests) and
    some are read-only while others can be modified. The coverindex parameter in
    property methods determines whether the property applies to a scope (-1) or
    a specific cover item (>= 0).
    
    See Also:
        Obj.getIntProperty(): Retrieve integer property values
        Obj.setIntProperty(): Modify integer property values
        UCIS LRM Section 8.3.5 "ucis_GetIntProperty"
    """
    
    # Database-level properties (read-only)
    IS_MODIFIED = 0  # Modified since opening stored UCISDB (In-memory and read only)
    """Database has been modified since opening. Read-only."""
    
    MODIFIED_SINCE_SIM = auto()  # Modified since end of simulation run (In-memory and read only)
    """Database has been modified since simulation. Read-only."""
    
    SUPPRESS_MODIFIED = auto()  # Suppress the modification flag
    """Suppress modification tracking. See UCIS_INT_SUPPRESS_MODIFIED."""
    
    NUM_TESTS = auto()  # Number of test history nodes (UCIS_HISTORYNODE_TEST) in UCISDB
    """Number of test history nodes in the database. Read-only."""
    
    # Scope-level properties
    SCOPE_WEIGHT = auto()  # Scope weight
    """Weight of the scope for coverage computation (default: 1)."""
    
    SCOPE_GOAL = auto()  # Scope goal
    """Coverage goal percentage for the scope (0-100)."""
    
    SCOPE_SOURCE_TYPE = auto()  # Scope source type (ucisSourceT)
    """HDL source language type (SourceT enum value)."""
    
    NUM_CROSSED_CVPS = auto()  # Number of coverpoints in a cross (read only)
    """Number of coverpoints crossed in a cross coverage. Read-only."""
    
    SCOPE_IS_UNDER_DU = auto()  # Scope is underneath design unit scope (read only)
    """True (1) if scope is under a design unit scope. Read-only."""
    
    SCOPE_IS_UNDER_COVERINSTANCE = auto()  # Scope is underneath covergroup instance (read only)
    """True (1) if scope is under a covergroup instance. Read-only."""
    
    SCOPE_NUM_COVERITEMS = auto()  # Number of coveritems underneath scope (read only)
    """Total number of cover items in this scope. Read-only."""
    
    SCOPE_NUM_EXPR_TERMS = auto()  # Number of input ordered expr term strings delimited by '#'
    """Number of expression terms in a complex expression."""
    
    # Toggle coverage properties
    TOGGLE_TYPE = auto()  # Toggle type (ucisToggleTypeT)
    """Toggle coverage type identifier."""
    
    TOGGLE_DIR = auto()  # Toggle direction (ucisToggleDirT)
    """Toggle direction (up, down, both)."""
    
    TOGGLE_COVERED = auto()  # Toggle object is covered
    """True (1) if toggle is covered."""
    
    TOGGLE_METRIC = auto()  # Toggle metric type (ToggleMetricT)
    """Toggle metric type. See UCIS_INT_TOGGLE_METRIC and ToggleMetricT."""
    
    # Branch coverage properties
    BRANCH_HAS_ELSE = auto()  # Branch has an 'else' coveritem
    """True (1) if branch has an else clause."""
    
    BRANCH_ISCASE = auto()  # Branch represents 'case' statement
    """True (1) if branch represents a case statement."""
    
    # Cover item properties
    COVER_GOAL = auto()  # Coveritem goal
    """Coverage goal for this cover item."""
    
    COVER_LIMIT = auto()  # Coverage count limit for coveritem
    """Maximum count limit for coverage saturation."""
    
    COVER_WEIGHT = auto()  # Coveritem weight
    """Weight of this cover item for coverage computation."""
    
    # Test properties
    TEST_STATUS = auto()  # Test run status (ucisTestStatusT)
    """Test execution status (TestStatusT enum value)."""
    
    TEST_COMPULSORY = auto()  # Test run is compulsory
    """True (1) if test is mandatory for coverage closure."""
    
    # Statement coverage properties
    STMT_INDEX = auto()  # Index or number of statement on a line
    """Statement index for statements on the same source line."""
    
    BRANCH_COUNT = auto()  # Total branch execution count
    """Total execution count for branch."""
    
    # FSM coverage properties
    FSM_STATEVAL = auto()  # FSM state value
    """Numeric value representing FSM state."""
    
    # Covergroup option properties (SystemVerilog)
    CVG_ATLEAST = auto()  # Covergroup at_least option
    """SystemVerilog covergroup at_least option value."""
    
    CVG_AUTOBINMAX = auto()  # Covergroup auto_bin_max option
    """SystemVerilog covergroup auto_bin_max option value."""
    
    CVG_DETECTOVERLAP = auto()  # Covergroup detect_overlap option
    """SystemVerilog covergroup detect_overlap option value."""
    
    CVG_NUMPRINTMISSING = auto()  # Covergroup cross_num_print_missing option
    """SystemVerilog cross_num_print_missing option value."""
    
    CVG_STROBE = auto()  # Covergroup strobe option
    """SystemVerilog covergroup strobe option value."""
    
    CVG_PERINSTANCE = auto()  # Covergroup per_instance option
    """True (1) if covergroup uses per-instance coverage."""
    
    CVG_GETINSTCOV = auto()  # Covergroup get_inst_coverage option
    """True (1) if instance coverage is collected."""
    
    CVG_MERGEINSTANCES = auto()  # Covergroup merge_instances option
    """True (1) if instances should be merged during coverage merge."""
    
    
    
    
    