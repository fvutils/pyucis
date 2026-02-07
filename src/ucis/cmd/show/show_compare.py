"""
Show Compare Command

Compares coverage data between two UCIS databases.
"""
from typing import Any, Dict, List
from ucis.cmd.show_base import ShowBase


class ShowCompare(ShowBase):
    """
    Compare coverage between two databases.
    
    Shows:
    - Coverage deltas
    - New/removed bins
    - Coverage improvements/regressions
    """
    
    def get_data(self) -> Dict[str, Any]:
        """
        Compare two databases.
        
        Returns:
            Dictionary containing comparison results
        """
        from ucis.report.coverage_report_builder import CoverageReportBuilder
        from ucis.rgy.format_rgy import FormatRgy
        
        # Load second database
        rgy = FormatRgy.inst()
        if self.args.input_format is None:
            self.args.input_format = rgy.getDefaultDatabase()
        
        input_desc = rgy.getDatabaseDesc(self.args.input_format)
        input_if = input_desc.fmt_if()
        db2 = input_if.read(self.args.compare_db)
        
        try:
            # Build reports for both databases
            report1 = CoverageReportBuilder.build(self.db)
            report2 = CoverageReportBuilder.build(db2)
            
            result = {
                "baseline": self.args.db,
                "comparison": self.args.compare_db,
                "summary": self._compare_summary(report1, report2),
                "covergroup_changes": self._compare_covergroups(report1, report2),
                "bin_changes": self._get_bin_changes(report1, report2),
            }
            
        finally:
            db2.close()
        
        return result
    
    def _compare_summary(self, report1, report2) -> Dict[str, Any]:
        """Compare overall summary statistics."""
        cov1 = report1.coverage
        cov2 = report2.coverage
        delta = cov2 - cov1
        
        return {
            "baseline_coverage": cov1,
            "comparison_coverage": cov2,
            "delta": delta,
            "delta_percent": delta,
            "improved": delta > 0,
            "regression": delta < 0,
        }
    
    def _compare_covergroups(self, report1, report2) -> List[Dict[str, Any]]:
        """Compare covergroups between databases."""
        changes = []
        
        # Create maps of covergroups by name
        cg1_map = {cg.name: cg for cg in report1.covergroups} if report1.covergroups else {}
        cg2_map = {cg.name: cg for cg in report2.covergroups} if report2.covergroups else {}
        
        # Find all covergroup names
        all_names = set(cg1_map.keys()) | set(cg2_map.keys())
        
        for name in sorted(all_names):
            cg1 = cg1_map.get(name)
            cg2 = cg2_map.get(name)
            
            if cg1 and cg2:
                # Both present - compare
                delta = cg2.coverage - cg1.coverage
                changes.append({
                    "covergroup": name,
                    "status": "modified" if delta != 0 else "unchanged",
                    "baseline_coverage": cg1.coverage,
                    "comparison_coverage": cg2.coverage,
                    "delta": delta,
                })
            elif cg1 and not cg2:
                # Removed
                changes.append({
                    "covergroup": name,
                    "status": "removed",
                    "baseline_coverage": cg1.coverage,
                    "comparison_coverage": None,
                    "delta": None,
                })
            else:
                # Added
                changes.append({
                    "covergroup": name,
                    "status": "added",
                    "baseline_coverage": None,
                    "comparison_coverage": cg2.coverage,
                    "delta": None,
                })
        
        return changes
    
    def _get_bin_changes(self, report1, report2) -> Dict[str, Any]:
        """Analyze bin-level changes."""
        # Collect all bins from both databases
        bins1 = self._collect_bins(report1)
        bins2 = self._collect_bins(report2)
        
        newly_covered = []
        lost_coverage = []
        
        for key, count1 in bins1.items():
            count2 = bins2.get(key, 0)
            if count1 == 0 and count2 > 0:
                newly_covered.append(key)
            elif count1 > 0 and count2 == 0:
                lost_coverage.append(key)
        
        # Find bins only in db2 (newly added)
        new_bins = [k for k in bins2.keys() if k not in bins1]
        
        return {
            "newly_covered_bins": newly_covered,
            "newly_covered_count": len(newly_covered),
            "lost_coverage_bins": lost_coverage,
            "lost_coverage_count": len(lost_coverage),
            "new_bins": new_bins,
            "new_bins_count": len(new_bins),
        }
    
    def _collect_bins(self, report) -> Dict[str, int]:
        """Collect all bins from a report into a dictionary."""
        bins = {}
        
        if not report.covergroups:
            return bins
        
        for cg in report.covergroups:
            if hasattr(cg, 'coverpoints') and cg.coverpoints:
                for cp in cg.coverpoints:
                    if hasattr(cp, 'bins') and cp.bins:
                        for bin in cp.bins:
                            key = f"{cg.name}.{cp.name}.{bin.name}"
                            bins[key] = bin.count
        
        return bins
