'''
Created on Jan 5, 2020

@author: ballance
'''
from pyucis.ucis import UCIS

from pyucis.history_node import HistoryNode
from pyucis.source_file import SourceFile
from pyucis.mem.mem_history_node import MemHistoryNode
from pyucis.mem.mem_source_file import MemSourceFile
from pyucis.mem.mem_instance_coverage import MemInstanceCoverage
from pyucis.instance_coverage import InstanceCoverage
from datetime import datetime
import getpass
from pyucis.statement_id import StatementId

class MemUCIS(UCIS):
    
    def __init__(self):
        super().__init__()
        self.ucis_version = "1.0"
        self.writtenBy = getpass.getuser()
        self.writtenTime = int(datetime.timestamp(datetime.now()))
        self.m_history_node_l = []
        self.m_source_file_l = []
        self.m_instance_coverage_l = []
        pass
    
    def getAPIVersion(self)->str:
        return "1.0"
    
    def getWrittenBy(self)->str:
        return self.writtenBy
    
    def setWrittenBy(self, by):
        self.writtenBy = by
    
    def getWrittenTime(self)->int:
        return self.writtenTime
    
    def setWrittenTime(self, time : int):
        self.writtenTime = time
    
    def createFileHandle(self, filename, workdir):
        ret = MemSourceFile(len(self.m_source_file_l), filename)
        self.m_source_file_l.append(ret)
        return ret
    
    def createHistoryNode(self, parent, logicalname, physicalname=None, kind=None):
        ret = MemHistoryNode(parent, logicalname, physicalname, kind)
        self.m_history_node_l.append(ret)
        return ret

    def createCoverInstance(self, name, stmt_id : StatementId):
        ret = MemInstanceCoverage(name, str(len(self.m_instance_coverage_l)), stmt_id)
        self.m_instance_coverage_l.append(ret)
        return ret
        
    def getHistoryNodes(self) -> [HistoryNode]:
        return self.m_history_node_l
    
    def getSourceFiles(self)->[SourceFile]:
        return self.m_source_file_l
    
    def getCoverInstances(self)->[InstanceCoverage]:
        return self.m_instance_coverage_l

    
    