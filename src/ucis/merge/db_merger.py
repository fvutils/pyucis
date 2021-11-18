'''
Created on Jan 5, 2021

@author: mballance
'''
from ucis import UCIS_OTHER, UCIS_INSTANCE, UCIS_DU_MODULE, UCIS_ENABLED_STMT, \
    UCIS_ENABLED_BRANCH, UCIS_ENABLED_COND, UCIS_ENABLED_EXPR, UCIS_ENABLED_FSM, \
    UCIS_ENABLED_TOGGLE, UCIS_INST_ONCE, UCIS_SCOPE_UNDER_DU, UCIS_CVGBIN,\
    UCIS_IGNOREBIN, UCIS_ILLEGALBIN, coverpoint
from ucis.cover_type_t import CoverTypeT
from ucis.report.coverage_report import CoverageReport
from ucis.report.coverage_report_builder import CoverageReportBuilder
from ucis.scope_type_t import ScopeTypeT
from ucis.ucis import UCIS


class DbMerger(object):
    
    def __init__(self, dst_db):
        self.dst_db = dst_db

    def merge(self, src_db):
        for src_iscope in src_db.scopes(ScopeTypeT.INSTANCE):
            # Search for relevant scope in dst_db
            # - If exists validate that it is the same as the source scope
            # - If it doesn't exist, copy src->dst
            print("src_name: %s" % src_iscope.getScopeName())
            dst_iscope = None
            for dst_iscope_t in self.dst_db.scopes(ScopeTypeT.INSTANCE):
                if dst_iscope_t.getScopeName() == src_iscope.getScopeName():
                    print("found scope")
                    dst_iscope = dst_iscope_t
                    break
                
            if dst_iscope is not None:
                # TODO: validate
                print("TODO: validate")
                pass
            else:
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

            self._merge_covergroups(dst_iscope, src_iscope)
            
    def _merge_covergroups(self, dst_scope, src_scope):
        
        for src_cg in src_scope.scopes(ScopeTypeT.COVERGROUP):
            dst_cg = None
            
            for dst_cg_t in dst_scope.scopes(ScopeTypeT.COVERGROUP):
                if dst_cg_t.getScopeName() == src_cg.getScopeName():
                    print("Found")
                    dst_cg = dst_cg_t
                    break
                
            if dst_cg is not None:
                print("TODO: compare covergroups")
            else:
                dst_cg = dst_scope.createCovergroup(
                    src_cg.getScopeName(),
                    None, # location
                    1, # weight
                    UCIS_OTHER)
                self._clone_coverpoints(dst_cg, src_cg)

                self._clone_coverinsts(dst_cg, src_cg)                    


    def _clone_coverpoints(self, dst_cg, src_cg):
        for cp in src_cg.scopes(ScopeTypeT.COVERPOINT):
            self._clone_coverpoint(dst_cg, cp)
            pass
        
        for cp in src_cg.scopes(ScopeTypeT.CROSS):
            self._clone_cross(dst_cg, cp)
            pass
        
        pass
    
    def _clone_coverpoint(self, dst_cg, src_cp):
        cp = dst_cg.createCoverpoint(
            src_cp.getScopeName(),
            None, # location
            1, # weight
            UCIS_OTHER) # SourceType
        
        for ci_n in src_cp.coverItems(CoverTypeT.CVGBIN):
            cvg_data = ci_n.getCoverData()
            cvg_data_c = cp.createBin(
                ci_n.getName(),
                None, # Location
                cvg_data.at_least,
                cvg_data.data,
                ci_n.getName(),
                UCIS_CVGBIN)
            
        for ci_n in src_cp.coverItems(CoverTypeT.IGNOREBIN):
            cvg_data = ci_n.getCoverData()
            cvg_data_c = cp.createBin(
                ci_n.getName(),
                None, # Location
                cvg_data.at_least,
                cvg_data.data,
                ci_n.getName(),
                UCIS_IGNOREBIN)
            
        for ci_n in src_cp.coverItems(CoverTypeT.ILLEGALBIN):
            cvg_data = ci_n.getCoverData()
            cvg_data_c = cp.createBin(
                ci_n.getName(),
                None, # Location
                cvg_data.at_least,
                cvg_data.data,
                ci_n.getName(),
                UCIS_ILLEGALBIN)
            
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


