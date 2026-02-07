"""
Helper module to load UCIS library for tests
"""
import ctypes
import os
import sys


def find_ucis_library():
    """Find the UCIS shared library in various locations"""
    
    # Check environment variable first (set by CMake tests)
    if 'UCIS_LIB_PATH' in os.environ:
        lib_dir = os.environ['UCIS_LIB_PATH']
        lib_path = os.path.join(lib_dir, 'libucis.so')
        if os.path.exists(lib_path):
            return lib_path
    
    # Check relative to this script (for make-based builds)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    lib_path = os.path.join(script_dir, '..', 'libucis.so')
    if os.path.exists(lib_path):
        return lib_path
    
    # Check in build directory
    lib_path = os.path.join(script_dir, '..', '..', '..', 'build', 'src', 'native', 'libucis.so')
    if os.path.exists(lib_path):
        return lib_path
    
    return None


def load_ucis_library():
    """Load and return the UCIS library with error handling"""
    lib_path = find_ucis_library()
    
    if lib_path is None:
        print("Error: libucis.so not found. Build the library first:", file=sys.stderr)
        print("  Using CMake: mkdir build && cd build && cmake .. && make", file=sys.stderr)
        print("  Using Make: cd src/native && make", file=sys.stderr)
        sys.exit(1)
    
    try:
        return ctypes.CDLL(lib_path)
    except OSError as e:
        print(f"Error loading library from {lib_path}: {e}", file=sys.stderr)
        sys.exit(1)
