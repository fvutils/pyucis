'''
Created on Jan 11, 2020

@author: ballance
'''
from _ctypes import byref
from pyucis.scope import Scope
from pyucis.unimpl_error import UnimplError

from pyucis.flags_t import FlagsT
from pyucis.lib.lib_obj import LibObj
from pyucis.lib.lib_source_info import LibSourceInfo
from pyucis.lib.libucis import get_lib
from pyucis.scope_type_t import ScopeTypeT
from pyucis.source_info import SourceInfo
from pyucis.source_t import SourceT


class LibScope(LibObj, Scope):
    
    def __init__(self, db, scope):
        super().__init__(db, scope)
        print("LibScope::init")
        
    def createScope(self, 
        name:str, 
        srcinfo:SourceInfo, 
        weight:int, 
        source, 
        type, 
        flags):
        print("createScope: type=" + str(type))
        srcinfo_p = None if srcinfo is None else byref(LibSourceInfo.ctor(srcinfo))
        sh = get_lib().ucis_CreateScope(
            self.db,
            self.obj,
            name,
            srcinfo_p,
            weight,
            source,
            type,
            flags)
        
        return LibScope(self.db, sh)
    
    def createInstance(self,
                    name : str,
                    fileinfo : SourceInfo,
                    weight : int,
                    source : SourceT,
                    type : ScopeTypeT,
                    du_scope : Scope,
                    flags : FlagsT):
        fileinfo_p = None if fileinfo is None else byref(LibSourceInfo.ctor(fileinfo))
        sh = get_lib().ucis_CreateInstance(
            self.db,
            self.obj,
            name,
            fileinfo_p,
            weight,
            source,
            type,
            du_scope.obj,
            flags)
        
        return LibScope(self.db, sh)
    