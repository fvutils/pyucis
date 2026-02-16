######################################
Coverage Import (cocotb and AVL)
######################################

PyUCIS provides built-in support for importing functional coverage data from 
**cocotb-coverage** and **AVL (Apheleia Verification Library)** frameworks, 
enabling seamless integration of Python-based verification results into the UCIS 
ecosystem.

Overview
========

The coverage import features support:

* **cocotb-coverage**: XML and YAML export formats
* **AVL (Apheleia Verification Library)**: JSON export formats (3 variations)
* **Automatic Format Detection**: Intelligently detects input format
* **Full Coverage Hierarchy**: Covergroups, coverpoints, crosses, and bins
* **Output Formats**: Convert to XML, SQLite, YAML, or any UCIS format
* **Hit Count Preservation**: Maintains bin hit counts from source data

Supported Frameworks
====================

cocotb-coverage
---------------

cocotb-coverage is a functional coverage library for cocotb (Python-based testbenches).

**Formats Supported:**

* **XML Format**: Hierarchical tree structure with nested elements
* **YAML Format**: Flat dictionary with dot-separated keys

Both formats produce identical UCIS databases (validated by equivalence tests).

**Website**: https://github.com/mciepluc/cocotb-coverage

AVL (Apheleia Verification Library)
------------------------------------

AVL is a Python verification framework focused on functional coverage.

**Formats Supported:**

* **Hierarchical JSON**: Nested covergroups/coverpoints structure
* **DataFrame Records**: List of coverage records (pandas export)
* **DataFrame Table**: Indexed coverage table (pandas export)

All three JSON variations are automatically detected and imported.

**Website**: https://github.com/projectapheleia/avl

Coverage Types Supported
=========================

Functional Coverage (Full Support)
-----------------------------------

* **Covergroups**: Coverage groups with complete hierarchy
* **Coverpoints**: Individual coverage points within groups
* **Cross Coverage**: Cross product of multiple coverpoints
* **Bins**: Coverage bins with hit counts and thresholds

Quick Start
===========

Command Line (CLI)
------------------

The fastest way to import coverage using the CLI:

.. code-block:: bash

    # Import cocotb XML and convert to UCIS XML
    pyucis convert --input-format cocotb-xml coverage.xml --output-format xml --out output.xml
    
    # Import cocotb YAML and convert to UCIS YAML
    pyucis convert --input-format cocotb-yaml coverage.yml --output-format yaml --out output.yml
    
    # Import AVL JSON and convert to UCIS XML
    pyucis convert --input-format avl-json coverage.json --output-format xml --out output.xml
    
    # Merge multiple cocotb files
    pyucis merge --input-format cocotb-xml run1.xml run2.xml run3.xml --output-format xml --out merged.xml

Automatic Import (Recommended)
-------------------------------

The simplest way to import coverage is using automatic format detection:

.. code-block:: python

    from ucis.format_detection import read_coverage_file
    
    # Automatically detects and imports any supported format
    db = read_coverage_file('coverage.xml')    # cocotb XML
    db = read_coverage_file('coverage.yml')    # cocotb YAML  
    db = read_coverage_file('coverage.json')   # AVL JSON

Import Specific Formats
------------------------

You can also import specific formats explicitly:

.. code-block:: python

    from ucis.cocotb import read_cocotb_xml, read_cocotb_yaml
    from ucis.avl import read_avl_json
    
    # Import cocotb XML
    db = read_cocotb_xml('coverage.xml')
    
    # Import cocotb YAML
    db = read_cocotb_yaml('coverage.yml')
    
    # Import AVL JSON (any variation)
    db = read_avl_json('coverage.json')

Export to Other Formats
------------------------

Once imported, you can export to any UCIS format:

.. code-block:: python

    from ucis.format_detection import read_coverage_file
    from ucis.sqlite.sqlite_ucis import SqliteUCIS
    
    # Import cocotb coverage
    db = read_coverage_file('cocotb_coverage.xml')
    
    # Export to SQLite
    db_sqlite = SqliteUCIS('coverage.ucisdb')
    # (Note: Full import/export workflow depends on PyUCIS backend capabilities)

cocotb-coverage Integration
============================

Generating cocotb Coverage
---------------------------

Use cocotb-coverage in your testbench:

.. code-block:: python

    from cocotb_coverage.coverage import CoverPoint, CoverGroup
    import cocotb
    
    # Define coverage
    @CoverGroup
    class MyCoverage:
        @CoverPoint("addr", bins=[(0, 31), (32, 63), (64, 127)])
        def addr_range(self):
            pass
    
    @cocotb.test()
    async def my_test(dut):
        cov = MyCoverage()
        # ... run test and sample coverage
        cov.addr_range.sample(dut.addr.value)
        
    # At end of simulation, export coverage
    from cocotb_coverage.coverage import coverage_db
    coverage_db.export_to_xml("coverage.xml")
    coverage_db.export_to_yaml("coverage.yml")

Importing into PyUCIS
---------------------

.. code-block:: python

    from ucis.format_detection import read_coverage_file
    
    # Import cocotb XML
    db = read_coverage_file('coverage.xml')
    
    # Analyze coverage
    from ucis.scope_type_t import ScopeTypeT
    
    def count_coverpoints(scope):
        count = 0
        if scope.getScopeType() == ScopeTypeT.COVERPOINT:
            count += 1
        for child in scope.scopes(-1):
            count += count_coverpoints(child)
        return count
    
    print(f"Total coverpoints: {count_coverpoints(db)}")

File Format Details
-------------------

**cocotb XML Format:**

.. code-block:: xml

    <top abs_name="top" coverage="35" cover_percentage="8.16">
      <test abs_name="top.test">
        <covergroup abs_name="top.test.my_cg">
          <coverpoint abs_name="top.test.my_cg.addr_cp" weight="1" at_least="1">
            <bin0 bin="low" hits="13" />
            <bin1 bin="mid" hits="8" />
          </coverpoint>
        </covergroup>
      </test>
    </top>

**cocotb YAML Format:**

.. code-block:: yaml

    top.test.my_cg.addr_cp:
      at_least: 1
      bins:_hits:
        low: 13
        mid: 8
      cover_percentage: 100.0
      weight: 1

AVL Integration
===============

Generating AVL Coverage
-----------------------

Use AVL in your Python testbench:

.. code-block:: python

    from avl.coverage import CoverPoint, CoverGroup
    import pandas as pd
    
    # Define coverage
    cg = CoverGroup("address_coverage")
    cp = CoverPoint("addr_range", bins={"low": (0, 31), "high": (32, 63)})
    cg.add_coverpoint(cp)
    
    # Sample coverage
    for addr in test_addresses:
        cp.sample(addr)
    
    # Export coverage
    cg.export_json("coverage.json")  # Hierarchical format
    cg.export_dataframe("coverage_df.json")  # DataFrame format

Importing into PyUCIS
---------------------

.. code-block:: python

    from ucis.avl import read_avl_json
    
    # Import AVL JSON (any variation)
    db = read_avl_json('coverage.json')
    
    # Access coverage data
    from ucis.scope_type_t import ScopeTypeT
    
    def print_bins(scope, indent=0):
        scope_type = scope.getScopeType()
        if scope_type in [ScopeTypeT.COVERPOINT, ScopeTypeT.CROSS]:
            bins = list(scope.coverItems(-1))
            print(f"{' '*indent}{scope.getScopeName()}: {len(bins)} bins")
            for bin_item in bins[:3]:
                name = bin_item.getName()
                hits = bin_item.getCoverData().data
                print(f"{' '*(indent+2)}- {name}: {hits} hits")
        
        for child in scope.scopes(-1):
            print_bins(child, indent + 2)
    
    print_bins(db)

File Format Details
-------------------

**AVL Hierarchical JSON:**

.. code-block:: json

    {
      "metadata": {
        "generator": "AVL",
        "version": "0.5.0"
      },
      "functional_coverage": {
        "covergroups": {
          "address_coverage": {
            "coverpoints": {
              "addr_range": {
                "bins": {
                  "low": {"hits": 45},
                  "high": {"hits": 22}
                }
              }
            }
          }
        }
      }
    }

**AVL DataFrame Format:**

.. code-block:: json

    [
      {
        "coverpoint_name": "addr_range.low",
        "bin_name": "low",
        "hits": 45,
        "goal": 1,
        "covered": true
      },
      {
        "coverpoint_name": "addr_range.high",
        "bin_name": "high",
        "hits": 22,
        "goal": 1,
        "covered": true
      }
    ]

Format Detection
================

PyUCIS automatically detects the input format based on file content:

.. code-block:: python

    from ucis.format_detection import detect_format, CoverageFormat
    
    # Detect format
    fmt = detect_format('coverage.xml')
    
    if fmt == CoverageFormat.COCOTB_XML:
        print("cocotb XML format detected")
    elif fmt == CoverageFormat.COCOTB_YAML:
        print("cocotb YAML format detected")
    elif fmt == CoverageFormat.AVL_JSON:
        print("AVL JSON format detected")
    else:
        print("Unknown format")

Detection Criteria
------------------

**cocotb XML**:
  - File extension: ``.xml`` or ``.cov``
  - Contains ``abs_name`` and ``cover_percentage`` attributes

**cocotb YAML**:
  - File extension: ``.yml`` or ``.yaml``
  - Contains ``bins:_hits`` and ``cover_percentage`` keys

**AVL JSON**:
  - File extension: ``.json``
  - Contains ``metadata.generator == "AVL"`` or hierarchical coverage structure
  - Or contains ``coverpoint_name``/``bin_name`` fields (DataFrame format)

Workflow Examples
=================

Command Line Workflows
----------------------

**Basic Conversion:**

.. code-block:: bash

    # Import and convert to standard UCIS
    pyucis convert --input-format cocotb-xml coverage.xml --output-format xml --out ucis.xml
    pyucis convert --input-format cocotb-yaml coverage.yml --output-format xml --out ucis.xml
    pyucis convert --input-format avl-json coverage.json --output-format xml --out ucis.xml

**Merge Multiple Runs:**

.. code-block:: bash

    # Merge coverage from multiple test runs
    pyucis merge --input-format cocotb-xml \
           test1_coverage.xml test2_coverage.xml test3_coverage.xml \
           --output-format xml --out merged.xml

**List Available Formats:**

.. code-block:: bash

    python -c "
    from ucis.rgy.format_rgy import FormatRgy
    rgy = FormatRgy.inst()
    for fmt in sorted(rgy.getDatabaseFormats()):
        desc = rgy.getDatabaseDesc(fmt)
        print(f'{fmt}: {desc._description}')
    "

Python API Workflows
--------------------

Basic Workflow
--------------

.. code-block:: python

    from ucis.format_detection import read_coverage_file
    
    # 1. Run your Python testbench (generates coverage file)
    # 2. Import coverage
    db = read_coverage_file('coverage.xml')
    
    # 3. Analyze
    from ucis.scope_type_t import ScopeTypeT
    
    covergroups = [s for s in db.scopes(-1) 
                   if s.getScopeType() == ScopeTypeT.COVERGROUP]
    print(f"Found {len(covergroups)} covergroups")

Merging Multiple Runs
---------------------

.. code-block:: python

    from ucis.format_detection import read_coverage_file
    from ucis.sqlite.sqlite_ucis import SqliteUCIS
    
    # Import multiple coverage files
    db1 = read_coverage_file('test1_coverage.xml')
    db2 = read_coverage_file('test2_coverage.yml')
    db3 = read_coverage_file('test3_coverage.json')
    
    # (Merging would use PyUCIS merge capabilities)
    # Note: Full merge workflow depends on PyUCIS backend

Mixed Format Import
-------------------

Import from multiple frameworks in the same workflow:

.. code-block:: python

    from ucis.format_detection import read_coverage_file
    
    # Import cocotb coverage
    cocotb_db = read_coverage_file('cocotb_coverage.xml')
    
    # Import AVL coverage  
    avl_db = read_coverage_file('avl_coverage.json')
    
    # Both are now in UCIS format and can be analyzed uniformly

Coverage Hierarchy
==================

All importers create standard UCIS hierarchy:

.. code-block:: text

    UCIS Database (root)
    └── DU_MODULE (design unit)
        └── INSTANCE
            └── COVERGROUP
                ├── COVERPOINT
                │   └── Bins (via coverItems())
                └── CROSS (cross coverage)
                    └── Bins (via coverItems())

Accessing Coverage Data
-----------------------

.. code-block:: python

    from ucis.format_detection import read_coverage_file
    from ucis.scope_type_t import ScopeTypeT
    
    db = read_coverage_file('coverage.xml')
    
    # Find all coverpoints
    def find_coverpoints(scope, found=None):
        if found is None:
            found = []
        if scope.getScopeType() == ScopeTypeT.COVERPOINT:
            found.append(scope)
        for child in scope.scopes(-1):
            find_coverpoints(child, found)
        return found
    
    # Access bins
    coverpoints = find_coverpoints(db)
    for cp in coverpoints:
        bins = list(cp.coverItems(-1))  # Get bins
        print(f"Coverpoint {cp.getScopeName()}: {len(bins)} bins")
        
        for bin_item in bins:
            name = bin_item.getName()
            count = bin_item.getCoverData().data  # Hit count
            print(f"  {name}: {count} hits")

Advanced Usage
==============

Custom Import Processing
------------------------

Process coverage data during import:

.. code-block:: python

    from ucis.cocotb import CocotbXmlReader
    from ucis.sqlite.sqlite_ucis import SqliteUCIS
    
    # Create custom database
    db = SqliteUCIS('custom.ucisdb')
    
    # Import with custom processing
    reader = CocotbXmlReader()
    reader.read('coverage.xml', db)
    
    # Database now contains imported coverage

Filtering Coverage
------------------

.. code-block:: python

    from ucis.format_detection import read_coverage_file
    from ucis.scope_type_t import ScopeTypeT
    
    db = read_coverage_file('coverage.xml')
    
    # Find uncovered bins
    def find_uncovered_bins(scope):
        uncovered = []
        if scope.getScopeType() in [ScopeTypeT.COVERPOINT, ScopeTypeT.CROSS]:
            bins = list(scope.coverItems(-1))
            for bin_item in bins:
                if bin_item.getCoverData().data == 0:
                    uncovered.append((scope.getScopeName(), bin_item.getName()))
        
        for child in scope.scopes(-1):
            uncovered.extend(find_uncovered_bins(child))
        return uncovered
    
    uncovered = find_uncovered_bins(db)
    print(f"Uncovered bins: {len(uncovered)}")
    for cp_name, bin_name in uncovered[:5]:
        print(f"  {cp_name}.{bin_name}")

Implementation Details
======================

Architecture
------------

The import implementation consists of:

**cocotb Module** (``src/ucis/cocotb/``):
  * ``cocotb_xml_reader.py`` - XML parser (326 lines)
  * ``cocotb_yaml_reader.py`` - YAML parser (309 lines)

**AVL Module** (``src/ucis/avl/``):
  * ``avl_json_reader.py`` - JSON parser with DataFrame support (315 lines)

**Format Detection** (``src/ucis/format_detection.py``):
  * Automatic format detection (257 lines)
  * Unified import interface

The import process:

.. code-block:: text

    Coverage file (XML/YAML/JSON)
           ↓
    Format Detection (identify type)
           ↓
    Appropriate Reader (parse format)
           ↓
    UCIS Database (in-memory)
           ↓
    Export (XML, SQLite, etc.)

Testing
-------

The implementation includes comprehensive tests:

* **34 unit tests** covering all format variations
* **XML/YAML equivalence validation**
* **DataFrame format variations**
* **End-to-end integration tests**

**Test Coverage**: 100% (34/34 tests passing)

Limitations
===========

Current Limitations
-------------------

* **Read-Only**: Import only (no export to cocotb/AVL formats)
* **In-Memory**: Coverage data loaded into memory during parsing
* **Source Locations**: Not preserved (cocotb/AVL don't provide detailed source info)

These limitations do not affect typical usage scenarios.

Troubleshooting
===============

Common Issues
-------------

**Format not detected automatically**
    Ensure file has correct extension (``.xml``, ``.yml``, ``.json``) and valid content

**Import fails with parsing error**
    Verify the file was generated by cocotb-coverage or AVL

**Empty coverage database**
    Check that the input file contains coverage data, not just metadata

**Missing bins**
    Use ``coverItems(-1)`` not ``scopes(-1)`` to access bins from coverpoints

See Also
========

* :doc:`commands` - PyUCIS command-line interface
* :doc:`verilator_coverage_import` - Verilator coverage import
* :doc:`reference/html_coverage_report` - HTML report generation
* `cocotb-coverage <https://github.com/mciepluc/cocotb-coverage>`_ - cocotb coverage library
* `AVL <https://github.com/projectapheleia/avl>`_ - Apheleia Verification Library

References
==========

* **cocotb**: https://github.com/cocotb/cocotb
* **cocotb-coverage**: https://github.com/mciepluc/cocotb-coverage
* **AVL**: https://github.com/projectapheleia/avl
* **UCIS Specification**: IEEE 1800.2
