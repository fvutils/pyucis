
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

class FileHandle():
    """Handle to a source file in the UCIS database.
    
    FileHandle provides an indirect reference to source file names, enabling
    efficient storage when the same file is referenced by many objects. Each
    unique filename is stored only once in the database, and objects reference
    the file through handles.
    
    File handles associate a filename (which may be relative or absolute) with
    an optional working directory. The UCIS API attempts to resolve relative
    paths to valid file system locations during database access.
    
    File handles are created through the database's createFileHandle() method
    and are typically used as part of SourceInfo objects to indicate where
    coverage objects are defined in HDL source code.
    
    Note:
        File handles are immutable once created. To reference a different file,
        create a new file handle.
        
    See Also:
        UCIS.createFileHandle(): Create file handles
        SourceInfo: Source location data structure
        UCIS LRM Section 8.12 "Coverage Source File Functions"
    """
    
    def __init__(self):
        pass
    
    def getFileName(self)->str:
        """Get the file name associated with this file handle.
        
        Retrieves the file name (path) that this handle references. The API
        attempts to reconstruct a valid file path from the stored filename,
        working directory, and database context.
        
        The resolution algorithm:
        1. If filename is absolute, return it directly
        2. If filename exists as relative path, return the relative path
        3. If fileworkdir + filename exists, return that path
        4. Otherwise, return the original filename
        
        Returns:
            String containing the file path (absolute or relative).
            
        Raises:
            NotImplementedError: If file name retrieval is not supported.
            
        Example:
            >>> fh = db.createFileHandle("test.sv", "/project/rtl")
            >>> path = fh.getFileName()
            >>> print(f"Source file: {path}")
            
        Note:
            The returned path may not exist in the current file system if the
            database was created in a different environment.
            
        See Also:
            UCIS.createFileHandle(): Create file handles with name/workdir
            UCIS LRM Section 8.12.3 "ucis_GetFileName"
        """
        raise NotImplementedError()
    
    