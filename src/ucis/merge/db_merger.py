'''
Created on Jan 5, 2021

@author: mballance
'''
from typing import Dict, Tuple, List

from ucis import UCIS_OTHER, UCIS_INSTANCE, UCIS_DU_MODULE, UCIS_ENABLED_STMT, \
    UCIS_ENABLED_BRANCH, UCIS_ENABLED_COND, UCIS_ENABLED_EXPR, UCIS_ENABLED_FSM, \
    UCIS_ENABLED_TOGGLE, UCIS_INST_ONCE, UCIS_SCOPE_UNDER_DU, UCIS_CVGBIN, \
    UCIS_IGNOREBIN, UCIS_ILLEGALBIN, coverpoint
from ucis.cover_type_t import CoverTypeT
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
        
        iscope_m : Dict[str, List[object]] = {}
        iscope_name_l = []

        for i,db in enumerate(src_db_l):
            for src_iscope in db.scopes(ScopeTypeT.INSTANCE):
                name = src_iscope.getScopeName()
                if not name in iscope_m.keys():
                    scope_l = [None]*len(src_db_l)
                    scope_l[i] = src_iscope
                    iscope_m[name] = scope_l
                    iscope_name_l.append(name)
                else:
                    iscope_m[name][i] = src_iscope
            
        for name in iscope_name_l:
            # We'll create the scope using the first src database
            # that it was in
            src_scopes = list(filter(lambda e: e is not None, iscope_m[name]))
            
            src_iscope = src_scopes[0]
            
            # Create a representation of the scope in the destination
            # database                
            src_du = src_iscope.getInstanceDu()
            dst_du = self.dst_db.createScope(
                src_du.getScopeName(),
                None,
                1,
                UCIS_OTHER, # TODO: must query SourceType
                UCIS_DU_MODULE, # TODO: must query GetScopeType
                UCIS_ENABLED_STMT | UCIS_ENABLED_BRANCH
                | UCIS_ENABLED_COND | UCIS_ENABLED_EXPR
                | UCIS_ENABLED_FSM | UCIS_ENABLED_TOGGLE
                | UCIS_INST_ONCE | UCIS_SCOPE_UNDER_DU) # TODO: GetScopeFlags
                    
            dst_iscope = self.dst_db.createInstance(
                src_iscope.getScopeName(),
                None,
                1, # weight
                UCIS_OTHER, # query SourceType
                UCIS_INSTANCE,
                dst_du,
                UCIS_INST_ONCE)
        
            self._merge_covergroups(dst_iscope, src_scopes)
            
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
                None, # location
                1, # weight
                UCIS_OTHER)
            self._merge_covergroup(dst_cg, src_cg_l)
        
    def _merge_covergroup(self, dst_cg, src_cg_l):
        
        dst_cp_m = self._merge_coverpoints(dst_cg, src_cg_l)
        
        self._merge_coverinsts(dst_cg, src_cg_l)
        
        pass
    
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
                        None, # location
                        1, # weight
                        UCIS_OTHER)
            self._merge_coverpoints(dst_cg_i, src_cg_i_l)

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
                None, # location
                1, # weight
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
    
    def _clone_cross(self, dst_cg, cp):
        coverpoint_l = []
        for i in range(cp.getNumCrossedCoverpoints()):
            src_cp = cp.getIthCrossedCoverpoint(i)

            dst_cp = None            
            for dst_cp_t in dst_cg.scopes(ScopeTypeT.COVERPOINT):
                if dst_cp_t.getName() == src_cp.getName():
                    dst_cp = dst_cp_t
                    break
            coverpoint_l.append(dst_cp)
            
        cp_c = dst_cg.createCross(
            cp.getName(),
            None,
            1, # weight
            UCIS_OTHER, # TODO: query
            coverpoint_l)
        
        for ci_n in cp.coverItems(CoverTypeT.CVGBIN):
            cvg_data = ci_n.getCoverData()
            cvg_data_c = cp.createBin(
                ci_n.getName(),
                None, # Location
                cvg_data.at_least,
                cvg_data.data,
                ci_n.getName(),
                UCIS_CVGBIN)
            
    
    def _clone_coverinsts(self, dst_cg, src_cg):
        for src_cg_i in src_cg.scopes(ScopeTypeT.COVERINSTANCE):
            dst_cg_i = dst_cg.createCoverInstance(
                        src_cg_i.getScopeName(),
                        None, # location
                        1, # weight
                        UCIS_OTHER)
            self._clone_coverpoints(dst_cg_i, src_cg_i)
            self._clone_coverinsts(dst_cg_i, src_cg_i)


