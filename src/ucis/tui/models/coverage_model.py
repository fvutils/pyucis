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
        self.test_filter: Optional[str] = None  # Current test filter
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
                tests = self.get_all_tests()
                info['test_count'] = len(tests)
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
    
    def get_coverage_by_type(self, cov_type: CoverTypeT, filtered: bool = True) -> Dict[str, Any]:
        """
        Get coverage summary for a specific coverage type.
        
        Args:
            cov_type: Coverage type to query
            filtered: If True and test_filter is set, only count items from that test
            
        Returns:
            Dictionary with total, covered, and percentage
        """
        # Check if filtering is needed
        filter_active = filtered and self.test_filter is not None
        cache_key = f'coverage_type_{int(cov_type)}'
        if filter_active:
            cache_key += f'_filter_{self.test_filter}'
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Get filtered coveritem IDs if needed
        filtered_ids = None
        if filter_active:
            filtered_ids = self.get_coveritems_for_test(self.test_filter)
        
        result = {
            'type': cov_type,
            'total': 0,
            'covered': 0,
            'coverage': 0.0
        }
        
        def visit_scope(scope):
            try:
                for item in scope.coverItems(cov_type):
                    # If filtering, check if this item is in the filtered set
                    if filter_active:
                        # Get the coveritem ID
                        item_id = item.cover_id if hasattr(item, 'cover_id') else item.getKey()
                        if item_id not in filtered_ids:
                            continue
                    
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
    
    def get_all_tests(self) -> List[Dict[str, Any]]:
        """
        Get all tests from the database with contribution data.
        
        Returns:
            List of test dictionaries with name, status, date, and coverage metrics
        """
        if 'all_tests' in self._cache:
            return self._cache['all_tests']
        
        tests = []
        
        if not self.db:
            return tests
        
        # Try to get test coverage API if available
        try:
            from ucis.sqlite.sqlite_test_coverage import SqliteTestCoverage
            
            # Check if this is a SQLite database with test coverage support
            if hasattr(self.db, 'conn'):
                api = SqliteTestCoverage(self.db)  # Pass the SqliteUCIS object, not just conn
                
                # Get all tests and their contributions
                all_contribs = api.get_all_test_contributions()
                
                # Create test dictionary for each test
                # all_contribs is a list of TestCoverageInfo objects
                for contrib in all_contribs:
                    test_info = {
                        'name': contrib.test_name,
                        'status': 'PASSED',  # Default, will try to get from history
                        'date': 'Unknown',
                        'total_items': contrib.total_items,
                        'unique_items': contrib.unique_items,
                    }
                    
                    # Try to get additional info from history node
                    try:
                        for history_node in self.db.historyNodes():
                            if history_node.getLogicalName() == contrib.test_name:
                                # Get status (UCIS_TESTSTATUS_OK = 1, anything else is failure)
                                try:
                                    from ucis import UCIS_TESTSTATUS_OK
                                    status = history_node.getTestStatus()
                                    if status == UCIS_TESTSTATUS_OK:
                                        test_info['status'] = 'PASSED'
                                    else:
                                        test_info['status'] = 'FAILED'
                                except:
                                    pass
                                
                                # Get date
                                try:
                                    date = history_node.getDate()
                                    if date:
                                        test_info['date'] = date
                                except:
                                    pass
                                
                                break
                    except:
                        pass
                    
                    tests.append(test_info)
        except:
            # Fallback: just enumerate history nodes without contribution data
            try:
                from ucis.history_node_kind import HistoryNodeKind
                from ucis import UCIS_TESTSTATUS_OK
                
                for history_node in self.db.historyNodes(HistoryNodeKind.TEST):
                    test_info = {
                        'name': history_node.getLogicalName() or 'Unknown',
                        'status': 'UNKNOWN',
                        'date': 'Unknown',
                        'total_items': 0,
                        'unique_items': 0,
                    }
                    
                    try:
                        status = history_node.getTestStatus()
                        if status == UCIS_TESTSTATUS_OK:
                            test_info['status'] = 'PASSED'
                        else:
                            test_info['status'] = 'FAILED'
                    except:
                        pass
                    
                    try:
                        date = history_node.getDate()
                        if date:
                            test_info['date'] = date
                    except:
                        pass
                    
                    tests.append(test_info)
            except:
                pass
        
        self._cache['all_tests'] = tests
        return tests
    
    def set_test_filter(self, test_name: Optional[str]):
        """
        Set the current test filter.
        
        Args:
            test_name: Name of test to filter by, or None to clear filter
        """
        self.test_filter = test_name
        
        # Clear relevant caches when filter changes
        if 'code_coverage_summary' in self._cache:
            del self._cache['code_coverage_summary']
    
    def get_test_filter(self) -> Optional[str]:
        """
        Get the current test filter.
        
        Returns:
            Name of the filtered test, or None if no filter active
        """
        return self.test_filter
    
    def clear_test_filter(self):
        """Clear the current test filter."""
        self.set_test_filter(None)
    
    def get_coveritems_for_test(self, test_name: str) -> Set[int]:
        """
        Get set of coveritem IDs hit by a specific test.
        
        Args:
            test_name: Name of the test
            
        Returns:
            Set of coveritem IDs hit by this test
        """
        if not self.db or not hasattr(self.db, 'conn'):
            return set()
        
        try:
            from ucis.sqlite.sqlite_test_coverage import SqliteTestCoverage
            api = SqliteTestCoverage(self.db)
            
            # Get test's history_id
            history_id = None
            cursor = self.db.conn.cursor()
            cursor.execute("""
                SELECT history_id FROM history_nodes 
                WHERE logical_name = ?
            """, (test_name,))
            row = cursor.fetchone()
            if row:
                history_id = row[0]
            
            if history_id is None:
                return set()
            
            # Get coveritems for this test
            coveritems = api.get_coveritems_for_test(history_id)
            return set(coveritems)  # Already a list of IDs
        except:
            import traceback
            traceback.print_exc()
            return set()
