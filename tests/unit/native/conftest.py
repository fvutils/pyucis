"""
Pytest configuration for native C API tests

These tests use ctypes to test the native C library and should be run via CTest,
not directly with pytest (though they can be if the library is built).
"""
import pytest
import os
import sys

# Add marker for native tests
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "native: mark test as a native C API test (requires libucis.so)"
    )

# Collect hook to skip all tests in this directory if library not available
def pytest_collection_modifyitems(session, config, items):
    """Skip native tests if library is not available at collection time"""
    # Don't try to import or use the tests if we're just collecting for pytest
    # The tests will be run via CTest which sets up the environment properly
    pass

# Session-scoped fixture to check library availability
@pytest.fixture(scope="session", autouse=True)
def check_native_library():
    """Check if native library is available before running tests"""
    try:
        # Try relative import first
        try:
            from .ucis_loader import find_ucis_library
        except ImportError:
            from ucis_loader import find_ucis_library
        
        lib_path = find_ucis_library()
        if lib_path is None:
            pytest.skip("libucis.so not found - build the library first with CMake", allow_module_level=True)
    except Exception as e:
        pytest.skip(f"Cannot load ucis_loader: {e}", allow_module_level=True)
