
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
from ucis.unimpl_error import UnimplError

class SourceFile():
    """Source file reference.
    
    Represents a source code file in the design. Used by source location
    tracking to reference files containing HDL code.
    
    Example:
        >>> # SourceFile is typically created internally
        >>> # Used in SourceInfo and StatementId
        >>> src_file = SourceFile()
        >>> src_file.setFilename("rtl/core.sv")
        >>> filename = src_file.getFilename()
        
    See Also:
        SourceInfo: Source location with file reference
        StatementId: Statement location with file
        FileHandle: UCIS file handle system
    """
    
    def __init__(self):
        pass
    
    def getFilename(self) -> str:
        """Get the source filename.
        
        Returns:
            Filename string.
            
        Raises:
            UnimplError: Not implemented in base class.
        """
        raise UnimplError()
    
    def setFilename(self, filename : str):
        """Set the source filename.
        
        Args:
            filename: Filename string.
            
        Raises:
            UnimplError: Not implemented in base class.
        """
        raise UnimplError()