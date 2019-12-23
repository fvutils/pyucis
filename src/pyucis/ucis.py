'''
Created on Dec 22, 2019

@author: ballance
'''
from pyucis.unimpl_error import UnimplError
from pyucis.scope import Scope

class UCIS(Scope):
    
    def __init__(self):
        pass
    
    def getAPIVersion(self):
        raise UnimplError()
    
    def getDBVersion(self):
        raise UnimplError()
    
    def getPathSeparator(self):
        raise UnimplError()
    
    def setPathSeparator(self):
        raise UnimplError()
    
    def write(self, file, scope=None, recurse=True, covertype=-1):
        raise UnimplError()

    def close(self):
        """Close the database and commit changes to backing storage"""
        raise UnimplError()
