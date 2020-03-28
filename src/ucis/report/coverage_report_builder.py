'''
Created on Mar 27, 2020

@author: ballance
'''
from ucis.scope_type_t import ScopeTypeT
from ucis.report.coverage_report import CoverageReport


class CoverageReportBuilder(object):
    
    def __init__(self, db):
        self.db = db
        self.report = CoverageReport()
    
    @staticmethod
    def build(db) ->'CoverageReport':
        builder = CoverageReportBuilder(db)
        return builder._build()
        

    def _build(self)->'CoverageReport':
        
        for iscope in self.db.scopes(ScopeTypeT.INSTANCE):
            self.build_covergroups(iscope)
            
        return self.report
            

    def build_covergroups(self, iscope):
        
        for cg_t in iscope.scopes(ScopeTypeT.COVERGROUP):
            self.report.covergroups.append(self.build_covergroup(cg_t))
            
    def build_covergroup(self, cg_n)->CoverageReport.Covergroup:
        cg_r = CoverageReport.Covergroup(cg_n.getScopeName())
        
        for cg_in in cg_n.scopes(ScopeTypeT.COVERINSTANCE):
            cg_r.covergroups.append(self.build_covergroup(cg_in))
        
        return cg_r
        
        
        
        
    
    