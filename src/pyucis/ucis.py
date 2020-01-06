'''
Created on Dec 22, 2019

@author: ballance
'''
from pyucis.unimpl_error import UnimplError
from pyucis.scope import Scope
from pyucis.history_node import HistoryNode
from pyucis.source_file import SourceFile

class UCIS(Scope):
    
    def __init__(self):
        pass
    
    def getAPIVersion(self) -> str:
        raise UnimplError()
    
    def getDBVersion(self):
        raise UnimplError()
    
    def getPathSeparator(self):
        raise UnimplError()

    def setPathSeparator(self):
        raise UnimplError()
    
    def createFileHandle(self, filename, workdir):
        raise UnimplError()
    
    def createHistoryNode(self, parent, logicalname, physicalname, kind):
        raise UnimplError()
    
    def getHistoryNodes(self) -> [HistoryNode]:
        raise UnimplError()
    
    def getSourceFiles(self) -> [SourceFile]:
        raise UnimplError()
    
    def write(self, file, scope=None, recurse=True, covertype=-1):
        raise UnimplError()

    def close(self):
        """Close the database and commit changes to backing storage"""
        raise UnimplError()
