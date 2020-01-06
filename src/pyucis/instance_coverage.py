'''
Created on Jan 5, 2020

@author: ballance
'''
from pyucis.name_value import NameValue
from pyucis.unimpl_error import UnimplError
from pyucis.statement_id import StatementId

class InstanceCoverage():
    
    def __init__(self):
        pass
    
    
    def getDesignParameters(self) -> [NameValue]:
        raise UnimplError()
    
    def addDesignParameter(self, p : NameValue):
        raise UnimplError()
    
    def getId(self) -> StatementId:
        raise UnimplError()
    
    def getName(self) -> str:
        raise UnimplError()
    
    def getKey(self) -> str:
        raise UnimplError()
    
    