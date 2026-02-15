# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
SQLite-backed test-coverage query API.

Provides methods to query the relationship between tests (history nodes)
and coverage items, enabling analysis of:
- Which tests hit specific coverage items
- What coverage each test provides
- Unique coverage per test
- Test contribution to overall goals
- Optimal test set selection
"""

from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass


@dataclass
class TestCoverageInfo:
    """Information about a test's coverage contribution."""
    history_id: int
    test_name: str
    total_items: int
    unique_items: int
    total_contribution: int
    coverage_percent: float


@dataclass
class CoverItemTestInfo:
    """Information about which tests hit a coveritem."""
    cover_id: int
    total_hits: int
    tests: List[Tuple[int, str, int]]  # (history_id, test_name, contribution)


class SqliteTestCoverage:
    """Query interface for test-coveritem associations in SQLite backend.
    
    This class provides methods to query and analyze the relationship between
    test history nodes and coverage items. It operates on the coveritem_tests
    table which records which tests incremented which coverage items.
    
    Example:
        >>> from ucis.sqlite.sqlite_ucis import SqliteUCIS
        >>> db = SqliteUCIS('coverage.cdb')
        >>> test_cov = SqliteTestCoverage(db)
        >>> 
        >>> # Find which tests hit a specific coveritem
        >>> info = test_cov.get_tests_for_coveritem(42)
        >>> for history_id, test_name, hits in info.tests:
        ...     print(f"{test_name}: {hits} hits")
        >>>
        >>> # Get contribution for all tests
        >>> contributions = test_cov.get_all_test_contributions()
        >>> for info in contributions:
        ...     print(f"{info.test_name}: {info.coverage_percent:.1f}%")
    """
    
    def __init__(self, ucis_db):
        """Initialize with UCIS database.
        
        Args:
            ucis_db: SqliteUCIS database instance
        """
        self.db = ucis_db
        self.conn = ucis_db.conn
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Ensure performance indexes exist on coveritem_tests table."""
        try:
            # Index for finding tests by coveritem
            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_coveritem_tests_cover 
                ON coveritem_tests(cover_id)
            """)
            
            # Index for finding coveritems by test
            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_coveritem_tests_history 
                ON coveritem_tests(history_id)
            """)
            
            self.conn.commit()
        except Exception as e:
            # Indexes might already exist or database might be read-only
            pass
    
    def record_test_association(self, cover_id: int, history_id: int, 
                               contribution: int = 1):
        """Record that a test hit a coverage item.
        
        Args:
            cover_id: Coveritem ID
            history_id: History node (test) ID
            contribution: How much this test contributed to the count (default 1)
        """
        self.conn.execute("""
            INSERT OR REPLACE INTO coveritem_tests 
            (cover_id, history_id, count_contribution)
            VALUES (?, ?, ?)
        """, (cover_id, history_id, contribution))
    
    def get_tests_for_coveritem(self, cover_id: int) -> CoverItemTestInfo:
        """Find which tests hit a specific coveritem.
        
        Args:
            cover_id: Coveritem ID to query
            
        Returns:
            CoverItemTestInfo with list of tests that hit this item
        """
        cursor = self.conn.execute("""
            SELECT 
                ct.history_id,
                hn.logical_name,
                ct.count_contribution
            FROM coveritem_tests ct
            JOIN history_nodes hn ON ct.history_id = hn.history_id
            WHERE ct.cover_id = ?
            ORDER BY ct.count_contribution DESC
        """, (cover_id,))
        
        tests = []
        total_hits = 0
        for row in cursor.fetchall():
            history_id, test_name, contribution = row
            tests.append((history_id, test_name, contribution))
            total_hits += contribution
        
        return CoverItemTestInfo(
            cover_id=cover_id,
            total_hits=total_hits,
            tests=tests
        )
    
    def get_coveritems_for_test(self, history_id: int) -> List[int]:
        """Get all coveritems hit by a specific test.
        
        Args:
            history_id: Test history node ID
            
        Returns:
            List of coveritem IDs hit by this test
        """
        cursor = self.conn.execute("""
            SELECT cover_id 
            FROM coveritem_tests
            WHERE history_id = ?
        """, (history_id,))
        
        return [row[0] for row in cursor.fetchall()]
    
    def get_unique_coveritems(self, history_id: int) -> List[int]:
        """Get coveritems hit ONLY by this test (not by any other test).
        
        Args:
            history_id: Test history node ID
            
        Returns:
            List of coveritem IDs uniquely hit by this test
        """
        cursor = self.conn.execute("""
            SELECT cover_id 
            FROM coveritem_tests
            WHERE history_id = ?
            AND cover_id NOT IN (
                SELECT cover_id 
                FROM coveritem_tests 
                WHERE history_id != ?
            )
        """, (history_id, history_id))
        
        return [row[0] for row in cursor.fetchall()]
    
    def get_test_contribution(self, history_id: int) -> Optional[TestCoverageInfo]:
        """Calculate a test's contribution to overall coverage.
        
        Args:
            history_id: Test history node ID
            
        Returns:
            TestCoverageInfo with contribution metrics, or None if test not found
        """
        # Get test name
        cursor = self.conn.execute("""
            SELECT logical_name FROM history_nodes WHERE history_id = ?
        """, (history_id,))
        row = cursor.fetchone()
        if not row:
            return None
        test_name = row[0]
        
        # Get total items hit by this test
        cursor = self.conn.execute("""
            SELECT COUNT(*), SUM(count_contribution)
            FROM coveritem_tests
            WHERE history_id = ?
        """, (history_id,))
        total_items, total_contribution = cursor.fetchone()
        
        if total_items is None:
            total_items = 0
            total_contribution = 0
        
        # Get unique items
        unique_items = len(self.get_unique_coveritems(history_id))
        
        # Get total coveritems in database
        cursor = self.conn.execute("SELECT COUNT(*) FROM coveritems")
        total_coveritems = cursor.fetchone()[0]
        
        coverage_percent = (total_items / total_coveritems * 100) if total_coveritems > 0 else 0.0
        
        return TestCoverageInfo(
            history_id=history_id,
            test_name=test_name,
            total_items=total_items,
            unique_items=unique_items,
            total_contribution=total_contribution or 0,
            coverage_percent=coverage_percent
        )
    
    def get_all_test_contributions(self) -> List[TestCoverageInfo]:
        """Get contribution metrics for all tests.
        
        Returns:
            List of TestCoverageInfo sorted by total items covered (descending)
        """
        # Get all test history nodes
        cursor = self.conn.execute("""
            SELECT history_id FROM history_nodes WHERE history_kind = 1
        """)  # 1 = UCIS_HISTORYNODE_TEST
        
        contributions = []
        for row in cursor.fetchall():
            history_id = row[0]
            info = self.get_test_contribution(history_id)
            if info and info.total_items > 0:
                contributions.append(info)
        
        # Sort by total items (descending)
        contributions.sort(key=lambda x: x.total_items, reverse=True)
        return contributions
    
    def get_coverage_timeline(self) -> List[Tuple[str, str, int, int, float]]:
        """Get chronological coverage accumulation.
        
        Returns:
            List of (date, test_name, new_items, cumulative_items, cumulative_percent)
            sorted by date
        """
        # Get tests ordered by date
        cursor = self.conn.execute("""
            SELECT history_id, logical_name, date
            FROM history_nodes 
            WHERE history_kind = 1
            ORDER BY date, history_id
        """)
        
        tests = cursor.fetchall()
        if not tests:
            return []
        
        # Get total coveritems
        cursor = self.conn.execute("SELECT COUNT(*) FROM coveritems")
        total_items = cursor.fetchone()[0]
        
        timeline = []
        covered_items = set()
        
        for history_id, test_name, date in tests:
            # Get items covered by this test
            test_items = set(self.get_coveritems_for_test(history_id))
            
            # Calculate new coverage
            new_items = test_items - covered_items
            covered_items.update(test_items)
            
            cumulative_count = len(covered_items)
            cumulative_percent = (cumulative_count / total_items * 100) if total_items > 0 else 0.0
            
            timeline.append((
                date or "unknown",
                test_name,
                len(new_items),
                cumulative_count,
                cumulative_percent
            ))
        
        return timeline
    
    def optimize_test_set_greedy(self, target_percent: float = 90.0) -> List[Tuple[str, int]]:
        """Find near-optimal test set using greedy algorithm.
        
        Uses greedy set cover approximation: repeatedly pick the test that
        covers the most uncovered items until target is reached.
        
        Args:
            target_percent: Target coverage percentage (default 90.0)
            
        Returns:
            List of (test_name, items_added) tuples in order selected
        """
        # Get total coveritems
        cursor = self.conn.execute("SELECT COUNT(*) FROM coveritems")
        total_items = cursor.fetchone()[0]
        target_count = int(total_items * target_percent / 100.0)
        
        # Get all test contributions
        contributions = self.get_all_test_contributions()
        if not contributions:
            return []
        
        covered_items = set()
        selected_tests = []
        remaining_tests = {info.history_id: info for info in contributions}
        
        while len(covered_items) < target_count and remaining_tests:
            # Find test that covers most uncovered items
            best_test_id = None
            best_new_items = set()
            
            for history_id, info in remaining_tests.items():
                test_items = set(self.get_coveritems_for_test(history_id))
                new_items = test_items - covered_items
                
                if len(new_items) > len(best_new_items):
                    best_test_id = history_id
                    best_new_items = new_items
            
            if not best_test_id:
                break
            
            # Add best test to selection
            info = remaining_tests[best_test_id]
            selected_tests.append((info.test_name, len(best_new_items)))
            covered_items.update(best_new_items)
            del remaining_tests[best_test_id]
        
        return selected_tests
    
    def has_test_associations(self) -> bool:
        """Check if database has any test-coveritem associations.
        
        Returns:
            True if coveritem_tests table has data, False otherwise
        """
        cursor = self.conn.execute("SELECT COUNT(*) FROM coveritem_tests")
        count = cursor.fetchone()[0]
        return count > 0
