#!/usr/bin/env python3
"""
Demonstrate test coverage query capabilities using the merged coverage database.

This script shows how to:
1. List all tests in the database
2. Find which tests hit specific coverage points
3. Calculate test contributions
4. Find unique coverage per test
5. Optimize test set for target coverage
"""

import sys
import os

# Add src to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from ucis.sqlite import SqliteUCIS
from ucis.history_node_kind import HistoryNodeKind

def main():
    db_path = "coverage/merged.cdb"
    
    if not os.path.exists(db_path):
        print(f"Error: Database not found: {db_path}")
        print("Run 'make merge' first to create the merged database")
        return 1
    
    print("=" * 70)
    print("PyUCIS Test Coverage Query Demonstration")
    print("=" * 70)
    print()
    
    # Open database
    db = SqliteUCIS.open_readonly(db_path)
    test_cov_api = db.get_test_coverage_api()
    
    # 1. List all tests
    print("1. ALL TESTS IN DATABASE")
    print("-" * 70)
    tests = list(db.historyNodes(HistoryNodeKind.TEST))
    print(f"Total tests found: {len(tests)}")
    print()
    for test in tests:
        print(f"  • {test.getLogicalName()}")
        test_date = test.getDate()
        if test_date:
            from datetime import datetime
            print(f"    Date: {datetime.fromtimestamp(test_date).strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 2. Test contributions
    print("2. TEST CONTRIBUTION ANALYSIS")
    print("-" * 70)
    contributions = test_cov_api.get_all_test_contributions()
    
    if contributions:
        print(f"{'Test Name':<30} {'Total':<8} {'Unique':<8} {'Contrib':<10} {'Coverage %':<12}")
        print("-" * 70)
        for contrib in contributions:
            print(f"{contrib.test_name:<30} "
                  f"{contrib.total_items:<8} "
                  f"{contrib.unique_items:<8} "
                  f"{contrib.total_contribution:<10} "
                  f"{contrib.coverage_percent:>6.2f}%")
        print()
        
        # Find test with most unique coverage
        max_unique = max(contributions, key=lambda c: c.unique_items)
        print(f"Test with most unique coverage: {max_unique.test_name} "
              f"({max_unique.unique_items} unique items)")
        print()
    else:
        print("No test contributions found (test associations may not be recorded)")
        print()
    
    # 3. Detailed contribution for first test
    if tests:
        print("3. DETAILED CONTRIBUTION FOR FIRST TEST")
        print("-" * 70)
        first_test = tests[0]
        contrib = test_cov_api.get_test_contribution(first_test.history_id)
        
        if contrib:
            print(f"Test: {contrib.test_name}")
            print(f"  Total coverage items: {contrib.total_items}")
            print(f"  Unique to this test: {contrib.unique_items}")
            print(f"  Total contribution: {contrib.total_contribution}")
            print(f"  Coverage percentage: {contrib.coverage_percent:.2f}%")
            print()
            
            # Show unique coveritems
            unique_items = test_cov_api.get_unique_coveritems(first_test.history_id)
            if unique_items:
                print(f"  Unique coverage items (first 5):")
                for item in unique_items[:5]:
                    print(f"    - Cover ID {item['cover_id']}: "
                          f"{item['cover_name'] or '(unnamed)'} "
                          f"(hits: {item['count']})")
            print()
        else:
            print(f"No contribution data for {first_test.getLogicalName()}")
            print()
    
    # 4. Find which tests hit a specific coveritem
    print("4. TESTS HITTING SPECIFIC COVERAGE POINTS")
    print("-" * 70)
    
    # Get first few coveritems
    root = db.getRoot()
    sample_items = []
    for scope in root.getScopes():
        for cover in scope.getCoverage():
            if hasattr(cover, 'cover_id'):
                sample_items.append(cover)
            if len(sample_items) >= 3:
                break
        if len(sample_items) >= 3:
            break
    
    if sample_items:
        for cover in sample_items:
            tests_for_item = test_cov_api.get_tests_for_coveritem(cover.cover_id)
            cover_name = cover.getCoverName() or "(unnamed)"
            print(f"Coverage item: {cover_name} (ID: {cover.cover_id})")
            if tests_for_item:
                print(f"  Hit by {len(tests_for_item)} test(s):")
                for test_info in tests_for_item:
                    print(f"    - {test_info['test_name']} "
                          f"(contribution: {test_info['count_contribution']})")
            else:
                print("  Not hit by any test (or associations not recorded)")
            print()
    else:
        print("No coveritems found in database")
        print()
    
    # 5. Coverage timeline
    print("5. COVERAGE ACCUMULATION TIMELINE")
    print("-" * 70)
    timeline = test_cov_api.get_coverage_timeline()
    
    if timeline:
        print(f"{'Order':<7} {'Test Name':<30} {'New Items':<12} {'Total Items':<13}")
        print("-" * 70)
        for entry in timeline:
            print(f"{entry['order']:<7} "
                  f"{entry['test_name']:<30} "
                  f"{entry['new_items']:<12} "
                  f"{entry['total_items']:<13}")
        print()
    else:
        print("No timeline data available")
        print()
    
    # 6. Optimize test set
    print("6. OPTIMIZED TEST SET (Greedy Algorithm)")
    print("-" * 70)
    print("Finding minimum test set to achieve 80% coverage...")
    
    optimized = test_cov_api.optimize_test_set_greedy(target_coverage=80.0)
    
    if optimized['selected_tests']:
        print(f"Selected {len(optimized['selected_tests'])} tests:")
        for test_name in optimized['selected_tests']:
            print(f"  • {test_name}")
        print()
        print(f"Coverage achieved: {optimized['coverage_percent']:.2f}%")
        print(f"Total items covered: {optimized['items_covered']} / {optimized['total_items']}")
    else:
        print("No optimization data available")
    print()
    
    # Close database
    db.close()
    
    print("=" * 70)
    print("Query demonstration complete!")
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
