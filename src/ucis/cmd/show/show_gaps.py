"""
Show Gaps Command

Displays coverage gaps - bins, coverpoints, and other coverage items
that have not been hit (count == 0).
"""
from typing import Any, Dict, List
from ucis.cmd.show_base import ShowBase


class ShowGaps(ShowBase):
    """
    Display coverage gaps.
    
    Shows:
    - Uncovered bins (hit count == 0)
    - Coverpoints with partial coverage
    - Summary statistics of gaps
    """
    
    def get_data(self) -> Dict[str, Any]:
        """
        Extract gap information from the database.
        
        Returns:
            Dictionary containing gap information
        """
        from ucis.report.coverage_report_builder import CoverageReportBuilder
        
        # Build coverage report
        report = CoverageReportBuilder.build(self.db)
        
        # Collect gaps
        gaps = {
            "database": self.args.db,
            "summary": self._get_gap_summary(report),
            "uncovered_bins": self._get_uncovered_bins(report),
        }
        
        # Add filtering if requested
        if hasattr(self.args, 'threshold') and self.args.threshold is not None:
            gaps["filter"] = {
                "threshold": self.args.threshold,
                "description": f"Showing coverpoints with coverage < {self.args.threshold}%"
            }
        
        return gaps
    
    def _get_gap_summary(self, report) -> Dict[str, Any]:
        """Calculate gap summary statistics."""
        total_bins = 0
        uncovered_bins = 0
        total_coverpoints = 0
        partial_coverpoints = 0
        
        if report.covergroups:
            for cg in report.covergroups:
                if hasattr(cg, 'coverpoints') and cg.coverpoints:
                    for cp in cg.coverpoints:
                        total_coverpoints += 1
                        
                        if hasattr(cp, 'bins') and cp.bins:
                            cp_has_gap = False
                            for bin in cp.bins:
                                total_bins += 1
                                if bin.count == 0:
                                    uncovered_bins += 1
                                    cp_has_gap = True
                            
                            if cp_has_gap and cp.coverage > 0:
                                partial_coverpoints += 1
        
        coverage_pct = 0.0
        if total_bins > 0:
            coverage_pct = ((total_bins - uncovered_bins) / total_bins) * 100
        
        return {
            "overall_coverage": coverage_pct,
            "total_bins": total_bins,
            "covered_bins": total_bins - uncovered_bins,
            "uncovered_bins": uncovered_bins,
            "total_coverpoints": total_coverpoints,
            "partial_coverpoints": partial_coverpoints,
        }
    
    def _get_uncovered_bins(self, report) -> List[Dict[str, Any]]:
        """Get list of all uncovered bins."""
        uncovered = []
        
        threshold = getattr(self.args, 'threshold', None)
        
        if report.covergroups:
            for cg in report.covergroups:
                if hasattr(cg, 'coverpoints') and cg.coverpoints:
                    for cp in cg.coverpoints:
                        # Check if coverpoint meets threshold criteria
                        if threshold is not None and cp.coverage >= threshold:
                            continue
                        
                        if hasattr(cp, 'bins') and cp.bins:
                            for bin in cp.bins:
                                if bin.count == 0:
                                    uncovered.append({
                                        "covergroup": cg.name,
                                        "coverpoint": cp.name,
                                        "bin": bin.name,
                                        "at_least": getattr(bin, 'at_least', 1),
                                        "count": bin.count,
                                    })
        
        return uncovered
