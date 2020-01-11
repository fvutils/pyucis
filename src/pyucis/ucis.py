'''
Created on Dec 22, 2019

@author: ballance
'''
from pyucis.unimpl_error import UnimplError
from pyucis.scope import Scope
from pyucis.history_node import HistoryNode
from pyucis.source_file import SourceFile
from pyucis.instance_coverage import InstanceCoverage
from pyucis.statement_id import StatementId
from pyucis.int_property import IntProperty
from pyucis.file_handle import FileHandle

class UCIS(Scope):
    
    def __init__(self):
        pass
    
    def getIntProperty(
            self, 
            coverindex : int,
            property : IntProperty
            )->int:
        if property == IntProperty.IS_MODIFIED:
            return 1 if self.isModified() else 0
        elif property == IntProperty.MODIFIED_SINCE_SIM:
            return 1 if self.modifiedSinceSim() else 0
        elif property == IntProperty.NUM_TESTS:
            return self.getNumTests()
        else:
            return super().getIntProperty(coverindex, property)
    
    def setIntProperty(
            self,
            coverindex : int,
            property : IntProperty,
            value : int):
        super().setIntProperty(coverindex, property, value)
        
    def isModified(self):
        raise UnimplError()
    
    def modifiedSinceSim(self):
        raise UnimplError()
    
    def getNumTests(self):
        raise UnimplError()
    
    def getAPIVersion(self) -> str:
        raise UnimplError()
    
    def getWrittenBy(self)->str:
        raise UnimplError()
    
    def setWrittenBy(self, by : str):
        raise UnimplError()

    def getWrittenTime(self)->int:
        raise UnimplError()
    
    def setWrittenTime(self, time : int):
        raise UnimplError()
    
    def getDBVersion(self):
        raise UnimplError()
    
    def getPathSeparator(self):
        raise UnimplError()

    def setPathSeparator(self):
        raise UnimplError()
    
    def createFileHandle(self, filename, workdir)->FileHandle:
        raise UnimplError()
    
    def createHistoryNode(self, parent, logicalname, physicalname, kind):
        raise UnimplError()
    
    def createCoverInstance(self, name, stmt_id : StatementId):
        raise UnimplError()
    
    def getHistoryNodes(self) -> [HistoryNode]:
        raise UnimplError()
    
    def getSourceFiles(self) -> [SourceFile]:
        raise UnimplError()
    
    def getCoverInstances(self) -> [InstanceCoverage]:
        raise UnimplError()
    
    def write(self, file, scope=None, recurse=True, covertype=-1):
        raise UnimplError()

    def close(self):
        """Close the database and commit changes to backing storage"""
        raise UnimplError()
