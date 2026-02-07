"""
LCOV Format Exporter

Exports UCIS coverage data to LCOV format (.info files).
LCOV is widely used for C/C++ code coverage and supported by many CI/CD tools.
"""
from typing import TextIO


class LcovFormatter:
    """
    Format UCIS data as LCOV .info format.
    
    LCOV format structure:
    TN:<test name>
    SF:<source file>
    FN:<line>,<function name>
    FNDA:<count>,<function name>
    FNF:<functions found>
    FNH:<functions hit>
    DA:<line>,<count>
    LF:<lines found>
    LH:<lines hit>
    BRDA:<line>,<block>,<branch>,<count>
    BRF:<branches found>
    BRH:<branches hit>
    end_of_record
    """
    
    def __init__(self):
        self.test_name = None
        
    def format(self, db, output: TextIO):
        """
        Format database as LCOV.
        
        Args:
            db: UCIS database
            output: Output file/stream
        """
        from ucis.report.coverage_report_builder import CoverageReportBuilder
        
        # Build coverage report
        report = CoverageReportBuilder.build(db)
        
        # Write test name if available
        test_name = self._get_test_name(db)
        if test_name:
            output.write(f"TN:{test_name}\n")
        
        # LCOV expects source file-based coverage
        # For UCIS functional coverage, we'll map covergroups to "files"
        self._write_coverage_as_files(report, output)
        
    def _get_test_name(self, db) -> str:
        """Extract test name from database."""
        try:
            from ucis.history_node_kind import HistoryNodeKind
            for node in db.historyNodes(HistoryNodeKind.TEST):
                return node.getLogicalName()
        except:
            pass
        return "ucis_coverage"
    
    def _write_coverage_as_files(self, report, output: TextIO):
        """Write coverage data as LCOV file records."""
        if not report.covergroups:
            return
        
        for cg in report.covergroups:
            # Treat each covergroup as a "source file"
            source_file = f"functional/{cg.name}.sv"
            output.write(f"SF:{source_file}\n")
            
            # Track statistics
            functions_found = 0
            functions_hit = 0
            lines_found = 0
            lines_hit = 0
            branches_found = 0
            branches_hit = 0
            
            line_num = 1
            
            if hasattr(cg, 'coverpoints') and cg.coverpoints:
                for cp in cg.coverpoints:
                    # Treat coverpoint as a function
                    functions_found += 1
                    output.write(f"FN:{line_num},{cp.name}\n")
                    
                    hit_count = 1 if cp.coverage > 0 else 0
                    if hit_count > 0:
                        functions_hit += 1
                    output.write(f"FNDA:{hit_count},{cp.name}\n")
                    
                    # Map bins to lines
                    if hasattr(cp, 'bins') and cp.bins:
                        for bin in cp.bins:
                            lines_found += 1
                            output.write(f"DA:{line_num},{bin.count}\n")
                            if bin.count > 0:
                                lines_hit += 1
                            line_num += 1
                            
                            # Treat bins as branches
                            branches_found += 1
                            branch_taken = 1 if bin.count > 0 else 0
                            output.write(f"BRDA:{line_num-1},0,0,{bin.count if branch_taken else '-'}\n")
                            if branch_taken:
                                branches_hit += 1
                    
                    line_num += 1
            
            # Write summary
            output.write(f"FNF:{functions_found}\n")
            output.write(f"FNH:{functions_hit}\n")
            output.write(f"LF:{lines_found}\n")
            output.write(f"LH:{lines_hit}\n")
            output.write(f"BRF:{branches_found}\n")
            output.write(f"BRH:{branches_hit}\n")
            output.write("end_of_record\n")
