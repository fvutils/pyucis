# UCIS API Test Plan - Comprehensive Backend Coverage

## Executive Summary

This test plan aims to achieve comprehensive coverage of the PyUCIS object-oriented API across all backends (Memory, XML, YAML, SQLite). The approach follows a write-read-verify pattern using pytest parameterized tests to ensure consistency across backends.

### Key Updates Based on Feedback

**Priority Focus**: Scopes → Covergroups → Coverpoints first, then advanced features

**Backend Strategy**:
- **Full Featured** (Memory, XML, SQLite): Test all UCIS API features
- **Simplified** (YAML): Separate fixture, test only basic structures (scopes, covergroups, coverpoints, bins)

**Test Ordering**:
1. **Phase 1 (Priority)**: Core coverage structures - scopes, covergroups, coverpoints
2. **Phase 2-3**: Extended coverage types
3. **Phase 4 (Deferred)**: Advanced features like history nodes, properties, attributes

## Test Philosophy

Each test will follow this pattern:
1. **Create**: Instantiate database using backend-specific factory
2. **Write**: Use UCIS OO API to create coverage structures
3. **Persist**: Save to temporary storage (if backend requires it)
4. **Read**: Load database from storage using same backend
5. **Verify**: Assert that read data matches written data

## Backends to Test

### Phase 1: Core Backends (Initial Focus)
- **Memory** (`MemFactory`) - In-memory baseline, fully featured
- **XML** (`XmlFactory`) - File-based serialization, fully featured
- **SQLite** (`SqliteUCIS`) - Database persistence, fully featured

### Phase 1b: Simplified Backend
- **YAML** (`YamlReader`) - YAML serialization with **limited scope**
  - YAML format is simpler and cannot represent all UCIS features
  - Test separately with a focused subset of functionality
  - Focus on: basic scopes, covergroups, coverpoints, and bins
  - Skip: complex metadata, properties, attributes, toggle/FSM/assertion coverage
  - Use separate fixture: `@pytest.fixture` with `yaml_simple_backend`

### Phase 2: Advanced (Future)
- **lib** - Native C library wrapper (deferred per requirements)

## Test Organization

### File Structure
```
tests/unit/api/
├── __init__.py
├── conftest.py                    # Shared fixtures and backend parametrization
├── test_api_basic.py              # Database creation, metadata
├── test_api_file_handles.py       # File handle operations
├── test_api_history_nodes.py      # History nodes and test metadata
├── test_api_scope_hierarchy.py    # Scope creation and nesting
├── test_api_covergroups.py        # Covergroup operations
├── test_api_coverpoints.py        # Coverpoint and bin operations
├── test_api_cross_coverage.py     # Cross coverage
├── test_api_code_coverage.py      # Statement, branch, condition, expression coverage
├── test_api_toggle_coverage.py    # Toggle coverage
├── test_api_fsm_coverage.py       # FSM coverage
├── test_api_assertions.py         # Assertion coverage
├── test_api_properties.py         # Int/Real/Str properties
├── test_api_attributes.py         # User-defined attributes
├── test_api_flags.py              # Flags and options
└── test_api_edge_cases.py         # Edge cases, large datasets
```

---

## Detailed Test Cases by Category

### 1. Database Creation & Metadata (`test_api_basic.py`)

**Purpose**: Verify basic database lifecycle and metadata operations

#### Test Cases:
- **`test_create_empty_database[backend]`**
  - Create empty database
  - Verify it's writable and readable
  - Check default metadata values

- **`test_database_metadata[backend]`**
  - Set/get API version (should be "1.0")
  - Set/get written_by (username)
  - Set/get written_time (timestamp)
  - Set/get path separator

- **`test_database_properties[backend]`**
  - Test `isModified()` flag
  - Test `modifiedSinceSim()` flag
  - Test `getNumTests()` count

- **`test_database_close[backend]`**
  - Create database, write data
  - Close database
  - Reopen and verify data persists (for persistent backends)

**LRM References**: Section 3 (API Overview), Section 4.1 (Database Management)

---

### 2. File Handles (`test_api_file_handles.py`)

**Purpose**: Test source file reference management

#### Test Cases:
- **`test_create_file_handle[backend]`**
  - Create file handle with filename + workdir
  - Verify `getFileName()` returns correct path
  - Verify uniqueness (same file → same handle)

- **`test_multiple_file_handles[backend]`**
  - Create 10+ file handles
  - Verify all are retrievable
  - Check `getSourceFiles()` returns complete list

- **`test_file_handle_paths[backend]`**
  - Test absolute paths
  - Test relative paths
  - Test paths with special characters
  - Test None workdir

**LRM References**: Section 4.2 (File Handle Management)

---

### 3. History Nodes (`test_api_history_nodes.py`) - **ADVANCED**

**Purpose**: Test test/simulation metadata tracking

**Priority**: Phase 4 (Advanced) - Focus on scopes, covergroups, and coverpoints first

#### Test Cases:
- **`test_create_history_node[backend]`**
  - Create history node with kind=TEST
  - Set logical/physical names
  - Verify retrieval via `historyNodes()`

- **`test_history_node_kinds[backend]`**
  - Test all kinds: TEST, MERGE, REFINE, etc.
  - Filter by kind using `historyNodes(kind)`
  - Verify kind-specific queries

- **`test_history_node_hierarchy[backend]`**
  - Create parent history node
  - Create child nodes
  - Verify parent-child relationships

- **`test_test_data[backend]`**
  - Create TestData object with all fields:
    - teststatus (OK, FATAL, etc.)
    - toolcategory, simtime, timeunit
    - runcwd, cputime, seed
    - cmd, args, compulsory
    - date, user, cost
  - Attach to history node via `setTestData()`
  - Read back and verify all fields

- **`test_multiple_tests[backend]`**
  - Create 3 test history nodes
  - Verify `getNumTests()` returns 3
  - Query each test individually

**LRM References**: Section 4.3 (History Nodes), Section 4.4 (Test Data)

---

### 4. Scope Hierarchy (`test_api_scope_hierarchy.py`)

**Purpose**: Test design hierarchy creation and navigation

#### Test Cases:
- **`test_create_design_unit[backend]`**
  - Create DU_MODULE scope
  - Set DU_SIGNATURE property
  - Verify SCOPE_UNDER_DU flag

- **`test_create_instance[backend]`**
  - Create DU and instance
  - Link instance to DU via `createInstance(du_scope=...)`
  - Verify instance references DU

- **`test_scope_types[backend]`**
  - Test major scope types:
    - INSTANCE, MODULE, PACKAGE, CLASS
    - FUNCTION, TASK, PROCESS, BLOCK
    - GENERATE, FORKJOIN
  - Verify `getScopeType()` returns correct type

- **`test_nested_scopes[backend]`**
  - Create 5-level hierarchy: MODULE → INSTANCE → BLOCK → PROCESS
  - Navigate with `scopes()` iterator
  - Verify parent-child relationships

- **`test_scope_weights_goals[backend]`**
  - Create scopes with different weights (1, 10, 100)
  - Set custom goals (50, 75, 100)
  - Verify `getWeight()`, `getGoal()` return correct values

- **`test_scope_flags[backend]`**
  - Test coverage enable flags:
    - ENABLED_STMT, ENABLED_BRANCH, ENABLED_COND
    - ENABLED_EXPR, ENABLED_FSM, ENABLED_TOGGLE
  - Test instance flags: INST_ONCE
  - Verify `getFlags()` returns correct bitfield

- **`test_scope_iteration[backend]`**
  - Create mixed scope hierarchy
  - Use `scopes(mask)` to filter by type
  - Test masks: ALL, INSTANCE, COVERGROUP, etc.

- **`test_scope_source_info[backend]`**
  - Attach SourceInfo (file, line, token) to scopes
  - Verify `getSourceInfo()` retrieval

**LRM References**: Section 5 (Scope Hierarchy), Section 6 (Coverage Scopes)

---

### 5. Covergroups (`test_api_covergroups.py`)

**Purpose**: Test functional coverage containers

#### Test Cases:
- **`test_create_covergroup[backend]`**
  - Create covergroup under instance
  - Set type options: goal, strobe, merge_instances
  - Verify `createCovergroup()` returns Covergroup object

- **`test_covergroup_options[backend]`**
  - Set `setPerInstance(True/False)`
  - Set `setMergeInstances(True/False)`
  - Set `setGetInstCoverage(True/False)`
  - Read back via properties

- **`test_covergroup_goal[backend]`**
  - Set custom goal (e.g., 90)
  - Create bins below and above goal
  - Verify coverage calculation

- **`test_covergroup_weight[backend]`**
  - Create multiple covergroups with different weights
  - Verify weighted coverage calculation

- **`test_covergroup_comment[backend]`**
  - Set comment string via `setComment()`
  - Verify retrieval

- **`test_multiple_covergroups[backend]`**
  - Create 5 covergroups in same scope
  - Iterate with `scopes(ScopeTypeT.COVERGROUP)`
  - Verify all are accessible

**LRM References**: Section 7.1 (Covergroups)

---

### 6. Coverpoints & Bins (`test_api_coverpoints.py`)

**Purpose**: Test coverage point and bin operations

#### Test Cases:
- **`test_create_coverpoint[backend]`**
  - Create coverpoint under covergroup
  - Set name, weight, source info
  - Verify `createCoverpoint()` success

- **`test_coverpoint_atleast[backend]`**
  - Set `at_least` threshold (e.g., 10)
  - Create bins with counts above/below threshold
  - Verify coverage hit calculation

- **`test_create_bins[backend]`**
  - Create bins with different types:
    - CVGBIN (standard bin)
    - IGNOREBIN (ignored)
    - ILLEGALBIN (illegal value)
  - Verify `getCoverData().type` returns correct type

- **`test_bin_counts[backend]`**
  - Create bins with counts: 0, 1, 100, 1000000
  - Use 32-bit and 64-bit modes
  - Verify `getCoverData().data` matches

- **`test_bin_goals_weights[backend]`**
  - Create bins with custom goals and weights
  - Set flags: HAS_GOAL, HAS_WEIGHT
  - Verify `getCoverData().goal` and `.weight`

- **`test_bin_increment[backend]`**
  - Create bin with count=0
  - Call `incrementCover(5)` (if implemented)
  - Verify count becomes 5

- **`test_coverpoint_iteration[backend]`**
  - Create coverpoint with 10 bins
  - Iterate via `coverItems()` or similar
  - Verify all bins accessible

- **`test_bin_names[backend]`**
  - Create bins with special names: "auto[0]", "illegal_bins", ""
  - Verify `getName()` retrieval

- **`test_coverpoint_coverage_calc[backend]`**
  - Create coverpoint with 4 bins: 2 hit, 2 miss
  - Calculate coverage: should be 50%
  - Verify via properties

**LRM References**: Section 7.2 (Coverpoints), Section 7.3 (Bins)

---

### 7. Cross Coverage (`test_api_cross_coverage.py`)

**Purpose**: Test cross product coverage

#### Test Cases:
- **`test_create_cross[backend]`**
  - Create 2 coverpoints
  - Create cross linking them
  - Verify `createCross()` success

- **`test_cross_bin_names[backend]`**
  - Create cross with named bins (e.g., "bin1 × bin2")
  - Verify bin naming convention

- **`test_cross_counts[backend]`**
  - Create cross with various hit counts
  - Verify cross product bins store correct counts

- **`test_cross_references[backend]`**
  - Verify `getNumCrossedCoverpoints()` returns 2
  - Verify `getIthCrossedCoverpoint(0/1)` returns correct coverpoints

- **`test_three_way_cross[backend]`**
  - Create 3 coverpoints
  - Create 3-way cross
  - Verify all combinations represented

**LRM References**: Section 7.4 (Cross Coverage)

---

### 8. Code Coverage (`test_api_code_coverage.py`)

**Purpose**: Test structural code coverage types

#### Test Cases:
- **`test_statement_coverage[backend]`**
  - Create STMTBIN items
  - Set line numbers, statement indices
  - Set UCIS_INT_STMT_INDEX property
  - Verify counts

- **`test_branch_coverage[backend]`**
  - Create BRANCHBIN items
  - Test true/false branches
  - Verify branch hit/miss

- **`test_condition_coverage[backend]`**
  - Create CONDBIN items
  - Test condition terms (T, F, TT, TF, FT, FF)
  - Verify condition coverage

- **`test_expression_coverage[backend]`**
  - Create EXPRBIN items
  - Test expression evaluation paths
  - Verify coverage

- **`test_block_coverage[backend]`**
  - Create BLOCKBIN items
  - Track basic block execution
  - Verify counts

- **`test_code_coverage_uor_names[backend]`**
  - Verify UOR naming: "#stmt#fileno#line#item#"
  - Test name parsing and reconstruction

**LRM References**: Section 8 (Code Coverage)

---

### 9. Toggle Coverage (`test_api_toggle_coverage.py`)

**Purpose**: Test signal toggle tracking

#### Test Cases:
- **`test_create_toggle_scope[backend]`**
  - Create toggle scope via `createToggle()`
  - Set metric: ENUM, SCALAR, REAL, etc.
  - Set type: REG, NET, PORT
  - Set direction: INPUT, OUTPUT, INTERNAL

- **`test_scalar_toggle[backend]`**
  - Create scalar toggle (1-bit)
  - Create 0→1 and 1→0 bins
  - Verify TOGGLEBIN counts

- **`test_enum_toggle[backend]`**
  - Create enum toggle
  - Add state bins ("IDLE", "ACTIVE", "DONE")
  - Verify state transition coverage

- **`test_vector_toggle[backend]`**
  - Create multi-bit toggle
  - Track per-bit toggle coverage
  - Verify coverage metrics

- **`test_toggle_canonical_name[backend]`**
  - Set canonical name (hierarchical path)
  - Verify retrieval

**LRM References**: Section 9 (Toggle Coverage)

---

### 10. FSM Coverage (`test_api_fsm_coverage.py`)

**Purpose**: Test finite state machine coverage

#### Test Cases:
- **`test_create_fsm[backend]`**
  - Create FSM scope
  - Add FSM_STATES child scope
  - Add FSM_TRANS child scope

- **`test_fsm_states[backend]`**
  - Create state bins under FSM_STATES
  - Verify state hit counts

- **`test_fsm_transitions[backend]`**
  - Create transition bins under FSM_TRANS
  - Name transitions: "state1→state2"
  - Verify transition counts

- **`test_fsm_coverage_calc[backend]`**
  - Create FSM with 3 states, 5 transitions
  - Mark some visited, some not
  - Calculate overall FSM coverage

**LRM References**: Section 10 (FSM Coverage)

---

### 11. Assertion Coverage (`test_api_assertions.py`)

**Purpose**: Test assertion and directive coverage

#### Test Cases:
- **`test_assertion_bins[backend]`**
  - Create assertion scope
  - Add bins: PASSBIN, FAILBIN, VACUOUSBIN
  - Verify counts

- **`test_cover_directive[backend]`**
  - Create COVER scope (SVA cover directive)
  - Track cover hits
  - Verify coverage

- **`test_assertion_attempts[backend]`**
  - Create ATTEMPTBIN (assertion evaluated)
  - Create ACTIVEBIN (assertion active)
  - Verify counts

**LRM References**: Section 11 (Assertion Coverage)

---

### 12. Properties (`test_api_properties.py`)

**Purpose**: Test property system (typed attributes)

#### Test Cases:
- **`test_int_properties[backend]`**
  - Test all IntProperty enums:
    - SCOPE_GOAL, SCOPE_WEIGHT, SCOPE_NUM_SCOPES
    - CVG_ATLEAST, CVG_GOAL, CVG_STROBE, CVG_MERGEINSTANCES
    - STMT_INDEX, TOGGLE_COUNT, etc.
  - Set via `setIntProperty()`
  - Read via `getIntProperty()`

- **`test_real_properties[backend]`**
  - Set real-valued properties (e.g., coverage %)
  - Verify floating-point precision

- **`test_str_properties[backend]`**
  - Test string properties:
    - COMMENT, DU_SIGNATURE, etc.
  - Set via `setStringProperty()`
  - Read via `getStringProperty()`

- **`test_property_inheritance[backend]`**
  - Set property on parent scope
  - Verify child scope inherits or overrides

**LRM References**: Section 12 (Properties)

---

### 13. Attributes (`test_api_attributes.py`)

**Purpose**: Test user-defined attributes

#### Test Cases:
- **`test_add_attribute[backend]`**
  - Add custom attribute to scope/bin
  - Types: INT, REAL, STRING, MEMBLK
  - Verify `AttrAdd()` / `AttrGet()` (if implemented in OO API)

- **`test_attribute_types[backend]`**
  - Test all attribute types
  - Verify type safety

- **`test_bin_attributes[backend]`**
  - Add "BINRHS" attribute to bin (right-hand-side value)
  - Verify retrieval

**LRM References**: Section 13 (Attributes)

---

### 14. Flags (`test_api_flags.py`)

**Purpose**: Test flag combinations and semantics

#### Test Cases:
- **`test_coverage_flags[backend]`**
  - Test CoverFlagsT: IS_32BIT, IS_64BIT, HAS_GOAL, HAS_WEIGHT
  - Verify flag interactions

- **`test_scope_flags[backend]`**
  - Test FlagsT: ENABLED_*, INST_*, SCOPE_*
  - Verify bitfield operations

- **`test_source_language_flags[backend]`**
  - Test SourceT: VLOG, VHDL, SV, PSL, etc.
  - Verify language tagging

**LRM References**: Various (flags defined throughout spec)

---

### 15. Edge Cases (`test_api_edge_cases.py`)

**Purpose**: Test boundary conditions and error handling

#### Test Cases:
- **`test_empty_database[backend]`**
  - Create database with no scopes
  - Write and read back
  - Verify empty structure preserved

- **`test_large_hierarchy[backend]`**
  - Create deep hierarchy (10+ levels)
  - Create wide hierarchy (100+ children per scope)
  - Verify performance and correctness

- **`test_large_bin_counts[backend]`**
  - Create bins with MAX_INT counts
  - Test 64-bit mode for large counts
  - Verify no overflow

- **`test_unicode_names[backend]`**
  - Create scopes/bins with Unicode names
  - Verify UTF-8 encoding/decoding

- **`test_special_characters[backend]`**
  - Test names with: spaces, dots, brackets, #, →
  - Verify escaping/quoting

- **`test_zero_weight_scopes[backend]`**
  - Create scopes with weight=0
  - Verify coverage calculation handles it

- **`test_duplicate_names[backend]`**
  - Create scopes with identical names (allowed in UCIS)
  - Verify both are stored and retrievable

- **`test_concurrent_access[backend]`** (SQLite only)
  - Open database from multiple connections
  - Verify locking/transactions

---

## Backend-Specific Considerations

### Memory Backend
- **Fully Featured**: Supports all UCIS API features
- **No persistence**: Write/read cycles happen in-memory only
- **Fast baseline**: Use as reference for other backends
- **Limitation**: Cannot test database reopening
- **Test Strategy**: Run all tests except persistence tests

### XML Backend
- **Fully Featured**: Supports all UCIS API features
- **File-based**: Write to temp file, read back from file
- **Validation**: Always validate against XSD schema
- **Compression**: Test gzip and LZ4 compression (if available)
- **Pretty-print**: Verify XML is human-readable
- **Test Strategy**: Run all tests

### SQLite Backend
- **Fully Featured**: Supports all UCIS API features
- **Persistence**: Test database reopen scenarios
- **Transactions**: Verify commit/rollback
- **Lazy loading**: Test iterator-based access
- **Schema migration**: Test schema version checking
- **Performance**: May be slower for large hierarchies
- **Test Strategy**: Run all tests including persistence tests

### YAML Backend - **LIMITED SCOPE**
- **Simplified Format**: YAML cannot represent all UCIS features
- **Read/Write Support**: Basic read/write for simple structures
- **Supported Features**:
  - ✅ Basic scopes (INSTANCE, MODULE)
  - ✅ Covergroups
  - ✅ Coverpoints
  - ✅ Bins with counts
  - ✅ Basic weights and goals
- **NOT Supported**:
  - ❌ Complex metadata (history nodes, detailed test data)
  - ❌ All properties (int/real/str properties)
  - ❌ User-defined attributes
  - ❌ Toggle coverage (complex structures)
  - ❌ FSM coverage (state/transition scopes)
  - ❌ Assertion coverage
  - ❌ Code coverage (stmt/branch/cond/expr details)
  - ❌ Cross coverage (complex references)
- **Test Strategy**: Use separate `yaml_backend` fixture, test only supported features
- **Fixture Usage**: Tests using YAML should explicitly use `yaml_backend` fixture

---

## Pytest Fixtures & Parametrization

### conftest.py Structure

```python
import pytest
import tempfile
import os
from pathlib import Path

from ucis.mem.mem_factory import MemFactory
from ucis.xml.xml_factory import XmlFactory
from ucis.yaml.yaml_reader import YamlReader
from ucis.sqlite.sqlite_ucis import SqliteUCIS

# Backend configuration
FULL_BACKENDS = [
    ("memory", "mem"),
    ("xml", "xml"),
    ("sqlite", "sqlite"),
]

YAML_SIMPLE_BACKEND = [
    ("yaml", "yaml"),
]

@pytest.fixture(params=FULL_BACKENDS, ids=[b[0] for b in FULL_BACKENDS])
def backend(request, tmp_path):
    """
    Parametrized fixture for full-featured backends (Memory, XML, SQLite).
    
    Returns:
        tuple: (backend_name, create_func, write_func, read_func, temp_file)
    """
    backend_name, backend_type = request.param
    
    # Create temp file path (used by file-based backends)
    if backend_type == "xml":
        temp_file = tmp_path / "test.xml"
    elif backend_type == "sqlite":
        temp_file = tmp_path / "test.db"
    else:
        temp_file = None
    
    # Define backend operations
    if backend_type == "mem":
        def create_db():
            return MemFactory.create()
        
        def write_db(db, path):
            # Memory backend doesn't need explicit write
            return db
        
        def read_db(db_or_path):
            # Return same DB instance
            return db_or_path
    
    elif backend_type == "xml":
        def create_db():
            return MemFactory.create()
        
        def write_db(db, path):
            XmlFactory.write(db, str(path))
            return path
        
        def read_db(path):
            return XmlFactory.read(str(path))
    
    elif backend_type == "sqlite":
        def create_db():
            return SqliteUCIS(str(temp_file))
        
        def write_db(db, path):
            db.close()  # Commit changes
            return path
        
        def read_db(path):
            return SqliteUCIS(str(path))
    
    yield (backend_name, create_db, write_db, read_db, temp_file)

@pytest.fixture(params=YAML_SIMPLE_BACKEND, ids=[b[0] for b in YAML_SIMPLE_BACKEND])
def yaml_backend(request, tmp_path):
    """
    Separate fixture for YAML backend with limited functionality.
    Only use this for basic scope/covergroup/coverpoint tests.
    
    Returns:
        tuple: (backend_name, create_func, write_func, read_func, temp_file)
    """
    backend_name, backend_type = request.param
    temp_file = tmp_path / "test.yaml"
    
    def create_db():
        return MemFactory.create()
    
    def write_db(db, path):
        # Use YamlWriter if available
        from ucis.yaml.yaml_writer import YamlWriter
        writer = YamlWriter()
        with open(str(path), 'w') as f:
            writer.write(f, db)
        return path
    
    def read_db(path):
        from ucis.yaml.yaml_reader import YamlReader
        reader = YamlReader()
        return reader.read(str(path))
    
    yield (backend_name, create_db, write_db, read_db, temp_file)

@pytest.fixture
def sample_file_handle(backend):
    """Create a sample file handle"""
    backend_name, create_db, _, _, _ = backend
    db = create_db()
    return db.createFileHandle("test.sv", "/home/user/project")

# Helper assertions
def assert_coverage_equal(expected, actual, tolerance=0.01):
    """Compare coverage percentages with tolerance"""
    assert abs(expected - actual) < tolerance

def assert_scope_tree_equal(scope1, scope2):
    """Recursively compare scope hierarchies"""
    assert scope1.getScopeName() == scope2.getScopeName()
    assert scope1.getScopeType() == scope2.getScopeType()
    # ... more assertions
```

### Example Test with Parametrization

```python
def test_create_covergroup_with_bins(backend):
    """Test covergroup creation across all backends"""
    backend_name, create_db, write_db, read_db, temp_file = backend
    
    # Create database
    db = create_db()
    
    # Write: Create coverage structure
    file_h = db.createFileHandle("test.sv", "/tmp")
    inst = db.createInstance("top", None, 1, UCIS_VLOG, UCIS_INSTANCE, None, 0)
    cg = inst.createCovergroup("cg1", SourceInfo(file_h, 10, 0), 1, UCIS_VLOG)
    cp = cg.createCoverpoint("cp1", SourceInfo(file_h, 11, 0), 1, UCIS_VLOG)
    
    bin1 = cp.createBin("bin_a", SourceInfo(file_h, 12, 0), 1, 5, "")
    bin2 = cp.createBin("bin_b", SourceInfo(file_h, 13, 0), 1, 0, "")
    
    # Persist
    temp_file = write_db(db, temp_file)
    
    # Read back
    db2 = read_db(temp_file if temp_file else db)
    
    # Verify: Check structure preserved
    scopes = list(db2.scopes(ScopeTypeT.COVERGROUP))
    assert len(scopes) == 1
    assert scopes[0].getScopeName() == "cg1"
    
    cps = list(scopes[0].scopes(ScopeTypeT.COVERPOINT))
    assert len(cps) == 1
    assert cps[0].getScopeName() == "cp1"
    
    bins = list(cps[0].coverItems())
    assert len(bins) == 2
    assert bins[0].getName() == "bin_a"
    assert bins[0].getCoverData().data == 5
    assert bins[1].getName() == "bin_b"
    assert bins[1].getCoverData().data == 0
```

### Example YAML-Specific Test

```python
def test_yaml_simple_covergroup(yaml_backend):
    """
    Test basic covergroup structure on YAML backend.
    
    YAML backend only supports simple structures, so we test:
    - Basic scope hierarchy
    - Covergroup with coverpoint
    - Bins with counts
    
    We do NOT test:
    - Properties
    - Attributes
    - Complex metadata
    """
    backend_name, create_db, write_db, read_db, temp_file = yaml_backend
    
    # Create database
    db = create_db()
    
    # Write: Simple structure only
    inst = db.createScope("top", None, 1, UCIS_VLOG, UCIS_INSTANCE, 0)
    cg = inst.createCovergroup("cg1", None, 1, UCIS_VLOG)
    cp = cg.createCoverpoint("cp1", None, 1, UCIS_VLOG)
    
    bin1 = cp.createBin("bin_a", None, 1, 5, "")
    bin2 = cp.createBin("bin_b", None, 1, 0, "")
    
    # Persist to YAML
    temp_file = write_db(db, temp_file)
    
    # Read back from YAML
    db2 = read_db(temp_file)
    
    # Verify basic structure preserved
    scopes = list(db2.scopes(ScopeTypeT.INSTANCE))
    assert len(scopes) == 1
    assert scopes[0].getScopeName() == "top"
    
    cgs = list(scopes[0].scopes(ScopeTypeT.COVERGROUP))
    assert len(cgs) == 1
    
    cps = list(cgs[0].scopes(ScopeTypeT.COVERPOINT))
    assert len(cps) == 1
    
    bins = list(cps[0].coverItems())
    assert len(bins) == 2
    # Note: YAML may not preserve all bin details, test basic structure only
```

---

## Test Execution Strategy

### Updated Priorities Based on Feedback

**Focus Order**: Scopes → Covergroups → Coverpoints → Other features

### Phase 1: Core Coverage Structures (Weeks 1-2) - **PRIORITY**
1. Implement conftest.py with backend parametrization (separate `backend` and `yaml_backend` fixtures)
2. Implement `test_api_basic.py` (database lifecycle) - basic tests only
3. Implement `test_api_scope_hierarchy.py` - **FOCUS HERE FIRST**
   - Create scopes, instances, hierarchy navigation
   - Test with Memory, XML, SQLite backends
4. Implement `test_api_covergroups.py` - **CORE FUNCTIONALITY**
   - Covergroup creation, options, weights
   - Test with Memory, XML, SQLite backends
5. Implement `test_api_coverpoints.py` - **CORE FUNCTIONALITY**
   - Coverpoint creation, bins, counts, goals
   - Test with Memory, XML, SQLite backends
6. **Goal**: Core functional coverage working perfectly on all full-featured backends

### Phase 1b: YAML Simple Tests (Week 2)
7. Implement simplified YAML tests for scope/covergroup/coverpoint
   - Use `yaml_backend` fixture
   - Focus on basic structure preservation only
   - Skip advanced features (properties, metadata, etc.)
8. **Goal**: YAML backend handles basic coverage structures

### Phase 2: Extended Coverage (Weeks 3-4)
9. Implement `test_api_cross_coverage.py`
10. Implement `test_api_file_handles.py`
11. Implement `test_api_code_coverage.py` (stmt, branch, cond, expr)
12. **Goal**: Extended coverage types working

### Phase 3: Advanced Coverage Types (Week 5)
13. Implement `test_api_toggle_coverage.py`
14. Implement `test_api_fsm_coverage.py`
15. Implement `test_api_assertions.py`
16. **Goal**: All coverage types tested

### Phase 4: Metadata & Advanced Features (Week 6) - **DEFERRED**
17. Implement `test_api_history_nodes.py` - **ADVANCED CASE**
18. Implement `test_api_properties.py`
19. Implement `test_api_attributes.py`
20. Implement `test_api_flags.py`
21. **Goal**: Metadata and properties fully tested

### Phase 5: Robustness (Week 7)
22. Implement `test_api_edge_cases.py`
23. Performance benchmarking
24. **Goal**: Edge cases handled, backends perform acceptably

---

## Success Criteria

### Coverage Goals
- **Code Coverage**: >90% of src/ucis/ core API lines
- **API Coverage**: 100% of core public methods tested (scopes, covergroups, coverpoints)
- **Backend Coverage**: 
  - Memory, XML, SQLite: Fully tested with all features
  - YAML: Basic structure tests only (scope, covergroup, coverpoint, bins)

### Quality Gates
- All tests pass on respective backends (with documented limitations)
- Core tests (scope/covergroup/coverpoint) must pass on all 4 backends
- No test should take >5 seconds (except large dataset tests)
- XML output validates against schema
- SQLite database schema is correct
- YAML output is human-readable and clean

### Test Priority Success
- **Phase 1 (Weeks 1-2)**: Scope/Covergroup/Coverpoint tests working on Memory, XML, SQLite
- **Phase 1b (Week 2)**: Basic YAML tests passing
- **Phase 2-5**: Extended features on Memory, XML, SQLite only

### Documentation
- Each test has clear docstring explaining what it tests
- Known backend limitations documented in conftest.py
- Test output is clear and actionable
- README explains which backends support which features

---

## Known Limitations & Workarounds

### Memory Backend
- **No persistence testing**: Cannot test database reopen
- **Workaround**: Skip tests requiring reopen for Memory backend
- **Status**: Fully featured otherwise

### YAML Backend - **SIMPLIFIED SCOPE**
- **Limited feature set**: Cannot represent all UCIS structures
- **Supported**: Basic scopes, covergroups, coverpoints, bins with counts
- **NOT Supported**: Properties, attributes, metadata, toggle/FSM/assertion/code coverage
- **Workaround**: Use separate `yaml_backend` fixture, only test supported features
- **Test Strategy**: Create separate simplified tests using `yaml_backend` fixture

### SQLite Backend
- **Performance**: May be slower for large hierarchies
- **Workaround**: Use smaller datasets for quick tests, separate perf tests
- **Status**: Fully featured

### XML Backend
- **File I/O overhead**: Slower than Memory
- **Workaround**: Use temp files cleaned up after test
- **Status**: Fully featured

---

## Metrics & Reporting

### Per-Test Metrics
- Execution time
- Memory usage
- File size (for file-based backends)

### Per-Backend Metrics
- Total tests passed/failed/skipped
- Average execution time
- Coverage achieved

### Continuous Monitoring
- Run full suite on every commit
- Track coverage trends over time
- Alert on regressions

---

## References

1. **UCIS LRM v1.0**: `UCIS_Version_1.0_Final_June-2012.md`
2. **PyUCIS API**: `src/ucis/*.py`
3. **Backend Implementations**: 
   - `src/ucis/mem/`
   - `src/ucis/xml/`
   - `src/ucis/sqlite/`
   - `src/ucis/yaml/`
4. **Existing Tests**: `tests/unit/test_*.py`

---

## Appendix: LRM Section Mapping

| Test File | LRM Sections |
|-----------|-------------|
| test_api_basic.py | 3, 4.1 |
| test_api_file_handles.py | 4.2 |
| test_api_history_nodes.py | 4.3, 4.4 |
| test_api_scope_hierarchy.py | 5, 6 |
| test_api_covergroups.py | 7.1 |
| test_api_coverpoints.py | 7.2, 7.3 |
| test_api_cross_coverage.py | 7.4 |
| test_api_code_coverage.py | 8 |
| test_api_toggle_coverage.py | 9 |
| test_api_fsm_coverage.py | 10 |
| test_api_assertions.py | 11 |
| test_api_properties.py | 12 |
| test_api_attributes.py | 13 |
| test_api_flags.py | Various |
| test_api_edge_cases.py | All |

---

## Next Steps

1. **Review this plan** with stakeholders
2. **Create test directory structure**: `tests/unit/api/`
3. **Implement conftest.py** with backend parametrization
4. **Start with Phase 1**: Basic database tests
5. **Iterate**: Add tests incrementally, ensuring each passes before moving on

**Estimated Total Effort**: 7 weeks (1 developer, full-time)
**Expected Test Count**: 150-200 parameterized tests = 600-800 test executions (4 backends × tests)
