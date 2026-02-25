# Verilator Coverage to UCIS Example

This example demonstrates how to use Verilator to collect code coverage and property coverage from a SystemVerilog design, and convert it to a UCIS SQLite database (.cdb) that can be viewed with PyUCIS tools.

> **🤖 AI-Assisted Coverage Analysis:** Want to learn how AI agents can analyze this coverage data? Check out the **[AI-Assisted Workflow Example](../ai_assisted_workflow/README.md)** which uses this example's data to demonstrate 13 scenarios for intelligent coverage analysis!

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
# Complete flow: build all tests, run, convert, merge, and view
make view
```

This single command will:
1. Build all 5 test simulations with coverage enabled
2. Run each test and collect separate coverage files
3. Convert each coverage file to UCIS SQLite format
4. Merge all databases into a unified coverage database
5. Launch the interactive TUI viewer

Or run step by step:
```bash
# 1. Run all tests and collect coverage
make run-all

# 2. Convert all coverage files to UCIS databases
make convert-all

# 3. Merge databases into merged.cdb
make merge

# 4. View the merged coverage database
pyucis view --input-format sqlite coverage/merged.cdb

# 5. Or generate text reports
make report
```

The result is a `coverage/merged.cdb` SQLite database containing all coverage from 5 tests:
- **5 test runs** merged into a single database (counter_tb, test_basic_counting, test_load_operations, test_overflow, test_reset)
- **748 line coverage items** tracking code execution
- **918 branch coverage items** tracking control flow decisions
- **4,284 toggle coverage items** tracking signal transitions
- Full source file tracking with line number information
- Test contribution history showing which tests cover which items

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

The new multi-test workflow automatically converts and merges all tests:
```bash
make merge
```

This runs:
1. `make run-all` - Runs all 5 tests, each generating a `.dat` file
2. `make convert-all` - Converts each `.dat` file to a UCIS SQLite `.cdb` database
3. Merges all individual `.cdb` files into `coverage/merged.cdb`

**PyUCIS Built-in Converter:**
- Uses the `vltcov` format (SystemC::Coverage-3)
- Parses Verilator's `.dat` file automatically
- Creates proper UCIS SQLite database
- No custom converter script needed!

For manual single-test conversion:
```bash
PYTHONPATH=$(cd ../.. && pwd)/src pyucis convert \
    --input-format vltcov --output-format sqlite \
    coverage/counter_tb.dat -o coverage/counter_tb.cdb
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
# OR view the merged database directly:
pyucis view coverage/merged.cdb
# OR with explicit format:
pyucis view --input-format sqlite coverage/merged.cdb
```

The TUI launches with a **Dashboard** that immediately shows code coverage statistics including:
- Line/Statement coverage with hit counts and percentages
- Branch coverage showing control flow coverage
- Toggle coverage displaying signal transition metrics

Navigate between views using number keys:

The TUI provides:
- **Dashboard** - Overall coverage statistics including line, branch, and toggle coverage (press '1')
- **Hierarchy** - Navigate design structure (press '2')
- **Gaps** - Identify uncovered items (press '3')
- **Hotspots** - Priority coverage targets (press '4')
- **Metrics** - Statistical analysis (press '5')
- **Code Coverage** - File-level line, branch, and toggle coverage details (press '6')
- **Test History** - View test contribution to coverage (press '7')
- **Help** - Keyboard shortcuts (press '?')

**Note**: PyUCIS now includes automatic format detection. `.cdb`, `.db`, and `.sqlite` files are automatically recognized as SQLite databases.

#### Command-Line Reports
```bash
make report
# OR manually:
pyucis show summary coverage/merged.cdb
pyucis show hierarchy coverage/merged.cdb
```

### Generating Different Report Formats

PyUCIS can export coverage to various formats:

```bash
# Note: Export formats work best with XML intermediate format
# First, export from SQLite to XML
pyucis convert --input-format sqlite --output-format xml \
    coverage/merged.cdb -o coverage/merged.xml

# Then convert XML to desired format
pyucis report coverage/merged.xml --format lcov -o coverage.lcov
pyucis report coverage/merged.xml --format cobertura -o coverage.xml
pyucis report coverage/merged.xml --format html -o coverage.html
pyucis report coverage/merged.xml --format json -o coverage.json
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

The example already demonstrates merging with the multi-test workflow:
```bash
# The recommended approach - use make targets
make run-all      # Run all 5 tests
make convert-all  # Convert each test
make merge        # Merge into coverage/merged.cdb
make view         # View merged results
```

Manual merging example:
```bash
# Run individual tests and convert them
./obj_dir/Vcounter_tb && mv coverage.dat coverage/test1.dat
pyucis convert --input-format vltcov --output-format sqlite \
    coverage/test1.dat -o coverage/test1.cdb

./obj_dir/Vtest_basic_counting && mv coverage.dat coverage/test2.dat
pyucis convert --input-format vltcov --output-format sqlite \
    coverage/test2.dat -o coverage/test2.cdb

# Merge databases
pyucis merge --input-format sqlite --output-format sqlite \
    -o coverage/merged.cdb coverage/test1.cdb coverage/test2.cdb
pyucis view coverage/merged.cdb
```

### Coverage-Driven Verification

Use PyUCIS to identify coverage gaps:
```bash
# Find coverage gaps below 80%
pyucis show gaps coverage/merged.cdb --threshold 80

# Identify priority targets
pyucis show hotspots coverage/merged.cdb

# Export for external analysis
pyucis report coverage/merged.cdb --format json -o coverage.json
```

### Integration with CI/CD

```yaml
# Example GitLab CI configuration
test_with_coverage:
  script:
    - cd examples/verilator
    - make merge  # Runs tests, converts, and merges
    - pyucis report coverage/merged.cdb --format cobertura -o coverage.xml
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
| `make all` or `make build` | Build all test executables with coverage |
| `make run-all` | Run all tests and collect coverage files |
| `make convert-all` | Convert all coverage files to UCIS SQLite |
| `make merge` | Merge all test databases into merged.cdb |
| `make view` | Launch PyUCIS TUI (runs merge first) |
| `make report` | Generate text coverage reports |
| `make run TEST=<name>` | Run a specific test |
| `make view-test TEST=<name>` | View specific test coverage |
| `make clean` | Remove build artifacts |
| `make distclean` | Remove everything including coverage DB |
| `make help` | Show all available targets |

## Files Generated

- `obj_dir/` - Verilator build directory
- `coverage/*.dat` - Verilator coverage data files (one per test)
- `coverage/*.cdb` - Individual UCIS SQLite databases (one per test)
- `coverage/merged.cdb` - Merged UCIS SQLite database (final format with all tests)
- `logs/` - Simulation logs (if generated)

## References

- [Verilator Manual](https://verilator.org/guide/latest/)
- [Verilator Coverage](https://verilator.org/guide/latest/exe_verilator_coverage.html)
- [PyUCIS Documentation](https://github.com/fvutils/pyucis)
- [UCIS Standard](https://www.accellera.org/downloads/standards/ucis)
- [SystemVerilog Assertions](https://standards.ieee.org/standard/1800-2017.html)

## Related Examples

### AI-Assisted Coverage Analysis

Want to see how AI agents can work with this coverage data? The **[AI-Assisted Workflow Example](../ai_assisted_workflow/README.md)** uses this example's coverage database to demonstrate:

- 13 detailed scenarios for coverage analysis
- Command selection and decision trees for AI agents
- Integration with CI/CD pipelines
- Test optimization and gap analysis
- Automated validation scripts

Perfect for learning how to:
- Query coverage programmatically
- Identify redundant tests
- Generate reports for different tools (LCOV, Cobertura)
- Make data-driven testing decisions

See **[../ai_assisted_workflow/README.md](../ai_assisted_workflow/README.md)** to get started!

## License

Apache License 2.0 - See LICENSE file in the repository root

## Support

For issues or questions:
- PyUCIS Issues: https://github.com/fvutils/pyucis/issues
- Verilator Issues: https://github.com/verilator/verilator/issues
