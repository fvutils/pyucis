# UCIS Coverage Gap Analysis and Implementation Plan

## 1. Executive Summary

This document provides a comprehensive review of the UCIS 1.0 API and data model
(as defined in `UCIS_Version_1.0_Final_June-2012.md`) versus the current Python
object-oriented API, the Mem (in-memory) backend, and the SQLite backend. It
identifies gaps in API representation, backend implementation, and test coverage,
and proposes a prioritised plan to close them.

---

## 2. UCIS Data Model and API Overview

The UCIS standard defines the following top-level concepts:

| Concept | Python Class | Notes |
|---------|-------------|-------|
| Database root | `UCIS` | Inherits `Scope` |
| Scope hierarchy | `Scope` | Base for all structural nodes |
| Design unit | `DUScope` | DU_MODULE, DU_ARCH, DU_PACKAGE, DU_PROGRAM, DU_INTERFACE |
| Instance | `InstanceScope` | INSTANCE scope with DU reference |
| Covergroup | `Covergroup` | Functional coverage type definition |
| Covergroup instance | `CvgScope` | COVERINSTANCE scope |
| Coverpoint | `Coverpoint` | Within a covergroup |
| Cross | `Cross` | Cross coverage over 2+ coverpoints |
| Toggle | `Scope` (TOGGLE type) | Signal transition coverage |
| FSM | SQLite-only `SqliteFSMScope` | State/transition coverage |
| Assertions | Not implemented | ASSERT/COVER directive coverage |
| Code coverage | `Scope` (various types) | STMT, BRANCH, EXPR, COND, COVBLOCK |
| History node | `HistoryNode` | Test metadata |
| File handle | `FileHandle` | Source file reference |
| Cover item | `CoverIndex` | Leaf coverage bin |
| Attributes | SQLite-only | User-defined key-value metadata |
| Tags | SQLite-only | Object tagging |
| Formal | Not implemented | Formal/proof coverage |

---

## 3. Python OO Abstract API Gaps

### 3.1 Missing IntProperty Enum Values

The `IntProperty` enum (`src/ucis/int_property.py`) is missing the following
values defined in the UCIS LRM:

| LRM Constant | Status | Notes |
|---|---|---|
| `UCIS_INT_TOGGLE_METRIC` | **Missing** | Toggle metric type (ToggleMetricT) |
| `UCIS_INT_SUPPRESS_MODIFIED` | **Missing** | Suppress modification flag |

### 3.2 RealProperty Enum: Inadequate

`RealProperty` (`src/ucis/real_property.py`) has only a placeholder `b = 0`.
The UCIS LRM defines the following real-valued properties:

| LRM Constant | Status | Notes |
|---|---|---|
| `UCIS_REAL_TEST_SIMTIME` | **Missing** | Simulation time at test end |
| `UCIS_REAL_HIST_CPUTIME` | **Missing** | CPU time for the test run |
| `UCIS_REAL_TEST_COST` | **Missing** | Relative cost of re-running the test |
| `UCIS_REAL_CVG_INST_AVERAGE` | **Missing** | Average coverage across instances |

### 3.3 Missing API Methods on Abstract Classes

#### UCIS (root DB) class — `src/ucis/ucis.py`

| LRM API | Python Status | Notes |
|---|---|---|
| `ucis_GetPathSeparator` / `ucis_SetPathSeparator` | Partial — defined but no standardised tests | |
| `ucis_GetDBVersion` | Partial — stub | |
| `ucis_Open` / `ucis_Close` | Present | |
| `ucis_Write` / `ucis_WriteToInterchangeFormat` | Present | |
| `ucis_OpenFromInterchangeFormat` | Partial | Not generalised |
| `ucis_OpenReadStream` / `ucis_OpenWriteStream` | **Missing** | Streaming model |
| `ucis_WriteStream` / `ucis_WriteStreamScope` | **Missing** | Streaming model |
| `ucis_RegisterErrorHandler` | **Missing** | Error handling callbacks |
| `ucis_GetHistoryNodeParent` | **Missing** | Parent traversal for history |
| `ucis_GetHistoryNodeVersion` | **Missing** | |
| `ucis_CreateHistoryNodeList` | **Missing** | History node lists |
| `ucis_AddToHistoryNodeList` | **Missing** | |
| `ucis_RemoveFromHistoryNodeList` | **Missing** | |
| `ucis_FreeHistoryNodeList` | **Missing** | |
| `ucis_SetHistoryNodeListAssoc` | **Missing** | |
| `ucis_GetHistoryNodeListAssoc` | **Missing** | |
| `ucis_HistoryNodeListIterate` | **Missing** | |
| `ucis_GetNumTests` | Present (`getNumTests`) | |
| `ucis_GetVersionStringProperty` | **Missing** | Separate version query |

#### Scope class — `src/ucis/scope.py`

| LRM API | Python Status | Notes |
|---|---|---|
| `ucis_CreateScope` | Present (`createScope`) | |
| `ucis_CreateInstance` | Present (`createInstance`) | |
| `ucis_CreateInstanceByName` | **Missing** | Create instance by DU name string |
| `ucis_CreateToggle` | Present (`createToggle`) | Mem raises UnimplError |
| `ucis_CreateNextCover` | Present (`createNextCover`) | |
| `ucis_CreateNextTransition` | **Missing from abstract Scope** | FSM only in SQLite |
| `ucis_RemoveScope` | **Missing** | Delete scope |
| `ucis_RemoveCover` | **Missing** | Delete cover item |
| `ucis_GetScopeFlag` / `ucis_SetScopeFlag` | Partial — `getFlags` present; no bit-level set | |
| `ucis_GetScopeFlags` / `ucis_SetScopeFlags` | Partial | |
| `ucis_GetScopeSourceInfo` / `ucis_SetScopeSourceInfo` | Present | |
| `ucis_GetScopeType` | Present (`getScopeType`) | |
| `ucis_GetCoverData` | Partial (via `CoverIndex`) | |
| `ucis_SetCoverData` | **Missing** | Set cover count |
| `ucis_IncrementCover` | Present (`incrementCover` on `CoverIndex`) | |
| `ucis_GetCoverFlag` / `ucis_SetCoverFlag` | **Missing** | Per-cover-item flags |
| `ucis_GetCoverFlags` / `ucis_SetCoverFlags` | **Missing** | |
| `ucis_ScopeIterate` / `ucis_ScopeScan` | Present (`scopes()`) | |
| `ucis_CoverIterate` / `ucis_CoverScan` | Present (`coverItems()`) | |
| `ucis_FreeIterator` | Not needed (Python iterators) | |
| `ucis_GetFSMTransitionStates` | **Missing from abstract API** | |
| `ucis_CallBack` | **Missing** | Traversal callback model |
| `ucis_MatchScopeByUniqueID` | **Missing** | Unique ID lookup |
| `ucis_CaseAwareMatchScopeByUniqueID` | **Missing** | |
| `ucis_MatchCoverByUniqueID` | **Missing** | |
| `ucis_CaseAwareMatchCoverByUniqueID` | **Missing** | |
| `ucis_MatchDU` | **Missing** | Design unit matching |

#### Obj class — `src/ucis/obj.py`

| LRM API | Python Status | Notes |
|---|---|---|
| `ucis_GetIntProperty` | Present | |
| `ucis_SetIntProperty` | Present | |
| `ucis_GetStringProperty` | Present | |
| `ucis_SetStringProperty` | Present | |
| `ucis_GetRealProperty` | Present but untested; RealProperty enum empty | |
| `ucis_SetRealProperty` | Present but untested | |
| `ucis_GetHandleProperty` | **Missing** | Handle-typed properties |
| `ucis_SetHandleProperty` | **Missing** | |
| `ucis_AttrAdd` | **Missing from abstract API** | Attribute management |
| `ucis_AttrMatch` | **Missing from abstract API** | |
| `ucis_AttrNext` | **Missing from abstract API** | |
| `ucis_AttrRemove` | **Missing from abstract API** | |
| `ucis_AddObjTag` | **Missing from abstract API** | Object tagging |
| `ucis_RemoveObjTag` | **Missing from abstract API** | |
| `ucis_ObjectTagsIterate` | **Missing from abstract API** | |
| `ucis_TaggedObjIterate` | **Missing from abstract API** | |
| `ucis_ObjKind` | **Missing** | Object type query |
| `ucis_GetObjType` | **Missing** | |

#### DU/Instance specific

| LRM API | Python Status | Notes |
|---|---|---|
| `ucis_ComposeDUName` | **Missing** | Build "work.module" DU name |
| `ucis_ParseDUName` | **Missing** | Split DU name into library/module |
| `ucis_GetIthCrossedCvp` | Present (`getIthCrossedCoverpoint`) | |

### 3.4 Visitor/Callback Model

The `UCISVisitor` class (`src/ucis/visitors/UCISVisitor.py`) defines only
`visit_du_scope`. The UCIS `ucis_CallBack` mechanism supports arbitrary
scope-type-filtered traversal. The visitor should be extended with methods for
all scope types and a traversal driver that calls them.

### 3.5 Formal Coverage APIs

The following UCIS formal/proof coverage APIs are entirely absent from the
Python API (not needed for most users but part of the standard):

- `ucis_SetFormalStatus` / `ucis_GetFormalStatus`
- `ucis_SetFormalRadius` / `ucis_GetFormalRadius`
- `ucis_SetFormalWitness` / `ucis_GetFormalWitness`
- `ucis_AddFormalEnv` / `ucis_FormalEnvGetData`
- `ucis_AssocFormalInfoTest` / `ucis_FormalTestGetInfo`
- `ucis_SetFormallyUnreachableCoverTest` / `ucis_ClearFormallyUnreachableCoverTest`

---

## 4. Mem Backend Implementation Gaps

### 4.1 Scope Types Not Supported in `createScope`

`MemScope.createScope()` raises `NotImplementedError` for:

| Scope Type | LRM Coverage Type | Priority |
|---|---|---|
| `TOGGLE` | Toggle coverage | **High** — createToggle also raises UnimplError |
| `BRANCH` | Branch coverage | High |
| `EXPR` | Expression coverage | Medium |
| `COND` | Condition coverage | Medium |
| `COVBLOCK` | Block coverage | Medium |
| `FSM` | FSM coverage | High |
| `ASSERT` | Assertion directive | Medium |
| `COVER` | Cover directive | Medium |
| `PROCESS` | HDL process | Low |
| `BLOCK` | HDL block | Low |
| `FUNCTION` | HDL function | Low |
| `FORKJOIN` | HDL fork-join | Low |
| `GENERATE` | HDL generate | Low |
| `TASK` | HDL task | Low |
| `PROGRAM` | SV program | Low |
| `PACKAGE` | Package | Low |
| `INTERFACE` | SV interface | Low |
| `CVGBINSCOPE` | SV bin scope | Medium |
| `ILLEGALBINSCOPE` | Illegal bin scope | Medium |
| `IGNOREBINSCOPE` | Ignore bin scope | Medium |

### 4.2 Missing Mem Method Implementations

| Method / Feature | File | Status |
|---|---|---|
| `createToggle()` | `mem_scope.py` | Raises `UnimplError` |
| FSM scope (states, transitions) | No mem FSM file | **Not implemented** |
| Assertion scope | No mem assertion file | **Not implemented** |
| `getSourceFiles()` | `mem_ucis.py` | Not implemented (returns None) |
| `getCoverInstances()` | `mem_ucis.py` | Not implemented (returns None) |
| Attribute storage (`setStringProperty` for custom attrs) | `mem_obj.py` | Incomplete |
| `setIntProperty` for many properties | `mem_scope.py` | Only SCOPE_WEIGHT/COVER_GOAL stored |
| Cover item flags | `mem_cover_index.py` | Not stored |
| `getCoverFlag` / `setCoverFlag` | Absent | Not implemented |
| `MemFactory.clone()` | `mem_factory.py` | Stub — `pass` |
| `RealProperty` getter/setter | `mem_obj.py` | Not implemented |
| Toggle `TOGGLE_METRIC` property | `mem_toggle_instance_scope.py` | Missing TOGGLE_METRIC |

### 4.3 Incomplete Mem Implementations

| Feature | Notes |
|---|---|
| `MemCoverpoint` | Minimal — no bin-level details beyond name/count |
| `MemCross` | Has crossed-cvp tracking but no bin coverage counts |
| `MemToggleInstanceScope` | Partially implemented; TOGGLE_METRIC missing |
| `MemDUScope` | Only DU scopes work; raises `UnimplError` for others |

---

## 5. SQLite Backend Implementation Gaps

### 5.1 Database-Level

| Feature | Status |
|---|---|
| `getSourceFiles()` | Returns `[]` (stub) |
| `getCoverInstances()` | Returns `[]` (stub) |
| `getDBVersion()` | Returns hardcoded stub |
| Error handler registration | Not implemented |
| Streaming read/write | Not implemented |

### 5.2 Scope Creation

`SqliteScope.createScope()` stores all scope types generically in the scopes
table but returns a plain `SqliteScope`. It only returns specialised subclasses
(`SqliteCovergroup`, `SqliteCoverpoint`, `SqliteCross`, `SqliteToggleScope`,
`SqliteFSMScope`) when reading back. This means FSM and toggle specialised
methods are unavailable immediately after creation. Additionally:

| Scope Type | Status |
|---|---|
| `ASSERT` / `COVER` | Stored generically; no assertion-specific API |
| `EXPR` / `COND` / `COVBLOCK` | Stored generically; no specialised API |
| `PROCESS` / `BLOCK` / `FUNCTION` | Stored generically; no specialised API |

### 5.3 Cover Item Level

| Feature | Status |
|---|---|
| `getCoverFlag` / `setCoverFlag` | **Missing** |
| `getCoverFlags` / `setCoverFlags` | **Missing** |
| `setCoverData` | **Missing** (can only increment) |
| IGNORE/ILLEGAL/DEFAULT bin types | Stored but no specialised getters |

### 5.4 Attribute and Tag API

The `sqlite_attributes.py` module implements attributes internally but:
- Attribute API is not exposed via the abstract `Obj` interface
- No `attrAdd`, `attrMatch`, `attrNext`, `attrRemove` on `SqliteObj`
- Tag API (`addObjTag` etc.) similarly not in abstract interface

### 5.5 FSM API Location

`SqliteFSMScope` has rich FSM methods (`createState`, `createTransition`, etc.)
but these are not declared in any abstract base class, making them
backend-specific. The abstract `Scope` class needs `createNextTransition()` and
related FSM accessor methods.

---

## 6. Test Coverage Gaps

### 6.1 Coverage Type Tests (all backends)

| Coverage Type | Test File Exists | Tests Exist |
|---|---|---|
| Covergroup / Coverpoint / Cross | `test_api_covergroups.py`, `test_api_coverpoints.py`, `test_api_cross_coverage.py` | Yes |
| Statement / Branch / Block | `test_api_code_coverage.py` | Yes — but Mem backend likely fails |
| Condition coverage | `test_api_code_coverage.py` | Yes — but Mem backend likely fails |
| Expression coverage | `test_api_code_coverage.py` | Yes — but Mem backend likely fails |
| **Toggle coverage** | None | **No tests** |
| **FSM coverage** | None | **No tests** |
| **Assertion (ASSERT/COVER)** | None | **No tests** |
| **CVGBINSCOPE / ILLEGALBINSCOPE / IGNOREBINSCOPE** | None | **No tests** |

### 6.2 API Feature Tests

| Feature | Tests |
|---|---|
| File handles | `test_api_file_handles.py` — basic tests exist |
| Scope hierarchy (DU + INSTANCE) | `test_api_scope_hierarchy.py` — basic tests exist |
| **Multiple DU types** (DU_ARCH, DU_PACKAGE, DU_PROGRAM, DU_INTERFACE) | **No tests** |
| **COVERINSTANCE scope** | **No tests** |
| **HDL scope types** (PROCESS, BLOCK, FUNCTION, FORKJOIN, GENERATE, TASK) | **No tests** |
| **Path separator** | **No tests** |
| **getSourceFiles()** | **No tests** |
| **getCoverInstances()** | **No tests** |

### 6.3 Property Tests

| Feature | Tests |
|---|---|
| IntProperty — SCOPE_WEIGHT, SCOPE_GOAL | Partial (`test_api_covergroups.py`) |
| IntProperty — CVG_ATLEAST, CVG_AUTOBINMAX, CVG_DETECTOVERLAP, CVG_STROBE | Partial |
| IntProperty — TOGGLE_TYPE, TOGGLE_DIR, TOGGLE_COVERED | **No tests** |
| IntProperty — TOGGLE_METRIC | **No tests** (also missing from enum) |
| IntProperty — BRANCH_HAS_ELSE, BRANCH_ISCASE | **No tests** |
| IntProperty — STMT_INDEX | **No tests** |
| IntProperty — FSM_STATEVAL | **No tests** |
| IntProperty — COVER_GOAL, COVER_LIMIT, COVER_WEIGHT | **No tests** |
| **RealProperty — SIMTIME, CPUTIME, COST, CVG_INST_AVERAGE** | **No tests** (enum also empty) |
| StrProperty — HIST_CMDLINE, HIST_RUNCWD, TEST_DATE, TEST_USERNAME etc. | **No tests** |
| StrProperty — DU_SIGNATURE, DESIGN_VERSION_ID | **No tests** |
| StrProperty — TOGGLE_CANON_NAME | **No tests** |
| StrProperty — EXPR_TERMS | **No tests** |
| StrProperty — UNIQUE_ID | **No tests** |

### 6.4 History Node Tests

| Feature | Tests |
|---|---|
| Basic createHistoryNode + setTestData | Present (`test_api_basic.py`) |
| **All HistoryNode properties** (cmd, args, seed, cwd, date, username, cost, toolcategory, vendor info) | **No systematic tests** |
| **History node list operations** (CreateHistoryNodeList, AddToHistoryNodeList, etc.) | **No tests** |
| **getHistoryNodeParent** | **No tests** |

### 6.5 Cover Item Tests

| Feature | Tests |
|---|---|
| Basic coverpoint bins (create + count) | `test_api_coverpoints.py` |
| **Cover item flags** (getCoverFlag / setCoverFlag) | **No tests** |
| **COVER_GOAL / COVER_LIMIT / COVER_WEIGHT properties** | **No tests** |
| **IGNORE/ILLEGAL/DEFAULT bin types** | **No tests** |
| **setCoverData** | **No tests** |
| **IncrementCover** | Partial (in coverage report tests) |

### 6.6 Attribute and Tag Tests

| Feature | Tests |
|---|---|
| **AttrAdd / AttrMatch / AttrNext / AttrRemove** | **No tests** |
| **AddObjTag / RemoveObjTag / ObjectTagsIterate** | **No tests** |

### 6.7 Traversal / Lookup Tests

| Feature | Tests |
|---|---|
| **MatchScopeByUniqueID** | **No tests** |
| **MatchCoverByUniqueID** | **No tests** |
| **CallBack traversal** | **No tests** |
| **DU name parse / compose** | **No tests** |
| **Scope deletion (RemoveScope)** | **No tests** |
| **Cover item deletion (RemoveCover)** | **No tests** |

---

## 7. Implementation Plan

The following work is ordered by priority. Phase 1 addresses the most impactful
API and implementation gaps; later phases extend to less-commonly-used features.

### Phase 1 — High Priority: Fixes to Core API and Missing Backends

#### 1.1 IntProperty: Add Missing Entries

- Add `TOGGLE_METRIC` to `IntProperty` enum  
- Add `SUPPRESS_MODIFIED` to `IntProperty` enum

#### 1.2 RealProperty: Populate Properly

Replace the placeholder `b = 0` with:
- `SIMTIME` (UCIS_REAL_TEST_SIMTIME)
- `CPUTIME` (UCIS_REAL_HIST_CPUTIME)
- `COST` (UCIS_REAL_TEST_COST)
- `CVG_INST_AVERAGE` (UCIS_REAL_CVG_INST_AVERAGE)

#### 1.3 Mem Backend: Implement Toggle Coverage

- Implement `MemScope.createToggle()` (currently raises UnimplError)
- Create `MemToggleScope` class with toggle metric, type, direction, coverage bins
- Support TOGGLE_METRIC, TOGGLE_TYPE, TOGGLE_DIR IntProperty on mem toggle scopes
- Add TOGGLE_CANON_NAME StrProperty

#### 1.4 Mem Backend: Implement FSM Coverage

- Create `MemFSMScope` class analogous to `SqliteFSMScope`
- Support `createState()`, `createTransition()`, state/transition iteration
- Add FSM_STATEVAL IntProperty support
- Add `createNextTransition()` to abstract `Scope` base class (currently missing)

#### 1.5 Mem Backend: Support BRANCH, COND, EXPR, COVBLOCK Scope Types

`MemScope.createScope()` currently raises `NotImplementedError` for BRANCH, EXPR, COND,
and COVBLOCK. These should return a plain `MemScope` (or a thin subclass) so code
coverage data can be stored in the Mem backend, consistent with what SQLite stores.

#### 1.6 Abstract Scope: Add createNextTransition

Add `createNextTransition()` to the abstract `Scope` class so FSM creation is
portable across backends.

#### 1.7 Test Suite: Toggle Coverage Tests

New test file `tests/unit/api/test_api_toggle_coverage.py`:
- `test_create_toggle_scope` — create a toggle scope under an instance
- `test_toggle_properties` — TOGGLE_TYPE, TOGGLE_DIR, TOGGLE_METRIC, TOGGLE_CANON_NAME
- `test_toggle_bins` — create 0→1 and 1→0 bins via createNextCover
- `test_toggle_covered_property` — TOGGLE_COVERED after hitting both transitions
- `test_toggle_multibit` — toggle scope on a multi-bit signal

#### 1.8 Test Suite: FSM Coverage Tests

New test file `tests/unit/api/test_api_fsm_coverage.py`:
- `test_create_fsm_scope` — create FSM scope under an instance
- `test_fsm_states` — create states, verify count, iterate states
- `test_fsm_transitions` — create transitions, verify count
- `test_fsm_state_value` — FSM_STATEVAL IntProperty
- `test_fsm_coverage_bins` — createNextCover for state/transition bins

---

### Phase 2 — Medium Priority: Assertion Coverage, Bin Scopes, Property Coverage

#### 2.1 Mem and SQLite: Assertion Coverage

Implement ASSERT and COVER directive scope types:
- ASSERTBIN (fail count), PASSBIN (pass count), VACUOUSBIN, DISABLEDBIN,
  ATTEMPTBIN, ACTIVEBIN, PEAKACTIVEBIN, FAILBIN, COVERBIN cover item types
- Thin `MemAssertScope` / `SqliteAssertScope` (or handle generically via
  base `MemScope` / `SqliteScope` with correct CoverTypeT on bins)
- Add `createAssertScope()` convenience method or document the pattern

#### 2.2 Test Suite: Assertion Coverage Tests

New test file `tests/unit/api/test_api_assertion_coverage.py`:
- `test_create_assert_scope` — ASSERT scope type
- `test_create_cover_directive_scope` — COVER scope type
- `test_assertion_bins` — ASSERTBIN, PASSBIN, VACUOUSBIN, FAILBIN, etc.
- `test_assertion_properties` — verify bin counts

#### 2.3 Test Suite: CVGBINSCOPE / ILLEGALBINSCOPE / IGNOREBINSCOPE Tests

New test file `tests/unit/api/test_api_bin_scopes.py`:
- `test_create_cvgbinscope` — SystemVerilog named bin scope
- `test_create_illegalbinscope` — illegal bin scope
- `test_create_ignorebinscope` — ignore bin scope
- `test_bin_scope_coveritems` — bins within a bin scope
- `test_illegal_bin_detection` — verify ILLEGALBIN type items

#### 2.4 RealProperty: Implement in Mem and SQLite

After adding values to the `RealProperty` enum (Phase 1.2):
- Implement `getRealProperty` / `setRealProperty` in `MemObj` for SIMTIME, CPUTIME, COST
- Verify SQLite `sqlite_obj.py` generic property table can store real values
- Hook up `UCIS_REAL_CVG_INST_AVERAGE` on covergroup scopes

#### 2.5 Test Suite: RealProperty Tests

New test file `tests/unit/api/test_api_real_properties.py`:
- `test_simtime_property` — set/get SIMTIME on history node
- `test_cputime_property` — set/get CPUTIME on history node
- `test_cost_property` — set/get COST on history node
- `test_cvg_inst_average` — get CVG_INST_AVERAGE on covergroup

#### 2.6 Test Suite: Extended StrProperty Tests

New test file `tests/unit/api/test_api_str_properties.py`:
- `test_history_cmdline` — HIST_CMDLINE
- `test_history_runcwd` — HIST_RUNCWD
- `test_test_date_username_seed` — TEST_DATE, TEST_USERNAME, TEST_SEED
- `test_du_signature` — DU_SIGNATURE
- `test_toggle_canon_name` — TOGGLE_CANON_NAME
- `test_expr_terms` — EXPR_TERMS on expression scope
- `test_unique_id_read` — UNIQUE_ID read-only property

#### 2.7 Test Suite: Cover Item Property Tests

New test file `tests/unit/api/test_api_cover_properties.py`:
- `test_cover_goal` — COVER_GOAL on individual bins
- `test_cover_limit` — COVER_LIMIT saturation count
- `test_cover_weight` — COVER_WEIGHT on bins
- `test_stmt_index` — STMT_INDEX for code coverage

#### 2.8 Cover Item Flags: Implement and Test

- Add `getCoverFlag()` / `setCoverFlag()` / `getCoverFlags()` / `setCoverFlags()`
  to abstract `Scope` or `CoverIndex` interface
- Implement in `MemCoverIndex` and `SqliteCoverIndex`
- New test file `tests/unit/api/test_api_cover_flags.py`:
  - `test_set_get_cover_flag` — set/get individual cover flag bits
  - `test_cover_flags_excluded` — SCOPE_EXCLUDED-equivalent on cover items

---

### Phase 3 — Medium Priority: Multiple DU/Instance Types, HDL Scopes

#### 3.1 Test Suite: Multiple DU Types

Extend `tests/unit/api/test_api_scope_hierarchy.py` or add new file
`tests/unit/api/test_api_du_types.py`:
- `test_create_du_arch` — DU_ARCH scope (VHDL architecture)
- `test_create_du_package` — DU_PACKAGE scope
- `test_create_du_program` — DU_PROGRAM scope
- `test_create_du_interface` — DU_INTERFACE scope
- `test_du_any_check` — ScopeTypeT.DU_ANY() helper

#### 3.2 Test Suite: COVERINSTANCE Scope Tests

Add `test_api_coverinstance.py`:
- `test_create_coverinstance` — COVERINSTANCE scope under covergroup
- `test_coverinstance_properties` — per-instance coverage metrics
- `test_getCoverInstances` — UCIS.getCoverInstances() returns populated list

#### 3.3 Mem Backend: Fix getCoverInstances / getSourceFiles

- `MemUCIS.getCoverInstances()` should return actual instance coverage data
- `MemUCIS.getSourceFiles()` should return list of file handles used

#### 3.4 SQLite Backend: Fix getCoverInstances / getSourceFiles

- `SqliteUCIS.getCoverInstances()` should query the database for COVERINSTANCE scopes
- `SqliteUCIS.getSourceFiles()` should return all files from the `files` table

#### 3.5 Test Suite: HDL Scope Type Tests

New test file `tests/unit/api/test_api_hdl_scopes.py`:
- `test_create_process_scope` — PROCESS under INSTANCE
- `test_create_block_scope` — BLOCK under INSTANCE
- `test_create_function_scope` — FUNCTION under INSTANCE
- `test_create_task_scope` — TASK under INSTANCE
- `test_create_forkjoin_scope` — FORKJOIN
- `test_create_generate_scope` — GENERATE

#### 3.6 Test Suite: Path Separator

Add `test_path_separator` to `test_api_basic.py`:
- `test_get_default_path_separator` — verify default is `/` or `.`
- `test_set_path_separator` — set and verify custom path separator

---

### Phase 4 — Extended History Node, Attributes, and Tags

#### 4.1 Test Suite: Comprehensive History Node Property Tests

New test file `tests/unit/api/test_api_history_nodes.py`:
- `test_history_node_basic` — logicalName, physicalName, kind
- `test_history_node_test_status` — all TestStatusT values
- `test_history_node_simtime_timeunit` — simtime with time unit
- `test_history_node_cputime` — CPU time (real property)
- `test_history_node_seed_cmd_args` — seed, cmdline, simargs
- `test_history_node_run_cwd` — working directory
- `test_history_node_date_username_cost` — date, username, cost
- `test_history_node_toolcategory` — toolcategory string
- `test_history_node_vendor_info` — vendorId, vendorTool, vendorToolVersion
- `test_history_node_compulsory` — compulsory flag
- `test_history_node_same_tests` — sameTests field
- `test_history_node_comment` — comment string
- `test_history_iterate_all` — historyNodes() iteration
- `test_history_iterate_by_kind` — filter by HISTORYNODE_TEST vs HISTORYNODE_MERGE

#### 4.2 Abstract API: Add Attribute Interface

Add attribute management methods to the abstract `Obj` class:
```python
def attrAdd(self, scope, coverindex, key, value): ...
def attrMatch(self, scope, coverindex, key): ...
def attrNext(self, scope, coverindex, key): ...
def attrRemove(self, scope, coverindex, key): ...
```

#### 4.3 Abstract API: Add Tag Interface

Add tag management to `Obj` or `Scope`:
```python
def addObjTag(self, tag): ...
def removeObjTag(self, tag): ...
def objectTagsIterate(self): ...
```

#### 4.4 Test Suite: Attribute Tests

New test file `tests/unit/api/test_api_attributes.py`:
- `test_add_attribute` — add attribute to scope
- `test_match_attribute` — find attribute by key
- `test_iterate_attributes` — attrNext iteration
- `test_remove_attribute` — remove attribute
- `test_attribute_on_coveritem` — attribute on cover item
- `test_attribute_on_history_node` — attribute on history node

#### 4.5 Test Suite: Tag Tests

New test file `tests/unit/api/test_api_tags.py`:
- `test_add_tag` — addObjTag on scope
- `test_remove_tag` — removeObjTag
- `test_iterate_object_tags` — objectTagsIterate
- `test_find_tagged_objects` — taggedObjIterate

---

### Phase 5 — Traversal, Lookup, and Deletion APIs

#### 5.1 Visitor: Extend UCISVisitor

Extend `UCISVisitor` class to include all scope types:
```python
def visit_instance(self, scope): ...
def visit_covergroup(self, scope): ...
def visit_coverpoint(self, scope): ...
def visit_cross(self, scope): ...
def visit_toggle(self, scope): ...
def visit_fsm(self, scope): ...
def visit_assert(self, scope): ...
def visit_cover(self, scope): ...
def visit_branch(self, scope): ...
def visit_stmt(self, scope): ...
def visit_cond(self, scope): ...
def visit_expr(self, scope): ...
```

Add a `traverse(db, visitor, mask)` function as the Python analogue of
`ucis_CallBack`.

#### 5.2 Test Suite: Traversal Tests

New test file `tests/unit/api/test_api_traversal.py`:
- `test_callback_traverse_all` — traverse all scopes, count types
- `test_callback_traverse_filtered` — traverse only COVERGROUP scopes
- `test_callback_traverse_instances` — traverse only INSTANCE scopes
- `test_visitor_all_types` — visitor covering all defined scope types

#### 5.3 Delete Operations

- Add `removeScope(scope)` to abstract `UCIS` or `Scope`
- Add `removeCover(scope, coverindex)` to abstract `Scope`
- Implement in Mem and SQLite backends

#### 5.4 Test Suite: Deletion Tests

New test file `tests/unit/api/test_api_delete.py`:
- `test_remove_scope` — remove a scope and verify it's gone
- `test_remove_cover` — remove a cover item
- `test_remove_scope_with_children` — verify cascade behaviour
- `test_remove_does_not_affect_siblings` — verify adjacent scopes unaffected

#### 5.5 Unique ID Lookup

- Add `matchScopeByUniqueId(uid)` to `UCIS`
- Add `matchCoverByUniqueId(uid)` to `UCIS`
- Add `caseAwareMatchScopeByUniqueId(uid)` to `UCIS`
- Implement in Mem (scan) and SQLite (query UCIS_STR_UNIQUE_ID property)

#### 5.6 Test Suite: Unique ID Tests

New test file `tests/unit/api/test_api_unique_id.py`:
- `test_scope_unique_id_read` — every scope has a non-empty UNIQUE_ID
- `test_match_scope_by_uid` — find scope by its unique ID
- `test_match_cover_by_uid` — find cover item by unique ID
- `test_uid_case_sensitive` — case-sensitive vs case-insensitive match

#### 5.7 DU Name Utilities

- Add `parseDUName(name)` returning `(library, module)` to UCIS or as a utility
- Add `composeDUName(library, module)` returning a string

#### 5.8 Test Suite: DU Name Tests

New test file `tests/unit/api/test_api_du_names.py`:
- `test_parse_du_name` — parse "work.my_module" → ("work", "my_module")
- `test_compose_du_name` — compose ("work", "my_module") → "work.my_module"
- `test_round_trip_du_name` — compose then parse gives same result

---

### Phase 6 — Formal Coverage (Low Priority)

The formal/proof coverage APIs (`ucis_SetFormalStatus`, `ucis_GetFormalRadius`,
witness data, etc.) are used only in formal verification flows. These are out of
scope for functional simulation-focused users. Implementation should be deferred
unless a concrete use case arises. A skeleton API with `NotImplementedError`
stubs can be defined to document the interface.

- Create `src/ucis/formal_coverage.py` with stub classes
- Document the formal coverage data model (properties, coverage contexts)

---

## 8. Summary Table: All Identified Gaps

### Python Abstract API
| Gap | Phase |
|---|---|
| `IntProperty.TOGGLE_METRIC` missing | 1 |
| `IntProperty.SUPPRESS_MODIFIED` missing | 1 |
| `RealProperty` enum nearly empty | 1 |
| `createNextTransition()` missing from `Scope` | 1 |
| `setCoverData()` missing from `Scope` | 2 |
| `getCoverFlag()` / `setCoverFlag()` / `getCoverFlags()` / `setCoverFlags()` missing | 2 |
| `attrAdd/attrMatch/attrNext/attrRemove` missing from `Obj` | 4 |
| `addObjTag/removeObjTag/objectTagsIterate` missing from `Obj` | 4 |
| `removeScope()` / `removeCover()` missing | 5 |
| `matchScopeByUniqueId()` / `matchCoverByUniqueId()` missing | 5 |
| `parseDUName()` / `composeDUName()` missing | 5 |
| `UCISVisitor` incomplete (1 method only) | 5 |
| `createInstanceByName()` missing | 5 |
| `GetHandleProperty` / `SetHandleProperty` missing | 5 |
| History node list API entirely missing | 4 |
| Formal coverage API entirely missing | 6 |
| Streaming API (`OpenReadStream` etc.) missing | 6 |

### Mem Backend
| Gap | Phase |
|---|---|
| `createToggle()` raises `UnimplError` | 1 |
| No FSM scope support | 1 |
| BRANCH / COND / EXPR / COVBLOCK scope types not supported | 1 |
| No assertion (ASSERT/COVER) scope support | 2 |
| No CVGBINSCOPE / ILLEGALBINSCOPE / IGNOREBINSCOPE support | 2 |
| `RealProperty` not implemented | 2 |
| `MemFactory.clone()` is stub | 3 |
| `getCoverInstances()` returns None | 3 |
| `getSourceFiles()` returns None | 3 |
| Cover item flags not stored | 2 |
| TOGGLE_METRIC property not stored | 1 |
| Attribute storage incomplete | 4 |
| `setIntProperty` incomplete | 2 |
| HDL scope types (PROCESS etc.) raise `NotImplementedError` | 3 |

### SQLite Backend
| Gap | Phase |
|---|---|
| `getSourceFiles()` returns `[]` | 3 |
| `getCoverInstances()` returns `[]` | 3 |
| `getCoverFlag()` / `setCoverFlag()` missing | 2 |
| `setCoverData()` missing | 2 |
| Assertion (ASSERT/COVER) no specialised scope | 2 |
| FSM API not in abstract interface | 1 |
| Attribute API not in abstract interface | 4 |
| Tag API not in abstract interface | 4 |

### Tests Missing
| Gap | Phase |
|---|---|
| Toggle coverage tests | 1 |
| FSM coverage tests | 1 |
| Assertion/Cover directive tests | 2 |
| CVGBINSCOPE / ILLEGALBINSCOPE / IGNOREBINSCOPE tests | 2 |
| `RealProperty` tests | 2 |
| Extended `StrProperty` tests | 2 |
| Cover item property tests (GOAL, LIMIT, WEIGHT) | 2 |
| Cover item flag tests | 2 |
| Multiple DU type tests (DU_ARCH, DU_PACKAGE, etc.) | 3 |
| `COVERINSTANCE` scope tests | 3 |
| `getCoverInstances()` / `getSourceFiles()` tests | 3 |
| HDL scope type tests | 3 |
| Path separator tests | 3 |
| History node comprehensive property tests | 4 |
| Attribute API tests | 4 |
| Tag API tests | 4 |
| Traversal / callback tests | 5 |
| Deletion (RemoveScope / RemoveCover) tests | 5 |
| Unique ID lookup tests | 5 |
| DU name parse/compose tests | 5 |
| Formal coverage tests | 6 |

---

## 9. Backends vs Coverage Types Matrix

This matrix shows which scope/coverage types are currently usable end-to-end
(create → persist → read back → verified by test).

| Coverage Type | Mem | SQLite | XML | Tested |
|---|:---:|:---:|:---:|:---:|
| Covergroup | ✅ | ✅ | ✅ | ✅ |
| Coverpoint | ✅ | ✅ | ✅ | ✅ |
| Cross | ✅ | ✅ | ✅ | ✅ |
| Statement (STMTBIN) | ✅ | ✅ | ✅ | ✅ |
| Branch (BRANCHBIN) | ✅ | ✅ | ✅ | ✅ |
| Condition (CONDBIN) | ❌ | ✅ | ✅ | ✅ |
| Expression (EXPRBIN) | ❌ | ✅ | ✅ | ✅ |
| Block (BLOCKBIN) | ❌ | ✅ | ✅ | ✅ |
| Toggle | ❌ | ✅ | ✅ | ❌ |
| FSM | ❌ | ✅ | ⚠️ | ❌ |
| Assert directive | ❌ | ❌ | ⚠️ | ❌ |
| Cover directive | ❌ | ❌ | ⚠️ | ❌ |
| CVGBINSCOPE | ⚠️ | ⚠️ | ✅ | ❌ |
| ILLEGALBINSCOPE | ⚠️ | ⚠️ | ✅ | ❌ |
| IGNOREBINSCOPE | ⚠️ | ⚠️ | ✅ | ❌ |
| COVERINSTANCE | ⚠️ | ⚠️ | ✅ | ❌ |
| DU_ARCH | ✅ | ✅ | ✅ | ❌ |
| DU_PACKAGE | ✅ | ✅ | ✅ | ❌ |
| HDL scopes (PROCESS etc.) | ❌ | ✅ | ✅ | ❌ |

Legend: ✅ Implemented and passing; ⚠️ Partial/untested; ❌ Not implemented or failing

---

## 10. Recommended Execution Order

1. **Start with property enum fixes** (1.1, 1.2) — small, no-risk changes enabling all downstream test work
2. **Mem toggle + FSM** (1.3, 1.4) — unlocks the widest backend parity gap
3. **Abstract API additions** (1.6, 2.8's getCoverFlag) — keeps mem/sqlite/xml in sync
4. **Write toggle and FSM tests** (1.7, 1.8) — confirm implementations
5. **Mem BRANCH/COND/EXPR/COVBLOCK** (1.5) — fixes code coverage on Mem backend
6. **RealProperty + StrProperty tests** (2.5, 2.6) — complete property coverage
7. **Assertion coverage** (2.1, 2.2) — add last missing major coverage type
8. **Bin scope tests** (2.3) — complete functional coverage bin testing
9. **Cover item property and flag tests** (2.7, 2.8 tests) — complete item-level API
10. **History node property tests** (4.1) — comprehensive test data validation
11. **Fix getSourceFiles / getCoverInstances** (3.3, 3.4) and test (3.2)
12. **Attribute and tag API** (4.2–4.5) — extensibility testing
13. **Traversal, deletion, lookup** (Phase 5)
14. **Formal coverage stubs** (Phase 6) — documentation

---

*Generated by analysis of `UCIS_Version_1.0_Final_June-2012.md` vs. `src/ucis/` and `tests/`.*
