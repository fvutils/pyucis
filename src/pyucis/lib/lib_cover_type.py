'''
Created on Mar 13, 2020

@author: ballance
'''
from pyucis.lib.lib_obj import LibObj
from pyucis.cover_type import CoverType
from pyucis.lib.libucis import get_lib
from pyucis import UCIS_INT_COVER_GOAL, UCIS_INT_COVER_LIMIT,\
    UCIS_INT_COVER_WEIGHT

class LibCoverType(LibObj, CoverType):
    
    def __init__(self, db, obj):
        LibObj.__init__(self, db, obj)
        
    def setCoverGoal(self, goal : int):
        self.setIntProperty(-1, UCIS_INT_COVER_GOAL, goal)
    
    def getCoverGoal(self)->int:
        return self.getIntProperty(-1, UCIS_INT_COVER_GOAL)
    
    def setCoverLimit(self, limit : int):
        self.setIntProperty(-1, UCIS_INT_COVER_LIMIT, limit)
    
    def getCoverLimit(self) -> int:
        return self.getIntProperty(-1, UCIS_INT_COVER_LIMIT)
    
    def setCoverWeight(self, weight : int):
        self.setIntProperty(-1, UCIS_INT_COVER_WEIGHT, weight)
    
    def getCoverWeight(self) -> int:
        return self.getIntProperty(-1, UCIS_INT_COVER_WEIGHT)