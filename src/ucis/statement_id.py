
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
Created on Jan 5, 2020

@author: ballance
'''
from ucis.source_file import SourceFile

class StatementId():
    """Statement identifier with file location.
    
    Identifies a specific statement in source code using file, line number,
    and item (column/token) position. Used for code coverage tracking.
    
    Attributes:
        file (SourceFile): Source file reference.
        line (int): Line number in file (1-based).
        item (int): Item/column position on line.
        
    Example:
        >>> # Create statement identifier
        >>> src_file = SourceFile()
        >>> src_file.setFilename("rtl/core.sv")
        >>> stmt_id = StatementId(src_file, 42, 10)
        >>>
        >>> # Query location
        >>> file = stmt_id.getFile()
        >>> line = stmt_id.getLine()
        >>> item = stmt_id.getItem()
        >>> print(f"Statement at {file.getFilename()}:{line}:{item}")
        
    See Also:
        SourceFile: File reference
        SourceInfo: Source location info
        InstanceCoverage: Uses statement IDs
    """
    
    def __init__(self, file : SourceFile, line : int, item : int):
        """Create statement identifier.
        
        Args:
            file: SourceFile reference.
            line: Line number (1-based).
            item: Item/column position.
        """
        self.file = file
        self.line = line
        self.item = item
        
    def getFile(self) -> SourceFile:
        """Get the source file.
        
        Returns:
            SourceFile object.
        """
        return self.file
    
    def getLine(self) -> int:
        """Get the line number.
        
        Returns:
            Line number (1-based).
        """
        return self.line
    
    def getItem(self) -> int:
        """Get the item/column position.
        
        Returns:
            Item position.
        """
        return self.item
    
    
    