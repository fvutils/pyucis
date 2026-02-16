# AI-Assisted Coverage Analysis Workflow

This document provides a structured set of coverage analysis scenarios that can be followed with an AI agent. Each scenario includes a problem statement, recommended prompt, and expected results.

## Prerequisites

Before starting, ensure you have:
1. The coverage database at `coverage/merged.cdb` (symlinked from verilator example)
2. PyUCIS installed and accessible
3. Run `./validate_ai_examples.sh` to verify setup

## Overview

The verilator example contains coverage data from 5 test runs:
- **counter_tb** - Main testbench with comprehensive scenarios
- **test_basic_counting** - Basic increment operations
- **test_load_operations** - Load value functionality
- **test_overflow** - Overflow condition testing
- **test_reset** - Reset behavior verification

The merged database contains:
- ~6,000 coverage items total (lines, branches, toggles)
- Test contribution tracking showing which tests hit which coverage points
- Full source file tracking with line numbers

---

## Scenario 1: Initial Coverage Assessment

### Problem Statement
You've just received a coverage database from your verification team. You need to understand the overall coverage status before deciding where to focus testing efforts.

### AI Agent Prompt
```
I have a coverage database at examples/ai_assisted_workflow/coverage/merged.cdb. 
Please give me a high-level summary of the coverage status including:
- Overall coverage percentage
- Number of tests included
- Coverage breakdown by type (line, branch, toggle)
- Key statistics

Use the pyucis show commands to extract this information.
```

### Expected Results
The AI agent should:
1. Use `pyucis show summary coverage/merged.cdb --output-format text` to get overall statistics
2. Use `pyucis show tests coverage/merged.cdb --output-format text` to list tests
3. Use `pyucis show code-coverage coverage/merged.cdb --output-format text` for detailed metrics
4. Report findings including:
   - 5 tests in the database
   - Coverage percentages for each type
   - Total number of coverage items

### Validation
Check the AI agent's commands:
```bash
cd examples/ai_assisted_workflow
PYTHONPATH=../../src python3 -m ucis show summary coverage/merged.cdb --output-format text
PYTHONPATH=../../src python3 -m ucis show tests coverage/merged.cdb --output-format text
```

---

## Scenario 2: Identifying Test Contributions

### Problem Statement
Your verification suite has grown to 5 tests, but you suspect there's redundancy. You need to understand which tests provide unique coverage and which might be redundant.

### AI Agent Prompt
```
Analyze the test contributions in examples/ai_assisted_workflow/coverage/merged.cdb. 
For each test, tell me:
- How many coverage items it hits
- How many are unique to that test
- Which test provides the most unique coverage
- Are there any tests that add no unique coverage?

Use the query_test_coverage.py script or write a similar analysis.
```

### Expected Results
The AI agent should:
1. Run `python3 query_test_coverage.py` or write equivalent code
2. Report test contribution analysis:
   - counter_tb: ~39 items, 9 unique (most unique)
   - test_overflow: ~48 items, 8 unique
   - test_reset: ~39 items, 2 unique
   - test_basic_counting: ~36 items, 0 unique
   - test_load_operations: ~39 items, 0 unique
3. Identify that test_basic_counting and test_load_operations add no unique coverage
4. Suggest these might be candidates for removal or refactoring

### Validation
```bash
cd examples/verilator
PYTHONPATH=../../src python3 query_test_coverage.py | grep -A 10 "TEST CONTRIBUTION"
```

---

## Scenario 3: Coverage Gap Analysis

### Problem Statement
Management wants 90% coverage, but you're not sure how far away you are or what areas need attention.

### AI Agent Prompt
```
Find coverage gaps in examples/ai_assisted_workflow/coverage/merged.cdb. Show me:
- Coverage items below 80% threshold
- Specific files or modules with low coverage
- Types of coverage that are lacking (line vs branch vs toggle)
- Prioritized list of what to test next

Use pyucis show gaps and other analysis commands.
```

### Expected Results
The AI agent should:
1. Use `pyucis show gaps coverage/merged.cdb --threshold 80 --output-format text`
2. Use `pyucis show hotspots coverage/merged.cdb --output-format text` to find priority areas
3. Analyze the output and report:
   - Specific uncovered or low-coverage items
   - Which coverage types have gaps
   - Suggested priorities based on coverage density
4. Provide actionable recommendations

### Validation
```bash
cd examples/verilator
PYTHONPATH=../../src python3 -m ucis show gaps coverage/merged.cdb --threshold 80 --output-format json | head -50
PYTHONPATH=../../src python3 -m ucis show hotspots coverage/merged.cdb --output-format text
```

---

## Scenario 4: Test Set Optimization

### Problem Statement
Your regression suite takes too long to run. You want to find the minimum set of tests that still achieves 80% coverage.

### AI Agent Prompt
```
Optimize the test suite in examples/ai_assisted_workflow/coverage/merged.cdb. 
Find the minimum set of tests needed to achieve 80% coverage.
Show me:
- Which tests to keep
- What coverage percentage is achieved
- How many tests can be removed
- The coverage timeline (what each test adds)

Use the test coverage API or query_test_coverage.py script.
```

### Expected Results
The AI agent should:
1. Run the optimization section of query_test_coverage.py
2. Use the greedy algorithm to select minimum tests
3. Report:
   - Selected test set (likely counter_tb and test_overflow due to unique coverage)
   - Coverage percentage achieved
   - Number of tests that can be removed (probably 3)
   - Timeline showing cumulative coverage as tests are added
4. Explain the greedy selection process

### Validation
```bash
cd examples/verilator
PYTHONPATH=../../src python3 query_test_coverage.py | grep -A 15 "OPTIMIZED TEST SET"
```

---

## Scenario 5: Comparing Test Runs

### Problem Statement
You've modified test_overflow to add more corner cases. You need to compare the new coverage against the original to see if your changes were effective.

### AI Agent Prompt
```
I have two coverage databases:
- Baseline: examples/verilator/coverage/test_basic_counting.cdb
- New version: examples/verilator/coverage/test_overflow.cdb

Compare these and tell me:
- What new coverage was added?
- Was any coverage lost?
- Overall coverage delta (percentage change)
- Specific coverage items that differ

Use pyucis show compare or write a comparison script.
```

### Expected Results
The AI agent should:
1. Use `pyucis show compare` command or write comparison code
2. Report coverage deltas:
   - Items in new but not baseline
   - Items in baseline but not new (regressions)
   - Net coverage change
3. Provide specific examples of coverage differences
4. Assess whether the changes were beneficial

### Validation
```bash
cd examples/verilator
PYTHONPATH=../../src python3 -m ucis show compare coverage/test_basic_counting.cdb coverage/test_overflow.cdb --output-format text
```

---

## Scenario 6: Coverage Hierarchy Navigation

### Problem Statement
Your database contains coverage for a complex hierarchical design. You need to understand the structure and drill down to specific modules.

### AI Agent Prompt
```
Show me the hierarchy of coverage in examples/ai_assisted_workflow/coverage/merged.cdb. 
Display:
- Top-level design structure
- Sub-modules and their coverage
- Drill down into the counter module specifically
- Coverage statistics at each level

Use pyucis show hierarchy with appropriate depth settings.
```

### Expected Results
The AI agent should:
1. Use `pyucis show hierarchy coverage/merged.cdb --output-format text`
2. Use `pyucis show hierarchy coverage/merged.cdb --max-depth 2` for limited depth
3. Report the hierarchical structure showing:
   - Root level scopes
   - Module hierarchy
   - Coverage at each level
4. Optionally write a script to drill into specific modules

### Validation
```bash
cd examples/verilator
PYTHONPATH=../../src python3 -m ucis show hierarchy coverage/merged.cdb --max-depth 3 --output-format text | head -100
```

---

## Scenario 7: Export for CI/CD Integration

### Problem Statement
Your CI/CD pipeline needs coverage data in LCOV format for integration with SonarQube and other tools.

### AI Agent Prompt
```
Export the coverage data from examples/ai_assisted_workflow/coverage/merged.cdb to LCOV format 
suitable for CI/CD tools. Also export to Cobertura XML for use with Jenkins.

Show me:
- Commands to export in both formats
- Verification that the exports worked
- File sizes and basic validation
- Example of how to use in a CI pipeline (GitLab or GitHub Actions)
```

### Expected Results
The AI agent should:
1. Use `pyucis show code-coverage coverage/merged.cdb --output-format lcov -o coverage.lcov`
2. Use `pyucis show code-coverage coverage/merged.cdb --output-format cobertura -o coverage.xml`
3. Verify the files were created and check their contents
4. Provide example CI configuration:
   ```yaml
   coverage:
     script:
       - make merge
       - pyucis show code-coverage coverage/merged.cdb --output-format cobertura -o coverage.xml
     artifacts:
       reports:
         coverage_report:
           coverage_format: cobertura
           path: coverage.xml
   ```

### Validation
```bash
cd examples/verilator
PYTHONPATH=../../src python3 -m ucis show code-coverage coverage/merged.cdb --output-format lcov -o /tmp/coverage.lcov
head -20 /tmp/coverage.lcov
PYTHONPATH=../../src python3 -m ucis show code-coverage coverage/merged.cdb --output-format cobertura -o /tmp/coverage.xml
head -20 /tmp/coverage.xml
```

---

## Scenario 8: Advanced Filtering and Querying

### Problem Statement
You need to find all coverage bins with specific characteristics for targeted testing.

### AI Agent Prompt
```
Query the coverage database at examples/ai_assisted_workflow/coverage/merged.cdb for:
1. All bins with exactly 0 hits (never exercised)
2. Bins with less than 10 hits (weak coverage)
3. Bins sorted by hit count to find outliers
4. Coverage items grouped by file

Use pyucis show bins with appropriate filters and sorting.
```

### Expected Results
The AI agent should:
1. Use `pyucis show bins coverage/merged.cdb --max-hits 0 --output-format text` for unhit bins
2. Use `pyucis show bins coverage/merged.cdb --max-hits 10 --sort count` for weak coverage
3. Use `pyucis show bins coverage/merged.cdb --sort count --output-format json` for sorted analysis
4. Write a custom script if needed to group by file
5. Report findings with specific examples and counts

### Validation
```bash
cd examples/verilator
PYTHONPATH=../../src python3 -m ucis show bins coverage/merged.cdb --max-hits 0 --output-format json | python3 -m json.tool | head -50
```

---

## Scenario 9: Assertion and Toggle Coverage Analysis

### Problem Statement
Beyond line coverage, you need to verify that assertions are firing and signals are toggling properly.

### AI Agent Prompt
```
Analyze assertion and toggle coverage in examples/ai_assisted_workflow/coverage/merged.cdb.
Report:
- Total number of assertions and their pass/fail status
- Toggle coverage for key signals
- Signals that never toggle (stuck values)
- Assertions that never fire

Use pyucis show assertions and pyucis show toggle commands.
```

### Expected Results
The AI agent should:
1. Use `pyucis show assertions coverage/merged.cdb --output-format text`
2. Use `pyucis show toggle coverage/merged.cdb --output-format text`
3. Analyze the data to find:
   - Assertion coverage percentages
   - Signals with 0->1 but not 1->0 transitions (or vice versa)
   - Completely static signals
   - Assertions that never triggered
4. Provide recommendations for additional testing

### Validation
```bash
cd examples/verilator
PYTHONPATH=../../src python3 -m ucis show assertions coverage/merged.cdb --output-format json | python3 -m json.tool
PYTHONPATH=../../src python3 -m ucis show toggle coverage/merged.cdb --output-format json | python3 -m json.tool | head -100
```

---

## Scenario 10: Coverage Metrics and Statistical Analysis

### Problem Statement
For a verification closure report, you need comprehensive coverage metrics and statistics.

### AI Agent Prompt
```
Generate a comprehensive coverage metrics report for examples/ai_assisted_workflow/coverage/merged.cdb.
Include:
- Overall statistics (mean, median, std dev of hit counts)
- Coverage distribution (histogram of coverage levels)
- Completeness metrics for each coverage type
- Trend analysis if multiple databases available
- Professional summary for management

Use pyucis show metrics and statistical analysis.
```

### Expected Results
The AI agent should:
1. Use `pyucis show metrics coverage/merged.cdb --output-format text`
2. Perform statistical analysis on coverage data:
   - Calculate mean/median hit counts
   - Show distribution of coverage percentages
   - Identify outliers
3. Generate a professional summary including:
   - Executive summary
   - Detailed metrics
   - Areas of concern
   - Recommendations
4. Optionally create visualizations (if matplotlib available)

### Validation
```bash
cd examples/verilator
PYTHONPATH=../../src python3 -m ucis show metrics coverage/merged.cdb --output-format json | python3 -m json.tool
```

---

## Advanced Scenarios

### Scenario 11: Custom Coverage Analysis Script

**Problem:** Standard commands don't provide the exact analysis you need.

**Prompt:** "Write a Python script using the PyUCIS API to analyze coverage/merged.cdb and find all coverage items that were hit by only one test. For each item, show which test hit it and how many times."

**Expected:** The AI should write a script using the SqliteUCIS API to query test associations and filter for unique hits.

---

### Scenario 12: Coverage Regression Detection

**Problem:** Detect if a new test run has decreased coverage compared to baseline.

**Prompt:** "Create a script that compares two coverage databases and alerts if coverage has regressed by more than 5% in any category. Output should be suitable for CI/CD gate checking."

**Expected:** Script that exits with non-zero if regression detected, includes detailed regression report.

---

### Scenario 13: Coverage-Driven Test Generation Guidance

**Problem:** Need to generate targeted tests for uncovered areas.

**Prompt:** "Analyze coverage gaps in merged.cdb and generate a prioritized test plan. For each gap, suggest what kind of test stimulus would hit that coverage point."

**Expected:** Intelligent analysis connecting uncovered items to required test scenarios.

---

## Tips for AI Agents

When working through these scenarios, AI agents should:

1. **Always check if databases exist** before running commands
2. **Use PYTHONPATH=../../src** when running commands from examples/verilator
3. **Start with simple queries** before attempting complex analysis
4. **Validate command syntax** with --help before running
5. **Chain commands** when multiple pieces of information are needed
6. **Parse JSON output** when programmatic processing is required
7. **Check for errors** and adjust approach if commands fail
8. **Provide context** in responses, not just raw command output
9. **Suggest next steps** based on findings
10. **Reference the SKILL.md** file for PyUCIS capabilities

## Common Command Patterns

```bash
# Set environment for commands from examples/verilator
cd examples/verilator
export PYTHONPATH=../../src

# Basic queries
python3 -m ucis show summary coverage/merged.cdb --output-format text
python3 -m ucis show tests coverage/merged.cdb --output-format json
python3 -m ucis show hierarchy coverage/merged.cdb --max-depth 2

# Advanced filtering
python3 -m ucis show gaps coverage/merged.cdb --threshold 80
python3 -m ucis show bins coverage/merged.cdb --min-hits 0 --max-hits 10 --sort count
python3 -m ucis show hotspots coverage/merged.cdb --limit 5

# Exports
python3 -m ucis show code-coverage coverage/merged.cdb --output-format lcov -o coverage.lcov
python3 -m ucis show code-coverage coverage/merged.cdb --output-format cobertura -o coverage.xml

# Comparisons
python3 -m ucis show compare baseline.cdb current.cdb --output-format json

# Using the API directly
python3 query_test_coverage.py
```

## Success Criteria

An AI agent successfully completes a scenario when it:
- ✅ Uses appropriate PyUCIS commands correctly
- ✅ Interprets results accurately
- ✅ Provides actionable insights
- ✅ Suggests next steps or recommendations
- ✅ Handles errors gracefully
- ✅ Explains its reasoning clearly

## Resources

- **PyUCIS Documentation:** See README.md in repository root
- **SKILL Definition:** src/ucis/share/SKILL.md
- **Example Scripts:** examples/verilator/query_test_coverage.py
- **Verilator Example:** examples/verilator/README.md
- **CLI Reference:** Run `python3 -m ucis --help` for all commands

---

**Note:** This is a living document. Add new scenarios as coverage analysis patterns emerge in your verification workflow.
