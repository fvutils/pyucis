'''
Created on Dec 22, 2019

@author: ballance
'''
from pyucis.scope import Scope
from pyucis.cover_type import CoverType
from pyucis.source_info import SourceInfo
from pyucis.unimpl_error import UnimplError
from pyucis.cvg_scope import CvgScope

class Covergroup(CvgScope):
    
    def __init__(self):
        pass

    def createCoverpoint(self,
                         name : str,
                         srcinfo : SourceInfo,
                         weight : int,
                         source) -> CoverType:
        raise UnimplError()
    
    def createCross(self, 
                    name, 
                    srcinfo : SourceInfo,
                    weight : int,
                    source, 
                    points_l):
        pass
    
    def createCrossByName(self, name, fileinfo, weight, source, point_names_l):
        pass
    