"""
Coverage data model wrapper.

Provides a convenient interface to PyUCIS API with caching.
All metric computation is delegated to ``CoverageMetrics`` — the single
source of truth — to ensure consistency across TUI, CLI and report output.
"""
from typing import Dict, Any, Optional, List, Set
from ucis.rgy.format_rgy import FormatRgy
from ucis.cover_type_t import CoverTypeT
from ucis.scope_type_t import ScopeTypeT


class CoverageModel:
    """
    Wraps PyUCIS API with caching and convenience methods.

    Delegates all metric computation to :class:`~ucis.report.coverage_metrics.CoverageMetrics`.
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
        self._metrics = None
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
        self._metrics = None  # reset on reload

    @property
    def metrics(self):
        """
        Lazily-constructed :class:`~ucis.report.coverage_metrics.CoverageMetrics`
        instance.  This is the canonical source of all coverage numbers.
        """
        if self._metrics is None and self.db is not None:
            from ucis.report.coverage_metrics import CoverageMetrics
            self._metrics = CoverageMetrics(self.db)
        return self._metrics
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get overall coverage summary.
        
        Returns:
            Dictionary with summary statistics
        """
        if 'summary' in self._cache:
            return self._cache['summary']

        summary = {'overall_coverage': 0.0, 'total_bins': 0, 'covered_bins': 0,
                   'covergroups': 0, 'coverpoints': 0, 'by_type': {}}

        if self.metrics is not None:
            summary.update(self.metrics.summary())

        self._cache['summary'] = summary
        return summary
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        Get database metadata.
        
        Returns:
            Dictionary with database information
        """
        info = {'path': self.db_path, 'format': 'UCIS', 'test_count': 0}
        if self.metrics is not None:
            m_info = self.metrics.database_info()
            info['test_count'] = m_info.get('test_count', 0)
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
        if self.metrics is not None:
            return self.metrics.coverage_types_present()
        return []
    
    def get_code_coverage_summary(self) -> Dict[str, Any]:
        """
        Get code coverage summary (line, branch, toggle statistics).
        
        Returns:
            Dictionary with code coverage statistics by type
        """
        if 'code_coverage_summary' in self._cache:
            return self._cache['code_coverage_summary']

        summary = {
            'line':       {'total': 0, 'covered': 0, 'coverage': 0.0},
            'branch':     {'total': 0, 'covered': 0, 'coverage': 0.0},
            'toggle':     {'total': 0, 'covered': 0, 'coverage': 0.0},
            'expression': {'total': 0, 'covered': 0, 'coverage': 0.0},
            'condition':  {'total': 0, 'covered': 0, 'coverage': 0.0},
            'fsm':        {'total': 0, 'covered': 0, 'coverage': 0.0},
            'block':      {'total': 0, 'covered': 0, 'coverage': 0.0},
        }

        if self.metrics is not None:
            type_map = {
                CoverTypeT.STMTBIN:   'line',
                CoverTypeT.BRANCHBIN: 'branch',
                CoverTypeT.TOGGLEBIN: 'toggle',
                CoverTypeT.EXPRBIN:   'expression',
                CoverTypeT.CONDBIN:   'condition',
                CoverTypeT.FSMBIN:    'fsm',
                CoverTypeT.BLOCKBIN:  'block',
            }
            by_type = self.metrics.code_coverage_by_type()
            for ct, key in type_map.items():
                bs = by_type.get(ct)
                if bs:
                    summary[key]['total']    = bs.total
                    summary[key]['covered']  = bs.covered
                    summary[key]['coverage'] = bs.coverage_pct

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
        test_filter = self.test_filter if filtered else None
        cache_key = f'coverage_type_{int(cov_type)}_{test_filter}'
        if cache_key in self._cache:
            return self._cache[cache_key]

        result = {'type': cov_type, 'total': 0, 'covered': 0, 'coverage': 0.0}
        if self.metrics is not None:
            bs = self.metrics.bins_by_type(cov_type, test_filter=test_filter)
            result['total']    = bs.total
            result['covered']  = bs.covered
            result['coverage'] = bs.coverage_pct
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
        if self.metrics is not None:
            for ti in self.metrics.tests():
                tests.append({
                    'name':         ti.name,
                    'status':       ti.status,
                    'date':         ti.date,
                    'total_items':  ti.total_items,
                    'unique_items': ti.unique_items,
                })
        self._cache['all_tests'] = tests
        return tests
    
    def set_test_filter(self, test_name: Optional[str]):
        """
        Set the current test filter.
        
        Args:
            test_name: Name of test to filter by, or None to clear filter
        """
        self.test_filter = test_name
        # Invalidate all caches — metrics and coverage-type caches all depend on filter
        self._cache.clear()
        if self._metrics is not None:
            self._metrics.invalidate()
    
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

    def get_testplan_closure(self) -> dict:
        """Compute testplan closure using the embedded testplan (if any).

        Returns a dict with keys ``results`` (list of row dicts) and
        ``summary`` (ClosureSummary-derived dict), or empty when no testplan
        is available.

        Each row dict contains: testpoint, stage, status, pass_count,
        fail_count, matched_tests, desc.
        """
        if 'testplan_closure' in self._cache:
            return self._cache['testplan_closure']

        result = {"results": [], "summary": None}
        try:
            from ucis.ncdb.testplan import get_testplan
            from ucis.ncdb.testplan_closure import TPStatus, compute_closure
            from ucis.ncdb.reports import report_testpoint_closure, _STATUS_LABEL

            plan = get_testplan(self.db)
            if plan is None:
                self._cache['testplan_closure'] = result
                return result

            tp_results = compute_closure(plan, self.db)
            summary = report_testplan_closure = report_testpoint_closure(tp_results)

            rows = []
            for r in tp_results:
                rows.append({
                    "testpoint":    r.testpoint.name,
                    "stage":        r.testpoint.stage or "?",
                    "status":       _STATUS_LABEL[r.status],
                    "pass_count":   r.pass_count,
                    "fail_count":   r.fail_count,
                    "matched_tests": r.matched_tests,
                    "desc":         r.testpoint.desc or "",
                })

            # Serialisable summary for the header
            summary_dict = {
                "total":        summary.total,
                "total_closed": summary.total_closed,
                "total_na":     summary.total_na,
                "by_stage":     summary.by_stage,
            }
            result = {"results": rows, "summary": summary_dict}
        except Exception:
            pass

        self._cache['testplan_closure'] = result
        return result

    def get_v2_test_stats(self, test_name: str):
        """Return v2 TestStatsEntry for *test_name* when db is NcdbUCIS.

        Returns None when v2 history is unavailable or the test is unknown.
        """
        try:
            return self.db.get_test_stats(test_name)
        except Exception:
            return None
