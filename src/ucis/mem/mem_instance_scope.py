'''
Created on Jan 12, 2020

@author: ballance
'''
from ucis.cover_data import CoverData
from ucis.cover_item import CoverItem
from ucis.flags_t import FlagsT
from ucis.instance_scope import InstanceScope
from ucis.int_property import IntProperty
from ucis.mem.mem_cover_item import MemCoverItem
from ucis.mem.mem_scope import MemScope
from ucis.scope_type_t import ScopeTypeT
from ucis.source_info import SourceInfo
from ucis.source_t import SourceT
from ucis.toggle_dir_t import ToggleDirT
from ucis.toggle_metric_t import ToggleMetricT
from ucis.toggle_type_t import ToggleTypeT
from ucis.unimpl_error import UnimplError
from ucis.mem.mem_covergroup import MemCovergroup
from ucis.mem.mem_code_scope import MemBlockScope, MemBranchScope, MemToggleScope


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
        
    def getInstanceDu(self) -> 'Scope':
        return self.m_du_scope
        
    def createScope(self, 
        name:str, 
        srcinfo:SourceInfo, 
        weight:int, 
        source : SourceT, 
        type : ScopeTypeT, 
        flags : FlagsT) -> 'Scope':
        if (type & ScopeTypeT.COVERGROUP) != 0:
            ret = MemCovergroup(self, name, srcinfo, weight, source)
        elif (type & ScopeTypeT.BLOCK) != 0:
            ret = MemBlockScope(self, name, srcinfo, weight, source, flags)
        elif (type & ScopeTypeT.BRANCH) != 0:
            ret = MemBranchScope(self, name, srcinfo, weight, source, flags)
        elif (type & ScopeTypeT.TOGGLE) != 0:
            ret = MemToggleScope(self, name, srcinfo, weight, source, flags)
        elif (type & ScopeTypeT.FSM) != 0:
            from ucis.mem.mem_fsm_scope import MemFSMScope
            ret = MemFSMScope(self, name, srcinfo, weight, source, flags)
        else:
            # Generic fallback for other scope types
            ret = MemScope(self, name, srcinfo, weight, source, type, flags)

        self.addChild(ret)        
        return ret

    def createNextCover(self, 
        name:str, 
        data:CoverData, 
        sourceinfo:SourceInfo)->int:
        ret = len(self.m_cover_item_l)
        ci = MemCoverItem(self, name, data, sourceinfo)
        self.m_cover_item_l.append(ci)
        # Also track in parent's m_cover_items for coverItems() iteration
        from ucis.mem.mem_cover_index import MemCoverIndex
        self.m_cover_items.append(MemCoverIndex(name, data, sourceinfo))
        return ret
    
    def createToggle(self,
                    name : str,
                    canonical_name : str,
                    flags : FlagsT,
                    toggle_metric : ToggleMetricT,
                    toggle_type : ToggleTypeT,
                    toggle_dir : ToggleDirT) -> 'Scope':
        from ucis.mem.mem_toggle_instance_scope import MemToggleInstanceScope
        ret = MemToggleInstanceScope(self, name, canonical_name,
                flags, toggle_metric, toggle_type, toggle_dir)
        self.addChild(ret)
        return ret
    
    def getIthCoverItem(self, i)->CoverItem:
        return self.m_cover_item_l[i]
   
    