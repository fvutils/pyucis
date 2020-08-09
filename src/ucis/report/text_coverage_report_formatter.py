'''
Created on Apr 8, 2020

@author: ballance
'''
from ucis.report.coverage_report import CoverageReport
from typing import List

class TextCoverageReportFormatter(object):
    
    def __init__(self, 
                report : CoverageReport, 
                fp):
        self._report = report
        self._fp = fp
        self._ind = ""
        self.details = False
        self.order_bins_by_hit = False
        
    def report(self):
        for cg in self._report.covergroups:
            self.report_covergroup(cg, False)
            
    def report_covergroup(self, 
                          cg : CoverageReport.Covergroup,
                          is_inst):
        self.writeln("%s %s : %f%%", 
                "INST" if is_inst else "TYPE",
                cg.name, cg.coverage)
        
        with self.indent():
            for cp in cg.coverpoints:
                self.report_coverpoint(cp)
            for cr in cg.crosses:
                self.report_cross(cr)
        
            for cg_i in cg.covergroups:
                self.report_covergroup(cg_i, True)
            
    def report_coverpoint(self, cp : CoverageReport.Coverpoint):
        self.writeln("CVP %s : %f%%", cp.name, cp.coverage)
        
        if self.details:
            self.writeln("Bins:")
            with self.indent():
                self.report_bins(cp.bins)
            

    def report_cross(self, cr : CoverageReport.Cross):
        self.writeln("CROSS %s : %f%%", cr.name, cr.coverage)
        
        if self.details:
            self.writeln("Bins:")
            with self.indent():
                self.report_bins(cr.bins)
        
    def report_bins(self, bins : List[CoverageReport.CoverBin]):
        if self.order_bins_by_hit:
            for b in bins:
                if b.hit:
                    self.writeln("%s : %d", b.name, b.count)
            for b in bins:
                if not b.hit:
                    self.writeln("%s : %d", b.name, b.count)
        else:
            for b in bins:
                self.writeln("%s : %d", b.name, b.count)
    
    def writeln(self, msg, *args):
        self._fp.write(self._ind + msg % args + "\n")

    def indent(self):
        return self
    
    def __enter__(self):
        self._ind += "    "
        
    def __exit__(self, t, v, tb):
        self._ind = self._ind[:-4]
        