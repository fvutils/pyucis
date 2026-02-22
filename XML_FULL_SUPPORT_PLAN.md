# UCIS XML Format — Comprehensive Support Plan

## Status

**Current state (as of this writing):**
- Tests: 508 passed, 7 xfailed
- XML writer implements: UCIS root, SOURCE_FILE, HISTORY_NODE, INSTANCE_COVERAGE
  (partial), COVERGROUP_COVERAGE, COVERPOINT, COVERPOINT_BIN (range), CROSS,
  CROSS_BIN
- XML reader implements: HISTORY_NODE, INSTANCE_COVERAGE (partial),
  COVERGROUP_COVERAGE, COVERPOINT, CROSS
- **3 xfails** in `test_xml_conversion.py` for cc1 (statement), cc2 (branch),
  cc5 (toggle) — writer does not yet emit those coverage types
- **Schema validation** in tests is not yet wired up

---

## 1. XML Schema vs UCIS Data Model — Complete Element Analysis

This section catalogs every XML complex type defined in UCIS LRM Chapter 9 and maps
it to the UCIS Python data model. Status codes:

- ✅ **Implemented** — both reader and writer handle this fully
- 🔶 **Partial** — implemented but with known gaps (noted)
- ❌ **Missing writer** — reader may handle it but writer does not
- 🚫 **Neither** — not in reader or writer
- 🔷 **XML-only concept** — no UCIS data model counterpart

### 1.1 Top-Level: UCIS element

| XML attribute/element | UCIS DM mapping | Status | Notes |
|----------------------|-----------------|--------|-------|
| `ucisVersion` | `db.getAPIVersion()` | ✅ | |
| `writtenBy` | `db.getWrittenBy()` | 🔶 | Writer uses `getpass.getuser()` instead of DB value |
| `writtenTime` | `db.getWrittenTime()` | 🔶 | Writer uses `date.today()` instead of DB value |
| `sourceFiles` | file handles | ✅ | Written from traversal of all scopes |
| `historyNodes` | `db.getHistoryNodes()` | ✅ | Dummy node added if DB has none |
| `instanceCoverages` | `ScopeTypeT.INSTANCE` scopes | ✅ | Written recursively |

**Gap**: `writtenBy` and `writtenTime` should come from `db.getWrittenBy()` /
`db.getWrittenTime()`, falling back to OS values only when the DB has none.

---

### 1.2 SOURCE_FILE

| XML attribute | UCIS DM mapping | Status |
|--------------|-----------------|--------|
| `fileName` | `file_handle.getFileName()` | ✅ |
| `id` | XML-local integer handle | ✅ |

No gaps. `id` is XML-local and managed by the writer.

---

### 1.3 HISTORY_NODE

| XML attribute/element | UCIS DM mapping | Status | Notes |
|----------------------|-----------------|--------|-------|
| `historyNodeId` | XML-local handle | ✅ | Sequential |
| `parentId` | parent node reference | 🚫 | Not written or read |
| `logicalName` | `h.getLogicalName()` | ✅ | |
| `physicalName` | `h.getPhysicalName()` | ✅ | |
| `kind` | `h.getKind()` | ✅ | |
| `testStatus` | `h.getTestStatus()` | ✅ | |
| `date` | `h.getDate()` | ✅ | |
| `toolCategory` | `h.getToolCategory()` | ✅ | |
| `ucisVersion` | `h.getUCISVersion()` | ✅ | |
| `vendorId` | `h.getVendorId()` | ✅ | |
| `vendorTool` | `h.getVendorTool()` | ✅ | |
| `vendorToolVersion` | `h.getVendorToolVersion()` | ✅ | |
| `simtime` | `h.getSimTime()` | ✅ | |
| `timeunit` | `h.getTimeUnit()` | ✅ | |
| `cpuTime` | `h.getCpuTime()` | ✅ | |
| `userName` | `h.getUserName()` | ✅ | |
| `seed` | `h.getSeed()` | ✅ | |
| `cost` | `h.getCost()` | ✅ | |
| `args` | `h.getArgs()` | ✅ | |
| `cmd` | `h.getCmd()` | ✅ | |
| `runCwd` | `h.getRunCwd()` | ✅ | |
| `compulsory` | `h.getCompulsory()` | ✅ | |
| `sameTests` | `h.getSameTests()` | ✅ | |
| `comment` | `h.getComment()` | ✅ | |
| `userAttr` child elements | user attributes | 🚫 | Not in Python DM API |

**Gap**: `parentId` is not written or read. Affects merged databases where history
nodes have parent/child relationships. The `userAttr` elements are XML extensions
not represented in the Python DM.

---

### 1.4 INSTANCE_COVERAGE

| XML attribute/element | UCIS DM mapping | Status | Notes |
|----------------------|-----------------|--------|-------|
| `name` | `s.getScopeName()` | ✅ | |
| `key` | XML-local | ✅ | Written as "0" |
| `instanceId` | XML-local handle | ✅ | Sequential |
| `alias` | alias attribute | 🚫 | Not written |
| `moduleName` | `s.getInstanceDu().getScopeName()` | ✅ | |
| `parentInstanceId` | parent instance reference | ✅ | |
| `designParameter` (NAME_VALUE list) | design parameters | 🚫 | Not in Python DM API |
| `id` (STATEMENT_ID) | `s.getSourceInfo()` | 🔶 | Written; file id lookup may be off-by-one |
| `toggleCoverage` | `ScopeTypeT.TOGGLE` scopes | ❌ | **Writer missing** |
| `blockCoverage` | `ScopeTypeT.BLOCK` scopes | ❌ | **Writer missing** |
| `conditionCoverage` | `ScopeTypeT.CONDITION` scopes | 🚫 | **Neither reader nor writer** |
| `branchCoverage` | `ScopeTypeT.BRANCH` scopes | ❌ | **Writer missing** |
| `fsmCoverage` | `ScopeTypeT.FSM` scopes | 🚫 | **Neither reader nor writer** |
| `assertionCoverage` | `ScopeTypeT.ASSERT` scopes | 🚫 | **Neither reader nor writer** |
| `covergroupCoverage` | `ScopeTypeT.COVERGROUP` scopes | ✅ | |
| `userAttr` | user attributes | 🚫 | Not in Python DM API |

---

### 1.5 TOGGLE_COVERAGE and Sub-types

**TOGGLE_COVERAGE:**

| XML element/attr | UCIS DM mapping | Status |
|-----------------|-----------------|--------|
| `toggleObject` list | TOGGLE scope objects | ❌ **Writer missing entirely** |
| `metricMode` (METRIC_MODE) | mode string | ❌ |
| `weight` | scope weight | ❌ |
| `userAttr` | user attributes | 🚫 |

**TOGGLE_OBJECT:**

| XML element/attr | UCIS DM mapping | Status |
|-----------------|-----------------|--------|
| `name` | signal scope name | ❌ |
| `key` | XML-local | ❌ |
| `type` | signal type string (wire, reg, etc.) | ❌ |
| `portDirection` | port direction | ❌ |
| `dimension` (DIMENSION list) | vector dimensions | ❌ |
| `id` (STATEMENT_ID) | source info | ❌ |
| `toggleBit` (TOGGLE_BIT list) | per-bit coverage | ❌ |
| `objAttributes` (alias, weight, excluded) | object attributes | ❌ |

**TOGGLE_BIT:**

| XML element/attr | UCIS DM mapping | Status |
|-----------------|-----------------|--------|
| `name` | bit name, e.g. `ff1[2]` | ❌ |
| `key` | XML-local | ❌ |
| `index` (nonNegInt list) | multi-dim indices | ❌ |
| `toggle` (TOGGLE list) | 0→1 and 1→0 transitions | ❌ |
| `objAttributes` | object attributes | ❌ |

**TOGGLE:**

| XML element/attr | UCIS DM mapping | Status |
|-----------------|-----------------|--------|
| `from` | transition start value (e.g. "0") | ❌ |
| `to` | transition end value (e.g. "1") | ❌ |
| `bin` (BIN) | coverage count | ❌ |

---

### 1.6 COVERGROUP_COVERAGE and Sub-types

**COVERGROUP_COVERAGE:**

| XML element/attr | UCIS DM mapping | Status | Notes |
|-----------------|-----------------|--------|-------|
| `cgInstance` (list) | COVERINSTANCE scope | ✅ | |
| `metricMode` | mode string | 🚫 | Not written |
| `weight` | covergroup weight | 🔶 | Not written |
| `userAttr` | user attributes | 🚫 | |

**CGINSTANCE:**

| XML element/attr | UCIS DM mapping | Status | Notes |
|-----------------|-----------------|--------|-------|
| `name` | `cg.getScopeName()` | ✅ | |
| `key` | XML-local | ✅ | |
| `alias` | alias attribute | 🚫 | |
| `excluded` | excluded flag | 🚫 | |
| `options` (CGINST_OPTIONS) | weight/goal/at_least/etc. | ✅ | |
| `cgId` (CG_ID) | declaration info | 🔶 | Source IDs written as dummy "1,1,1" |
| `cgParms` (NAME_VALUE list) | design parameters | 🚫 | Not in Python DM API |
| `coverpoint` list | COVERPOINT scopes | ✅ | |
| `cross` list | CROSS scopes | ✅ | |
| `userAttr` | user attributes | 🚫 | |

**CGINST_OPTIONS:**

| XML attribute | UCIS DM mapping | Status |
|--------------|-----------------|--------|
| `weight` | `getWeight()` | ✅ |
| `goal` | `getGoal()` | ✅ |
| `comment` | `getComment()` | 🚫 |
| `at_least` | `getAtLeast()` | ✅ |
| `detect_overlap` | `getDetectOverlap()` | 🔶 |
| `auto_bin_max` | `getAutoBinMax()` | 🔶 |
| `cross_num_print_missing` | `getCrossNumPrintMissing()` | 🚫 |
| `per_instance` | `getPerInstance()` | 🔶 |
| `merge_instances` | `getMergeInstances()` | 🔶 |

**COVERPOINT:**

| XML element/attr | UCIS DM mapping | Status |
|-----------------|-----------------|--------|
| `name` | `cp.getScopeName()` | ✅ |
| `key` | XML-local | ✅ |
| `exprString` | expression string | 🚫 Not written |
| `alias` | alias | 🚫 |
| `options` (COVERPOINT_OPTIONS) | weight/goal/at_least/etc. | ✅ |
| `coverpointBin` list | CVGBIN / IGNOREBIN / ILLEGALBIN items | 🔶 range from/to are "-1" (meaningless) |

**COVERPOINT_BIN:**

| XML element/attr | UCIS DM mapping | Status | Notes |
|-----------------|-----------------|--------|-------|
| `name` | bin name | ✅ | |
| `key` | XML-local | ✅ | |
| `type` | bins/ignore/illegal | ✅ | |
| `alias` | alias | 🚫 | |
| `range` (RANGE_VALUE) | value ranges | 🔶 | from/to always -1 |
| `sequence` (SEQUENCE) | transition sequences | 🚫 | Not written |
| `contents.coverageCount` | bin hit count | ✅ | |
| `contents.historyNodeId` list | per-bin test attribution | 🚫 | Not in Python DM |

**CROSS:**

| XML element/attr | UCIS DM mapping | Status |
|-----------------|-----------------|--------|
| `name` | `cr.getScopeName()` | ✅ |
| `key` | XML-local | ✅ |
| `alias` | alias | 🚫 |
| `options` (CROSS_OPTIONS) | weight/goal/at_least | ✅ |
| `crossExpr` (string list) | crossed coverpoint names | ✅ |
| `crossBin` list | cross bins | 🔶 index always -1 |

**CROSS_BIN:**

| XML element/attr | UCIS DM mapping | Status | Notes |
|-----------------|-----------------|--------|-------|
| `name` | bin name | ✅ | |
| `key` | XML-local | ✅ | |
| `type` | default/ignore/illegal | 🔶 | Always "default" |
| `alias` | alias | 🚫 | |
| `index` (int list) | coverpoint bin ordinals | 🔶 | Always -1 |
| `contents.coverageCount` | hit count | ✅ | |

---

### 1.7 CONDITION_COVERAGE and EXPR

| XML element | UCIS DM mapping | Status |
|------------|-----------------|--------|
| `expr` (EXPR list) | expression objects | 🚫 **Neither reader nor writer** |
| `metricMode` | mode string | 🚫 |
| `userAttr` | user attributes | 🚫 |

**EXPR** (highly complex, multi-mode, hierarchical):

| XML element/attr | Status |
|-----------------|--------|
| `name`, `key`, `exprString`, `index`, `width` | 🚫 |
| `statementType` | 🚫 |
| `id` (STATEMENT_ID) | 🚫 |
| `subExpr` (string list) | 🚫 |
| `exprBin` (EXPR_BIN list) | 🚫 |
| `hierarchicalExpr` (EXPR list, recursive) | 🚫 |
| `objAttributes` | 🚫 |

**Assessment**: Condition/expression coverage is the most complex XML type. The
Python UCIS DM has `ScopeTypeT.EXPR` / `ScopeTypeT.CONDITION` scopes but the
writer/reader support for them is zero. The multi-mode (BITWISE_FLAT, STD_HIER,
BITWISE_VECTOR) semantics require deep DM changes to support faithfully. **This
feature is documented as out of scope for this plan.**

---

### 1.8 ASSERTION_COVERAGE and ASSERTION

| XML element | UCIS DM mapping | Status |
|------------|-----------------|--------|
| `assertion` (ASSERTION list) | assertion objects | 🚫 **Neither reader nor writer** |
| `metricMode` | mode string | 🚫 |
| `userAttr` | user attributes | 🚫 |

**ASSERTION:**

| XML element/attr | UCIS DM mapping | Status |
|-----------------|-----------------|--------|
| `name` | assertion scope name | 🚫 |
| `nameComponent` | UCIS name component | 🚫 |
| `typeComponent` | UCIS type component | 🚫 |
| `assertionKind` | assert / cover / assume | 🚫 |
| `coverBin` (BIN) | cover property bin | 🚫 |
| `passBin` (BIN) | pass bin | 🚫 |
| `failBin` (BIN) | fail bin | 🚫 |
| `vacuousBin` (BIN) | vacuous pass bin | 🚫 |
| `disabledBin` (BIN) | disabled bin | 🚫 |
| `attemptBin` (BIN) | attempt bin | 🚫 |
| `activeBin` (BIN) | active thread bin | 🚫 |
| `peakActiveBin` (BIN) | peak active threads bin | 🚫 |
| `objAttributes` | weight, alias, excluded | 🚫 |

---

### 1.9 FSM_COVERAGE, FSM, FSM_STATE, FSM_TRANSITION

| XML element | UCIS DM mapping | Status |
|------------|-----------------|--------|
| `fsm` (FSM list) | FSM scope objects | 🚫 **Neither reader nor writer** |
| `metricMode` | mode string | 🚫 |
| `userAttr` | user attributes | 🚫 |

**FSM:**

| XML element/attr | UCIS DM mapping | Status |
|-----------------|-----------------|--------|
| `name` | FSM register name | 🚫 |
| `type` | register type (reg, logic) | 🚫 |
| `width` | register width in bits | 🚫 |
| `state` (FSM_STATE list) | state cover items | 🚫 |
| `stateTransition` (FSM_TRANSITION list) | transition cover items | 🚫 |
| `objAttributes` | weight, alias, excluded | 🚫 |

**FSM_STATE:**

| XML element/attr | UCIS DM mapping | Status |
|-----------------|-----------------|--------|
| `stateName` | state name string | 🚫 |
| `stateValue` | state integer value | 🚫 |
| `stateBin` (BIN) | coverage count | 🚫 |

**FSM_TRANSITION:**

| XML element/attr | UCIS DM mapping | Status |
|-----------------|-----------------|--------|
| `state` (string list, ≥ 2) | from/to state values | 🚫 |
| `transitionBin` (BIN) | coverage count | 🚫 |

---

### 1.10 BLOCK_COVERAGE, PROCESS_BLOCK, BLOCK, STATEMENT

**BLOCK_COVERAGE:**

| XML element | UCIS DM mapping | Status | Notes |
|------------|-----------------|--------|-------|
| `process` (PROCESS_BLOCK list) OR `block` (BLOCK list) OR `statement` (STATEMENT list) | block/stmt scopes | ❌ **Writer missing** | Three alternative representations |
| `metricMode` | mode string | ❌ | |
| `userAttr` | user attributes | 🚫 | |

**STATEMENT** (flat representation — preferred for writer):

| XML element/attr | UCIS DM mapping | Status |
|-----------------|-----------------|--------|
| `id` (STATEMENT_ID) | `stmt.getSourceInfo()` | ❌ |
| `bin` (BIN) | statement hit count | ❌ |
| `objAttributes` | weight, alias, excluded | ❌ |

**BLOCK** (hierarchical representation):

| XML element/attr | UCIS DM mapping | Status |
|-----------------|-----------------|--------|
| `statementId` (STATEMENT_ID list) | statement IDs in block | ❌ |
| `hierarchicalBlock` (BLOCK list, recursive) | nested blocks | ❌ |
| `blockBin` (BIN) | block hit count | ❌ |
| `blockId` (STATEMENT_ID) | block source location | ❌ |
| `parentProcess` | process type string | ❌ |

**PROCESS_BLOCK:**

| XML element/attr | UCIS DM mapping | Status |
|-----------------|-----------------|--------|
| `processType` | always / initial / etc. | ❌ |
| `block` (BLOCK list) | blocks in process | ❌ |

---

### 1.11 BRANCH_COVERAGE, BRANCH_STATEMENT, BRANCH

**BRANCH_COVERAGE:**

| XML element | UCIS DM mapping | Status |
|------------|-----------------|--------|
| `statement` (BRANCH_STATEMENT list) | branching statements | ❌ **Writer missing** |
| `metricMode` | mode string | ❌ |
| `userAttr` | user attributes | 🚫 |

**BRANCH_STATEMENT:**

| XML element/attr | UCIS DM mapping | Status |
|-----------------|-----------------|--------|
| `id` (STATEMENT_ID) | source location of if/case statement | ❌ |
| `branchExpr` | condition expression string | ❌ |
| `statementType` | if / case / ? | ❌ |
| `branch` (BRANCH list) | branch arms | ❌ |

**BRANCH:**

| XML element/attr | UCIS DM mapping | Status |
|-----------------|-----------------|--------|
| `id` (STATEMENT_ID) | branch arm source location | ❌ |
| `nestedBranch` (BRANCH_STATEMENT list, recursive) | nested if/case | ❌ |
| `branchBin` (BIN) | branch hit count | ❌ |

---

### 1.12 Shared / Primitive Types

| Type | Status | Notes |
|------|--------|-------|
| BIN | 🔶 | Partially written; `binAttributes` (alias, excluded) not written |
| BIN_CONTENTS | 🔶 | `coverageCount` ✅; `historyNodeId` list 🚫; `nameComponent`/`typeComponent` 🚫 |
| RANGE_VALUE | 🔶 | Written for coverpoint bins but `from`/`to` always -1 |
| SEQUENCE | 🚫 | Not written (transition bins) |
| binAttributes | 🔶 | `weight`/`goal` ✅; `alias`/`excluded`/`excludedReason` 🚫 |
| objAttributes | 🚫 | Not written for any scope |
| USER_ATTR | 🚫 | Not in Python DM API — silently ignored |
| NAME_VALUE | 🚫 | Not written |
| DIMENSION | 🚫 | Not written; needed for toggle vector signals |
| STATEMENT_ID | 🔶 | Written for instance `id`; file-id lookup may be off-by-one |
| METRIC_MODE | 🚫 | Not written |
| metricAttributes | 🚫 | Not written |

---

## 2. What Can and Cannot Be Represented

### 2.1 Fully Representable (lossless in practice after this plan)

- History nodes with all test metadata fields (after W1-fix)
- Instance hierarchy (DU + instance scopes, parent references)
- Source file handles (fileName ↔ id mapping)
- Covergroup coverage: covergroups, coverinstances, coverpoints, crosses, bins
  (bin names, types bins/ignore/illegal, hit counts)
- Covergroup options: weight, goal, at_least, per_instance, merge_instances,
  auto_bin_max, detect_overlap
- Statement coverage (BLOCK_COVERAGE flat statement mode, per-statement hit counts)
- Branch coverage (BRANCH_COVERAGE with if/case branching statements, nested)
- Toggle coverage (TOGGLE_COVERAGE, per-signal per-bit 0→1 and 1→0 bins)
- FSM state coverage + FSM transition coverage
- Assertion coverage (cover/assert with up to 8 bin kinds)

### 2.2 Limitations and Caveats

| Item | Limitation |
|------|-----------|
| Coverpoint bin range values | `RANGE_VALUE.from`/`.to` are not meaningful — the Python DM stores only bin names and hit counts, not the exact integer ranges. Written as `from="-1" to="-1"`. |
| Transition bins (SEQUENCE) | Not supported — the Python DM does not expose transition sequences via the `coverItem` API. |
| Cross bin indices | `CROSS_BIN.index` references coverpoint bin ordinals. The DM does not expose these, so they are written as -1. |
| BIN_CONTENTS historyNodeId list | Per-bin test attribution is not in the Python DM API. The list is always empty on write. |
| BIN nameComponent / typeComponent | Internal UCIS UID components; not round-tripped. |
| `alias` on objects | Not currently round-tripped. |
| `excluded` / `excludedReason` on objects | Not fully round-tripped. |
| `userAttr` (USER_ATTR) | Not in Python DM API — silently dropped on read; not emitted on write. |
| `designParameter` / `cgParms` | Not in Python DM API — dropped. |
| `parentId` in HISTORY_NODE | Parent-child history node relationships not preserved. |
| `writtenBy` / `writtenTime` | Uses OS fallback instead of DB metadata (minor, easy fix). |

### 2.3 Explicitly Not Supported (document prominently)

- **`CONDITION_COVERAGE` / `EXPR`** — condition and expression coverage. The XML
  schema supports multi-mode hierarchical expression bins (BITWISE_FLAT,
  STD_HIER, etc.). The Python UCIS DM does not expose these at the granularity
  needed for round-trip fidelity. When encountered during read, these elements
  are silently ignored. When writing, no `conditionCoverage` elements are emitted.
  The writer will issue `ctx.warn("xml: condition coverage is not supported — %d scope(s) skipped")`.

- **`userAttr` (USER_ATTR)** — tool-specific user attributes. Not in the Python DM
  API. Silently dropped on read; not emitted on write.

- **`designParameter` and `cgParms`** — design parameterization metadata. Dropped.

- **`BIN_CONTENTS.historyNodeId` list** — per-bin test attribution is not in the
  Python DM API and is dropped.

- **Transition bins (SEQUENCE)** — `coverpointBin` elements with `<sequence>`
  instead of `<range>`. The DM does not expose transition sequences.

- **Cross bin `index` values** — meaningful coverpoint bin ordinals for cross bins
  are not exposed by the DM.

---

## 3. Implementation Plan

### Phase W1 — Fix existing writer gaps (resolves 3 xfails)

These are the highest priority items — they fix known xfailing tests.

#### W1-1: BLOCK_COVERAGE (statement) writer

Add `write_block_coverage(inst_elem, inst_scope)` to `xml_writer.py`.

Use **flat statement mode** (simplest of the three allowed representations):

```xml
<blockCoverage>
  <statement>
    <id file="1" line="42" inlineCount="1"/>
    <bin>
      <contents coverageCount="5"/>
    </bin>
  </statement>
</blockCoverage>
```

Implementation steps:
1. In `write_instance_coverages`, after `write_covergroups()`, add a call to
   `write_block_coverage(inst, s)`.
2. Iterate `s.scopes(ScopeTypeT.BLOCK)` — each BLOCK scope contains statement
   cover items.
3. For each block scope, emit `<blockCoverage>` with `metricMode` from scope name.
4. For each cover item in the block scope (CoverTypeT.STMTBIN or similar), emit
   `<statement>` with `<id>` and `<bin>`.

**Key**: Study `ucis_builders.py::build_cc1_statement_coverage` to understand the
scope type hierarchy used to represent statement coverage in the Python DM.

**Acceptance**: `test_xml_conversion.py[cc1_statement_coverage]` passes and XML
validates against schema.

#### W1-2: BRANCH_COVERAGE writer

Add `write_branch_coverage(inst_elem, inst_scope)` to `xml_writer.py`.

```xml
<branchCoverage>
  <statement statementType="if">
    <id file="1" line="10" inlineCount="1"/>
    <branch>
      <id file="1" line="11" inlineCount="1"/>
      <branchBin>
        <contents coverageCount="3"/>
      </branchBin>
    </branch>
    <branch>
      <id file="1" line="13" inlineCount="1"/>
      <branchBin>
        <contents coverageCount="1"/>
      </branchBin>
    </branch>
  </statement>
</branchCoverage>
```

Implementation steps:
1. In `write_instance_coverages`, add call to `write_branch_coverage(inst, s)`.
2. Iterate `s.scopes(ScopeTypeT.BRANCH)` — each BRANCH scope has branch arm
   cover items.
3. For each BRANCH scope emit `<branchCoverage>` → `<statement>` → `<branch>`
   with a `<branchBin>`.

**Acceptance**: `test_xml_conversion.py[cc2_branch_coverage]` passes.

#### W1-3: TOGGLE_COVERAGE writer

Add `write_toggle_coverage(inst_elem, inst_scope)` to `xml_writer.py`.

```xml
<toggleCoverage>
  <toggleObject name="ff1" type="wire" key="0">
    <id file="1" line="5" inlineCount="1"/>
    <toggleBit name="ff1[0]" key="0">
      <toggle from="0" to="1">
        <bin><contents coverageCount="4"/></bin>
      </toggle>
      <toggle from="1" to="0">
        <bin><contents coverageCount="3"/></bin>
      </toggle>
    </toggleBit>
  </toggleObject>
</toggleCoverage>
```

Implementation steps:
1. In `write_instance_coverages`, add call to `write_toggle_coverage(inst, s)`.
2. Iterate `s.scopes(ScopeTypeT.TOGGLE)` — each TOGGLE scope represents one signal.
3. For each TOGGLE scope emit `<toggleCoverage>` → `<toggleObject>`.
4. For each cover item, determine if it is a 0→1 or 1→0 transition and emit the
   appropriate `<toggleBit>` / `<toggle>` elements.

**Key**: Study `ucis_builders.py::build_cc5_toggle_coverage` and the existing
`xml_reader.py` (which already reads toggle) to understand the DM structure.

**Acceptance**: `test_xml_conversion.py[cc5_toggle_coverage]` passes.

---

### Phase W2 — FSM and Assertion coverage writer (medium priority)

#### W2-1: FSM_COVERAGE writer

Add `write_fsm_coverage(inst_elem, inst_scope)`:
- Iterate `s.scopes(ScopeTypeT.FSM)` scopes
- Emit `<fsmCoverage>` → `<fsm>` with name, type, width attributes
- For state cover items (CoverTypeT.STATEBIN), emit `<state>` with `stateBin`
- For transition cover items (CoverTypeT.TRANSITIONBIN), emit `<stateTransition>`
  with `<state>` values and `<transitionBin>`

Also add reader if not already present (audit `xml_reader.py` first).

#### W2-2: ASSERTION_COVERAGE writer

Add `write_assertion_coverage(inst_elem, inst_scope)`:
- Iterate `s.scopes(ScopeTypeT.ASSERT)` scopes
- Emit `<assertionCoverage>` → `<assertion>` with `name` and `assertionKind`
- Map each assertion bin type to the correct XML bin element:
  - `CoverTypeT.ASSERTCOVER` → `<coverBin>`
  - `CoverTypeT.ASSERTPASS` → `<passBin>`
  - `CoverTypeT.ASSERTFAIL` → `<failBin>`
  - `CoverTypeT.ASSERTVACUOUS` → `<vacuousBin>`
  - `CoverTypeT.ASSERTDISABLED` → `<disabledBin>`
  - `CoverTypeT.ASSERTATTEMPT` → `<attemptBin>`
  - `CoverTypeT.ASSERTACTIVE` → `<activeBin>`

Also add reader if not already present.

---

### Phase W3 — Reader completeness audit and fixes

Audit `xml_reader.py` against this plan:

#### W3-1: Toggle reader audit
- Confirm `readInstanceCoverage` calls a toggle reader
- If missing, add `readToggleCoverage` method

#### W3-2: Block/statement reader audit
- Confirm block/statement is read; add if missing

#### W3-3: Branch reader audit
- Confirm branch is read; add if missing

#### W3-4: FSM reader (after W2-1)
- Add `readFsmCoverage` method

#### W3-5: Assertion reader (after W2-2)
- Add `readAssertionCoverage` method

---

### Phase W4 — Writer quality improvements (lower priority)

#### W4-1: Fix `writtenBy` / `writtenTime` to use DB metadata

```python
wb = db.getWrittenBy()
self.setAttr(self.root, "writtenBy", wb or getpass.getuser())
wt = db.getWrittenTime()
self.setAttrDateTime(self.root, "writtenTime",
                     wt or datetime.now().strftime("%Y%m%d%H%M%S"))
```

#### W4-2: Fix HISTORY_NODE `parentId`

Track a `{history_node: id}` map. When a history node has a non-null parent,
emit `parentId` referencing the parent's assigned integer id.

#### W4-3: Fix STATEMENT_ID file lookup (off-by-one potential)

Verify `file_id_m` starts from 1 and `addId` uses the correct key. Write a unit
test asserting that the id in `<id file="X">` matches the id in the
`<sourceFiles id="X">` element for the same file.

#### W4-4: Emit `ctx.warn()` for unsupported features

Add after W1 is done:
```python
# In write_instance_coverages()
for _ in s.scopes(ScopeTypeT.CONDITION):
    if ctx:
        ctx.warn("xml: condition/expression coverage is not supported — scopes skipped")
    break  # warn once per instance
```

---

## 4. Test Plan

### 4.1 Wire Schema Validation Into Existing Tests

Add a `schema_validate` helper to `tests/conversion/test_xml_conversion.py`:

```python
def validate_xml_schema(filepath):
    from ucis.xml.ucis_validator import UcisValidator
    result = UcisValidator.validate(filepath)
    assert result is True, f"XML failed schema validation: {filepath}"
```

Call it in `test_write_roundtrip` after writing XML. This is a one-line addition
and applies immediately to all existing tests.

### 4.2 Remove xfails as phases complete

After W1-1: remove `"cc1_statement_coverage"` from `_XML_WRITER_UNIMPLEMENTED`
After W1-2: remove `"cc2_branch_coverage"`
After W1-3: remove `"cc5_toggle_coverage"`

The set should be empty after W1 is complete.

### 4.3 New Builder / Verifier Pairs

Add to `tests/conversion/builders/ucis_builders.py`:
- `build_cc7_fsm_state_coverage` / `verify_cc7_fsm_state_coverage` (after W2-1)
- `build_cc8_fsm_transition_coverage` / `verify_cc8_fsm_transition_coverage`
- `build_as1_cover_assertion` / `verify_as1_cover_assertion` (after W2-2)
- `build_as2_assert_property` / `verify_as2_assert_property`

These builders are added to `ALL_BUILDERS` so they automatically participate in
the XML round-trip tests and the UCIS-to-UCIS parameterized tests.

### 4.4 Golden File Tests

Create `tests/conversion/fixtures/xml/` with hand-crafted valid XML files:
- `toggle_2state.xml` — toggle coverage with 2STOGGLE mode
- `assertion_cover.xml` — cover property assertion
- `fsm_example.xml` — FSM state + transition coverage
- `block_statement.xml` — flat statement coverage
- `branch_nested.xml` — nested branch coverage (if/case nesting)

Each file is read by `xml_fmt.read()` and verified with the corresponding
`verify_*` function.

```python
@pytest.mark.parametrize("fixture_file,verify_fn", [
    ("fixtures/xml/toggle_2state.xml", verify_cc5_toggle_coverage),
    ("fixtures/xml/fsm_example.xml", verify_cc7_fsm_state_coverage),
    ("fixtures/xml/assertion_cover.xml", verify_as1_cover_assertion),
    ("fixtures/xml/block_statement.xml", verify_cc1_statement_coverage),
    ("fixtures/xml/branch_nested.xml", verify_cc2_branch_coverage),
])
def test_read_golden_file(self, fixture_file, verify_fn):
    db = xml_fmt.read(os.path.join(os.path.dirname(__file__), fixture_file))
    verify_fn(db)
```

### 4.5 Schema-Validity Smoke Test for Every Builder

```python
def test_all_builders_schema_valid(self, xml_fmt, tmp_xml, schema_validate):
    """Every builder, even unsupported ones, must produce schema-valid XML."""
    src = MemUCIS()
    for build_fn, _ in ALL_BUILDERS:
        build_fn(src)
    xml_fmt.write(src, tmp_xml)
    schema_validate(tmp_xml)
```

This catches any writer regression that produces invalid XML.

### 4.6 `ctx.warn()` Tests for Condition Coverage

```python
def test_condition_coverage_warns(self, xml_fmt, tmp_xml):
    """Writing condition coverage emits a ctx.warn() and does not error."""
    db = MemUCIS()
    # build a DB with a CONDITION scope
    build_condition_coverage(db)
    ctx = ConversionContext(strict=False)
    xml_fmt.write(db, tmp_xml, ctx=ctx)
    assert any("condition" in w.lower() for w in ctx.warnings)

def test_condition_coverage_strict(self, xml_fmt, tmp_xml):
    """Strict mode raises ConversionError for unsupported condition coverage."""
    db = MemUCIS()
    build_condition_coverage(db)
    ctx = ConversionContext(strict=True)
    with pytest.raises(ConversionError):
        xml_fmt.write(db, tmp_xml, ctx=ctx)
```

---

## 5. Documentation Plan

### 5.1 New Documentation File: `doc/xml_format.md`

Contents:
1. **Overview** — what UCIS XML is, where the spec lives (LRM §9)
2. **Supported features table** — all coverage types with ✅/⚠/❌
3. **Reading XML** — Python code example using `FormatRgy`
4. **Writing XML** — Python code example
5. **Known limitations** — range values, cross indices, condition coverage, etc.
6. **Schema validation** — how to validate output against `ucis.xsd`
7. **Migration note** — XML used to be a MemUCIS backend; now it is a pure
   import/export format

### 5.2 Module Docstrings

`xml_writer.py` class docstring should include:
```
Supported XML elements: UCIS, SOURCE_FILE, HISTORY_NODE, INSTANCE_COVERAGE,
COVERGROUP_COVERAGE (cgInstance, coverpoint, cross, bins), BLOCK_COVERAGE
(statement mode), BRANCH_COVERAGE, TOGGLE_COVERAGE, FSM_COVERAGE,
ASSERTION_COVERAGE.

Explicitly NOT supported: CONDITION_COVERAGE / EXPR (complex multi-mode
hierarchical expression bins), userAttr, designParameter, coverpoint bin
range values (from/to written as -1), cross bin ordinal indices.
```

`xml_reader.py` class docstring should mirror this.

### 5.3 README Format Matrix Update

After W1 and W2, update the format capability matrix in `README.md`:

| UCIS Feature | XML |
|---|---|
| Statement coverage | ✅ (after W1-1) |
| Branch coverage | ✅ (after W1-2) |
| Toggle coverage | ✅ (after W1-3) |
| FSM coverage | ✅ (after W2-1) |
| Assertion coverage | ✅ (after W2-2) |
| Condition/expression coverage | ⚠ Not supported |

---

## 6. Priority and Sequencing

| Priority | Task | Effort | Outcome |
|----------|------|--------|---------|
| 🔴 1 | W1-1: BLOCK_COVERAGE writer | Medium | Fixes cc1 xfail |
| 🔴 2 | W1-2: BRANCH_COVERAGE writer | Medium | Fixes cc2 xfail |
| 🔴 3 | W1-3: TOGGLE_COVERAGE writer | Medium | Fixes cc5 xfail |
| 🔴 4 | Schema validation in tests | Small | Quality gate for all XML tests |
| 🟡 5 | W3-1 to W3-3: Audit reader | Small | Round-trip completeness |
| 🟡 6 | W2-1: FSM_COVERAGE writer | Medium | New cc7/cc8 tests pass |
| 🟡 7 | W2-2: ASSERTION_COVERAGE writer | Medium | New as1/as2 tests pass |
| 🟡 8 | W3-4/W3-5: FSM/Assertion reader | Small | Depends on W2 |
| 🟢 9 | W4-1: Fix writtenBy/writtenTime | Tiny | Metadata fidelity |
| 🟢 10 | W4-2: HISTORY_NODE parentId | Small | Merge fidelity |
| 🟢 11 | W4-3: STATEMENT_ID file lookup | Tiny | Correctness |
| 🟢 12 | W4-4: ctx.warn for unsupported | Small | ConversionContext completeness |
| 🟢 13 | Golden file tests | Small | Reader regression protection |
| 🟢 14 | doc/xml_format.md | Small | Documentation |
| 🟢 15 | Module docstrings | Tiny | Documentation |

---

## 7. Key Design Decisions

### Q: Which BLOCK_COVERAGE representation to use?

**Decision**: Flat `statement` mode. The spec allows three equivalent alternatives
(process → block → statement, block → statement, or flat statement list). The flat
mode is the simplest to implement and sufficient for storing hit counts per source
location. No information is lost relative to what the Python DM exposes.

### Q: Should CONDITION_COVERAGE ever be emitted?

**Decision**: No. The Python DM does not expose the per-expression bin structure
needed for faithful XML. Writing partial condition XML would either be schema-invalid
or misleading. The writer emits `ctx.warn()` and skips condition scopes entirely.

### Q: What should the writer do with unknown scope types?

**Decision**: Skip them silently (debug log only). Unknown scope types are tool
extensions not covered by the UCIS spec. The writer should not fail.

### Q: Should the reader fail on unrecognized XML elements?

**Decision**: No — silently ignore unknown elements. This ensures compatibility
with UCIS tool extensions and future spec versions.

### Q: How do TOGGLE_BIT names map between DM and XML?

**Decision**: The `toggleObject.name` attribute = the TOGGLE scope name. Each
`toggleBit.name` = the bit's string name (e.g. `ff1[2]`). The 0→1 and 1→0
transitions are identified by `CoverTypeT.TOGGLE01` and `CoverTypeT.TOGGLE10`
cover item types. Confirm with the existing `xml_reader.py` toggle reader code.

---

## 8. File Inventory After Full Implementation

**Modified files:**
- `src/ucis/xml/xml_writer.py` — add 5 new write methods; fix writtenBy/writtenTime; add ctx.warn
- `src/ucis/xml/xml_reader.py` — audit and complete toggle/block/branch/FSM/assertion readers
- `src/ucis/xml/db_format_if_xml.py` — update FormatCapabilities to reflect new capabilities
- `tests/conversion/test_xml_conversion.py` — remove xfails; add schema validation; add golden tests
- `tests/conversion/builders/ucis_builders.py` — add FSM and assertion builder/verifier pairs
- `README.md` — update format capability matrix

**New files:**
- `doc/xml_format.md` — format documentation
- `tests/conversion/fixtures/xml/*.xml` — golden test files (5-6 files)
