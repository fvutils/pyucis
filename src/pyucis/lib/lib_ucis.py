'''
Created on Jan 10, 2020

@author: ballance
'''
from pyucis.ucis import UCIS
from pyucis.lib.libucis import _lib, get_ucis_library, get_lib
from pyucis.int_property import IntProperty
from pyucis.file_handle import FileHandle
from pyucis.lib.lib_file_handle import LibFileHandle

class LibUCIS(UCIS):
    
    def __init__(self, file : str=None):
        self.db = get_lib().ucis_Open(file)
        print("LibUCIS: db=" + str(self.db))
        print("LibUCIS: db=" + str(self.db))
        print("LibUCIS: db=" + str(self.db))
        
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
