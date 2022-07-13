'''
Created on Mar 27, 2020

@author: ballance
'''
from ucis.scope_type_t import ScopeTypeT
from ucis.report.coverage_report import CoverageReport
from ucis.coverpoint import Coverpoint
from ucis.cover_data import CoverData
from ucis.cover_type_t import CoverTypeT
from math import ceil
from ucis.cross import Cross
from ucis.mem.mem_cover_index import MemCoverIndex
from collections import defaultdict


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
        
        self.update_coverage()
        for iscope in self.db.scopes(ScopeTypeT.INSTANCE):
            self.build_covergroups(iscope)
            
        return self.report
            
    def update_coverage(self):
        import copy
        for inst in self.db.scopes(ScopeTypeT.INSTANCE):
            for cg in inst.scopes(ScopeTypeT.COVERGROUP):
                cps = dict()
                crs = dict()
                merged_cps = defaultdict(lambda: defaultdict(lambda: CoverData(CoverTypeT.CVGBIN, 0)))
                merged_crs = defaultdict(lambda: defaultdict(lambda: CoverData(CoverTypeT.CVGBIN, 0)))
                not_initialized = True
                for ci in cg.scopes(ScopeTypeT.COVERINSTANCE):
                    if ci.getMergeInstances():
                        if not_initialized:
                            for cp in ci.scopes(ScopeTypeT.COVERPOINT):
                                cp_m = cg.createCoverpoint(
                                    cp.m_name, cp.m_srcinfo, cp.m_weight, cp.m_source)
                                cps[cp.m_name] = cp_m
                                for ci_n in cp.coverItems(CoverTypeT.CVGBIN):
                                    cp_m.createNextCover(ci_n.name, copy.copy(ci_n.data), ci_n.srcinfo)
                                    merged_cps[cp.m_name][ci_n.name] = copy.copy(ci_n.getCoverData())
                                    merged_cps[cp.m_name][ci_n.name].data = 0
                            for cr in ci.scopes(ScopeTypeT.CROSS):
                                cr_m = cg.createCross(
                                    cr.m_name, cr.m_srcinfo, cr.m_weight, cr.m_source,
                                        copy.copy(cr.coverItems))
                                crs[cr.m_name] = cr_m
                                for ci_n in cr.coverItems(CoverTypeT.CVGBIN):
                                    cr_m.createNextCover(ci_n.name, copy.copy(ci_n.data), ci_n.srcinfo)
                                    merged_cps[cr.m_name][ci_n.name] = copy.copy(ci_n.getCoverData())
                                    merged_cps[cr.m_name][ci_n.name].data = 0
                            not_initialized = False
                        for cp in ci.scopes(ScopeTypeT.COVERPOINT):
                            for ci_n in cp.coverItems(CoverTypeT.CVGBIN):
                                merged_cps[cp.m_name][ci_n.name].data+= ci_n.getCoverData().data
                        for cr in ci.scopes(ScopeTypeT.CROSS):
                            for ci_n in cr.coverItems(CoverTypeT.CVGBIN):
                                merged_crs[cr.m_name][ci_n.name].data+= ci_n.getCoverData().data
                for cp in cps.values():
                    for ci_n in cp.coverItems(CoverTypeT.CVGBIN):
                        ci_n.data.data = merged_cps[cp.m_name][ci_n.name].data
                    cp.m_name += " (merged)"
                for cr in crs.values():
                    for ci_n in cr.coverItems(CoverTypeT.CVGBIN):
                        ci_n.data.data = merged_crs[cr.m_name][ci_n.name].data
                    cr.m_name += " (merged)"


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
        self.report.coverage = coverage/div
            
    def build_covergroup(self, cg_n)->CoverageReport.Covergroup:
        cg_r = CoverageReport.Covergroup(
            cg_n.getScopeName(),
            cg_n.getScopeName())
        
        cg_r.weight = cg_n.getWeight()
        
        for cp_in in cg_n.scopes(ScopeTypeT.COVERPOINT):
            cg_r.coverpoints.append(self.build_coverpoint(cp_in))
            
        for cr_in in cg_n.scopes(ScopeTypeT.CROSS):
            cg_r.crosses.append(self.build_cross(cr_in))

        unmerged_ci = list()
        for cg_in in cg_n.scopes(ScopeTypeT.COVERINSTANCE):
            ci = self.build_coverinstance(cg_in)
            if cg_in.getPerInstance():
                cg_r.covergroups.append(ci)
            if not cg_in.getMergeInstances():
                unmerged_ci.append(ci)
        # Determine the covergroup coverage
        coverage = 0.0
        div = 0
            
        for cp in cg_r.coverpoints:
            if cp.weight > 0:
                coverage += cp.coverage * cp.weight
            div += cp.weight
            
        for cr in cg_r.crosses:
            if cr.weight > 0:
                coverage += cr.coverage * cr.weight
            div += cr.weight
            
        for cg in unmerged_ci:
            if cg.weight > 0:
                coverage += cg.coverage * cg.weight
            div += cg.weight

        if div > 0: coverage /= div

        cg_r.coverage = coverage
        
        return cg_r

    def build_coverinstance(self, cg_i)->CoverageReport.Covergroup:
        cg_r = CoverageReport.Covergroup(
            cg_i.getScopeName(),
            cg_i.getScopeName())
        
        cg_r.weight = cg_i.getWeight()
        
        for cp_in in cg_i.scopes(ScopeTypeT.COVERPOINT):
            cg_r.coverpoints.append(self.build_coverpoint(cp_in))
            
        for cr_in in cg_i.scopes(ScopeTypeT.CROSS):
            cg_r.crosses.append(self.build_cross(cr_in))

        coverage = 0.0

        div = 0
        for cp in cg_r.coverpoints:
            if cp.weight > 0:
                coverage += cp.coverage * cp.weight
            div += cp.weight
            
        for cr in cg_r.crosses:
            coverage += cr.coverage * cr.weight
            div += cr.weight
            
        if div > 0: coverage /= div

        cg_r.coverage = coverage
        
        return cg_r

    def build_coverpoint(self, cp_n : Coverpoint):
        cp_r = CoverageReport.Coverpoint(cp_n.getScopeName())
        cp_r.weight = cp_n.getWeight()
        
        # Read in bins
        num_hit = 0
        total = 0
        for ci_n in cp_n.coverItems(CoverTypeT.CVGBIN):
            cvg_data = ci_n.getCoverData()
            
            if cvg_data.data >= cvg_data.at_least:
                num_hit += 1
                
            cp_r.bins.append(CoverageReport.CoverBin(
                    ci_n.getName(),
                    cvg_data.at_least,
                    cvg_data.data))

            total += 1
            
        for ci_n in cp_n.coverItems(CoverTypeT.IGNOREBIN):
            cvg_data = ci_n.getCoverData()
            
            cp_r.ignore_bins.append(CoverageReport.CoverBin(
                    ci_n.getName(),
                    cvg_data.at_least,
                    cvg_data.data))
            
        for ci_n in cp_n.coverItems(CoverTypeT.ILLEGALBIN):
            cvg_data = ci_n.getCoverData()
            
            cp_r.illegal_bins.append(CoverageReport.CoverBin(
                    ci_n.getName(),
                    cvg_data.at_least,
                    cvg_data.data))

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
        
        
    
    
