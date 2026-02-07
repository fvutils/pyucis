"""
Show Bins Command

Displays detailed bin-level coverage information with filtering options.
"""
from typing import Any, Dict, List
from ucis.cmd.show_base import ShowBase


class ShowBins(ShowBase):
    """
    Display bin-level coverage details.
    
    Shows:
    - All bins with hit counts
    - Filtering by covergroup/coverpoint
    - Sorting options
    """
    
    def get_data(self) -> Dict[str, Any]:
        """
        Extract bin information from the database.
        
        Returns:
            Dictionary containing bin details
        """
        from ucis.report.coverage_report_builder import CoverageReportBuilder
        
        # Build coverage report
        report = CoverageReportBuilder.build(self.db)
        
        # Collect bin data
        result = {
            "database": self.args.db,
            "bins": self._get_bins(report),
        }
        
        # Add filter metadata
        filters = []
        if hasattr(self.args, 'covergroup') and self.args.covergroup:
            filters.append(f"covergroup={self.args.covergroup}")
        if hasattr(self.args, 'coverpoint') and self.args.coverpoint:
            filters.append(f"coverpoint={self.args.coverpoint}")
        if hasattr(self.args, 'min_hits') and self.args.min_hits is not None:
            filters.append(f"min_hits={self.args.min_hits}")
        if hasattr(self.args, 'max_hits') and self.args.max_hits is not None:
            filters.append(f"max_hits={self.args.max_hits}")
        
        if filters:
            result["filters"] = filters
        
        result["total_bins"] = len(result["bins"])
        
        return result
    
    def _get_bins(self, report) -> List[Dict[str, Any]]:
        """Get all bins with filtering."""
        bins = []
        
        cg_filter = getattr(self.args, 'covergroup', None)
        cp_filter = getattr(self.args, 'coverpoint', None)
        min_hits = getattr(self.args, 'min_hits', None)
        max_hits = getattr(self.args, 'max_hits', None)
        
        if not report.covergroups:
            return bins
        
        for cg in report.covergroups:
            # Filter by covergroup
            if cg_filter and cg.name != cg_filter:
                continue
            
            if hasattr(cg, 'coverpoints') and cg.coverpoints:
                for cp in cg.coverpoints:
                    # Filter by coverpoint
                    if cp_filter and cp.name != cp_filter:
                        continue
                    
                    if hasattr(cp, 'bins') and cp.bins:
                        for bin in cp.bins:
                            # Filter by hit count
                            if min_hits is not None and bin.count < min_hits:
                                continue
                            if max_hits is not None and bin.count > max_hits:
                                continue
                            
                            bins.append({
                                "covergroup": cg.name,
                                "coverpoint": cp.name,
                                "bin": bin.name,
                                "count": bin.count,
                                "at_least": getattr(bin, 'at_least', 1),
                                "goal_met": bin.count >= getattr(bin, 'at_least', 1),
                            })
        
        # Sort if requested
        sort_by = getattr(self.args, 'sort', None)
        if sort_by == 'count':
            bins.sort(key=lambda x: x['count'], reverse=True)
        elif sort_by == 'name':
            bins.sort(key=lambda x: (x['covergroup'], x['coverpoint'], x['bin']))
        
        return bins
