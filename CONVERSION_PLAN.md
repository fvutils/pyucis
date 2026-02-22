# PyUCIS Bi-Directional Conversion Plan

## Implementation Status (as of 2026-02-21) — ALL PHASES COMPLETE

**Tests: 384 passed, 4 xfailed (documented gaps), 0 failures**

| Phase | Item | Status |
|-------|------|--------|
| P1 | ConversionContext, ConversionError, ConversionListener | ✅ Done |
| P1 | FormatCapabilities registered for all 8 formats | ✅ Done |
| P1 | ucis_builders.py (11 builders + verifiers) | ✅ Done |
| P2 | XML decoupled from MemUCIS | ✅ Done |
| P3 | DbFormatIfLcov registered (write-only, warns via ctx) | ✅ Done |
| P3 | YamlWriter implemented | ✅ Done |
| P3 | CocotbYamlWriter, CocotbXmlWriter implemented | ✅ Done |
| P3 | AvlJsonWriter implemented | ✅ Done |
| P3 | VltCovWriter implemented | ✅ Done |
| P4 | ConversionContext wired into all writers | ✅ Done |
| P4 | cmd_convert --strict / --warn-summary flags | ✅ Done |
| P5 | All conversion test files (P5-1 through P5-10) | ✅ Done |
| P6 | README capability table | ✅ Done |
| P6 | Writer docstrings | ✅ Done |

Known xfail items (documented limitations, not regressions):
- XML write: statement/branch/toggle coverage not yet written (3 tests)
- cocotb-xml round-trip: writer format not readable by reader (1 test)

---

## Problem Statement

pyucis supports several coverage data formats: UCIS-XML, custom YAML, cocotb-coverage
(YAML and XML), AVL JSON, SQLite, Verilator (vltcov), and LCOV (output only). Currently:

1. **UCIS-XML is treated as a data model backend** (`XmlUCIS` extends `MemUCIS`). It must be
   refactored to be a pure import/export format, like cocotb and AVL.
2. **Conversion is one-directional for several formats** — cocotb, AVL, and vltcov have
   readers but no writers; LCOV has a writer (formatter) but no reader.
3. **There is no warning/error infrastructure** for unsupportable content during conversion.
4. **There is no progress notification infrastructure** — large databases can take seconds to
   convert with no feedback to the caller or UI.
5. **Test coverage is incomplete** — there are no parameterized UCIS-to-UCIS round-trip
   tests spanning Mem/SQLite/XML backend combinations, and format-specific conversion
   tests are sparse.

The goal is a comprehensive, symmetric, well-tested conversion framework where:
- Every format has a reader (`<Format> → UCIS`) and a writer (`UCIS → <Format>`)
- Writers emit `WARNING` for UCIS content the format cannot represent
- A `--strict` / `strict=True` mode turns those warnings into errors
- Progress is reported through a pluggable listener interface (supports rich TUI, logging, etc.)
- A test suite validates each feature in each direction and cross-backend round-trips

---

## Formats and Their Capabilities

### Format Capability Matrix

| UCIS Feature                  | XML | YAML | cocotb-YAML | cocotb-XML | AVL-JSON | SQLite | vltcov | LCOV |
|-------------------------------|-----|------|-------------|------------|----------|--------|--------|------|
| Covergroups / Coverinstances  | ✓   | ✓    | ✓ (in)      | ✓ (in)     | ✓ (in)   | ✓      | —      | —    |
| Coverpoints + bins            | ✓   | ✓    | ✓ (in)      | ✓ (in)     | ✓ (in)   | ✓      | —      | —    |
| Cross coverage                | ✓   | ✓    | ✓ (in)      | ✓ (in)     | —        | ✓      | —      | —    |
| Ignore / Illegal bins         | ✓   | ✓    | partial     | partial    | —        | ✓      | —      | —    |
| Statement coverage            | ✓   | —    | —           | —          | —        | ✓      | ✓ (in) | ✓    |
| Branch coverage               | ✓   | —    | —           | —          | —        | ✓      | ✓ (in) | ✓    |
| Expression / Condition cov.   | ✓   | —    | —           | —          | —        | ✓      | —      | —    |
| Toggle coverage               | ✓   | —    | —           | —          | —        | ✓      | ✓ (in) | —    |
| FSM coverage                  | ✓   | —    | —           | —          | —        | ✓      | —      | —    |
| Assertion (cover/assert)      | ✓   | —    | —           | —          | —        | ✓      | —      | —    |
| History nodes / test metadata | ✓   | ✓    | —           | —          | —        | ✓      | partial| —    |
| Design hierarchy (DU/Instance)| ✓   | ✓    | —           | —          | —        | ✓      | ✓      | —    |
| File handles / source info    | ✓   | ✓    | —           | —          | —        | ✓      | ✓      | ✓    |
| DB metadata (writtenBy, etc.) | ✓   | ✓    | —           | —          | —        | ✓      | —      | —    |
| Per-instance coverage         | ✓   | ✓    | —           | —          | —        | ✓      | —      | —    |

Legend: ✓ = full bidirectional, ✓ (in) = import only (currently), — = not representable

### Per-Format Unsupportable Content (documented limitations)

#### LCOV
- Does NOT support: covergroups, coverpoints, cross coverage, ignore/illegal bins,
  toggle coverage, FSM coverage, assertions, history nodes, design hierarchy
- Can represent: statement (line) coverage, branch coverage, function coverage
- Mapping: UCIS statement bins → LCOV `DA:` records; branch bins → `BRDA:` records

#### cocotb-coverage YAML / XML
- Does NOT support: code coverage (stmt, branch, expr, cond, toggle, FSM),
  assertions, design hierarchy (DU/instance scopes), history nodes, file handles,
  DB metadata, per-instance coverage, cross coverage with complex expressions,
  ignore/illegal bins (only normal bins)
- Can represent: covergroups, coverpoints with named bins and hit counts

#### AVL JSON
- Does NOT support: code coverage, assertions, design hierarchy, history nodes,
  file handles, DB metadata, cross coverage, ignore/illegal bins
- Can represent: covergroups, coverpoints with named bins and hit counts

#### Verilator vltcov
- Does NOT support: functional coverage (covergroups/points/cross), assertions,
  per-instance functional coverage, FSM coverage, history nodes, DB metadata
- Can represent: statement coverage, branch coverage, toggle coverage with
  design hierarchy (module/instance structure)

#### Custom YAML
- Does NOT support: expression coverage, condition coverage, FSM coverage,
  assertion coverage, block coverage, advanced metadata properties
- Can represent: covergroups, coverpoints, cross, statement, branch, toggle,
  design hierarchy, history nodes, file handles

#### UCIS-XML
- Full UCIS data model representation — nearly lossless
- Minor limitations: some advanced assertion properties, tool-specific extensions

---

## Architecture Changes

### 1. Decouple UCIS-XML from MemUCIS Data Model (was §1, now §3)

**Current state:** `XmlUCIS` extends `MemUCIS` — the XML file IS the data model.

**Required change:** XML becomes a pure import/export format like cocotb/AVL:
- `XmlReader.read(file) → UCIS` (reads XML, populates a Mem or SQLite DB)
- `XmlWriter.write(db, file)` (serializes any UCIS DB to XML)
- `XmlUCIS` class is removed or kept as a thin compatibility shim only

The `FormatIfDb.create()` for XML should return a `MemUCIS` (or SQLite) instance.
The `FormatIfDb.read()` for XML should read XML into a fresh in-memory DB.

### 2. Progress Notification — Listener Interface

Conversions can be slow (large SQLite databases, deep hierarchies). `ConversionContext`
exposes a pluggable listener so callers can drive any UI (rich progress bar, logging,
silent) without the converter knowing about the display layer.

#### ConversionListener Protocol

```python
# ucis/conversion/conversion_listener.py

from typing import Optional

class ConversionListener:
    """
    Protocol for receiving conversion progress events.

    All methods have default no-op implementations so callers only override
    what they care about. Thread-safety is the caller's responsibility.
    """

    def on_phase_start(self, phase: str, total: Optional[int] = None):
        """
        A named conversion phase is starting.

        Args:
            phase:  Human-readable phase name, e.g. "Reading covergroups",
                    "Writing toggle scopes".
            total:  Expected number of items in this phase, or None if unknown.
        """

    def on_item(self, description: Optional[str] = None, advance: int = 1):
        """
        One or more items in the current phase have been processed.

        Args:
            description:  Optional label for the current item (e.g. scope name).
            advance:      Number of items completed since the last call (default 1).
        """

    def on_phase_end(self):
        """The current phase has completed."""

    def on_warning(self, message: str):
        """
        A lossless-conversion warning was emitted.

        Called in addition to (not instead of) appending to ctx.warnings.
        Allows the UI to show warnings inline with the progress display.
        """

    def on_complete(self, warnings: int, items_converted: int):
        """
        The entire conversion is done.

        Args:
            warnings:         Total number of warnings emitted.
            items_converted:  Total number of UCIS items processed.
        """
```

#### ConversionContext integration

`ConversionContext` grows a `listener` field and thin delegation methods so
converters never call the listener directly — they always go through the context:

```python
class ConversionContext:
    strict: bool = False
    warnings: List[str] = []
    _listener: ConversionListener = ConversionListener()   # no-op default
    _items_converted: int = 0

    def __init__(self, strict=False, listener=None):
        self.strict = strict
        self.warnings = []
        self._listener = listener or ConversionListener()
        self._items_converted = 0

    # --- warning helpers (existing) ---
    def warn(self, message: str):
        self.warnings.append(message)
        self._listener.on_warning(message)
        if self.strict:
            raise ConversionError(message)

    # --- progress helpers (new) ---
    def phase(self, name: str, total: Optional[int] = None):
        """Context manager for a named phase."""
        return _PhaseContext(self, name, total)

    def item(self, description=None, advance=1):
        self._items_converted += advance
        self._listener.on_item(description, advance)

    def complete(self):
        self._listener.on_complete(len(self.warnings), self._items_converted)

    def summarize(self) -> str: ...
```

Converters use it like this:

```python
def write(self, db: UCIS, file: str, ctx: ConversionContext = None):
    ctx = ctx or ConversionContext()
    covergroups = list(db.scopes(ScopeTypeT.COVERGROUP))
    with ctx.phase("Writing covergroups", total=len(covergroups)):
        for cg in covergroups:
            self._write_covergroup(cg, ctx)
            ctx.item(cg.getScopeName())
    ctx.complete()
```

#### Provided listener implementations

Three concrete listeners ship with pyucis, each in its own module:

| Class | Module | Behaviour |
|-------|--------|-----------|
| `ConversionListener` | `conversion_listener.py` | No-op base / default |
| `LoggingConversionListener` | `conversion_listener.py` | Emits Python `logging` calls at INFO/WARNING level |
| `RichConversionListener` | `conversion_listener_rich.py` | Drives a `rich.progress.Progress` bar; file is only imported if `rich` is installed — no hard dependency |

`RichConversionListener` example behaviour:
```
Converting  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%  Writing covergroups [14/14]
  ⚠ cocotb-yaml does not support cross coverage — 2 cross(es) skipped
Done. 14 items converted, 1 warning.
```

`LoggingConversionListener` example:
```
INFO  conversion: phase=Reading covergroups total=14
INFO  conversion: item=cg_top [1/14]
WARNING conversion: cocotb-yaml does not support cross coverage — 2 cross(es) skipped
INFO  conversion: complete items=14 warnings=1
```

#### _PhaseContext helper

```python
class _PhaseContext:
    """Context manager that brackets a conversion phase."""
    def __enter__(self):
        self._ctx._listener.on_phase_start(self._name, self._total)
        return self
    def __exit__(self, *_):
        self._ctx._listener.on_phase_end()
```

#### cmd_convert.py integration

```
--progress {none,log,rich}   Show conversion progress (default: none)
```

When `--progress rich` is passed, `RichConversionListener` is constructed and
passed into `ConversionContext`. When `--progress log` is passed,
`LoggingConversionListener` is used. This keeps the CLI pleasant without
coupling the conversion library to any display toolkit.

### 3. Conversion Warning / Strict Mode Infrastructure

New module: `ucis/conversion/conversion_context.py`

```python
class ConversionContext:
    strict: bool = False
    warnings: List[str] = []
    
    def warn(self, message: str):
        """Emit warning or raise if strict mode."""
        ...
    
    def summarize(self) -> str:
        """Return summary of all warnings."""
        ...
```

Each format writer accepts an optional `ConversionContext`. When a UCIS feature
cannot be represented, it calls `ctx.warn(msg)` with a descriptive message:

```
WARNING: lcov does not support covergroup coverage — 3 covergroup(s) skipped
WARNING: cocotb-yaml does not support cross coverage — 2 cross(es) skipped
WARNING: avl-json does not support history nodes — 1 history node skipped
```

In strict mode, these become `ConversionError` exceptions.

### 4. Complete Missing Writers

Each read-only format needs a writer added:

| Format | Current | Required |
|--------|---------|----------|
| cocotb-YAML | reader only | add `CocotbYamlWriter` |
| cocotb-XML  | reader only | add `CocotbXmlWriter` |
| AVL JSON    | reader only | add `AvlJsonWriter` |
| vltcov      | reader only | add `VltCovWriter` |
| LCOV        | formatter only (non-standard) | add proper `LcovReader` + `LcovWriter` via `FormatIfDb` |

LCOV is currently a formatter (`formatters/format_lcov.py`). It must be promoted
to a first-class registered DB format with a reader that parses `.info` files.

### 5. Format Registry Updates

All formats registered in `FormatRgy._init_rgy()` must implement both `read()` and
`write()` in their `FormatIfDb` subclass, or explicitly raise `NotImplementedError`
with a clear message. Add a `capabilities` property to `FormatDescDb`:

```python
@dataclass
class FormatCapabilities:
    can_read: bool
    can_write: bool
    functional_coverage: bool
    code_coverage: bool
    assertions: bool
    history_nodes: bool
    strict_mode: bool
    lossless: bool  # True only for XML and SQLite
```

### 6. `cmd_convert.py` Enhancement

- Add `--strict` flag that passes `ConversionContext(strict=True)` to writers
- Add `--warn-summary` flag to print a summary of all conversion warnings at end
- Add `--progress {none,log,rich}` flag; default `none`; `rich` uses `RichConversionListener`, `log` uses `LoggingConversionListener`
- Auto-detect input format if not specified (already partially implemented)
- Replace the SQLite-special-case with a generic path through `FormatIfDb`

---

## UCIS Data Model Feature Inventory

For test parameterization, each feature is a distinct test axis:

### Functional Coverage Features
- FC-1: Single covergroup, single coverpoint, normal bins, hit counts
- FC-2: Multiple covergroups in one database
- FC-3: Covergroup with min/max/weight on bins
- FC-4: Cross coverage (2-way, 3-way)
- FC-5: Ignore bins
- FC-6: Illegal bins
- FC-7: Default bin
- FC-8: Per-instance coverage (multiple coverinstances of same covergroup type)
- FC-9: Transition bins
- FC-10: Wildcard bins

### Code Coverage Features
- CC-1: Statement coverage (with source file + line number)
- CC-2: Branch coverage (true/false arms)
- CC-3: Expression coverage
- CC-4: Condition coverage
- CC-5: Toggle coverage (0→1 and 1→0 bins)
- CC-6: Block coverage
- CC-7: FSM state coverage
- CC-8: FSM transition coverage

### Assertion Features
- AS-1: SVA cover property (pass count)
- AS-2: SVA assert property (fail/pass counts)

### Structural/Metadata Features
- SM-1: Design unit (DU_MODULE) + instance hierarchy
- SM-2: Nested instance hierarchy (multiple levels)
- SM-3: File handles and source info on scopes
- SM-4: History node (single test)
- SM-5: Multiple history nodes (merged from multiple tests)
- SM-6: Test data (name, status, date, seed)
- SM-7: Database metadata (writtenBy, writtenTime, pathSeparator)
- SM-8: Multiple top-level instances of same DU

---

## Test Suite Design

### Directory Structure

```
tests/
  conversion/
    __init__.py
    conftest.py               # DB factory fixtures, format fixtures
    fixtures/                 # Golden input files for each format
      xml/
      yaml/
      cocotb_yaml/
      cocotb_xml/
      avl_json/
      vltcov/
      lcov/
    
    test_ucis_to_ucis.py     # Parameterized UCIS→UCIS round-trip tests
    test_xml_conversion.py   # XML ↔ UCIS tests
    test_yaml_conversion.py  # YAML ↔ UCIS tests
    test_cocotb_conversion.py # cocotb ↔ UCIS tests
    test_avl_conversion.py   # AVL ↔ UCIS tests
    test_vltcov_conversion.py # vltcov ↔ UCIS tests
    test_lcov_conversion.py  # LCOV ↔ UCIS tests
    test_strict_mode.py      # Warning/strict-mode behavior tests
    test_format_capabilities.py # Format capability registry tests
    builders/
      __init__.py
      ucis_builders.py       # Functions that build each FC/CC/AS/SM feature
```

### conftest.py — DB Backend Fixtures

```python
import pytest
from ucis.mem import MemFactory
from ucis.sqlite import SqliteUCIS

@pytest.fixture(params=["mem", "sqlite"])
def empty_db(request, tmp_path):
    if request.param == "mem":
        return MemFactory.create()
    else:
        return SqliteUCIS(str(tmp_path / "test.db"))

@pytest.fixture(params=["mem", "sqlite"])
def dst_db(request, tmp_path):
    if request.param == "mem":
        return MemFactory.create()
    else:
        return SqliteUCIS(str(tmp_path / "dst.db"))
```

### ucis_builders.py — Feature Builder Functions

Each builder function creates a UCIS DB containing exactly one feature:

```python
def build_fc1_single_covergroup(db: UCIS) -> UCIS:
    """Build DB with one covergroup, one coverpoint, three bins."""
    ...

def build_fc4_cross_coverage(db: UCIS) -> UCIS:
    """Build DB with two coverpoints and a 2-way cross."""
    ...

def build_cc1_statement_coverage(db: UCIS) -> UCIS:
    """Build DB with one module/instance having statement bins."""
    ...
# etc. for all FC-*, CC-*, AS-*, SM-* features
```

### test_ucis_to_ucis.py — Parameterized Round-Trip Tests

```python
import pytest
from .builders.ucis_builders import ALL_BUILDERS
from .conftest import db_backend_combos

@pytest.mark.parametrize("builder", ALL_BUILDERS, ids=lambda b: b.__name__)
@pytest.mark.parametrize("src_backend,dst_backend", [
    ("mem",    "mem"),
    ("sqlite", "sqlite"),
    ("sqlite", "mem"),
    ("mem",    "sqlite"),
], ids=["mem-mem", "sqlite-sqlite", "sqlite-mem", "mem-sqlite"])
def test_ucis_roundtrip(builder, src_backend, dst_backend, tmp_path):
    """
    Build a UCIS DB with a specific feature in src_backend, copy to
    dst_backend using DbMerger, and verify all data is preserved.
    """
    src_db = make_db(src_backend, tmp_path / "src")
    builder(src_db)
    
    dst_db = make_db(dst_backend, tmp_path / "dst")
    merger = DbMerger()
    merger.merge(dst_db, [src_db])
    
    verify_builder_content(builder, dst_db)
    src_db.close()
    dst_db.close()
```

The parameterization produces 4 × N test cases (N = number of feature builders).
The mem/mem case validates the builder + verifier. The sqlite/sqlite case validates
the SQLite implementation completeness. The cross-backend cases validate that the
data model API is symmetric across implementations.

### test_xml_conversion.py — XML ↔ UCIS

```python
@pytest.mark.parametrize("builder", ALL_BUILDERS, ids=lambda b: b.__name__)
def test_ucis_to_xml(builder, tmp_path):
    """Write UCIS feature to XML file, verify XML is valid."""
    db = MemFactory.create()
    builder(db)
    db.write(str(tmp_path / "out.xml"))
    validate_ucis_xml(str(tmp_path / "out.xml"))

@pytest.mark.parametrize("builder", BUILDERS_XML_SUPPORTS, ids=lambda b: b.__name__)
def test_xml_roundtrip(builder, tmp_path):
    """Build → XML → read back → verify content preserved."""
    db1 = MemFactory.create()
    builder(db1)
    db1.write(str(tmp_path / "out.xml"))
    
    db2 = XmlReader().read(str(tmp_path / "out.xml"))
    verify_builder_content(builder, db2)

@pytest.mark.parametrize("fixture_file,expected_builder", XML_GOLDEN_FILES)
def test_xml_read_golden(fixture_file, expected_builder, tmp_path):
    """Read a known-good XML file and verify content."""
    db = XmlReader().read(fixture_file)
    verify_builder_content(expected_builder, db)
```

Pattern repeats for every other format with appropriate `BUILDERS_<FORMAT>_SUPPORTS`
subsets reflecting the capability matrix above.

### test_strict_mode.py

```python
@pytest.mark.parametrize("builder,format_name,expected_warnings", [
    (build_fc1_single_covergroup, "lcov",    ["lcov does not support covergroup"]),
    (build_cc1_statement_coverage,"cocotb-yaml", ["cocotb-yaml does not support code coverage"]),
    (build_fc4_cross_coverage,    "avl-json", ["avl-json does not support cross coverage"]),
    # ... etc.
])
def test_conversion_warning(builder, format_name, expected_warnings, tmp_path):
    """Verify that writing unsupported content emits correct warnings."""
    ctx = ConversionContext(strict=False)
    db = MemFactory.create()
    builder(db)
    write_format(db, format_name, tmp_path / "out", ctx=ctx)
    for warn in expected_warnings:
        assert any(warn in w for w in ctx.warnings)

@pytest.mark.parametrize("builder,format_name", [
    (build_fc1_single_covergroup, "lcov"),
    ...
])
def test_strict_mode_raises(builder, format_name, tmp_path):
    """Verify that strict mode raises ConversionError on unsupported content."""
    ctx = ConversionContext(strict=True)
    db = MemFactory.create()
    builder(db)
    with pytest.raises(ConversionError):
        write_format(db, format_name, tmp_path / "out", ctx=ctx)
```

### Coverage of Format × Feature Matrix

For each non-lossless format, tests must explicitly verify:
1. **Supported features**: data is preserved after round-trip
2. **Unsupported features**: warning is emitted (default) / error is raised (strict)
3. **Partial support**: partial data is preserved, with warning for lost data

---

## Implementation Phases

### Phase 1 — Infrastructure (no user-visible behavior change)
- P1-1: Create `ConversionListener` base class (no-op) and `LoggingConversionListener` (`ucis/conversion/conversion_listener.py`)
- P1-2: Create `RichConversionListener` (`ucis/conversion/conversion_listener_rich.py`; guards `import rich` so it is not a hard dependency)
- P1-3: Create `ConversionContext` with `strict`, `warnings`, `listener`, `phase()`, `item()`, `complete()`, `warn()` (`ucis/conversion/conversion_context.py`)
- P1-4: Create `ConversionError` exception (`ucis/conversion/__init__.py`)
- P1-5: Create `FormatCapabilities` dataclass and add to `FormatDescDb`
- P1-6: Create `ucis_builders.py` with all feature builder functions
- P1-7: Create `tests/conversion/conftest.py` with DB backend fixtures and `write_format(db, fmt, path, ctx)` helper
- P1-8: Implement verify functions that mirror each builder

### Phase 2 — Decouple UCIS-XML from MemUCIS
- P2-1: Refactor `XmlUCIS` — make `XmlReader.read()` return a `MemUCIS` instance
- P2-2: Update `DbFormatIfXml.create()` to return `MemUCIS`
- P2-3: Update `DbFormatIfXml.read()` to call `XmlReader` into fresh `MemUCIS`
- P2-4: Keep `XmlUCIS` as deprecated alias for one release
- P2-5: Update all existing XML-related tests to pass

### Phase 3 — Add Missing Writers
- P3-1: `CocotbYamlWriter` (covergroups/points/bins only, warn on other content)
- P3-2: `CocotbXmlWriter` (same scope as CocotbYamlWriter)
- P3-3: `AvlJsonWriter` (covergroups/points/bins only, warn on other content)
- P3-4: `VltCovWriter` (stmt/branch/toggle + design hierarchy, warn on func cov)
- P3-5: `LcovReader` — parse `.info` files into UCIS (stmt + branch + function → UCIS)
- P3-6: Promote LCOV to first-class `FormatIfDb` registration

### Phase 4 — Wire ConversionContext into All Writers
- P4-1: `XmlWriter` — add `ctx` parameter, warn on unsupported tool extensions
- P4-2: `YamlWriter` — warn on code coverage, assertions, FSM
- P4-3: `CocotbYamlWriter` / `CocotbXmlWriter` — warn on code cov, assertions, hierarchy
- P4-4: `AvlJsonWriter` — warn on code cov, assertions, cross, hierarchy
- P4-5: `VltCovWriter` — warn on functional coverage, assertions
- P4-6: `LcovWriter` — warn on functional coverage, toggle, FSM, assertions
- P4-7: `cmd_convert.py` — add `--strict`, `--warn-summary`, and `--progress {none,log,rich}` flags

### Phase 5 — Test Suite
- P5-1: `test_ucis_to_ucis.py` with all backend combos × all builders
- P5-2: `test_xml_conversion.py`
- P5-3: `test_yaml_conversion.py`
- P5-4: `test_cocotb_conversion.py`
- P5-5: `test_avl_conversion.py`
- P5-6: `test_vltcov_conversion.py`
- P5-7: `test_lcov_conversion.py`
- P5-8: `test_strict_mode.py`
- P5-9: `test_format_capabilities.py`
- P5-10: `test_conversion_listener.py` — test `LoggingConversionListener` captures phases/items/warnings; test `RichConversionListener` instantiation when `rich` available; test no-op base listener; test that `ConversionContext.phase()` / `.item()` / `.complete()` invoke listener correctly

### Phase 6 — Documentation
- P6-1: Update README with format capability table
- P6-2: Add docstrings to all new writer classes documenting limitations
- P6-3: Add `--strict`, `--progress` flags to CLI help text and README

---

## Key Design Decisions

### Q: Why use a listener rather than a callback or asyncio event?
**Decision**: A listener object (class with overridable methods) is the right choice
because: (a) it groups related events (start/item/end/warning/complete) without
requiring callers to wire up five separate callbacks; (b) it is trivially subclassable
for test spies and real implementations; (c) it avoids imposing an async execution
model on synchronous converters. If async support is needed later, a thin adapter
wrapping the listener in an asyncio queue can be added without changing converter code.

### Q: Should `rich` be a required or optional dependency?
**Decision**: Optional. `RichConversionListener` lives in its own module
(`conversion_listener_rich.py`) and does a guarded `import rich` at class
instantiation time. If `rich` is not installed and the user passes `--progress rich`,
a clear `ImportError` with install instructions is raised. This keeps the core
library free of heavy UI dependencies.

### Q: How are phases reported for formats with unknown item counts?
**Decision**: `on_phase_start(phase, total=None)` allows `total=None`. The
`RichConversionListener` renders an indeterminate spinner in that case. After the
phase completes, `on_phase_end()` closes it. Converters should always pass a total
when they can pre-count items (e.g., `len(list(db.scopes(COVERGROUP)))`) and pass
`None` only when a pre-count would require a full traversal.

### Q: Should UCIS-XML round-trip through Mem or SQLite internally?
**Decision**: Mem. XML is a complete lossless representation, so Mem is a natural
intermediate. The `DbFormatIfXml.read()` reads XML into `MemUCIS`; callers who
want SQLite persistence can convert afterwards.

### Q: How granular should ConversionContext warnings be?
**Decision**: One warning per distinct unsupported feature type, not per instance.
e.g., "lcov: 3 covergroup(s) skipped" rather than one warning per covergroup.
This keeps output clean for large databases.

### Q: Should vltcov writer generate `.dat` files or something else?
**Decision**: `.dat` files using the Verilator coverage data format. The writer
reconstructs the flat key=value format from UCIS hierarchy + code coverage bins.

### Q: What is the LCOV reader mapping from LCOV → UCIS?
**Decision**:
- `SF:` file → UCIS file handle + DU_MODULE instance hierarchy
- `DA:` line,count → statement bin under BLOCK scope with source info
- `BRDA:` line,block,branch,count → branch bin under BRANCH scope
- `FN:` / `FNDA:` function → sub-scope under the module instance
- `TN:` test name → history node with TestData

### Q: How are the UCIS-to-UCIS verify functions implemented?
**Decision**: Each builder function has a corresponding `verify_<name>(db)` function
that asserts the exact expected structure. Both live in `builders/ucis_builders.py`.
This keeps builder and verifier in sync and makes test failures easy to diagnose.
