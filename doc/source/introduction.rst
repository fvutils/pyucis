############
Introduction
############

What is PyUCIS?
===============
The Accellera Unified Coverage Interoperability Standard (UCIS) specifies
a data model, C API, and XML interchange format for coverage metrics
data. The PyUCIS library provides two APIs for creating and accessing 
coverage data via the UCIS data model:

- An object-oriented Python API
- A functional C-style Python API that is identical to the API defined in the Accellera standard

The PyUCIS library currently supports three back-ends for storing
and accessing coverage data:

- In-Memory: An in-memory transient data model
- XML: Ability to write and read a UCIS data model to the Accellera-defined interchange format
- Library: Ability to call a tool-provided implementation of the UCIS C API

Here is a short example of using the object-oriented Python API to create
a covergroup with a single coverpoint. Note that the database handle (`db`)
must be obtained from the appropriate back-end factory:

.. code-block:: python3

        testnode = db.createHistoryNode(
            None, 
            "logicalName",
            ucisdb,
            UCIS_HISTORYNODE_TEST)
        td = TestData(
            teststatus=UCIS_TESTSTATUS_OK,
            toolcategory="UCIS:simulator",
            date="20200202020"
            )
        testnode.setTestData(td)
        
        file = db.createFileHandle("dummy", os.getcwd())

        srcinfo = SourceInfo(file, 0, 0)
        du = db.createScope(
            "foo.bar",
            srcinfo,
            1, # weight
            UCIS_OTHER,
            UCIS_DU_MODULE,
            UCIS_ENABLED_STMT | UCIS_ENABLED_BRANCH
            | UCIS_ENABLED_COND | UCIS_ENABLED_EXPR
            | UCIS_ENABLED_FSM | UCIS_ENABLED_TOGGLE
            | UCIS_INST_ONCE | UCIS_SCOPE_UNDER_DU
            )
        
        instance = db.createInstance(
            "dummy",
            None, # sourceinfo
            1, # weight
            UCIS_OTHER,
            UCIS_INSTANCE,
            du,
            UCIS_INST_ONCE)
        
        cg = instance.createCovergroup(
            "cg",
            SourceInfo(file, 3, 0),
            1, # weight
            UCIS_OTHER)
        
        cp = cg.createCoverpoint(
            "t",
            SourceInfo(file, 4, 0),
            1, # weight
            UCIS_VLOG
            )
        cp.setComment("Hello There")
        
        cp.createBin(
            "auto[a]",
            SourceInfo(file, 4, 0),
            1,
            4,
            "a")

        db.write(ucisdb, None, True, -1)
        db.close()


Command-Line Tools
==================

PyUCIS includes comprehensive command-line tools for coverage analysis and reporting.
The ``ucis`` command provides several operations:

**Show Commands** (New!)
  Extract and analyze coverage data with support for multiple output formats:
  
  - **12 analysis commands**: summary, gaps, covergroups, bins, tests, hierarchy, 
    metrics, compare, hotspots, code-coverage, assertions, toggle
  - **4 export formats**: LCOV, Cobertura, JaCoCo, Clover
  - **CI/CD integration**: Works with Jenkins, GitLab CI, GitHub Actions, SonarQube, and more
  - **JSON & text output**: Machine-readable and human-readable formats
  
  See :doc:`show_commands` for detailed documentation.

**Merge**
  Combine multiple coverage databases into a single unified database

**Convert**
  Convert between different UCIS database formats (XML, YAML, LibUCIS)

**Report**
  Generate coverage reports from UCIS databases

Example:

.. code-block:: bash

    # Analyze coverage
    ucis show summary coverage.ucis
    
    # Export to CI/CD formats
    ucis show code-coverage coverage.ucis --output-format lcov > coverage.info
    
    # Compare databases
    ucis show compare baseline.ucis current.ucis
    
    # Merge databases
    ucis merge -o merged.ucis test1.ucis test2.ucis


MCP Server for AI Integration
==============================

PyUCIS includes a Model Context Protocol (MCP) server that enables AI agents and 
assistants to interact with coverage databases through a standardized API. This 
allows intelligent analysis, automated reporting, and natural language queries 
against your verification coverage data.

The MCP server provides 17+ specialized tools for:

- **Database Operations**: Open, close, and manage multiple coverage databases
- **Coverage Analysis**: Get summaries, identify gaps, analyze metrics
- **Advanced Queries**: Covergroups, bins, assertions, toggle coverage
- **Comparison**: Compare databases for regression detection
- **Export**: Generate LCOV, Cobertura, JaCoCo, and Clover reports

See :doc:`mcp_server` for detailed documentation on installation, configuration,
and integration with AI platforms like Claude Desktop.

Quick start:

.. code-block:: bash

    # Install with MCP support
    pip install pyucis[dev]
    
    # Start the MCP server
    pyucis-mcp-server


Contributors
============

   Ballance

