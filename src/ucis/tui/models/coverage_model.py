"""
Coverage data model wrapper.

Provides a convenient interface to PyUCIS API with caching.
"""
from typing import Dict, Any, Optional
from ucis.rgy.format_rgy import FormatRgy


class CoverageModel:
    """
    Wraps PyUCIS API with caching and convenience methods.
    """
    
    def __init__(self, db_path: str, input_format: Optional[str] = None):
        """
        Initialize coverage model.
        
        Args:
            db_path: Path to the UCIS database
            input_format: Database format (default: auto-detect)
        """
        self.db_path = db_path
        self.db = None
        self._cache: Dict[str, Any] = {}
        self._load_database(input_format)
    
    def _load_database(self, input_format: Optional[str] = None):
        """Load the UCIS database."""
        rgy = FormatRgy.inst()
        
        if input_format is None:
            input_format = rgy.getDefaultDatabase()
        
        if not rgy.hasDatabaseFormat(input_format):
            raise Exception(f"Unknown format: {input_format}")
        
        input_desc = rgy.getDatabaseDesc(input_format)
        input_if = input_desc.fmt_if()
        self.db = input_if.read(self.db_path)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get overall coverage summary.
        
        Returns:
            Dictionary with summary statistics
        """
        if 'summary' in self._cache:
            return self._cache['summary']
        
        # Compute summary
        summary = {
            'overall_coverage': 0.0,
            'total_bins': 0,
            'covered_bins': 0,
            'covergroups': 0,
            'coverpoints': 0,
            'by_type': {}
        }
        
        # Walk through database to compute statistics
        def visit_scope(scope, depth=0):
            from ucis.scope_type_t import ScopeTypeT
            
            scope_type = scope.getScopeType()
            if scope_type in (ScopeTypeT.COVERGROUP,):
                summary['covergroups'] += 1
            
            # Visit children
            from ucis.scope_type_t import ScopeTypeT
            for child in scope.scopes(ScopeTypeT.ALL):
                visit_scope(child, depth + 1)
            
            # Count coveritems
            try:
                for item in scope.coverItems():
                    summary['total_bins'] += 1
                    count = item.getCount()
                    if count > 0:
                        summary['covered_bins'] += 1
            except:
                pass  # Not all scopes have cover items
        
        if self.db:
            from ucis.scope_type_t import ScopeTypeT
            for scope in self.db.scopes(ScopeTypeT.ALL):
                visit_scope(scope)
        
        # Calculate percentage
        if summary['total_bins'] > 0:
            summary['overall_coverage'] = (summary['covered_bins'] / summary['total_bins']) * 100
        
        self._cache['summary'] = summary
        return summary
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        Get database metadata.
        
        Returns:
            Dictionary with database information
        """
        info = {
            'path': self.db_path,
            'format': 'UCIS',
            'test_count': 0,
        }
        
        # Get test data if available
        if self.db:
            try:
                history = self.db.historyNodes()
                info['test_count'] = len(list(history)) if history else 0
            except:
                pass
        
        return info
    
    def close(self):
        """Close the database."""
        if self.db:
            self.db.close()
            self.db = None
