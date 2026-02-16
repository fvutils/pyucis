# AI-Assisted Coverage Analysis Workflow

Learn how AI agents can effectively analyze hardware verification coverage databases using PyUCIS.

## Overview

This example demonstrates how AI agents (like LLMs) can work with coverage data to:
- Understand coverage status and metrics
- Identify testing gaps and redundancies  
- Optimize test suites
- Generate reports for CI/CD
- Make data-driven testing decisions

The examples use real coverage data from a Verilator simulation of a SystemVerilog counter module with 5 test runs.

## Quick Start

### 1. Validate Setup

```bash
cd examples/ai_assisted_workflow
./validate_ai_examples.sh
```

This verifies:
- ✅ PyUCIS is accessible
- ✅ Coverage database exists
- ✅ All commands work correctly
- ✅ Export formats are functional

### 2. Explore the Documentation

Start with the navigation index:

```bash
cat AI_INDEX.md
```

Or jump directly to:
- **[AI_INDEX.md](AI_INDEX.md)** - Navigation hub (start here!)
- **[QUICK_START_AI.md](QUICK_START_AI.md)** - Command reference
- **[AI_ASSISTED_WORKFLOW.md](AI_ASSISTED_WORKFLOW.md)** - 13 detailed scenarios

### 3. Try a Basic Command

```bash
export PYTHONPATH=../../src
python3 -m ucis show summary coverage/merged.cdb --output-format text
```

## What's Included

### Documentation

| File | Purpose | Audience |
|------|---------|----------|
| **[AI_INDEX.md](AI_INDEX.md)** | Navigation hub with quick links | Everyone |
| **[QUICK_START_AI.md](QUICK_START_AI.md)** | Command reference and cheat sheet | AI agents |
| **[AI_ASSISTED_WORKFLOW.md](AI_ASSISTED_WORKFLOW.md)** | 13 detailed scenarios with prompts | AI agents & developers |
| **[AI_EXAMPLES_SUMMARY.md](AI_EXAMPLES_SUMMARY.md)** | Package statistics and details | Developers |
| **[validate_ai_examples.sh](validate_ai_examples.sh)** | Automated validation script | Everyone |

### Example Data

- **coverage/merged.cdb** - SQLite database with coverage from 5 tests (372KB)
  - counter_tb (39 coverage items, 9 unique)
  - test_basic_counting (36 items)
  - test_load_operations (39 items)
  - test_overflow (48 items, 8 unique)
  - test_reset (39 items, 2 unique)
  
- **query_test_coverage.py** - Python script demonstrating PyUCIS API usage

*Note: Coverage data and scripts are shared with the verilator example via symlinks.*

## 13 Learning Scenarios

Each scenario provides:
- **Problem Statement** - Real verification challenge
- **AI Agent Prompt** - Exact prompt to use
- **Expected Results** - What the AI should do
- **Validation** - Commands to verify correctness

### Basic Scenarios (Scenarios 1-3)
- Initial coverage assessment
- Test contribution analysis
- Coverage gap identification

### Intermediate Scenarios (Scenarios 4-8)
- Test suite optimization
- Before/after comparisons
- Hierarchy navigation
- CI/CD integration
- Advanced filtering

### Advanced Scenarios (Scenarios 9-13)
- Assertion and toggle coverage
- Statistical analysis
- Custom Python scripts
- Regression detection
- AI-driven test planning

See [AI_ASSISTED_WORKFLOW.md](AI_ASSISTED_WORKFLOW.md) for complete details.

## Commands Covered

### Query Commands
```bash
# Overall status
python3 -m ucis show summary coverage/merged.cdb

# List tests
python3 -m ucis show tests coverage/merged.cdb

# Design hierarchy
python3 -m ucis show hierarchy coverage/merged.cdb --max-depth 3

# Find gaps
python3 -m ucis show gaps coverage/merged.cdb --threshold 80

# Identify priorities
python3 -m ucis show hotspots coverage/merged.cdb --limit 10
```

### Analysis Commands
```bash
# Detailed metrics
python3 -m ucis show metrics coverage/merged.cdb

# Code coverage
python3 -m ucis show code-coverage coverage/merged.cdb

# Assertions
python3 -m ucis show assertions coverage/merged.cdb

# Toggle coverage
python3 -m ucis show toggle coverage/merged.cdb

# Test contributions
python3 query_test_coverage.py
```

### Export Commands
```bash
# LCOV format
python3 -m ucis show code-coverage coverage/merged.cdb --output-format lcov -o coverage.lcov

# Cobertura XML
python3 -m ucis show code-coverage coverage/merged.cdb --output-format cobertura -o coverage.xml

# JSON for processing
python3 -m ucis show summary coverage/merged.cdb --output-format json > summary.json
```

### Interactive TUI
```bash
python3 -m ucis view coverage/merged.cdb
```

## For AI Agents

### Decision Tree

When analyzing coverage, choose commands based on the task:

```
User Request
├─ "What's the coverage status?"
│  └─ show summary + show tests
│
├─ "What needs more testing?"
│  └─ show gaps --threshold 80 + show hotspots
│
├─ "Which tests can I remove?"
│  └─ query_test_coverage.py (test contributions)
│
├─ "Export for CI/CD"
│  └─ show code-coverage --output-format [lcov|cobertura]
│
└─ "Compare two runs"
   └─ show compare baseline.cdb current.cdb
```

### Best Practices

1. **Always set PYTHONPATH** when running commands:
   ```bash
   export PYTHONPATH=../../src
   ```

2. **Check file existence** before running:
   ```bash
   [ -f coverage/merged.cdb ] && echo "OK" || echo "Run validation first"
   ```

3. **Use JSON output** for programmatic processing:
   ```bash
   python3 -m ucis show summary coverage/merged.cdb --output-format json | python3 -m json.tool
   ```

4. **Chain commands** for efficiency:
   ```bash
   python3 -m ucis show summary coverage/merged.cdb --output-format text && \
   python3 -m ucis show gaps coverage/merged.cdb --threshold 80 --output-format text
   ```

5. **Reference the SKILL file** for full capabilities:
   ```
   ../../src/ucis/share/SKILL.md
   ```

## Example AI Interaction

```
USER: "Analyze the coverage and suggest test improvements"

AI AGENT:
1. Validates setup (checks database exists)
2. Gets overview:
   → python3 -m ucis show summary coverage/merged.cdb
   → python3 -m ucis show tests coverage/merged.cdb
   → Result: 5 tests, ~6,000 coverage items

3. Analyzes contributions:
   → python3 query_test_coverage.py
   → Finds: counter_tb (9 unique), test_basic_counting (0 unique)

4. Identifies gaps:
   → python3 -m ucis show gaps coverage/merged.cdb --threshold 80
   → python3 -m ucis show hotspots coverage/merged.cdb --limit 5

5. Provides recommendations:
   ✓ Remove test_basic_counting and test_load_operations (no unique coverage)
   ✓ Keep counter_tb, test_overflow, test_reset
   ✓ Focus new tests on identified gaps
   ✓ Achieves same coverage with 40% fewer tests
```

## Learning Path

### Beginner (30 minutes)
1. Run `./validate_ai_examples.sh`
2. Read [QUICK_START_AI.md](QUICK_START_AI.md)
3. Try scenarios 1-3 from [AI_ASSISTED_WORKFLOW.md](AI_ASSISTED_WORKFLOW.md)

### Intermediate (1-2 hours)
4. Complete scenarios 4-8
5. Experiment with output formats (text, JSON, LCOV)
6. Parse JSON output with Python

### Advanced (2-4 hours)
7. Master scenarios 9-13
8. Write custom analysis scripts using PyUCIS API
9. Integrate with CI/CD pipelines

## Integration with CI/CD

### GitLab CI Example

```yaml
coverage_analysis:
  script:
    - cd examples/ai_assisted_workflow
    - export PYTHONPATH=../../src
    - python3 -m ucis show code-coverage coverage/merged.cdb --output-format cobertura -o coverage.xml
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: examples/ai_assisted_workflow/coverage.xml
```

### GitHub Actions Example

```yaml
- name: Analyze Coverage
  run: |
    cd examples/ai_assisted_workflow
    export PYTHONPATH=../../src
    python3 -m ucis show summary coverage/merged.cdb --output-format json > coverage_summary.json
    
- name: Export LCOV
  run: |
    cd examples/ai_assisted_workflow
    export PYTHONPATH=../../src
    python3 -m ucis show code-coverage coverage/merged.cdb --output-format lcov -o coverage.lcov
```

## Troubleshooting

### "No module named pyucis"
```bash
export PYTHONPATH=$(pwd)/../../src
# OR
pip install -e ../..
```

### "Database not found"
```bash
# Ensure symlinks are working
ls -l coverage/merged.cdb
# If broken, recreate them:
ln -sf ../verilator/coverage .
```

### "Command failed"
```bash
# Verify PyUCIS can be imported
python3 -c "import sys; sys.path.insert(0, '../../src'); import ucis; print('OK')"

# Check database integrity
file coverage/merged.cdb  # Should show: SQLite 3.x database
```

### "Empty results"
```bash
# The coverage data might not have functional coverage (covergroups)
# This is normal for Verilator line/branch/toggle coverage
# Use code-coverage commands instead:
python3 -m ucis show code-coverage coverage/merged.cdb --output-format text
```

## Data Source

The coverage data comes from the **verilator example** (`../verilator`), which includes:

- **counter.sv** - Parametric counter module with assertions
- **counter_tb.sv** - Comprehensive testbench
- **Additional tests** - Targeted scenarios (basic counting, load, overflow, reset)

The verilator example demonstrates:
- Line, branch, and toggle coverage collection
- Verilator integration with PyUCIS
- Multiple test runs merged into single database

See [../verilator/README.md](../verilator/README.md) for details on the design and verification.

## File Structure

```
ai_assisted_workflow/
├── README.md                      # This file
├── AI_INDEX.md                    # Navigation hub
├── QUICK_START_AI.md              # Command reference
├── AI_ASSISTED_WORKFLOW.md        # 13 detailed scenarios
├── AI_EXAMPLES_SUMMARY.md         # Package statistics
├── AI_EXAMPLES_COMPLETE.md        # Completion summary
├── validate_ai_examples.sh        # Validation script
├── coverage/                      # → ../verilator/coverage/
│   ├── merged.cdb                 # Merged coverage database (372KB)
│   ├── counter_tb.cdb             # Individual test databases
│   ├── test_basic_counting.cdb
│   ├── test_load_operations.cdb
│   ├── test_overflow.cdb
│   └── test_reset.cdb
└── query_test_coverage.py         # → ../verilator/query_test_coverage.py
```

*Symlinks (→) point to the verilator example for shared data.*

## Success Criteria

An AI agent demonstrates proficiency when it can:

- ✅ Choose appropriate commands for different tasks
- ✅ Use correct syntax and options
- ✅ Interpret results accurately
- ✅ Provide actionable insights and recommendations
- ✅ Handle errors gracefully with fallbacks
- ✅ Suggest logical next steps based on findings

## Additional Resources

### Within This Repository
- **[PyUCIS SKILL.md](../../src/ucis/share/SKILL.md)** - Full capabilities reference for AI agents
- **[Verilator Example](../verilator/README.md)** - Source of coverage data
- **[Main README](../../README.md)** - PyUCIS overview

### External Resources
- **[UCIS Standard](https://www.accellera.org/activities/committees/ucis)** - Coverage interoperability standard
- **[Verilator Documentation](https://verilator.org/guide/latest/)** - Verilog simulator
- **[PyUCIS GitHub](https://github.com/fvutils/pyucis)** - Repository and issues

## Contributing

Found a useful coverage analysis pattern? Add it to [AI_ASSISTED_WORKFLOW.md](AI_ASSISTED_WORKFLOW.md):

```markdown
### Scenario XX: Your Scenario Name

**Problem:** What verification challenge does this address?

**Prompt:** "Exact prompt for the AI agent"

**Expected:** What the AI should do and report

**Validation:** Commands to verify the solution
```

## License

Apache License 2.0 - See LICENSE file in repository root

## Support

- **Questions:** Check [AI_INDEX.md](AI_INDEX.md) FAQ
- **Issues:** https://github.com/fvutils/pyucis/issues
- **Discussions:** GitHub discussions for questions and ideas

---

**Ready to start?** Run `./validate_ai_examples.sh` then open [AI_INDEX.md](AI_INDEX.md)!
