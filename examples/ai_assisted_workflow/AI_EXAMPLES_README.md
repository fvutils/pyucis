# AI-Assisted Coverage Analysis Examples

This directory contains resources for using AI agents to analyze coverage data from the PyUCIS verilator example.

## Overview

These guides demonstrate how AI agents (LLMs) can effectively work with hardware verification coverage databases using PyUCIS tools. The examples are based on real coverage data from a Verilator simulation of a SystemVerilog counter module.

## Files in This Guide

### Core Documentation

1. **AI_ASSISTED_WORKFLOW.md** (Main Guide)
   - 13 detailed scenarios with problem statements, AI prompts, and expected results
   - Covers everything from basic queries to advanced optimization
   - Includes validation commands for each scenario
   - ~17KB comprehensive guide

2. **QUICK_START_AI.md** (Quick Reference)
   - Condensed cheat sheet for AI agents
   - Common command patterns
   - Decision tree for command selection
   - Error handling tips
   - ~6KB quick reference

3. **This README** (Overview)
   - Guide structure explanation
   - Getting started instructions
   - Testing the examples

### Example Data

The verilator example provides:
- **coverage/merged.cdb** - SQLite database with coverage from 5 tests
- **coverage/*.cdb** - Individual test databases
- **query_test_coverage.py** - Example Python script using PyUCIS API
- **README.md** - Full verilator example documentation

## Getting Started

### 1. Build the Example Database

```bash
cd examples/ai_assisted_workflow
make merge
```

This creates `coverage/merged.cdb` with data from 5 test runs:
- counter_tb (39 coverage items, 9 unique)
- test_basic_counting (36 items)
- test_load_operations (39 items)
- test_overflow (48 items, 8 unique)
- test_reset (39 items, 2 unique)

### 2. Set Up Environment

```bash
export PYTHONPATH=../../src
python3 -c "import ucis; print('✓ PyUCIS ready')"
```

### 3. Try Basic Commands

```bash
# Summary
python3 -m ucis show summary coverage/merged.cdb --output-format text

# Test list
python3 -m ucis show tests coverage/merged.cdb --output-format text

# Test contributions
python3 query_test_coverage.py
```

### 4. Launch Interactive TUI

```bash
python3 -m ucis view coverage/merged.cdb
```

## For AI Agents

### Recommended Reading Order

1. **Start here:** QUICK_START_AI.md
   - Get familiar with basic commands
   - Try the validation commands
   - Understand the decision tree

2. **Deep dive:** AI_ASSISTED_WORKFLOW.md
   - Work through scenarios 1-5 first
   - Try the advanced scenarios (6-10)
   - Experiment with custom scenarios (11-13)

3. **Reference:** ../../src/ucis/share/SKILL.md
   - Full PyUCIS capabilities
   - API reference
   - Best practices

### Key Capabilities to Develop

AI agents should be able to:

✅ **Basic Queries**
- Get coverage summaries
- List tests
- Show hierarchy
- Display metrics

✅ **Analysis**
- Identify coverage gaps
- Find hotspots
- Analyze test contributions
- Detect redundant tests

✅ **Optimization**
- Find minimum test sets
- Prioritize testing efforts
- Compare coverage runs
- Track coverage timelines

✅ **Integration**
- Export to CI/CD formats (LCOV, Cobertura)
- Generate reports
- Parse JSON output
- Write custom analysis scripts

✅ **Problem Solving**
- Understand requirements
- Choose appropriate commands
- Interpret results
- Provide actionable recommendations

## Testing AI Agent Performance

### Scenario-Based Testing

Use scenarios from AI_ASSISTED_WORKFLOW.md:

```bash
# Test Scenario 1: Basic assessment
AI_PROMPT="Summarize coverage status of examples/ai_assisted_workflow/coverage/merged.cdb"
# Expected: Agent uses show summary + show tests, reports 5 tests, coverage stats

# Test Scenario 2: Test contributions  
AI_PROMPT="Which tests in merged.cdb provide unique coverage?"
# Expected: Agent runs query_test_coverage.py, identifies counter_tb has most unique

# Test Scenario 3: Gap analysis
AI_PROMPT="Find coverage gaps below 80% in merged.cdb"
# Expected: Agent uses show gaps --threshold 80, interprets results

# Test Scenario 7: Export
AI_PROMPT="Export merged.cdb coverage to LCOV format"
# Expected: Agent uses show code-coverage --output-format lcov
```

### Validation Checklist

For each scenario, verify the AI agent:
- [ ] Chose appropriate commands
- [ ] Used correct syntax and options
- [ ] Set environment variables (PYTHONPATH)
- [ ] Checked file existence before running commands
- [ ] Interpreted results accurately
- [ ] Provided actionable insights
- [ ] Handled errors gracefully
- [ ] Suggested logical next steps

### Sample Success Metrics

- **Command Accuracy:** >90% of commands execute without errors
- **Interpretation:** Correctly identifies key findings from output
- **Efficiency:** Uses minimal commands to answer questions
- **Completeness:** Addresses all aspects of the problem
- **Clarity:** Explains results in accessible language

## Example AI Agent Session

Here's what a successful AI agent interaction looks like:

```
USER: What's the coverage status of merged.cdb?

AI: I'll analyze the coverage database for you.

[Runs: python3 -m ucis show summary coverage/merged.cdb --output-format text]
[Runs: python3 -m ucis show tests coverage/merged.cdb --output-format text]

Based on the analysis:

📊 Overall Status:
- Database: coverage/merged.cdb
- Total Tests: 5 (counter_tb, test_basic_counting, test_load_operations, 
  test_overflow, test_reset)
- Coverage Items: ~6,000 total (lines, branches, toggles)

📈 Coverage by Type:
- Line Coverage: XX%
- Branch Coverage: XX%  
- Toggle Coverage: XX%

🔍 Key Findings:
- counter_tb provides the most unique coverage (9 unique items)
- test_basic_counting adds no unique coverage (potential redundancy)
- test_overflow has high item count (48) with good uniqueness (8)

💡 Recommendations:
1. Review test_basic_counting for possible removal/refactoring
2. Focus new tests on identified gaps (use: show gaps --threshold 80)
3. Consider test set optimization (use query_test_coverage.py)

Would you like me to dive deeper into any of these areas?
```

## Advanced Usage

### Custom Analysis Scripts

AI agents can write Python scripts using the PyUCIS API:

```python
import sys
sys.path.insert(0, '../../src')
from ucis.sqlite import SqliteUCIS

db = SqliteUCIS.open_readonly('coverage/merged.cdb')
test_cov_api = db.get_test_coverage_api()

# Perform custom analysis
contributions = test_cov_api.get_all_test_contributions()
for contrib in contributions:
    print(f"{contrib.test_name}: {contrib.unique_items} unique")

db.close()
```

### Integration with Other Tools

```bash
# Export for visualization
python3 -m ucis show code-coverage coverage/merged.cdb --output-format json > cov.json

# Generate CI/CD artifacts
python3 -m ucis show code-coverage coverage/merged.cdb --output-format cobertura -o coverage.xml

# Create custom reports
python3 -m ucis show summary coverage/merged.cdb --output-format json | \
  jq '.statistics.total_covergroups'
```

## Troubleshooting

### Common Issues

**Problem:** Commands fail with "No module named pyucis"
```bash
# Solution
export PYTHONPATH=$(pwd)/../../src
```

**Problem:** Database not found
```bash
# Solution
cd examples/ai_assisted_workflow && make merge
```

**Problem:** Empty or zero coverage results
```bash
# Check database integrity
ls -lh coverage/merged.cdb  # Should be ~372KB
python3 query_test_coverage.py  # Should show 5 tests
```

### Debugging AI Agent Commands

Enable verbose output:
```bash
set -x  # Show commands as they execute
python3 -m ucis show summary coverage/merged.cdb --output-format text
set +x
```

Validate JSON output:
```bash
python3 -m ucis show summary coverage/merged.cdb --output-format json | python3 -m json.tool
```

## Resources

### Documentation
- **Verilator Example:** README.md (this directory)
- **PyUCIS Root:** ../../README.md
- **SKILL Definition:** ../../src/ucis/share/SKILL.md
- **API Examples:** query_test_coverage.py

### External Resources
- **UCIS Standard:** https://www.accellera.org/activities/committees/ucis
- **Verilator:** https://verilator.org/guide/latest/
- **PyUCIS GitHub:** https://github.com/fvutils/pyucis

## Contributing

Found a useful AI agent pattern? Add it to AI_ASSISTED_WORKFLOW.md:

```markdown
### Scenario XX: Your Scenario Name

**Problem:** Description of the problem

**Prompt:** "Exact prompt to give AI agent"

**Expected:** What the AI should do and report

**Validation:** Commands to verify the result
```

## License

Apache License 2.0 - See LICENSE file in repository root

## Support

- **Issues:** https://github.com/fvutils/pyucis/issues
- **Discussions:** Use GitHub discussions for questions
- **Examples:** See examples/ directory for more use cases

---

**Ready to start?** Open QUICK_START_AI.md and try the first few commands!
