"""
Show Hotspots Command

Identifies coverage hotspots - areas that need attention or have high value.
"""
from typing import Any, Dict, List
from ucis.cmd.show_base import ShowBase


class ShowHotspots(ShowBase):
    """
    Identify coverage hotspots.
    
    Shows:
    - Low-coverage items that impact overall coverage
    - High-value targets for increasing coverage
    - Areas with poor bin coverage
    """
    
    def get_data(self) -> Dict[str, Any]:
        """
        Identify coverage hotspots.
        
        Returns:
            Dictionary containing hotspot analysis
        """
        from ucis.report.coverage_report_builder import CoverageReportBuilder
        
        # Build coverage report
        report = CoverageReportBuilder.build(self.db)
        
        result = {
            "database": self.args.db,
            "hotspots": {
                "low_coverage_covergroups": self._find_low_coverage_groups(report),
                "incomplete_coverpoints": self._find_incomplete_coverpoints(report),
                "high_value_targets": self._find_high_value_targets(report),
            },
            "recommendations": self._generate_recommendations(report),
        }
        
        return result
    
    def _find_low_coverage_groups(self, report) -> List[Dict[str, Any]]:
        """Find covergroups with low coverage."""
        threshold = getattr(self.args, 'threshold', 80.0)
        low_groups = []
        
        if not report.covergroups:
            return low_groups
        
        for cg in report.covergroups:
            if cg.coverage < threshold:
                # Calculate impact on overall coverage
                weight = getattr(cg, 'weight', 1)
                impact = (100 - cg.coverage) * weight
                
                low_groups.append({
                    "covergroup": cg.name,
                    "coverage": cg.coverage,
                    "weight": weight,
                    "impact_score": impact,
                    "gap": 100 - cg.coverage,
                })
        
        # Sort by impact score
        low_groups.sort(key=lambda x: x['impact_score'], reverse=True)
        
        # Limit results
        limit = getattr(self.args, 'limit', 10)
        return low_groups[:limit]
    
    def _find_incomplete_coverpoints(self, report) -> List[Dict[str, Any]]:
        """Find coverpoints with partial coverage."""
        incomplete = []
        
        if not report.covergroups:
            return incomplete
        
        for cg in report.covergroups:
            if hasattr(cg, 'coverpoints') and cg.coverpoints:
                for cp in cg.coverpoints:
                    if 0 < cp.coverage < 100:
                        # Count bins
                        total_bins = 0
                        uncovered_bins = 0
                        if hasattr(cp, 'bins') and cp.bins:
                            for bin in cp.bins:
                                total_bins += 1
                                if bin.count == 0:
                                    uncovered_bins += 1
                        
                        incomplete.append({
                            "covergroup": cg.name,
                            "coverpoint": cp.name,
                            "coverage": cp.coverage,
                            "total_bins": total_bins,
                            "uncovered_bins": uncovered_bins,
                            "effort_estimate": uncovered_bins,
                        })
        
        # Sort by effort (fewer uncovered bins = easier to complete)
        incomplete.sort(key=lambda x: x['effort_estimate'])
        
        # Limit results
        limit = getattr(self.args, 'limit', 10)
        return incomplete[:limit]
    
    def _find_high_value_targets(self, report) -> List[Dict[str, Any]]:
        """Find high-value coverage targets."""
        targets = []
        
        if not report.covergroups:
            return targets
        
        for cg in report.covergroups:
            if hasattr(cg, 'coverpoints') and cg.coverpoints:
                for cp in cg.coverpoints:
                    if cp.coverage < 100:
                        # Calculate value score based on:
                        # - How close to completion (higher coverage = higher value)
                        # - Number of remaining bins (fewer = easier)
                        remaining_bins = 0
                        if hasattr(cp, 'bins') and cp.bins:
                            remaining_bins = sum(1 for b in cp.bins if b.count == 0)
                        
                        if remaining_bins > 0 and remaining_bins <= 5:
                            # High value if close to completion
                            value_score = cp.coverage / remaining_bins
                            
                            targets.append({
                                "covergroup": cg.name,
                                "coverpoint": cp.name,
                                "current_coverage": cp.coverage,
                                "remaining_bins": remaining_bins,
                                "value_score": value_score,
                                "reason": f"Only {remaining_bins} bins left to reach 100%",
                            })
        
        # Sort by value score
        targets.sort(key=lambda x: x['value_score'], reverse=True)
        
        # Limit results
        limit = getattr(self.args, 'limit', 10)
        return targets[:limit]
    
    def _generate_recommendations(self, report) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Overall coverage check
        if report.coverage < 80:
            recommendations.append(
                f"Overall coverage is {report.coverage:.1f}%. Focus on low-coverage covergroups first."
            )
        elif report.coverage >= 95:
            recommendations.append(
                "Excellent coverage! Focus on completing partially-covered coverpoints."
            )
        else:
            recommendations.append(
                f"Good progress at {report.coverage:.1f}%. Target high-value coverpoints for quick wins."
            )
        
        # Count gaps
        total_bins = 0
        uncovered_bins = 0
        if report.covergroups:
            for cg in report.covergroups:
                if hasattr(cg, 'coverpoints') and cg.coverpoints:
                    for cp in cg.coverpoints:
                        if hasattr(cp, 'bins') and cp.bins:
                            for bin in cp.bins:
                                total_bins += 1
                                if bin.count == 0:
                                    uncovered_bins += 1
        
        if uncovered_bins > 0:
            recommendations.append(
                f"{uncovered_bins} of {total_bins} bins uncovered. "
                f"Use 'ucis show gaps --threshold 100' to see details."
            )
        
        return recommendations
