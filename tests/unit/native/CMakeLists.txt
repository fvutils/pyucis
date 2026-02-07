# Test CMakeLists.txt for UCIS C API
cmake_minimum_required(VERSION 3.12)

# Find Python for running tests
find_package(Python3 COMPONENTS Interpreter REQUIRED)

# Create a wrapper script that sets up the library path
set(TEST_WRAPPER "${CMAKE_CURRENT_BINARY_DIR}/run_test.sh")
file(WRITE ${TEST_WRAPPER}
"#!/bin/bash
export LD_LIBRARY_PATH=${CMAKE_BINARY_DIR}/src/native:\$LD_LIBRARY_PATH
export DYLD_LIBRARY_PATH=${CMAKE_BINARY_DIR}/src/native:\$DYLD_LIBRARY_PATH
cd ${CMAKE_CURRENT_BINARY_DIR}
exec \"\$@\"
")
file(CHMOD ${TEST_WRAPPER} PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE)

# Helper function to add Python test
function(add_python_test test_name script_name)
    add_test(
        NAME ${test_name}
        COMMAND ${TEST_WRAPPER} ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/${script_name}
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    )
    
    # Set environment for tests - point to build directory
    set_tests_properties(${test_name} PROPERTIES
        ENVIRONMENT "UCIS_LIB_PATH=${CMAKE_BINARY_DIR}/src/native"
    )
endfunction()

# Copy test scripts to build directory
configure_file(ucis_loader.py ucis_loader.py COPYONLY)
configure_file(test_basic.py test_basic.py COPYONLY)
configure_file(test_scopes.py test_scopes.py COPYONLY)
configure_file(test_coverage.py test_coverage.py COPYONLY)
configure_file(run_all_tests.py run_all_tests.py COPYONLY)

# Add tests
add_python_test(test_basic test_basic.py)
add_python_test(test_scopes test_scopes.py)
add_python_test(test_coverage test_coverage.py)

# Add combined test runner
add_test(
    NAME run_all_tests
    COMMAND ${TEST_WRAPPER} ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/run_all_tests.py
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
)

set_tests_properties(run_all_tests PROPERTIES
    ENVIRONMENT "UCIS_LIB_PATH=${CMAKE_BINARY_DIR}/src/native"
)

# Add custom target to run tests
add_custom_target(check
    COMMAND ${CMAKE_CTEST_COMMAND} --output-on-failure
    DEPENDS ucis
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    COMMENT "Running UCIS tests..."
)
