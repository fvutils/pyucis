'''
Created on Jan 12, 2020

@author: ballance
'''
from pyucis.scope import Scope
from pyucis.unimpl_error import UnimplError

from pyucis.cover_instance import CoverInstance
from pyucis.cover_item import CoverItem
from pyucis.int_property import IntProperty


class InstanceScope(Scope):
    
    def __init__(self):
        super().__init__()
        
    def getIthCoverItem(self, i)->CoverItem:
        raise UnimplError()
    
    def setIntProperty(
        self, 
        coverindex:int, 
        property:IntProperty, 
        value:int):
        if property == IntProperty.STMT_INDEX:
            ci = self.getIthCoverItem(coverindex)
            ci.setStmtIndex(value)
        else:
            super().setIntProperty(coverindex, property, value)
        
    def getIntProperty(
        self, 
        coverindex:int, 
        property:IntProperty)-> int:
        if property == IntProperty.STMT_INDEX:
            ci = self.getIthCoverItem(coverindex)
            return ci.getStmtIndex()
        else:
            return super().getIntProperty(coverindex, property)