'''
Created on Jan 12, 2020

@author: ballance
'''
from pyucis.obj import Obj
from pyucis.unimpl_error import UnimplError

class CoverItem(Obj):
    
    def __init__(self):
        super().__init__()
        
    def getStmtIndex(self)->int:
        raise UnimplError()
    
    def setStmtIndex(self, i):
        raise UnimplError()
        