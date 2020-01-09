'''
Created on Jan 8, 2020

@author: ballance
'''
from pyucis.scope import Scope
from pyucis.unimpl_error import UnimplError

class CoverType(Scope):
    
    def __init__(self):
        super().__init__()
        
    def setCoverGoal(self, goal : int):
        raise UnimplError()
    
    def getCoverGoal(self)->int:
        raise UnimplError()
        