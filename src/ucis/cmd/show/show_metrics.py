"""
Show Metrics Command

Calculates and displays various coverage metrics and statistics.
"""
from typing import Any, Dict
from ucis.cmd.show_base import ShowBase


class ShowMetrics(ShowBase):
    """
    Display coverage metrics.
    
    Shows:
    - Detailed coverage metrics
    - Goal achievement statistics
    - Coverage distribution
    """
    
    def get_data(self) -> Dict[str, Any]:
        """
        Calculate coverage metrics from the database.
        
        Returns:
            Dictionary containing metrics
        """
        from ucis.report.coverage_report_builder import CoverageReportBuilder
        
        # Build coverage report
        report = CoverageReportBuilder.build(self.db)
        
        result = {
            "database": self.args.db,
            "metrics": {
                "overall": self._get_overall_metrics(report),
                "functional": self._get_functional_metrics(report),
                "bin_distribution": self._get_bin_distribution(report),
            }
        }
        
        return result
    
    def _get_overall_metrics(self, report) -> Dict[str, Any]:
        """Calculate overall coverage metrics."""
        total_bins = 0
        covered_bins = 0
        total_hits = 0
        
        if report.covergroups:
            for cg in report.covergroups:
                if hasattr(cg, 'coverpoints') and cg.coverpoints:
                    for cp in cg.coverpoints:
                        if hasattr(cp, 'bins') and cp.bins:
                            for bin in cp.bins:
                                total_bins += 1
                                if bin.count > 0:
                                    covered_bins += 1
                                total_hits += bin.count
        
        return {
            "overall_coverage": report.coverage,
            "total_bins": total_bins,
            "covered_bins": covered_bins,
            "uncovered_bins": total_bins - covered_bins,
            "coverage_percentage": (covered_bins / total_bins * 100) if total_bins > 0 else 0,
            "total_hits": total_hits,
            "average_hits_per_bin": (total_hits / covered_bins) if covered_bins > 0 else 0,
        }
    
    def _get_functional_metrics(self, report) -> Dict[str, Any]:
        """Calculate functional coverage metrics."""
        total_covergroups = len(report.covergroups) if report.covergroups else 0
        total_coverpoints = 0
        fully_covered_coverpoints = 0
        partial_coverpoints = 0
        empty_coverpoints = 0
        
        if report.covergroups:
            for cg in report.covergroups:
                if hasattr(cg, 'coverpoints') and cg.coverpoints:
                    for cp in cg.coverpoints:
                        total_coverpoints += 1
                        if cp.coverage == 100.0:
                            fully_covered_coverpoints += 1
                        elif cp.coverage > 0:
                            partial_coverpoints += 1
                        else:
                            empty_coverpoints += 1
        
        return {
            "total_covergroups": total_covergroups,
            "total_coverpoints": total_coverpoints,
            "fully_covered_coverpoints": fully_covered_coverpoints,
            "partially_covered_coverpoints": partial_coverpoints,
            "empty_coverpoints": empty_coverpoints,
            "coverpoint_completion_rate": (fully_covered_coverpoints / total_coverpoints * 100) if total_coverpoints > 0 else 0,
        }
    
    def _get_bin_distribution(self, report) -> Dict[str, Any]:
        """Analyze bin hit distribution."""
        hit_counts = []
        
        if report.covergroups:
            for cg in report.covergroups:
                if hasattr(cg, 'coverpoints') and cg.coverpoints:
                    for cp in cg.coverpoints:
                        if hasattr(cp, 'bins') and cp.bins:
                            for bin in cp.bins:
                                hit_counts.append(bin.count)
        
        if not hit_counts:
            return {
                "min_hits": 0,
                "max_hits": 0,
                "median_hits": 0,
            }
        
        hit_counts_sorted = sorted(hit_counts)
        n = len(hit_counts_sorted)
        
        return {
            "min_hits": hit_counts_sorted[0],
            "max_hits": hit_counts_sorted[-1],
            "median_hits": hit_counts_sorted[n // 2] if n > 0 else 0,
            "bins_with_zero_hits": sum(1 for h in hit_counts if h == 0),
            "bins_with_single_hit": sum(1 for h in hit_counts if h == 1),
            "bins_with_multiple_hits": sum(1 for h in hit_counts if h > 1),
        }
