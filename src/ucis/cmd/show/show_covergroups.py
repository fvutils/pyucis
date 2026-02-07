"""
Show Covergroups Command

Displays detailed information about covergroups including
hierarchical coverage data.
"""
from typing import Any, Dict, List
from ucis.cmd.show_base import ShowBase


class ShowCovergroups(ShowBase):
    """
    Display detailed covergroup information.
    
    Shows:
    - List of all covergroups with coverage percentages
    - Coverpoints within each covergroup
    - Bin counts and coverage details
    """
    
    def get_data(self) -> Dict[str, Any]:
        """
        Extract covergroup information from the database.
        
        Returns:
            Dictionary containing covergroup details
        """
        from ucis.report.coverage_report_builder import CoverageReportBuilder
        
        # Build coverage report
        report = CoverageReportBuilder.build(self.db)
        
        # Collect covergroup data
        result = {
            "database": self.args.db,
            "covergroups": self._get_covergroups(report),
            "summary": {
                "total_covergroups": len(report.covergroups) if report.covergroups else 0,
                "overall_coverage": report.coverage,
            }
        }
        
        return result
    
    def _get_covergroups(self, report) -> List[Dict[str, Any]]:
        """Get detailed covergroup information."""
        covergroups = []
        
        if not report.covergroups:
            return covergroups
        
        for cg in report.covergroups:
            cg_data = {
                "name": cg.name,
                "coverage": cg.coverage,
                "weight": getattr(cg, 'weight', 1),
                "coverpoints": self._get_coverpoints(cg),
            }
            
            # Add statistics
            total_bins = 0
            covered_bins = 0
            if hasattr(cg, 'coverpoints') and cg.coverpoints:
                for cp in cg.coverpoints:
                    if hasattr(cp, 'bins') and cp.bins:
                        for bin in cp.bins:
                            total_bins += 1
                            if bin.count > 0:
                                covered_bins += 1
            
            cg_data["statistics"] = {
                "total_coverpoints": len(cg.coverpoints) if hasattr(cg, 'coverpoints') and cg.coverpoints else 0,
                "total_bins": total_bins,
                "covered_bins": covered_bins,
            }
            
            covergroups.append(cg_data)
        
        return covergroups
    
    def _get_coverpoints(self, cg) -> List[Dict[str, Any]]:
        """Get coverpoint details for a covergroup."""
        coverpoints = []
        
        if not hasattr(cg, 'coverpoints') or not cg.coverpoints:
            return coverpoints
        
        for cp in cg.coverpoints:
            cp_data = {
                "name": cp.name,
                "coverage": cp.coverage,
            }
            
            # Add bin information if requested
            if hasattr(self.args, 'include_bins') and self.args.include_bins:
                cp_data["bins"] = self._get_bins(cp)
            else:
                # Just counts
                if hasattr(cp, 'bins') and cp.bins:
                    cp_data["bin_count"] = len(cp.bins)
                    cp_data["covered_bin_count"] = sum(1 for b in cp.bins if b.count > 0)
            
            coverpoints.append(cp_data)
        
        return coverpoints
    
    def _get_bins(self, cp) -> List[Dict[str, Any]]:
        """Get bin details for a coverpoint."""
        bins = []
        
        if not hasattr(cp, 'bins') or not cp.bins:
            return bins
        
        for bin in cp.bins:
            bins.append({
                "name": bin.name,
                "count": bin.count,
                "at_least": getattr(bin, 'at_least', 1),
            })
        
        return bins
