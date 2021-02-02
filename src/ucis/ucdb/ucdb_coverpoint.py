'''
Created on Mar 12, 2020

@author: ballance
'''
from ucis import UCIS_CVGBIN, UCIS_IS_32BIT, UCIS_HAS_GOAL, UCIS_HAS_WEIGHT
from ucis.cover_data import CoverData
from ucis.coverpoint import Coverpoint
from ucis.ucdb.ucdb_scope import UcdbScope
from ucis.source_info import SourceInfo

from ucis.cover_index import CoverIndex
from ucis.ucdb.ucdb_cvg_scope import UcdbCvgScope


class UcdbCoverpoint(UcdbCvgScope, Coverpoint):
    
    def __init__(self, db, obj):
        UcdbCvgScope.__init__(self, db, obj)
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
        