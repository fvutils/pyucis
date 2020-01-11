
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
Created on Jan 10, 2020

@author: ballance
'''
from pyucis.ucis import UCIS
from pyucis.lib.libucis import _lib, get_ucis_library, get_lib
from pyucis.int_property import IntProperty
from pyucis.file_handle import FileHandle
from pyucis.lib.lib_file_handle import LibFileHandle
from pyucis.lib.lib_scope import LibScope

class LibUCIS(LibScope,UCIS):
    
    def __init__(self, file : str=None):
        db = get_lib().ucis_Open(file)
        super().__init__(db, None)
        
        
    def isModified(self):
        return get_lib().ucis_GetIntProperty(self.db, -1, IntProperty.IS_MODIFIED) == 1
    
    def modifiedSinceSim(self):
        return get_lib().ucis_GetIntProperty(self.db, -1, IntProperty.MODIFIED_SINCE_SIM) == 1
        
    def getNumTests(self):
        return get_lib().ucis_GetIntProperty(self.db, -1, IntProperty.NUM_TESTS)
    
    def createFileHandle(self, filename, workdir)->FileHandle:
        fh = get_lib().ucis_CreateFileHandle(
            self.db,
            filename,
            workdir)
        
        return LibFileHandle(fh)
        
    
    def createHistoryNode(self, parent, logicalname, physicalname, kind):
        print("--> createHistoryNode")
        print("  db=" + str(self.db))
        print("  parent=" + str(parent))
        print("  logicalname=" + str(logicalname))
        print("  physicalname=" + str(physicalname))
        print("  kind=" + str(kind))
        
        hn = get_lib().ucis_CreateHistoryNode(
            self.db,
            parent,
            logicalname,
            physicalname,
            kind)
        print("hn=" + str(hn))
        print("<-- createHistoryNode")
        
    def write(self, file, scope=None, recurse=True, covertype=-1):
        get_lib().ucis_Write(
            self.db, 
            file,
            scope,
            1 if recurse else 0,
            covertype)
        
    def close(self):
        get_lib().ucis_Close(self.db)
