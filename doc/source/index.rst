PyUCIS Documentation
====================

PyUCIS is a Python implementation of the Unified Coverage Interoperability Standard (UCIS) for storing, manipulating, and reporting functional verification coverage data.

**Key Features:**

* **Multiple Backend Support** - In-memory, SQLite, XML, and YAML backends
* **SQLite Backend** - Persistent, queryable storage with SQL access
* **Native C Library** - High-performance UCIS 1.0 C API with SQLite backend
* **Full UCIS API** - Complete implementation of the UCIS object-oriented API
* **Coverage Import** - Import from Verilator, cocotb-coverage, and AVL frameworks
* **Coverage Reporting** - Interactive HTML, JSON, XML, Cobertura, and text report formats
* **Interactive HTML Reports** - Single-file reports with visualizations, bin details, and filtering
* **Interactive Terminal UI** - Real-time coverage exploration with keyboard-driven navigation
* **Coverage Merging** - Combine coverage from multiple test runs
* **Cross-Platform** - Works on Linux, macOS, and Windows

Contents:

.. toctree::
   :maxdepth: 2
   
   introduction
   commands
   tui
   show_commands
   verilator_coverage_import
   cocotb_avl_coverage_import
   mcp_server
   reference/reference
   
   
Indices and tables
==================
