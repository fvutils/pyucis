# Test History & Testplan Implementation Plan

Based on `TEST_HISTORY_DESIGN.md`.

---

## Scope

This plan covers the full implementation, testing, and documentation of:

1. **Binary history store** (Parts 1–6): efficient per-test-run records inside the NCDB ZIP
2. **Coverage-per-test fixes** (Part 4): stable `run_id`, contrib data loss bug fix
3. **Testplan embedding** (Parts 9–10): `testplan.json` ZIP member, closure computation
4. **Reports** (Parts 9.4, 11): regression summary, stage gate, delta, trend, CI export
5. **Competitive parity additions** (Part 11.3): waivers, contribution ranking, safety traceability

---

## Phase 1 — Binary History Store

### 1.1 New module: `src/ucis/ncdb/test_registry.py`

Implements `TestRegistry` class:

- **Struct layout** (`magic=0x54535452`, `version=1`, `next_run_id`, `num_names`, `num_seeds`, offset tables, two string heaps)
- `assign_run_id() -> int` — atomic increment of `next_run_id`
- `lookup_name_id(name: str) -> int` — binary search on sorted name heap; assign if absent
- `lookup_seed_id(seed: str) -> int` — same for seed heap
- `name_for_id(name_id: int) -> str` — O(1) offset-table access
- `seed_for_id(seed_id: int) -> str`
- `serialize() -> bytes` / `@classmethod deserialize(data: bytes) -> TestRegistry`

Invariants:
- Name heap kept sorted; insertion preserves sort order (re-builds heap on insert)
- Seeds stored as decimal string for integers, verbatim for complex strings
- `next_run_id` never decreases; survives ZIP rewrite and merge

### 1.2 New module: `src/ucis/ncdb/test_stats.py`

Implements `TestStatsTable` with one 64-byte `TestStatsEntry` per test (indexed by `name_id`):

Fields per entry (matching design §3.4):
`total_runs`, `pass_count`, `fail_count`, `error_count`, `first_ts`, `last_ts`,
`last_green_ts`, `transition_count`, `streak` (i16), `last_status`, `_pad`,
`flake_score` (f32), `fail_rate` (f32), `mean_cpu_time` (f32), `m2_cpu_time` (f32),
`cusum_value` (f32), `cusum_ref_mean` (f32), `grade_score` (f32), `total_seeds_seen` (u16),
`_reserved[6]`

Methods:
- `update(name_id, status, ts, cpu_time=None)` — Welford online update + CUSUM step (k=0.5, h=4.0)
- `get(name_id) -> TestStatsEntry`
- `top_flaky(n=20) -> list[TestStatsEntry]` — sort by `flake_score DESC`
- `top_failing(n=20, flake_threshold=0.1) -> list[TestStatsEntry]`
- `serialize() -> bytes` / `@classmethod deserialize(data: bytes, num_entries: int) -> TestStatsTable`

CUSUM update rule (on each run):
```
x = 1.0 if FAIL else 0.0
S = max(0, S + x - (cusum_ref_mean + 0.5))
if S > 4.0: record change-point, reset S = 0
```

### 1.3 New module: `src/ucis/ncdb/history_buckets.py`

Implements `HistoryBucket` for reading and writing `history/NNNNNN.bin` files.

Write path:
- `BucketWriter` accumulates records in memory, sorted by `(name_id, ts)`
- `seal() -> bytes` — produce compressed bucket bytes
- Sealed once the calendar day rolls over or record count reaches 10,000 (fixed threshold)

Read path:
- `BucketReader(data: bytes)` — decompress and parse header, name index, seed dict, columns
- `records_for_name(name_id: int) -> list[BucketRecord]` — binary search name index → O(log N)
- `all_records() -> Iterable[BucketRecord]`

`BucketRecord` fields: `name_id`, `seed_idx` (mapped to `seed_id` via local dict), `ts`, `status`, `flags`

`status_flags` byte layout:
- bits `[7:4]`: status (0=OK, 1=FAIL, 2=ERROR, 3=FATAL, 4=COMPILE)
- bits `[3:0]`: flags (bit0=seed_is_hash, bit1=is_rerun, bit2=has_coverage, bit3=was_squashed)

Compression tiering:
- Current-day (mutable) bucket: `ZIP_DEFLATE, level=1`
- Sealed (past-day, immutable) buckets: `ZIP_LZMA` if `liblzma` is available, else `ZIP_DEFLATE, level=9` (automatic fallback — no error raised)
- At close: sealed buckets are copied verbatim (no re-decompression) — critical for write performance

Varint encoding for `ts_deltas`: use existing `src/ucis/ncdb/varint.py`

### 1.4 New module: `src/ucis/ncdb/bucket_index.py`

Implements `BucketIndex` for `history/bucket_index.bin` (magic `0x42494458`).

One 24-byte entry per bucket:
`bucket_seq (u32)`, `ts_start (u32)`, `ts_end (u32)`, `num_records (u32)`,
`fail_count (u32)`, `min_name_id (u32)`, `max_name_id (u32)`

Methods:
- `add_bucket(seq, ts_start, ts_end, num_records, fail_count, min_name_id, max_name_id)`
- `buckets_in_range(ts_from, ts_to) -> list[BucketIndexEntry]`
- `buckets_for_name(name_id, ts_from=None, ts_to=None) -> list[BucketIndexEntry]`
  — filters by `min_name_id ≤ name_id ≤ max_name_id`
- `pass_rate_series() -> list[(ts_start, pass_rate)]` — from `fail_count`/`num_records` per bucket
- `serialize() -> bytes` / `@classmethod deserialize(data: bytes) -> BucketIndex`

### 1.5 New module: `src/ucis/ncdb/contrib_index.py`

Implements `ContribIndex` for `contrib_index.bin` (magic `0x43494458`).

Header: `magic`, `version`, `merge_policy (u8)`, `squash_watermark (u32)`, `num_active (u32)`

One 8-byte entry per active contrib: `run_id (u32)`, `name_id (u16)`, `status (u8)`, `flags (u8)`

Methods:
- `add_entry(run_id, name_id, status, flags)`
- `passing_run_ids(policy=PASS_ONLY) -> list[int]`
  — applies merge policy filter (all / pass_only / pass_first_attempt / strict)
- `set_squash_watermark(run_id: int)`
- `remove_entries_up_to(run_id: int)` — after squash
- `serialize() -> bytes` / `@classmethod deserialize(data: bytes) -> ContribIndex`

Merge policy constants:
```python
POLICY_ALL = 0
POLICY_PASS_ONLY = 1
POLICY_EXCLUDE_ERROR_RERUN = 2
POLICY_STRICT = 3
```

### 1.6 New module: `src/ucis/ncdb/squash_log.py`

Implements `SquashLog` for `squash_log.bin` (append-only, 28 bytes/entry).

Entry fields: `ts (u32)`, `policy (u8)`, `_pad[3]`, `from_run (u32)`, `to_run (u32)`,
`num_runs (u32)`, `pass_runs (u32)`

Methods:
- `append(ts, policy, from_run, to_run, num_runs, pass_runs)`
- `entries() -> list[SquashLogEntry]`
- `serialize() -> bytes` / `@classmethod deserialize(data: bytes) -> SquashLog`

### 1.7 Modifications to existing files

#### `src/ucis/ncdb/constants.py`
- Add `NCDB_VERSION = "2.0"` (bump from `"1.0"`)
- Add new member name constants:
  ```python
  MEMBER_TEST_REGISTRY   = "test_registry.bin"
  MEMBER_TEST_STATS      = "test_stats.bin"
  MEMBER_BUCKET_INDEX    = "history/bucket_index.bin"
  MEMBER_CONTRIB_INDEX   = "contrib_index.bin"
  MEMBER_SQUASH_LOG      = "squash_log.bin"
  MEMBER_TESTPLAN        = "testplan.json"
  MEMBER_WAIVERS         = "waivers.json"
  ```
- Add status constants:
  ```python
  HIST_STATUS_OK      = 0
  HIST_STATUS_FAIL    = 1
  HIST_STATUS_ERROR   = 2
  HIST_STATUS_FATAL   = 3
  HIST_STATUS_COMPILE = 4
  ```

#### `src/ucis/ncdb/manifest.py`
- Add `history_format: str` field — `"v1"` (JSON only) or `"v2"` (binary + JSON for MERGE nodes)
- Backward-compat: default to `"v1"` when reading old manifests without this field
- Auto-upgrade to `"v2"` the first time `add_test_run()` is called on any database; no explicit opt-in required

#### `src/ucis/ncdb/ncdb_ucis.py` (`NcdbUCIS`)
- Add lazy-load fields and public API for binary history:
  ```python
  _test_registry: Optional[TestRegistry]
  _test_stats: Optional[TestStatsTable]
  _bucket_index: Optional[BucketIndex]
  _contrib_index: Optional[ContribIndex]
  _squash_log: Optional[SquashLog]
  _history_v2_dirty: bool
  ```
- New public methods:
  - `add_test_run(name, seed, status, ts=None, cpu_time=None, has_coverage=False, is_rerun=False) -> int`
    — assigns `run_id`, updates registry, stats, current bucket, optionally adds contrib entry
  - `query_test_history(name, ts_from=None, ts_to=None) -> list[BucketRecord]`
    — uses registry → bucket index → targeted bucket reads
  - `get_test_stats(name) -> Optional[TestStatsEntry]`
  - `top_flaky_tests(n=20) -> list[TestStatsEntry]`
  - `top_failing_tests(n=20) -> list[TestStatsEntry]`
  - `squash_coverage(policy=POLICY_PASS_ONLY)` — implements §4.5 squash operation
- Backward-compat: if `manifest.history_format == "v1"`, only `history.json` is used
  for TEST nodes (existing behavior unchanged)

#### `src/ucis/ncdb/ncdb_writer.py`
- Write all new binary members when `history_format == "v2"`:
  - `test_registry.bin`, `test_stats.bin`, `contrib_index.bin`, `squash_log.bin`
  - `history/bucket_index.bin`
  - Current-day bucket with `ZIP_DEFLATE, level=1`
  - Sealed buckets: copy verbatim compressed bytes (no re-decompression)
- Write `testplan.json` if set
- Write `waivers.json` if set
- Write `manifest.json` with updated `history_format` and `NCDB_VERSION`

#### `src/ucis/ncdb/ncdb_reader.py`
- Read `history_format` from manifest; if `"v2"`, load binary members
- Fall back to `history.json` for MERGE nodes in all versions
- Attach `_testplan` and `_waivers` attributes to returned db object if present

#### `src/ucis/ncdb/ncdb_merger.py` — **Critical bug fix**

Fix `_merge_same_schema()` contrib data loss:

1. **Assign `run_id` offsets** so each source's run IDs are disjoint:
   ```python
   offset_B = max(run_id_in_A) + 1
   offset_C = max(run_id_in_B) + 1
   ```
2. **Copy and rename contrib files**: `contrib/{src_run_id}.bin` → `contrib/{src_run_id + offset}.bin`
3. **Merge `contrib_index.bin` entries** from all sources (adjust `run_id`, re-sort)
4. **Merge `test_registry.bin`** — unify name_ids across sources (remap as needed)
5. **Merge `test_stats.bin`** — sum counts, recompute derived fields
6. **Merge bucket files** — copy all sealed buckets, reconcile name_ids if registries differed
7. **Merge `bucket_index.bin`** — concatenate entries, re-sort by `ts_start`
8. **Append `squash_log.bin`** entries from all sources (no run_id adjustment needed)
9. **Sum `counts.bin`** arrays for the merged output (existing behavior, kept)

Also add `_merge_testplans(sources) -> Optional[bytes]` implementing §10.8 strategy.

---

## Phase 2 — Testplan Embedding

### 2.1 New module: `src/ucis/ncdb/testplan.py`

Implements the data model (exactly as specified in §10.2):

- `CovergroupEntry(name, desc)`
- `Testpoint(name, stage, desc, tests, tags, na, source_template)`
  - Optional `requirements: list[RequirementLink]` field for ALM traceability (§11.3.6)
- `RequirementLink(system, project, item_id, url)`
- `Testplan(format_version, source_file, import_timestamp, testpoints, covergroups)`
  - Lazy indices: `_tp_by_name`, `_tp_by_test` (built once on first query)
  - `getTestpoint(name)`, `testpointForTest(test_name)` (3-strategy match: exact / seed-strip / wildcard)
  - `testpointsForStage(stage)`, `stages()`
  - `to_dict()`, `serialize() -> bytes`, `from_dict()`, `from_bytes()`, `load(path)`, `save(path)`
- Module-level helpers: `get_testplan(db)`, `set_testplan(db, tp)`

### 2.2 New module: `src/ucis/ncdb/testplan_closure.py`

Closure computation (§10.9) and covergroup joining (§10.10):

- `TPStatus` enum: `CLOSED`, `PARTIAL`, `FAILING`, `NOT_RUN`, `NA`, `UNIMPLEMENTED`
- `TestpointResult(testpoint, status, matched_tests, pass_count, fail_count)`
- `compute_closure(testplan, db, waivers=None) -> list[TestpointResult]`
  - Optional `waivers` argument filters waived bins from coverage percentage
- `stage_gate_status(results, stage, testplan, require_flake_score_below=None, require_coverage_pct=None) -> dict`
  - When `require_flake_score_below` is set, gate fails if covering tests have `flake_score` above threshold
- `find_covergroup_scopes(db, cg_name) -> list`
- `build_covergroup_index(db) -> dict[str, list]`

Competitive parity additions (§11.3.1, §11.3.2):
- `compute_contribution(db) -> list[TestContribution]`
  — iterates `contrib/*.bin`, computes unique bins per test; returns ranked list
- `compute_minimum_test_set(db, target_coverage=0.95) -> MinimumTestSet`
  — greedy set-cover approximation over contrib vectors; returns included/excluded test lists + CPU savings estimate

### 2.3 New module: `src/ucis/ncdb/testplan_hjson.py`

OpenTitan Hjson import (§10.11):

- `import_hjson(hjson_path, substitutions=None) -> Testplan`
  — parses Hjson, expands `{key}` wildcards (cartesian product for list values), handles `tests: ["N/A"]`
- `_expand_tests(test_list, subs) -> list[str]`
- `_expand_template(template, subs) -> list[str]`

Falls back to `json` if `hjson` package is not installed (handles JSON-subset .hjson files).
`hjson` is added as a regular (non-optional) dependency in `setup.py` and `ivpm.yaml`
(both `default` and `default-dev` dependency groups).

### 2.4 NcdbUCIS testplan API (§10.4)

Add to `NcdbUCIS`:
```python
_loaded_testplan: bool
_testplan: Optional[Testplan]
_testplan_dirty: bool

def getTestplan() -> Optional[Testplan]
def setTestplan(tp: Testplan) -> None
def _ensure_testplan() -> None
```

### 2.5 New module: `src/ucis/ncdb/waivers.py` (§11.3.3)

- `Waiver(id, scope_pattern, bin_pattern, rationale, approver, approved_at, expires_at, status)`
- `WaiverSet.load(path_or_bytes)`, `WaiverSet.save(path)`, `WaiverSet.matches_scope(scope_path, bin_name)`
- `NcdbUCIS.getWaivers()` / `setWaivers(ws)` analogous to testplan
- `WaiverSet.matches_scope()` performs pattern matching only; expiry enforcement is the caller's responsibility

---

## Phase 3 — Reports

All report functions live in a new module `src/ucis/ncdb/reports.py` (or split into
`testplan_reports.py` for testplan-oriented reports and `history_reports.py` for trend reports)
unless otherwise noted.

**Output convention**: every report function returns a structured dataclass (e.g.
`ClosureSummary`, `StagGateResult`) AND provides a companion `format_*(result) -> str`
function that renders the dataclass to human-readable text. A `to_json()` method on each
result dataclass enables machine-readable output as a first step. CLI commands call the
formatter; tests assert against the structured data.

### P0 Reports (essential for v1)

| ID | Function | Inputs | Output |
|----|----------|--------|--------|
| A  | `report_testpoint_closure(results)` | `list[TestpointResult]` | formatted table + stage roll-up |
| B  | `report_stage_gate(results, stage, testplan)` | as above | go/no-go summary with critical path |
| C  | `report_coverage_per_testpoint(results, db, testplan)` | testplan + scopes | testpoint × covergroup × pct table |
| D  | `report_regression_delta(results_new, results_old)` | two closure result lists | newly-closed, newly-failing, coverage delta |

### P1 Reports

| ID | Function | Inputs | Output |
|----|----------|--------|--------|
| E  | `report_stage_progression(db, testplan)` | merged NCDB with history | stage closure % over time (ASCII art or data) |
| F  | `report_testpoint_reliability(results, db)` | closure results + test_stats | flake score per testpoint |
| G  | `report_unexercised_covergroups(db, testplan)` | UCIS scopes + testplan | zero-hit covergroups list |
| I  | `report_coverage_contribution(db)` | contrib/*.bin | per-test unique bin contribution table |

### P2 Reports (future)

| ID | Function | Inputs | Output |
|----|----------|--------|--------|
| H  | `report_test_budget(testplan, db)` | test_stats CPU mean + testplan | CPU hours by stage |
| J  | `report_minimum_test_set(db, target)` | contrib + target | minimum test set with savings estimate |
| K  | `report_closure_forecast(db)` | history coverage series | timeline prediction with CI |
| L  | `report_safety_matrix(results, waivers, path)` | traceability + waivers | CSV/text safety matrix |
| M  | `report_seed_reliability(db, test_name)` | history buckets | seed range heat-map |

### CI/CD Export (§11.3.5)

New module: `src/ucis/ncdb/testplan_export.py`

- `export_junit_xml(results, output_path)` — testpoints as JUnit `<testcase>` elements
- `export_github_annotations(results)` — writes `::error::` / `::warning::` lines to stdout
- `export_summary_markdown(results, history_db=None)` — GitHub Actions Job Summary markdown

---

## Phase 4 — CLI Integration

Add new sub-commands to the existing `pyucis` CLI (wherever it lives):

- `pyucis history query <cdb> <test_name> [--days N]`
- `pyucis history stats <cdb> [--top-flaky N] [--top-failing N]`
- `pyucis testplan import <cdb> <hjson_path> [--subs key=val ...]`
- `pyucis testplan closure <cdb> [--testplan path] [--stage V2]`
- `pyucis testplan export-junit <cdb> [--testplan path] -o output.xml`
- `pyucis squash <cdb> [--policy pass_only]`
- `pyucis merge <out.cdb> <in1.cdb> [<in2.cdb> ...]`

---

## Testing Strategy

### Unit Tests — Binary Formats

**File**: `tests/unit/ncdb/test_test_registry.py`
- `test_assign_run_id_increments` — monotonic, survives roundtrip
- `test_lookup_name_id_new` — new name assigned correctly
- `test_lookup_name_id_existing` — same name returns same ID
- `test_name_heap_sorted` — binary search correctness
- `test_seed_id_roundtrip` — seed stored and retrieved verbatim
- `test_serialize_deserialize_empty` — empty registry roundtrip
- `test_serialize_deserialize_1000_names` — large registry roundtrip

**File**: `tests/unit/ncdb/test_test_stats.py`
- `test_update_pass` — pass_count increments, last_ts updates
- `test_update_fail` — fail_count, transition_count, streak update
- `test_welford_mean` — cpu_time mean converges on known series
- `test_welford_stddev` — M2 accumulator → stddev correct
- `test_flake_score_alternating` — alternating pass/fail → score ≈ 1.0
- `test_flake_score_stable` — all-pass → score = 0.0
- `test_cusum_change_point` — sustained failures → CUSUM exceeds h=4.0
- `test_grade_score_range` — [0, 1] always
- `test_serialize_deserialize` — full table roundtrip

**File**: `tests/unit/ncdb/test_history_buckets.py`
- `test_write_read_single_record` — one record, roundtrip
- `test_name_index_binary_search` — lookup for specific name_id O(log N)
- `test_seed_dict_compression` — seed_idx maps to correct global seed_id
- `test_ts_delta_encoding` — varint deltas decode to correct timestamps
- `test_status_flags_pack_unpack` — nibble-packed byte round-trips all values
- `test_seal_deflate` — sealed bucket compresses, decompresses correctly
- `test_seal_lzma` — LZMA tier works
- `test_10k_records_size` — 10K records bucket ≤ design projection (~5 KB compressed)
- `test_records_for_name_not_present` — returns empty list

**File**: `tests/unit/ncdb/test_bucket_index.py`
- `test_add_and_query_range` — date range filter
- `test_buckets_for_name` — name_id range filter
- `test_pass_rate_series` — fail_count/num_records computation
- `test_serialize_deserialize_empty`
- `test_serialize_deserialize_3650_entries` — 10-year index ≤ 90 KB

**File**: `tests/unit/ncdb/test_contrib_index.py`
- `test_passing_run_ids_pass_only` — POLICY_PASS_ONLY filter
- `test_passing_run_ids_strict` — is_rerun + first_attempt filtering
- `test_squash_watermark_update`
- `test_remove_entries_after_squash`
- `test_serialize_deserialize`

**File**: `tests/unit/ncdb/test_squash_log.py`
- `test_append_one_entry`
- `test_append_multiple_entries` — all entries preserved
- `test_serialize_deserialize`

### Unit Tests — Testplan

**File**: `tests/unit/ncdb/test_testplan.py`
- `test_testpointForTest_exact`
- `test_testpointForTest_seed_strip` — `uart_smoke_12345` → `uart_smoke`
- `test_testpointForTest_wildcard` — `foo_*` matches `foo_bar`
- `test_testpointsForStage`
- `test_stages_ordered` — V1 < V2 < V2S < V3
- `test_serialize_deserialize_roundtrip`
- `test_load_save_standalone` — Mode B file write/read
- `test_na_testpoint` — `na=True` serializes/deserializes correctly

**File**: `tests/unit/ncdb/test_testplan_closure.py`
- `test_compute_closure_all_closed`
- `test_compute_closure_partial`
- `test_compute_closure_not_run` — test not in DB
- `test_compute_closure_na` — N/A testpoint → TPStatus.NA
- `test_compute_closure_unimplemented` — empty tests list
- `test_stage_gate_pass` — all V1+V2 testpoints closed
- `test_stage_gate_fail` — one gap in V2
- `test_stage_gate_requires_flake_score` — flake gate integration
- `test_find_covergroup_scopes` — DFS finds matching covergroup scope

**File**: `tests/unit/ncdb/test_testplan_hjson.py`
- `test_import_simple_hjson` — basic parse
- `test_import_wildcard_expansion` — `{name}{intf}` expands to list
- `test_import_na_testpoint` — `tests: ["N/A"]` → `na=True, tests=[]`
- `test_import_fallback_no_hjson_package` — works with stdlib json for valid JSON subset

### Unit Tests — Merger Fix

**File**: `tests/unit/ncdb/test_merger.py` (extend existing)
- `test_merge_preserves_contrib_data` — merge two DBs with contrib/*.bin; output has both
- `test_merge_run_id_renumbering` — no run_id collisions after merge
- `test_merge_testplan_same` — both inputs have same testplan → copied to output
- `test_merge_testplan_different_source_file` — warning emitted, no testplan in output
- `test_merge_testplan_newer_timestamp_wins`

### Integration Tests

**File**: `tests/integration/test_history_workflow.py`
- `test_write_and_query_7_days` — write 7 days × 100 tests; query last 7 days; check record count
- `test_cold_start_load_200kb` — measure total I/O on open (registry + stats + contrib_index + bucket_index)
- `test_add_test_run_updates_stats` — `add_test_run()` → `get_test_stats()` reflects update
- `test_squash_operation` — end-to-end: write runs → squash → verify contrib files removed + squash_log entry
- `test_backward_compat_v1_db` — open existing v1 CDB; all v1 reads still work; no v2 members written unless explicitly requested
- `test_pass_only_merge_filter` — failing runs excluded from coverage after squash

**File**: `tests/integration/test_testplan_workflow.py`
- `test_embed_testplan_and_retrieve` — write CDB with testplan; reopen; `getTestplan()` returns correct data
- `test_standalone_testplan_mode_b` — `Testplan.load()` + `compute_closure()` without opening a CDB
- `test_regression_delta` — two CDB snapshots → `report_regression_delta()` returns newly-closed/failing
- `test_closure_report_stage_gate` — end-to-end: import hjson → embed → compute_closure → stage_gate_status

**File**: `tests/integration/test_ci_export.py`
- `test_export_junit_xml` — valid JUnit XML produced; testpoint names appear as test cases
- `test_export_github_annotations` — `::error::` lines produced for FAILING testpoints

### Performance Test (manual / benchmark only, not in CI)

**File**: `tests/integration/test_history_performance.py` (marked `@pytest.mark.slow`)
- `bench_write_1m_records` — 1M test run records written; bucket files ≤ design projections
- `bench_query_single_test_7_days` — query for one test over 7 days in < 100 ms
- `bench_top_flaky_no_bucket_io` — `top_flaky_tests()` involves zero bucket file reads

---

## Documentation

### Docstrings

All new public functions and classes must have Google-style docstrings covering:
- One-line summary
- Args (with types)
- Returns
- Raises (if any)
- Example snippet for non-obvious usage

### `doc/source/working-with-coverage/test-history.rst` (new file)

Added to the `working-with-coverage/index.rst` toctree.

Section outline:
1. **Overview** — why binary history, size comparison table
2. **ZIP Members** — table of all new members with purpose
3. **Reading and Writing History** — `add_test_run()`, `query_test_history()`, `get_test_stats()`
4. **Squash Operation** — when to squash, policy options, what changes
5. **Backward Compatibility** — v1/v2 flag, old files remain readable

### `doc/source/working-with-coverage/testplan.rst` (new file)

Added to the `working-with-coverage/index.rst` toctree.

Section outline:
1. **Overview** — testplan concepts, two storage modes (A/B)
2. **Data Model** — `Testplan`, `Testpoint`, `CovergroupEntry` with field descriptions
3. **Embedding a Testplan (Mode A)** — `setTestplan()`, `getTestplan()`, write/read cycle
4. **Standalone Testplan (Mode B)** — `Testplan.load()`, `Testplan.save()`, when to use each mode
5. **OpenTitan Hjson Import** — `import_hjson()` with wildcard substitution examples
6. **Closure Computation** — `compute_closure()`, `stage_gate_status()`, `TPStatus` values
7. **Coverage Per Testpoint** — `build_covergroup_index()`, Report C
8. **Waiver Management** — `WaiverSet` API, `waivers.json` schema
9. **CI/CD Export** — JUnit XML, GitHub Annotations, Summary Markdown
10. **Usage Examples** — full worked example from hjson → closure → JUnit XML

### `doc/source/reference/formats/ncdb-format.rst` (extend existing)

Add a new section to the existing NCDB format reference covering the v2 binary history
members: `test_registry.bin`, `test_stats.bin`, `history/NNNNNN.bin`, `history/bucket_index.bin`,
`contrib_index.bin`, `squash_log.bin`. Each member gets a field table and encoding notes.
No new file needed — this is an extension of the existing format reference.

### `README.md` update

Add a "Test History & Testplan" section (after the existing format descriptions) pointing to
the published docs and listing key capabilities:
- Binary history store for thousands of regressions
- Per-test flake score, CUSUM change-point detection
- Testplan embedding and closure computation
- Stage gate readiness, confidence-weighted closure
- CI/CD export (JUnit, GitHub Actions)

---

## File Inventory

### New files

| File | Phase | Notes |
|------|-------|-------|
| `src/ucis/ncdb/test_registry.py` | 1 | |
| `src/ucis/ncdb/test_stats.py` | 1 | |
| `src/ucis/ncdb/history_buckets.py` | 1 | |
| `src/ucis/ncdb/bucket_index.py` | 1 | |
| `src/ucis/ncdb/contrib_index.py` | 1 | |
| `src/ucis/ncdb/squash_log.py` | 1 | |
| `src/ucis/ncdb/testplan.py` | 2 | |
| `src/ucis/ncdb/testplan_closure.py` | 2 | |
| `src/ucis/ncdb/testplan_hjson.py` | 2 | |
| `src/ucis/ncdb/waivers.py` | 2 | |
| `src/ucis/ncdb/testplan_export.py` | 3 | |
| `src/ucis/ncdb/reports.py` | 3 | |
| `tests/unit/ncdb/test_test_registry.py` | 1 | |
| `tests/unit/ncdb/test_test_stats.py` | 1 | |
| `tests/unit/ncdb/test_history_buckets.py` | 1 | |
| `tests/unit/ncdb/test_bucket_index.py` | 1 | |
| `tests/unit/ncdb/test_contrib_index.py` | 1 | |
| `tests/unit/ncdb/test_squash_log.py` | 1 | |
| `tests/unit/ncdb/test_testplan.py` | 2 | |
| `tests/unit/ncdb/test_testplan_closure.py` | 2 | |
| `tests/unit/ncdb/test_testplan_hjson.py` | 2 | |
| `tests/integration/test_history_workflow.py` | 1 | |
| `tests/integration/test_testplan_workflow.py` | 2 | |
| `tests/integration/test_ci_export.py` | 3 | |
| `doc/source/working-with-coverage/test-history.rst` | 1 | Add to `working-with-coverage/index.rst` toctree |
| `doc/source/working-with-coverage/testplan.rst` | 2 | Add to `working-with-coverage/index.rst` toctree |

### Modified files

| File | Phase | Change |
|------|-------|--------|
| `src/ucis/ncdb/constants.py` | 1 | New member constants, version bump, status constants |
| `src/ucis/ncdb/manifest.py` | 1 | `history_format` field |
| `src/ucis/ncdb/ncdb_ucis.py` | 1+2 | Binary history API, testplan API, waivers API |
| `src/ucis/ncdb/ncdb_writer.py` | 1+2 | Write new members, compression tiering |
| `src/ucis/ncdb/ncdb_reader.py` | 1+2 | Read new members, backward compat |
| `src/ucis/ncdb/ncdb_merger.py` | 1+2 | Fix contrib loss bug, merge testplan, merge stats |
| `tests/unit/ncdb/test_merger.py` | 1 | Extend with contrib + testplan merge tests |
| `doc/source/reference/formats/ncdb-format.rst` | 1 | New section for v2 binary history members (field tables) |
| `doc/source/working-with-coverage/index.rst` | 1+2 | Add `test-history` and `testplan` to toctree |
| `README.md` | 2 | New section on history + testplan features |

---

## Implementation Order

Within each phase, implement in dependency order:

**Phase 1 sequence:**
1. `constants.py` additions
2. `varint.py` — verify existing varint sufficient (read/review)
3. `test_registry.py` + unit tests
4. `test_stats.py` + unit tests
5. `history_buckets.py` + unit tests
6. `bucket_index.py` + unit tests
7. `contrib_index.py` + unit tests
8. `squash_log.py` + unit tests
9. `manifest.py` update
10. `ncdb_ucis.py` Phase 1 additions
11. `ncdb_writer.py` Phase 1 additions
12. `ncdb_reader.py` Phase 1 additions
13. `ncdb_merger.py` bug fix + Phase 1 additions
14. Integration tests
15. `doc/source/working-with-coverage/test-history.rst` + update `ncdb-format.rst` + update `working-with-coverage/index.rst`

**Phase 2 sequence:**
1. `testplan.py` + unit tests
2. `testplan_hjson.py` + unit tests
3. `testplan_closure.py` + unit tests
4. `waivers.py`
5. `ncdb_ucis.py` Phase 2 additions
6. `ncdb_writer.py` / `ncdb_reader.py` / `ncdb_merger.py` Phase 2 additions
7. Integration tests
8. `doc/source/working-with-coverage/testplan.rst` + update `working-with-coverage/index.rst`

**Phase 3 sequence:**
1. P0 reports (A, B, C, D)
2. P1 reports (E, F, G, I)
3. `testplan_export.py` (JUnit, GitHub, markdown)
4. CLI additions
5. `README.md` update
6. P2 reports (H, J, K, L, M) — as time allows

---

## Design Decisions (Resolved)

| # | Question | Decision |
|---|----------|----------|
| 1 | NCDB_VERSION / v2 opt-in | **Auto-migrate**: calling `add_test_run()` automatically upgrades the manifest to `history_format = "v2"`. No explicit flag needed. Existing v1 databases remain fully readable. |
| 2 | Bucket seal threshold | **Fixed at 10,000 records**. Not configurable for now; revisit if real-world workloads require tuning. |
| 3 | LZMA dependency | **Graceful fallback**: attempt `ZIP_LZMA`; if `liblzma` is unavailable, silently use `ZIP_DEFLATE, level=9`. No error raised, no user action required. |
| 4 | `hjson` package | **Hard dependency**: add `hjson` to `setup.py` install_requires and to `ivpm.yaml` in both `default` and `default-dev` groups. |
| 5 | Report output format | **Both structured and text**: each report function returns a typed dataclass with a `to_json()` method; a companion `format_*()` function renders it to human-readable text. CLI calls the formatter; tests assert on the dataclass. |
| 6 | Waiver expiry enforcement | **Caller's responsibility**: `WaiverSet.matches_scope()` checks scope/bin pattern only. Callers filter on `expires_at` as needed. |

