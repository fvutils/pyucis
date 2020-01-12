'''
Created on Jan 12, 2020

@author: ballance
'''
from pyucis.mem.mem_scope import MemScope
from pyucis.source_info import SourceInfo
from pyucis.flags_t import FlagsT
from pyucis.source_t import SourceT

class MemInstanceScope(MemScope):
    
    def __init__(
            self,
            parent : 'MemInstanceScope',
            name : str,
            fileinfo : SourceInfo,
            weight : int,
            source : SourceT,
            du_scope : 'MemScope',
            flags : FlagsT
            ):
        super().__init(parent, name, fileinfo, weight, source, flags)
        self.m_du_scope = du_scope
