'''
Created on Dec 22, 2019

@author: ballance
'''
from pyucis.source_info import SourceInfo
from pyucis.unimpl_error import UnimplError
from pyucis.obj import Obj
from pyucis.int_property import IntProperty

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
    
    def createCovergroup(self,
                    name : str,
                    srcinfo : SourceInfo,
                    weight : int,
                    source) -> 'Covergroup':
        raise UnimplError()
    
    def getWeight(self, coverindex):
        return self.getIntProperty(coverindex, IntProperty.COVER_WEIGHT)
    
