# Verilator Coverage Import for PyUCIS

This module provides import support for Verilator's coverage output format (SystemC::Coverage-3) into PyUCIS.

## Features

- **Format Support**: Imports Verilator `.dat` coverage files (SystemC::Coverage-3 format)
- **Coverage Types**: 
  - ✅ Functional Coverage (covergroups, coverpoints, bins)
  - ⚠️  Code Coverage (line, branch, toggle) - parsed but not yet mapped due to PyUCIS limitations
- **Integration**: Registered as `vltcov` format in PyUCIS format registry
- **Output**: Convert to XML, SQLite, or other UCIS formats

## Installation

The Verilator coverage import is included in PyUCIS. Install dependencies:

```bash
pip install lxml python-jsonschema-objects
```

## Usage

### Command Line

**Convert Verilator coverage to XML:**
```bash
pyucis convert --input-format vltcov coverage.dat --out output.xml
```

**Convert to SQLite:**
```bash
pyucis convert --input-format vltcov --output-format sqlite \
       coverage.dat --out output.ucis
```

**Merge multiple Verilator runs:**
```bash
pyucis merge --input-format vltcov run1.dat run2.dat --out merged.xml
```

### Python API

```python
from ucis.rgy.format_rgy import FormatRgy

# Get format registry
rgy = FormatRgy.inst()
desc = rgy.getDatabaseDesc('vltcov')
fmt_if = desc.fmt_if()

# Import Verilator coverage
db = fmt_if.read('coverage.dat')

# Export to XML
db.write('output.xml')
```

## Verilator Coverage Format

Verilator outputs coverage in SystemC::Coverage-3 format:
- **File Extension**: `.dat`
- **Format**: Text-based with compact key-value encoding
- **Delimiters**: Uses ASCII control characters `\001` and `\002`
- **Coverage Types**: Line, branch, toggle, and functional coverage

### Example Coverage Entry
```
C '\001t\002funccov\001page\002v_funccov/cg1\001f\002test.v\001l\00219\001bin\002low\001h\002cg1.cp\001' 42
```

This decodes to:
- Type: functional coverage
- Covergroup: `cg1`
- File: `test.v`, line 19
- Bin: `low`
- Hits: 42

## Current Limitations

### Code Coverage Not Fully Mapped

Line, branch, and toggle coverage are **parsed correctly** but not yet mapped to the UCIS database. This is due to a limitation in PyUCIS's MemUCIS implementation, which doesn't support creating code coverage scopes (BLOCK, BRANCH, TOGGLE) under design units or instances.

**Workaround**: The data is still parsed and available in intermediate structures. Future PyUCIS versions may add full support.

**Status**: Functional coverage (covergroups, bins) works perfectly. This is typically the primary use case for merging and analyzing SystemVerilog functional coverage.

## Implementation Details

### Components

1. **vlt_parser.py**: Parses SystemC::Coverage-3 format
   - Handles control character delimiters
   - Extracts all coverage metadata
   - Groups by coverage type

2. **vlt_coverage_item.py**: Data structure for coverage items
   - Stores parsed coverage data
   - Provides type checking (is_functional_coverage, etc.)
   - Extracts covergroup/bin names

3. **vlt_to_ucis_mapper.py**: Maps to UCIS database
   - Creates scope hierarchy (DU → instances → covergroups → coverpoints)
   - Creates cover items with hit counts
   - Manages file handles and source info

4. **db_format_if_vltcov.py**: Format interface
   - Registered as 'vltcov' format
   - Read-only (write not yet implemented)
   - Integrates with PyUCIS CLI

### Architecture

```
Verilator .dat file
       ↓
VltParser (parse format)
       ↓
VltCoverageItem list
       ↓
VltToUcisMapper (build UCIS)
       ↓
UCIS Database (MemUCIS)
       ↓
Export (XML, SQLite, etc.)
```

## Testing

Test with actual Verilator coverage files:

```bash
# Set up environment
cd /path/to/pyucis-vltcov
export PYTHONPATH=src

# Test import
python3 -c "
from ucis.rgy.format_rgy import FormatRgy
rgy = FormatRgy.inst()
db = rgy.getDatabaseDesc('vltcov').fmt_if().read('coverage.dat')
print(f'✓ Imported successfully')
"

# Test conversion
python3 -m ucis convert --input-format vltcov coverage.dat --out test.xml
```

## Future Enhancements

- [ ] Full code coverage mapping (when PyUCIS adds support)
- [ ] Write support (export to Verilator format)
- [ ] Coverage merging optimizations
- [ ] Additional Verilator-specific features

## References

- **Verilator Documentation**: https://verilator.org/guide/latest/
- **UCIS Specification**: IEEE 1800.2
- **Implementation**: `/home/mballance/projects/verilator/verilator-funccov`

## Contributing

The implementation follows PyUCIS patterns:
- Format interfaces extend `FormatIfDb`
- Register with `FormatRgy`
- Use UCIS API for database construction

See existing format implementations (XML, SQLite) for examples.

## License

Apache License 2.0 (same as PyUCIS)
