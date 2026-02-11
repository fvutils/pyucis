from ucis.file_handle import FileHandle

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

class SourceInfo():
    """Source code location information for UCIS objects.
    
    SourceInfo encapsulates the location in HDL source code where a coverage
    object (scope, cover item, etc.) is defined. This includes the source file,
    line number, and column/token position.
    
    Source information enables:
    - Traceability from coverage data back to source code
    - Source-level coverage visualization in IDEs/editors
    - Navigation from coverage reports to code
    - Debugging and analysis of uncovered items
    
    SourceInfo objects are typically provided when creating scopes, cover items,
    and other UCIS objects. They can be None/NULL if source location is unknown
    or not applicable.
    
    Attributes:
        file (FileHandle): Handle to the source file, or None if not available.
        line (int): Line number in the source file (1-based), or 0 if not applicable.
        token (int): Token/column position on the line (0-based), or 0 for start of line.
        
    Example:
        >>> # Create source location for line 42, column 10 of a file
        >>> fh = db.createFileHandle("counter.sv", "/project/rtl")
        >>> src = SourceInfo(fh, 42, 10)
        >>> # Use when creating coverage objects
        >>> scope = parent.createScope("counter", src, 1, SourceT.SV,
        ...                            ScopeTypeT.INSTANCE, 0)
        
    Note:
        Token/column position interpretation may vary by tool. A value of 0
        typically indicates "start of line" or "not specified".
        
    See Also:
        FileHandle: Source file reference
        Scope.createScope(): Source info used in scope creation
        UCIS LRM Section 8.12 "Coverage Source File Functions"
    """
    
    def __init__(self, file : FileHandle, line : int, token : int):
        """Create a source location reference.
        
        Args:
            file: FileHandle referencing the source file, or None if file
                is not known or not applicable.
            line: Line number in the source file (1-based). Use 0 if line
                number is not known or not applicable.
            token: Token/column position on the line (0-based). Use 0 for
                start of line or if position is not known.
                
        Example:
            >>> # Known file, line, and column
            >>> src = SourceInfo(file_handle, 100, 5)
            >>> # Known file and line only
            >>> src = SourceInfo(file_handle, 100, 0)
            >>> # No source information available
            >>> src = None  # Can pass None to creation methods
        """
        self.file = file
        self.line = line
        self.token = token
        
    
        