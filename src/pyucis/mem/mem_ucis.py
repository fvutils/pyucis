'''
Created on Jan 5, 2020

@author: ballance
'''
from pyucis.ucis import UCIS

from pyucis.history_node import HistoryNode
from pyucis.source_file import SourceFile
from pyucis.mem.mem_history_node import MemHistoryNode


class MemUCIS(UCIS):
    
    def __init__(self):
        super().__init__()
        self.ucis_version = "1.0"
        self.writtenBy = "TODO"
        self.writtenTime = "TODO"
        self.m_history_node_l = []
        self.m_source_file_l = []
        self.m_instance_coverage_l = []
        pass
    
    def getAPIVersion(self)->str:
        return "1.0"
    
    def createHistoryNode(self, parent, logicalname, physicalname=None, kind=None):
        ret = MemHistoryNode(parent, logicalname, physicalname, kind)
        self.m_history_node_l.append(ret)
        
        return ret
    
    def getHistoryNodes(self) -> [HistoryNode]:
        return self.m_history_node_l
    
    def getSourceFiles(self)->[SourceFile]:
        return self.m_source_file_l

    
    