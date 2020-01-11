'''
Created on Dec 22, 2019

@author: ballance
'''
from pyucis.source_info import SourceInfo
from pyucis.unimpl_error import UnimplError
from pyucis.obj import Obj
from pyucis.int_property import IntProperty
from pyucis.scope_type_t import ScopeTypeT
from pyucis.flags_t import FlagsT
from pyucis.source_t import SourceT

class Scope(Obj):
    
    def __init__(self):
        pass
    
    def createScope(self,
                    name : str,
                    srcinfo : SourceInfo,
                    weight : int,
                    source,
                    type,
                    flags):
        raise UnimplError()
    
    def createInstance(self,
                    name : str,
                    fileinfo : SourceInfo,
                    weight : int,
                    source : SourceT,
                    type : ScopeTypeT,
                    du_scope : 'Scope',
                    flags : FlagsT) ->'Scope':
        raise UnimplError()
    
    def createCovergroup(self,
                    name : str,
                    srcinfo : SourceInfo,
                    weight : int,
                    source) -> 'Covergroup':
        raise UnimplError()
    
    def getWeight(self, coverindex):
        return self.getIntProperty(coverindex, IntProperty.COVER_WEIGHT)
    
