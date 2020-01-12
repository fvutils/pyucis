'''
Created on Jan 12, 2020

@author: ballance
'''
from pyucis.du_scope import DUScope
from pyucis.flags_t import FlagsT
from pyucis.mem.mem_scope import MemScope
from pyucis.scope_type_t import ScopeTypeT
from pyucis.source_info import SourceInfo
from pyucis.source_t import SourceT
from pyucis.unimpl_error import UnimplError


class MemDUScope(MemScope, DUScope):
    
    def __init__(self,
                 parent : 'MemScope',
                 name : str,
                 srcinfo : SourceInfo,
                 weight : int,
                 source : SourceT,
                 type :ScopeTypeT,
                 flags : FlagsT):
        super().__init__(parent, name, srcinfo, weight, source, type, flags)
        self.m_du_signature = None
        
    def getSignature(self):
        return self.m_du_signature
    
    def setSignature(self, sig):
        self.m_du_signature = sig
        
    def createScope(self,
                name : str,
                srcinfo : SourceInfo,
                weight : int,
                source : SourceT,
                type : ScopeTypeT,
                flags : FlagsT):
        # Creates a type scope and associates source information with it
        if ScopeTypeT.DU_ANY(type):
            ret = MemDUScope(self, name, srcinfo, weight,
                              source, type, flags)
            self.add_child(ret)
        else:
            raise UnimplError()