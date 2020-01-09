'''
Created on Jan 8, 2020

@author: ballance
'''
from pyucis import IntProperty, RealProperty, StringProperty, HandleProperty
from pyucis.unimpl_error import UnimplError
from pyucis.scope import Scope

class Obj():
    
    def __init__(self):
        pass
    
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
            property : StringProperty) -> str:
        raise UnimplError()
    
    def setStringProperty(
            self,
            coverindex : int,
            property : StringProperty,
            value : str):
        raise UnimplError()
        
    def getHandleProperty(
            self,
            coverindex : int,
            property : HandleProperty):
        raise UnimplError()
    
    def setHandleProperty(
            self,
            coverindex : int,
            property : HandleProperty,
            value : Scope):
        raise UnimplError()
