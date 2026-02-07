# pyucis
Python API to Unified Coverage Interoperability Standard (UCIS) Data Model

[![Build Status](https://dev.azure.com/mballance/fvutils/_apis/build/status/fvutils.pyucis?branchName=master)](https://dev.azure.com/mballance/fvutils/_build/latest?definitionId=16&branchName=master)
[![PyPI version](https://badge.fury.io/py/pyucis.svg)](https://badge.fury.io/py/pyucis)
[![PyPI](https://img.shields.io/pypi/dm/pyucis.svg?label=PyPI%20downloads)](https://pypi.org/project/pyucis/)

## Features

- **Python API** for manipulating UCIS coverage databases
- **CLI Tools** for database conversion, merging, and reporting
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

# Query coverage information
pyucis show summary coverage.xml
pyucis show gaps coverage.xml --threshold 80
pyucis show covergroups coverage.xml
```

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

## Documentation

- [MCP Server Documentation](MCP_SERVER.md)
- [UCIS Standard](https://www.accellera.org/activities/committees/ucis)

## License

Apache 2.0

## Links

- [PyPI](https://pypi.org/project/pyucis/)
- [GitHub](https://github.com/fvutils/pyucis)
- [Issue Tracker](https://github.com/fvutils/pyucis/issues)

