'''
Created on Jan 5, 2020

@author: ballance
'''
from pyucis.unimpl_error import UnimplError

class SourceFile():
    
    def __init__(self):
        pass
    
    def getFilename(self) -> str:
        raise UnimplError()
    
    def setFilename(self, filename : str):
        raise UnimplError()