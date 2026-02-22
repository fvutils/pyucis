'''
Created on Jan 12, 2020

@author: ballance
'''
from typing import List
from ucis.cover_type import CoverType
from ucis.covergroup import Covergroup
from ucis.mem.mem_cvg_scope import MemCvgScope
from ucis.scope_type_t import ScopeTypeT
from ucis.source_t import SourceT
from ucis.source_info import SourceInfo

class MemCovergroup(MemCvgScope,Covergroup):
    
    def __init__(self,
                 parent,
                 name,
                 srcinfo,
                 weight,
                 source):
        MemCvgScope.__init__(self, parent, name, srcinfo, weight, source, 
                         ScopeTypeT.COVERGROUP, 0)
        Covergroup.__init__(self)
        self.at_least = 0
        self.auto_bin_max
        self.m_per_instance = True
        self.m_merge_instances = True
        
    def getAtLeast(self)->int:
        return self.at_least
    
    def setAtLeast(self, atleast):
        self.at_least = atleast
        
    def getAutoBinMax(self)->int:
        return self.auto_bin_max
    
    def setAutoBinMax(self, auto_max):
        self.auto_bin_max = auto_max
        
    def getPerInstance(self)->bool:
        return self.m_per_instance
    
    def setPerInstance(self, perinst):
        self.m_per_instance = perinst
    
    def getMergeInstances(self)->bool:
        return self.m_merge_instances
    
    def setMergeInstances(self, m:bool):
        self.m_merge_instances = m
        
    def createCoverpoint(self, 
        name:str, 
        srcinfo:SourceInfo, 
        weight:int, 
        source)->CoverType:
        from .mem_coverpoint import MemCoverpoint
        ret = MemCoverpoint(self, name, srcinfo, weight, source)
        self.addChild(ret)
        return ret
    
    def createCross(self, 
        name:str, 
        srcinfo:SourceInfo, 
        weight:int, 
        source:SourceT, 
        points_l:List['Coverpoint']):
        from .mem_cross import MemCross
        ret = MemCross(self, name, srcinfo, weight, source, points_l)
        self.addChild(ret)
        return ret
    
    def createCoverInstance(
        self, 
        name:str, 
        srcinfo:SourceInfo, 
        weight:int, 
        source)->'Covergroup':
        ci_obj = self.createScope(
            name, 
            srcinfo, 
            weight, 
            source, 
            ScopeTypeT.COVERINSTANCE,
            0)
        return ci_obj

    def getRealProperty(self, property):
        """Get a real-valued property. CVG_INST_AVERAGE computes average coverage."""
        from ucis.real_property import RealProperty
        if property == RealProperty.CVG_INST_AVERAGE:
            return self._compute_instance_average()
        return None

    def _compute_instance_average(self) -> float:
        """Compute average coverage percentage across all COVERINSTANCE children."""
        instances = [c for c in self.m_children
                     if c.getScopeType() == ScopeTypeT.COVERINSTANCE]
        if not instances:
            return 0.0
        total = 0.0
        for inst in instances:
            total += self._instance_coverage(inst)
        return total / len(instances)

    def _instance_coverage(self, inst) -> float:
        """Rough per-instance coverage: fraction of coverpoints with all bins hit."""
        from ucis.scope_type_t import ScopeTypeT as ST
        from ucis.cover_type_t import CoverTypeT
        coverpoints = [c for c in inst.m_children
                       if c.getScopeType() == ST.COVERPOINT]
        if not coverpoints:
            return 0.0
        covered = 0
        for cp in coverpoints:
            bins = list(cp.coverItems(CoverTypeT.CVGBIN))
            if bins and all(b.getCoverData().data >= max(1, cp.getAtLeast()) for b in bins):
                covered += 1
        return 100.0 * covered / len(coverpoints)

    
    