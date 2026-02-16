# PyUCIS Examples

This directory contains examples demonstrating PyUCIS capabilities.

## Available Examples

### 1. Verilator Coverage Example
**Directory:** [verilator/](verilator/)

Complete workflow for collecting coverage from Verilator simulations and converting to UCIS SQLite format.

**Features:**
- SystemVerilog counter design with assertions and covergroups
- Multiple test scenarios with coverage collection
- Conversion from Verilator coverage format to UCIS SQLite
- Database merging from multiple test runs
- Interactive TUI and command-line reporting
- ~6,000 coverage items (line, branch, toggle)

**Quick Start:**
```bash
cd verilator
make view  # Build, run tests, merge, and launch TUI
```

**See:** [verilator/README.md](verilator/README.md)

---

### 2. AI-Assisted Coverage Analysis
**Directory:** [ai_assisted_workflow/](ai_assisted_workflow/)

🤖 Learn how AI agents can work with coverage data for intelligent analysis.

**Features:**
- 13 detailed scenarios with problem statements and AI prompts
- Command selection and decision trees for AI agents
- Test optimization and gap analysis workflows
- CI/CD integration examples (LCOV, Cobertura)
- Automated validation scripts

**Quick Start:**
```bash
cd ai_assisted_workflow
./validate_ai_examples.sh  # Validate setup
cat AI_INDEX.md            # Navigation hub
```

**See:** [ai_assisted_workflow/README.md](ai_assisted_workflow/README.md)

---

## Which Example Should I Use?

| If you want to... | Use this example |
|-------------------|------------------|
| Learn Verilator integration | [verilator/](verilator/) |
| Collect coverage from RTL | [verilator/](verilator/) |
| Build coverage flow | [verilator/](verilator/) |
| Analyze existing coverage | [ai_assisted_workflow/](ai_assisted_workflow/) |
| Automate coverage analysis | [ai_assisted_workflow/](ai_assisted_workflow/) |
| Train AI agents | [ai_assisted_workflow/](ai_assisted_workflow/) |

## License

Apache License 2.0 - See LICENSE file in repository root
