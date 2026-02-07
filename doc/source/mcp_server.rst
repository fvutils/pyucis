##########
MCP Server
##########

Overview
========

The PyUCIS MCP (Model Context Protocol) server enables AI agents and assistants to 
interact with UCIS coverage databases through a standardized API. This allows for 
intelligent coverage analysis, automated reporting, natural language queries, and 
seamless integration with AI-powered development workflows.

The MCP server uses stdio-based communication, making it compatible with various 
MCP clients including Claude Desktop, VS Code extensions, and custom integrations.

Features
========

Database Operations
-------------------

* **open_database**: Load UCIS databases in XML, YAML, or UCIS binary formats
* **close_database**: Clean up database resources
* **list_databases**: List all currently open databases
* **get_database_info**: Retrieve database metadata and statistics

Coverage Analysis Tools
-----------------------

* **get_coverage_summary**: Overall coverage statistics by type (statement, branch, etc.)
* **get_coverage_gaps**: Identify uncovered or low-coverage items with configurable thresholds
* **get_covergroups**: Retrieve covergroup details with optional bin information
* **get_bins**: Detailed bin-level coverage with advanced filtering capabilities
* **get_tests**: Test execution information and results
* **get_hierarchy**: Navigate and explore the design hierarchy
* **get_metrics**: Advanced coverage metrics and analysis

Advanced Features
-----------------

* **compare_databases**: Compare two databases for regression analysis and coverage deltas
* **get_hotspots**: Identify high-value coverage targets for optimization
* **get_code_coverage**: Export code coverage in multiple formats (LCOV, Cobertura, JaCoCo, Clover)
* **get_assertions**: SVA/PSL assertion coverage details
* **get_toggle_coverage**: Signal toggle coverage information

Installation
============

Prerequisites
-------------

* Python 3.8 or later
* mcp >= 0.9.0
* lxml
* python-jsonschema-objects
* jsonschema
* pyyaml

From Source
-----------

.. code-block:: bash

    # Clone the repository
    cd pyucis-mcp
    
    # Create and activate virtual environment
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    
    # Install with MCP server support
    pip install -e ".[dev]"

From PyPI
---------

.. code-block:: bash

    # Install with MCP support
    pip install pyucis[dev]

Usage
=====

Starting the Server
-------------------

The MCP server uses stdio-based communication:

.. code-block:: bash

    # Start the server
    pyucis-mcp-server

The server will listen for JSON-RPC messages on stdin and respond on stdout.

Configuration for Claude Desktop
---------------------------------

To integrate with Claude Desktop, add the following to your configuration file:

**macOS**: ``~/Library/Application Support/Claude/claude_desktop_config.json``

**Linux**: ``~/.config/Claude/claude_desktop_config.json``

**Windows**: ``%APPDATA%\Claude\claude_desktop_config.json``

.. code-block:: json

    {
      "mcpServers": {
        "pyucis": {
          "command": "pyucis-mcp-server",
          "env": {}
        }
      }
    }

After adding the configuration, restart Claude Desktop. The PyUCIS tools will be 
available in your conversations.

Available Tools
===============

Database Management
-------------------

open_database
~~~~~~~~~~~~~

Open a UCIS database for analysis.

**Parameters:**

* ``path`` (string, required): Path to the database file
* ``format`` (string, optional): Format type - "xml", "yaml", or "ucis" (auto-detected if not specified)

**Returns:** Database ID for subsequent operations

**Example:**

.. code-block:: json

    {
      "path": "/path/to/coverage.xml",
      "format": "xml"
    }

close_database
~~~~~~~~~~~~~~

Close an open database and release resources.

**Parameters:**

* ``db_id`` (string, required): Database ID returned from open_database

**Example:**

.. code-block:: json

    {
      "db_id": "db_1"
    }

list_databases
~~~~~~~~~~~~~~

List all currently open databases.

**Returns:** Array of database information including IDs, paths, and status

**Example:**

.. code-block:: json

    {}

get_database_info
~~~~~~~~~~~~~~~~~

Get metadata and statistics for a database.

**Parameters:**

* ``db_id`` (string, required): Database ID

**Returns:** Database metadata including format, size, and coverage type counts

Coverage Queries
----------------

get_coverage_summary
~~~~~~~~~~~~~~~~~~~~

Get overall coverage statistics aggregated by coverage type.

**Parameters:**

* ``db_id`` (string, required): Database ID

**Returns:** Coverage percentages for statement, branch, condition, expression, FSM, and toggle coverage

**Example:**

.. code-block:: json

    {
      "db_id": "db_1"
    }

get_coverage_gaps
~~~~~~~~~~~~~~~~~

Identify coverage gaps and items below a specified threshold.

**Parameters:**

* ``db_id`` (string, required): Database ID
* ``threshold`` (number, optional): Coverage percentage threshold (default: 80)

**Returns:** List of uncovered or low-coverage items with details

**Example:**

.. code-block:: json

    {
      "db_id": "db_1",
      "threshold": 80
    }

get_covergroups
~~~~~~~~~~~~~~~

Retrieve covergroup information with optional bin details.

**Parameters:**

* ``db_id`` (string, required): Database ID
* ``include_bins`` (boolean, optional): Include detailed bin information (default: false)

**Returns:** List of covergroups with coverage percentages and bin data if requested

get_bins
~~~~~~~~

Get detailed bin-level coverage with advanced filtering.

**Parameters:**

* ``db_id`` (string, required): Database ID
* ``covergroup`` (string, optional): Filter by covergroup name
* ``coverpoint`` (string, optional): Filter by coverpoint name
* ``min_hits`` (number, optional): Minimum hit count filter
* ``max_hits`` (number, optional): Maximum hit count filter
* ``sort_by`` (string, optional): Sort order - "count" or "name"

**Returns:** Detailed bin information including hit counts and coverage status

get_tests
~~~~~~~~~

Get test execution information and results.

**Parameters:**

* ``db_id`` (string, required): Database ID

**Returns:** List of tests with execution status, timestamps, and coverage contributions

get_hierarchy
~~~~~~~~~~~~~

Navigate and explore the design hierarchy.

**Parameters:**

* ``db_id`` (string, required): Database ID
* ``max_depth`` (number, optional): Maximum traversal depth (default: unlimited)

**Returns:** Hierarchical structure of design elements

get_metrics
~~~~~~~~~~~

Get advanced coverage metrics and analysis.

**Parameters:**

* ``db_id`` (string, required): Database ID

**Returns:** Comprehensive metrics including coverage density, complexity, and quality scores

Advanced Analysis
-----------------

compare_databases
~~~~~~~~~~~~~~~~~

Compare two databases for regression detection and coverage deltas.

**Parameters:**

* ``db_id`` (string, required): Baseline database ID
* ``compare_db_id`` (string, required): Comparison database ID

**Returns:** Coverage differences, regressions, and improvements

**Example:**

.. code-block:: json

    {
      "db_id": "baseline_db",
      "compare_db_id": "current_db"
    }

get_hotspots
~~~~~~~~~~~~

Identify high-value coverage targets for optimization.

**Parameters:**

* ``db_id`` (string, required): Database ID
* ``threshold`` (number, optional): Coverage threshold percentage
* ``limit`` (number, optional): Maximum items per category

**Returns:** Priority-ordered list of coverage hotspots

get_code_coverage
~~~~~~~~~~~~~~~~~

Export code coverage in various industry-standard formats.

**Parameters:**

* ``db_id`` (string, required): Database ID
* ``output_format`` (string, required): Export format - "json", "lcov", "cobertura", "jacoco", or "clover"

**Returns:** Formatted coverage data suitable for CI/CD tools

**Example:**

.. code-block:: json

    {
      "db_id": "db_1",
      "output_format": "lcov"
    }

get_assertions
~~~~~~~~~~~~~~

Get assertion coverage for SVA and PSL assertions.

**Parameters:**

* ``db_id`` (string, required): Database ID

**Returns:** Assertion coverage details including pass/fail counts

get_toggle_coverage
~~~~~~~~~~~~~~~~~~~

Get signal toggle coverage information.

**Parameters:**

* ``db_id`` (string, required): Database ID

**Returns:** Toggle coverage for signals including 0->1 and 1->0 transitions

Export Formats
==============

The MCP server supports multiple export formats for integration with CI/CD tools:

LCOV Format
-----------

Standard format for code coverage, compatible with:

* genhtml (HTML report generation)
* Codecov
* Coveralls
* GitHub Actions coverage reports

**Use case:** Visual HTML reports and cloud-based coverage tracking

Cobertura Format
----------------

XML format widely used in CI/CD pipelines:

* Jenkins (Cobertura Plugin)
* GitLab CI
* SonarQube
* Azure DevOps

**Use case:** Enterprise CI/CD integration and code quality platforms

JaCoCo Format
-------------

Java coverage format also supported by many tools:

* Maven
* Gradle
* SonarQube
* Bamboo

**Use case:** Java-based toolchains and enterprise quality gates

Clover Format
-------------

Atlassian coverage format:

* Bamboo
* Jenkins (Clover Plugin)
* IntelliJ IDEA

**Use case:** Atlassian ecosystem integration

CI/CD Integration Examples
==========================

GitHub Actions
--------------

.. code-block:: yaml

    name: Coverage Analysis
    on: [push, pull_request]
    
    jobs:
      coverage:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v3
          
          - name: Generate LCOV Report
            run: |
              pip install pyucis[dev]
              pyucis show code-coverage coverage.xml --output-format lcov > coverage.info
          
          - name: Upload to Codecov
            uses: codecov/codecov-action@v3
            with:
              files: ./coverage.info

GitLab CI
---------

.. code-block:: yaml

    coverage:
      stage: test
      script:
        - pip install pyucis[dev]
        - pyucis show code-coverage coverage.xml --output-format cobertura > coverage.xml
      artifacts:
        reports:
          coverage_report:
            coverage_format: cobertura
            path: coverage.xml

Jenkins Pipeline
----------------

.. code-block:: groovy

    pipeline {
        agent any
        stages {
            stage('Coverage') {
                steps {
                    sh 'pip install pyucis[dev]'
                    sh 'pyucis show code-coverage coverage.xml --output-format cobertura > coverage.xml'
                }
                post {
                    always {
                        cobertura coberturaReportFile: 'coverage.xml'
                    }
                }
            }
        }
    }

Development
===========

Running Tests
-------------

.. code-block:: bash

    # Run all MCP server tests
    pytest tests/test_mcp_*.py -v
    
    # Run with coverage
    pytest tests/test_mcp_*.py -v --cov=ucis.mcp --cov-report=html

Project Structure
-----------------

.. code-block:: text

    src/ucis/mcp/
    ├── __init__.py          # Package initialization
    ├── server.py            # MCP server implementation
    ├── db_manager.py        # Database handle management
    └── tools.py             # Tool implementations
    
    tests/
    ├── test_db_manager.py   # Database manager tests
    └── test_tools.py        # Tool implementation tests

Troubleshooting
===============

Server Not Starting
-------------------

**Issue:** Server fails to start or crashes immediately

**Solutions:**

1. Verify Python version is 3.8 or later:

   .. code-block:: bash

       python --version

2. Check all dependencies are installed:

   .. code-block:: bash

       pip install pyucis[dev]

3. Test with verbose output:

   .. code-block:: bash

       pyucis-mcp-server --help

Connection Issues
-----------------

**Issue:** Claude Desktop or other clients cannot connect

**Solutions:**

1. Verify the configuration file syntax is correct (valid JSON)
2. Check the command path is correct and executable
3. Restart the client application after configuration changes
4. Check client logs for error messages

Database Loading Errors
------------------------

**Issue:** Cannot open database files

**Solutions:**

1. Verify file path is absolute or correctly relative
2. Check file format matches the database content
3. Ensure file permissions allow reading
4. For XML files, validate against UCIS schema

Performance Optimization
------------------------

For large databases:

* Use specific queries instead of loading entire databases
* Close databases when no longer needed
* Use filtering options to reduce result sizes
* Consider pagination for large result sets

Resources
=========

* `Model Context Protocol Specification <https://modelcontextprotocol.io/>`_
* `UCIS Standard Documentation <https://www.accellera.org/activities/committees/ucis>`_
* `PyUCIS GitHub Repository <https://github.com/fvutils/pyucis>`_
* `Issue Tracker <https://github.com/fvutils/pyucis/issues>`_

License
=======

Apache License 2.0

See the LICENSE file in the repository for full license text.
