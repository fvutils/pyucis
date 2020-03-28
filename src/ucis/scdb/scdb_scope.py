'''
Created on Mar 25, 2020

@author: ballance
'''
from ucis.scope import Scope
from ucis.source_info import SourceInfo


class SCDBScope(Scope):
    
    def __init__(self):
        Scope.__init__(self)
        pass
    
    def createScope(self, 
        name:str, 
        srcinfo:SourceInfo, 
        weight:int, 
        source, 
        type, 
        flags)->Scope:
        Scope.createScope(self, name, srcinfo, weight, source, type, flags)
    