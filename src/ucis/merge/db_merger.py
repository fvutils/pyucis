'''
Created on Jan 5, 2021

@author: mballance
'''
from typing import Dict, Tuple, List

from ucis import UCIS_OTHER, UCIS_INSTANCE, UCIS_DU_MODULE, UCIS_ENABLED_STMT, \
    UCIS_ENABLED_BRANCH, UCIS_ENABLED_COND, UCIS_ENABLED_EXPR, UCIS_ENABLED_FSM, \
    UCIS_ENABLED_TOGGLE, UCIS_INST_ONCE, UCIS_SCOPE_UNDER_DU, UCIS_CVGBIN, \
    UCIS_IGNOREBIN, UCIS_ILLEGALBIN, coverpoint
from ucis.cover_data import CoverData
from ucis.cover_type_t import CoverTypeT
from ucis.history_node_kind import HistoryNodeKind
from ucis.report.coverage_report import CoverageReport
from ucis.report.coverage_report_builder import CoverageReportBuilder
from ucis.scope_type_t import ScopeTypeT
from ucis.ucis import UCIS


class DbMerger(object):
    
    def __init__(self):
        self.dst_db = None

    def merge(self, dst_db, src_db_l : List[UCIS]):
        # There are three possible actions for each instance scope
        # in the two databases:
        # - Only exists in DB1 -> Copy from DB1
        # - Only exists in DB2 -> Copy from DB2
        # - Exists in both -> Copy from one (DB1?) and merge
        
        self.dst_db = dst_db
        
        self._merge_instances_under(dst_db, src_db_l, dst_db)
        self._merge_history_nodes(dst_db, src_db_l)

    def _merge_instances_under(self, dst_parent, src_parents, dst_root):
        """Merge all INSTANCE scopes that are immediate children of each parent.

        *dst_parent* is either the destination db (top level) or a destination
        INSTANCE scope (recursive call for nested instances).
        *src_parents* is a list of source containers (db or INSTANCE scopes)
        aligned by database index — a None means that database has no matching
        parent at this level.
        *dst_root* is the top-level destination db, used for history merging
        only at the outermost call.
        """
        iscope_m : Dict[str, List[object]] = {}
        iscope_name_l = []

        for i, parent in enumerate(src_parents):
            if parent is None:
                continue
            for src_iscope in parent.scopes(ScopeTypeT.INSTANCE):
                name = src_iscope.getScopeName()
                if name not in iscope_m:
                    scope_l = [None] * len(src_parents)
                    iscope_m[name] = scope_l
                    iscope_name_l.append(name)
                iscope_m[name][i] = src_iscope

        for name in iscope_name_l:
            src_scopes = list(filter(lambda e: e is not None, iscope_m[name]))
            src_iscope = src_scopes[0]

            src_du = src_iscope.getInstanceDu()
            dst_du = dst_parent.createScope(
                src_du.getScopeName(),
                src_du.getSourceInfo(),
                src_du.getWeight(),
                UCIS_OTHER,
                UCIS_DU_MODULE,
                UCIS_ENABLED_STMT | UCIS_ENABLED_BRANCH
                | UCIS_ENABLED_COND | UCIS_ENABLED_EXPR
                | UCIS_ENABLED_FSM | UCIS_ENABLED_TOGGLE
                | UCIS_INST_ONCE | UCIS_SCOPE_UNDER_DU)

            dst_iscope = dst_parent.createInstance(
                src_iscope.getScopeName(),
                src_iscope.getSourceInfo(),
                1,
                UCIS_OTHER,
                UCIS_INSTANCE,
                dst_du,
                UCIS_INST_ONCE)

            self._merge_covergroups(dst_iscope, src_scopes)
            self._merge_code_coverage(dst_iscope, src_scopes)
            # Recurse into nested INSTANCE scopes
            self._merge_instances_under(dst_iscope, iscope_m[name], dst_root)

    def _merge_history_nodes(self, dst_db, src_db_l: List[UCIS]):
        """Copy history nodes from all source databases into *dst_db*."""
        def _node_key(n):
            return getattr(n, 'history_id', id(n))

        for db in src_db_l:
            src_nodes = list(db.historyNodes(HistoryNodeKind.ALL))
            src_to_dst = {}

            def _sort_key(n):
                depth = 0
                p = n.getParent()
                while p is not None:
                    depth += 1
                    p = p.getParent()
                return depth

            for src_hn in sorted(src_nodes, key=_sort_key):
                src_parent = src_hn.getParent()
                dst_parent = src_to_dst.get(_node_key(src_parent)) if src_parent is not None else None
                dst_hn = dst_db.createHistoryNode(
                    dst_parent,
                    src_hn.getLogicalName(),
                    src_hn.getPhysicalName(),
                    src_hn.getKind()
                )
                src_to_dst[_node_key(src_hn)] = dst_hn
                dst_hn.setTestStatus(src_hn.getTestStatus())
                if src_hn.getSimTime() is not None:
                    dst_hn.setSimTime(src_hn.getSimTime())
                if src_hn.getTimeUnit() is not None:
                    dst_hn.setTimeUnit(src_hn.getTimeUnit())
                if src_hn.getRunCwd() is not None:
                    dst_hn.setRunCwd(src_hn.getRunCwd())
                if src_hn.getCpuTime() is not None:
                    dst_hn.setCpuTime(src_hn.getCpuTime())
                if src_hn.getSeed() is not None:
                    dst_hn.setSeed(src_hn.getSeed())
                if src_hn.getCmd() is not None:
                    dst_hn.setCmd(src_hn.getCmd())
                if src_hn.getDate() is not None:
                    dst_hn.setDate(src_hn.getDate())
                if src_hn.getUserName() is not None:
                    dst_hn.setUserName(src_hn.getUserName())
                if src_hn.getToolCategory() is not None:
                    dst_hn.setToolCategory(src_hn.getToolCategory())
                if src_hn.getVendorId() is not None:
                    dst_hn.setVendorId(src_hn.getVendorId())
                if src_hn.getVendorTool() is not None:
                    dst_hn.setVendorTool(src_hn.getVendorTool())
                if src_hn.getVendorToolVersion() is not None:
                    dst_hn.setVendorToolVersion(src_hn.getVendorToolVersion())
                if src_hn.getComment() is not None:
                    dst_hn.setComment(src_hn.getComment())

    def _merge_covergroups(self, dst_scope, src_scopes):
        
        cg_name_m : Dict[str,List] = {}
        cg_name_l = []
      
        for i,src_scope in enumerate(src_scopes): 
            for src_cg in src_scope.scopes(ScopeTypeT.COVERGROUP):
                name = src_cg.getScopeName()
                
                if name not in cg_name_m.keys():
                    scope_l = [None]*len(src_scopes)
                    cg_name_m[name] = scope_l
                    cg_name_l.append(name)
                cg_name_m[name][i] = src_cg

        for name in cg_name_l:                
            src_cg_l = list(filter(lambda cg: cg is not None, cg_name_m[name]))
            
            # Create the destination using the first covergroup
            dst_cg = dst_scope.createCovergroup(
                src_cg_l[0].getScopeName(),
                src_cg_l[0].getSourceInfo(), # location
                src_cg_l[0].getWeight(), # weight
                UCIS_OTHER)
            self._merge_covergroup(dst_cg, src_cg_l)
        
    def _merge_covergroup(self, dst_cg, src_cg_l):
        
        dst_cp_m = self._merge_coverpoints(dst_cg, src_cg_l)

        self._merge_crosses(dst_cg, dst_cp_m, src_cg_l)
        
        self._merge_coverinsts(dst_cg, src_cg_l)

    def _merge_coverinsts(self, dst_cg, src_cg_l):

        cg_i_m = {}
        cg_n_l = []
        
        for i,src_cg in enumerate(src_cg_l):
            
            for src_cg_i in src_cg.scopes(ScopeTypeT.COVERINSTANCE):
                name = src_cg_i.getScopeName()
                
                if name not in cg_i_m.keys():
                    cg_i_m[name] = [None]*len(src_cg_l)
                    cg_n_l.append(name)
                cg_i_m[name][i] = src_cg_i
                
        for name in cg_n_l:
            src_cg_i_l = list(filter(lambda cg : cg is not None, cg_i_m[name]))
            
            dst_cg_i = dst_cg.createCoverInstance(
                        name,
                        src_cg_i_l[0].getSourceInfo(), # location
                        src_cg_i_l[0].getWeight(), # weight
                        UCIS_OTHER)
            dst_cp_m = self._merge_coverpoints(dst_cg_i, src_cg_i_l)

            self._merge_crosses(dst_cg_i, dst_cp_m, src_cg_i_l)

    def _merge_coverpoints(self, dst_cg, src_cg_l) -> Dict[str,object]:
        dst_cp_m : Dict[str, object] = {}
        cp_name_m : Dict[str,List] = {}
        cp_name_l = []
        
        for i,src_cg in enumerate(src_cg_l):
            for cp in src_cg.scopes(ScopeTypeT.COVERPOINT):
                name = cp.getScopeName()
                
                if name not in cp_name_m.keys():
                    scope_l = [None]*len(src_cg_l)
                    cp_name_m[name] = scope_l
                    cp_name_l.append(name)
                cp_name_m[name][i] = cp
                
        for name in cp_name_l:
            src_cp_l = list(filter(lambda cp : cp is not None, cp_name_m[name]))
            
            dst_cp = dst_cg.createCoverpoint(
                src_cp_l[0].getScopeName(),
                src_cp_l[0].getSourceInfo(), # location
                src_cp_l[0].getWeight(), # weight
                UCIS_OTHER) # SourceType
            dst_cp_m[name] = dst_cp
            
            self._merge_coverpoint_bins(dst_cp, src_cp_l)

        return dst_cp_m
    
    def _merge_coverpoint_bins(self, dst_cp, src_cp_l):

        for bin_t in (CoverTypeT.CVGBIN,CoverTypeT.IGNOREBIN,CoverTypeT.ILLEGALBIN):
            bin_name_m : Dict[str,List[int,int]] = {}
            bin_name_l = []
            
            for src_cp in src_cp_l:
                for ci_n in src_cp.coverItems(bin_t):
                    cvg_data = ci_n.getCoverData()
                    name = ci_n.getName()
                    if name not in bin_name_m.keys():
                        bin_name_m[name] = [0, cvg_data.at_least]
                        bin_name_l.append(name)
                    bin_name_m[name][0] += cvg_data.data
                    
            for name in bin_name_l:
                dst_cp.createBin(
                    name,
                    None, # Location
                    bin_name_m[name][1],
                    bin_name_m[name][0],
                    name,
                    bin_t)

    def _merge_crosses(self, dst_cg, dst_cp_m, src_cg_l):

        cross_m = {}
        cross_name_l = []

        for i,src_cg in enumerate(src_cg_l):
            for cr in src_cg.scopes(ScopeTypeT.CROSS):
                name = cr.getScopeName()
                if name not in cross_m.keys():
                    cross_m[name] = []
                    cross_name_l.append(name)
                cross_m[name].append(cr)

        for name in cross_name_l:
            src_cr_l = cross_m[name]

            # Create the destination cross
            coverpoint_l = []
            for i in range(src_cr_l[0].getNumCrossedCoverpoints()):
                src_cp = src_cr_l[0].getIthCrossedCoverpoint(i)
                if src_cp.getScopeName() in dst_cp_m.keys():
                    coverpoint_l.append(dst_cp_m[src_cp.getScopeName()])
                else:
                    raise Exception("Cannot find coverpoint %s when creating cross %s" % (
                        src_cp.getName(), name))

            dst_cr = dst_cg.createCross(
                name,
                src_cr_l[0].getSourceInfo(),
                src_cr_l[0].getWeight(), # weight
                UCIS_OTHER,
                coverpoint_l)

            self._merge_cross(dst_cr, src_cr_l)

    def _merge_cross(self, dst_cr, src_cr_l):

        for cvg_t in (CoverTypeT.CVGBIN,CoverTypeT.IGNOREBIN,CoverTypeT.ILLEGALBIN):
            bin_name_m = {}
            bin_name_l = []

            for src_cr in src_cr_l:
                for ci in src_cr.coverItems(cvg_t):
                    bin_n = ci.getName()
                    cvg_data = ci.getCoverData()
                    if bin_n not in bin_name_m.keys():
                        bin_name_m[bin_n] = [0, cvg_data.at_least]
                        bin_name_l.append(bin_n)
                    bin_name_m[bin_n][0] += cvg_data.data

            for bin_n in bin_name_l:
                dst_cr.createBin(
                    bin_n,
                    None, # Location
                    bin_name_m[bin_n][1], # at_least
                    bin_name_m[bin_n][0], # count
                    bin_n,
                    cvg_t)
    
    def _merge_code_coverage(self, dst_scope, src_scopes):
        """Merge code coverage scopes (BLOCK, BRANCH, TOGGLE).
        
        Args:
            dst_scope: Destination instance scope
            src_scopes: List of source instance scopes
        """
        # Merge BLOCK scopes (line/statement coverage)
        self._merge_scopes_by_type(dst_scope, src_scopes, ScopeTypeT.BLOCK)
        
        # Merge BRANCH scopes (branch coverage)
        self._merge_scopes_by_type(dst_scope, src_scopes, ScopeTypeT.BRANCH)
        
        # Merge TOGGLE scopes (toggle coverage)
        self._merge_scopes_by_type(dst_scope, src_scopes, ScopeTypeT.TOGGLE)

        # Merge FSM scopes (FSM state/transition coverage)
        self._merge_scopes_by_type(dst_scope, src_scopes, ScopeTypeT.FSM)

        # Merge assertion scopes (assert/cover directives)
        self._merge_scopes_by_type(dst_scope, src_scopes, ScopeTypeT.ASSERT)
        self._merge_scopes_by_type(dst_scope, src_scopes, ScopeTypeT.COVER)
    
    def _merge_scopes_by_type(self, dst_parent, src_scopes, scope_type):
        """Merge scopes of a specific type.
        
        Args:
            dst_parent: Destination parent scope
            src_scopes: List of source parent scopes
            scope_type: Type of scopes to merge (BLOCK, BRANCH, TOGGLE, etc.)
        """
        scope_name_m: Dict[str, List] = {}
        scope_name_l = []
        
        # Collect scopes from all source databases
        for i, src_scope in enumerate(src_scopes):
            for src_sub_scope in src_scope.scopes(scope_type):
                name = src_sub_scope.getScopeName()
                
                if name not in scope_name_m:
                    scope_l = [None] * len(src_scopes)
                    scope_name_m[name] = scope_l
                    scope_name_l.append(name)
                scope_name_m[name][i] = src_sub_scope
        
        # Merge each scope
        for name in scope_name_l:
            src_scope_l = list(filter(lambda s: s is not None, scope_name_m[name]))
            
            # Create destination scope using first source as template
            src_template = src_scope_l[0]
            dst_sub_scope = dst_parent.createScope(
                src_template.getScopeName(),
                src_template.getSourceInfo(),
                src_template.getWeight(),
                UCIS_OTHER,  # source language type
                src_template.getScopeType(),
                0  # flags - use default
            )
            
            if scope_type == ScopeTypeT.FSM:
                # Per LRM: FSMBIN items live in FSM_STATES/FSM_TRANS sub-scopes.
                # Collect from src sub-scopes; dst.createNextCover() routes correctly.
                item_name_m: Dict[str, List] = {}
                item_name_l = []
                for src_fsm in src_scope_l:
                    for sub_type in (ScopeTypeT.FSM_STATES, ScopeTypeT.FSM_TRANS):
                        for sub_scope in src_fsm.scopes(sub_type):
                            for ci in sub_scope.coverItems(CoverTypeT.FSMBIN):
                                nm = ci.getName()
                                cvg = ci.getCoverData()
                                if nm not in item_name_m:
                                    item_name_m[nm] = [0, cvg.goal]
                                    item_name_l.append(nm)
                                item_name_m[nm][0] += cvg.data
                for nm in item_name_l:
                    count, goal = item_name_m[nm]
                    cd = CoverData(CoverTypeT.FSMBIN, goal)
                    cd.data = count
                    dst_sub_scope.createNextCover(nm, cd, None)
            else:
                # Merge coverage items
                self._merge_code_coverage_items(dst_sub_scope, src_scope_l)
    
    def _merge_code_coverage_items(self, dst_scope, src_scopes):
        """Merge code coverage items from multiple source scopes.
        
        Handles STMTBIN, BRANCHBIN, TOGGLEBIN, etc.
        
        Args:
            dst_scope: Destination scope
            src_scopes: List of source scopes with same name
        """
        # Coverage types to merge
        coverage_types = [
            CoverTypeT.STMTBIN,     # Line/statement coverage
            CoverTypeT.BRANCHBIN,   # Branch coverage
            CoverTypeT.TOGGLEBIN,   # Toggle coverage
            CoverTypeT.EXPRBIN,     # Expression coverage
            CoverTypeT.CONDBIN,     # Condition coverage
            CoverTypeT.FSMBIN,      # FSM coverage
            CoverTypeT.ASSERTBIN,   # Assertion directive bins
            CoverTypeT.COVERBIN,
            CoverTypeT.PASSBIN,
            CoverTypeT.FAILBIN,
            CoverTypeT.VACUOUSBIN,
            CoverTypeT.DISABLEDBIN,
            CoverTypeT.ATTEMPTBIN,
            CoverTypeT.ACTIVEBIN,
            CoverTypeT.PEAKACTIVEBIN,
        ]
        
        for cvg_type in coverage_types:
            item_name_m: Dict[str, List[int]] = {}
            item_name_l = []
            
            # Collect items from all sources
            for src_scope in src_scopes:
                for ci in src_scope.coverItems(cvg_type):
                    item_name = ci.getName()
                    cvg_data = ci.getCoverData()
                    
                    if item_name not in item_name_m:
                        # [accumulated_count, goal]
                        item_name_m[item_name] = [0, cvg_data.goal]
                        item_name_l.append(item_name)
                    
                    # Accumulate hit counts
                    item_name_m[item_name][0] += cvg_data.data
            
            # Create merged items in destination
            for item_name in item_name_l:
                count, goal = item_name_m[item_name]
                
                # Get source info from first occurrence (they should be identical)
                src_info = None
                for src_scope in src_scopes:
                    for ci in src_scope.coverItems(cvg_type):
                        if ci.getName() == item_name:
                            src_info = ci.getSourceInfo()
                            break
                    if src_info:
                        break
                
                # Create cover data
                cover_data = CoverData(cvg_type, 0)
                cover_data.data = count
                cover_data.goal = goal
                
                # Create cover item
                dst_scope.createNextCover(
                    item_name,
                    cover_data,
                    src_info
                )
    

