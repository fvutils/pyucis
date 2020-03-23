'''
Created on Jan 12, 2020

@author: ballance
'''
from pyucis.cover_data import CoverData
from pyucis.cover_item import CoverItem
from pyucis.flags_t import FlagsT
from pyucis.instance_scope import InstanceScope
from pyucis.int_property import IntProperty
from pyucis.mem.mem_cover_item import MemCoverItem
from pyucis.mem.mem_scope import MemScope
from pyucis.scope_type_t import ScopeTypeT
from pyucis.source_info import SourceInfo
from pyucis.source_t import SourceT
from pyucis.toggle_dir_t import ToggleDirT
from pyucis.toggle_metric_t import ToggleMetricT
from pyucis.toggle_type_t import ToggleTypeT
from pyucis.unimpl_error import UnimplError
from pyucis.mem.mem_covergroup import MemCovergroup


class MemInstanceScope(MemScope,InstanceScope):
    
    def __init__(
            self,
            parent : 'MemInstanceScope',
            name : str,
            srcinfo : SourceInfo,
            weight : int,
            source : SourceT,
            type : ScopeTypeT,
            du_scope : 'MemScope',
            flags : FlagsT
            ):
        MemScope.__init__(self, parent, name, srcinfo, weight, source, type, flags)
        InstanceScope.__init__(self)
            
        self.m_du_scope = du_scope
        self.m_cover_item_l = []
        
    def createScope(self, 
        name:str, 
        srcinfo:SourceInfo, 
        weight:int, 
        source : SourceT, 
        type : ScopeTypeT, 
        flags : FlagsT) -> 'Scope':
        if (type & ScopeTypeT.COVERGROUP) != 0:
            ret = MemCovergroup(self, name, srcinfo, weight, source, type, flags)
        else:
            raise UnimplError()

        self.addChild(ret)        
        return ret
            
        
        MemScope.createScope(self, name, srcinfo, weight, source, type, flags)

    def createNextCover(self, 
        name:str, 
        data:CoverData, 
        sourceinfo:SourceInfo)->int:
        ret = len(self.m_cover_item_l)
        ci = MemCoverItem(self, name, data, sourceinfo)
        self.m_cover_item_l.append(ci)
        
        return ret
    
    def createToggle(self,
                    name : str,
                    canonical_name : str,
                    flags : FlagsT,
                    toggle_metric : ToggleMetricT,
                    toggle_type : ToggleTypeT,
                    toggle_dir : ToggleDirT) -> 'Scope':
        from pyucis.mem.mem_toggle_instance_scope import MemToggleInstanceScope
        ret = MemToggleInstanceScope(self, name, canonical_name,
                flags, toggle_metric, toggle_type, toggle_dir)
        self.addChild(ret)
        return ret
    
    def getIthCoverItem(self, i)->CoverItem:
        return self.m_cover_item_l[i]
   
    