#!/usr/bin/env python3
"""
Tests for UCIS Coverage operations
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

# Define ucisCoverDataT structure
class CoverData(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_int),
        ("data", ctypes.c_int64),
        ("data_fec", ctypes.c_int64),
        ("at_least", ctypes.c_int),
        ("weight", ctypes.c_int),
        ("goal", ctypes.c_int),
        ("flags", ctypes.c_int),
    ]

# Define function signatures
libucis.ucis_Open.argtypes = [ctypes.c_char_p]
libucis.ucis_Open.restype = ctypes.c_void_p

libucis.ucis_Close.argtypes = [ctypes.c_void_p]
libucis.ucis_Close.restype = None

libucis.ucis_CreateInstance.argtypes = [
    ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p,
    ctypes.c_void_p, ctypes.c_int, ctypes.c_int
]
libucis.ucis_CreateInstance.restype = ctypes.c_void_p

libucis.ucis_CreateScope.argtypes = [
    ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p,
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int
]
libucis.ucis_CreateScope.restype = ctypes.c_void_p

libucis.ucis_CreateNextCover.argtypes = [
    ctypes.c_void_p,  # db
    ctypes.c_void_p,  # parent
    ctypes.c_char_p,  # name
    ctypes.POINTER(CoverData),  # data
    ctypes.c_void_p   # source
]
libucis.ucis_CreateNextCover.restype = ctypes.c_void_p

libucis.ucis_GetCoverData.argtypes = [
    ctypes.c_void_p,  # db
    ctypes.c_void_p,  # cover
    ctypes.POINTER(CoverData)  # data
]
libucis.ucis_GetCoverData.restype = ctypes.c_int

libucis.ucis_SetCoverData.argtypes = [
    ctypes.c_void_p,  # db
    ctypes.c_void_p,  # cover
    ctypes.POINTER(CoverData)  # data
]
libucis.ucis_SetCoverData.restype = ctypes.c_int

libucis.ucis_IncrementCoverData.argtypes = [
    ctypes.c_void_p,  # db
    ctypes.c_void_p,  # cover
    ctypes.c_int64    # increment
]
libucis.ucis_IncrementCoverData.restype = ctypes.c_int

# Callback type for iteration
COVER_CALLBACK = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)

libucis.ucis_CoverIterate.argtypes = [
    ctypes.c_void_p,  # db
    ctypes.c_void_p,  # parent
    COVER_CALLBACK,   # callback
    ctypes.c_void_p   # userdata
]
libucis.ucis_CoverIterate.restype = ctypes.c_int

# Constants
UCIS_INSTANCE = 0x10
UCIS_COVERGROUP = 0x1000
UCIS_COVERPOINT = 0x4000
UCIS_VERILOG = 1

UCIS_CVGBIN = 0x01
UCIS_BRANCHBIN = 0x04
UCIS_TOGGLEBIN = 0x200


def test_create_simple_coverage():
    """Test creating a single coverage item"""
    print("TEST: Create Simple Coverage")
    
    db = libucis.ucis_Open(None)
    
    # Create scope hierarchy
    top = libucis.ucis_CreateInstance(db, None, b"top", None, 1, UCIS_VERILOG)
    cg = libucis.ucis_CreateScope(db, top, b"addr_cg", None, 1, UCIS_VERILOG,
                                  UCIS_COVERGROUP, 0)
    cp = libucis.ucis_CreateScope(db, cg, b"addr_cp", None, 1, UCIS_VERILOG,
                                  UCIS_COVERPOINT, 0)
    
    # Create coverage bin
    data = CoverData()
    data.type = UCIS_CVGBIN
    data.data = 42
    data.data_fec = 0
    data.at_least = 10
    data.weight = 1
    data.goal = 100
    data.flags = 0
    
    cover = libucis.ucis_CreateNextCover(db, cp, b"low", ctypes.byref(data), None)
    assert cover is not None
    print("  ✓ Created coverage bin")
    
    # Retrieve and verify data
    retrieved = CoverData()
    result = libucis.ucis_GetCoverData(db, cover, ctypes.byref(retrieved))
    assert result == 0
    assert retrieved.type == UCIS_CVGBIN
    assert retrieved.data == 42
    assert retrieved.at_least == 10
    print(f"  ✓ Retrieved data: count={retrieved.data}, at_least={retrieved.at_least}")
    
    libucis.ucis_Close(db)


def test_multiple_bins():
    """Test creating multiple coverage bins"""
    print("\nTEST: Multiple Coverage Bins")
    
    db = libucis.ucis_Open(None)
    
    top = libucis.ucis_CreateInstance(db, None, b"top", None, 1, UCIS_VERILOG)
    cg = libucis.ucis_CreateScope(db, top, b"addr_cg", None, 1, UCIS_VERILOG,
                                  UCIS_COVERGROUP, 0)
    cp = libucis.ucis_CreateScope(db, cg, b"addr_cp", None, 1, UCIS_VERILOG,
                                  UCIS_COVERPOINT, 0)
    
    # Create multiple bins
    bins = [
        (b"low", 45, 10),
        (b"mid", 67, 10),
        (b"high", 23, 10),
        (b"max", 5, 10),
    ]
    
    covers = []
    for name, count, at_least in bins:
        data = CoverData()
        data.type = UCIS_CVGBIN
        data.data = count
        data.at_least = at_least
        data.weight = 1
        
        cover = libucis.ucis_CreateNextCover(db, cp, name, ctypes.byref(data), None)
        assert cover is not None
        covers.append((name.decode(), cover))
    
    print(f"  ✓ Created {len(bins)} coverage bins")
    
    libucis.ucis_Close(db)


def test_update_coverage():
    """Test updating coverage data"""
    print("\nTEST: Update Coverage Data")
    
    db = libucis.ucis_Open(None)
    
    top = libucis.ucis_CreateInstance(db, None, b"top", None, 1, UCIS_VERILOG)
    cp = libucis.ucis_CreateScope(db, top, b"cp", None, 1, UCIS_VERILOG,
                                  UCIS_COVERPOINT, 0)
    
    # Create bin with initial count
    data = CoverData()
    data.type = UCIS_CVGBIN
    data.data = 10
    data.at_least = 5
    data.weight = 1
    
    cover = libucis.ucis_CreateNextCover(db, cp, b"bin1", ctypes.byref(data), None)
    print("  ✓ Created bin with count=10")
    
    # Update the count
    data.data = 50
    result = libucis.ucis_SetCoverData(db, cover, ctypes.byref(data))
    assert result == 0
    print("  ✓ Updated count to 50")
    
    # Verify update
    retrieved = CoverData()
    libucis.ucis_GetCoverData(db, cover, ctypes.byref(retrieved))
    assert retrieved.data == 50
    print(f"  ✓ Verified count: {retrieved.data}")
    
    libucis.ucis_Close(db)


def test_increment_coverage():
    """Test incrementing coverage atomically"""
    print("\nTEST: Increment Coverage")
    
    db = libucis.ucis_Open(None)
    
    top = libucis.ucis_CreateInstance(db, None, b"top", None, 1, UCIS_VERILOG)
    cp = libucis.ucis_CreateScope(db, top, b"cp", None, 1, UCIS_VERILOG,
                                  UCIS_COVERPOINT, 0)
    
    # Create bin
    data = CoverData()
    data.type = UCIS_CVGBIN
    data.data = 10
    data.at_least = 5
    data.weight = 1
    
    cover = libucis.ucis_CreateNextCover(db, cp, b"bin1", ctypes.byref(data), None)
    print("  ✓ Created bin with count=10")
    
    # Increment multiple times
    libucis.ucis_IncrementCoverData(db, cover, 5)
    libucis.ucis_IncrementCoverData(db, cover, 3)
    libucis.ucis_IncrementCoverData(db, cover, 7)
    print("  ✓ Incremented by 5, 3, 7")
    
    # Verify final count
    retrieved = CoverData()
    libucis.ucis_GetCoverData(db, cover, ctypes.byref(retrieved))
    assert retrieved.data == 25  # 10 + 5 + 3 + 7
    print(f"  ✓ Final count: {retrieved.data}")
    
    libucis.ucis_Close(db)


def test_coverage_iteration():
    """Test iterating over coverage items"""
    print("\nTEST: Coverage Iteration")
    
    db = libucis.ucis_Open(None)
    
    top = libucis.ucis_CreateInstance(db, None, b"top", None, 1, UCIS_VERILOG)
    cp = libucis.ucis_CreateScope(db, top, b"cp", None, 1, UCIS_VERILOG,
                                  UCIS_COVERPOINT, 0)
    
    # Create several bins
    for i in range(5):
        data = CoverData()
        data.type = UCIS_CVGBIN
        data.data = i * 10
        data.at_least = 5
        data.weight = 1
        
        libucis.ucis_CreateNextCover(db, cp, f"bin{i}".encode(), ctypes.byref(data), None)
    
    print("  ✓ Created 5 coverage bins")
    
    # Iterate and collect counts
    counts = []
    
    def collect_callback(userdata, cover):
        data = CoverData()
        libucis.ucis_GetCoverData(db, cover, ctypes.byref(data))
        counts.append(data.data)
        return 0  # Continue
    
    callback = COVER_CALLBACK(collect_callback)
    count = libucis.ucis_CoverIterate(db, cp, callback, None)
    
    assert count == 5
    assert counts == [0, 10, 20, 30, 40]
    print(f"  ✓ Iterated {count} bins")
    print(f"    Counts: {counts}")
    
    libucis.ucis_Close(db)


def test_coverage_types():
    """Test different coverage types"""
    print("\nTEST: Different Coverage Types")
    
    db = libucis.ucis_Open(None)
    
    top = libucis.ucis_CreateInstance(db, None, b"top", None, 1, UCIS_VERILOG)
    
    # Create a covergroup bin
    cg = libucis.ucis_CreateScope(db, top, b"cg", None, 1, UCIS_VERILOG,
                                  UCIS_COVERGROUP, 0)
    cp = libucis.ucis_CreateScope(db, cg, b"cp", None, 1, UCIS_VERILOG,
                                  UCIS_COVERPOINT, 0)
    
    data_cvg = CoverData()
    data_cvg.type = UCIS_CVGBIN
    data_cvg.data = 100
    data_cvg.at_least = 1
    data_cvg.weight = 1
    
    cover_cvg = libucis.ucis_CreateNextCover(db, cp, b"cvg_bin", ctypes.byref(data_cvg), None)
    assert cover_cvg is not None
    print("  ✓ Created CVGBIN")
    
    # Create a branch bin
    data_branch = CoverData()
    data_branch.type = UCIS_BRANCHBIN
    data_branch.data = 50
    data_branch.at_least = 1
    data_branch.weight = 1
    
    cover_branch = libucis.ucis_CreateNextCover(db, top, b"branch_true", 
                                                ctypes.byref(data_branch), None)
    assert cover_branch is not None
    print("  ✓ Created BRANCHBIN")
    
    # Create a toggle bin
    data_toggle = CoverData()
    data_toggle.type = UCIS_TOGGLEBIN
    data_toggle.data = 75
    data_toggle.at_least = 1
    data_toggle.weight = 1
    
    cover_toggle = libucis.ucis_CreateNextCover(db, top, b"toggle_01",
                                                ctypes.byref(data_toggle), None)
    assert cover_toggle is not None
    print("  ✓ Created TOGGLEBIN")
    
    # Verify types
    retrieved = CoverData()
    
    libucis.ucis_GetCoverData(db, cover_cvg, ctypes.byref(retrieved))
    assert retrieved.type == UCIS_CVGBIN
    
    libucis.ucis_GetCoverData(db, cover_branch, ctypes.byref(retrieved))
    assert retrieved.type == UCIS_BRANCHBIN
    
    libucis.ucis_GetCoverData(db, cover_toggle, ctypes.byref(retrieved))
    assert retrieved.type == UCIS_TOGGLEBIN
    
    print("  ✓ All types verified")
    
    libucis.ucis_Close(db)


def test_coverage_flags_and_goal():
    """Test coverage flags and goal attributes"""
    print("\nTEST: Coverage Flags and Goal")
    
    db = libucis.ucis_Open(None)
    
    top = libucis.ucis_CreateInstance(db, None, b"top", None, 1, UCIS_VERILOG)
    cp = libucis.ucis_CreateScope(db, top, b"cp", None, 1, UCIS_VERILOG,
                                  UCIS_COVERPOINT, 0)
    
    # Create bin with flags and goal
    data = CoverData()
    data.type = UCIS_CVGBIN
    data.data = 150
    data.at_least = 10
    data.weight = 2
    data.goal = 200
    data.flags = 0x01  # UCIS_IS_COVERED
    
    cover = libucis.ucis_CreateNextCover(db, cp, b"bin1", ctypes.byref(data), None)
    print("  ✓ Created bin with flags=0x01, goal=200")
    
    # Verify
    retrieved = CoverData()
    libucis.ucis_GetCoverData(db, cover, ctypes.byref(retrieved))
    
    assert retrieved.flags == 0x01
    assert retrieved.goal == 200
    assert retrieved.weight == 2
    print(f"  ✓ Verified: flags=0x{retrieved.flags:02x}, goal={retrieved.goal}, weight={retrieved.weight}")
    
    libucis.ucis_Close(db)


def main():
    print("=" * 60)
    print("UCIS C API - Phase 3 Coverage Tests")
    print("=" * 60)
    
    try:
        test_create_simple_coverage()
        test_multiple_bins()
        test_update_coverage()
        test_increment_coverage()
        test_coverage_iteration()
        test_coverage_types()
        test_coverage_flags_and_goal()
        
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
