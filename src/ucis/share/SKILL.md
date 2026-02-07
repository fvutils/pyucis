---
name: pyucis
description: Python API and tools for working with UCIS (Unified Coverage Interoperability Standard) coverage databases. Use when working with hardware verification coverage data, converting coverage formats, merging coverage databases, generating coverage reports, or analyzing functional and code coverage metrics.
license: Apache-2.0
metadata:
  author: fvutils
  version: "1.0"
  repository: https://github.com/fvutils/pyucis
compatibility: Requires Python 3.x. Network access optional for remote database operations.
---

# PyUCIS - Coverage Database Manipulation

PyUCIS provides a comprehensive Python API and command-line tools for working with UCIS (Unified Coverage Interoperability Standard) coverage databases. This skill enables agents to effectively manage, analyze, and report on hardware verification coverage data.

## When to Use This Skill

Use PyUCIS when you need to:
- Convert coverage databases between formats (XML, YAML, UCIS binary)
- Merge multiple coverage databases from different test runs
- Generate coverage reports in various formats (text, JSON, LCOV, Cobertura, JaCoCo, Clover)
- Analyze functional coverage (covergroups, coverpoints, bins)
- Query code coverage metrics (line, branch, toggle, assertion)
- Compare coverage between test runs
- Identify coverage gaps and hotspots
- Export coverage data for CI/CD pipelines

## Installation

```bash
# Standard installation
pip install pyucis

# With MCP server support for AI agents
pip install pyucis[dev]
```

## Command Line Usage

### Database Conversion

Convert coverage data between different formats:

```bash
# XML to YAML
pyucis convert --input-format xml --output-format yaml coverage.xml -o coverage.yaml

# YAML to XML
pyucis convert --input-format yaml --output-format xml coverage.yaml -o coverage.xml

# Auto-detect input format
pyucis convert coverage.xml -o coverage.yaml
```

### Database Merging

Merge multiple coverage databases:

```bash
# Merge databases
pyucis merge test1.xml test2.xml test3.xml -o merged.xml

# Merge with format specification
pyucis merge --input-format xml --output-format yaml test*.xml -o merged.yaml

# Merge using native UCIS library (if available)
pyucis merge -l libucis.so db1.xml db2.xml -o merged.xml
```

### Coverage Reporting

Generate various types of reports:

```bash
# Basic text report
pyucis report coverage.xml -o report.txt

# Specify output format
pyucis report --output-format txt coverage.xml -o report.txt
```

### Coverage Queries

Query specific coverage information:

```bash
# Show overall summary
pyucis show summary coverage.xml

# Find coverage gaps (items below threshold)
pyucis show gaps coverage.xml --threshold 80

# Display covergroup details
pyucis show covergroups coverage.xml --include-bins

# Show bin-level details
pyucis show bins coverage.xml --covergroup my_cg --min-hits 0

# View test information
pyucis show tests coverage.xml

# Display design hierarchy
pyucis show hierarchy coverage.xml --max-depth 3

# Show coverage metrics
pyucis show metrics coverage.xml

# Compare two databases
pyucis show compare baseline.xml current.xml

# Find coverage hotspots
pyucis show hotspots coverage.xml --threshold 80 --limit 10

# Export code coverage in standard formats
pyucis show code-coverage coverage.xml --output-format lcov -o coverage.info
pyucis show code-coverage coverage.xml --output-format cobertura -o coverage.xml
pyucis show code-coverage coverage.xml --output-format jacoco

# View assertion coverage
pyucis show assertions coverage.xml

# View toggle coverage
pyucis show toggle coverage.xml
```

## Python API

### Basic Database Operations

```python
from ucis import UCIS

# Open a database
db = UCIS("coverage.xml")

# Access scopes (design hierarchy)
for scope in db.scopes():
    print(f"Scope: {scope.name}, Type: {scope.type}")
    
    # Access cover items within a scope
    for item in scope.coveritems():
        print(f"  Item: {item.name}, Hits: {item.count}")

# Create a new database
new_db = UCIS()
new_db.create_scope("top", scope_type=UCIS.SCOPE_INSTANCE)

# Write database
new_db.write("output.xml", format="xml")
```

### Working with Covergroups

```python
from ucis import UCIS

db = UCIS("coverage.xml")

# Find covergroups
for scope in db.scopes():
    if scope.type == UCIS.SCOPE_COVERGROUP:
        print(f"Covergroup: {scope.name}")
        
        # Access coverpoints
        for cp_scope in scope.scopes():
            if cp_scope.type == UCIS.SCOPE_COVERPOINT:
                print(f"  Coverpoint: {cp_scope.name}")
                
                # Access bins
                for bin_item in cp_scope.coveritems():
                    print(f"    Bin: {bin_item.name}, Count: {bin_item.count}")
```

### Coverage Metrics

```python
from ucis import UCIS

db = UCIS("coverage.xml")

# Calculate overall coverage
total_bins = 0
covered_bins = 0

for scope in db.scopes():
    for item in scope.coveritems():
        total_bins += 1
        if item.count > 0:
            covered_bins += 1

coverage_pct = (covered_bins / total_bins * 100) if total_bins > 0 else 0
print(f"Overall Coverage: {coverage_pct:.2f}%")
```

## MCP Server Integration

PyUCIS includes a Model Context Protocol (MCP) server that enables AI agents to interact with coverage databases:

```bash
# Start the MCP server
pyucis-mcp-server

# Or with custom port
pyucis-mcp-server --port 8080
```

The MCP server provides 17+ specialized tools for coverage analysis. See `MCP_SERVER.md` for detailed documentation.

## Coverage Data Model

### Scope Types
- **INSTANCE**: Design instance in hierarchy
- **COVERGROUP**: Functional coverage group
- **COVERPOINT**: Individual coverage point
- **CROSS**: Cross coverage between coverpoints
- **FUNCTION**: Function coverage
- **BLOCK**: Code block coverage
- **BRANCH**: Branch coverage
- **TOGGLE**: Signal toggle coverage
- **FSM**: FSM state/transition coverage

### Coverage Item Types
- **BIN**: Coverpoint bin with hit count
- **LINE**: Source line coverage
- **BRANCH**: Branch coverage point
- **TOGGLE**: Signal toggle (0->1, 1->0)
- **ASSERTION**: Assertion coverage
- **STATEMENT**: Statement coverage

## Supported File Formats

### Input Formats
- **XML**: UCIS XML format (default)
- **YAML**: UCIS YAML format
- **UCDB**: Binary UCIS database (requires libucis)

### Export Formats
- **XML**: Standard UCIS XML
- **YAML**: UCIS YAML
- **JSON**: Structured JSON output
- **LCOV**: LCOV format for code coverage
- **Cobertura**: Cobertura XML format
- **JaCoCo**: JaCoCo XML format
- **Clover**: Clover XML format

## Common Workflows

### CI/CD Integration

```bash
# Merge coverage from parallel test runs
pyucis merge test_run_*.xml -o merged_coverage.xml

# Generate LCOV report for visualization
pyucis show code-coverage merged_coverage.xml --output-format lcov -o coverage.info

# Check coverage threshold
pyucis show metrics merged_coverage.xml --output-format json | jq '.coverage_percent'
```

### Coverage Analysis

```bash
# Find all uncovered items
pyucis show gaps coverage.xml --threshold 0

# Identify high-value coverage targets
pyucis show hotspots coverage.xml --threshold 90 --limit 20

# Compare coverage progress
pyucis show compare yesterday.xml today.xml
```

### Format Conversion

```bash
# Convert for different tools
pyucis convert legacy.xml -o modern.yaml
pyucis show code-coverage coverage.xml --output-format cobertura -o cobertura.xml
```

## Error Handling

Common errors and solutions:

1. **File not found**: Ensure the coverage database path is correct
2. **Format errors**: Specify `--input-format` explicitly if auto-detection fails
3. **Merge conflicts**: Use `--libucis` option if merging complex databases
4. **Memory issues**: Process large databases in chunks or use YAML format

## Advanced Features

### Custom Filtering

Use plusargs to pass tool-specific options:

```bash
pyucis report coverage.xml +filter=uncovered +detail=high
```

### Programmatic Database Creation

```python
from ucis import UCIS, CoverGroup, CoverPoint, Bin

db = UCIS()
top = db.create_scope("top", UCIS.SCOPE_INSTANCE)

# Create covergroup
cg = CoverGroup("my_covergroup")
top.add_child(cg)

# Add coverpoint with bins
cp = CoverPoint("my_coverpoint")
cg.add_child(cp)

cp.add_bin("low", 100)   # bin with 100 hits
cp.add_bin("mid", 50)    # bin with 50 hits
cp.add_bin("high", 0)    # uncovered bin

db.write("new_coverage.xml")
```

## Best Practices

1. **Use YAML for readability**: YAML format is easier to inspect and version control
2. **Merge regularly**: Combine coverage from parallel runs to get complete picture
3. **Set coverage goals**: Use `--threshold` options to enforce coverage requirements
4. **Export for tools**: Convert to LCOV/Cobertura for integration with CI/CD dashboards
5. **Track trends**: Use `show compare` to monitor coverage progress over time

## Resources

- Full documentation: See `MCP_SERVER.md` for MCP server details
- UCIS standard: https://www.accellera.org/activities/committees/ucis
- PyPI package: https://pypi.org/project/pyucis/
- GitHub repository: https://github.com/fvutils/pyucis
- Issue tracker: https://github.com/fvutils/pyucis/issues

## Getting Help

To see available command options:

```bash
pyucis --help
pyucis convert --help
pyucis merge --help
pyucis report --help
pyucis show --help
pyucis show summary --help
```

For listing supported formats:

```bash
pyucis list-db-formats
pyucis list-rpt-formats
```
