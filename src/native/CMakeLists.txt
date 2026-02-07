# CMakeLists.txt for UCIS C API Native Library
cmake_minimum_required(VERSION 3.12)
project(ucis VERSION 1.0.0 LANGUAGES C)

# Project options
option(UCIS_BUILD_TESTS "Build tests" ON)
option(UCIS_BUILD_SHARED "Build shared library" ON)
option(UCIS_BUILD_STATIC "Build static library" OFF)
option(UCIS_ENABLE_ASAN "Enable AddressSanitizer" OFF)

# C standard
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Build type
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Compiler flags
add_compile_options(
    -Wall
    -Wextra
    -Wpedantic
    $<$<CONFIG:Debug>:-g>
    $<$<CONFIG:Debug>:-O0>
    $<$<CONFIG:Release>:-O2>
)

# Position Independent Code for shared library
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# AddressSanitizer support
if(UCIS_ENABLE_ASAN)
    add_compile_options(-fsanitize=address -fno-omit-frame-pointer)
    add_link_options(-fsanitize=address)
endif()

# Find SQLite3 from packages directory
set(SQLITE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../packages/sqlite/sqlite-amalgamation-3470200")

if(EXISTS "${SQLITE_DIR}/sqlite3.c")
    message(STATUS "Using SQLite3 from packages directory: ${SQLITE_DIR}")
    
    # Create SQLite3 library target
    add_library(sqlite3_embedded STATIC
        ${SQLITE_DIR}/sqlite3.c
    )
    
    target_include_directories(sqlite3_embedded PUBLIC
        ${SQLITE_DIR}
    )
    
    target_compile_definitions(sqlite3_embedded PUBLIC
        SQLITE_ENABLE_COLUMN_METADATA
        SQLITE_ENABLE_FTS5
        SQLITE_ENABLE_JSON1
        SQLITE_ENABLE_RTREE
        SQLITE_THREADSAFE=1
    )
    
    target_link_libraries(sqlite3_embedded PUBLIC
        pthread
        dl
        m
    )
    
    # Create alias for consistency
    add_library(SQLite::SQLite3 ALIAS sqlite3_embedded)
    set(SQLite3_FOUND TRUE)
else()
    # Fall back to system SQLite3
    find_package(SQLite3 REQUIRED)
    if(NOT TARGET SQLite::SQLite3)
        # Create alias if package doesn't provide it
        add_library(SQLite::SQLite3 INTERFACE IMPORTED)
        set_target_properties(SQLite::SQLite3 PROPERTIES
            INTERFACE_INCLUDE_DIRECTORIES "${SQLite3_INCLUDE_DIRS}"
            INTERFACE_LINK_LIBRARIES "${SQLite3_LIBRARIES}"
        )
    endif()
endif()

# UCIS library source files
set(UCIS_SOURCES
    ucis_api.c
    ucis_handle.c
    ucis_util.c
    ucis_schema.c
    ucis_scope.c
    ucis_iterator.c
    ucis_cover.c
)

set(UCIS_HEADERS
    ucis.h
    ucis_types.h
    ucis_impl.h
)

# Shared library target
if(UCIS_BUILD_SHARED)
    add_library(ucis SHARED ${UCIS_SOURCES})
    
    target_include_directories(ucis
        PUBLIC
            $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
            $<INSTALL_INTERFACE:include>
    )
    
    target_compile_definitions(ucis PRIVATE
        SQLITE_ENABLE_COLUMN_METADATA
    )
    
    if(TARGET SQLite::SQLite3)
        target_link_libraries(ucis PRIVATE SQLite::SQLite3)
    else()
        target_link_libraries(ucis PRIVATE SQLite::SQLite3)
    endif()
    
    target_link_libraries(ucis PRIVATE
        pthread
        dl
        m
    )
    
    set_target_properties(ucis PROPERTIES
        VERSION ${PROJECT_VERSION}
        SOVERSION ${PROJECT_VERSION_MAJOR}
        OUTPUT_NAME "ucis"
        PUBLIC_HEADER "${UCIS_HEADERS}"
    )
endif()

# Static library target
if(UCIS_BUILD_STATIC)
    add_library(ucis_static STATIC ${UCIS_SOURCES})
    
    target_include_directories(ucis_static
        PUBLIC
            $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
            $<INSTALL_INTERFACE:include>
    )
    
    target_compile_definitions(ucis_static PRIVATE
        SQLITE_ENABLE_COLUMN_METADATA
    )
    
    if(TARGET SQLite::SQLite3)
        target_link_libraries(ucis_static PRIVATE SQLite::SQLite3)
    else()
        target_link_libraries(ucis_static PRIVATE SQLite::SQLite3)
    endif()
    
    target_link_libraries(ucis_static PRIVATE
        pthread
        dl
        m
    )
    
    set_target_properties(ucis_static PROPERTIES
        OUTPUT_NAME "ucis"
        PUBLIC_HEADER "${UCIS_HEADERS}"
    )
endif()

# Installation
include(GNUInstallDirs)

if(UCIS_BUILD_SHARED)
    install(TARGETS ucis
        EXPORT ucisTargets
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    )
endif()

if(UCIS_BUILD_STATIC)
    install(TARGETS ucis_static
        EXPORT ucisTargets
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    )
endif()

# Install CMake config files
install(EXPORT ucisTargets
    FILE ucisTargets.cmake
    NAMESPACE ucis::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/ucis
)

# Create config file
include(CMakePackageConfigHelpers)

configure_package_config_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/ucisConfig.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/ucisConfig.cmake
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/ucis
)

write_basic_package_version_file(
    ${CMAKE_CURRENT_BINARY_DIR}/ucisConfigVersion.cmake
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

install(FILES
    ${CMAKE_CURRENT_BINARY_DIR}/ucisConfig.cmake
    ${CMAKE_CURRENT_BINARY_DIR}/ucisConfigVersion.cmake
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/ucis
)

# Tests
if(UCIS_BUILD_TESTS)
    # Tests are now located in tests/unit/native
    add_subdirectory(${CMAKE_SOURCE_DIR}/tests/unit/native ${CMAKE_BINARY_DIR}/tests/unit/native)
endif()

# Print configuration summary
message(STATUS "")
message(STATUS "UCIS Configuration Summary:")
message(STATUS "  Version:          ${PROJECT_VERSION}")
message(STATUS "  Build type:       ${CMAKE_BUILD_TYPE}")
message(STATUS "  C Compiler:       ${CMAKE_C_COMPILER}")
message(STATUS "  Build shared:     ${UCIS_BUILD_SHARED}")
message(STATUS "  Build static:     ${UCIS_BUILD_STATIC}")
message(STATUS "  Build tests:      ${UCIS_BUILD_TESTS}")
message(STATUS "  SQLite3 found:    ${SQLite3_FOUND}")
message(STATUS "  Enable ASAN:      ${UCIS_ENABLE_ASAN}")
message(STATUS "  Install prefix:   ${CMAKE_INSTALL_PREFIX}")
message(STATUS "")
