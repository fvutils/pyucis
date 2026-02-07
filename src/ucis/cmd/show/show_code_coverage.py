"""
Show Code Coverage Command

Displays code coverage information with support for multiple output formats.
"""
from typing import Any, Dict
from ucis.cmd.show_base import ShowBase


class ShowCodeCoverage(ShowBase):
    """
    Display code coverage information.
    
    Supports multiple output formats:
    - json (default)
    - text
    - lcov (LCOV .info format)
    - cobertura (Cobertura XML)
    """
    
    def get_data(self) -> Dict[str, Any]:
        """
        Extract code coverage information.
        
        Returns:
            Dictionary containing coverage data
        """
        from ucis.report.coverage_report_builder import CoverageReportBuilder
        
        # Build coverage report
        report = CoverageReportBuilder.build(self.db)
        
        # For now, we'll present functional coverage data
        # In future, this would include actual code coverage (statements, branches, etc.)
        result = {
            "database": self.args.db,
            "coverage_type": "functional",
            "overall_coverage": report.coverage,
            "covergroups": self._get_coverage_data(report),
        }
        
        return result
    
    def _get_coverage_data(self, report) -> list:
        """Extract coverage data from report."""
        coverage_data = []
        
        if not report.covergroups:
            return coverage_data
        
        for cg in report.covergroups:
            cg_data = {
                "name": cg.name,
                "coverage": cg.coverage,
                "items": []
            }
            
            if hasattr(cg, 'coverpoints') and cg.coverpoints:
                for cp in cg.coverpoints:
                    cp_data = {
                        "name": cp.name,
                        "coverage": cp.coverage,
                        "hits": []
                    }
                    
                    if hasattr(cp, 'bins') and cp.bins:
                        for bin in cp.bins:
                            cp_data["hits"].append({
                                "name": bin.name,
                                "count": bin.count,
                                "covered": bin.count > 0,
                            })
                    
                    cg_data["items"].append(cp_data)
            
            coverage_data.append(cg_data)
        
        return coverage_data
    
    def _write_output(self, data: Dict[str, Any]):
        """
        Write output in the specified format.
        
        Overrides base class to support LCOV and Cobertura formats.
        """
        output_format = getattr(self.args, 'output_format', 'json')
        out = getattr(self.args, 'out', None)
        
        if out is None:
            import sys
            fp = sys.stdout
            close_fp = False
        else:
            fp = open(out, 'w')
            close_fp = True
            
        try:
            if output_format == 'lcov':
                self._write_lcov(fp)
            elif output_format == 'cobertura':
                self._write_cobertura(fp)
            elif output_format == 'jacoco':
                self._write_jacoco(fp)
            elif output_format == 'clover':
                self._write_clover(fp)
            elif output_format == 'json':
                import json
                json.dump(data, fp, indent=2)
                fp.write("\n")
            elif output_format in ('text', 'txt'):
                self._write_text(data, fp)
            else:
                raise Exception(f"Unknown output format: {output_format}")
        finally:
            if close_fp:
                fp.close()
    
    def _write_lcov(self, fp):
        """Write LCOV format."""
        from ucis.formatters.format_lcov import LcovFormatter
        formatter = LcovFormatter()
        formatter.format(self.db, fp)
    
    def _write_cobertura(self, fp):
        """Write Cobertura XML format."""
        from ucis.formatters.format_cobertura import CoberturaFormatter
        formatter = CoberturaFormatter()
        formatter.format(self.db, fp)
    
    def _write_jacoco(self, fp):
        """Write JaCoCo XML format."""
        from ucis.formatters.format_jacoco import JacocoFormatter
        formatter = JacocoFormatter()
        formatter.format(self.db, fp)
    
    def _write_clover(self, fp):
        """Write Clover XML format."""
        from ucis.formatters.format_clover import CloverFormatter
        formatter = CloverFormatter()
        formatter.format(self.db, fp)
