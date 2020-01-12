'''
Created on Jan 12, 2020

@author: ballance
'''
from pyucis.mem.mem_scope import MemScope
from pyucis.covergroup import Covergroup
from pyucis.mem.mem_cvg_scope import MemCvgScope

class MemCovergroup(MemCvgScope,Covergroup):
    
    def __init__(self,
                 parent,
                 name,
                 srcinfo,
                 weight,
                 source,
                 type,
                 flags):
        super().__init__(parent, name, srcinfo, weight, source, type, flags)
        self.m_per_instance = True
        self.m_merge_instances = True
        
    def getPerInstance(self)->bool:
        return self.m_per_instance
    
    def setPerInstance(self, perinst):
        self.m_per_instance = perinst
    
    def getMergeInstances(self)->bool:
        return self.m_merge_instances
    
    def setMergeInstances(self, m:bool):
        self.m_merge_instances = m