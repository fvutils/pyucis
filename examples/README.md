# PyUCIS Examples

This directory contains example applications demonstrating PyUCIS usage.

## Available Examples

### Verilator Coverage Example

**Location:** `verilator/`

**Description:** Complete workflow for collecting coverage from Verilator simulations and converting to UCIS SQLite format.

**Quick Start:**
```bash
cd verilator
make run convert view
```

**Features:**
- SystemVerilog counter design with covergroups
- Automated build and test flow with Makefile
- Verilator coverage collection (line, toggle, branch, expression)
- Conversion from Verilator .dat to UCIS SQLite .cdb format
- Interactive viewing with PyUCIS TUI
- 218 coverage items across 17 design scopes

**Files:** ~1,100 lines of code including:
- SystemVerilog design (counter.sv, counter_tb.sv)
- Python conversion tool (verilator2ucis.py)
- Build automation (Makefile)
- Comprehensive documentation (README.md, EXAMPLE_SUMMARY.md)

**Requirements:**
- Verilator 5.0+
- Python 3.7+
- PyUCIS

**See:** `verilator/README.md` for detailed documentation

---

## Contributing Examples

To add a new example:
1. Create a subdirectory with a descriptive name
2. Include a README.md with usage instructions
3. Provide working code and test data
4. Update this file with a link to your example

## License

All examples are licensed under Apache License 2.0
