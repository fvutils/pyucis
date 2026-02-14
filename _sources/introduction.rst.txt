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

The PyUCIS library supports multiple back-ends for storing
and accessing coverage data:

- **In-Memory**: Fast transient data model stored in RAM
- **SQLite**: Persistent, queryable storage using SQLite3 databases  
- **XML**: Read and write UCIS data in the Accellera-defined interchange format
- **YAML**: Human-readable text format for coverage data
- **Verilator**: Import coverage from Verilator (SystemC::Coverage-3 format)
- **Library**: Call tool-provided implementations of the UCIS C API

SQLite Backend
==============

The SQLite backend is a powerful option for persistent coverage storage:

* **Persistent Storage** - Coverage data saved directly to .ucisdb files
* **SQL Queries** - Direct database access for custom analysis
* **Large Databases** - Efficient handling of very large coverage datasets
* **Native C Library** - High-performance UCIS 1.0 C API implementation

Quick example using SQLite:

.. code-block:: python3

    from ucis.sqlite import SqliteUCIS
    from ucis.scope_type_t import ScopeTypeT
    from ucis.source_t import SourceT
    
    # Create or open database
    db = SqliteUCIS("coverage.ucisdb")
    
    # Build hierarchy
    top = db.createScope("top", None, 1, SourceT.NONE, 
                        ScopeTypeT.INSTANCE, 0)
    
    # Create covergroup
    cg = top.createCovergroup("addr_cg", None, 1, SourceT.NONE)
    
    # Close database
    db.close()

See :doc:`reference/sqlite_api` for complete SQLite API documentation.

Object-Oriented API Example
============================

Here is an example using the in-memory backend with the object-oriented Python API:

.. code-block:: python3

        from ucis.mem import MemFactory
        from ucis.history_node_kind import HistoryNodeKind
        from ucis.test_status_t import TestStatusT
        from ucis.source_t import SourceT
        from ucis.source_info import SourceInfo
        from ucis.test_data import TestData
        
        # Create in-memory database
        db = MemFactory.create()
        
        testnode = db.createHistoryNode(
            None, 
            "logicalName",
            "test.sv",
            HistoryNodeKind.TEST)
        td = TestData(
            teststatus=TestStatusT.OK,
            toolcategory="UCIS:simulator",
            date="20200202020"
            )
        testnode.setTestData(td)
        
        file = db.createFileHandle("dummy.v", os.getcwd())

        srcinfo = SourceInfo(file, 0, 0)
        du = db.createScope(
            "foo.bar",
            srcinfo,
            1, # weight
            SourceT.VLOG,
            ScopeTypeT.DU_MODULE,
            0  # flags
            )
        
        instance = db.createInstance(
            "dummy",
            None, # sourceinfo
            1, # weight
            SourceT.VLOG,
            ScopeTypeT.INSTANCE,
            du,
            0)  # flags
        
        cg = instance.createCovergroup(
            "cg",
            SourceInfo(file, 3, 0),
            1, # weight
            SourceT.VLOG)
        
        cp = cg.createCoverpoint(
            "t",
            SourceInfo(file, 4, 0),
            1, # weight
            SourceT.VLOG
            )
        cp.setComment("Hello There")
        
        cp.createBin(
            "auto[a]",
            SourceInfo(file, 4, 0),
            1,
            4,
            "a")

        db.write("output.xml", None, True, -1)
        db.close()


Command-Line Tools
==================

PyUCIS includes comprehensive command-line tools for coverage analysis and reporting.
The ``ucis`` command provides several operations:

**Interactive Terminal UI** (New!)
  Real-time coverage exploration with a keyboard-driven interface:
  
  - **5 specialized views**: Dashboard, Hierarchy, Gaps, Hotspots, Metrics
  - **Color-coded indicators**: Quick visual assessment of coverage levels
  - **Smart prioritization**: Built-in hotspot analysis for test planning
  - **SSH-friendly**: Works perfectly in remote terminal sessions
  - **Fast navigation**: Keyboard shortcuts for efficient browsing
  
  See :doc:`tui` for complete TUI documentation.

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
  Convert between different UCIS database formats (XML, YAML, Verilator, LibUCIS)

**Report**
  Generate coverage reports from UCIS databases in multiple formats:
  
  - **HTML** - Interactive single-file report with charts, bin details, and filtering
  - **JSON** - Machine-readable structured data
  - **Text** - Human-readable terminal output
  - **XML** - Interchange format
  - **Cobertura** - XML format for CI/CD tools
  
  See :doc:`reference/html_coverage_report` for HTML report documentation.

Example:

.. code-block:: bash

    # Interactive Terminal UI - new!
    ucis view coverage.ucis
    # Import Verilator coverage
    ucis convert --input-format vltcov coverage.dat --out coverage.xml
    
    # Generate interactive HTML report
    ucis report coverage.ucis -of html -o report.html
    
    # Analyze coverage
    ucis show summary coverage.ucis
    
    # Export to CI/CD formats
    ucis show code-coverage coverage.ucis --output-format lcov > coverage.info
    
    # Compare databases
    ucis show compare baseline.ucis current.ucis
    
    # Merge databases
    ucis merge -o merged.ucis test1.ucis test2.ucis

See :doc:`verilator_coverage_import` for detailed Verilator import documentation.


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

   Matthew Ballance


