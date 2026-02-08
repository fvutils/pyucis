##########################
SQLite Backend API
##########################

The SQLite backend provides persistent, queryable storage for UCIS coverage data using SQLite3 databases. It offers a complete implementation of the UCIS Python API with efficient lazy loading, property caching, and transaction support.

********
Overview
********

Features
========

* **Persistent Storage** - Coverage data saved directly to SQLite database files (.ucisdb)
* **Full API Compatibility** - Drop-in replacement for in-memory and libucis implementations
* **Lazy Loading** - Memory-efficient loading of large databases
* **Transaction Support** - Atomic operations with rollback capability
* **Property System** - Complete int/real/string/handle property storage
* **Hierarchical Queries** - Efficient scope and coverage iteration with filtering
* **Test Tracking** - History node management with complete metadata
* **Source Information** - File and line number tracking for all coverage items
* **Type Filtering** - Scope and coverage type mask filtering for targeted queries

Architecture
============

The SQLite backend implements a comprehensive relational database schema that captures all UCIS concepts:

* **15 normalized tables** with full referential integrity
* **30+ indexes** for optimized query performance
* **Foreign key constraints** for data consistency
* **WAL mode** for concurrent read access
* **Prepared statements** for efficient repeated operations

*************
Quick Start
*************

Creating a Database
===================

.. code-block:: python

    from ucis.sqlite import SqliteUCIS
    from ucis.scope_type_t import ScopeTypeT
    from ucis.source_t import SourceT
    from ucis.cover_data import CoverData
    from ucis.history_node_kind import HistoryNodeKind

    # Create or open database
    ucis = SqliteUCIS("coverage.ucisdb")
    
    # Build design hierarchy
    top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
    dut = top.createScope("dut", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
    
    # Add coverage item
    cover_data = CoverData(0x01, 0)  # CVGBIN type
    cover_data.data = 100  # Hit count
    bin1 = dut.createNextCover("bin1", cover_data, None)
    
    # Create test record
    test = ucis.createHistoryNode(None, "test1", "test1.sv", HistoryNodeKind.TEST)
    test.setSeed("12345")
    
    # Save and close
    ucis.close()

Querying Coverage
=================

.. code-block:: python

    # Reopen database
    ucis = SqliteUCIS("coverage.ucisdb")
    
    # Iterate through hierarchy
    for scope in ucis.scopes(ScopeTypeT.INSTANCE):
        print(f"Scope: {scope.getScopeName()}")
        for cover in scope.coverItems(-1):
            print(f"  {cover.getName()}: {cover.getCoverData().data} hits")
    
    # Access history
    print(f"Number of tests: {ucis.getNumTests()}")
    for test in ucis.historyNodes(HistoryNodeKind.TEST):
        print(f"Test: {test.getLogicalName()}")
    
    ucis.close()

Using Transactions
==================

.. code-block:: python

    ucis = SqliteUCIS("coverage.ucisdb")
    
    # Begin transaction for bulk operations
    ucis.begin_transaction()
    try:
        # Create multiple scopes efficiently
        for i in range(1000):
            scope = top.createScope(f"module_{i}", None, 1, 
                                   SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        ucis.commit()
    except Exception as e:
        ucis.rollback()
        raise
    
    ucis.close()

*************
API Reference
*************

SqliteUCIS Class
================

Main database class providing UCIS root functionality.

Constructor
-----------

.. py:class:: SqliteUCIS(db_path: str = None)

   Create or open a SQLite UCIS database.
   
   :param db_path: Path to database file. If None, creates in-memory database.
   :type db_path: str or None

Database Management
-------------------

.. py:method:: close()

   Close the database connection. Commits any pending changes.

.. py:method:: write(filename: str)

   Write database to a file (for in-memory databases).
   
   :param filename: Target file path
   :type filename: str

.. py:method:: isModified() -> bool

   Check if database has been modified since last write.
   
   :return: True if modified

Metadata Operations
-------------------

.. py:method:: getAPIVersion() -> str

   Get UCIS API version.
   
   :return: Version string (e.g., "1.0")

.. py:method:: getWrittenBy() -> str
              setWrittenBy(by: str)

   Get or set the tool/user that wrote the database.

.. py:method:: getWrittenTime() -> int
              setWrittenTime(time: int)

   Get or set the timestamp when database was written.

.. py:method:: getPathSeparator() -> str
              setPathSeparator(sep: str)

   Get or set the path separator character (default: '/').

Test Management
---------------

.. py:method:: getNumTests() -> int

   Get the total number of test history nodes.
   
   :return: Number of tests

.. py:method:: createHistoryNode(parent, logicalname: str, physicalname: str = None, kind: HistoryNodeKind = None) -> HistoryNode

   Create a new test history node.
   
   :param parent: Parent history node or None for root
   :param logicalname: Logical test name
   :param physicalname: Physical file path (optional)
   :param kind: History node kind (TEST, MERGE, etc.)
   :return: New history node

.. py:method:: historyNodes(kind: HistoryNodeKind = None) -> Iterator[HistoryNode]

   Iterate over history nodes, optionally filtered by kind.
   
   :param kind: Filter by kind (None for all)
   :return: Iterator of history nodes

File Management
---------------

.. py:method:: createFileHandle(filename: str, workdir: str = None) -> FileHandle

   Create or retrieve a file handle for source file tracking.
   
   :param filename: Source file path
   :param workdir: Working directory (optional)
   :return: File handle

Transaction Control
-------------------

.. py:method:: begin_transaction()

   Begin a database transaction for bulk operations.

.. py:method:: commit()

   Commit the current transaction.

.. py:method:: rollback()

   Rollback the current transaction.

SqliteScope Class
=================

Hierarchical coverage container class.

Scope Creation
--------------

.. py:method:: createScope(name: str, srcinfo, weight: int, source: SourceT, type: ScopeTypeT, flags: int) -> Scope

   Create a child scope.
   
   :param name: Scope name
   :param srcinfo: Source information (SourceInfo or None)
   :param weight: Coverage weight
   :param source: Source type
   :param type: Scope type (INSTANCE, BRANCH, COVERGROUP, etc.)
   :param flags: Scope flags
   :return: New scope

.. py:method:: createInstance(name: str, fileinfo, weight: int, source: SourceT, type: ScopeTypeT, du_scope, flags: int) -> Scope

   Create an instance scope (convenience method).
   
   :param name: Instance name
   :param fileinfo: File information
   :param weight: Coverage weight
   :param source: Source type
   :param type: Scope type
   :param du_scope: Design unit scope
   :param flags: Instance flags
   :return: New instance scope

.. py:method:: createToggle(name: str, canonical_name: str, flags: int, toggle_metric: int, toggle_type: int, toggle_dir: int) -> Scope

   Create a toggle coverage scope.
   
   :param name: Toggle name
   :param canonical_name: Canonical signal name
   :param flags: Toggle flags
   :param toggle_metric: Metric type
   :param toggle_type: Toggle type
   :param toggle_dir: Direction
   :return: New toggle scope

.. py:method:: createCovergroup(name: str, srcinfo, weight: int, source: SourceT) -> Scope

   Create a covergroup scope.
   
   :param name: Covergroup name
   :param srcinfo: Source information
   :param weight: Coverage weight
   :param source: Source type
   :return: New covergroup scope

Coverage Item Creation
----------------------

.. py:method:: createNextCover(name: str, data: CoverData, sourceinfo) -> CoverIndex

   Create the next coverage item in this scope.
   
   :param name: Coverage item name
   :param data: Coverage data (type and count)
   :param sourceinfo: Source information
   :return: New coverage item

Scope Properties
----------------

.. py:method:: getScopeName() -> str

   Get the scope name.

.. py:method:: getScopeType() -> ScopeTypeT

   Get the scope type.

.. py:method:: getFlags() -> int

   Get scope flags.

.. py:method:: getWeight() -> int
              setWeight(weight: int)

   Get or set coverage weight.

.. py:method:: getGoal() -> int
              setGoal(goal: int)

   Get or set coverage goal percentage.

.. py:method:: getSourceInfo() -> SourceInfo

   Get source information (file, line, token).

Iteration
---------

.. py:method:: scopes(mask: ScopeTypeT = -1) -> Iterator[Scope]

   Iterate over child scopes, optionally filtered by type.
   
   :param mask: Scope type mask (bitwise OR of types, -1 for all)
   :return: Iterator of child scopes

.. py:method:: coverItems(mask: int = -1) -> Iterator[CoverIndex]

   Iterate over coverage items, optionally filtered by type.
   
   :param mask: Coverage type mask (-1 for all)
   :return: Iterator of coverage items

SqliteCoverIndex Class
======================

Coverage item with hit count and metadata.

Coverage Data Access
--------------------

.. py:method:: getName() -> str

   Get coverage item name.

.. py:method:: getCoverData() -> CoverData

   Get coverage data structure.
   
   :return: CoverData with type and count

.. py:method:: getCount() -> int
              setCount(count: int)

   Get or set hit count.

.. py:method:: incrementCover(amount: int = 1)

   Increment hit count by specified amount.
   
   :param amount: Amount to increment (default: 1)

Coverage Source Information
---------------------------

.. py:method:: getSourceInfo() -> SourceInfo

   Get source file location for this coverage item.

SqliteHistoryNode Class
=======================

Test record with execution metadata.

Identification
--------------

.. py:method:: getLogicalName() -> str
              setLogicalName(name: str)

   Get or set logical test name.

.. py:method:: getPhysicalName() -> str
              setPhysicalName(name: str)

   Get or set physical file path.

.. py:method:: getKind() -> HistoryNodeKind

   Get history node kind (TEST, MERGE, TESTPLAN).

Test Status
-----------

.. py:method:: getTestStatus() -> TestStatusT
              setTestStatus(status: TestStatusT)

   Get or set test execution status (OK, WARNING, FATAL).

Timing Information
------------------

.. py:method:: getSimTime() -> float
              setSimTime(time: float)

   Get or set simulation time.

.. py:method:: getCpuTime() -> float
              setCpuTime(time: float)

   Get or set CPU execution time.

Test Metadata
-------------

.. py:method:: getSeed() -> str
              setSeed(seed: str)

   Get or set random seed.

.. py:method:: getCmd() -> str
              setCmd(cmd: str)

   Get or set command line.

.. py:method:: getDate() -> int
              setDate(date: int)

   Get or set execution date (Unix timestamp).

.. py:method:: getUserName() -> str
              setUserName(user: str)

   Get or set user name.

.. py:method:: getCost() -> int
              setCost(cost: int)

   Get or set test cost metric.

Property System
===============

All SQLite objects support the UCIS property system for extensible metadata.

Integer Properties
------------------

.. py:method:: setIntProperty(key: IntProperty, value: int)

   Set an integer property.

.. py:method:: getIntProperty(key: IntProperty) -> int

   Get an integer property value.

String Properties
-----------------

.. py:method:: setStringProperty(key: int, value: str)

   Set a string property.

.. py:method:: getStringProperty(key: int) -> str

   Get a string property value.

Real Properties
---------------

.. py:method:: setRealProperty(key: int, value: float)

   Set a real (floating point) property.

.. py:method:: getRealProperty(key: int) -> float

   Get a real property value.

Handle Properties
-----------------

.. py:method:: setHandleProperty(key: int, value)

   Set a handle property (reference to another object).

.. py:method:: getHandleProperty(key: int)

   Get a handle property value.

************
Performance
************

Optimization Strategies
=======================

The SQLite backend is optimized for both read and write performance:

**Lazy Loading**
   Objects are loaded from database only when accessed, minimizing memory usage.

**Property Caching**
   Frequently-accessed properties are cached in memory to reduce database queries.

**Indexed Queries**
   Strategic indexes on common query patterns (parent_id, type, name combinations).

**WAL Mode**
   Write-Ahead Logging enables concurrent read access during writes.

**Transaction Support**
   Bulk operations can be wrapped in transactions for significant speedup.

**Prepared Statements**
   Common queries use prepared statements for reduced parsing overhead.

Typical Performance
===================

Database sizes:

* Small (10 scopes, 50 bins, 5 tests): ~100 KB
* Medium (100 scopes, 500 bins, 20 tests): ~500 KB  
* Large (1000 scopes, 5000 bins, 100 tests): ~5 MB
* Very Large (10k scopes, 50k bins, 500 tests): ~50 MB

Operation speeds (on modern hardware):

* Scope creation: ~10,000 scopes/second
* Coverage item creation: ~20,000 items/second
* Iteration: ~50,000 items/second
* Property access (cached): ~1,000,000 reads/second
* Property access (uncached): ~100,000 reads/second

Best Practices
==============

1. **Use transactions for bulk operations**
   
   Wrap large batches of creates/updates in begin_transaction()/commit()

2. **Close databases when done**
   
   Always call close() to ensure all changes are flushed

3. **Filter iterations when possible**
   
   Use type masks to reduce iteration overhead

4. **Cache frequently-accessed objects**
   
   Store scope/cover references rather than re-querying

5. **Use in-memory for temporary work**
   
   Create with db_path=None, write to file when complete

****************
Database Format
****************

File Extension
==============

SQLite databases use the ``.ucisdb`` extension by convention, though any extension works.

Compatibility
=============

* SQLite version: 3.31.0 or later recommended
* Schema version: 1.0
* Python version: 3.7+
* No external dependencies beyond Python's built-in sqlite3 module

Direct SQL Access
=================

SQLite databases can be queried directly using standard SQLite tools:

.. code-block:: bash

    # Open with sqlite3 command-line tool
    sqlite3 coverage.ucisdb
    
    # Run queries
    SELECT scope_name, scope_type FROM scopes WHERE parent_id IS NULL;
    
    # Export to CSV
    .mode csv
    .output coveritems.csv
    SELECT * FROM coveritems;

For detailed schema information, see :doc:`sqlite_schema_reference`.

Migration
=========

Converting from other formats:

.. code-block:: python

    # From XML
    from ucis.xml import XMLUCIS
    from ucis.sqlite import SqliteUCIS
    
    xml_db = XMLUCIS("old.xml")
    sqlite_db = SqliteUCIS("new.ucisdb")
    # Copy logic here
    
    # From YAML
    from ucis.yaml import YAMLUCIS
    yaml_db = YAMLUCIS("old.yaml")
    # Copy to sqlite_db

********
Examples
********

Complete Example
================

.. code-block:: python

    from ucis.sqlite import SqliteUCIS
    from ucis.scope_type_t import ScopeTypeT
    from ucis.source_t import SourceT
    from ucis.cover_data import CoverData
    from ucis.history_node_kind import HistoryNodeKind
    from ucis.test_status_t import TestStatusT
    
    # Create database
    ucis = SqliteUCIS("example.ucisdb")
    
    # Build hierarchy
    top = ucis.createScope("top", None, 1, SourceT.NONE, 
                          ScopeTypeT.INSTANCE, 0)
    dut = top.createScope("dut", None, 1, SourceT.NONE,
                         ScopeTypeT.INSTANCE, 0)
    
    # Create covergroup
    cg = dut.createCovergroup("addr_cg", None, 1, SourceT.NONE)
    cp = cg.createScope("addr_cp", None, 1, SourceT.NONE,
                       ScopeTypeT.COVERPOINT, 0)
    
    # Add bins
    for i, name in enumerate(["low", "mid", "high"]):
        data = CoverData(0x01, 0)  # CVGBIN
        data.data = 10 * (i + 1)
        cp.createNextCover(name, data, None)
    
    # Create test
    test = ucis.createHistoryNode(None, "test_basic", 
                                 "test_basic.sv", 
                                 HistoryNodeKind.TEST)
    test.setTestStatus(TestStatusT.OK)
    test.setSeed("424242")
    test.setSimTime(1000.0)
    
    # Query results
    print(f"Tests: {ucis.getNumTests()}")
    for scope in ucis.scopes(ScopeTypeT.INSTANCE):
        print(f"Instance: {scope.getScopeName()}")
    
    ucis.close()

See Also
========

* :doc:`sqlite_schema_reference` - Detailed SQL schema documentation
* :doc:`ucis_oo_api` - Object-oriented API reference
* :doc:`recording_coverage_best_practices` - General best practices
