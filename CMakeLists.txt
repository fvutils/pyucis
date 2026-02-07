# Top-level CMakeLists.txt for pyucis-sqlite
cmake_minimum_required(VERSION 3.12)
project(pyucis-sqlite VERSION 1.0.0 LANGUAGES C)

# Enable testing at top level
enable_testing()

# Include native library
add_subdirectory(src/native)

# Print build summary
message(STATUS "")
message(STATUS "pyucis-sqlite Build Configuration:")
message(STATUS "  Version:          ${PROJECT_VERSION}")
message(STATUS "  Source dir:       ${CMAKE_SOURCE_DIR}")
message(STATUS "  Build dir:        ${CMAKE_BINARY_DIR}")
message(STATUS "  Install prefix:   ${CMAKE_INSTALL_PREFIX}")
message(STATUS "")
