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

"""
Memory-based implementation of code coverage scopes.

This module provides MemUCIS implementations for code coverage scope types
(BLOCK, BRANCH, TOGGLE) that can be created under instance scopes.
"""

from ucis.cov_scope import CovScope
from ucis.mem.mem_scope import MemScope
from ucis.scope_type_t import ScopeTypeT
from ucis.source_info import SourceInfo
from ucis.source_t import SourceT
from ucis.flags_t import FlagsT


class MemBlockScope(MemScope, CovScope):
    """Memory-based implementation of block (line) coverage scope.
    
    Represents a code block with line coverage information.
    """
    
    def __init__(self,
                 parent: 'MemScope',
                 name: str,
                 srcinfo: SourceInfo,
                 weight: int,
                 source: SourceT,
                 flags: FlagsT):
        MemScope.__init__(self, parent, name, srcinfo, weight, source, 
                         ScopeTypeT.BLOCK, flags)
        CovScope.__init__(self)


class MemBranchScope(MemScope, CovScope):
    """Memory-based implementation of branch coverage scope.
    
    Represents a branch point with branch coverage information.
    """
    
    def __init__(self,
                 parent: 'MemScope',
                 name: str,
                 srcinfo: SourceInfo,
                 weight: int,
                 source: SourceT,
                 flags: FlagsT):
        MemScope.__init__(self, parent, name, srcinfo, weight, source, 
                         ScopeTypeT.BRANCH, flags)
        CovScope.__init__(self)


class MemToggleScope(MemScope, CovScope):
    """Memory-based implementation of toggle coverage scope.
    
    Represents a signal with toggle coverage information.
    """
    
    def __init__(self,
                 parent: 'MemScope',
                 name: str,
                 srcinfo: SourceInfo,
                 weight: int,
                 source: SourceT,
                 flags: FlagsT):
        MemScope.__init__(self, parent, name, srcinfo, weight, source, 
                         ScopeTypeT.TOGGLE, flags)
        CovScope.__init__(self)
