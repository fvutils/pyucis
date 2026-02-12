# PyUCIS Python API Documentation Plan

## Executive Summary

This plan outlines a comprehensive approach to documenting the PyUCIS Python API by adding docstrings to all public API classes and methods in `src/ucis/*.py`, using information from the UCIS Version 1.0 LRM document as a reference. The plan adapts the C API descriptions from the LRM to the object-oriented Python implementation and includes updates to the Sphinx RST documentation files in `doc/source/`.

## Current State Assessment

### Documentation Gaps

**Critical Finding**: The core Python API has **zero class or method docstrings**.

- All 47 Python files in `src/ucis/` use old-style module docstrings (`'''Created on...'''`) with only creation date and author
- No class-level documentation explaining purpose or usage patterns
- No method docstrings for parameters, return values, or exceptions
- No examples or usage guidance in the code

### Existing Documentation

**RST Documentation** (`doc/source/reference/`):
- `ucis_oo_api.rst` - **Placeholder only** (12 lines, attempts to use autoclass but has no docstrings to extract)
- `sqlite_api.rst` - Detailed SQLite-specific API (17KB)
- `native_api.rst` - C library documentation (20KB)
- `ucis_c_api.rst` - Placeholder for C API wrapper (215 bytes)
- Other: XML, YAML, schema reference, reporting APIs

**Reference Material**:
- `UCIS_Version_1.0_Final_June-2012.md` - Complete LRM (29,979 lines) describing the C API
- Contains detailed descriptions of all API functions, data structures, and concepts
- Chapter 8 covers the C API functions (`ucis_*` functions)
- Chapters 4-7 cover data model, schema, and concepts

### Python API Structure

**Core Class Hierarchy**:
```
Obj (base for all UCIS objects)
  ├─ Scope (base container class)
  │   ├─ UCIS (root database scope)
  │   ├─ InstanceScope
  │   ├─ CovScope
  │   │   ├─ FuncCovScope
  │   │   │   ├─ CvgScope
  │   │   │   │   ├─ Covergroup
  │   │   │   │   └─ Coverpoint
  │   │   │   │       └─ Cross
  │   │   │   └─ DUScope
  │   └─ CoverType
  └─ CoverItem (coverage measurement base)
```

**Key Classes Requiring Documentation** (47 total files):
- `obj.py` - Base object class with property interface
- `scope.py` - Base scope container
- `ucis.py` - Root database API
- `covergroup.py`, `coverpoint.py`, `cross.py` - Functional coverage
- `cover_item.py`, `cover_data.py`, `cover_index.py` - Coverage measurements
- `history_node.py`, `test_data.py` - Test tracking
- `source_info.py`, `file_handle.py` - Source location
- Plus 30+ supporting classes (enums, scopes, properties, etc.)

## Documentation Strategy

### Adapting C API to Python OO API

The UCIS LRM describes a C API with function-based calls like:

```c
ucis_HandleT ucis_CreateScope(
    ucis_HandleT db,
    ucis_HandleT parent,
    const char* name,
    /* ... more params ... */
);
```

The Python API uses an object-oriented approach:

```python
scope = parent.createScope(
    name,
    sourceinfo,
    weight,
    source_type,
    scope_type,
    flags
)
```

**Adaptation Rules**:

1. **Function → Method**: C functions become methods on appropriate classes
   - `ucis_CreateScope(db, parent, ...)` → `Scope.createScope(...)`
   - `ucis_GetIntProperty(handle, ...)` → `Obj.getIntProperty(...)`

2. **Handle → Self**: First `ucis_HandleT` parameter becomes implicit `self`
   - C: `ucis_GetScopeName(scope_handle)`
   - Python: `scope.getName()`

3. **Return Types**: Adapt from C types to Python types
   - `ucis_HandleT` → object references
   - `int*` (out params) → return values or tuples
   - `const char*` → `str`
   - C arrays → Python lists/iterators

4. **Naming Convention**: Python uses `camelCase` (LRM uses `snake_case`)
   - C: `ucis_create_scope()`
   - Python: `createScope()`

5. **Error Handling**: C return codes → Python exceptions
   - Document exceptions raised in docstrings

### Docstring Format

Use **Google Style** Python docstrings (compatible with Sphinx):

```python
class Scope(Obj):
    """Base class for all UCIS scope objects.
    
    A scope represents a hierarchical container in the UCIS coverage model.
    Scopes can contain other scopes (forming a hierarchy) and cover items
    (measurement data). This class provides the foundation for all scope types
    including instances, design units, covergroups, and more.
    
    The scope hierarchy mirrors the design hierarchy and functional coverage
    structure. Each scope has properties like weight, goal, and source location.
    
    Attributes:
        weight (int): Relative importance for coverage computation
        goal (int): Target coverage percentage (0-100)
        
    Note:
        This is an abstract base class. Use factory methods to create
        specific scope types (createInstance, createCovergroup, etc.)
        
    See Also:
        UCIS LRM Section 5.1 "Scope Objects"
        UCIS LRM Section 8.5 "Scope Functions"
    """
    
    def createScope(
        self,
        name: str,
        sourceinfo: SourceInfo,
        weight: int,
        source_type: SourceT,
        scope_type: ScopeTypeT,
        flags: int
    ) -> 'Scope':
        """Create a child scope within this scope.
        
        Creates a new scope as a child of the current scope. The type of
        scope created depends on the scope_type parameter. Scopes form a
        hierarchical tree structure representing the design hierarchy or
        functional coverage organization.
        
        Args:
            name: Unique name for this scope within its parent
            sourceinfo: Source file location where scope is defined,
                or None if not applicable
            weight: Relative weight for coverage computation (typically 1)
            source_type: HDL source language (VLOG, VHDL, SV, etc.)
            scope_type: Type of scope to create (INSTANCE, DU_MODULE,
                COVERGROUP, etc.)
            flags: Bitwise OR of scope flags from ScopeFlagsT
            
        Returns:
            Newly created Scope object of the appropriate subclass
            
        Raises:
            ValueError: If name is empty or contains path separator
            TypeError: If parent scope type doesn't allow this child type
            
        Example:
            >>> top = db.createScope("top", None, 1, SourceT.SV,
            ...                      ScopeTypeT.INSTANCE, 0)
            >>> sub = top.createScope("sub", src_info, 1, SourceT.SV,
            ...                       ScopeTypeT.INSTANCE, 0)
            
        Note:
            The scope name must be unique among siblings. Use the path
            separator character (default '/') to create hierarchical names.
            
        See Also:
            createInstance(): Convenience method for INSTANCE scopes
            createCovergroup(): Convenience method for COVERGROUP scopes
            UCIS LRM Section 8.5.1 "ucis_CreateScope"
        """
        raise UnimplError()
```

**Key Elements**:
- One-line summary
- Detailed description with context
- Args section with type hints and descriptions
- Returns section
- Raises section for exceptions
- Example section showing usage
- Note section for caveats
- See Also section with LRM references

## Documentation Work Plan

### Phase 1: Foundation Classes (Week 1)

**Priority: CRITICAL** - These are the base classes used by all code.

#### 1.1 Base Object Classes

- [ ] **`obj.py` (Obj class)** - Base for all UCIS objects
  - Reference: LRM Section 8.4 "Attribute Functions"
  - Methods: `getIntProperty`, `setIntProperty`, `getRealProperty`, `setRealProperty`, 
    `getStringProperty`, `setStringProperty`, `getHandleProperty`, `setHandleProperty`, `accept`
  - 10 methods to document

- [ ] **`scope.py` (Scope class)** - Base scope container
  - Reference: LRM Section 8.5 "Scope Functions", Section 5.1 "Scope Objects"
  - Methods: `createScope`, `createInstance`, `createToggle`, `createCovergroup`, 
    `createCoverpoint`, `createNextCover`, `getWeight`, `setWeight`, `getGoal`, `setGoal`,
    `getName`, `getSourceInfo`, `getType`, iterators
  - ~20 methods to document

#### 1.2 Core Type Classes

- [ ] **`scope_type_t.py` (ScopeTypeT enum)** - Scope type enumeration
  - Reference: LRM Section 5.1.1 "Scope Types"
  - Document each enum value (INSTANCE, DU_MODULE, COVERGROUP, etc.)
  - ~15 enum values

- [ ] **`source_t.py` (SourceT enum)** - Source language types
  - Reference: LRM Section 5.4 "Source Language Types"
  - Document each value (VLOG, VHDL, SV, E, PSL, etc.)
  - ~10 enum values

- [ ] **`cover_type_t.py` (CoverTypeT enum)** - Coverage type enumeration
  - Document coverage types (CVGBIN, TOGGLE, etc.)
  - ~8 enum values

- [ ] **`flags_t.py` (FlagsT enum)** - Generic flags
  - Reference: LRM Section 8.5 "Scope Flags"
  - Document flag values
  - ~5 enum values

### Phase 2: Database and Top-Level API (Week 1-2)

**Priority: CRITICAL** - Main entry points for users.

- [ ] **`ucis.py` (UCIS class)** - Root database class
  - Reference: LRM Section 8.1 "Database Functions", Chapter 4 "Data Model"
  - Methods: `isModified`, `modifiedSinceSim`, `getNumTests`, `getAPIVersion`,
    `getWrittenBy`, `setWrittenBy`, `getWrittenTime`, `setWrittenTime`,
    `createFileHandle`, `createHistoryNode`, `write`, `close`
  - ~25 methods to document

- [ ] **`db.py` (DB class)** - Database factory interface
  - Document factory methods for creating databases
  - Note: Currently mostly stub, document intended interface
  - ~5 methods

- [ ] **`file_handle.py` (FileHandle class)** - Source file reference
  - Reference: LRM Section 8.12 "Coverage Source File Functions"
  - Methods: `getFileName`, file management
  - ~5 methods

- [ ] **`source_info.py` (SourceInfo class)** - Source location
  - Reference: LRM Section 8.5.23 "Source Info"
  - Constructor and accessors
  - ~5 methods

### Phase 3: Coverage Data Classes (Week 2)

**Priority: HIGH** - Core coverage measurement.

- [ ] **`cover_item.py` (CoverItem class)** - Base coverage item
  - Reference: LRM Section 8.11 "Coveritem Functions", Section 5.3 "Cover Items"
  - Methods: Property accessors for goal, data, at_least, weight
  - ~15 methods

- [ ] **`cover_data.py` (CoverData class)** - Coverage data container
  - Reference: LRM Section 8.11.3 "ucis_GetCoverData"
  - Constructor parameters: `goal`, `weight`, `data`, `limit`
  - Document all fields
  - ~8 attributes + constructor

- [ ] **`cover_index.py` (CoverIndex class)** - Coverage item reference
  - Reference: LRM Section 8.7 "Coveritem Traversal"
  - Methods for indexing and accessing cover items
  - ~5 methods

- [ ] **`cover_flags_t.py` (CoverFlagsT enum)** - Coverage flags
  - Reference: LRM Section 8.11.6 "ucis_GetCoverFlag"
  - Document flag values (ENABLED, ACTIVE, etc.)
  - ~8 enum values

### Phase 4: Functional Coverage Classes (Week 2-3)

**Priority: HIGH** - User-facing functional coverage API.

- [ ] **`covergroup.py` (Covergroup class)** - Coverage group
  - Reference: LRM Section 6.3 "Functional Coverage", Section 8.5 "Scope Functions"
  - Methods: `getPerInstance`, `setPerInstance`, `createCoverpoint`, `createCross`,
    `createCoverInstance`
  - ~10 methods

- [ ] **`coverpoint.py` (Coverpoint class)** - Coverage point
  - Reference: LRM Section 6.3.2 "Coverpoints"
  - Methods: `createBin`, `getScopeGoal`, `setScopeGoal`, bin management
  - ~12 methods

- [ ] **`cross.py` (Cross class)** - Cross coverage
  - Reference: LRM Section 6.3.3 "Cross Coverage", Section 8.5.17 "ucis_GetIthCrossedCvp"
  - Methods: `getNumCrossedCoverpoints`, `getIthCrossedCoverpoint`
  - ~8 methods

- [ ] **`cvg_scope.py` (CvgScope class)** - Coverage scope base
  - Methods: Coverage-specific scope operations
  - ~8 methods

- [ ] **`cvg_bin_scope.py` (CvgBinScope class)** - Coverage bin
  - Reference: LRM Section 6.3.4 "Bins"
  - ~5 methods

- [ ] **`illegal_bin_scope.py`, `ignore_bin_scope.py`** - Special bin types
  - ~5 methods each

### Phase 5: Scope Type Classes (Week 3)

**Priority: MEDIUM** - Specialized scope implementations.

- [ ] **`instance_scope.py` (InstanceScope class)** - Instance scope
  - Reference: LRM Section 6.1 "Design Hierarchy", Section 8.5.7 "ucis_CreateInstance"
  - ~8 methods

- [ ] **`du_scope.py` (DUScope class)** - Design unit scope
  - Reference: LRM Section 6.1.1 "Design Units"
  - ~8 methods

- [ ] **`func_cov_scope.py` (FuncCovScope class)** - Functional coverage scope
  - ~8 methods

- [ ] **`cov_scope.py` (CovScope class)** - Generic coverage scope
  - ~8 methods

- [ ] **`cover_type.py` (CoverType class)** - Coverage type container
  - ~5 methods

### Phase 6: History and Test Management (Week 3-4)

**Priority: MEDIUM** - Test tracking and history.

- [ ] **`history_node.py` (HistoryNode class)** - Test history node
  - Reference: LRM Section 4.3 "History Nodes", Section 8.13 "History Node Functions"
  - Methods: `getHistoryKind`, `getTestData`, `setTestData`, parent/child navigation
  - ~12 methods

- [ ] **`history_node_kind.py` (HistoryNodeKind enum)** - History node types
  - Reference: LRM Section 8.13.3 "ucis_GetHistoryKind"
  - Document kinds: TEST, TESTPLAN, MERGE, etc.
  - ~6 enum values

- [ ] **`test_data.py` (TestData class)** - Test execution data
  - Reference: LRM Section 8.14 "Coverage Test Management"
  - Attributes: `teststatus`, `toolcategory`, `date`, `simargs`, etc.
  - ~10 attributes

- [ ] **`test_status_t.py` (TestStatusT enum)** - Test status enumeration
  - Reference: LRM Section 8.14.1 "Test Status typedef"
  - Values: OK, WARNING, ERROR, FATAL
  - ~4 enum values

- [ ] **`instance_coverage.py` (InstanceCoverage class)** - Instance coverage data
  - ~8 methods

### Phase 7: Supporting Classes (Week 4)

**Priority: LOW** - Utility and supporting classes.

- [ ] **`name_value.py` (NameValue class)** - Name-value pairs
  - Reference: LRM Section 8.4 "Attributes"
  - ~3 methods

- [ ] **`int_property.py`, `real_property.py`, `str_property.py`** - Property enums
  - Reference: LRM Section 8.4 "Attribute Functions"
  - Document each property enum value
  - ~15 enum values each

- [ ] **`handle_property.py` (HandleProperty enum)** - Handle property types
  - ~5 enum values

- [ ] **`statement_id.py` (StatementId class)** - Statement identifier
  - Reference: LRM Section 8.12 "Source File Functions"
  - ~5 methods

- [ ] **`source_file.py` (SourceFile class)** - Source file representation
  - ~5 methods

- [ ] **`toggle_*.py` files** - Toggle coverage types
  - Reference: LRM Section 8.15 "Toggle Functions", Section 6.4 "Toggle Coverage"
  - `toggle_dir_t.py`, `toggle_metric_t.py`, `toggle_type_t.py`
  - ~5 enum values each

- [ ] **`unimpl_error.py` (UnimplError exception)** - Unimplemented method exception
  - ~2 methods

### Phase 8: Update RST Documentation (Week 4-5)

**Priority: HIGH** - User-facing documentation.

#### 8.1 Create New API Documentation Files

- [ ] **`doc/source/reference/api_overview.rst`** - NEW
  - Overview of the Python OO API
  - Comparison with C API
  - Basic usage patterns
  - Class hierarchy diagram (ASCII art or image)
  - Quick start examples
  - ~500 lines

- [ ] **`doc/source/reference/api_core_classes.rst`** - NEW
  - Document core classes: Obj, Scope, UCIS
  - Usage examples
  - Common patterns
  - ~300 lines

- [ ] **`doc/source/reference/api_coverage.rst`** - NEW
  - Functional coverage classes
  - Document: Covergroup, Coverpoint, Cross, CoverItem, CoverData
  - Examples of creating and measuring coverage
  - ~400 lines

- [ ] **`doc/source/reference/api_scopes.rst`** - NEW
  - Scope hierarchy and types
  - Document: InstanceScope, DUScope, CvgScope
  - Examples of scope creation and traversal
  - ~300 lines

- [ ] **`doc/source/reference/api_history.rst`** - NEW
  - Test history and tracking
  - Document: HistoryNode, TestData
  - Merge tracking examples
  - ~200 lines

- [ ] **`doc/source/reference/api_types.rst`** - NEW
  - Enumerations and type definitions
  - Document all enum classes with values
  - ~300 lines

#### 8.2 Update Existing Files

- [ ] **`doc/source/reference/ucis_oo_api.rst`** - EXPAND
  - Currently 12 lines (placeholder)
  - Replace with comprehensive API reference using Sphinx autodoc
  - Add introduction and organization
  - Use `.. autoclass::` directives for all main classes
  - Group classes by category
  - Target: ~200 lines

- [ ] **`doc/source/reference/reference.rst`** - UPDATE
  - Add new API documentation files to toctree
  - Improve organization and navigation
  - Add section on Python vs C API differences
  - ~100 lines total

- [ ] **`doc/source/introduction.rst`** - UPDATE
  - Add section on using the Python OO API
  - Expand examples with more context
  - Add "When to use OO API vs C-style API" guidance
  - ~50 lines of additions

- [ ] **`doc/source/index.rst`** - UPDATE
  - Ensure API reference is prominently featured
  - Update feature list to highlight documented API
  - ~20 lines of changes

### Phase 9: Examples and Tutorials (Week 5)

**Priority: MEDIUM** - Practical usage guidance.

- [ ] **`doc/source/tutorials/basic_usage.rst`** - NEW
  - Complete tutorial for creating a database
  - Hierarchy creation example
  - Coverage data recording
  - Writing and reading databases
  - ~400 lines

- [ ] **`doc/source/tutorials/functional_coverage.rst`** - NEW
  - Covergroup creation tutorial
  - Coverpoint and cross examples
  - Per-instance vs per-design unit coverage
  - Bin definition examples
  - ~500 lines

- [ ] **`doc/source/tutorials/merge_and_history.rst`** - NEW
  - Test history tracking
  - Merging databases
  - Query history information
  - ~300 lines

- [ ] **`doc/source/examples/`** directory - NEW
  - Create standalone example scripts
  - `01_simple_database.py`
  - `02_functional_coverage.py`
  - `03_hierarchy.py`
  - `04_merge.py`
  - Each with detailed inline comments
  - ~200 lines each

### Phase 10: Validation and Review (Week 5-6)

**Priority: CRITICAL** - Quality assurance.

- [ ] **Docstring Validation**
  - Run Sphinx with `-W` (warnings as errors)
  - Check all cross-references resolve
  - Verify all `See Also` LRM references are accurate
  - Run docstring linter (pydocstyle)

- [ ] **Build Documentation**
  - Build HTML documentation: `make -C doc html`
  - Build PDF if applicable
  - Review rendering of all pages
  - Check navigation and search

- [ ] **Code Examples Testing**
  - Extract and test all example code
  - Ensure examples run without errors
  - Add examples to automated tests if possible

- [ ] **Technical Review**
  - Cross-check against UCIS LRM for accuracy
  - Verify Python API behavior matches descriptions
  - Review with maintainers

- [ ] **User Testing**
  - Have new users try following the documentation
  - Collect feedback on clarity
  - Identify gaps or confusing sections

## Documentation Standards

### Docstring Guidelines

1. **Every public class must have a docstring**
   - One-line summary
   - Detailed description
   - Attributes section (if applicable)
   - See Also with LRM references

2. **Every public method must have a docstring**
   - One-line summary
   - Args section with all parameters
   - Returns section
   - Raises section (if exceptions possible)
   - Example (for key methods)
   - See Also with LRM references

3. **Use type hints in signatures**
   ```python
   def createScope(
       self,
       name: str,
       sourceinfo: SourceInfo,
       weight: int,
       source_type: SourceT,
       scope_type: ScopeTypeT,
       flags: int
   ) -> 'Scope':
   ```

4. **Reference the LRM consistently**
   - Format: `UCIS LRM Section X.Y "Title"`
   - Always provide section number and title
   - Link to C API function when applicable

5. **Provide examples for complex methods**
   - Use doctest format when possible
   - Show common use cases
   - Include expected output

### RST Documentation Guidelines

1. **Use consistent heading levels**
   ```rst
   ############
   Level 1 (Chapter)
   ############
   
   Level 2 (Section)
   ================
   
   Level 3 (Subsection)
   --------------------
   
   Level 4 (Subsubsection)
   ^^^^^^^^^^^^^^^^^^^^^^
   ```

2. **Use Sphinx directives effectively**
   - `.. autoclass::` for automatic API docs
   - `.. code-block:: python` for examples
   - `.. note::` for important information
   - `.. seealso::` for cross-references
   - `.. versionadded::` for new features

3. **Include working examples**
   - All code must be tested
   - Show imports
   - Show complete workflows

4. **Cross-reference consistently**
   - Link between related sections
   - Link to external LRM document
   - Use `:class:`, `:meth:`, `:func:` roles

## Implementation Notes

### C to Python API Mapping

Common patterns for adapting C API to Python:

| C API Pattern | Python OO Pattern | Example |
|---------------|-------------------|---------|
| `ucis_CreateScope(db, parent, ...)` | `parent.createScope(...)` | Scope.createScope() |
| `ucis_GetScopeName(scope)` | `scope.getName()` | Scope.getName() |
| `ucis_SetIntProperty(obj, prop, val)` | `obj.setIntProperty(prop, val)` | Obj.setIntProperty() |
| `ucis_ScopeIterate(scope, ...)` | `for s in scope.scopes(): ...` | Scope.scopes() |
| `ucis_CoverIterate(scope, ...)` | `for c in scope.coverItems(): ...` | Scope.coverItems() |

### LRM Section Mapping

Key sections from UCIS LRM to Python classes:

- **Chapter 4**: Data model concepts → Introduction and overview docs
- **Chapter 5**: Schema → Class structure and relationships
- **Chapter 6**: Data models → Specific coverage type classes
- **Section 8.1-8.3**: Database functions → UCIS class
- **Section 8.4**: Attributes → Obj class property methods
- **Section 8.5**: Scopes → Scope class and subclasses
- **Section 8.7-8.11**: Coverage → CoverItem and related classes
- **Section 8.13**: History → HistoryNode class
- **Section 8.14**: Tests → TestData class

### Tools and Automation

1. **Sphinx Configuration**
   - Enable autodoc extension
   - Configure napoleon for Google-style docstrings
   - Set up intersphinx for external links
   - Enable viewcode for source links

2. **Linting**
   - Use `pydocstyle` for docstring style checking
   - Use `mypy` for type hint validation
   - Use `pylint` for code quality

3. **Testing**
   - Use `doctest` for inline examples
   - Create separate test suite for examples
   - Validate all cross-references build correctly

## Success Criteria

Documentation is complete when:

1. ✅ All 47 Python files have class docstrings
2. ✅ All public methods have complete docstrings with Args/Returns/Raises
3. ✅ All enum types have value descriptions
4. ✅ Sphinx builds without warnings (`make -C doc html -W`)
5. ✅ All examples can be executed and work correctly
6. ✅ RST documentation includes API reference with autodoc
7. ✅ Navigation between RST docs and code is seamless
8. ✅ LRM references are accurate and complete
9. ✅ New users can learn the API from documentation alone
10. ✅ Documentation passes technical review

## Estimated Effort

Based on analysis:
- **47 Python files** requiring docstrings
- **~500 methods** to document across all classes
- **~100 enum values** to describe
- **8 new RST files** to create (~2,500 lines)
- **4 RST files** to update (~400 lines)
- **5 example scripts** to create (~1,000 lines)

**Total estimated effort**: 5-6 weeks for one developer

Breakdown by phase:
- Phase 1-7 (Python docstrings): 3-4 weeks
- Phase 8 (RST updates): 1 week
- Phase 9 (Examples): 0.5 weeks
- Phase 10 (Validation): 0.5-1 week

## Dependencies and Prerequisites

1. **UCIS LRM Access**: The markdown version is already available
2. **Sphinx Setup**: Existing doc infrastructure is in place
3. **Type Hints**: Python 3.7+ supports type hints
4. **Testing Framework**: pytest is already configured

## Risk Mitigation

**Risks**:
1. API behavior may not exactly match LRM C API
   - Mitigation: Note differences clearly in docstrings
2. Some methods may be unimplemented (raise UnimplError)
   - Mitigation: Document as "Not yet implemented"
3. Examples may become outdated
   - Mitigation: Include examples in automated tests

## Next Steps

To begin implementation:

1. Review and approve this plan
2. Set up Sphinx napoleon extension for Google-style docstrings
3. Start with Phase 1 (Foundation Classes)
4. Implement in order, validating each phase before moving on
5. Use this checklist to track progress

---

**Plan Created**: 2026-02-11
**Document Version**: 1.0
**Status**: Ready for Review
