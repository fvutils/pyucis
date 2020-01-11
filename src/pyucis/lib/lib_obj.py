'''
Created on Jan 11, 2020

@author: ballance
'''
from pyucis.obj import Obj
from pyucis.int_property import IntProperty
from pyucis.real_property import RealProperty
from pyucis.str_property import StrProperty
from pyucis.handle_property import HandleProperty
from pyucis.lib.libucis import get_lib

class LibObj(Obj):
    
    def __init__(self, db, obj):
        self.db = db
        self.obj = obj

    def getIntProperty(
            self, 
            coverindex : int,
            property : IntProperty
            )->int:
        raise UnimplError()
    
    def setIntProperty(
            self,
            coverindex : int,
            property : IntProperty,
            value : int):
        raise UnimplError()

    def getRealProperty(
            self,
            coverindex : int,
            property : RealProperty) -> float:
        raise UnimplError()
        
    def setRealProperty(
            self,
            coverindex : int,
            property : RealProperty,
            value : float):
        raise UnimplError()

    def getStringProperty(
            self,
            coverindex : int,
            property : StrProperty) -> str:
        raise UnimplError()
    
    def setStringProperty(
            self,
            coverindex : int,
            property : StrProperty,
            value : str):
        obj = self.db if self.obj is None else self.obj
        get_lib().ucis_SetStringProperty(self.db, obj, coverindex, property, value)
        
    def getHandleProperty(
            self,
            coverindex : int,
            property : HandleProperty) -> 'Scope':
        raise UnimplError()
    
    def setHandleProperty(
            self,
            coverindex : int,
            property : HandleProperty,
            value : 'Scope'):
        raise UnimplError()        