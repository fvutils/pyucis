##########################
Native C Library API
##########################

The PyUCIS Native C Library provides a complete implementation of the UCIS 1.0 C API using SQLite3 as the backend storage. This native library can be used directly from C/C++ applications or through Python's ctypes interface.

********
Overview
********

Features
========

* **UCIS 1.0 Standard Compliant** - Full implementation of the official C API
* **SQLite3 Backend** - Persistent, queryable storage with SQL access
* **High Performance** - Optimized with prepared statements and caching
* **Thread-Safe** - Can be used in multi-threaded applications
* **Cross-Platform** - Builds on Linux, macOS, and Windows
* **Python Integration** - Can be loaded via ctypes from Python

Architecture
============

**Opaque Handles**
   All API types are opaque pointers backed by an internal handle table for type safety.

**Prepared Statements**
   Frequently-used SQL queries are prepared once and cached for performance.

**Foreign Keys**
   Referential integrity enforced at the database level.

**WAL Mode**
   Write-Ahead Logging enabled for better concurrency.

**Handle Caching**
   Frequently-accessed data cached in handle entries to minimize database queries.

************
Building
************

Requirements
============

* C compiler (GCC, Clang, or MSVC)
* CMake 3.10 or later
* SQLite3 (included as amalgamation)

Build Steps
===========

.. code-block:: bash

    # Navigate to native directory
    cd src/native
    
    # Build with CMake
    mkdir build
    cd build
    cmake ..
    make
    
    # Or use make directly
    cd src/native
    make
    
    # Install library (optional)
    sudo make install

Build Outputs
=============

* **libucis.so** (Linux) - Shared library
* **libucis.dylib** (macOS) - Shared library  
* **ucis.dll** (Windows) - Dynamic link library
* **libucis.a** - Static library (optional)

Testing
=======

.. code-block:: bash

    # Run test suite
    make test
    
    # Or run individual tests
    cd test
    python3 test_basic.py
    python3 test_scopes.py

*************
API Reference
*************

Database Lifecycle
==================

ucis_Open
---------

.. c:function:: ucisT ucis_Open(const char* name)

   Open or create a UCIS database.
   
   :param name: File path or NULL for in-memory database
   :return: Database handle or NULL on error
   
   **Example:**
   
   .. code-block:: c
   
       ucisT db = ucis_Open("coverage.ucisdb");
       if (!db) {
           fprintf(stderr, "Error: %s\n", ucis_GetLastError());
           return 1;
       }

ucis_Close
----------

.. c:function:: void ucis_Close(ucisT db)

   Close a UCIS database and free all resources.
   
   :param db: Database handle
   
   **Example:**
   
   .. code-block:: c
   
       ucis_Close(db);

ucis_Write
----------

.. c:function:: int ucis_Write(ucisT db, const char* name)

   Write database to a file (useful for in-memory databases).
   
   :param db: Database handle
   :param name: Target file path
   :return: 0 on success, non-zero on error
   
   **Example:**
   
   .. code-block:: c
   
       if (ucis_Write(db, "output.ucisdb") != 0) {
           fprintf(stderr, "Write failed: %s\n", ucis_GetLastError());
       }

ucis_GetAPIVersion
------------------

.. c:function:: const char* ucis_GetAPIVersion(void)

   Get UCIS API version string.
   
   :return: Version string (e.g., "1.0")
   
   **Example:**
   
   .. code-block:: c
   
       printf("UCIS API Version: %s\n", ucis_GetAPIVersion());

ucis_GetLastError
-----------------

.. c:function:: const char* ucis_GetLastError(void)

   Get the last error message from any UCIS operation.
   
   :return: Error message string or NULL if no error
   
   **Example:**
   
   .. code-block:: c
   
       if (!db) {
           fprintf(stderr, "Error: %s\n", ucis_GetLastError());
       }

Scope Operations
================

ucis_CreateScope
----------------

.. c:function:: ucisScopeT ucis_CreateScope(ucisT db, ucisScopeT parent, const char* name, ucisSourceInfoT* source, int weight, ucisSourceT source_type, ucisScopeTypeT type, int flags)

   Create a new scope in the hierarchy.
   
   :param db: Database handle
   :param parent: Parent scope or NULL for root-level scope
   :param name: Scope name
   :param source: Source location info or NULL
   :param weight: Coverage weight (typically 1)
   :param source_type: Source type (UCIS_VHDL, UCIS_VLOG, etc.)
   :param type: Scope type (UCIS_INSTANCE, UCIS_COVERGROUP, etc.)
   :param flags: Scope flags (coverage enables, UOR flags)
   :return: New scope handle or NULL on error
   
   **Example:**
   
   .. code-block:: c
   
       // Create top-level instance
       ucisScopeT top = ucis_CreateScope(
           db,
           NULL,               // No parent
           "top",
           NULL,               // No source info
           1,                  // Weight
           UCIS_VLOG,
           UCIS_INSTANCE,
           0                   // No flags
       );

ucis_CreateInstance
-------------------

.. c:function:: ucisScopeT ucis_CreateInstance(ucisT db, ucisScopeT parent, const char* name, ucisSourceInfoT* source, int weight, ucisSourceT source_type)

   Create an instance scope (convenience wrapper).
   
   :param db: Database handle
   :param parent: Parent scope
   :param name: Instance name
   :param source: Source location or NULL
   :param weight: Coverage weight
   :param source_type: Source type
   :return: New instance scope or NULL on error
   
   **Example:**
   
   .. code-block:: c
   
       ucisScopeT dut = ucis_CreateInstance(db, top, "dut", NULL, 1, UCIS_VLOG);

ucis_GetScopeName
-----------------

.. c:function:: const char* ucis_GetScopeName(ucisT db, ucisScopeT scope)

   Get the name of a scope.
   
   :param db: Database handle
   :param scope: Scope handle
   :return: Scope name or NULL on error
   
   **Example:**
   
   .. code-block:: c
   
       const char* name = ucis_GetScopeName(db, scope);
       printf("Scope name: %s\n", name);

ucis_GetScopeType
-----------------

.. c:function:: ucisScopeTypeT ucis_GetScopeType(ucisT db, ucisScopeT scope)

   Get the type of a scope.
   
   :param db: Database handle
   :param scope: Scope handle
   :return: Scope type flags
   
   **Example:**
   
   .. code-block:: c
   
       ucisScopeTypeT type = ucis_GetScopeType(db, scope);
       if (type & UCIS_INSTANCE) {
           printf("This is an instance\n");
       }

ucis_GetParent
--------------

.. c:function:: ucisScopeT ucis_GetParent(ucisT db, ucisScopeT scope)

   Get the parent scope.
   
   :param db: Database handle
   :param scope: Scope handle
   :return: Parent scope handle or NULL if root
   
   **Example:**
   
   .. code-block:: c
   
       ucisScopeT parent = ucis_GetParent(db, scope);
       if (parent) {
           printf("Parent: %s\n", ucis_GetScopeName(db, parent));
       }

ucis_SetScopeWeight
-------------------

.. c:function:: int ucis_SetScopeWeight(ucisT db, ucisScopeT scope, int weight)

   Set the coverage weight of a scope.
   
   :param db: Database handle
   :param scope: Scope handle
   :param weight: New weight value
   :return: 0 on success, non-zero on error

ucis_SetScopeGoal
-----------------

.. c:function:: int ucis_SetScopeGoal(ucisT db, ucisScopeT scope, int goal)

   Set the coverage goal percentage.
   
   :param db: Database handle
   :param scope: Scope handle
   :param goal: Goal percentage (0-100)
   :return: 0 on success, non-zero on error

ucis_SetScopeFlags
------------------

.. c:function:: int ucis_SetScopeFlags(ucisT db, ucisScopeT scope, int flags)

   Set scope flags.
   
   :param db: Database handle
   :param scope: Scope handle
   :param flags: Flag bits (coverage enables, UOR flags)
   :return: 0 on success, non-zero on error

ucis_ScopeIterate
-----------------

.. c:function:: int ucis_ScopeIterate(ucisT db, ucisScopeT parent, ucisScopeTypeT type_mask, ucisScopeCBT callback, void* userdata)

   Iterate over child scopes with optional type filtering.
   
   :param db: Database handle
   :param parent: Parent scope or NULL for root-level scopes
   :param type_mask: Scope type filter (bitwise OR of types, -1 for all)
   :param callback: Callback function called for each scope
   :param userdata: User data passed to callback
   :return: 0 on success, non-zero on error
   
   **Callback signature:**
   
   .. code-block:: c
   
       typedef int (*ucisScopeCBT)(void* userdata, ucisScopeT scope);
   
   **Example:**
   
   .. code-block:: c
   
       int print_scope(void* userdata, ucisScopeT scope) {
           ucisT db = (ucisT)userdata;
           printf("Scope: %s\n", ucis_GetScopeName(db, scope));
           return 0;  // Continue iteration
       }
       
       // Iterate all child scopes
       ucis_ScopeIterate(db, parent, -1, print_scope, db);
       
       // Iterate only instances
       ucis_ScopeIterate(db, parent, UCIS_INSTANCE, print_scope, db);

Coverage Operations
===================

ucis_CreateNextCover
--------------------

.. c:function:: ucisCoverT ucis_CreateNextCover(ucisT db, ucisScopeT parent, const char* name, ucisCoverDataT* data, ucisSourceInfoT* source)

   Create the next coverage item in a scope.
   
   :param db: Database handle
   :param parent: Parent scope
   :param name: Coverage item name
   :param data: Coverage data (type and initial count)
   :param source: Source location or NULL
   :return: New coverage item handle or NULL on error
   
   **Example:**
   
   .. code-block:: c
   
       ucisCoverDataT data = {0};
       data.type = UCIS_CVGBIN;
       data.data = 0;  // Initial count
       
       ucisCoverT bin = ucis_CreateNextCover(db, coverpoint, "low", &data, NULL);

ucis_GetCoverData
-----------------

.. c:function:: int ucis_GetCoverData(ucisT db, ucisCoverT cover, ucisCoverDataT* data)

   Get coverage data for an item.
   
   :param db: Database handle
   :param cover: Coverage item handle
   :param data: Output parameter for coverage data
   :return: 0 on success, non-zero on error
   
   **Example:**
   
   .. code-block:: c
   
       ucisCoverDataT data;
       if (ucis_GetCoverData(db, cover, &data) == 0) {
           printf("Hit count: %d\n", data.data);
       }

ucis_SetCoverData
-----------------

.. c:function:: int ucis_SetCoverData(ucisT db, ucisCoverT cover, ucisCoverDataT* data)

   Set coverage data for an item.
   
   :param db: Database handle
   :param cover: Coverage item handle
   :param data: New coverage data
   :return: 0 on success, non-zero on error

ucis_IncrementCoverData
------------------------

.. c:function:: int ucis_IncrementCoverData(ucisT db, ucisCoverT cover, int amount)

   Increment coverage count.
   
   :param db: Database handle
   :param cover: Coverage item handle
   :param amount: Amount to increment (default: 1)
   :return: 0 on success, non-zero on error
   
   **Example:**
   
   .. code-block:: c
   
       // Increment by 1
       ucis_IncrementCoverData(db, cover, 1);

ucis_CoverIterate
-----------------

.. c:function:: int ucis_CoverIterate(ucisT db, ucisScopeT parent, ucisCoverTypeT type_mask, ucisCoverCBT callback, void* userdata)

   Iterate over coverage items in a scope.
   
   :param db: Database handle
   :param parent: Parent scope
   :param type_mask: Coverage type filter (-1 for all)
   :param callback: Callback function
   :param userdata: User data passed to callback
   :return: 0 on success, non-zero on error
   
   **Callback signature:**
   
   .. code-block:: c
   
       typedef int (*ucisCoverCBT)(void* userdata, ucisCoverT cover);

History Operations
==================

ucis_CreateHistoryNode
-----------------------

.. c:function:: ucisHistoryNodeT ucis_CreateHistoryNode(ucisT db, ucisHistoryNodeT parent, const char* logicalname, const char* physicalname, ucisHistoryNodeKindT kind)

   Create a test history node.
   
   :param db: Database handle
   :param parent: Parent history node or NULL
   :param logicalname: Logical test name
   :param physicalname: Physical file path or NULL
   :param kind: History node kind (TEST, MERGE, TESTPLAN)
   :return: New history node handle or NULL on error

ucis_SetTestStatus
------------------

.. c:function:: int ucis_SetTestStatus(ucisT db, ucisHistoryNodeT node, ucisTestStatusT status)

   Set test execution status.
   
   :param db: Database handle
   :param node: History node handle
   :param status: Test status (OK, WARNING, FATAL)
   :return: 0 on success, non-zero on error

ucis_HistoryNodeIterate
------------------------

.. c:function:: int ucis_HistoryNodeIterate(ucisT db, ucisHistoryNodeKindT kind_mask, ucisHistoryNodeCBT callback, void* userdata)

   Iterate over history nodes.
   
   :param db: Database handle
   :param kind_mask: Kind filter (-1 for all)
   :param callback: Callback function
   :param userdata: User data
   :return: 0 on success, non-zero on error

*****************
Type Definitions
*****************

Opaque Handle Types
===================

.. code-block:: c

    typedef struct ucis_s* ucisT;                    // Database handle
    typedef struct ucis_scope_s* ucisScopeT;         // Scope handle
    typedef struct ucis_cover_s* ucisCoverT;         // Coverage item handle
    typedef struct ucis_history_s* ucisHistoryNodeT; // History node handle

Scope Types
===========

.. code-block:: c

    typedef enum {
        UCIS_TOGGLE        = 0x0001,   // Toggle coverage
        UCIS_BRANCH        = 0x0002,   // Branch coverage
        UCIS_EXPR          = 0x0004,   // Expression coverage
        UCIS_COND          = 0x0008,   // Condition coverage
        UCIS_INSTANCE      = 0x0010,   // Design instance
        UCIS_DU_MODULE     = 0x0020,   // Module design unit
        UCIS_DU_ARCH       = 0x0040,   // Architecture design unit
        UCIS_COVERGROUP    = 0x1000,   // Covergroup type
        UCIS_COVERINSTANCE = 0x2000,   // Covergroup instance
        UCIS_COVERPOINT    = 0x4000,   // Coverpoint
        UCIS_CROSS         = 0x8000,   // Cross coverage
        UCIS_FSM           = 0x400000, // Finite state machine
        UCIS_ASSERT        = 0x800000  // Assertion
    } ucisScopeTypeT;

Coverage Types
==============

.. code-block:: c

    typedef enum {
        UCIS_CVGBIN     = 0x0001,   // Covergroup bin
        UCIS_STMTBIN    = 0x0002,   // Statement
        UCIS_BRANCHBIN  = 0x0004,   // Branch
        UCIS_EXPRBIN    = 0x0008,   // Expression
        UCIS_CONDBIN    = 0x0010,   // Condition
        UCIS_TOGGLEBIN  = 0x0200,   // Toggle
        UCIS_ASSERTBIN  = 0x0400,   // Assertion
        UCIS_FSMBIN     = 0x0800,   // FSM state/transition
        UCIS_IGNOREBIN  = 0x80000,  // Ignore bin
        UCIS_ILLEGALBIN = 0x100000, // Illegal bin
        UCIS_DEFAULTBIN = 0x200000  // Default bin
    } ucisCoverTypeT;

Coverage Data
=============

.. code-block:: c

    typedef struct {
        ucisCoverTypeT type;  // Coverage type
        int data;             // Hit count
        int goal;             // Goal value
        int weight;           // Weight
        int at_least;         // Minimum count for coverage
    } ucisCoverDataT;

Source Information
==================

.. code-block:: c

    typedef struct {
        const char* file;  // Source file path
        int line;          // Line number
        int token;         // Token position
    } ucisSourceInfoT;

Source Types
============

.. code-block:: c

    typedef enum {
        UCIS_NONE = 0,
        UCIS_VHDL,
        UCIS_VLOG,
        UCIS_SV,
        UCIS_PSL,
        UCIS_E,
        UCIS_VERA
    } ucisSourceT;

Test Status
===========

.. code-block:: c

    typedef enum {
        UCIS_TESTSTATUS_OK = 0,      // Test passed
        UCIS_TESTSTATUS_WARNING = 1, // Test passed with warnings
        UCIS_TESTSTATUS_FATAL = 2    // Test failed
    } ucisTestStatusT;

History Node Kinds
==================

.. code-block:: c

    typedef enum {
        UCIS_HISTORYNODE_TEST = 0x01,     // Test run
        UCIS_HISTORYNODE_MERGE = 0x02,    // Merged coverage
        UCIS_HISTORYNODE_TESTPLAN = 0x04  // Test plan node
    } ucisHistoryNodeKindT;

******************
Complete Examples
******************

Basic Usage
===========

.. code-block:: c

    #include "ucis.h"
    #include <stdio.h>
    
    int main() {
        // Create database
        ucisT db = ucis_Open("example.ucisdb");
        if (!db) {
            fprintf(stderr, "Failed to open database\n");
            return 1;
        }
        
        // Create hierarchy
        ucisScopeT top = ucis_CreateInstance(db, NULL, "top", NULL, 1, UCIS_VLOG);
        ucisScopeT dut = ucis_CreateInstance(db, top, "dut", NULL, 1, UCIS_VLOG);
        
        // Create covergroup
        ucisScopeT cg = ucis_CreateScope(db, dut, "addr_cg", NULL, 1, 
                                         UCIS_SV, UCIS_COVERGROUP, 0);
        ucisScopeT cp = ucis_CreateScope(db, cg, "addr_cp", NULL, 1,
                                         UCIS_SV, UCIS_COVERPOINT, 0);
        
        // Add bins
        ucisCoverDataT data = {UCIS_CVGBIN, 0, 0, 1, 1};
        data.data = 25;
        ucis_CreateNextCover(db, cp, "low", &data, NULL);
        
        data.data = 50;
        ucis_CreateNextCover(db, cp, "high", &data, NULL);
        
        // Create test record
        ucisHistoryNodeT test = ucis_CreateHistoryNode(db, NULL, "test1", 
                                                       "test1.sv", 
                                                       UCIS_HISTORYNODE_TEST);
        ucis_SetTestStatus(db, test, UCIS_TESTSTATUS_OK);
        
        // Close database
        ucis_Close(db);
        
        return 0;
    }

Iterating Scopes
================

.. code-block:: c

    typedef struct {
        ucisT db;
        int depth;
    } IterCtx;
    
    int print_scope_cb(void* userdata, ucisScopeT scope) {
        IterCtx* ctx = (IterCtx*)userdata;
        
        // Print with indentation
        for (int i = 0; i < ctx->depth; i++) printf("  ");
        printf("%s (type=0x%x)\n", 
               ucis_GetScopeName(ctx->db, scope),
               ucis_GetScopeType(ctx->db, scope));
        
        // Recurse to children
        ctx->depth++;
        ucis_ScopeIterate(ctx->db, scope, -1, print_scope_cb, ctx);
        ctx->depth--;
        
        return 0;
    }
    
    void print_hierarchy(ucisT db) {
        IterCtx ctx = {db, 0};
        ucis_ScopeIterate(db, NULL, -1, print_scope_cb, &ctx);
    }

Using from Python
=================

.. code-block:: python

    import ctypes
    
    # Load library
    libucis = ctypes.CDLL("./libucis.so")
    
    # Define function signatures
    libucis.ucis_Open.argtypes = [ctypes.c_char_p]
    libucis.ucis_Open.restype = ctypes.c_void_p
    
    libucis.ucis_CreateInstance.argtypes = [
        ctypes.c_void_p,  # db
        ctypes.c_void_p,  # parent
        ctypes.c_char_p,  # name
        ctypes.c_void_p,  # source
        ctypes.c_int,     # weight
        ctypes.c_int      # source_type
    ]
    libucis.ucis_CreateInstance.restype = ctypes.c_void_p
    
    libucis.ucis_Close.argtypes = [ctypes.c_void_p]
    
    # Use the API
    db = libucis.ucis_Open(b"test.ucisdb")
    top = libucis.ucis_CreateInstance(db, None, b"top", None, 1, 2)  # UCIS_VLOG=2
    libucis.ucis_Close(db)

************
Performance
************

Optimization Tips
=================

1. **Use transactions for bulk operations:**

   .. code-block:: c
   
       sqlite3_exec(db_conn, "BEGIN TRANSACTION", NULL, NULL, NULL);
       // Create many scopes/covers
       sqlite3_exec(db_conn, "COMMIT", NULL, NULL, NULL);

2. **Cache handles when possible:**

   Store scope/cover handles rather than looking them up repeatedly.

3. **Use type masks in iteration:**

   Filter iterations to specific types to reduce overhead.

4. **Close database when done:**

   Call ucis_Close() to ensure all data is flushed.

Typical Performance
===================

* Scope creation: ~10,000 scopes/second
* Coverage item creation: ~20,000 items/second
* Iteration: ~50,000 items/second
* Handle lookup: ~1,000,000 lookups/second

**********
See Also
**********

* :doc:`sqlite_api` - Python SQLite API
* :doc:`sqlite_schema_reference` - SQL schema details
* :doc:`ucis_c_api` - General UCIS C API reference
