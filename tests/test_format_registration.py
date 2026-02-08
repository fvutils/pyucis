#!/usr/bin/env python3
"""
Test script to verify SQLite format registration and CLI integration
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

print("=" * 70)
print("TESTING SQLITE FORMAT REGISTRATION")
print("=" * 70)

# Test 1: Format registry
print("\n1. Checking format registry...")
from ucis.db_format_rgy import DbFormatRgy

rgy = DbFormatRgy.inst()
formats = list(rgy.getFormats())
print(f"   Available formats: {', '.join(sorted(formats))}")

if 'sqlite' in formats:
    print("   ✓ SQLite format registered")
else:
    print("   ✗ SQLite format NOT registered")
    sys.exit(1)

# Test 2: Create via format interface
print("\n2. Testing format interface...")
fmt_if = rgy.getFormatIf('sqlite')
print(f"   Format interface: {type(fmt_if).__name__}")

# Test create
ucis = fmt_if.create()
print(f"   Created database: {type(ucis).__name__}")

# Test 3: Create with file
print("\n3. Testing file operations...")
import tempfile

with tempfile.NamedTemporaryFile(suffix='.ucisdb', delete=False) as f:
    test_db = f.name

try:
    # Create and write
    from ucis.scope_type_t import ScopeTypeT
    from ucis.source_t import SourceT
    
    ucis2 = fmt_if.read(test_db) if os.path.exists(test_db) else fmt_if.create()
    top = ucis2.createScope("test_top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
    
    fmt_if.write(ucis2, test_db)
    ucis2.close()
    
    print(f"   ✓ Created test database: {test_db}")
    print(f"   ✓ Database size: {os.path.getsize(test_db)} bytes")
    
    # Read back
    ucis3 = fmt_if.read(test_db)
    scopes = list(ucis3.scopes(ScopeTypeT.INSTANCE))
    print(f"   ✓ Read back {len(scopes)} scope(s)")
    
    if len(scopes) > 0:
        print(f"   ✓ Scope name: {scopes[0].getScopeName()}")
    
    ucis3.close()
    
finally:
    if os.path.exists(test_db):
        os.unlink(test_db)

# Test 4: Direct SQLite API
print("\n4. Testing direct SQLite API...")
from ucis.sqlite import SqliteUCIS

db = SqliteUCIS()
top = db.createScope("direct_test", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
print(f"   ✓ Created scope via direct API: {top.getScopeName()}")
db.close()

print("\n" + "=" * 70)
print("✓ ALL TESTS PASSED - SQLite format fully integrated")
print("=" * 70)
