'''
Created on Jan 5, 2021

@author: mballance
'''
from ucis.report.coverage_report import CoverageReport
from ucis.report.coverage_report_builder import CoverageReportBuilder
from ucis.ucis import UCIS

class DbMerger(object):
    
    def __init__(self):
        self.merged = CoverageReport()

    def merge(self, db):
        report = CoverageReportBuilder.build(db)

        self.apply(report)        

    def result(self, db):
        for cg in self.merged.covergroups:
            self.write_covergroup(db, cg)
        # TODO: convert back to UCIS
        pass
    
    def apply(self, report):
        covergroup_m = {}
        for cg in self.merged.covergroups:
            covergroup_m[cg.instname] = cg
            
        for cg in report.covergroups:
            if cg.instname in covergroup_m.keys():
                # Already have this covergroup. Merge
                self.apply_covergroup(covergroup_m[cg.instname], cg)
            else:
                # It's a new covergroup
                self.merged.covergroups.append(cg)
        
    def apply_covergroup(self, 
                         cg_result : CoverageReport.Covergroup, 
                         cg : CoverageReport.Covergroup):
        coverpoint_m = {}
        
        for cp in cg_result.coverpoints:
            coverpoint_m[cp.instname] = cp

        for cp in cg.coverpoints:
            if cp.instname in coverpoint_m.keys():
                # Existing coverpoint
                self.apply_coverpoint(coverpoint_m[cp.instname], cp)
            else:
                cg_result.add_coverpoint(cp)
                
        coverpoint_m = {}
        
        for cp in cg_result.crosses:
            coverpoint_m[cp.instname] = cp
            
        for cp in cg.crosses:
            if cp.instname in coverpoint_m.keys():
                # Existing coverpoint
                self.apply_coverpoint(coverpoint_m[cp.instname], cp)
            else:
                cg_result.add_coverpoint(cp)
            
    def apply_coverpoint(self,
                         cp_result : CoverageReport.Coverpoint,
                         cp : CoverageReport.Coverpoint):
        bin_m = {}
        for b in cp_result.bins:
            bin_m[b.name] = b

        for b in cp.bins:
            if b.name in bin_m.keys():
                bin_m[b.name].count += b.count
            else:
                cp_result.bins.append(b)
                
    def write_covergroup(self, db : UCIS, cg : CoverageReport.Covergroup):
        from ucis.source_info import SourceInfo
        cg_inst = self.get_cg_inst(cg)
        
        cg_name = cg.name if cg.name is not None else "<unknown>"
        inst_location = None
        
        if cg.type_cg is None:
            if cg.srcinfo_decl is not None:
                fh = self.get_file_handle(cg.srcinfo_decl.filename)
                inst_location = SourceInfo(
                    fh, 
                    cg.srcinfo_decl.lineno, 
                    0)

            # obtain weight from covergroup
            # TODO: should be .options vs .type_options
            weight = cg.options.weight
            # TODO: obtain at_least from coverpoint and set on cp_scope
            # TODO: obtain goal from coverpoint and set on cp_scope
            # TODO: obtain comment from coverpoint and set on cp_scope
            self.active_scope_s.append(cg_inst.createCovergroup(
                cg_name,
                inst_location,
                weight, # weight
                UCIS_OTHER)) # Source type
        else:
            if cg.srcinfo_inst is not None:
                fh = self.get_file_handle(cg.srcinfo_inst.filename)
                inst_location = SourceInfo(
                    fh, 
                    cg.srcinfo_inst.lineno, 
                    0)
            self.active_scope_s.append(cg_inst.createCoverInstance(
                self.get_cg_instname(cg),
                inst_location,
                1, # weight
                UCIS_OTHER)) # Source type
        
        super().visit_covergroup(cg)
        self.active_scope_s.pop()        
        pass

        