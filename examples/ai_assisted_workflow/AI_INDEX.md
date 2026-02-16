# AI-Assisted Coverage Analysis - Index

Quick navigation guide for all AI-related documentation.

## 📚 Start Here

**New to PyUCIS AI examples?** Follow this path:

1. 📖 **[AI_EXAMPLES_README.md](AI_EXAMPLES_README.md)** ← Start here!
   - Overview of the AI examples system
   - Getting started instructions
   - Setup and validation

2. ⚡ **[QUICK_START_AI.md](QUICK_START_AI.md)**
   - Command cheat sheet
   - Common patterns
   - Quick reference for AI agents

3. 📘 **[AI_ASSISTED_WORKFLOW.md](AI_ASSISTED_WORKFLOW.md)**
   - 13 detailed scenarios
   - Problem → Prompt → Expected results
   - Complete workflow examples

4. ✅ **[validate_ai_examples.sh](validate_ai_examples.sh)**
   - Validation script (run this first!)
   - Tests all core commands
   - Ensures everything works

5. 📊 **[AI_EXAMPLES_SUMMARY.md](AI_EXAMPLES_SUMMARY.md)**
   - What was created and why
   - Statistics and metrics
   - Integration guide

## 🎯 Quick Access by Task

### For AI Agents Learning PyUCIS
→ **QUICK_START_AI.md** - Commands and patterns

### For Scenario-Based Training
→ **AI_ASSISTED_WORKFLOW.md** - 13 detailed scenarios

### For Setup and Validation
→ **validate_ai_examples.sh** - Run this first

### For Overview and Context
→ **AI_EXAMPLES_README.md** - Big picture

### For Statistics and Metrics
→ **AI_EXAMPLES_SUMMARY.md** - What's included

## 📋 Scenario Quick Reference

| # | Scenario | Difficulty | File |
|---|----------|-----------|------|
| 1 | Coverage Assessment | 🟢 Basic | [AI_ASSISTED_WORKFLOW.md](AI_ASSISTED_WORKFLOW.md#scenario-1-initial-coverage-assessment) |
| 2 | Test Contributions | 🟢 Basic | [AI_ASSISTED_WORKFLOW.md](AI_ASSISTED_WORKFLOW.md#scenario-2-identifying-test-contributions) |
| 3 | Gap Analysis | 🟢 Basic | [AI_ASSISTED_WORKFLOW.md](AI_ASSISTED_WORKFLOW.md#scenario-3-coverage-gap-analysis) |
| 4 | Test Optimization | 🟡 Medium | [AI_ASSISTED_WORKFLOW.md](AI_ASSISTED_WORKFLOW.md#scenario-4-test-set-optimization) |
| 5 | Comparing Runs | 🟡 Medium | [AI_ASSISTED_WORKFLOW.md](AI_ASSISTED_WORKFLOW.md#scenario-5-comparing-test-runs) |
| 6 | Hierarchy Navigation | 🟡 Medium | [AI_ASSISTED_WORKFLOW.md](AI_ASSISTED_WORKFLOW.md#scenario-6-coverage-hierarchy-navigation) |
| 7 | CI/CD Export | 🟡 Medium | [AI_ASSISTED_WORKFLOW.md](AI_ASSISTED_WORKFLOW.md#scenario-7-export-for-cicd-integration) |
| 8 | Advanced Filtering | 🟡 Medium | [AI_ASSISTED_WORKFLOW.md](AI_ASSISTED_WORKFLOW.md#scenario-8-advanced-filtering-and-querying) |
| 9 | Assertions & Toggle | 🔴 Advanced | [AI_ASSISTED_WORKFLOW.md](AI_ASSISTED_WORKFLOW.md#scenario-9-assertion-and-toggle-coverage-analysis) |
| 10 | Metrics & Stats | 🔴 Advanced | [AI_ASSISTED_WORKFLOW.md](AI_ASSISTED_WORKFLOW.md#scenario-10-coverage-metrics-and-statistical-analysis) |
| 11 | Custom Scripts | 🔴 Advanced | [AI_ASSISTED_WORKFLOW.md](AI_ASSISTED_WORKFLOW.md#scenario-11-custom-coverage-analysis-script) |
| 12 | Regression Detection | 🔴 Advanced | [AI_ASSISTED_WORKFLOW.md](AI_ASSISTED_WORKFLOW.md#scenario-12-coverage-regression-detection) |
| 13 | Test Generation | 🔴 Advanced | [AI_ASSISTED_WORKFLOW.md](AI_ASSISTED_WORKFLOW.md#scenario-13-coverage-driven-test-generation-guidance) |

## 🔧 Command Quick Reference

### Most Common Commands
```bash
# Get started
cd examples/verilator
export PYTHONPATH=../../src
./validate_ai_examples.sh

# Basic queries
python3 -m ucis show summary coverage/merged.cdb --output-format text
python3 -m ucis show tests coverage/merged.cdb --output-format json
python3 -m ucis show hierarchy coverage/merged.cdb --max-depth 3

# Analysis
python3 -m ucis show gaps coverage/merged.cdb --threshold 80
python3 -m ucis show hotspots coverage/merged.cdb --limit 10
python3 query_test_coverage.py

# Export
python3 -m ucis show code-coverage coverage/merged.cdb --output-format lcov -o coverage.lcov
python3 -m ucis show code-coverage coverage/merged.cdb --output-format cobertura -o coverage.xml

# Interactive
python3 -m ucis view coverage/merged.cdb
```

See **[QUICK_START_AI.md](QUICK_START_AI.md)** for complete reference.

## 📦 Package Contents

```
examples/verilator/
├── AI_INDEX.md                    ← You are here
├── AI_EXAMPLES_README.md          ← Start here for overview
├── QUICK_START_AI.md              ← Command reference
├── AI_ASSISTED_WORKFLOW.md        ← 13 detailed scenarios
├── AI_EXAMPLES_SUMMARY.md         ← Statistics and metrics
├── validate_ai_examples.sh        ← Validation script
├── coverage/merged.cdb            ← Example database (372KB)
├── query_test_coverage.py         ← API example script
└── README.md                      ← Verilator example docs
```

## 🚀 Getting Started (3 Steps)

1. **Validate Setup**
   ```bash
   cd examples/verilator
   ./validate_ai_examples.sh
   ```

2. **Read Quick Start**
   Open [QUICK_START_AI.md](QUICK_START_AI.md) and try the basic commands

3. **Try a Scenario**
   Pick scenario 1 from [AI_ASSISTED_WORKFLOW.md](AI_ASSISTED_WORKFLOW.md) and follow along

## 🎓 Learning Path

### Beginner Track
1. Read AI_EXAMPLES_README.md (setup)
2. Run validate_ai_examples.sh (verify)
3. Read QUICK_START_AI.md (commands)
4. Try scenarios 1-3 (basic queries)

### Intermediate Track
5. Try scenarios 4-8 (analysis & export)
6. Experiment with JSON output
7. Write simple parsing scripts
8. Explore the TUI

### Advanced Track
9. Try scenarios 9-13 (advanced analysis)
10. Use PyUCIS API directly
11. Create custom workflows
12. Integrate with CI/CD

## 🔗 Related Resources

- **[Verilator Example README](README.md)** - Full verilator example docs
- **[PyUCIS SKILL.md](../../src/ucis/share/SKILL.md)** - API reference for AI agents
- **[Main README](../../README.md)** - PyUCIS overview
- **[query_test_coverage.py](query_test_coverage.py)** - Python API example

## ❓ Quick FAQ

**Q: Which file should I read first?**
A: [AI_EXAMPLES_README.md](AI_EXAMPLES_README.md) for overview, then [QUICK_START_AI.md](QUICK_START_AI.md) for commands.

**Q: How do I know if my setup is correct?**
A: Run `./validate_ai_examples.sh` - it tests everything.

**Q: I'm an AI agent, where do I start?**
A: [QUICK_START_AI.md](QUICK_START_AI.md) is designed for you!

**Q: What's the difference between the scenario files?**
A: 
- QUICK_START_AI.md = Command reference (cheat sheet)
- AI_ASSISTED_WORKFLOW.md = Detailed scenarios with prompts
- AI_EXAMPLES_README.md = Overview and getting started
- AI_EXAMPLES_SUMMARY.md = What was created and why

**Q: Do I need to read everything?**
A: No! Start with AI_EXAMPLES_README.md, then pick what you need:
- Need commands? → QUICK_START_AI.md
- Need scenarios? → AI_ASSISTED_WORKFLOW.md
- Need stats? → AI_EXAMPLES_SUMMARY.md

## 📈 Progress Tracking

Track your progress through the scenarios:

- [ ] Completed setup validation
- [ ] Tried basic commands (scenarios 1-3)
- [ ] Completed analysis scenarios (4-8)
- [ ] Mastered advanced scenarios (9-10)
- [ ] Created custom scripts (11-13)
- [ ] Integrated with CI/CD
- [ ] Applied to real verification project

## 🤝 Contributing

Found a useful pattern? Add it to [AI_ASSISTED_WORKFLOW.md](AI_ASSISTED_WORKFLOW.md)!

See the Contributing section in AI_EXAMPLES_README.md for details.

## 📝 License

Apache License 2.0 - See LICENSE file in repository root

---

**Questions?** Open an issue at https://github.com/fvutils/pyucis/issues

**Ready to start?** → [AI_EXAMPLES_README.md](AI_EXAMPLES_README.md)
