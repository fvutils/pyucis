'''
Created on Mar 12, 2020

@author: ballance
'''
from pyucis.cover_data import CoverData
from pyucis.coverpoint import Coverpoint
from pyucis.lib.lib_scope import LibScope
from pyucis.source_info import SourceInfo
from pyucis import UCIS_CVGBIN, UCIS_IS_32BIT, UCIS_HAS_GOAL, UCIS_HAS_WEIGHT


class LibCoverpoint(LibScope, Coverpoint):
    
    def __init__(self, db, obj):
        super().__init__(db, obj)
        
    def createBin(
        self, 
        name:str, 
        srcinfo:SourceInfo, 
        at_least:int, 
        count:int,
        binrhs):
        coverdata = CoverData(
            UCIS_CVGBIN,
            (UCIS_IS_32BIT|UCIS_HAS_GOAL|UCIS_HAS_WEIGHT))
        coverdata.data = count
        coverdata.at_least = at_least
        # TODO: bring weight in via API?
        coverdata.weight = 1
        
        print("createBin: self.obj=" + str(self.obj))
        
        index = self.createNextCover(
            name, 
            coverdata,
            srcinfo)
        
        return index
        