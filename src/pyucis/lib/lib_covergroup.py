'''
Created on Mar 12, 2020

@author: ballance
'''
from _ctypes import pointer
from pyucis.cover_type import CoverType
from pyucis.covergroup import Covergroup
from pyucis.lib.lib_scope import LibScope
from pyucis.lib.lib_source_info import LibSourceInfo
from pyucis.lib.libucis import get_lib
from pyucis.source_info import SourceInfo
from pyucis import UCIS_VLOG, UCIS_COVERPOINT, UCIS_INT_SCOPE_GOAL,\
    UCIS_INT_CVG_ATLEAST, UCIS_STR_COMMENT


class LibCovergroup(LibScope, Covergroup):
    
    def __init__(self, db, obj):
        super().__init__(db, obj)

    def createCoverpoint(self, 
        name:str, 
        srcinfo:SourceInfo, 
        weight:int, 
        source)->CoverType:
        from pyucis.lib.lib_coverpoint import LibCoverpoint

        cp_s = self.createScope(
            name, 
            srcinfo, 
            weight, 
            source, 
            UCIS_COVERPOINT, 
            0)
        
        print("createCoverpoint: self.obj=" + str(self.obj) + " cp_obj=" + str(cp_s))        
        
        
        cp = LibCoverpoint(self.db, cp_s.obj)
        cp.setIntProperty(-1, UCIS_INT_SCOPE_GOAL, 100)
        cp.setIntProperty(-1, UCIS_INT_CVG_ATLEAST, 1)
        cp.setStringProperty(-1, UCIS_STR_COMMENT, "")
        
        return cp
        