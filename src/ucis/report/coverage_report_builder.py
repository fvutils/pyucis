'''
Created on Mar 27, 2020

@author: ballance
'''
from ucis.scope_type_t import ScopeTypeT
from ucis.report.coverage_report import CoverageReport
from ucis.coverpoint import Coverpoint
from ucis.cover_type_t import CoverTypeT
from math import ceil
from ucis.cross import Cross


class CoverageReportBuilder(object):
    """
    Builds a coverage-report object from a UCIS database
    """
    
    def __init__(self, db):
        self.db = db
        self.report = CoverageReport()
    
    @staticmethod
    def build(db : 'UCIS') ->'CoverageReport':
        """
        Builds a CoverageReport object from a UCIS database
        """
        
        builder = CoverageReportBuilder(db)
        return builder._build()
        

    def _build(self)->'CoverageReport':

        all_coverage = 0.0
        all_div = 0
        for iscope in self.db.scopes(ScopeTypeT.INSTANCE):
            cov, div = self.build_covergroups(iscope)
            all_coverage += cov
            all_div += div

        if all_div > 0:
            self.report.coverage = all_coverage / all_div
        else:
            self.report.coverage = 0.0

        return self.report

    def build_covergroups(self, iscope):

        coverage = 0.0
        div = 0

        for cg_t in iscope.scopes(ScopeTypeT.COVERGROUP):
            cg = self.build_covergroup(cg_t)
            if cg.weight > 0:
                coverage += cg.coverage * cg.weight
            div += cg.weight
            self.report.covergroups.append(cg)
            self.report.covergroup_m[cg.instname] = cg

        return coverage, div

    def build_covergroup(self, cg_n)->CoverageReport.Covergroup:
        cg_r = CoverageReport.Covergroup(
            cg_n.getScopeName(),
            cg_n.getScopeName())
        
        cg_r.weight = cg_n.getWeight()
        
        for cp_in in cg_n.scopes(ScopeTypeT.COVERPOINT):
            cg_r.coverpoints.append(self.build_coverpoint(cp_in))
            
        for cr_in in cg_n.scopes(ScopeTypeT.CROSS):
            cg_r.crosses.append(self.build_cross(cr_in))

        for cg_in in cg_n.scopes(ScopeTypeT.COVERINSTANCE):
            cg_r.covergroups.append(self.build_covergroup(cg_in))
            
        # Determine the covergroup coverage.
        # If the covergroup has type-level coverpoints/crosses (the aggregate
        # view across all instances), use those. Otherwise fall back to the
        # average of sub-instances.
        coverage = 0.0
        div = 0

        if cg_r.coverpoints or cg_r.crosses:
            for cp in cg_r.coverpoints:
                if cp.weight > 0:
                    coverage += cp.coverage * cp.weight
                div += cp.weight

            for cr in cg_r.crosses:
                coverage += cr.coverage * cr.weight
                div += cr.weight
        else:
            for sub in cg_r.covergroups:
                if sub.weight > 0:
                    coverage += sub.coverage * sub.weight
                div += sub.weight

        if div > 0: coverage /= div

        cg_r.coverage = coverage
        
        return cg_r

    def build_coverpoint(self, cp_n : Coverpoint):
        cp_r = CoverageReport.Coverpoint(cp_n.getScopeName())
        cp_r.weight = cp_n.getWeight()
        
        # Read in bins — check both direct cover items and typed bin
        # sub-scopes (CVGBINSCOPE, IGNOREBINSCOPE, ILLEGALBINSCOPE).
        num_hit = 0
        total = 0

        def _collect_items(scope):
            """Yield (cover_item, effective_type) from a scope."""
            for ci in scope.coverItems(CoverTypeT.CVGBIN):
                yield ci, CoverTypeT.CVGBIN
            for ci in scope.coverItems(CoverTypeT.IGNOREBIN):
                yield ci, CoverTypeT.IGNOREBIN
            for ci in scope.coverItems(CoverTypeT.ILLEGALBIN):
                yield ci, CoverTypeT.ILLEGALBIN

        # Collect from direct items on the coverpoint
        sources = [cp_n]
        # Also collect from typed bin sub-scopes
        for sub in cp_n.scopes(ScopeTypeT.CVGBINSCOPE):
            sources.append(sub)
        for sub in cp_n.scopes(ScopeTypeT.IGNOREBINSCOPE):
            sources.append(sub)
        for sub in cp_n.scopes(ScopeTypeT.ILLEGALBINSCOPE):
            sources.append(sub)

        for src in sources:
            for ci_n, ct in _collect_items(src):
                cvg_data = ci_n.getCoverData()
                bin_obj = CoverageReport.CoverBin(
                    ci_n.getName(), cvg_data.at_least, cvg_data.data)
                if ct == CoverTypeT.CVGBIN:
                    cp_r.bins.append(bin_obj)
                    total += 1
                    if cvg_data.data >= cvg_data.at_least:
                        num_hit += 1
                elif ct == CoverTypeT.IGNOREBIN:
                    cp_r.ignore_bins.append(bin_obj)
                elif ct == CoverTypeT.ILLEGALBIN:
                    cp_r.illegal_bins.append(bin_obj)

        if total > 0:
            cp_r.coverage = (100*num_hit)/total
        else:
            cp_r.coverage = 0
        
        return cp_r
        

    def build_cross(self, cr_n : Cross):
        cr_r = CoverageReport.Cross(cr_n.getScopeName())
        
        # Read in bins
        num_hit = 0
        total = 0
        for ci_n in cr_n.coverItems(CoverTypeT.CVGBIN):
            cvg_data = ci_n.getCoverData()

            if cvg_data.data >= cvg_data.at_least:
                num_hit += 1
                
            cr_r.bins.append(CoverageReport.CoverBin(
                    ci_n.getName(),
                    cvg_data.goal,
                    cvg_data.data))

            total += 1

        if total > 0: cr_r.coverage = (100*num_hit)/total
        
        return cr_r        
        
        
    
    
