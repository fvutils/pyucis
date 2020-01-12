'''
Created on Mar 12, 2020

@author: ballance
'''
from pyucis import UCIS_CVGBIN, UCIS_IS_32BIT, UCIS_HAS_GOAL, UCIS_HAS_WEIGHT
from pyucis.cover_data import CoverData
from pyucis.coverpoint import Coverpoint
from pyucis.lib.lib_scope import LibScope
from pyucis.source_info import SourceInfo

from pyucis.cover_index import CoverIndex
from pyucis.lib.lib_cvg_scope import LibCvgScope


class LibCoverpoint(LibCvgScope, Coverpoint):
    
    def __init__(self, db, obj):
        LibCvgScope.__init__(self, db, obj)
        Coverpoint.__init__(self)
        
    def createBin(
        self, 
        name:str, 
        srcinfo:SourceInfo, 
        at_least:int, 
        count:int,
        binrhs) -> CoverIndex:
        coverdata = CoverData(
            UCIS_CVGBIN,
            (UCIS_IS_32BIT|UCIS_HAS_GOAL|UCIS_HAS_WEIGHT))
        coverdata.data = count
        coverdata.at_least = at_least
        coverdata.goal = 1
        # TODO: bring weight in via API?
        coverdata.weight = 1
        
        index = self.createNextCover(
            name, 
            coverdata,
            srcinfo)
        
        return index
        