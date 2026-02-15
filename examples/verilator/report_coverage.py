#!/usr/bin/env python3
"""
Generate a code coverage summary report.
"""
import sys
from ucis.sqlite import SqliteUCIS
from ucis.scope_type_t import ScopeTypeT

if len(sys.argv) != 2:
    print("Usage: report_coverage.py <database.cdb>")
    sys.exit(1)

db_path = sys.argv[1]
db = SqliteUCIS.open_readonly(db_path)

# Count coverage items by type
coverage_by_type = {}
total_items = 0
total_hits = 0

def count_items_in_scope(scope):
    """Recursively count all coverage items in a scope and its children."""
    items = 0
    hits = 0
    
    # Count items directly in this scope
    for item in scope.coverItems(-1):
        items += 1
        data = item.getCoverData()
        if data and data.data > 0:
            hits += 1
    
    # Recurse into child scopes
    for child in scope.scopes(-1):
        child_items, child_hits = count_items_in_scope(child)
        items += child_items
        hits += child_hits
    
    return items, hits

def collect_scopes_by_type(scope, scope_type, result):
    """Recursively collect all scopes of a given type."""
    if scope.getScopeType() == scope_type:
        result.append(scope)
    
    # Recurse into children
    for child in scope.scopes(-1):
        collect_scopes_by_type(child, scope_type, result)

# Count by scope type
type_names = {
    ScopeTypeT.TOGGLE: "Toggle",
    ScopeTypeT.BLOCK: "Block",
    ScopeTypeT.BRANCH: "Branch"
}

for scope_type, type_name in type_names.items():
    # Find all scopes of this type (may be nested)
    matching_scopes = []
    for top_scope in db.scopes(-1):
        collect_scopes_by_type(top_scope, scope_type, matching_scopes)
    
    # Count items in all matching scopes
    items = 0
    hits = 0
    for scope in matching_scopes:
        scope_items, scope_hits = count_items_in_scope(scope)
        items += scope_items
        hits += scope_hits
    
    if items > 0:
        coverage_by_type[type_name] = {
            'items': items,
            'hits': hits,
            'coverage': hits / items * 100
        }
        total_items += items
        total_hits += hits

# Print report
if coverage_by_type:
    for type_name, stats in sorted(coverage_by_type.items()):
        print(f"{type_name:15s}: {stats['hits']:4d} / {stats['items']:4d} ({stats['coverage']:5.2f}%)")
    
    print("-" * 50)
    overall_coverage = (total_hits / total_items * 100) if total_items > 0 else 0
    print(f"{'Overall':15s}: {total_hits:4d} / {total_items:4d} ({overall_coverage:5.2f}%)")
else:
    print("No code coverage data found")

db.close()
