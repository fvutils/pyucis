
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

class FlagsT(IntFlag):
    """Scope and coverage flags for UCIS objects.
    
    Defines bit flags that modify the behavior and interpretation of scopes and
    coverage objects. Flags can be combined using bitwise OR operations to set
    multiple flags simultaneously.
    
    Flags control various aspects:
    - **Coverage enablement**: Which coverage types are collected
    - **Scope properties**: Exclusion, instantiation behavior
    - **Covergroup options**: Auto-generation, type of coverage
    - **Assertion properties**: Immediate vs. concurrent
    
    Flags are typically set during scope creation and can be queried or modified
    using scope flag methods. Multiple flags can be active simultaneously.
    
    See Also:
        Scope.createScope(): Flags specified during scope creation
        UCIS LRM Section 8.5.19 "ucis_GetScopeFlag"
        UCIS LRM Section 8.5.20 "ucis_SetScopeFlag"
    """
    
    # Instance instantiation flags
    INST_ONCE = 0x00000001
    """Instance is instantiated only once; code coverage stored in instance only."""
    
    # Code coverage enablement flags
    ENABLED_STMT = 0x00000002
    """Statement coverage is collected for this scope."""
    
    ENABLED_BRANCH = 0x00000004
    """Branch coverage is collected for this scope."""
    
    ENABLED_COND = 0x00000008
    """Condition coverage is collected for this scope."""
    
    ENABLED_EXPR = 0x00000010
    """Expression coverage is collected for this scope."""
    
    ENABLED_FSM = 0x00000020
    """FSM (finite state machine) coverage is collected for this scope."""
    
    ENABLED_TOGGLE = 0x00000040
    """Toggle coverage is collected for this scope."""
    
    ENABLED_BLOCK = 0x00800000
    """Block coverage is collected for this scope."""
    
    # Scope hierarchy flags
    SCOPE_UNDER_DU = 0x00000100
    """Scope is located under a design unit scope (read-only property)."""
    
    # Coverage exclusion flags
    SCOPE_EXCLUDED = 0x00000200
    """Scope is excluded from coverage calculations."""
    
    SCOPE_PRAGMA_EXCLUDED = 0x00000400
    """Scope excluded by pragma directive in source code."""
    
    SCOPE_PRAGMA_CLEARED = 0x00000800
    """Pragma exclusion has been cleared/removed."""
    
    # Specialized scope flags
    SCOPE_SPECIALIZED = 0x00001000
    """Scope has specialized coverage semantics."""
    
    # Universal Object Recognition (UOR) flags
    UOR_SAFE_SCOPE = 0x00002000
    """Scope is safe for Universal Object Recognition."""
    
    UOR_SAFE_SCOPE_ALLCOVERS = 0x00004000
    """Scope and all cover items are safe for Universal Object Recognition."""
    
    # Top-level and assertion flags
    IS_TOP_NODE = 0x00010000
    """Scope is a top-level node in the hierarchy."""
    
    IS_IMMEDIATE_ASSERT = 0x00010000
    """Assertion is immediate (not concurrent)."""
    
    # SystemVerilog covergroup type flags
    SCOPE_CVG_AUTO = 0x00010000
    """Covergroup uses auto-generated bins."""
    
    SCOPE_CVG_SCALAR = 0x00020000
    """Coverpoint covers scalar (single-bit) values."""
    
    SCOPE_CVG_VECTOR = 0x00040000
    """Coverpoint covers vector (multi-bit) values."""
    
    SCOPE_CVG_TRANSITION = 0x00080000
    """Coverpoint covers state transitions."""
    
    # Conditional flags
    SCOPE_IFF_EXISTS = 0x00100000
    """Scope has an 'iff' (if and only if) condition."""
    
    # Block coverage flags
    SCOPE_BLOCK_ISBRANCH = 0x01000000
    """Block scope represents a branch decision."""


