"""
Coverage data model wrapper.

Provides a convenient interface to PyUCIS API with caching.
"""
from typing import Dict, Any, Optional, List, Set
from ucis.rgy.format_rgy import FormatRgy
from ucis.cover_type_t import CoverTypeT
from ucis.scope_type_t import ScopeTypeT


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
            # Try to detect format from file
            detected_format = rgy.detectDatabaseFormat(self.db_path)
            if detected_format is not None:
                input_format = detected_format
            else:
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
            from ucis.cover_type_t import CoverTypeT
            
            scope_type = scope.getScopeType()
            if scope_type in (ScopeTypeT.COVERGROUP,):
                summary['covergroups'] += 1
                # Covergroups have coverpoints
                for cp in scope.scopes(ScopeTypeT.COVERPOINT):
                    summary['coverpoints'] += 1
                    # Coverpoints have bins
                    try:
                        for bin_idx in cp.coverItems(CoverTypeT.CVGBIN):
                            summary['total_bins'] += 1
                            cover_data = bin_idx.getCoverData()
                            if cover_data:
                                # Check if bin has been hit (data > 0 or data >= goal)
                                if cover_data.data > 0:
                                    summary['covered_bins'] += 1
                    except Exception as e:
                        pass
            
            # Visit children recursively
            try:
                for child in scope.scopes(ScopeTypeT.ALL):
                    visit_scope(child, depth + 1)
            except:
                pass
        
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
    
    def get_coverage_types(self) -> List[CoverTypeT]:
        """
        Get list of coverage types present in the database.
        
        Returns:
            List of CoverTypeT values found in the database
        """
        if 'coverage_types' in self._cache:
            return self._cache['coverage_types']
        
        types_found: Set[CoverTypeT] = set()
        
        def visit_scope(scope):
            # Check all coverage item types in this scope
            for cov_type in [CoverTypeT.CVGBIN, CoverTypeT.STMTBIN, CoverTypeT.BRANCHBIN, 
                            CoverTypeT.TOGGLEBIN, CoverTypeT.EXPRBIN, CoverTypeT.CONDBIN,
                            CoverTypeT.FSMBIN, CoverTypeT.BLOCKBIN]:
                try:
                    items = list(scope.coverItems(cov_type))
                    if items:
                        types_found.add(cov_type)
                except:
                    pass
            
            # Visit children recursively
            try:
                for child in scope.scopes(ScopeTypeT.ALL):
                    visit_scope(child)
            except:
                pass
        
        if self.db:
            for scope in self.db.scopes(ScopeTypeT.ALL):
                visit_scope(scope)
        
        types_list = sorted(list(types_found), key=lambda t: int(t))
        self._cache['coverage_types'] = types_list
        return types_list
    
    def get_code_coverage_summary(self) -> Dict[str, Any]:
        """
        Get code coverage summary (line, branch, toggle statistics).
        
        Returns:
            Dictionary with code coverage statistics by type
        """
        if 'code_coverage_summary' in self._cache:
            return self._cache['code_coverage_summary']
        
        summary = {
            'line': {'total': 0, 'covered': 0, 'coverage': 0.0},
            'branch': {'total': 0, 'covered': 0, 'coverage': 0.0},
            'toggle': {'total': 0, 'covered': 0, 'coverage': 0.0},
            'expression': {'total': 0, 'covered': 0, 'coverage': 0.0},
            'condition': {'total': 0, 'covered': 0, 'coverage': 0.0},
            'fsm': {'total': 0, 'covered': 0, 'coverage': 0.0},
            'block': {'total': 0, 'covered': 0, 'coverage': 0.0},
        }
        
        type_map = {
            CoverTypeT.STMTBIN: 'line',
            CoverTypeT.BRANCHBIN: 'branch',
            CoverTypeT.TOGGLEBIN: 'toggle',
            CoverTypeT.EXPRBIN: 'expression',
            CoverTypeT.CONDBIN: 'condition',
            CoverTypeT.FSMBIN: 'fsm',
            CoverTypeT.BLOCKBIN: 'block',
        }
        
        def visit_scope(scope):
            for cov_type, key in type_map.items():
                try:
                    for item in scope.coverItems(cov_type):
                        summary[key]['total'] += 1
                        cover_data = item.getCoverData()
                        if cover_data and cover_data.data > 0:
                            summary[key]['covered'] += 1
                except:
                    pass
            
            # Visit children
            try:
                for child in scope.scopes(ScopeTypeT.ALL):
                    visit_scope(child)
            except:
                pass
        
        if self.db:
            for scope in self.db.scopes(ScopeTypeT.ALL):
                visit_scope(scope)
        
        # Calculate percentages
        for key in summary:
            if summary[key]['total'] > 0:
                summary[key]['coverage'] = (summary[key]['covered'] / summary[key]['total']) * 100
        
        self._cache['code_coverage_summary'] = summary
        return summary
    
    def get_coverage_by_type(self, cov_type: CoverTypeT) -> Dict[str, Any]:
        """
        Get coverage summary for a specific coverage type.
        
        Args:
            cov_type: Coverage type to query
            
        Returns:
            Dictionary with total, covered, and percentage
        """
        cache_key = f'coverage_type_{int(cov_type)}'
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        result = {
            'type': cov_type,
            'total': 0,
            'covered': 0,
            'coverage': 0.0
        }
        
        def visit_scope(scope):
            try:
                for item in scope.coverItems(cov_type):
                    result['total'] += 1
                    cover_data = item.getCoverData()
                    if cover_data and cover_data.data > 0:
                        result['covered'] += 1
            except:
                pass
            
            # Visit children
            try:
                for child in scope.scopes(ScopeTypeT.ALL):
                    visit_scope(child)
            except:
                pass
        
        if self.db:
            for scope in self.db.scopes(ScopeTypeT.ALL):
                visit_scope(scope)
        
        # Calculate percentage
        if result['total'] > 0:
            result['coverage'] = (result['covered'] / result['total']) * 100
        
        self._cache[cache_key] = result
        return result
