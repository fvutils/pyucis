"""
Show Summary Command

Displays high-level coverage summary including overall coverage
percentages, statistics by coverage type, and test information.
"""
from typing import Any, Dict
from ucis.cmd.show_base import ShowBase


class ShowSummary(ShowBase):
    """
    Display overall coverage summary.
    
    Provides:
    - Overall coverage percentage
    - Coverage by type (functional, code, assertion)
    - Test statistics
    - Coverage scope counts
    """
    
    def get_data(self) -> Dict[str, Any]:
        """
        Extract summary data from the database.
        
        Returns:
            Dictionary containing summary information
        """
        from ucis.report.coverage_report_builder import CoverageReportBuilder
        
        # Build coverage report
        report = CoverageReportBuilder.build(self.db)
        
        # Collect overall statistics
        summary = {
            "database": self.args.db,
            "overall_coverage": report.coverage,
            "coverage_by_type": self._get_coverage_by_type(report),
            "statistics": self._get_statistics(report),
            "tests": self._get_test_info(),
        }
        
        return summary
    
    def _get_coverage_by_type(self, report) -> Dict[str, Any]:
        """Extract coverage percentages by type."""
        coverage_by_type = {}
        
        # Functional coverage (covergroups)
        if report.covergroups:
            total_weight = 0
            weighted_coverage = 0.0
            for cg in report.covergroups:
                weight = getattr(cg, 'weight', 1)
                total_weight += weight
                weighted_coverage += cg.coverage * weight
            
            coverage_by_type['functional'] = {
                'coverage': weighted_coverage / total_weight if total_weight > 0 else 0.0,
                'covergroups': len(report.covergroups)
            }
        else:
            coverage_by_type['functional'] = {
                'coverage': 0.0,
                'covergroups': 0
            }
        
        # Note: Code coverage and assertions would be added when those
        # data structures are available in the report builder
        
        return coverage_by_type
    
    def _get_statistics(self, report) -> Dict[str, Any]:
        """Get coverage statistics."""
        stats = {
            'total_covergroups': len(report.covergroups) if report.covergroups else 0,
        }
        
        # Count coverpoints and bins
        total_coverpoints = 0
        total_bins = 0
        covered_bins = 0
        
        if report.covergroups:
            for cg in report.covergroups:
                if hasattr(cg, 'coverpoints') and cg.coverpoints:
                    total_coverpoints += len(cg.coverpoints)
                    for cp in cg.coverpoints:
                        if hasattr(cp, 'bins') and cp.bins:
                            total_bins += len(cp.bins)
                            covered_bins += sum(1 for bin in cp.bins if bin.count > 0)
        
        stats['total_coverpoints'] = total_coverpoints
        stats['total_bins'] = total_bins
        stats['covered_bins'] = covered_bins
        
        return stats
    
    def _get_test_info(self) -> Dict[str, Any]:
        """Get test execution information."""
        from ucis import UCIS_HISTORYNODE_TEST
        from ucis.history_node_kind import HistoryNodeKind
        
        tests = []
        
        # Get all test history nodes
        try:
            for node in self.db.historyNodes(HistoryNodeKind.TEST):
                test_data = node.getTestData()
                if test_data:
                    tests.append({
                        'name': node.getLogicalName(),
                        'status': test_data.teststatus,
                        'date': test_data.date if hasattr(test_data, 'date') else None,
                    })
        except Exception:
            # If historyNodes fails, just return empty
            pass
        
        return {
            'total_tests': len(tests),
            'tests': tests
        }
