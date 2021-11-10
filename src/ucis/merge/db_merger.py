'''
Created on Jan 5, 2021

@author: mballance
'''
from ucis.report.coverage_report import CoverageReport
from ucis.report.coverage_report_builder import CoverageReportBuilder
from ucis.ucis import UCIS
from ucis.scope_type_t import ScopeTypeT

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
                # TODO: clone
                print("TODO: clone")
                pass
                
            