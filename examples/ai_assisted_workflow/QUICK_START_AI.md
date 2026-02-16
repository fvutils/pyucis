# Quick Start: AI-Assisted Coverage Analysis

A condensed guide for AI agents working with PyUCIS coverage databases.

## Setup (One-time)

```bash
cd examples/ai_assisted_workflow
# Coverage data is already available (symlinked from verilator example)
export PYTHONPATH=../../src
# Validate everything works:
./validate_ai_examples.sh
```

## Core Commands Cheat Sheet

### Basic Information
```bash
# Overall summary
python3 -m ucis show summary coverage/merged.cdb --output-format text

# List all tests
python3 -m ucis show tests coverage/merged.cdb --output-format json

# Design hierarchy
python3 -m ucis show hierarchy coverage/merged.cdb --max-depth 3
```

### Coverage Analysis
```bash
# Code coverage details
python3 -m ucis show code-coverage coverage/merged.cdb --output-format text

# Find gaps below threshold
python3 -m ucis show gaps coverage/merged.cdb --threshold 80

# Identify priority targets
python3 -m ucis show hotspots coverage/merged.cdb --limit 10

# Detailed metrics
python3 -m ucis show metrics coverage/merged.cdb --output-format json
```

### Specialized Coverage Types
```bash
# Assertion coverage
python3 -m ucis show assertions coverage/merged.cdb --output-format text

# Toggle coverage
python3 -m ucis show toggle coverage/merged.cdb --output-format text

# Covergroup and bin details
python3 -m ucis show covergroups coverage/merged.cdb --include-bins
python3 -m ucis show bins coverage/merged.cdb --sort count
```

### Export Formats
```bash
# LCOV for CI/CD
python3 -m ucis show code-coverage coverage/merged.cdb --output-format lcov -o coverage.lcov

# Cobertura XML for Jenkins
python3 -m ucis show code-coverage coverage/merged.cdb --output-format cobertura -o coverage.xml

# JSON for custom processing
python3 -m ucis show summary coverage/merged.cdb --output-format json > summary.json
```

### Advanced Queries
```bash
# Test contribution analysis
python3 query_test_coverage.py

# Compare two databases
python3 -m ucis show compare coverage/test1.cdb coverage/test2.cdb --output-format text

# Interactive TUI
python3 -m ucis view coverage/merged.cdb
```

## Common AI Agent Tasks

### Task 1: "What's the coverage status?"
```bash
python3 -m ucis show summary coverage/merged.cdb --output-format text
python3 -m ucis show tests coverage/merged.cdb --output-format text
```

### Task 2: "Find what needs more testing"
```bash
python3 -m ucis show gaps coverage/merged.cdb --threshold 80
python3 -m ucis show hotspots coverage/merged.cdb --limit 5
```

### Task 3: "Which tests are most valuable?"
```bash
python3 query_test_coverage.py | grep -A 10 "TEST CONTRIBUTION"
```

### Task 4: "Export for CI/CD"
```bash
python3 -m ucis show code-coverage coverage/merged.cdb --output-format cobertura -o coverage.xml
```

### Task 5: "Compare before/after changes"
```bash
python3 -m ucis show compare coverage/baseline.cdb coverage/current.cdb --output-format json
```

## Quick Validation

Verify commands work:
```bash
cd examples/ai_assisted_workflow && export PYTHONPATH=../../src
python3 -c "import ucis; print('✓ PyUCIS available')"
ls -lh coverage/merged.cdb  # Should exist (~372K)
python3 -m ucis show summary coverage/merged.cdb --output-format text | head -20
```

## AI Agent Decision Tree

```
Need to analyze coverage?
├─ Basic overview → use "show summary" + "show tests"
├─ Find problems → use "show gaps" + "show hotspots"  
├─ Test optimization → use query_test_coverage.py
├─ Compare versions → use "show compare"
├─ Export to tools → use "show code-coverage --output-format lcov/cobertura"
├─ Deep dive → use "show hierarchy" + "show bins" + custom scripts
└─ Interactive exploration → use "view" (TUI)
```

## Error Handling

**"No module named pyucis"**
```bash
export PYTHONPATH=/path/to/pyucis/src
# OR
pip install -e /path/to/pyucis
```

**"Database not found"**
```bash
cd examples/verilator && make merge
```

**"Format not recognized"**
```bash
# Add --input-format sqlite for .cdb files
python3 -m ucis show summary --input-format sqlite coverage/merged.cdb
```

## Output Format Options

All `show` commands support:
- `--output-format text` - Human readable
- `--output-format json` - Machine parseable
- `--output-format txt` - Formatted text

Some commands also support:
- `--output-format lcov` - For LCOV tools
- `--output-format cobertura` - For Cobertura XML
- `--output-format jacoco` - For JaCoCo
- `--output-format clover` - For Clover

## Pro Tips for AI Agents

1. **Always set PYTHONPATH** when in examples/verilator
2. **Use JSON output** when you need to parse results programmatically
3. **Check file exists** before running commands: `[ -f coverage/merged.cdb ] && echo OK`
4. **Chain commands** for efficiency: `cmd1 && cmd2 && cmd3`
5. **Start simple** then drill down: summary → gaps → specific bins
6. **Use query_test_coverage.py** for test contribution analysis
7. **Reference SKILL.md** at src/ucis/share/SKILL.md for API details

## Example AI Agent Workflow

```bash
#!/bin/bash
# Full coverage analysis workflow

cd examples/verilator
export PYTHONPATH=../../src

# 1. Get overview
echo "=== Coverage Summary ==="
python3 -m ucis show summary coverage/merged.cdb --output-format text

# 2. Analyze test contributions
echo -e "\n=== Test Contributions ==="
python3 query_test_coverage.py | grep -A 15 "TEST CONTRIBUTION"

# 3. Find gaps
echo -e "\n=== Coverage Gaps (< 80%) ==="
python3 -m ucis show gaps coverage/merged.cdb --threshold 80 --output-format text | head -30

# 4. Identify hotspots
echo -e "\n=== Priority Targets ==="
python3 -m ucis show hotspots coverage/merged.cdb --limit 5 --output-format text

# 5. Export for CI
python3 -m ucis show code-coverage coverage/merged.cdb --output-format cobertura -o coverage.xml
echo "✓ Exported to coverage.xml"
```

## Interactive Exploration

Launch the TUI for visual exploration:
```bash
python3 -m ucis view coverage/merged.cdb
```

Navigation:
- `1` - Dashboard (overview)
- `2` - Hierarchy (design structure)
- `3` - Gaps (uncovered items)
- `4` - Hotspots (priorities)
- `5` - Metrics (statistics)
- `6` - Code Coverage (files)
- `7` - Test History (contributions)
- `?` - Help
- `q` - Quit

## See Also

- **Full Workflow Guide:** AI_ASSISTED_WORKFLOW.md (detailed scenarios)
- **This Example:** README.md (overview and setup)
- **Verilator Example:** ../verilator/README.md (source data details)
- **PyUCIS Skills:** ../../src/ucis/share/SKILL.md (API reference)
- **Query Example:** query_test_coverage.py (test analysis script)
