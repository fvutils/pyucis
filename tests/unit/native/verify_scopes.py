#!/usr/bin/env python3
"""Verify scope data in database using direct SQL"""

import sqlite3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ctypes
lib_path = os.path.join(os.path.dirname(__file__), "..", "libucis.so")
libucis = ctypes.CDLL(lib_path)

# Setup
libucis.ucis_Open.argtypes = [ctypes.c_char_p]
libucis.ucis_Open.restype = ctypes.c_void_p
libucis.ucis_Close.argtypes = [ctypes.c_void_p]
libucis.ucis_CreateInstance.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
libucis.ucis_CreateInstance.restype = ctypes.c_void_p

# Create test database
db_path = "verify_scopes.ucisdb"
if os.path.exists(db_path):
    os.unlink(db_path)

db = libucis.ucis_Open(db_path.encode())
top = libucis.ucis_CreateInstance(db, None, b"top", None, 1, 1)
dut = libucis.ucis_CreateInstance(db, top, b"dut", None, 2, 1)
mem = libucis.ucis_CreateInstance(db, dut, b"memory", None, 3, 1)
libucis.ucis_Close(db)

# Verify with SQL
print("SQL Verification:")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT scope_id, parent_id, scope_name, scope_type, weight FROM scopes ORDER BY scope_id")
print("\nScopes table:")
print("  scope_id | parent_id | name   | type | weight")
print("  " + "-" * 45)
for row in cursor.fetchall():
    parent = row[1] if row[1] else "NULL"
    print(f"  {row[0]:8} | {parent:9} | {row[2]:6} | 0x{row[3]:02x} | {row[4]}")

# Verify parent-child relationships
cursor.execute("""
    WITH RECURSIVE scope_path AS (
        SELECT scope_id, scope_name, parent_id, 0 as level, scope_name as path
        FROM scopes WHERE parent_id IS NULL
        UNION ALL
        SELECT s.scope_id, s.scope_name, s.parent_id, sp.level + 1, 
               sp.path || '/' || s.scope_name
        FROM scopes s
        JOIN scope_path sp ON s.parent_id = sp.scope_id
    )
    SELECT path, level FROM scope_path ORDER BY path
""")

print("\nHierarchy:")
for row in cursor.fetchall():
    indent = "  " * row[1]
    print(f"  {indent}{row[0]}")

conn.close()
os.unlink(db_path)
print("\n✓ SQL verification complete")
