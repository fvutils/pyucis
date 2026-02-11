
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


class StrProperty(IntEnum):
    """String property identifiers for UCIS objects.
    
    Defines property identifiers for accessing string-valued properties on
    UCIS objects via getStringProperty() and setStringProperty() methods.
    
    String properties store textual metadata including:
    - File and scope names
    - Version information (tool, vendor, standard)
    - Test run metadata (command line, date, username, etc.)
    - Design identification (signatures, version IDs)
    - Comments and descriptions
    
    Properties are categorized by scope:
    - Database-level: Version info, file names
    - Scope-level: Names, hierarchical paths, signatures
    - History node: Test metadata, command lines
    - Coverage-specific: Toggle names, expression terms
    
    Example:
        >>> # Access version information
        >>> vendor = db.getStringProperty(-1, StrProperty.VER_VENDOR_ID)
        >>> tool = db.getStringProperty(-1, StrProperty.VER_VENDOR_TOOL)
        >>> print(f"Tool: {vendor} {tool}")
        >>>
        >>> # Set test metadata on history node
        >>> hist.setStringProperty(-1, StrProperty.TEST_NAME, "regression_test_42")
        >>> hist.setStringProperty(-1, StrProperty.TEST_HOSTNAME, "build-server-01")
        >>>
        >>> # Get scope name
        >>> name = scope.getStringProperty(-1, StrProperty.SCOPE_NAME)
        
    See Also:
        Obj.getStringProperty(): Get string property value
        Obj.setStringProperty(): Set string property value
        IntProperty: Integer property identifiers
        RealProperty: Real property identifiers
        UCIS LRM Section 8.16 "Property Management"
    """
    
    # File and database properties
    FILE_NAME = 0
    """UCIS database file or directory name (read-only)."""
    
    # Scope properties
    SCOPE_NAME = auto()
    """Scope name (base name without hierarchy)."""
    
    SCOPE_HIER_NAME = auto()
    """Hierarchical scope name (full path from root)."""
    
    INSTANCE_DU_NAME = auto()
    """Instance's design unit name (DU reference)."""
    
    UNIQUE_ID = auto()
    """Scope or coveritem unique identifier (read-only)."""
    
    # Version and tool information
    VER_STANDARD = auto()
    """Standard name (fixed to "UCIS")."""
    
    VER_STANDARD_VERSION = auto()
    """Version of UCIS standard (e.g., "2011")."""
    
    VER_VENDOR_ID = auto()
    """Vendor identifier (e.g., "CDNS", "MENT", "SNPS")."""
    
    VER_VENDOR_TOOL = auto()
    """Vendor tool name (e.g., "Incisive", "Questa", "VCS")."""
    
    VER_VENDOR_VERSION = auto()
    """Vendor tool version (e.g., "6.5c", "Jun-12-2009")."""
    
    # Generic properties
    GENERIC = auto()
    """Miscellaneous string data."""
    
    # Coverage-specific properties
    ITH_CROSSED_CVP_NAME = auto()
    """Ith coverpoint name of a cross (for cross coverage)."""
    
    COMMENT = auto()
    """Descriptive comment text."""
    
    # History node properties (test run metadata)
    HIST_CMDLINE = auto()
    """Test run command line string."""
    
    HIST_RUNCWD = auto()
    """Test run working directory path."""
    
    HIST_TOOLCATEGORY = auto()
    """Tool category for history node."""
    
    HIST_LOG_NAME = auto()
    """Log file name for history node."""
    
    HIST_PHYS_NAME = auto()
    """Physical name for history node."""
    
    # Test data properties
    TEST_TIMEUNIT = auto()
    """Test run simulation time unit."""
    
    TEST_DATE = auto()
    """Test run date/timestamp."""
    
    TEST_SIMARGS = auto()
    """Test run simulator arguments."""
    
    TEST_USERNAME = auto()
    """Test run user name."""
    
    TEST_NAME = auto()
    """Test run name or identifier."""
    
    TEST_SEED = auto()
    """Test run random seed value."""
    
    TEST_HOSTNAME = auto()
    """Test run hostname."""
    
    TEST_HOSTOS = auto()
    """Test run host operating system."""
    
    # Code coverage properties
    EXPR_TERMS = auto()
    """Input ordered expression term strings delimited by '#'."""
    
    TOGGLE_CANON_NAME = auto()
    """Toggle object canonical name."""
    
    # Design identification
    UNIQUE_ID_ALIAS = auto()
    """Scope or coveritem unique identifier alias."""
    
    DESIGN_VERSION_ID = auto()
    """Version of the design or elaboration identifier."""
    
    DU_SIGNATURE = auto()
    """Design unit signature for unique identification."""
