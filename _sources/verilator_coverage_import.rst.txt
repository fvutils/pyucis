###########################
Verilator Coverage Import
###########################

PyUCIS provides built-in support for importing coverage data from Verilator, 
enabling seamless integration of Verilator verification results into the UCIS 
ecosystem.

Overview
========

The Verilator coverage import feature (``vltcov`` format) supports:

* **Functional Coverage**: Covergroups, coverpoints, and bins with hit counts
* **Code Coverage**: Line, branch, and toggle coverage
* **File Format**: SystemC::Coverage-3 format (``.dat`` files)
* **Output Formats**: Convert to XML, SQLite, YAML, or any UCIS format
* **CLI Integration**: Works with all PyUCIS commands (convert, merge, report)

Coverage Types Supported
========================

Functional Coverage (Full Support)
----------------------------------

* **Covergroups**: SystemVerilog covergroups with complete hierarchy
* **Coverpoints**: Individual coverage points within covergroups  
* **Bins**: Coverage bins with hit counts and thresholds
* **Source Locations**: File names and line numbers preserved

Code Coverage (Full Support)
----------------------------

* **Line Coverage**: Statement execution tracking
* **Branch Coverage**: Conditional branch tracking
* **Toggle Coverage**: Signal toggle tracking

Quick Start
===========

Command Line Usage
------------------

**Convert Verilator coverage to UCIS XML:**

.. code-block:: bash

    pyucis convert --input-format vltcov coverage.dat --out output.xml

**Convert to SQLite database:**

.. code-block:: bash

    pyucis convert --input-format vltcov --output-format sqlite \
           coverage.dat --out coverage.ucisdb

**Merge multiple Verilator runs:**

.. code-block:: bash

    pyucis merge --input-format vltcov run1.dat run2.dat run3.dat --out merged.xml

**Generate HTML report:**

.. code-block:: bash

    pyucis convert --input-format vltcov coverage.dat --out temp.xml
    pyucis report temp.xml -of html -o report.html

Python API
----------

Import Verilator coverage using the format registry:

.. code-block:: python

    from ucis.rgy.format_rgy import FormatRgy
    
    # Get format registry and vltcov interface
    rgy = FormatRgy.inst()
    desc = rgy.getDatabaseDesc('vltcov')
    fmt_if = desc.fmt_if()
    
    # Import Verilator coverage
    db = fmt_if.read('coverage.dat')
    
    # Export to XML
    db.write('output.xml')
    db.close()

Verilator Coverage Format
==========================

Verilator generates coverage data in the **SystemC::Coverage-3** text format:

* **File Extension**: ``.dat``
* **Format**: Text-based with compact key-value encoding
* **Delimiters**: Uses ASCII control characters (``\001`` and ``\002``)
* **Location**: Generated in simulation output directory

Example Verilator coverage entry:

.. code-block:: text

    C '\001t\002funccov\001page\002v_funccov/cg1\001f\002test.v\001l\00219\001bin\002low\001h\002cg1.cp\001' 42

This decodes to:

* Type: Functional coverage
* Covergroup: ``cg1``
* File: ``test.v``, line 19
* Bin: ``low``
* Hit count: 42

Generating Verilator Coverage
==============================

Enable coverage in your Verilator simulation:

.. code-block:: bash

    # Enable functional coverage
    verilator --coverage --coverage-func --coverage-line -cc design.v
    
    # Run simulation (generates coverage.dat)
    make -C obj_dir -f Vdesign.mk
    ./obj_dir/Vdesign
    
    # Import into PyUCIS
    pyucis convert --input-format vltcov coverage.dat --out coverage.xml

Workflow Examples
=================

Basic Workflow
--------------

.. code-block:: bash

    # 1. Run Verilator simulation with coverage
    verilator --coverage --coverage-func design.v testbench.cpp
    make -C obj_dir -f Vdesign.mk
    ./obj_dir/Vdesign  # Generates coverage.dat
    
    # 2. Convert to UCIS
    pyucis convert --input-format vltcov coverage.dat --out coverage.xml
    
    # 3. Generate report
    pyucis report coverage.xml -of html -o report.html

Regression Testing
------------------

Merge coverage from multiple test runs:

.. code-block:: bash

    # Run multiple tests (each generates coverage.dat)
    ./run_test1.sh  # → test1/coverage.dat
    ./run_test2.sh  # → test2/coverage.dat
    ./run_test3.sh  # → test3/coverage.dat
    
    # Merge all coverage
    pyucis merge --input-format vltcov \
           test1/coverage.dat test2/coverage.dat test3/coverage.dat \
           --out merged.ucisdb --output-format sqlite
    
    # Analyze merged results
    pyucis show summary merged.ucisdb
    pyucis show gaps merged.ucisdb

CI/CD Integration
-----------------

Export Verilator coverage to CI-friendly formats:

.. code-block:: bash

    # Convert to SQLite for querying
    pyucis convert --input-format vltcov coverage.dat \
           --output-format sqlite --out coverage.ucisdb
    
    # Export to LCOV for CI tools
    pyucis show code-coverage coverage.ucisdb --output-format lcov > coverage.info
    
    # Export to Cobertura for Jenkins/GitLab
    pyucis show code-coverage coverage.ucisdb --output-format cobertura > coverage.xml

Advanced Usage
==============

Selective Import
----------------

Filter coverage during import:

.. code-block:: python

    from ucis.rgy.format_rgy import FormatRgy
    from ucis.vltcov import VltParser
    
    # Parse Verilator file
    parser = VltParser()
    items = parser.parse_file('coverage.dat')
    
    # Filter to functional coverage only
    func_items = [item for item in items if item.is_functional_coverage()]
    
    # Build custom database
    # ... (map filtered items to UCIS)

Integration with PyUCIS Features
---------------------------------

Use all PyUCIS capabilities with imported Verilator coverage:

.. code-block:: bash

    # Analyze coverage
    pyucis show summary coverage.dat --input-format vltcov
    pyucis show gaps coverage.dat --input-format vltcov
    pyucis show covergroups coverage.dat --input-format vltcov
    
    # Compare runs
    pyucis show compare baseline.dat current.dat --input-format vltcov
    
    # Export to various formats
    pyucis show code-coverage coverage.dat --input-format vltcov \
           --output-format jacoco > jacoco.xml

Implementation Details
======================

Architecture
------------

The Verilator import implementation consists of:

1. **VltParser** - Parses SystemC::Coverage-3 format
2. **VltCoverageItem** - Data structure for coverage entries
3. **VltToUcisMapper** - Maps Verilator data to UCIS hierarchy
4. **DbFormatIfVltcov** - Format interface for PyUCIS registry

The import process:

.. code-block:: text

    Verilator .dat file
           ↓
    VltParser (parse format)
           ↓
    VltCoverageItem list
           ↓
    VltToUcisMapper (build UCIS)
           ↓
    UCIS Database (MemUCIS)
           ↓
    Export (XML, SQLite, etc.)

Source Code
-----------

The implementation is in ``src/ucis/vltcov/``:

* ``vlt_parser.py`` - Format parser
* ``vlt_coverage_item.py`` - Data structures
* ``vlt_to_ucis_mapper.py`` - UCIS mapping
* ``db_format_if_vltcov.py`` - Format interface

Limitations
===========

Current Limitations
-------------------

* **Read-Only**: Import only (no export to Verilator format)
* **Memory**: Large coverage files loaded entirely into memory during parsing

These limitations do not affect typical usage and may be addressed in future releases.

Troubleshooting
===============

Common Issues
-------------

**"Unknown format: vltcov"**
    Ensure PyUCIS is properly installed: ``pip install -e .``

**Import fails with parsing error**
    Verify the file is a valid Verilator coverage file (should start with ``'SystemC::Coverage-3```)

**Missing coverage data**
    Check that Verilator was run with appropriate coverage flags (``--coverage``, ``--coverage-func``)

**Empty output database**
    Ensure the input ``.dat`` file contains coverage data (not just headers)

See Also
========

* :doc:`commands` - PyUCIS command-line interface
* :doc:`show_commands` - Coverage analysis commands
* :doc:`reference/html_coverage_report` - HTML report generation
* `Verilator Documentation <https://verilator.org/guide/latest/>`_ - Verilator coverage guide

References
==========

* **Verilator**: https://verilator.org/
* **UCIS Specification**: IEEE 1800.2
* **Format Registry**: :doc:`reference/native_api`
