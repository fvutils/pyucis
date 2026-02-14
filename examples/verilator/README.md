# Verilator Coverage to UCIS Example

This example demonstrates how to use Verilator to collect code coverage and property coverage from a SystemVerilog design, and convert it to a UCIS SQLite database (.cdb) that can be viewed with PyUCIS tools.

## Overview

This example includes:
- **counter.sv** - A parametric counter module with SystemVerilog assertions (SVA) and covergroups
- **counter_tb.sv** - A testbench that exercises the counter through various scenarios
- **sim_main.cpp** - C++ wrapper for Verilator simulation with coverage collection
- **verilator2ucis.py** - Conversion tool from Verilator coverage format to UCIS SQLite
- **Makefile** - Build and run automation

## Features Demonstrated

### Code Coverage
- **Line coverage** - Tracks which lines of code are executed
- **Toggle coverage** - Monitors signal bit transitions
- **Branch coverage** - Tracks control flow branches

### Functional Coverage
- **Covergroups** - Systematic tracking of interesting scenarios (in design)
- **Coverpoints** - Monitor specific signal values
- **Cross coverage** - Track combinations of signals
- **Bins** - Organize values into meaningful groups

### Built-in Verilator Support
- **Native Parser** - PyUCIS includes `vltcov` format for SystemC::Coverage-3
- **No Dependencies** - No external converter scripts needed
- **Full Integration** - Works with all PyUCIS commands and tools

## Prerequisites

1. **Verilator** (version 5.0 or later)
   ```bash
   verilator --version
   ```

2. **PyUCIS** (installed in development mode or via pip)
   ```bash
   pip install pyucis
   # OR from source:
   cd /path/to/pyucis && pip install -e .
   ```

3. **Python 3.7+** with required dependencies

## Quick Start

Run everything with a single command:
```bash
# Complete flow: build, simulate, convert, and view
make run convert view
```

Or step by step:
```bash
# 1. Build Verilator simulation with coverage enabled
make build

# 2. Run the simulation (generates coverage.dat)
make run

# 3. Convert to UCIS SQLite format (.cdb)
make convert

# 4. View the coverage database
make view

# 5. Or generate text reports
make report
```

The result is a `coverage/coverage.cdb` file - a SQLite database containing:
- **17 design scopes** (modules, instances)
- **218 coverage items** (lines, toggles, branches, expressions)
- Full source file tracking and line number information

## Detailed Usage

### Building with Coverage

The Makefile configures Verilator with these coverage flags:
```makefile
VERILATOR_COV_FLAGS = --coverage --coverage-line --coverage-toggle --coverage-user
```

- `--coverage` - Enable coverage collection
- `--coverage-line` - Track line coverage
- `--coverage-toggle` - Track toggle coverage (signal transitions)
- `--coverage-user` - Track user-defined coverage (covergroups)

### Running the Simulation

```bash
make run
```

This command:
1. Compiles the SystemVerilog design with Verilator
2. Runs the simulation
3. Generates `coverage.dat` file with coverage data

Expected output:
```
Building Verilator simulation with coverage...
Running simulation...
Test 1: Basic counting
Test 2: Load operation
Test 3: Disable counting
Test 4: Load while enabled
Test 5: Count to overflow
Test 6: Multiple overflow events
Test 7: Random operations
Simulation completed successfully!
```

### Converting to UCIS

```bash
make convert
# OR directly:
PYTHONPATH=$(cd ../.. && pwd)/src pyucis convert \
    --input-format vltcov --output-format sqlite \
    coverage.dat -o coverage/coverage.cdb
```

**PyUCIS Built-in Converter:**
- Uses the `vltcov` format (SystemC::Coverage-3)
- Parses Verilator's `.dat` file automatically
- Creates proper UCIS SQLite database
- No custom converter script needed!

### Viewing Coverage

#### Interactive TUI (Terminal User Interface)
```bash
make view
# OR (auto-detects format from .cdb extension)
pyucis view coverage/coverage.cdb
# OR with explicit format
pyucis view --input-format sqlite coverage/coverage.cdb
```

The TUI provides:
- **Dashboard** - Overall coverage statistics (press '1')
- **Hierarchy** - Navigate design structure (press '2')
- **Gaps** - Identify uncovered items (press '3')
- **Hotspots** - Priority coverage targets (press '4')
- **Metrics** - Statistical analysis (press '5')
- **Help** - Keyboard shortcuts (press '?')

**Note**: PyUCIS now includes automatic format detection. `.cdb`, `.db`, and `.sqlite` files are automatically recognized as SQLite databases.

#### Command-Line Reports
```bash
make report
# OR manually (auto-detects format):
pyucis show summary coverage/coverage.cdb
pyucis show hierarchy coverage/coverage.cdb
```

### Generating Different Report Formats

PyUCIS can export coverage to various formats:

```bash
# Note: Export formats work best with XML intermediate format
# First, export from SQLite to XML
pyucis convert --input-format sqlite --output-format xml \
    coverage/coverage.cdb -o coverage/coverage.xml

# Then convert XML to desired format
pyucis report coverage/coverage.xml --format lcov -o coverage.lcov
pyucis report coverage/coverage.xml --format cobertura -o coverage.xml
pyucis report coverage/coverage.xml --format html -o coverage.html
pyucis report coverage/coverage.xml --format json -o coverage.json
```

## Understanding the Coverage Database

The UCIS SQLite database (.cdb) contains:

### Hierarchical Structure
```
Root
└── Design Units (modules)
    ├── Line Coverage Items
    ├── Toggle Coverage Items
    └── Covergroups
        └── Coverpoints
            └── Bins (with hit counts)
```

### Metadata
- Test name and status
- Simulation date and time
- Tool information (Verilator)
- Source file locations

### Coverage Types
1. **Line Coverage** - Execution counts per source line
2. **Toggle Coverage** - Bit transition counts per signal
3. **Functional Coverage** - Coverpoint bin hit counts
4. **Property Coverage** - Assertion pass/fail status

## Customization

### Modifying the Design

Edit `counter.sv` to:
- Add more coverpoints
- Define additional assertions
- Create new cross-coverage combinations
- Adjust bins and ranges

### Extending the Testbench

Edit `counter_tb.sv` to:
- Add new test scenarios
- Increase simulation time
- Modify stimulus patterns
- Target specific coverage goals

### Conversion Script Options

The `verilator2ucis.py` script can be extended to:
- Parse additional coverage types
- Add custom metadata
- Filter coverage data
- Merge multiple coverage files

## Advanced Features

### Merging Multiple Test Runs

```bash
# Run multiple tests
./obj_dir/Vcounter_tb    # Creates coverage.dat
python3 verilator2ucis.py coverage.dat test1.cdb

# Run another test (different seed/config)
./obj_dir/Vcounter_tb
python3 verilator2ucis.py coverage.dat test2.cdb

# Merge databases
pyucis merge test1.cdb test2.cdb -o merged.cdb
pyucis view merged.cdb
```

### Coverage-Driven Verification

Use PyUCIS to identify coverage gaps:
```bash
# Find coverage gaps below 80%
pyucis show gaps coverage/coverage.cdb --threshold 80

# Identify priority targets
pyucis show hotspots coverage/coverage.cdb

# Export for external analysis
pyucis report coverage/coverage.cdb --format json -o coverage.json
```

### Integration with CI/CD

```yaml
# Example GitLab CI configuration
test_with_coverage:
  script:
    - cd examples/verilator
    - make run
    - make convert
    - pyucis report coverage/coverage.cdb --format cobertura -o coverage.xml
  coverage: '/TOTAL.*\s+(\d+%)/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: examples/verilator/coverage.xml
```

## Troubleshooting

### Verilator Not Found
```bash
# Check installation
which verilator
verilator --version

# Install on Ubuntu/Debian
sudo apt-get install verilator

# Or build from source
git clone https://github.com/verilator/verilator
cd verilator
autoconf && ./configure && make && sudo make install
```

### PyUCIS Import Errors
```bash
# Install in development mode
cd /path/to/pyucis
pip install -e .

# Or install from PyPI
pip install pyucis
```

### Coverage File Not Generated
- Ensure Verilator coverage flags are enabled (`--coverage`)
- Check that simulation completes successfully
- Verify `VerilatedCov::write()` is called in sim_main.cpp

### Conversion Errors
- Verify coverage.dat exists and is readable
- Check Python version (3.7+ required)
- Ensure PyUCIS is properly installed

## Makefile Targets

| Target | Description |
|--------|-------------|
| `make all` or `make build` | Compile Verilator simulation with coverage |
| `make run` | Run simulation and generate coverage.dat |
| `make convert` | Convert coverage.dat to UCIS SQLite |
| `make view` | Launch PyUCIS interactive TUI |
| `make report` | Generate text coverage reports |
| `make clean` | Remove build artifacts |
| `make distclean` | Remove everything including coverage DB |
| `make help` | Show all available targets |

## Files Generated

- `obj_dir/` - Verilator build directory
- `coverage.dat` - Verilator coverage data (intermediate format)
- `coverage/coverage.cdb` - UCIS SQLite database (final format)
- `logs/` - Simulation logs

## References

- [Verilator Manual](https://verilator.org/guide/latest/)
- [Verilator Coverage](https://verilator.org/guide/latest/exe_verilator_coverage.html)
- [PyUCIS Documentation](https://github.com/fvutils/pyucis)
- [UCIS Standard](https://www.accellera.org/activities/committees/ucis)
- [SystemVerilog Assertions](https://standards.ieee.org/standard/1800-2017.html)

## License

Apache License 2.0 - See LICENSE file in the repository root

## Support

For issues or questions:
- PyUCIS Issues: https://github.com/fvutils/pyucis/issues
- Verilator Issues: https://github.com/verilator/verilator/issues
