# Building UCIS Native Library

This document describes how to build the UCIS native C library using CMake.

## Prerequisites

- CMake 3.12 or higher
- C compiler (gcc, clang, etc.)
- Python 3 (for tests)
- SQLite3 amalgamation (included in `packages/sqlite/`)

## Quick Start

### Build with CMake (Recommended)

```bash
# From project root
mkdir build
cd build
cmake ..
make

# Run tests
ctest --output-on-failure
# or
make check
```

### Build from native directory

```bash
# From src/native
mkdir build
cd build
cmake ..
make

# Run tests
ctest --output-on-failure
```

### Build with Make (Legacy)

```bash
cd src/native
make
make test
```

## CMake Build Options

The following options can be passed to CMake using `-D<OPTION>=ON/OFF`:

| Option | Default | Description |
|--------|---------|-------------|
| `UCIS_BUILD_TESTS` | `ON` | Build test suite |
| `UCIS_BUILD_SHARED` | `ON` | Build shared library (libucis.so) |
| `UCIS_BUILD_STATIC` | `OFF` | Build static library (libucis.a) |
| `UCIS_ENABLE_ASAN` | `OFF` | Enable AddressSanitizer for debugging |

### Examples

```bash
# Build with both shared and static libraries
cmake -DUCIS_BUILD_STATIC=ON ..

# Build without tests
cmake -DUCIS_BUILD_TESTS=OFF ..

# Debug build with AddressSanitizer
cmake -DCMAKE_BUILD_TYPE=Debug -DUCIS_ENABLE_ASAN=ON ..

# Release build with optimizations
cmake -DCMAKE_BUILD_TYPE=Release ..
```

## Build Configurations

### Debug Build

```bash
mkdir build-debug
cd build-debug
cmake -DCMAKE_BUILD_TYPE=Debug ..
make
```

Debug builds include:
- Debug symbols (`-g`)
- No optimizations (`-O0`)
- Better error messages
- Optional AddressSanitizer support

### Release Build

```bash
mkdir build-release
cd build-release
cmake -DCMAKE_BUILD_TYPE=Release ..
make
```

Release builds include:
- Optimizations (`-O2`)
- No debug symbols
- Smaller binary size

## Installation

```bash
# Install to default prefix (/usr/local)
sudo make install

# Install to custom prefix
cmake -DCMAKE_INSTALL_PREFIX=/opt/ucis ..
make
sudo make install
```

This installs:
- `lib/libucis.so` - Shared library
- `include/ucis.h` - Public API header
- `include/ucis_types.h` - Type definitions
- `lib/cmake/ucis/` - CMake config files

## Using Installed Library

### In CMake projects

```cmake
find_package(ucis REQUIRED)
target_link_libraries(your_target PRIVATE ucis::ucis)
```

### Manual compilation

```bash
gcc -o myapp myapp.c -lucis -I/usr/local/include -L/usr/local/lib
```

## Running Tests

### All tests

```bash
# From build directory
ctest --output-on-failure

# or with verbose output
ctest -V

# or using make target
make check
```

### Individual tests

```bash
ctest -R test_basic
ctest -R test_scopes
ctest -R test_coverage
```

### Running test scripts directly

```bash
cd src/native/test

# Set library path
export LD_LIBRARY_PATH=../../../build/src/native:$LD_LIBRARY_PATH

# Run tests
python3 test_basic.py
python3 test_scopes.py
python3 run_all_tests.py
```

## Directory Structure

```
src/native/
├── CMakeLists.txt           # Main CMake configuration
├── ucisConfig.cmake.in      # CMake package config template
├── Makefile                 # Legacy Makefile
├── *.c, *.h                 # Source files
└── test/
    ├── CMakeLists.txt       # Test configuration
    ├── ucis_loader.py       # Helper to load library
    ├── test_*.py            # Test scripts
    └── run_all_tests.py     # Test runner
```

## Build Output

After building, you'll find:

```
build/
├── src/native/
│   ├── libucis.so           # Shared library
│   └── test/
│       ├── test_*.py        # Copied test scripts
│       └── *.ucisdb         # Test databases (generated)
└── Testing/
    └── Temporary/           # CTest output
```

## Troubleshooting

### Library not found

If tests fail with "library not found":

```bash
# Set LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$PWD/build/src/native:$LD_LIBRARY_PATH

# Or use ld.so.conf (system-wide, requires root)
echo "/path/to/build/src/native" | sudo tee /etc/ld.so.conf.d/ucis.conf
sudo ldconfig
```

### SQLite not found

The build uses SQLite from `packages/sqlite/sqlite-amalgamation-3470200/`. 
If this directory is missing, you'll get an error. The SQLite amalgamation should already be present in the repository.

### Compiler warnings

The build uses strict compiler flags. If you see warnings:
- Fix them (preferred)
- Or disable specific warnings: `cmake -DCMAKE_C_FLAGS="-Wno-specific-warning" ..`

## Performance Notes

- Release builds are significantly faster (up to 10x)
- Enable threading with `-DSQLITE_THREADSAFE=1` (default)
- For debugging memory issues, use AddressSanitizer: `-DUCIS_ENABLE_ASAN=ON`

## Cross-Compilation

For cross-compilation, specify a toolchain file:

```bash
cmake -DCMAKE_TOOLCHAIN_FILE=path/to/toolchain.cmake ..
```

## Continuous Integration

Example CI configuration:

```yaml
# .github/workflows/build.yml
build:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v2
    - name: Build
      run: |
        mkdir build && cd build
        cmake -DCMAKE_BUILD_TYPE=Release ..
        make -j$(nproc)
    - name: Test
      run: |
        cd build
        ctest --output-on-failure
```
