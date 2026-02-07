#!/usr/bin/env python3
"""
Tests for UCIS Scope operations
"""

import ctypes
import os
import sys

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
libucis.ucis_Open.argtypes = [ctypes.c_char_p]
libucis.ucis_Open.restype = ctypes.c_void_p

libucis.ucis_Close.argtypes = [ctypes.c_void_p]
libucis.ucis_Close.restype = None

libucis.ucis_CreateScope.argtypes = [
    ctypes.c_void_p,  # db
    ctypes.c_void_p,  # parent
    ctypes.c_char_p,  # name
    ctypes.c_void_p,  # source (NULL for now)
    ctypes.c_int,     # weight
    ctypes.c_int,     # source_type
    ctypes.c_int,     # type
    ctypes.c_int      # flags
]
libucis.ucis_CreateScope.restype = ctypes.c_void_p

libucis.ucis_CreateInstance.argtypes = [
    ctypes.c_void_p,  # db
    ctypes.c_void_p,  # parent
    ctypes.c_char_p,  # name
    ctypes.c_void_p,  # source
    ctypes.c_int,     # weight
    ctypes.c_int      # source_type
]
libucis.ucis_CreateInstance.restype = ctypes.c_void_p

libucis.ucis_GetScopeName.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
libucis.ucis_GetScopeName.restype = ctypes.c_char_p

libucis.ucis_GetScopeType.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
libucis.ucis_GetScopeType.restype = ctypes.c_int

libucis.ucis_GetParent.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
libucis.ucis_GetParent.restype = ctypes.c_void_p

libucis.ucis_SetScopeWeight.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
libucis.ucis_SetScopeWeight.restype = ctypes.c_int

libucis.ucis_SetScopeGoal.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
libucis.ucis_SetScopeGoal.restype = ctypes.c_int

libucis.ucis_SetScopeFlags.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
libucis.ucis_SetScopeFlags.restype = ctypes.c_int

# Callback type for iteration
SCOPE_CALLBACK = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)

libucis.ucis_ScopeIterate.argtypes = [
    ctypes.c_void_p,  # db
    ctypes.c_void_p,  # parent
    ctypes.c_int,     # type_mask
    SCOPE_CALLBACK,   # callback
    ctypes.c_void_p   # userdata
]
libucis.ucis_ScopeIterate.restype = ctypes.c_int

# Constants from ucis_types.h
UCIS_INSTANCE = 0x10
UCIS_DU_MODULE = 0x20
UCIS_COVERGROUP = 0x1000
UCIS_COVERPOINT = 0x4000
UCIS_VERILOG = 1


def test_create_simple_scope():
    """Test creating a single scope"""
    print("TEST: Create Simple Scope")
    
    db = libucis.ucis_Open(None)
    assert db is not None
    
    # Create a top-level instance
    top = libucis.ucis_CreateInstance(db, None, b"top", None, 1, UCIS_VERILOG)
    assert top is not None
    print("  ✓ Created scope")
    
    # Get scope name
    name = libucis.ucis_GetScopeName(db, top)
    assert name == b"top"
    print(f"  ✓ Scope name: {name.decode()}")
    
    # Get scope type
    scope_type = libucis.ucis_GetScopeType(db, top)
    assert scope_type == UCIS_INSTANCE
    print(f"  ✓ Scope type: 0x{scope_type:x} (INSTANCE)")
    
    libucis.ucis_Close(db)


def test_parent_child_relationship():
    """Test creating parent-child scope hierarchy"""
    print("\nTEST: Parent-Child Relationship")
    
    db = libucis.ucis_Open(None)
    
    # Create parent
    parent = libucis.ucis_CreateInstance(db, None, b"top", None, 1, UCIS_VERILOG)
    assert parent is not None
    print("  ✓ Created parent scope: top")
    
    # Create child
    child = libucis.ucis_CreateInstance(db, parent, b"dut", None, 1, UCIS_VERILOG)
    assert child is not None
    print("  ✓ Created child scope: dut")
    
    # Verify parent of child
    retrieved_parent = libucis.ucis_GetParent(db, child)
    assert retrieved_parent is not None
    
    parent_name = libucis.ucis_GetScopeName(db, retrieved_parent)
    assert parent_name == b"top"
    print(f"  ✓ Child's parent: {parent_name.decode()}")
    
    # Verify parent has no parent
    grandparent = libucis.ucis_GetParent(db, parent)
    assert grandparent is None
    print("  ✓ Parent has no parent (NULL)")
    
    libucis.ucis_Close(db)


def test_multiple_children():
    """Test creating multiple child scopes"""
    print("\nTEST: Multiple Children")
    
    db = libucis.ucis_Open(None)
    
    # Create parent
    parent = libucis.ucis_CreateInstance(db, None, b"top", None, 1, UCIS_VERILOG)
    
    # Create multiple children
    child1 = libucis.ucis_CreateInstance(db, parent, b"dut", None, 1, UCIS_VERILOG)
    child2 = libucis.ucis_CreateInstance(db, parent, b"tb", None, 1, UCIS_VERILOG)
    child3 = libucis.ucis_CreateInstance(db, parent, b"monitor", None, 1, UCIS_VERILOG)
    
    assert child1 is not None
    assert child2 is not None
    assert child3 is not None
    
    print("  ✓ Created 3 child scopes")
    
    # Create grandchildren
    grandchild = libucis.ucis_CreateInstance(db, child1, b"memory", None, 1, UCIS_VERILOG)
    assert grandchild is not None
    print("  ✓ Created grandchild scope")
    
    libucis.ucis_Close(db)


def test_scope_attributes():
    """Test setting and retrieving scope attributes"""
    print("\nTEST: Scope Attributes")
    
    db = libucis.ucis_Open(None)
    
    scope = libucis.ucis_CreateInstance(db, None, b"top", None, 1, UCIS_VERILOG)
    
    # Set weight
    result = libucis.ucis_SetScopeWeight(db, scope, 42)
    assert result == 0
    print("  ✓ Set scope weight: 42")
    
    # Set goal
    result = libucis.ucis_SetScopeGoal(db, scope, 100)
    assert result == 0
    print("  ✓ Set scope goal: 100")
    
    # Set flags
    result = libucis.ucis_SetScopeFlags(db, scope, 0x01 | 0x02)
    assert result == 0
    print("  ✓ Set scope flags: 0x03")
    
    libucis.ucis_Close(db)


def test_scope_iteration():
    """Test iterating over child scopes"""
    print("\nTEST: Scope Iteration")
    
    db = libucis.ucis_Open(None)
    
    # Create hierarchy
    top = libucis.ucis_CreateInstance(db, None, b"top", None, 1, UCIS_VERILOG)
    child1 = libucis.ucis_CreateInstance(db, top, b"child1", None, 1, UCIS_VERILOG)
    child2 = libucis.ucis_CreateInstance(db, top, b"child2", None, 1, UCIS_VERILOG)
    child3 = libucis.ucis_CreateInstance(db, top, b"child3", None, 1, UCIS_VERILOG)
    
    # Create a covergroup (different type)
    cg = libucis.ucis_CreateScope(db, top, b"addr_cg", None, 1, UCIS_VERILOG, 
                                  UCIS_COVERGROUP, 0)
    
    # Collect scopes via callback
    collected_scopes = []
    
    def collect_callback(userdata, scope):
        name = libucis.ucis_GetScopeName(db, scope)
        collected_scopes.append(name.decode())
        return 0  # Continue iteration
    
    callback = SCOPE_CALLBACK(collect_callback)
    
    # Iterate all children (no type filter)
    count = libucis.ucis_ScopeIterate(db, top, 0, callback, None)
    assert count == 4
    print(f"  ✓ Found {count} total children")
    print(f"    Names: {', '.join(collected_scopes)}")
    
    # Iterate only instances
    collected_scopes.clear()
    count = libucis.ucis_ScopeIterate(db, top, UCIS_INSTANCE, callback, None)
    assert count == 3
    print(f"  ✓ Found {count} instance children")
    print(f"    Names: {', '.join(collected_scopes)}")
    
    # Iterate only covergroups
    collected_scopes.clear()
    count = libucis.ucis_ScopeIterate(db, top, UCIS_COVERGROUP, callback, None)
    assert count == 1
    assert collected_scopes[0] == "addr_cg"
    print(f"  ✓ Found {count} covergroup child: {collected_scopes[0]}")
    
    libucis.ucis_Close(db)


def test_iteration_early_stop():
    """Test stopping iteration early via callback"""
    print("\nTEST: Iteration Early Stop")
    
    db = libucis.ucis_Open(None)
    
    top = libucis.ucis_CreateInstance(db, None, b"top", None, 1, UCIS_VERILOG)
    for i in range(10):
        libucis.ucis_CreateInstance(db, top, f"child{i}".encode(), None, 1, UCIS_VERILOG)
    
    # Stop after 5 items
    collected = []
    
    def stop_after_5(userdata, scope):
        collected.append(scope)
        if len(collected) >= 5:
            return 1  # Stop iteration
        return 0  # Continue
    
    callback = SCOPE_CALLBACK(stop_after_5)
    count = libucis.ucis_ScopeIterate(db, top, 0, callback, None)
    
    assert count == 5
    print(f"  ✓ Stopped after {count} items (out of 10)")
    
    libucis.ucis_Close(db)


def test_mixed_scope_types():
    """Test creating different scope types"""
    print("\nTEST: Mixed Scope Types")
    
    db = libucis.ucis_Open(None)
    
    # Create instance
    inst = libucis.ucis_CreateScope(db, None, b"inst", None, 1, UCIS_VERILOG,
                                    UCIS_INSTANCE, 0)
    assert inst is not None
    print("  ✓ Created INSTANCE scope")
    
    # Create module
    mod = libucis.ucis_CreateScope(db, inst, b"mod", None, 1, UCIS_VERILOG,
                                   UCIS_DU_MODULE, 0)
    assert mod is not None
    print("  ✓ Created MODULE scope")
    
    # Create covergroup
    cg = libucis.ucis_CreateScope(db, mod, b"cg", None, 1, UCIS_VERILOG,
                                  UCIS_COVERGROUP, 0)
    assert cg is not None
    print("  ✓ Created COVERGROUP scope")
    
    # Create coverpoint
    cp = libucis.ucis_CreateScope(db, cg, b"cp", None, 1, UCIS_VERILOG,
                                  UCIS_COVERPOINT, 0)
    assert cp is not None
    print("  ✓ Created COVERPOINT scope")
    
    # Verify types
    assert libucis.ucis_GetScopeType(db, inst) == UCIS_INSTANCE
    assert libucis.ucis_GetScopeType(db, mod) == UCIS_DU_MODULE
    assert libucis.ucis_GetScopeType(db, cg) == UCIS_COVERGROUP
    assert libucis.ucis_GetScopeType(db, cp) == UCIS_COVERPOINT
    print("  ✓ All scope types verified")
    
    libucis.ucis_Close(db)


def main():
    print("=" * 60)
    print("UCIS C API - Phase 2 Scope Tests")
    print("=" * 60)
    
    try:
        test_create_simple_scope()
        test_parent_child_relationship()
        test_multiple_children()
        test_scope_attributes()
        test_scope_iteration()
        test_iteration_early_stop()
        test_mixed_scope_types()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
