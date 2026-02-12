############################
SQLite Schema Reference
############################

This document provides a detailed reference of the SQLite database schema used by the SQLite backend. The schema is designed to efficiently represent all UCIS (Unified Coverage Interoperability Standard) concepts with full relational integrity.

*****************
Design Principles
*****************

The schema is designed with the following priorities:

1. **Efficient Merging** - Support for combining coverage data from multiple test runs
2. **Fast Querying** - Indexed access patterns for common operations
3. **API Compatibility** - Enable C API semantics through Python
4. **Relational Integrity** - Proper foreign key relationships with cascading deletes
5. **Storage Efficiency** - Normalized design with selective denormalization

Hierarchical Organization
==========================

UCIS organizes coverage data hierarchically:

* **Scopes** - Hierarchical containers (design units, instances, covergroups, etc.)
* **Coveritems** - Leaf nodes containing coverage counts
* **History Nodes** - Test records that produced coverage data

Object Identification
=====================

Objects can be identified by:

* **Hierarchical names** - Path-based identification (e.g., ``/top/module/signal``)
* **Unique IDs** - Type + name components for universal object recognition
* **Primary keys** - Integer IDs for efficient database operations

*********************
Schema Initialization
*********************

Database Pragmas
================

.. code-block:: sql

    -- Enable foreign key constraints
    PRAGMA foreign_keys = ON;
    
    -- Use Write-Ahead Logging for better concurrency
    PRAGMA journal_mode = WAL;
    
    -- Optimize for modern systems
    PRAGMA page_size = 4096;
    PRAGMA cache_size = -64000;  -- 64MB cache

Metadata Initialization
=======================

.. code-block:: sql

    INSERT INTO db_metadata (key, value) VALUES
        ('UCIS_VERSION', '1.0'),
        ('API_VERSION', '1.0'),
        ('PATH_SEPARATOR', '/'),
        ('CREATED_TIME', datetime('now'));

*****************
Table Reference
*****************

1. Database Metadata
====================

db_metadata
-----------

Stores database-level configuration and version information.

**Schema:**

.. code-block:: sql

    CREATE TABLE db_metadata (
        key TEXT PRIMARY KEY NOT NULL,
        value TEXT
    );
    
    CREATE INDEX idx_db_metadata_key ON db_metadata(key);

**Standard Keys:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Key
     - Description
   * - ``DATABASE_TYPE``
     - Database type identifier (always "PYUCIS")
   * - ``DATABASE_FORMAT_VERSION``
     - Database format version (current: "1.0")
   * - ``UCIS_VERSION``
     - UCIS standard version (e.g., "1.0")
   * - ``API_VERSION``
     - Implementation API version
   * - ``SCHEMA_VERSION``
     - Database schema version (current: "2.1")
   * - ``CREATED_TIME``
     - Database creation timestamp (ISO 8601)
   * - ``MODIFIED_TIME``
     - Last modification timestamp
   * - ``PATH_SEPARATOR``
     - Character used for path separation (default: '/')

**Database Identification:**

The ``DATABASE_TYPE`` key serves as a marker to identify PyUCIS coverage databases. This allows validation that a SQLite file is specifically a PyUCIS database rather than an arbitrary SQLite file.

**Example:**

.. code-block:: sql

    SELECT key, value FROM db_metadata;
    -- Result:
    -- DATABASE_TYPE           | PYUCIS
    -- DATABASE_FORMAT_VERSION | 1.0
    -- UCIS_VERSION            | 1.0
    -- API_VERSION             | 1.0
    -- SCHEMA_VERSION          | 2.1
    -- CREATED_TIME            | 2026-01-12T15:30:00

2. File Management
==================

files
-----

Tracks source files referenced by coverage objects.

**Schema:**

.. code-block:: sql

    CREATE TABLE files (
        file_id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT NOT NULL UNIQUE,
        file_hash TEXT,          -- Optional hash for version tracking
        file_table_id INTEGER    -- For multi-file design units (1-indexed)
    );
    
    CREATE INDEX idx_files_path ON files(file_path);
    CREATE INDEX idx_files_hash ON files(file_hash) WHERE file_hash IS NOT NULL;

**Columns:**

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Column
     - Type
     - Description
   * - file_id
     - INTEGER
     - Primary key (auto-increment)
   * - file_path
     - TEXT
     - File path (unique)
   * - file_hash
     - TEXT
     - Optional hash (MD5/SHA) for version tracking
   * - file_table_id
     - INTEGER
     - Multi-file compilation unit ID (1-indexed)

**Example:**

.. code-block:: sql

    INSERT INTO files (file_path, file_hash) 
    VALUES ('/project/rtl/counter.v', 'a1b2c3d4');
    
    SELECT file_id, file_path FROM files WHERE file_path LIKE '%.v';

3. Scope Hierarchy
==================

scopes
------

Hierarchical coverage containers representing design structure, coverage organization, and functional coverage groups.

**Schema:**

.. code-block:: sql

    CREATE TABLE scopes (
        scope_id INTEGER PRIMARY KEY AUTOINCREMENT,
        parent_id INTEGER,                    -- NULL for root scopes
        scope_type INTEGER NOT NULL,          -- ucisScopeTypeT (bit flags)
        scope_name TEXT NOT NULL,
        scope_flags INTEGER DEFAULT 0,        -- Configuration flags
        weight INTEGER DEFAULT 1,             -- Coverage weight
        goal INTEGER,                         -- Coverage goal percentage
        limit INTEGER,                        -- Coverage limit
        source_file_id INTEGER,               -- Source location
        source_line INTEGER,
        source_token INTEGER,
        language_type INTEGER,                -- VHDL, Verilog, etc.
        
        FOREIGN KEY (parent_id) REFERENCES scopes(scope_id) ON DELETE CASCADE,
        FOREIGN KEY (source_file_id) REFERENCES files(file_id) ON DELETE SET NULL
    );
    
    CREATE INDEX idx_scopes_parent ON scopes(parent_id);
    CREATE INDEX idx_scopes_parent_type_name ON scopes(parent_id, scope_type, scope_name);

**Columns:**

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Column
     - Type
     - Description
   * - scope_id
     - INTEGER
     - Primary key (auto-increment)
   * - parent_id
     - INTEGER
     - Parent scope ID (NULL for root)
   * - scope_type
     - INTEGER
     - Scope type bit flags (see ucisScopeTypeT)
   * - scope_name
     - TEXT
     - Scope name
   * - scope_flags
     - INTEGER
     - Configuration flags (enabled coverage, UOR flags)
   * - weight
     - INTEGER
     - Coverage weight (default: 1)
   * - goal
     - INTEGER
     - Coverage goal percentage
   * - limit
     - INTEGER
     - Coverage limit
   * - source_file_id
     - INTEGER
     - Reference to files table
   * - source_line
     - INTEGER
     - Source line number
   * - source_token
     - INTEGER
     - Source token position
   * - language_type
     - INTEGER
     - Source language (VHDL, Verilog, SV, etc.)

**Scope Types (ucisScopeTypeT):**

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Type
     - Value
     - Description
   * - UCIS_TOGGLE
     - 0x0001
     - Toggle coverage scope
   * - UCIS_BRANCH
     - 0x0002
     - Branch coverage scope
   * - UCIS_EXPR
     - 0x0004
     - Expression coverage scope
   * - UCIS_COND
     - 0x0008
     - Condition coverage scope
   * - UCIS_INSTANCE
     - 0x0010
     - Design instance
   * - UCIS_DU_MODULE
     - 0x0020
     - Module design unit
   * - UCIS_DU_ARCH
     - 0x0040
     - Architecture design unit
   * - UCIS_DU_PACKAGE
     - 0x0080
     - Package design unit
   * - UCIS_DU_PROGRAM
     - 0x0100
     - Program design unit
   * - UCIS_DU_INTERFACE
     - 0x0200
     - Interface design unit
   * - UCIS_BLOCK
     - 0x0800
     - Block coverage scope
   * - UCIS_COVERGROUP
     - 0x1000
     - Covergroup type definition
   * - UCIS_COVERINSTANCE
     - 0x2000
     - Covergroup instance
   * - UCIS_COVERPOINT
     - 0x4000
     - Coverpoint
   * - UCIS_CROSS
     - 0x8000
     - Cross coverage
   * - UCIS_FSM
     - 0x400000
     - Finite state machine
   * - UCIS_ASSERT
     - 0x800000
     - Assertion/cover directive

**Scope Flags:**

.. list-table::
   :header-rows: 1
   :widths: 40 15 45

   * - Flag
     - Value
     - Description
   * - UCIS_ENABLED_STMT
     - 0x01
     - Statement coverage enabled
   * - UCIS_ENABLED_BRANCH
     - 0x02
     - Branch coverage enabled
   * - UCIS_ENABLED_COND
     - 0x04
     - Condition coverage enabled
   * - UCIS_ENABLED_EXPR
     - 0x08
     - Expression coverage enabled
   * - UCIS_ENABLED_FSM
     - 0x10
     - FSM coverage enabled
   * - UCIS_ENABLED_TOGGLE
     - 0x20
     - Toggle coverage enabled
   * - UCIS_UOR_SAFE_SCOPE
     - 0x40
     - Universal Object Recognition safe
   * - UCIS_UOR_SAFE_SCOPE_ALLCOVERS
     - 0x80
     - All coveritems UOR safe
   * - UCIS_INST_ONCE
     - 0x100
     - Instance appears once in design

**Example:**

.. code-block:: sql

    -- Create top-level instance
    INSERT INTO scopes (parent_id, scope_type, scope_name, scope_flags, weight)
    VALUES (NULL, 0x10, 'top', 0, 1);
    
    -- Create child module with toggle coverage enabled
    INSERT INTO scopes (parent_id, scope_type, scope_name, scope_flags, weight)
    VALUES (1, 0x10, 'dut', 0x20, 1);
    
    -- Query all instances
    SELECT scope_id, scope_name FROM scopes 
    WHERE scope_type & 0x10 != 0;

4. Coverage Items
=================

coveritems
----------

Leaf nodes containing actual coverage counts and metadata.

**Schema:**

.. code-block:: sql

    CREATE TABLE coveritems (
        cover_id INTEGER PRIMARY KEY AUTOINCREMENT,
        scope_id INTEGER NOT NULL,
        cover_index INTEGER NOT NULL,         -- Index within parent (0-based)
        cover_type INTEGER NOT NULL,          -- ucisCoverTypeT (bit flags)
        cover_name TEXT NOT NULL,
        cover_flags INTEGER DEFAULT 0,        -- Coverage state flags
        cover_data INTEGER DEFAULT 0,         -- Primary hit count
        cover_data_fec INTEGER DEFAULT 0,     -- Functional equivalent count
        at_least INTEGER DEFAULT 1,           -- Minimum for coverage
        weight INTEGER DEFAULT 1,
        goal INTEGER,
        limit INTEGER,
        source_file_id INTEGER,               -- Source location
        source_line INTEGER,
        source_token INTEGER,
        
        FOREIGN KEY (scope_id) REFERENCES scopes(scope_id) ON DELETE CASCADE,
        FOREIGN KEY (source_file_id) REFERENCES files(file_id) ON DELETE SET NULL,
        UNIQUE(scope_id, cover_index)
    );
    
    CREATE INDEX idx_coveritems_scope_index ON coveritems(scope_id, cover_index);

**Columns:**

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Column
     - Type
     - Description
   * - cover_id
     - INTEGER
     - Primary key (auto-increment)
   * - scope_id
     - INTEGER
     - Parent scope reference
   * - cover_index
     - INTEGER
     - Index within parent scope (0-based)
   * - cover_type
     - INTEGER
     - Coverage type bit flags
   * - cover_name
     - TEXT
     - Coverage item name
   * - cover_flags
     - INTEGER
     - State flags (covered, excluded, etc.)
   * - cover_data
     - INTEGER
     - Primary hit count
   * - cover_data_fec
     - INTEGER
     - Functional equivalent count
   * - at_least
     - INTEGER
     - Minimum count for coverage (default: 1)
   * - weight
     - INTEGER
     - Coverage weight
   * - goal
     - INTEGER
     - Coverage goal
   * - limit
     - INTEGER
     - Coverage limit
   * - source_file_id
     - INTEGER
     - Reference to files table
   * - source_line
     - INTEGER
     - Source line number
   * - source_token
     - INTEGER
     - Source token position

**Cover Types (ucisCoverTypeT):**

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Type
     - Value
     - Description
   * - UCIS_CVGBIN
     - 0x0001
     - Regular covergroup bin
   * - UCIS_STMTBIN
     - 0x0002
     - Statement
   * - UCIS_BRANCHBIN
     - 0x0004
     - Branch (true/false)
   * - UCIS_EXPRBIN
     - 0x0008
     - Expression term
   * - UCIS_CONDBIN
     - 0x0010
     - Condition
   * - UCIS_TOGGLEBIN
     - 0x0200
     - Toggle (0->1 or 1->0)
   * - UCIS_ASSERTBIN
     - 0x0400
     - Assertion/cover
   * - UCIS_FSMBIN
     - 0x0800
     - FSM state or transition
   * - UCIS_IGNOREBIN
     - 0x80000
     - Ignore bin (excluded from coverage)
   * - UCIS_ILLEGALBIN
     - 0x100000
     - Illegal bin (should not be hit)
   * - UCIS_DEFAULTBIN
     - 0x200000
     - Default bin

**Cover Flags:**

.. list-table::
   :header-rows: 1
   :widths: 40 15 45

   * - Flag
     - Value
     - Description
   * - UCIS_IS_COVERED
     - 0x01
     - Meets coverage goal
   * - UCIS_CVG_EXCLUDE
     - 0x02
     - Excluded from coverage
   * - UCIS_UOR_SAFE_COVERITEM
     - 0x04
     - Universal Object Recognition safe

**Example:**

.. code-block:: sql

    -- Create toggle coveritems (0->1 and 1->0)
    INSERT INTO coveritems (scope_id, cover_index, cover_type, cover_name, cover_data)
    VALUES (5, 0, 0x200, '0->1', 157);
    
    INSERT INTO coveritems (scope_id, cover_index, cover_type, cover_name, cover_data)
    VALUES (5, 1, 0x200, '1->0', 156);
    
    -- Find uncovered items
    SELECT c.cover_name, c.cover_data, c.at_least
    FROM coveritems c
    WHERE c.cover_data < c.at_least;

5. History Nodes (Test Records)
================================

history_nodes
-------------

Records of test runs, merges, and test plan nodes that contribute coverage data.

**Schema:**

.. code-block:: sql

    CREATE TABLE history_nodes (
        history_id INTEGER PRIMARY KEY AUTOINCREMENT,
        parent_id INTEGER,                    -- Hierarchical organization
        history_kind INTEGER NOT NULL,        -- TEST, MERGE, TESTPLAN
        logical_name TEXT NOT NULL,
        physical_name TEXT,
        test_status INTEGER,                  -- Pass/fail status
        sim_time_low INTEGER,                 -- 64-bit simulation time
        sim_time_high INTEGER,
        time_unit INTEGER,                    -- Time unit scale
        cpu_time REAL,                        -- CPU execution time
        seed TEXT,                            -- Random seed
        cmd_line TEXT,                        -- Command line
        compulsory INTEGER DEFAULT 0,         -- Is test mandatory
        date TEXT,                            -- Execution date
        user_name TEXT,
        cost REAL,                            -- Test cost metric
        version TEXT,                         -- Tool version
        
        FOREIGN KEY (parent_id) REFERENCES history_nodes(history_id) ON DELETE CASCADE
    );
    
    CREATE INDEX idx_history_parent ON history_nodes(parent_id);
    CREATE INDEX idx_history_kind ON history_nodes(history_kind);
    CREATE INDEX idx_history_logical ON history_nodes(logical_name);
    CREATE INDEX idx_history_status ON history_nodes(test_status);
    CREATE INDEX idx_history_date ON history_nodes(date) WHERE date IS NOT NULL;

**Columns:**

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Column
     - Type
     - Description
   * - history_id
     - INTEGER
     - Primary key (auto-increment)
   * - parent_id
     - INTEGER
     - Parent history node (for hierarchical organization)
   * - history_kind
     - INTEGER
     - Node kind (TEST, MERGE, TESTPLAN)
   * - logical_name
     - TEXT
     - Logical test name
   * - physical_name
     - TEXT
     - Physical file path
   * - test_status
     - INTEGER
     - Test execution status
   * - sim_time_low
     - INTEGER
     - Lower 32 bits of simulation time
   * - sim_time_high
     - INTEGER
     - Upper 32 bits of simulation time
   * - time_unit
     - INTEGER
     - Time unit scale factor
   * - cpu_time
     - REAL
     - CPU execution time (seconds)
   * - seed
     - TEXT
     - Random seed value
   * - cmd_line
     - TEXT
     - Command line used
   * - compulsory
     - INTEGER
     - Is test mandatory (boolean)
   * - date
     - TEXT
     - Execution date (ISO 8601)
   * - user_name
     - TEXT
     - User who ran test
   * - cost
     - REAL
     - Test cost metric
   * - version
     - TEXT
     - Tool version

**History Kinds:**

.. list-table::
   :header-rows: 1
   :widths: 35 15 50

   * - Kind
     - Value
     - Description
   * - UCIS_HISTORYNODE_TEST
     - 0x01
     - Individual test run
   * - UCIS_HISTORYNODE_MERGE
     - 0x02
     - Merged coverage from multiple sources
   * - UCIS_HISTORYNODE_TESTPLAN
     - 0x04
     - Test plan organizational node

**Test Status:**

.. list-table::
   :header-rows: 1
   :widths: 35 15 50

   * - Status
     - Value
     - Description
   * - UCIS_TESTSTATUS_OK
     - 0
     - Test passed
   * - UCIS_TESTSTATUS_WARNING
     - 1
     - Test passed with warnings
   * - UCIS_TESTSTATUS_FATAL
     - 2
     - Test failed

**Example:**

.. code-block:: sql

    -- Create test record
    INSERT INTO history_nodes (history_kind, logical_name, physical_name, 
                               test_status, seed, date)
    VALUES (0x01, 'test_basic', 'tests/test_basic.sv', 0, '12345', 
            '2026-01-12T10:30:00');
    
    -- Query failed tests
    SELECT logical_name, test_status FROM history_nodes 
    WHERE test_status = 2 AND history_kind = 0x01;

6. Test-Coverage Associations
==============================

coveritem_tests
---------------

Many-to-many relationship linking coverage items to the tests that hit them. Enables test minimization and impact analysis.

**Schema:**

.. code-block:: sql

    CREATE TABLE coveritem_tests (
        cover_id INTEGER NOT NULL,
        history_id INTEGER NOT NULL,
        count_contribution INTEGER DEFAULT 0,  -- Count from this test
        
        PRIMARY KEY (cover_id, history_id),
        FOREIGN KEY (cover_id) REFERENCES coveritems(cover_id) ON DELETE CASCADE,
        FOREIGN KEY (history_id) REFERENCES history_nodes(history_id) ON DELETE CASCADE
    );
    
    CREATE INDEX idx_coveritem_tests_cover ON coveritem_tests(cover_id);
    CREATE INDEX idx_coveritem_tests_history ON coveritem_tests(history_id);

**Use Cases:**

* Identify which tests hit specific coverage points
* Find tests that uniquely cover certain items
* Rank tests by unique coverage contribution
* Test minimization analysis

**Example:**

.. code-block:: sql

    -- Link test to coverage items
    INSERT INTO coveritem_tests (cover_id, history_id, count_contribution)
    VALUES (42, 1, 15);
    
    -- Find tests that hit a specific coverage point
    SELECT h.logical_name, ct.count_contribution
    FROM coveritem_tests ct
    JOIN history_nodes h ON ct.history_id = h.history_id
    WHERE ct.cover_id = 42;
    
    -- Find coverage unique to a test
    SELECT c.cover_name
    FROM coveritems c
    JOIN coveritem_tests ct ON c.cover_id = ct.cover_id
    WHERE ct.history_id = 1
    AND NOT EXISTS (
        SELECT 1 FROM coveritem_tests ct2 
        WHERE ct2.cover_id = c.cover_id AND ct2.history_id != 1
    );

7. Properties
=============

Generic key-value storage for extensible metadata on scopes, coveritems, and history nodes.

scope_properties
----------------

.. code-block:: sql

    CREATE TABLE scope_properties (
        scope_id INTEGER NOT NULL,
        property_key INTEGER NOT NULL,        -- Property enum
        property_type INTEGER NOT NULL,       -- INT, REAL, STRING, HANDLE
        int_value INTEGER,
        real_value REAL,
        string_value TEXT,
        handle_value INTEGER,                 -- Reference to another object
        
        PRIMARY KEY (scope_id, property_key),
        FOREIGN KEY (scope_id) REFERENCES scopes(scope_id) ON DELETE CASCADE
    );
    
    CREATE INDEX idx_scope_props_key ON scope_properties(property_key);

coveritem_properties
--------------------

.. code-block:: sql

    CREATE TABLE coveritem_properties (
        cover_id INTEGER NOT NULL,
        property_key INTEGER NOT NULL,
        property_type INTEGER NOT NULL,
        int_value INTEGER,
        real_value REAL,
        string_value TEXT,
        handle_value INTEGER,
        
        PRIMARY KEY (cover_id, property_key),
        FOREIGN KEY (cover_id) REFERENCES coveritems(cover_id) ON DELETE CASCADE
    );
    
    CREATE INDEX idx_cover_props_key ON coveritem_properties(property_key);

history_properties
------------------

.. code-block:: sql

    CREATE TABLE history_properties (
        history_id INTEGER NOT NULL,
        property_key INTEGER NOT NULL,
        property_type INTEGER NOT NULL,
        int_value INTEGER,
        real_value REAL,
        string_value TEXT,
        handle_value INTEGER,
        
        PRIMARY KEY (history_id, property_key),
        FOREIGN KEY (history_id) REFERENCES history_nodes(history_id) ON DELETE CASCADE
    );
    
    CREATE INDEX idx_history_props_key ON history_properties(property_key);

**Property Types:**

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Type
     - Description
   * - UCIS_ATTR_INT (1)
     - Integer value
   * - UCIS_ATTR_REAL (2)
     - Floating point value
   * - UCIS_ATTR_STRING (3)
     - String value
   * - UCIS_ATTR_HANDLE (4)
     - Reference to another object

**Common Property Keys:**

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Key
     - Description
   * - UCIS_STR_UNIQUE_ID (0x100)
     - Unique identifier string
   * - UCIS_STR_NAME (0x101)
     - Name property
   * - UCIS_STR_COMMENT (0x102)
     - Comment text
   * - UCIS_INT_SCOPE_NUM_COVERS (0x200)
     - Number of coveritems
   * - UCIS_INT_COVERAGE_COUNT (0x201)
     - Total coverage count
   * - UCIS_REAL_CVG_INST_AVERAGE (0x300)
     - Average coverage percentage

8. User-Defined Attributes
===========================

attributes
----------

Flexible user-defined key-value pairs for custom metadata.

**Schema:**

.. code-block:: sql

    CREATE TABLE attributes (
        attr_id INTEGER PRIMARY KEY AUTOINCREMENT,
        obj_kind INTEGER NOT NULL,            -- Scope, coveritem, or history
        obj_id INTEGER NOT NULL,
        attr_key TEXT NOT NULL,
        attr_value TEXT,
        
        UNIQUE(obj_kind, obj_id, attr_key)
    );
    
    CREATE INDEX idx_attributes_obj ON attributes(obj_kind, obj_id);
    CREATE INDEX idx_attributes_key ON attributes(attr_key);

**Object Kinds:**

.. list-table::
   :header-rows: 1
   :widths: 35 15 50

   * - Kind
     - Value
     - Description
   * - UCIS_OBJ_SCOPE
     - 1
     - Attribute on scope
   * - UCIS_OBJ_COVER
     - 2
     - Attribute on coveritem
   * - UCIS_OBJ_HISTORY
     - 3
     - Attribute on history node

9. Tags
=======

tags / object_tags
------------------

Named tags for linking objects to verification plans or categories.

**Schema:**

.. code-block:: sql

    CREATE TABLE tags (
        tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
        tag_name TEXT NOT NULL UNIQUE
    );
    
    CREATE INDEX idx_tags_name ON tags(tag_name);
    
    CREATE TABLE object_tags (
        obj_kind INTEGER NOT NULL,
        obj_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        
        PRIMARY KEY (obj_kind, obj_id, tag_id),
        FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON DELETE CASCADE
    );
    
    CREATE INDEX idx_object_tags_obj ON object_tags(obj_kind, obj_id);
    CREATE INDEX idx_object_tags_tag ON object_tags(tag_id);

10. Toggle Coverage Details
============================

toggle_bits
-----------

Per-bit toggle information for multi-bit signals.

**Schema:**

.. code-block:: sql

    CREATE TABLE toggle_bits (
        toggle_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cover_id INTEGER NOT NULL,            -- Parent toggle coveritem
        bit_index INTEGER NOT NULL,
        bit_type INTEGER NOT NULL,            -- Bit, enum, others
        toggle_01 INTEGER DEFAULT 0,          -- 0->1 count
        toggle_10 INTEGER DEFAULT 0,          -- 1->0 count
        
        FOREIGN KEY (cover_id) REFERENCES coveritems(cover_id) ON DELETE CASCADE,
        UNIQUE(cover_id, bit_index)
    );
    
    CREATE INDEX idx_toggle_bits_cover ON toggle_bits(cover_id);

11. FSM Coverage Details
=========================

fsm_states / fsm_transitions
-----------------------------

Finite state machine state definitions and transitions.

**Schema:**

.. code-block:: sql

    CREATE TABLE fsm_states (
        state_id INTEGER PRIMARY KEY AUTOINCREMENT,
        scope_id INTEGER NOT NULL,            -- Parent FSM scope
        state_name TEXT NOT NULL,
        state_index INTEGER NOT NULL,
        
        FOREIGN KEY (scope_id) REFERENCES scopes(scope_id) ON DELETE CASCADE,
        UNIQUE(scope_id, state_index)
    );
    
    CREATE INDEX idx_fsm_states_scope ON fsm_states(scope_id);
    CREATE INDEX idx_fsm_states_name ON fsm_states(state_name);
    
    CREATE TABLE fsm_transitions (
        cover_id INTEGER NOT NULL,            -- Transition coveritem
        from_state_id INTEGER NOT NULL,
        to_state_id INTEGER NOT NULL,
        
        PRIMARY KEY (cover_id),
        FOREIGN KEY (cover_id) REFERENCES coveritems(cover_id) ON DELETE CASCADE,
        FOREIGN KEY (from_state_id) REFERENCES fsm_states(state_id) ON DELETE CASCADE,
        FOREIGN KEY (to_state_id) REFERENCES fsm_states(state_id) ON DELETE CASCADE
    );
    
    CREATE INDEX idx_fsm_trans_from ON fsm_transitions(from_state_id);
    CREATE INDEX idx_fsm_trans_to ON fsm_transitions(to_state_id);

12. Cross Coverage
==================

cross_coverpoints
-----------------

Links cross coverage to constituent coverpoints.

**Schema:**

.. code-block:: sql

    CREATE TABLE cross_coverpoints (
        cross_scope_id INTEGER NOT NULL,      -- UCIS_CROSS scope
        coverpoint_scope_id INTEGER NOT NULL, -- UCIS_COVERPOINT scope
        cvp_index INTEGER NOT NULL,           -- Order in cross
        
        PRIMARY KEY (cross_scope_id, cvp_index),
        FOREIGN KEY (cross_scope_id) REFERENCES scopes(scope_id) ON DELETE CASCADE,
        FOREIGN KEY (coverpoint_scope_id) REFERENCES scopes(scope_id) ON DELETE CASCADE
    );
    
    CREATE INDEX idx_cross_cvps_cross ON cross_coverpoints(cross_scope_id);
    CREATE INDEX idx_cross_cvps_cvp ON cross_coverpoints(coverpoint_scope_id);

13. Formal Verification
========================

formal_data / formal_envs
--------------------------

Formal verification results and environment settings.

**Schema:**

.. code-block:: sql

    CREATE TABLE formal_data (
        cover_id INTEGER PRIMARY KEY,         -- Assertion coveritem
        formal_status INTEGER,                -- Proven, disproven, etc.
        formal_radius INTEGER,                -- Proof depth
        witness_file TEXT,                    -- Counter-example location
        
        FOREIGN KEY (cover_id) REFERENCES coveritems(cover_id) ON DELETE CASCADE
    );
    
    CREATE INDEX idx_formal_status ON formal_data(formal_status);
    
    CREATE TABLE formal_envs (
        env_id INTEGER PRIMARY KEY AUTOINCREMENT,
        history_id INTEGER,                   -- Associated test/proof
        env_type INTEGER NOT NULL,
        env_name TEXT,
        env_value TEXT,
        
        FOREIGN KEY (history_id) REFERENCES history_nodes(history_id) ON DELETE CASCADE
    );
    
    CREATE INDEX idx_formal_envs_history ON formal_envs(history_id);
    CREATE INDEX idx_formal_envs_type ON formal_envs(env_type);

**Formal Status Values:**

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Status
     - Description
   * - UCIS_FORMAL_VACUOUS (1)
     - Vacuously true
   * - UCIS_FORMAL_UNREACHABLE (2)
     - Unreachable
   * - UCIS_FORMAL_DISPROVEN (3)
     - Counter-example found
   * - UCIS_FORMAL_PROVEN (4)
     - Formally proven
   * - UCIS_FORMAL_INCONCLUSIVE (5)
     - Inconclusive result

14. Design Unit Management
===========================

design_units
------------

Tracks design unit definitions and relationships.

**Schema:**

.. code-block:: sql

    CREATE TABLE design_units (
        du_id INTEGER PRIMARY KEY AUTOINCREMENT,
        du_scope_id INTEGER NOT NULL UNIQUE,  -- References scopes table
        du_name TEXT NOT NULL,
        du_type INTEGER NOT NULL,             -- Module, architecture, etc.
        
        FOREIGN KEY (du_scope_id) REFERENCES scopes(scope_id) ON DELETE CASCADE
    );
    
    CREATE INDEX idx_design_units_name ON design_units(du_name);
    CREATE INDEX idx_design_units_type ON design_units(du_type);

******************
Query Examples
******************

Hierarchical Path Queries
==========================

Build full paths using recursive CTEs:

.. code-block:: sql

    WITH RECURSIVE scope_path AS (
        SELECT scope_id, scope_name, scope_type, parent_id, 
               scope_name as full_path
        FROM scopes
        WHERE parent_id IS NULL
        
        UNION ALL
        
        SELECT s.scope_id, s.scope_name, s.scope_type, s.parent_id,
               sp.full_path || '/' || s.scope_name
        FROM scopes s
        JOIN scope_path sp ON s.parent_id = sp.scope_id
    )
    SELECT full_path, scope_type
    FROM scope_path
    WHERE scope_name LIKE '%clk%';

Coverage Calculation
====================

Calculate coverage percentages:

.. code-block:: sql

    -- Coverpoint coverage
    SELECT 
        s.scope_name,
        COUNT(*) as total_bins,
        SUM(CASE WHEN c.cover_data >= c.at_least THEN 1 ELSE 0 END) as covered_bins,
        (100.0 * SUM(CASE WHEN c.cover_data >= c.at_least THEN 1 ELSE 0 END) / 
         COUNT(*)) as coverage_pct
    FROM scopes s
    JOIN coveritems c ON s.scope_id = c.scope_id
    WHERE s.scope_type = 0x4000  -- COVERPOINT
    GROUP BY s.scope_id;

Test Unique Coverage
====================

Find coverage unique to specific tests:

.. code-block:: sql

    SELECT 
        h.logical_name,
        COUNT(DISTINCT ct.cover_id) as bins_hit,
        COUNT(DISTINCT CASE WHEN unique_hits = 1 THEN ct.cover_id END) as unique_bins
    FROM history_nodes h
    JOIN coveritem_tests ct ON h.history_id = ct.history_id
    LEFT JOIN (
        SELECT cover_id, COUNT(*) as unique_hits
        FROM coveritem_tests
        GROUP BY cover_id
    ) u ON ct.cover_id = u.cover_id
    GROUP BY h.history_id;

Uncovered Items
===============

Find items not meeting coverage goals:

.. code-block:: sql

    SELECT 
        s.scope_name,
        c.cover_name,
        c.cover_data as hits,
        c.at_least as required
    FROM coveritems c
    JOIN scopes s ON c.scope_id = s.scope_id
    WHERE c.cover_data < c.at_least
    AND (c.cover_flags & 0x02) = 0  -- Not excluded
    ORDER BY s.scope_name, c.cover_index;

*******************
Performance Tuning
*******************

Schema Version
==============

**Current Version: 2.1**

The database schema includes a version number stored in the ``db_metadata`` table. Version 2.1 introduces optimizations for merge performance and storage efficiency:

* **Reduced indexes** - Removed 7 unused indexes that provided no query benefit
* **Merge optimization** - Streamlined bin creation to minimize row growth
* **History tracking** - Optional history squashing for large-scale merges

Opening a database with a mismatched schema version will raise an error. Databases from older schema versions must be recreated with the current schema.

Index Optimization
==================

Version 2.1 includes optimized indexes for common query patterns:

**Scopes:**

* ``idx_scopes_parent`` - Parent-child traversal
* ``idx_scopes_parent_type_name`` - Composite lookup by parent, type, and name

**Coveritems:**

* ``idx_coveritems_scope_index`` - Lookup by scope and cover index (critical for merge performance)

**Removed Indexes (v2.1):**

The following indexes were removed as they provided no measurable performance benefit:

* ``idx_scopes_type``, ``idx_scopes_name``, ``idx_scopes_parent_name``, ``idx_scopes_source``
* ``idx_coveritems_scope``, ``idx_coveritems_type``, ``idx_coveritems_name``, ``idx_coveritems_source``

This reduces storage overhead by approximately 30-40% with no query performance impact.

ANALYZE Command
===============

Update statistics for query optimization:

.. code-block:: sql

    ANALYZE;

Vacuum
======

Reclaim space and optimize storage:

.. code-block:: sql

    VACUUM;

**********
See Also
**********

* :doc:`sqlite_api` - Python API documentation
* :doc:`native_api` - C API documentation
* :doc:`ucis_oo_api` - General object-oriented API
