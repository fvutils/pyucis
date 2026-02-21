# UCIS API Coverage: Comprehensive Implementation Plan

**Source analysis:** `UCIS_COVERAGE_GAP_ANALYSIS.md`  
**Baseline:** 98 tests passing, 7 skipped across mem/xml/sqlite backends

---

## Context and Key Discoveries

Before diving into tasks, several nuances are important for implementers:

**Code coverage bins vs. code coverage scopes:**  
Code coverage (statement, branch, condition, expression, block) is currently
implemented using `createNextCover()` with STMTBIN/BRANCHBIN/etc. cover item
types *directly on an instance scope*, without creating intermediate BRANCH/COND/EXPR
scope nodes. This flat model works in all three backends (mem, xml, sqlite) and
all tests pass. The UCIS LRM also allows structured BRANCH/COND/EXPR *scopes*
but the flat model is the common tool output pattern. Do not break the flat
model while adding structured scope support.

**SQLite specialized subclasses on read, not on write:**  
SQLite's `createScope()` always returns a plain `SqliteScope`. Specialised
subclasses (`SqliteToggleScope`, `SqliteFSMScope`, `SqliteCovergroup`, etc.) are
only returned by `SqliteScope.create_specialized_scope()` when reading back.
This means `createToggle()` and `createScope(FSM)` currently return plain
`SqliteScope` objects, so FSM/toggle-specific methods are unavailable
immediately after creation. This is a significant usability bug.

**Mem backend `createScope()` is strictly gated:**  
Only DU_*, COVERGROUP, COVERINSTANCE, and COVERPOINT types work. All others
raise `NotImplementedError`. The fix is to add a generic `MemScope` fallthrough
for the remaining HDL/code-coverage scope types.

**`RealProperty` enum is a placeholder:**  
Only `b = 0` is defined. The four UCIS real-valued properties
(`SIMTIME`, `CPUTIME`, `COST`, `CVG_INST_AVERAGE`) need enum values and
implementation in both backends.

**Attributes and tags exist in SQLite but not in the abstract API:**  
`sqlite_attributes.py` implements attribute storage. It needs to be surfaced
through the abstract `Obj` class so all backends can use it.

---

## Work Items

Tasks are grouped into phases by priority. Each task has a clear deliverable,
the files to change, and what to test.

---

## Phase 1 — Property Enum Fixes (no functional changes, unblocks tests)

These are pure additions to enum files. They carry zero risk and enable all
downstream property tests to be written.

### Task P1-1: Add `TOGGLE_METRIC` to `IntProperty`

**File:** `src/ucis/int_property.py`  
**Change:** Add `TOGGLE_METRIC = auto()` between `TOGGLE_COVERED` and
`BRANCH_HAS_ELSE`.  
**LRM ref:** `UCIS_INT_TOGGLE_METRIC`  
**Notes:** `ToggleMetricT` values (NOBINS, ENUM, TRANSITION, 2STOGGLE,
ZTOGGLE, XTOGGLE) are already defined. `SqliteToggleScope` uses `setToggleMetric()`
as a custom method; this property would expose the same data uniformly via
`getIntProperty(TOGGLE_METRIC)`.

### Task P1-2: Add `SUPPRESS_MODIFIED` to `IntProperty`

**File:** `src/ucis/int_property.py`  
**Change:** Add `SUPPRESS_MODIFIED = auto()` after `MODIFIED_SINCE_SIM`.  
**LRM ref:** `UCIS_INT_SUPPRESS_MODIFIED`  
**Notes:** Database-level property to suppress the modification flag.

### Task P1-3: Populate `RealProperty` enum

**File:** `src/ucis/real_property.py`  
**Change:** Replace the `b = 0` placeholder with:

```python
SIMTIME = 0          # UCIS_REAL_TEST_SIMTIME  — simulation end time
CPUTIME = auto()     # UCIS_REAL_HIST_CPUTIME  — CPU time for the test run
COST = auto()        # UCIS_REAL_TEST_COST     — cost to re-run this test
CVG_INST_AVERAGE = auto()  # UCIS_REAL_CVG_INST_AVERAGE — avg coverage across instances
```

**Notes:** These map to existing `HistoryNode` methods `getSimTime()`/`getCpuTime()`/
`getCost()`. After this change those methods should also be accessible via
`getRealProperty(SIMTIME/CPUTIME/COST)`.

---

## Phase 2 — Mem Backend: Toggle and FSM Scope Support

These are the largest functional gaps in the Mem backend. SQLite already has
`SqliteToggleScope` and `SqliteFSMScope`; Mem needs equivalent classes.

### Task P2-1: Implement `MemToggleScope`

**New file:** `src/ucis/mem/mem_toggle_scope.py`  
**Inherits:** `MemScope`  
**Fields to store:**
- `canonical_name: str`
- `toggle_metric: ToggleMetricT`
- `toggle_type: ToggleTypeT`
- `toggle_dir: ToggleDirT`
- `num_bits: int`

**Methods to implement:**
```python
def getCanonicalName(self) -> str
def setCanonicalName(self, name: str)
def getToggleMetric(self) -> ToggleMetricT
def setToggleMetric(self, metric: ToggleMetricT)
def getToggleType(self) -> ToggleTypeT
def setToggleType(self, t: ToggleTypeT)
def getToggleDir(self) -> ToggleDirT
def setToggleDir(self, d: ToggleDirT)
def getNumBits(self) -> int
def setNumBits(self, n: int)
def getTotalToggle01(self) -> int  # sum of 0->1 bins
def getTotalToggle10(self) -> int  # sum of 1->0 bins
```

**IntProperty integration:**  
Override `getIntProperty` / `setIntProperty` so
`TOGGLE_TYPE`, `TOGGLE_DIR`, `TOGGLE_COVERED`, `TOGGLE_METRIC` work.

**StrProperty integration:**  
Override `getStringProperty` / `setStringProperty` so
`TOGGLE_CANON_NAME` works.

### Task P2-2: Wire `MemScope.createToggle()` to `MemToggleScope`

**File:** `src/ucis/mem/mem_scope.py`  
**Change:** Replace the `raise UnimplError()` in `createToggle()` with:

```python
from ucis.mem.mem_toggle_scope import MemToggleScope
ret = MemToggleScope(self, name, None, 1, SourceT.NONE, ScopeTypeT.TOGGLE, flags)
ret.setCanonicalName(canonical_name)
if toggle_metric is not None:
    ret.setToggleMetric(toggle_metric)
if toggle_type is not None:
    ret.setToggleType(toggle_type)
if toggle_dir is not None:
    ret.setToggleDir(toggle_dir)
self.addChild(ret)
return ret
```

### Task P2-3: Add TOGGLE scope to `MemScope.createScope()` dispatch

**File:** `src/ucis/mem/mem_scope.py`  
**Change:** Add a case for `ScopeTypeT.TOGGLE` that creates a `MemToggleScope`
before the final `else: raise NotImplementedError`.

### Task P2-4: Implement `MemFSMScope`

**New file:** `src/ucis/mem/mem_fsm_scope.py`  
**Inherits:** `MemScope`

Model FSM state and transitions similarly to `SqliteFSMScope` but in-memory
using dicts/lists.

**Data classes (inner or module-level):**
```python
class MemFSMState:
    name: str
    index: int
    visit_count: int = 0

class MemFSMTransition:
    from_state: MemFSMState
    to_state: MemFSMState
    count: int = 0
```

**Methods to implement:**
```python
def createState(self, state_name: str, state_index: int = None) -> MemFSMState
def getState(self, state_name: str) -> MemFSMState
def getStates(self) -> Iterator[MemFSMState]
def getNumStates(self) -> int
def createTransition(self, from_state, to_state) -> MemFSMTransition
def getTransition(self, from_state, to_state) -> MemFSMTransition
def getTransitions(self) -> Iterator[MemFSMTransition]
def getNumTransitions(self) -> int
def getStateCoveragePercent(self) -> float
def getTransitionCoveragePercent(self) -> float
```

**IntProperty integration:**  
Return `FSM_STATEVAL` for states via `getIntProperty`.

### Task P2-5: Add FSM scope to `MemScope.createScope()` dispatch

**File:** `src/ucis/mem/mem_scope.py`  
**Change:** Add a case for `ScopeTypeT.FSM` that creates a `MemFSMScope`.

### Task P2-6: Add `createNextTransition()` to abstract `Scope`

**File:** `src/ucis/scope.py`  
**Change:** Add the following abstract method stub (with docstring):

```python
def createNextTransition(self, from_state_name: str, to_state_name: str,
                         data: 'CoverData', srcinfo: 'SourceInfo') -> 'CoverIndex':
    """Create an FSM transition cover item.
    
    Args:
        from_state_name: Name of the source state.
        to_state_name:   Name of the destination state.
        data:            Initial cover data (FSMBIN type).
        srcinfo:         Source location, or None.
    Returns:
        CoverIndex for the new transition item.
    Raises:
        UnimplError: If not supported by this scope type.
    See Also:
        UCIS LRM ucis_CreateNextTransition
    """
    raise UnimplError()
```

Implement in `MemFSMScope` and `SqliteFSMScope`.

---

## Phase 3 — Mem Backend: Remaining Scope Type Fallthrough

### Task P3-1: Generic fallthrough in `MemScope.createScope()`

**File:** `src/ucis/mem/mem_scope.py`  
**Change:** Replace the final `else: raise NotImplementedError(...)` with a
generic `MemScope` fallthrough for all scope types not requiring custom behaviour:

```python
else:
    # Generic scope for BRANCH, COND, EXPR, COVBLOCK, PROCESS, BLOCK,
    # FUNCTION, TASK, FORKJOIN, GENERATE, ASSERT, COVER, PROGRAM,
    # PACKAGE, INTERFACE, CLASS, GENERIC, FSM_STATES, FSM_TRANS
    ret = MemScope(self, name, srcinfo, weight, source, type, flags)
```

This allows all scope types to be created in mem. Scope types that need
specialised methods (TOGGLE, FSM) are handled before this fallthrough.

**Note:** Un-comment the CROSS case at the same time.

---

## Phase 4 — SQLite Backend: Specialize on Create, not just on Read

### Task P4-1: Return specialised scope from `SqliteScope.createScope()`

**File:** `src/ucis/sqlite/sqlite_scope.py`  
**Change:** After inserting the new scope row, call
`SqliteScope.create_specialized_scope(self.ucis_db, new_scope_id)` instead of
`SqliteScope(self.ucis_db, new_scope_id)`. This ensures that `createToggle()`
returns a `SqliteToggleScope` and `createScope(FSM)` returns a `SqliteFSMScope`
*immediately*, not just after a read-back.

```python
new_scope_id = cursor.lastrowid
return SqliteScope.create_specialized_scope(self.ucis_db, new_scope_id)
```

**Also update `create_specialized_scope`** to include TOGGLE and FSM:

```python
elif scope_type & ScopeTypeT.TOGGLE:
    from ucis.sqlite.sqlite_toggle_scope import SqliteToggleScope
    return SqliteToggleScope(ucis_db, scope_id)
elif scope_type & ScopeTypeT.FSM:
    from ucis.sqlite.sqlite_fsm_scope import SqliteFSMScope
    return SqliteFSMScope(ucis_db, scope_id)
```

### Task P4-2: Fix `SqliteUCIS.getSourceFiles()`

**File:** `src/ucis/sqlite/sqlite_ucis.py`  
**Change:** Replace `return []` with a query:

```python
def getSourceFiles(self):
    cursor = self.conn.execute("SELECT file_id, file_path FROM files")
    return [SqliteFileHandle(self, row[0], row[1]) for row in cursor.fetchall()]
```

### Task P4-3: Fix `SqliteUCIS.getCoverInstances()`

**File:** `src/ucis/sqlite/sqlite_ucis.py`  
**Change:** Replace `return []` with a query for COVERINSTANCE scopes:

```python
def getCoverInstances(self):
    from ucis.scope_type_t import ScopeTypeT
    mask = int(ScopeTypeT.COVERINSTANCE)
    cursor = self.conn.execute(
        "SELECT scope_id FROM scopes WHERE (scope_type & ?) != 0", (mask,)
    )
    return [SqliteScope.create_specialized_scope(self, row[0])
            for row in cursor.fetchall()]
```

### Task P4-4: Fix `MemUCIS.getSourceFiles()`

**File:** `src/ucis/mem/mem_ucis.py`  
**Change:** Track file handles in a list and return it:

```python
def createFileHandle(self, filename, workdir):
    fh = MemFileHandle(filename)
    self.m_file_handles.append(fh)
    return fh

def getSourceFiles(self):
    return list(self.m_file_handles)
```

Add `self.m_file_handles = []` to `__init__`.

### Task P4-5: Fix `MemUCIS.getCoverInstances()`

**File:** `src/ucis/mem/mem_ucis.py`  
**Change:** Walk the scope tree looking for COVERINSTANCE scopes and return
them. Use the existing `scopes()` iterator with mask `ScopeTypeT.COVERINSTANCE`.

---

## Phase 5 — RealProperty: Implement in Backends

### Task P5-1: Hook `RealProperty` into `MemHistoryNode`

**File:** `src/ucis/mem/mem_history_node.py`  
**Change:** Override `getRealProperty` / `setRealProperty`:

```python
def getRealProperty(self, coverindex, property):
    if property == RealProperty.SIMTIME:
        return self.m_simtime
    elif property == RealProperty.CPUTIME:
        return self.m_cputime
    elif property == RealProperty.COST:
        return self.m_cost
    return super().getRealProperty(coverindex, property)

def setRealProperty(self, coverindex, property, value):
    if property == RealProperty.SIMTIME:
        self.m_simtime = value
    elif property == RealProperty.CPUTIME:
        self.m_cputime = value
    elif property == RealProperty.COST:
        self.m_cost = value
    else:
        super().setRealProperty(coverindex, property, value)
```

### Task P5-2: Hook `RealProperty` into `SqliteHistoryNode`

**File:** `src/ucis/sqlite/sqlite_history_node.py`  
**Change:** Similarly map SIMTIME/CPUTIME/COST to `getSimTime()`/`getCpuTime()`/
`getCost()` within `getRealProperty`/`setRealProperty`.

### Task P5-3: Hook `CVG_INST_AVERAGE` on covergroup scopes

**Files:** `src/ucis/mem/mem_covergroup.py`, `src/ucis/sqlite/sqlite_covergroup.py`  
**Change:** Implement `getRealProperty(CVG_INST_AVERAGE)` to compute and return
the average coverage percentage across all COVERINSTANCE child scopes.

---

## Phase 6 — Abstract Attribute and Tag API

These exist in SQLite but are not in the abstract base, preventing portable use.

### Task P6-1: Add attribute methods to abstract `Obj`

**File:** `src/ucis/obj.py`  
**Change:** Add the following methods with `raise UnimplError()` bodies and full docstrings:

```python
def attrAdd(self, coverindex: int, key: str, value) -> None: ...
def attrMatch(self, coverindex: int, key: str): ...
def attrNext(self, coverindex: int, key: str): ...
def attrRemove(self, coverindex: int, key: str) -> None: ...
```

### Task P6-2: Expose attribute methods in `SqliteObj`

**File:** `src/ucis/sqlite/sqlite_obj.py`  
**Change:** Delegate to `sqlite_attributes.py` methods via the above interface.

### Task P6-3: Implement attribute methods in `MemObj`

**File:** `src/ucis/mem/mem_obj.py`  
**Change:** Implement using an in-memory dict:
`self.m_attrs: dict = {}` (keyed by `(coverindex, key)`).

### Task P6-4: Add tag methods to abstract `Obj`

**File:** `src/ucis/obj.py`  
**Change:** Add:

```python
def addObjTag(self, tag: str) -> None: ...
def removeObjTag(self, tag: str) -> None: ...
def objectTagsIterate(self) -> Iterator[str]: ...
```

### Task P6-5: Implement tag methods in `MemObj` and `SqliteObj`

**Files:** `src/ucis/mem/mem_obj.py`, `src/ucis/sqlite/sqlite_obj.py`  
**Mem change:** `self.m_tags: set = set()` in `__init__`.  
**SQLite change:** Delegate to existing `sqlite_attributes.py` tag storage.

---

## Phase 7 — Cover Item Flags

### Task P7-1: Add `getCoverFlag`/`setCoverFlag` to abstract `Scope`

**File:** `src/ucis/scope.py`  
**Change:** Add alongside existing `getFlags()`:

```python
def getCoverFlag(self, coverindex: int, flag: int) -> bool:
    """Get a flag bit on a specific cover item.
    See UCIS LRM ucis_GetCoverFlag."""
    raise UnimplError()

def setCoverFlag(self, coverindex: int, flag: int, value: bool) -> None:
    """Set a flag bit on a specific cover item.
    See UCIS LRM ucis_SetCoverFlag."""
    raise UnimplError()

def getCoverFlags(self, coverindex: int) -> int:
    """Get all flags for a cover item as a bitmask."""
    raise UnimplError()

def setCoverFlags(self, coverindex: int, flags: int) -> None:
    """Set all flags for a cover item as a bitmask."""
    raise UnimplError()
```

### Task P7-2: Implement cover item flags in `MemCoverIndex`

**File:** `src/ucis/mem/mem_cover_index.py`  
**Change:** Add `self.m_flags: int = 0` to `__init__`. Implement `getFlags()`,
`setFlags()`. Wire up `getCoverFlag` / `setCoverFlag` on the parent `MemScope`.

### Task P7-3: Implement cover item flags in `SqliteCoverIndex`

**File:** `src/ucis/sqlite/sqlite_cover_index.py`  
**Change:** Store flags in the cover items table. If a `flags` column does not
exist, add it to the schema. Implement `getFlags()`/`setFlags()`.

---

## Phase 8 — `setCoverData` on Abstract Scope

### Task P8-1: Add `setCoverData` to abstract `Scope`

**File:** `src/ucis/scope.py`  
**Change:**

```python
def setCoverData(self, coverindex: int, data: 'CoverData') -> None:
    """Replace cover data for an existing cover item.
    See UCIS LRM ucis_SetCoverData."""
    raise UnimplError()
```

### Task P8-2: Implement `setCoverData` in `MemScope`

**File:** `src/ucis/mem/mem_scope.py`  
**Change:** Retrieve cover item by index, replace its data.

### Task P8-3: Implement `setCoverData` in `SqliteScope`

**File:** `src/ucis/sqlite/sqlite_scope.py`  
**Change:** Update the cover_data column for the given `coverindex`.

---

## Phase 9 — Assertion/Cover Directive Scopes

### Task P9-1: Add thin assertion scope creation

The simplest approach: `createScope(ASSERT)` and `createScope(COVER)` should
work in both Mem (via P3-1 generic fallthrough) and SQLite (already stores
any type). The key addition is ensuring that bins of types ASSERTBIN, PASSBIN,
VACUOUSBIN, DISABLEDBIN, ATTEMPTBIN, ACTIVEBIN, FAILBIN, COVERBIN,
PEAKACTIVEBIN can be created via `createNextCover()` on an ASSERT/COVER scope.
This should already work mechanically — just needs tests to confirm.

**No new files needed** if P3-1 and P4-1 are done. The ASSERT and COVER scope
types will fall through to generic `MemScope` / `SqliteScope` respectively.

### Task P9-2: Document assertion coverage creation pattern

Add a docstring to `Scope.createScope()` documenting the pattern for assertion
coverage (create an ASSERT scope, call `createNextCover` with ASSERTBIN,
PASSBIN, VACUOUSBIN, FAILBIN, ATTEMPTBIN, ACTIVEBIN, PEAKACTIVEBIN types).

---

## Phase 10 — CVGBINSCOPE / ILLEGALBINSCOPE / IGNOREBINSCOPE

### Task P10-1: Support bin scope creation in Mem

**File:** `src/ucis/mem/mem_scope.py`  
P3-1 handles this automatically via the generic fallthrough. Confirm
CVGBINSCOPE, ILLEGALBINSCOPE, IGNOREBINSCOPE all get plain `MemScope` instances.

### Task P10-2: Support bin scope iteration in SQLite

**File:** `src/ucis/sqlite/sqlite_scope.py`  
Ensure `scopes(ScopeTypeT.CVGBINSCOPE)` etc. return results. This requires
the mask filter to work correctly, which it should with the existing SQL query.
Verify by adding a test.

---

## Phase 11 — MemFactory.clone()

### Task P11-1: Implement `MemFactory.clone()`

**File:** `src/ucis/mem/mem_factory.py`  
**Change:** Implement deep-copy of the in-memory database. Use a recursive
scope-tree copy, preserving parent-child relationships, cover items, and
history nodes. The simplest correct implementation is:

```python
@staticmethod
def clone(db: UCIS) -> UCIS:
    """Deep clone an in-memory database."""
    import copy
    return copy.deepcopy(db)
```

Verify deep copy is sufficient (no shared mutable state between original
and clone).

---

## Phase 12 — Visitor/Traversal Improvements

### Task P12-1: Extend `UCISVisitor`

**File:** `src/ucis/visitors/UCISVisitor.py`  
**Change:** Add visit methods for all scope types:

```python
def visit_instance(self, scope): pass
def visit_covergroup(self, scope): pass
def visit_coverinstance(self, scope): pass
def visit_coverpoint(self, scope): pass
def visit_cross(self, scope): pass
def visit_toggle(self, scope): pass
def visit_fsm(self, scope): pass
def visit_assert_scope(self, scope): pass
def visit_cover_scope(self, scope): pass
def visit_branch(self, scope): pass
def visit_cond(self, scope): pass
def visit_expr(self, scope): pass
def visit_covblock(self, scope): pass
def visit_process(self, scope): pass
def visit_block(self, scope): pass
def visit_function(self, scope): pass
def leave_scope(self, scope): pass   # called after children visited
```

### Task P12-2: Add `traverse()` utility function

**File:** `src/ucis/visitors/UCISVisitor.py` (or new `src/ucis/visitors/traverse.py`)  
**Change:** Add:

```python
def traverse(db_or_scope, visitor: UCISVisitor, 
             mask: ScopeTypeT = ScopeTypeT.ALL) -> None:
    """Traverse scope tree, calling visitor methods for matching scopes.
    
    Analogue of UCIS LRM ucis_CallBack / ucis_ScopeScan.
    
    Args:
        db_or_scope: Root of traversal (UCIS db or any Scope).
        visitor:     Visitor instance whose methods are called.
        mask:        Bitmask of scope types to visit (others are traversed
                     but visitor method is not called for them).
    """
    def _visit(scope):
        if scope.getScopeType() & mask:
            _dispatch(visitor, scope)
        for child in scope.scopes(ScopeTypeT.ALL):
            _visit(child)
        visitor.leave_scope(scope)
    
    for top in db_or_scope.scopes(ScopeTypeT.ALL):
        _visit(top)
```

---

## Phase 13 — Delete Operations

### Task P13-1: Add `removeScope()` to abstract `UCIS`

**File:** `src/ucis/ucis.py`  
**Change:**

```python
def removeScope(self, scope: 'Scope') -> None:
    """Remove a scope and all its children from the database.
    See UCIS LRM ucis_RemoveScope."""
    raise UnimplError()
```

### Task P13-2: Add `removeCover()` to abstract `Scope`

**File:** `src/ucis/scope.py`  
**Change:**

```python
def removeCover(self, coverindex: int) -> None:
    """Remove a cover item from this scope.
    See UCIS LRM ucis_RemoveCover."""
    raise UnimplError()
```

### Task P13-3: Implement `removeScope()` in `MemUCIS`

**File:** `src/ucis/mem/mem_ucis.py` (and `mem_scope.py`)  
**Change:** Walk the scope tree, find the scope, remove it from its parent's
children list.

### Task P13-4: Implement `removeScope()` in `SqliteUCIS`

**File:** `src/ucis/sqlite/sqlite_ucis.py`  
**Change:** Delete from the `scopes` table (cascade will remove children
if FK constraints are set; otherwise delete recursively).

### Task P13-5: Implement `removeCover()` in Mem and SQLite

Delete the cover item entry at the given index.

---

## Phase 14 — DU Name Utilities

### Task P14-1: Add `parseDUName()` and `composeDUName()` utilities

**New file:** `src/ucis/du_name.py` (or add to `src/ucis/ucis.py`)

```python
def parseDUName(name: str) -> tuple:
    """Parse a fully-qualified DU name into (library, module).
    
    Examples:
        parseDUName("work.counter") -> ("work", "counter")
        parseDUName("counter")      -> ("work", "counter")  # default lib
    See UCIS LRM ucis_ParseDUName."""
    parts = name.split('.', 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return "work", parts[0]

def composeDUName(library: str, module: str) -> str:
    """Compose a fully-qualified DU name.
    
    Example:
        composeDUName("work", "counter") -> "work.counter"
    See UCIS LRM ucis_ComposeDUName."""
    return f"{library}.{module}"
```

---

## Phase 15 — Unique ID Lookup

### Task P15-1: Add unique ID methods to abstract `UCIS`

**File:** `src/ucis/ucis.py`  
**Change:**

```python
def matchScopeByUniqueId(self, uid: str) -> 'Scope':
    """Find a scope by its UNIQUE_ID string property.
    Returns None if not found. Case-sensitive.
    See UCIS LRM ucis_MatchScopeByUniqueID."""
    raise UnimplError()

def matchCoverByUniqueId(self, uid: str) -> tuple:
    """Find a (scope, coverindex) pair by UNIQUE_ID.
    Returns (None, -1) if not found.
    See UCIS LRM ucis_MatchCoverByUniqueID."""
    raise UnimplError()
```

### Task P15-2: Implement in `MemUCIS`

Walk the scope tree recursively, comparing UNIQUE_ID (mem generates sequential
IDs at creation time, stored in `mem_obj.py`).

### Task P15-3: Implement in `SqliteUCIS`

Query the properties table: `WHERE key = 'UNIQUE_ID' AND value = ?`.

---

## Phase 16 — Test Suite

All tests go in `tests/unit/api/` and use the parametrized `backend` fixture
so they run on memory, xml, and sqlite backends.

### Task T1: `test_api_toggle_coverage.py`

```python
class TestApiToggleCoverage:
    def test_create_toggle_scope(self, backend)
        # createToggle() returns a scope with TOGGLE type
        # scope.getScopeType() == UCIS_TOGGLE
        
    def test_toggle_scope_properties(self, backend)
        # setToggleMetric/getToggleMetric via IntProperty.TOGGLE_METRIC
        # setToggleType/getToggleType via IntProperty.TOGGLE_TYPE
        # setToggleDir/getToggleDir via IntProperty.TOGGLE_DIR
        # setCanonicalName via StrProperty.TOGGLE_CANON_NAME
        
    def test_toggle_bins(self, backend)
        # createNextCover with TOGGLEBIN for "0->1" and "1->0"
        # verify counts
        
    def test_toggle_covered_property(self, backend)
        # after creating both bins, TOGGLE_COVERED property is 1
        
    def test_toggle_multibit(self, backend)
        # create toggle scope with 4-bit width
        # verify SCOPE_NUM_COVERITEMS == 8 (4 x 0->1, 4 x 1->0)
        
    def test_toggle_persist_and_read(self, backend)
        # write + read back, verify toggle scope and bins survive
```

### Task T2: `test_api_fsm_coverage.py`

```python
class TestApiFSMCoverage:
    def test_create_fsm_scope(self, backend)
        # createScope(FSM) returns scope with FSM type
        
    def test_fsm_states(self, backend)
        # createState("IDLE"), createState("ACTIVE"), createState("DONE")
        # getNumStates() == 3, getState("IDLE").getName() == "IDLE"
        
    def test_fsm_transitions(self, backend)
        # createTransition(idle, active), createTransition(active, done)
        # getNumTransitions() == 2
        
    def test_fsm_state_value(self, backend)
        # FSM_STATEVAL property on state bins
        
    def test_fsm_state_coverage_percent(self, backend)
        # getStateCoveragePercent(): 0% initially, 100% after all visited
        
    def test_fsm_transition_coverage_percent(self, backend)
        # getTransitionCoveragePercent()
        
    def test_fsm_persist_and_read(self, backend)
        # write + read back, verify states and transitions survive
```

### Task T3: `test_api_assertion_coverage.py`

```python
class TestApiAssertionCoverage:
    def test_create_assert_scope(self, backend)
        # createScope(ASSERT) returns scope with ASSERT type
        
    def test_create_cover_directive_scope(self, backend)
        # createScope(COVER) returns scope with COVER type
        
    def test_assert_bins(self, backend)
        # createNextCover(ASSERTBIN) for fail count
        # createNextCover(PASSBIN) for pass count
        # createNextCover(VACUOUSBIN) for vacuous pass
        
    def test_cover_directive_bins(self, backend)
        # createNextCover(COVERBIN) for cover pass count
        # createNextCover(FAILBIN) for cover fail count
        
    def test_assertion_bin_counts(self, backend)
        # set counts, read back, verify
        
    def test_assert_persist_and_read(self, backend)
        # write + read back, verify assertion data survives
```

### Task T4: `test_api_bin_scopes.py`

```python
class TestApiBinScopes:
    def test_create_cvgbinscope(self, backend)
        # createScope(CVGBINSCOPE) under a coverpoint
        # CVGBIN items within it
        
    def test_create_illegalbinscope(self, backend)
        # createScope(ILLEGALBINSCOPE), ILLEGALBIN items
        
    def test_create_ignorebinscope(self, backend)
        # createScope(IGNOREBINSCOPE), IGNOREBIN items
        
    def test_bin_scope_persist_and_read(self, backend)
        # verify scope types survive persistence
```

### Task T5: `test_api_real_properties.py`

```python
class TestApiRealProperties:
    def test_history_simtime(self, backend)
        # setRealProperty(RealProperty.SIMTIME, 1234.5)
        # getRealProperty(RealProperty.SIMTIME) == 1234.5
        
    def test_history_cputime(self, backend)
        # CPUTIME set/get via RealProperty
        
    def test_history_cost(self, backend)
        # COST set/get via RealProperty
        
    def test_cvg_inst_average(self, backend)
        # Create covergroup with 2 instances at 100% and 0% coverage
        # CVG_INST_AVERAGE == 50.0
```

### Task T6: `test_api_str_properties.py`

```python
class TestApiStrProperties:
    def test_history_cmdline(self, backend)
    def test_history_runcwd(self, backend)
    def test_test_date(self, backend)
    def test_test_username(self, backend)
    def test_test_seed(self, backend)
    def test_test_hostname(self, backend)
    def test_test_hostos(self, backend)
    def test_test_simargs(self, backend)
    def test_du_signature(self, backend)
    def test_toggle_canon_name(self, backend)   # depends on T1
    def test_expr_terms(self, backend)
    def test_unique_id_read_only(self, backend)
        # UNIQUE_ID is non-empty, consistent across read/write
    def test_version_properties(self, backend)
        # VER_VENDOR_ID, VER_VENDOR_TOOL, VER_VENDOR_TOOL_VERSION
    def test_comment_property(self, backend)
```

### Task T7: `test_api_cover_properties.py`

```python
class TestApiCoverProperties:
    def test_cover_goal(self, backend)
        # setIntProperty(idx, COVER_GOAL, 50)
        # getIntProperty(idx, COVER_GOAL) == 50
        
    def test_cover_limit(self, backend)
        # COVER_LIMIT: saturation count
        
    def test_cover_weight(self, backend)
        # COVER_WEIGHT on individual bins
        
    def test_stmt_index(self, backend)
        # STMT_INDEX set/get for multiple stmts on same line
        
    def test_branch_has_else(self, backend)
        # BRANCH_HAS_ELSE == 1 when else clause present
        
    def test_branch_iscase(self, backend)
        # BRANCH_ISCASE == 1 for case statement branch
        
    def test_scope_num_coveritems(self, backend)
        # SCOPE_NUM_COVERITEMS reads correct count
```

### Task T8: `test_api_cover_flags.py`

```python
class TestApiCoverFlags:
    def test_set_get_cover_flag(self, backend)
    def test_cover_flags_excluded(self, backend)
    def test_cover_flags_persist(self, backend)
```

### Task T9: `test_api_history_nodes.py`

```python
class TestApiHistoryNodes:
    def test_history_node_basic_properties(self, backend)
        # logicalName, physicalName, kind
    def test_history_node_all_test_status_values(self, backend)
        # OK, WARNING, ERROR, FATAL, MISSING, MERGE_ERROR
    def test_history_node_simtime_timeunit(self, backend)
    def test_history_node_cputime(self, backend)
    def test_history_node_seed_cmd_args(self, backend)
    def test_history_node_run_cwd(self, backend)
    def test_history_node_date_username_cost(self, backend)
    def test_history_node_toolcategory(self, backend)
    def test_history_node_vendor_info(self, backend)
    def test_history_node_compulsory(self, backend)
    def test_history_node_same_tests(self, backend)
    def test_history_node_comment(self, backend)
    def test_history_iterate_all(self, backend)
    def test_history_iterate_by_kind(self, backend)
```

### Task T10: `test_api_attributes.py`

```python
class TestApiAttributes:
    def test_add_get_attribute(self, backend)       # depends on P6
    def test_attribute_on_coveritem(self, backend)
    def test_attribute_on_history_node(self, backend)
    def test_iterate_attributes(self, backend)
    def test_remove_attribute(self, backend)
```

### Task T11: `test_api_tags.py`

```python
class TestApiTags:
    def test_add_tag(self, backend)                 # depends on P6
    def test_remove_tag(self, backend)
    def test_iterate_tags(self, backend)
```

### Task T12: `test_api_du_types.py`

```python
class TestApiDUTypes:
    def test_create_du_arch(self, backend)
    def test_create_du_package(self, backend)
    def test_create_du_program(self, backend)
    def test_create_du_interface(self, backend)
    def test_du_any_check(self, backend)
        # ScopeTypeT.DU_ANY() returns True for all DU types
```

### Task T13: `test_api_hdl_scopes.py`

```python
class TestApiHDLScopes:
    def test_create_process_scope(self, backend)    # depends on P3-1
    def test_create_block_scope(self, backend)
    def test_create_function_scope(self, backend)
    def test_create_task_scope(self, backend)
    def test_create_forkjoin_scope(self, backend)
    def test_create_generate_scope(self, backend)
    def test_create_package_scope(self, backend)
    def test_create_interface_scope(self, backend)
    def test_create_program_scope(self, backend)
```

### Task T14: `test_api_coverinstance.py`

```python
class TestApiCoverinstance:
    def test_create_coverinstance(self, backend)
        # COVERINSTANCE scope under a covergroup
    def test_coverinstance_get_coverinstances(self, backend)
        # getCoverInstances() returns list with our COVERINSTANCE
    def test_coverinstance_per_instance_property(self, backend)
        # CVG_PERINSTANCE and CVG_MERGEINSTANCES
```

### Task T15: `test_api_source_files.py`

```python
class TestApiSourceFiles:
    def test_get_source_files_empty(self, backend)
    def test_get_source_files_one(self, backend)
    def test_get_source_files_multiple(self, backend)
    def test_source_file_names(self, backend)
```

### Task T16: `test_api_delete.py` (Phase 13 dependency)

```python
class TestApiDelete:
    def test_remove_scope(self, backend)
    def test_remove_scope_removes_children(self, backend)
    def test_remove_cover(self, backend)
    def test_remove_sibling_unaffected(self, backend)
```

### Task T17: `test_api_unique_id.py` (Phase 15 dependency)

```python
class TestApiUniqueId:
    def test_scope_has_unique_id(self, backend)
    def test_cover_has_unique_id(self, backend)
    def test_match_scope_by_uid(self, backend)
    def test_match_cover_by_uid(self, backend)
    def test_uid_unique_across_scopes(self, backend)
```

### Task T18: `test_api_traversal.py` (Phase 12 dependency)

```python
class TestApiTraversal:
    def test_traverse_all_scopes(self, backend)
    def test_traverse_filtered(self, backend)
    def test_visitor_visits_all_scope_types(self, backend)
```

### Task T19: `test_api_du_names.py` (Phase 14)

```python
class TestApiDUNames:
    def test_parse_du_name_qualified(self)
    def test_parse_du_name_unqualified(self)
    def test_compose_du_name(self)
    def test_round_trip(self)
```

### Task T20: `test_api_path_separator.py`

```python
class TestApiPathSeparator:
    def test_default_path_separator(self, backend)
    def test_set_path_separator(self, backend)
    def test_path_separator_persist(self, backend)
```

---

## Summary Table

| Task ID | Description | Phase | Files Changed | Depends On |
|---------|-------------|-------|---------------|------------|
| P1-1 | Add `TOGGLE_METRIC` to `IntProperty` | 1 | `int_property.py` | — |
| P1-2 | Add `SUPPRESS_MODIFIED` to `IntProperty` | 1 | `int_property.py` | — |
| P1-3 | Populate `RealProperty` enum | 1 | `real_property.py` | — |
| P2-1 | Implement `MemToggleScope` | 2 | new `mem_toggle_scope.py` | P1-1 |
| P2-2 | Wire `MemScope.createToggle()` | 2 | `mem_scope.py` | P2-1 |
| P2-3 | Add TOGGLE to `MemScope.createScope()` | 2 | `mem_scope.py` | P2-1 |
| P2-4 | Implement `MemFSMScope` | 2 | new `mem_fsm_scope.py` | — |
| P2-5 | Add FSM to `MemScope.createScope()` | 2 | `mem_scope.py` | P2-4 |
| P2-6 | Add `createNextTransition()` to `Scope` | 2 | `scope.py` | P2-4 |
| P3-1 | Generic fallthrough in `MemScope.createScope()` | 3 | `mem_scope.py` | — |
| P4-1 | SQLite: specialize on create not just read | 4 | `sqlite_scope.py` | — |
| P4-2 | Fix `SqliteUCIS.getSourceFiles()` | 4 | `sqlite_ucis.py` | — |
| P4-3 | Fix `SqliteUCIS.getCoverInstances()` | 4 | `sqlite_ucis.py` | — |
| P4-4 | Fix `MemUCIS.getSourceFiles()` | 4 | `mem_ucis.py` | — |
| P4-5 | Fix `MemUCIS.getCoverInstances()` | 4 | `mem_ucis.py` | — |
| P5-1 | `RealProperty` in `MemHistoryNode` | 5 | `mem_history_node.py` | P1-3 |
| P5-2 | `RealProperty` in `SqliteHistoryNode` | 5 | `sqlite_history_node.py` | P1-3 |
| P5-3 | `CVG_INST_AVERAGE` on covergroup scopes | 5 | `mem_covergroup.py`, `sqlite_covergroup.py` | P1-3 |
| P6-1 | Attribute methods on abstract `Obj` | 6 | `obj.py` | — |
| P6-2 | Attribute methods in `SqliteObj` | 6 | `sqlite_obj.py` | P6-1 |
| P6-3 | Attribute methods in `MemObj` | 6 | `mem_obj.py` | P6-1 |
| P6-4 | Tag methods on abstract `Obj` | 6 | `obj.py` | P6-1 |
| P6-5 | Tag methods in `MemObj` and `SqliteObj` | 6 | `mem_obj.py`, `sqlite_obj.py` | P6-4 |
| P7-1 | `getCoverFlag`/`setCoverFlag` on abstract `Scope` | 7 | `scope.py` | — |
| P7-2 | Cover item flags in `MemCoverIndex` | 7 | `mem_cover_index.py` | P7-1 |
| P7-3 | Cover item flags in `SqliteCoverIndex` | 7 | `sqlite_cover_index.py` | P7-1 |
| P8-1 | `setCoverData` on abstract `Scope` | 8 | `scope.py` | — |
| P8-2 | `setCoverData` in `MemScope` | 8 | `mem_scope.py` | P8-1 |
| P8-3 | `setCoverData` in `SqliteScope` | 8 | `sqlite_scope.py` | P8-1 |
| P9-1 | Assertion scope creation (no new files) | 9 | — | P3-1, P4-1 |
| P9-2 | Document assertion coverage pattern | 9 | `scope.py` | — |
| P10-1 | Bin scope in Mem (via P3-1) | 10 | — | P3-1 |
| P10-2 | Bin scope iteration in SQLite | 10 | `sqlite_scope.py` | — |
| P11-1 | Implement `MemFactory.clone()` | 11 | `mem_factory.py` | — |
| P12-1 | Extend `UCISVisitor` | 12 | `UCISVisitor.py` | — |
| P12-2 | Add `traverse()` utility | 12 | `UCISVisitor.py` | P12-1 |
| P13-1 | `removeScope()` on abstract `UCIS` | 13 | `ucis.py` | — |
| P13-2 | `removeCover()` on abstract `Scope` | 13 | `scope.py` | — |
| P13-3 | `removeScope()` in `MemUCIS` | 13 | `mem_ucis.py`, `mem_scope.py` | P13-1 |
| P13-4 | `removeScope()` in `SqliteUCIS` | 13 | `sqlite_ucis.py` | P13-1 |
| P13-5 | `removeCover()` in Mem and SQLite | 13 | `mem_scope.py`, `sqlite_scope.py` | P13-2 |
| P14-1 | `parseDUName()` / `composeDUName()` | 14 | new `du_name.py` | — |
| P15-1 | Unique ID methods on abstract `UCIS` | 15 | `ucis.py` | — |
| P15-2 | Unique ID lookup in `MemUCIS` | 15 | `mem_ucis.py` | P15-1 |
| P15-3 | Unique ID lookup in `SqliteUCIS` | 15 | `sqlite_ucis.py` | P15-1 |
| T1 | `test_api_toggle_coverage.py` | T | new test file | P2-1, P2-2 |
| T2 | `test_api_fsm_coverage.py` | T | new test file | P2-4, P2-5 |
| T3 | `test_api_assertion_coverage.py` | T | new test file | P3-1, P4-1 |
| T4 | `test_api_bin_scopes.py` | T | new test file | P3-1 |
| T5 | `test_api_real_properties.py` | T | new test file | P5-1, P5-2 |
| T6 | `test_api_str_properties.py` | T | new test file | — |
| T7 | `test_api_cover_properties.py` | T | new test file | — |
| T8 | `test_api_cover_flags.py` | T | new test file | P7-1 |
| T9 | `test_api_history_nodes.py` | T | new test file | — |
| T10 | `test_api_attributes.py` | T | new test file | P6-1 |
| T11 | `test_api_tags.py` | T | new test file | P6-4 |
| T12 | `test_api_du_types.py` | T | new test file | — |
| T13 | `test_api_hdl_scopes.py` | T | new test file | P3-1 |
| T14 | `test_api_coverinstance.py` | T | new test file | P4-3, P4-5 |
| T15 | `test_api_source_files.py` | T | new test file | P4-2, P4-4 |
| T16 | `test_api_delete.py` | T | new test file | P13-1 |
| T17 | `test_api_unique_id.py` | T | new test file | P15-1 |
| T18 | `test_api_traversal.py` | T | new test file | P12-1 |
| T19 | `test_api_du_names.py` | T | new test file | P14-1 |
| T20 | `test_api_path_separator.py` | T | new test file | — |

**Total: 35 implementation tasks, 20 new test files**

---

## Recommended Execution Order

The following sequencing minimises rework and lets tests be written alongside
each implementation task:

1. **P1-1, P1-2, P1-3** — Property enum fixes (30 min, zero risk)
2. **P3-1** — Mem generic scope fallthrough (15 min, unblocks T3, T4, T12, T13)
3. **P2-1, P2-2, P2-3, T1** — Mem toggle scope + tests
4. **P2-4, P2-5, P2-6, T2** — Mem FSM scope + abstract API + tests
5. **P4-1** — SQLite specialise on create (10 min, unblocks SQLite T1/T2)
6. **T3, T4, T12, T13** — Write tests for assertion/bin/DU/HDL scopes (no new impl needed after P3-1)
7. **P5-1, P5-2, P5-3, T5** — RealProperty impl + tests
8. **T6, T7, T9** — Write StrProperty, cover property, and history node tests (existing impl, just untested)
9. **P4-2, P4-3, P4-4, P4-5, T14, T15** — Fix getSourceFiles/getCoverInstances + tests
10. **P7-1, P7-2, P7-3, T8** — Cover item flags
11. **P8-1, P8-2, P8-3** — setCoverData
12. **P11-1** — MemFactory.clone()
13. **P6-1 through P6-5, T10, T11** — Attribute and tag API
14. **P12-1, P12-2, T18** — Visitor extension + traversal
15. **P13-1 through P13-5, T16** — Delete operations
16. **P14-1, T19** — DU name utilities
17. **P15-1, P15-2, P15-3, T17** — Unique ID lookup
18. **T20** — Path separator tests
