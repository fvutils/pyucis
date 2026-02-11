
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
from enum import IntEnum, auto

class SourceT(IntEnum):
    """HDL source language type identifiers.
    
    Defines the enumeration of source language types for scopes and objects in
    the UCIS coverage model. The source type indicates which hardware description
    language or verification language was used to define the object.
    
    Source types are used to:
    - Identify the language context of coverage objects
    - Support language-specific coverage semantics
    - Enable cross-language coverage integration
    - Assist tools in language-appropriate formatting
    
    The source type is stored as part of scope metadata and can be queried using
    the SCOPE_SOURCE_TYPE integer property.
    
    See Also:
        IntProperty.SCOPE_SOURCE_TYPE: Property to get/set source type
        Scope.createScope(): Source type is specified during scope creation
        UCIS LRM Section 5.4 "Source Language Types"
    """
    
    VHDL = 0
    """VHDL hardware description language."""
    
    VLOG = auto()
    """Verilog hardware description language."""
    
    SV = auto()
    """SystemVerilog hardware description and verification language."""
    
    SYSTEMC = auto()
    """SystemC transaction-level modeling language."""
    
    PSL_VHDL = auto()
    """PSL (Property Specification Language) assertions in VHDL context."""
    
    PSL_VLOG = auto()
    """PSL (Property Specification Language) assertions in Verilog context."""
    
    PSL_SV = auto()
    """PSL (Property Specification Language) assertions in SystemVerilog context."""
    
    PSL_SYSTEMC = auto()
    """PSL (Property Specification Language) assertions in SystemC context."""
    
    E = auto()
    """e verification language (Specman Elite)."""
    
    VERA = auto()
    """Vera verification language (OpenVera)."""
    
    NONE = auto()
    """Source language is not specified or not applicable."""
    
    OTHER = auto()
    """User-defined or non-standard source language."""
    
    SOURCE_ERROR = auto()
    """Error value indicating invalid source type."""
