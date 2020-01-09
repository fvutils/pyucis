'''
Created on Jan 8, 2020

@author: ballance
'''
from pyucis.mem.mem_obj import MemObj
from pyucis import IntProperty

class MemScope(MemObj):
    
    def __init__(self):
        super().__init__()
        self.m_weight = -1
        self.m_goal = -1
        self.m_source_type = 0
        self.m_is_under_du = 0
        
    def getIntProperty(
            self, 
            coverindex : int,
            property : IntProperty
            )->int:
        if property == IntProperty.SCOPE_WEIGHT:
            return self.m_weight
        elif property == IntProperty.COVER_GOAL:
            return self.m_goal
        elif property == IntProperty.SCOPE_SOURCE_TYPE:
            return self.m_source_type
        elif property == IntProperty.SCOPE_IS_UNDER_DU:
            # TODO: need to detect
            return self.m_is_under_du
        else:
            return super().getIntProperty(coverindex, property)
    
    def setIntProperty(
            self,
            coverindex : int,
            property : IntProperty,
            value : int):
        if property == IntProperty.SCOPE_WEIGHT:
            self.m_weight = value
        elif property == IntProperty.COVER_GOAL:
            self.m_goal = value
        elif property == IntProperty.SCOPE_SOURCE_TYPE:
            self.m_source_type = value
        else:
            super().setIntProperty(coverindex, property, value)    