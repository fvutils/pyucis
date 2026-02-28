# pyucis
Python API to Unified Coverage Interoperability Standard (UCIS) Data Model

[![Build Status](https://dev.azure.com/mballance/fvutils/_apis/build/status/fvutils.pyucis?branchName=master)](https://dev.azure.com/mballance/fvutils/_build/latest?definitionId=16&branchName=master)
[![PyPI version](https://badge.fury.io/py/pyucis.svg)](https://badge.fury.io/py/pyucis)
[![PyPI](https://img.shields.io/pypi/dm/pyucis.svg?label=PyPI%20downloads)](https://pypi.org/project/pyucis/)

## Features

- **Python API** for manipulating UCIS coverage databases
- **CLI Tools** for database conversion, merging, and reporting
- **Coverage Import** - Import from Verilator, cocotb-coverage, and AVL frameworks
- **MCP Server** for AI agent integration (see [MCP_SERVER.md](MCP_SERVER.md))
- **AgentSkills Support** for enhanced AI agent understanding (see https://agentskills.io)
- Support for XML, YAML, and UCIS binary formats
- Multiple export formats: LCOV, Cobertura, JaCoCo, Clover

## Installation

```bash
# Standard installation
pip install pyucis

# With MCP server support
pip install pyucis[dev]
```

## Usage

### Command Line Interface

```bash
# Convert coverage database
pyucis convert --input-format xml --output-format yaml input.xml -o output.yaml

# Merge multiple databases
pyucis merge db1.xml db2.xml db3.xml -o merged.xml

# Generate reports
pyucis report coverage.xml -o report.txt

# Interactive Terminal UI (NEW!)
pyucis view coverage.xml

# Query coverage information
pyucis show summary coverage.xml
pyucis show gaps coverage.xml --threshold 80
pyucis show covergroups coverage.xml
```

### Interactive Terminal UI

PyUCIS now includes an interactive Terminal User Interface (TUI) for exploring coverage databases:

```bash
# Launch the TUI
pyucis view coverage.xml
```

**Features:**
- **Dashboard View** - High-level coverage overview with statistics
- **Hierarchy View** - Navigate design structure with interactive tree
- **Gaps View** - Identify uncovered items for test planning
- **Hotspots View** - Priority-based improvement targets with P0/P1/P2 classification
- **Metrics View** - Statistical analysis, distributions, and quality indicators
- **Help System** - Comprehensive keyboard shortcuts (press `?`)
- Color-coded coverage indicators (red <50%, yellow 50-80%, green 80%+)
- Keyboard-driven navigation optimized for terminal workflows
- Fast, responsive interface using Rich library

**Keyboard Shortcuts:**
- `1` - Dashboard view
- `2` - Hierarchy view  
- `3` - Gaps view
- `4` - Hotspots view
- `5` - Metrics view
- `↑/↓` - Navigate items
- `←/→` - Collapse/expand tree nodes
- `?` - Help overlay
- `q` - Quit

**Hotspots Analysis:**
The Hotspots view intelligently identifies high-priority coverage targets:
- **P0/P1 (Critical/High):** Low coverage modules (<50%) requiring immediate attention
- **P1/P2 (High/Medium):** Near-complete items (90%+) - low hanging fruit
- **P1 (High):** Completely untested coverpoints

**Metrics & Statistics:**
The Metrics view provides in-depth analysis:
- Coverage distribution by hit count (0, 1-10, 11-100, 100+)
- Statistical measures (mean, median, min, max)
- Quality indicators (complete, high, medium, low tiers)
- Bin utilization and zero-hit ratios

The TUI provides an efficient alternative to HTML reports for real-time coverage analysis, especially useful for:
- Quick coverage assessment during verification
- Identifying coverage gaps without generating static reports
- Priority-driven test planning with hotspot analysis
- Remote terminal sessions over SSH
- CI/CD pipeline integration

### MCP Server for AI Agents

PyUCIS now includes a Model Context Protocol (MCP) server that enables AI agents to interact with coverage databases:

```bash
# Start the MCP server
pyucis-mcp-server
```

See [MCP_SERVER.md](MCP_SERVER.md) for detailed documentation on:
- Available MCP tools (17+ coverage analysis tools)
- Integration with Claude Desktop and other AI platforms
- API usage examples

### AgentSkills Support

PyUCIS includes an [AgentSkills](https://agentskills.io) skill definition that provides LLM agents with comprehensive information about PyUCIS capabilities. When you run any PyUCIS command, the absolute path to the skill file is displayed, allowing agents to reference it for better understanding of UCIS coverage data manipulation.

```bash
# Running any pyucis command displays the skill file location
pyucis --help
# Output includes: Skill Definition: /path/to/ucis/share/SKILL.md
```

### Python API

```python
from ucis import UCIS

# Open a database
db = UCIS("coverage.xml")

# Access coverage data
for scope in db.scopes():
    print(f"Scope: {scope.name}")
    for coveritem in scope.coveritems():
        print(f"  {coveritem.name}: {coveritem.count} hits")
```

### Coverage Import

Import coverage from various verification frameworks:

**Command Line (CLI):**
```bash
# cocotb-coverage (XML/YAML)
pyucis convert --input-format cocotb-xml coverage.xml --output-format xml --out output.xml
pyucis convert --input-format cocotb-yaml coverage.yml --output-format xml --out output.xml

# AVL (JSON)
pyucis convert --input-format avl-json coverage.json --output-format xml --out output.xml

# Merge multiple runs
pyucis merge --input-format cocotb-xml run1.xml run2.xml --output-format xml --out merged.xml
```

**Python API:**

cocotb-coverage (Python testbenches):
```python
from ucis.format_detection import read_coverage_file

# Automatically detects cocotb XML or YAML format
db = read_coverage_file('cocotb_coverage.xml')
db = read_coverage_file('cocotb_coverage.yml')
```

AVL - Apheleia Verification Library:
```python
from ucis.avl import read_avl_json

# Import AVL JSON coverage (all variations supported)
db = read_avl_json('avl_coverage.json')
```

Verilator:
```bash
# Import Verilator coverage via CLI
pyucis convert --input-format vltcov coverage.dat --out coverage.xml
```

See documentation for complete import examples and supported formats.

## Supported Formats

PyUCIS supports bi-directional conversion between formats using the UCIS data model as the common representation.  Conversion is lossy for formats that do not support all UCIS features; a warning is emitted for each unsupported construct (use `--strict` to turn warnings into errors).

| Format | Key | Read | Write | Functional Cov | Code Cov | Toggle Cov | Lossless |
|--------|-----|:----:|:-----:|:--------------:|:--------:|:----------:|:--------:|
| UCIS XML | `xml` | ✓ | ✓ | ✓ | ✓ | - | near |
| UCIS YAML | `yaml` | ✓ | ✓ | ✓ | - | - | - |
| SQLite | `sqlite` | ✓ | ✓ | ✓ | ✓ | ✓ | **✓** |
| **NCDB** | `ncdb` | **✓** | **✓** | **✓** | **✓** | **✓** | **✓** |
| LCOV | `lcov` | - | ✓ | - | ✓ | - | - |
| cocotb YAML | `cocotb-yaml` | ✓ | ✓ | ✓ | - | - | - |
| cocotb XML | `cocotb-xml` | ✓ | ✓ | ✓ | - | - | - |
| AVL JSON | `avl-json` | ✓ | ✓ | ✓ | - | - | - |
| Verilator | `vltcov` | ✓ | ✓ | - | ✓ | ✓ | - |

**Conversion CLI:**

```bash
# Convert with warnings on unsupported constructs (default)
pyucis convert --input-format xml --output-format yaml input.xml -o output.yaml

# Strict mode: fail on any unsupported construct
pyucis convert --input-format xml --output-format lcov --strict input.xml -o output.lcov

# Show a summary of warnings after conversion
pyucis convert --input-format xml --output-format cocotb-yaml --warn-summary input.xml -o out.yml
```

## NCDB — Native Coverage Database Format

NCDB (`.cdb`) is a compact binary format for UCIS coverage data, implemented as a ZIP archive. It achieves **~60–73× size reduction** over SQLite by using schema-aware V2 encoding: LEB128 varints, toggle-pair compression, presence bitfields, and type-level defaults.

### NCDB CLI Examples

```bash
# Convert SQLite → NCDB
pyucis convert --input-format sqlite --output-format ncdb input.cdb -o compact.cdb

# Convert NCDB → SQLite (for tool interop)
pyucis convert --input-format ncdb --output-format sqlite compact.cdb -o output.cdb

# Merge NCDB files (fast same-schema path avoids re-decoding the scope tree)
pyucis merge --input-format ncdb --output-format ncdb run1.cdb run2.cdb -o merged.cdb

# Auto-detect format (.cdb files are identified by header bytes)
pyucis show summary coverage.cdb
```

### NCDB Python API

```python
from ucis.ncdb.ncdb_writer import NcdbWriter
from ucis.ncdb.ncdb_reader import NcdbReader

# Write any UCIS database as NCDB
NcdbWriter().write(db, "coverage.cdb")

# Read back as an in-memory UCIS database
db = NcdbReader().read("coverage.cdb")

# Merge NCDB files
from ucis.ncdb.ncdb_merger import NcdbMerger
NcdbMerger().merge(["run1.cdb", "run2.cdb"], "merged.cdb")
```

### NCDB ZIP Archive Members

| Member | Contents |
|--------|----------|
| `manifest.json` | Format version, schema hash (for fast-path merge) |
| `scope_tree.bin` | V2-encoded scope hierarchy |
| `counts.bin` | Coverage hit counts (LEB128 varint or uint32 array) |
| `strings.bin` | Deduplicated string table |
| `history.json` | Test/merge history nodes |
| `sources.json` | Source file references |

## Documentation

- [MCP Server Documentation](MCP_SERVER.md)
- [Python SQLite Performance Report](PYTHON_SQLITE_PERFORMANCE_REPORT.md)
- [UCIS Standard](https://www.accellera.org/activities/committees/ucis)

## License

Apache 2.0

## Links

- [PyPI](https://pypi.org/project/pyucis/)
- [GitHub](https://github.com/fvutils/pyucis)
- [Issue Tracker](https://github.com/fvutils/pyucis/issues)
