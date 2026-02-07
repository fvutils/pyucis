#!/usr/bin/env python3
"""
Basic tests for UCIS C API
Tests database creation, opening, closing, and schema validation
"""

import ctypes
import os
import sys
import sqlite3

# Try to import ucis_loader (works for both make and CMake builds)
try:
    from ucis_loader import load_ucis_library
    libucis = load_ucis_library()
except ImportError:
    # Fallback for direct execution
    lib_path = os.path.join(os.path.dirname(__file__), "..", "libucis.so")
    if not os.path.exists(lib_path):
        print(f"Error: {lib_path} not found. Run 'make' first.")
        sys.exit(1)
    libucis = ctypes.CDLL(lib_path)

# Define function signatures
libucis.ucis_GetAPIVersion.argtypes = []
libucis.ucis_GetAPIVersion.restype = ctypes.c_char_p

libucis.ucis_Open.argtypes = [ctypes.c_char_p]
libucis.ucis_Open.restype = ctypes.c_void_p

libucis.ucis_Close.argtypes = [ctypes.c_void_p]
libucis.ucis_Close.restype = None

libucis.ucis_Write.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
libucis.ucis_Write.restype = ctypes.c_int

libucis.ucis_GetLastError.argtypes = [ctypes.c_void_p]
libucis.ucis_GetLastError.restype = ctypes.c_char_p


def test_api_version():
    """Test that API version is correct"""
    print("TEST: API Version")
    version = libucis.ucis_GetAPIVersion()
    assert version == b"1.0", f"Expected version '1.0', got {version}"
    print("  ✓ API version: 1.0")


def test_open_close_memory():
    """Test opening and closing in-memory database"""
    print("\nTEST: Open/Close In-Memory Database")
    
    db = libucis.ucis_Open(None)
    assert db is not None, "Failed to open in-memory database"
    print("  ✓ Opened in-memory database")
    
    libucis.ucis_Close(db)
    print("  ✓ Closed database")


def test_open_close_file():
    """Test opening and closing file-based database"""
    print("\nTEST: Open/Close File Database")
    
    db_path = b"test_basic.ucisdb"
    
    # Remove if exists
    if os.path.exists(db_path):
        os.unlink(db_path)
    
    db = libucis.ucis_Open(db_path)
    assert db is not None, "Failed to open file database"
    print(f"  ✓ Opened database: {db_path.decode()}")
    
    libucis.ucis_Close(db)
    print("  ✓ Closed database")
    
    # Verify file exists
    assert os.path.exists(db_path), "Database file not created"
    print(f"  ✓ Database file exists: {os.path.getsize(db_path)} bytes")
    
    # Clean up
    os.unlink(db_path)


def test_schema_validation():
    """Test that schema is correctly initialized"""
    print("\nTEST: Schema Validation")
    
    db_path = "test_schema.ucisdb"
    
    # Remove if exists
    if os.path.exists(db_path):
        os.unlink(db_path)
    
    # Create database via UCIS API
    db = libucis.ucis_Open(db_path.encode())
    assert db is not None
    libucis.ucis_Close(db)
    
    # Open with sqlite3 and verify schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check for required tables
    required_tables = [
        'db_metadata', 'files', 'scopes', 'coveritems', 
        'history_nodes', 'scope_properties', 'coveritem_properties',
        'history_properties', 'attributes'
    ]
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    for table in required_tables:
        assert table in tables, f"Missing table: {table}"
        print(f"  ✓ Table exists: {table}")
    
    # Check metadata
    cursor.execute("SELECT key, value FROM db_metadata")
    metadata = dict(cursor.fetchall())
    
    assert 'UCIS_VERSION' in metadata
    assert metadata['UCIS_VERSION'] == '1.0'
    print(f"  ✓ UCIS_VERSION: {metadata['UCIS_VERSION']}")
    
    assert 'API_VERSION' in metadata
    assert metadata['API_VERSION'] == '1.0'
    print(f"  ✓ API_VERSION: {metadata['API_VERSION']}")
    
    conn.close()
    
    # Clean up
    os.unlink(db_path)


def test_write_database():
    """Test writing database to different file"""
    print("\nTEST: Write Database")
    
    db_path1 = b"test_write_src.ucisdb"
    db_path2 = b"test_write_dst.ucisdb"
    
    # Clean up
    for path in [db_path1, db_path2]:
        if os.path.exists(path):
            os.unlink(path)
    
    # Create database
    db = libucis.ucis_Open(db_path1)
    assert db is not None
    print(f"  ✓ Created: {db_path1.decode()}")
    
    # Write to different file
    result = libucis.ucis_Write(db, db_path2)
    assert result == 0, "Write failed"
    print(f"  ✓ Wrote to: {db_path2.decode()}")
    
    libucis.ucis_Close(db)
    
    # Verify both files exist
    assert os.path.exists(db_path1)
    assert os.path.exists(db_path2)
    print("  ✓ Both files exist")
    
    # Clean up
    os.unlink(db_path1)
    os.unlink(db_path2)


def test_reopen_database():
    """Test reopening existing database"""
    print("\nTEST: Reopen Database")
    
    db_path = b"test_reopen.ucisdb"
    
    # Remove if exists
    if os.path.exists(db_path):
        os.unlink(db_path)
    
    # Create and close
    db1 = libucis.ucis_Open(db_path)
    assert db1 is not None
    libucis.ucis_Close(db1)
    print("  ✓ Created database")
    
    # Reopen
    db2 = libucis.ucis_Open(db_path)
    assert db2 is not None
    print("  ✓ Reopened database")
    
    libucis.ucis_Close(db2)
    
    # Clean up
    os.unlink(db_path)


def main():
    print("=" * 60)
    print("UCIS C API - Phase 1 Basic Tests")
    print("=" * 60)
    
    try:
        test_api_version()
        test_open_close_memory()
        test_open_close_file()
        test_schema_validation()
        test_write_database()
        test_reopen_database()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
