'''
Created on Mar 22, 2020

@author: ballance
'''
from pyucis import UCIS_COVERPOINT
from pyucis.cover_index import CoverIndex
from pyucis.coverpoint import Coverpoint
from pyucis.mem.mem_cvg_scope import MemCvgScope
from pyucis.source_info import SourceInfo


class MemCoverpoint(MemCvgScope,Coverpoint):
    
    def __init__(self,
                 parent,
                 name : str,
                 srcinfo : SourceInfo,
                 weight : int,
                 source):
        MemCvgScope.__init__(self, parent, name, srcinfo, weight, source, 
                             UCIS_COVERPOINT, 0)
        Coverpoint.__init__(self)
        
    def createBin(
        self, 
        name:str, 
        srcinfo:SourceInfo, 
        at_least:int, 
        count:int, 
        rhs:str)->CoverIndex:
        # TODO:
        return None
#        Coverpoint.createBin(self, name, srcinfo, at_least, count, rhs)
        
        