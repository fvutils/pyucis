
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
from ucis.cvg_scope import CvgScope

class CvgBinScope(CvgScope):
    """Base class for coverage bin scopes.
    
    CvgBinScope is a specialized coverage scope class used for certain
    types of bins or bin-like structures that need scope-level representation
    rather than being simple cover items.
    
    This class extends CvgScope, inheriting all coverpoint/cross options
    (at_least, auto_bin_max, detect_overlap, etc.), but is used for
    specialized bin-related scopes in the UCIS hierarchy.
    
    Note:
        This is primarily a structural class in the type hierarchy. Most
        coverage bins are represented as cover items (CoverItem) accessed
        via CoverIndex, not as scopes. CvgBinScope is used for special cases
        where bin-like entities need to be scopes.
        
    Example:
        >>> # CvgBinScope is typically not directly instantiated by users
        >>> # It's used internally by the UCIS implementation for specialized
        >>> # bin scope structures
        
    See Also:
        CvgScope: Base coverage scope class
        CoverItem: Regular coverage items (bins)
        CoverIndex: Access to coverage items
        Coverpoint: Coverpoint containing bins
    """
    
    def __init__(self):
        super().__init__()
        