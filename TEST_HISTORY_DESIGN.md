# NCDB Test History Design

## Background and Motivation

UCIS coverage databases are typically used as snapshots — one file per regression, periodically
merged and squashed. But the underlying NCDB ZIP format can also serve as a long-term store for
test pass/fail history over thousands of runs and millions of test executions, provided the
representation is efficient enough.

This document covers:
1. Analysis of why `history.json` is unsuitable at scale
2. A complete binary format design for efficient test history storage inside NCDB ZIP files
3. Metrics that can be extracted from history data
4. How coverage-per-test and merge policy interact with the design

---

## Part 1: Why `history.json` Does Not Scale

### Current Format

Each test run is stored as a JSON object with ~23 fields in a single monolithic array in
`history.json`. Example compressed size: ~200–500 bytes per entry uncompressed.

### Problems at Scale

| Problem | Root Cause |
|---|---|
| ~200–500 bytes/entry uncompressed | 23 JSON field keys repeated every record |
| Full array parse to read anything | No structure within the ZIP entry |
| No time-based filtering | Single monolithic member |
| Full ZIP rewrite to append any data | ZIP format limitation — mitigable but not eliminated |
| No aggregate statistics | Must scan everything to find noisy tests |
| Merge discards `contrib/*.bin` | Bug in `_merge_same_schema`: only copies strings/scope/counts/history/sources |

### Size Comparison

| Scenario | `history.json`-in-ZIP | Proposed binary buckets |
|---|---|---|
| 1K tests × 1K runs | ~75 MB | ~5 MB |
| 1K tests × 1M runs | ~75 GB | ~5 GB |
| Read to query 1 test over 7 days | Decompress all | 7 × ~5–10 KB |

---

## Part 2: New ZIP Members

Four new ZIP entries are added alongside the existing members. Existing members (`history.json`,
`contrib/*.bin`, `counts.bin`, etc.) are retained for backward compatibility and coverage data.

```
test_registry.bin          ← global: test name ↔ stable integer ID + seed registry
test_stats.bin             ← global: per-test aggregate metrics (flake score, CUSUM, etc.)
history/NNNNNN.bin         ← one ZIP entry per bounded bucket of test run records
history/bucket_index.bin   ← index: maps bucket number → date range, record count, name range
contrib_index.bin          ← index: run_id → status, for efficient pass-only merge
squash_log.bin             ← audit trail: each squash operation recorded permanently
```

`history.json` continues to store MERGE nodes (small, infrequent). TEST nodes move to the
binary bucket files.

---

## Part 3: Binary Format Specifications

### 3.1 `test_registry.bin`

Stores each unique test base name and seed exactly once. Assigned stable integer IDs that
persist across ZIP rewrites and merges. Also holds the global `run_id` counter.

```
magic:              u32 = 0x54535452   # 'TSTR'
version:            u8  = 1
next_run_id:        u32                # monotonically increasing, never decreases
num_names:          u32
num_seeds:          u32

# Fixed-size offset table (O(1) access by name_id):
name_string_offsets: u32[num_names]   # byte offset into string heap
seed_string_offsets: u32[num_seeds]   # byte offset into seed heap

# String heaps (null-terminated UTF-8):
name_heap:          bytes
seed_heap:          bytes
```

- Names are stored sorted → binary search gives O(log N) name → name_id lookup
- Seeds with integer values are stored as their decimal string representation
- Seeds that are complex strings (e.g. tool-specific) stored verbatim
- 1000 names × ~30 bytes avg = ~30 KB total (trivially small, load once at open)

### 3.2 `history/NNNNNN.bin` — Bounded Bucket Files

Buckets are bounded by record count (~10K records max), not strictly by date. The bucket
sequence number is zero-padded 6 digits. This keeps individual buckets small and decompressible
independently.

#### Layout: Columnar, Not Row-Oriented

Records are sorted by `(name_id, ts)` within each bucket. The name_id column is eliminated
from per-record storage by using a name index (which doubles as perfect run-length encoding).

```
Header:
  magic:          u32 = 0x48445942   # 'HDYB'
  version:        u8  = 1
  num_records:    u32
  num_names:      u16                # unique name_ids in this bucket
  ts_base:        u32                # unix timestamp of the first record

Name index (sorted by name_id — enables O(log N) lookup, eliminates name_id column):
  entries[num_names]:
    name_id:      u32
    start_row:    u32               # first record index for this name
    count:        u16               # number of records for this name

Seed dictionary (local to this bucket, enables 1-byte seed references):
  num_seeds:      u16
  seed_ids:       u32[num_seeds]    # global seed_id from test_registry.bin

Columns (independent arrays, each compresses optimally under DEFLATE/LZMA):
  seeds[]:        u8[num_records]   # index into seed dictionary (1 byte vs 4)
  ts_deltas[]:    varint[num_records]  # seconds since ts_base, delta per name group
  status_flags[]: u8[num_records]   # nibble-packed: high nibble=status, low nibble=flags
```

The `status_flags` byte packs two fields:
```
  bits [7:4]  status:  0=OK  1=FAIL  2=ERROR  3=FATAL  4=COMPILE  (3 bits used)
  bits [3:0]  flags:   bit0=seed_is_hash  bit1=is_rerun
                       bit2=has_coverage  bit3=was_squashed
```

CPU time is intentionally omitted from per-record storage — it is maintained as mean and
variance in `test_stats.bin` via Welford's online algorithm, which is sufficient for all
metrics described in Part 5.

#### Per-Record Cost (Revised)

| Field | Old row design | New columnar design |
|---|---|---|
| name_id | 4 bytes | **0** (implicit from name index) |
| seed | 4 bytes | **1** (local dict index, u8) |
| timestamp | 4 bytes | **~1.5** (varint delta) |
| status + flags | 2 bytes | **1** (nibble-packed) |
| cpu_time (f16) | 2 bytes | **0** (moved to test_stats.bin) |
| padding | 1 byte | **0** |
| **Total** | **~16 bytes** | **~3.5 bytes avg** |

Before DEFLATE. Columnar layout with homogeneous columns achieves 5–8× DEFLATE compression
on typical regression data (compared to ~3× for interleaved row layout). Effective storage:
~0.5–0.7 bytes per test run record.

#### Compression Tiers

- **Current day's bucket** (may be rewritten): `ZIP_DEFLATE, compresslevel=1` — fast write
- **Sealed buckets** (day has passed, immutable): `ZIP_LZMA` or `ZIP_DEFLATE, compresslevel=9`
- **`test_stats.bin`, `test_registry.bin`** (read on every open): `ZIP_DEFLATE, compresslevel=1`

### 3.3 `history/bucket_index.bin`

Maps bucket sequence numbers to date ranges and provides aggregate counts for fast
regression-trend queries without opening individual bucket files.

```
magic:        u32 = 0x42494458   # 'BIDX'
version:      u8
num_buckets:  u32

entries[num_buckets]:              # sorted by bucket_seq
  bucket_seq:   u32               # matches NNNNNN in filename
  ts_start:     u32               # unix timestamp of first record
  ts_end:       u32               # unix timestamp of last record
  num_records:  u32
  fail_count:   u32               # enables pass-rate-over-time without opening bucket
  min_name_id:  u32               # range bounds for fast skip
  max_name_id:  u32
```

24 bytes/entry. For 3650 days (10 years) at ~10K records/bucket:
- ~3650 buckets × 24 bytes = **87 KB** for the complete 10-year index
- The `fail_count` field enables regression pass-rate trend plots from the index alone

### 3.4 `test_stats.bin`

One fixed-size 64-byte record per unique test, indexed by `name_id`. Load entire file at open
time (1000 tests × 64 bytes = 64 KB). Enables all aggregate queries without touching buckets.

All fields maintained incrementally — O(1) update per new test run.

```
magic:            u32 = 0x54535441   # 'TSTA'
version:          u8
num_tests:        u32

entries[num_tests]:         # indexed by name_id (O(1) access)
  total_runs:        u32
  pass_count:        u32
  fail_count:        u32
  error_count:       u32
  first_ts:          u32    # unix timestamp of first ever run
  last_ts:           u32    # unix timestamp of most recent run
  last_green_ts:     u32    # unix timestamp of last passing run
  transition_count:  u32    # consecutive status changes (for flake_score)
  streak:            i16    # current streak: positive=passes, negative=fails
  last_status:       u8     # status of most recent run
  _pad:              u8
  flake_score:       f32    # transition_count / max(total_runs-1, 1)  ∈ [0,1]
  fail_rate:         f32    # fail_count / total_runs                  ∈ [0,1]
  mean_cpu_time:     f32    # Welford online mean (seconds)
  m2_cpu_time:       f32    # Welford M2 accumulator → stddev = sqrt(M2/N)
  cusum_value:       f32    # running CUSUM statistic for change detection
  cusum_ref_mean:    f32    # μ₀ used for CUSUM (set at baseline period)
  grade_score:       f32    # composite effectiveness score [0,1]
  total_seeds_seen:  u16    # unique seeds ever run for this test
  _reserved:         u8[6]
```

Key derived values:
- `stddev_cpu_time = sqrt(m2_cpu_time / total_runs)` — no bucket scan needed
- `days_since_last_pass = (now - last_green_ts) / 86400`
- `streak < -5` → definitively broken (not just flaky)
- `abs(streak) < 3 AND flake_score > 0.3` → likely flaky

### 3.5 `contrib_index.bin` — Pass-Only Merge Support

This is the pivotal addition for coverage-per-test efficiency. Every test run that produced
coverage data has an entry here. Status is cached so pass-only merge decisions require no
bucket scanning.

```
magic:             u32 = 0x43494458   # 'CIDX'
version:           u8
merge_policy:      u8    # 0=all_tests  1=pass_only  2=exclude_error_and_rerun
squash_watermark:  u32   # highest run_id already baked into counts.bin
num_active:        u32   # contrib files present (not yet squashed)

entries[num_active]:     # sorted by run_id
  run_id:    u32
  name_id:   u16         # cached for display without hitting bucket
  status:    u8          # cached — avoids opening bucket for merge decision
  flags:     u8          # bit0=is_rerun  bit1=first_attempt_passed
```

8 bytes/entry. Pass-only merge:
```python
passing = [e.run_id for e in contrib_index.entries if e.status == OK]
counts = sum(load_contrib(f"contrib/{run_id}.bin") for run_id in passing)
```

### 3.6 `squash_log.bin` — Coverage Provenance Audit Trail

Append-only log. Survives squash operations permanently. Answers "was my counts.bin built from
passing tests only?" even years after the fact.

```
magic:   u32
version: u8
num_squashes: u32

entries[num_squashes]:
  ts:         u32   # unix timestamp of squash
  policy:     u8    # 0=all  1=pass_only  2=exclude_error_and_rerun
  _pad:       u8[3]
  from_run:   u32   # first run_id included in squash
  to_run:     u32   # new squash_watermark after this operation
  num_runs:   u32   # total runs included
  pass_runs:  u32   # passing runs included in counts.bin contribution
```

28 bytes/squash event.

---

## Part 4: Coverage-Per-Test Interaction

### 4.1 Stable `run_id` Replaces Positional `history_idx`

**Current bug**: `contrib/{history_idx}.bin` uses position in `history.json` as key. After a
merge of two sources (each with `contrib/0.bin`, `contrib/1.bin`, ...), filenames collide and
the merger silently drops all contrib data.

**Fix**: each test run is assigned a globally unique `run_id` (u32) from the counter in
`test_registry.bin` at write time. Contrib files become `contrib/{run_id}.bin`. The run_id is
stable across ZIP rewrites, merges, and squash operations.

### 4.2 Coverage Watermark Model

At any point in time, total coverage is:

```
total_coverage = counts.bin                              (squashed base)
              + Σ contrib/{run_id}.bin                   (active delta)
                for run_id in contrib_index.entries
                where merge_policy_filter(entry.status, entry.flags)
```

`squash_watermark` in `contrib_index.bin` defines the boundary. Run IDs ≤ watermark are baked
into `counts.bin`; run IDs > watermark have their contrib files present.

### 4.3 Merge Policy Options

The `flags` byte in `contrib_index.bin` entries enables four distinct merge policies without
re-scanning bucket files:

| Policy | Filter |
|---|---|
| All tests | no filter |
| Pass only (any attempt) | `status == OK` |
| Pass on first attempt only | `status == OK AND NOT is_rerun` |
| Strict (exclude flaky contributions) | `status == OK AND NOT (is_rerun AND first_attempt_passed)` |

The last policy ("strict") excludes coverage from tests that only pass on retry — coverage
that cannot be reliably reproduced and may indicate environmental flakiness rather than real
design behavior.

### 4.4 Fixed Same-Schema Fast Merge Path

`NcdbMerger._merge_same_schema()` currently discards all `contrib/*.bin` data. It must be
updated to:

1. Assign run_id offsets to each source:
   - `offset_B = max(run_id in source_A) + 1`
   - `offset_C = max(run_id in source_B) + 1`, etc.

2. Copy and rename contrib files: `contrib/{source_run_id}.bin` → `contrib/{source_run_id + offset}.bin`

3. Merge `contrib_index.bin` entries from all sources (adjust run_ids by offset, re-sort)

4. Append `squash_log.bin` entries from all sources (no run_id adjustment needed)

5. Sum counts arrays for the merged `counts.bin`

This changes the fast path from O(bins) to O(bins + total_contrib_data). For large merges,
squash sources first (bake their contribs into counts.bin) before merging — which is the
correct operational model for a coverage closure flow anyway.

### 4.5 Squash Operation

When squashing coverage:

1. Read `contrib_index.bin` for active entries (run_ids > squash_watermark)
2. Apply merge policy filter
3. Sum selected `contrib/{run_id}.bin` files into `counts.bin`
4. Delete the contrib files for squashed run_ids
5. Update `squash_watermark` in `contrib_index.bin`
6. Remove squashed entries from `contrib_index.bin`
7. Append a record to `squash_log.bin`
8. Mark `was_squashed=1` in the corresponding bucket record flags

Test history bucket records are **never modified** during squash (only the `was_squashed` flag
is set). Bucket files themselves are immutable once sealed.

---

## Part 5: Metrics Extractable from History Data

### 5.1 Instantaneous Metrics (from `test_stats.bin` only — no bucket scan)

All O(1) or O(N_tests) with a single file read:

- **Flake score**: `transition_count / max(total_runs-1, 1)` ∈ [0,1]
  - 0.0 = completely stable; 1.0 = alternates every single run
  - Distinguishes noisy from broken (a broken test has `flake_score ≈ 0` despite `fail_rate ≈ 1`)
- **Fail rate**: `fail_count / total_runs`
- **Current streak**: `streak` field — negative = consecutive failures, positive = consecutive passes
- **Days since last pass**: `(now - last_green_ts) / 86400`
- **CPU time mean and stddev**: from Welford fields (no raw data needed)
- **Silent death**: `last_ts` is stale despite test being in the suite
- **Test re-introduction**: `first_ts` is recent for a known-old test name
- **Top N flakiest tests**: sort by `flake_score DESC` — no bucket scan
- **Top N consistently failing tests**: filter `fail_rate > threshold AND flake_score < 0.1`
- **Composite test grade**: `(1 - fail_rate) × (1 - flake_score) × (1 / mean_cpu_time_normalized)`
- **CPU time regression**: `mean_cpu_time` trending up week-over-week (compare saved baselines)

### 5.2 Trend Metrics (from `bucket_index.bin` only — no bucket decompression)

From the 24-byte per-bucket index entries:

- **Regression pass rate over time**: `(num_records - fail_count) / num_records` per bucket
- **Run volume per day**: `num_records` per bucket → detect farm capacity changes
- **Failure spike detection**: buckets where `fail_count / num_records > threshold`

### 5.3 Historical Detail Metrics (from bucket files — targeted reads)

For a specific test X in a date range:
1. Get `name_id` from `test_registry.bin`
2. Use `bucket_index.bin` to find buckets where `min_name_id ≤ name_id ≤ max_name_id`
3. For each candidate bucket, binary-search the name index → O(log N_unique_tests)
4. Extract only the records for that test

Metrics enabled:
- **Pass/fail history timeline**: full status over time for one test
- **Fail streak history**: detect multiple distinct failure episodes
- **Seed-correlated failures**: group by `seed_id`, compute `fail_count / total` per seed
  - Seeds with 100% failure rate = deterministic RTL bug masquerading as random failure
- **Seed diversity**: entropy over seed→status distribution; low entropy = poor randomization
- **Rerun effectiveness**: `P(pass | is_rerun AND prior_status == FAIL)` — infrastructure flakiness signal

### 5.4 Cross-Test Pattern Metrics (from bucket files — multi-test scan)

Reading a single bucket (one day or one regression):

- **Killer seeds**: seeds where `count(failing_tests) > threshold` in one bucket
  - `GROUP BY seed_id → set of failing name_ids → find recurring clusters`
  - Indicates a systemic RTL issue (deadlock, resource contention at a specific init value)
- **Failure co-occurrence**: `P(test_B fails | test_A fails in same bucket)`
  - High co-occurrence → tests hit same RTL block → redundancy or common bug
- **Cascade detection**: temporal causality — does failing test A precede failing test B?
- **Redundant test candidates**: pairs with `correlation(status_A, status_B) > 0.95`
  - Both always pass and fail together; one adds no value

### 5.5 CUSUM Change-Point Detection

The `cusum_value` and `cusum_ref_mean` in `test_stats.bin` implement an incremental CUSUM
(Cumulative Sum) control chart for detecting when a test's pass/fail behavior changed. This
is the algorithm used by Atlassian's "Flakinator" and Google's flaky-test detection systems.

Update rule on each new run (O(1)):
```python
k = 0.5  # allowance parameter
h = 4.0  # decision threshold (tune to desired sensitivity)
x = 1.0 if status == FAIL else 0.0
S = max(0, S + x - (cusum_ref_mean + k))
if S > h:
    # change point detected — record timestamp, reset S
    S = 0.0
```

When a change point is detected, the timestamp is recorded so you can correlate with RTL
commits: "test X started failing consistently on 2026-03-01."

### 5.6 EDA-Specific: Seed Analytics

Unique to hardware verification — no software CI tool provides this:

- **Valuable seed ranking**: seeds that historically expose the most failures first
  - Re-run high-value seeds more frequently; Springer "Seed Selector" paper shows 42%+ speedup
- **Seed fatigue**: `fail_count_per_seed` approaching zero with recency weighting
  - Seeds that never fail anymore are candidates for replacement
- **Seed coverage diversity**: entropy of the seed→status distribution per test
  - Low entropy = seeds are not actually exploring different design states

---

## Part 6: Read/Write Strategy Summary

### Opening the Database (cold start)

1. Read `test_registry.bin` (~30 KB) → in-memory name↔id dict
2. Read `test_stats.bin` (~64 KB for 1000 tests) → all aggregate metrics immediately available
3. Read `contrib_index.bin` → pass-only merge table available
4. Read `history/bucket_index.bin` (~90 KB for 10 years) → full time index available

Total cold-start I/O: ~200 KB. All aggregate queries answerable immediately.

### Writing a New Test Run

1. Assign `run_id` (increment counter in `test_registry.bin`)
2. Look up or assign `name_id` and `seed_id`
3. Append record to current day's bucket (in memory; written at close)
4. Update `test_stats.bin` entry: O(1) Welford + CUSUM update
5. If coverage: add entry to `contrib_index.bin`

### Writing at Close (full ZIP rewrite)

1. Copy all sealed bucket files verbatim (read compressed bytes, write without re-compression)
2. Write current day's bucket (new or updated)
3. Write updated `bucket_index.bin`, `test_registry.bin`, `test_stats.bin`, `contrib_index.bin`
4. Write `squash_log.bin` (unchanged if no squash happened)
5. Write all existing `contrib/*.bin` files (only active ones — not squashed)

### Query: "All runs of test X, last 7 days"

1. Get `name_id` for X (from in-memory registry)
2. Scan `bucket_index.bin` for buckets where `ts_start ≥ 7_days_ago AND min_name_id ≤ name_id ≤ max_name_id`
3. For each candidate bucket (~7): decompress, binary-search name index, extract records
4. Total I/O: ~7 × 5–10 KB = **35–70 KB** regardless of total history size

### Query: "Top 20 flakiest tests"

1. Scan `test_stats.bin` (already loaded)
2. Sort by `flake_score DESC`, take top 20
3. Map `name_id → name` via registry
4. **Zero bucket I/O**

---

## Part 7: Files to Create/Modify for Implementation

### New Files

| File | Purpose |
|---|---|
| `src/ucis/ncdb/test_registry.py` | Serialize/deserialize `test_registry.bin`; assign run_ids, name_ids, seed_ids |
| `src/ucis/ncdb/test_stats.py` | Serialize/deserialize `test_stats.bin`; Welford + CUSUM incremental update |
| `src/ucis/ncdb/history_buckets.py` | Write/read columnar bucket files; name index; seed dict |
| `src/ucis/ncdb/bucket_index.py` | Write/read `history/bucket_index.bin` |
| `src/ucis/ncdb/contrib_index.py` | Write/read `contrib_index.bin`; pass-only filter enumeration |
| `src/ucis/ncdb/squash_log.py` | Write/read `squash_log.bin`; squash operation implementation |

### Modified Files

| File | Change |
|---|---|
| `src/ucis/ncdb/constants.py` | Add new member name constants; bump `NCDB_VERSION` to `"2.0"` |
| `src/ucis/ncdb/ncdb_writer.py` | Write new members; compression tiering; sealed-bucket copy optimization |
| `src/ucis/ncdb/ncdb_reader.py` | Read new members; fall back to `history.json` for MERGE nodes |
| `src/ucis/ncdb/ncdb_merger.py` | Fix contrib data loss bug; run_id renumbering; contrib_index merge |
| `src/ucis/ncdb/manifest.py` | Add `history_format` field to distinguish v1 (JSON) from v2 (binary) |

### Backward Compatibility

- `manifest.json` gains a `history_format` field: `"v1"` (JSON only) or `"v2"` (binary + JSON for MERGE nodes)
- Reader checks `history_format` and falls back to `history.json` for old files
- Old files without binary bucket members are fully readable; new features simply unavailable
- `history.json` continues to be written for MERGE nodes in all versions

---

## Part 8: Size Projections

At 1K tests × 10 runs/test/day = 10K records/day:

| Component | Size/day (raw) | Compressed (LZMA) | 10-year total |
|---|---|---|---|
| Bucket files | ~35 KB | ~5 KB | ~18 MB |
| bucket_index.bin | 24 bytes/bucket | — | ~90 KB |
| test_stats.bin | 64 KB (static) | ~20 KB | 20 KB |
| test_registry.bin | ~30 KB (static) | ~10 KB | 10 KB |
| contrib_index.bin | ~8 bytes/run | — | ~3 MB (for 400K active) |
| squash_log.bin | 28 bytes/squash | — | ~100 KB (1K squashes) |
| **Total** | | | **~21 MB** |

Compare to `history.json`: **~75 GB** for the same data. Approximately **3500× more
space-efficient**.

---

## Part 9: Testplan Integration — Mapping Issues and End-of-Regression Reports

### 9.1 OpenTitan Testplan Format Summary

The OpenTitan `testplanner` tool uses Hjson files with two top-level collections:

- **`testpoints`**: each has `name`, `stage` (V1/V2/V2S/V3), `desc`, `tests` (list of written
  test names), and optional `tags`.
- **`covergroups`**: each has `name` and `desc`, declaring the functional coverage groups
  expected to be exercised.

Testplans support `import_testplans` for shared plans with wildcard substitution (e.g.
`{name}_csr_hw_reset` expands per DUT). Setting `tests: ["N/A"]` marks a testpoint as
intentionally not mapped to simulation results.

A more detailed analysis is in `TESTPLAN_ANALYSIS_REPORT.md`.

---

### 9.2 Mapping Issues: OpenTitan Testplan Format → UCIS

#### Issue 1: No Native Testplan/Testpoint Hierarchy in UCIS

UCIS defines exactly two history node types (`UCIS_HISTORYNODE_TEST` and
`UCIS_HISTORYNODE_MERGE`). There is no `UCIS_HISTORYNODE_TESTPLAN` or testpoint scope type.
The UCIS LRM glossary references a "verification plan hierarchy" but this concept is not
realized in the standard API — it amounts to using UCIS tags to link coverage scopes back to
an external plan. The testplan must therefore be stored **outside** UCIS (as an Hjson/JSON
sidecar or in a dedicated ZIP member) and joined to UCIS data at query time.

#### Issue 2: Verification Stage Has No UCIS Equivalent

OpenTitan's `stage` field (`V1`/`V2`/`V2S`/`V3`) encodes the verification lifecycle milestone
a testpoint targets. UCIS has no such concept. `UCIS_INT_TEST_COMPULSORY` is the closest
analog — a boolean "must run" flag on individual test records — but it does not convey staged
milestone semantics and applies to tests, not testpoints.

Stage data must be stored in the testplan database (ZIP member or sidecar) and treated as an
external grouping key when producing reports.

#### Issue 3: Test-Name Matching is Implicit and Fragile

The binding between a testplan `tests` list entry (e.g. `"uart_smoke"`) and a UCIS history
node is by string match: the testplan test name must equal the logical name of the
`UCIS_HISTORYNODE_TEST` node (`UCIS_STR_TEST_NAME`). This convention is not enforced by UCIS.

Failure modes:
- The UCIS test name includes a seed suffix (`uart_smoke_12345`) while the testplan uses the
  bare name.
- Tool-specific prefixes or path components are added to the UCIS logical name.
- After squash, individual test history nodes may be absent from a merged database; only
  aggregate coverage remains.

**Recommended approach**: normalize test names by stripping known suffixes (seed, run index,
timestamp) at UCIS write time, or store the canonical testplan name as a user-defined
attribute `testplan:name` on the history node.

#### Issue 4: M:N Testpoint-to-Test Mapping

A single testpoint can map to multiple written tests; conversely, one written test can satisfy
multiple testpoints (the testplanner tool does not enforce 1:1 mapping). UCIS history nodes
are flat — there is no grouping structure to express "this test runs for this testpoint."

This mapping must be maintained in the testplan database and resolved at report time, not
inside UCIS.

#### Issue 5: Tag Semantics Mismatch

UCIS tags are plain strings with no associated value, intended as a grouping construct (e.g.
linking coverage scopes to plan items via a shared tag name). OpenTitan testplan tags carry
richer meaning: platform (`verilator`, `fpga_cw310`), mode (`gls`, `pa`, `rom`), or lifecycle
(`vector`). These are filter dimensions used to select which testpoints appear in a run.

UCIS tags cannot represent this; they would need to be stored as user-defined attributes on
the history nodes (`testplan:tag:gls = true`) or kept entirely in the testplan sidecar.

#### Issue 6: `tests: ["N/A"]` Has No UCIS Equivalent

A testpoint with `tests: ["N/A"]` is defined in the plan but intentionally has no simulation
coverage. UCIS has no concept of a "planned but unverifiable" entry. The testplan layer must
track `N/A` testpoints and exclude them from closure calculations, not from UCIS.

#### Issue 7: Covergroup Name Correlation Relies on Naming Convention

Testplan `covergroups` entries list the functional coverage groups expected to be exercised
by testpoints. In UCIS, covergroups are scope nodes in the design hierarchy. Matching a
testplan covergroup name (`timer_cg`) to a UCIS scope requires an agreed naming convention
(the UCIS scope name equals the SV covergroup name suffixed with `_cg`). No cross-file
uniqueness guarantee exists when designs are large or when multiple DUTs share covergroup
names.

#### Issue 8: Wildcard Expansion is Ephemeral

Imported testplans use substitution wildcards (e.g. `{name}{intf}_csr_hw_reset`). After
parsing, expanded test names exist only in memory; the unexpanded template is what's stored
in the Hjson file. UCIS has no awareness of this expansion. Any database that stores testplan
data must store the **post-expansion** test name list alongside the source template, so that
a query tool can reconstruct both the human-readable template and the runnable test names.

#### Issue 9: Merged Database Loses Individual Test Records

After a UCIS merge + squash, individual `UCIS_HISTORYNODE_TEST` nodes for squashed tests may
be absent from the merged database — only aggregate `counts.bin` coverage survives. This
means testpoint-level pass/fail status cannot be reconstructed from the merged UCIS database
alone. This is precisely why the binary history store (Parts 2–6 of this document) is
needed: it preserves per-test status even after coverage squash.

---

### 9.3 Testplan Storage Modes

Two storage modes are supported. They use the same JSON schema and the same
`Testplan` data model; the choice affects only where the file lives.

#### Mode A — Embedded (testplan stored inside the NCDB ZIP)

Add a `testplan.json` member to the NCDB ZIP file:

```
testplan.json   ← testplan snapshot stored with the database at import time
```

Best when the testplan is stable for the duration of the regression and should
travel with the coverage database (the most common case).

#### Mode B — Standalone (testplan kept as a separate file)

The testplan is maintained as a standalone `testplan.json` file on disk (or in a
source-control tree) and is **not** embedded in the NCDB. At analysis time the
user points tooling at both files:

```
uart_testplan.json   ← standalone testplan snapshot
regression.cdb       ← NCDB with no embedded testplan
```

This mode is preferred when:
- The testplan file is version-controlled separately from the regression database
  (e.g. testplan lives in the RTL repo; CDB is produced by CI and stored in
  artifact storage).
- You want to perform ad-hoc cross-analysis between an existing NCDB and a
  testplan that was never embedded (e.g. retro-fitting plan coverage onto legacy
  databases).
- Different testplan revisions must be compared against the same NCDB without
  re-generating the database.

`compute_closure()`, `stage_gate_status()`, and all report generators accept a
`Testplan` object regardless of whether it was loaded from an embedded ZIP member
or a standalone file — the API is identical in both modes.

---

Contents of `testplan.json` (stored post-expansion, with all imports resolved):

```json
{
  "format_version": 1,
  "source_file": "hw/ip/uart/data/uart_testplan.hjson",
  "import_timestamp": "2026-03-05T19:00:00Z",
  "testpoints": [
    {
      "name": "smoke",
      "stage": "V1",
      "desc": "Basic smoke test ...",
      "tests": ["uart_smoke"],
      "tags": [],
      "na": false
    },
    {
      "name": "csr",
      "stage": "V1",
      "desc": "CSR tests ...",
      "tests": ["uart_csr_hw_reset", "uart_jtag_csr_hw_reset"],
      "tags": ["csr"],
      "na": false,
      "source_template": "{name}{intf}_csr_hw_reset"
    }
  ],
  "covergroups": [
    { "name": "timer_cg", "desc": "Cover timer inputs ..." }
  ]
}
```

This snapshot approach means:
- The testplan in force when data was collected is always available alongside the data.
- Plan evolution (adding/removing testpoints, stage changes) is tracked naturally as part of
  the database's commit history.
- The post-expansion `tests` list is the authoritative source for UCIS test-name matching.

In Mode B (standalone), the same JSON schema is used; the file simply lives outside the ZIP.
Use `Testplan.load(path)` to read it and pass the resulting object directly to
`compute_closure()` alongside any NCDB opened with `NcdbUCIS`.

---

### 9.4 End-of-Regression Reports

Given the combination of:
- **Testplan** (`testplan.json`): testpoints, stages, test lists, covergroups
- **Latest regression UCIS** (current NCDB): per-test pass/fail, per-covergroup coverage
- **Historical UCIS** (merged NCDB with binary history): trends, flake scores, stage
  progression over time

the following report types offer high value:

#### Report A: Testpoint Closure Summary (per-regression)

For each testpoint, derive a status from the union of its mapped tests' UCIS results:

| Status | Condition |
|---|---|
| `CLOSED` | All mapped tests passed in this regression |
| `PARTIAL` | At least one mapped test passed, at least one failed |
| `FAILING` | All mapped tests ran and failed |
| `NOT RUN` | No mapped test appears in this regression's history nodes |
| `N/A` | Testpoint is marked `na: true` |
| `UNIMPLEMENTED` | `tests` list is empty |

Roll up by `stage` to show:

```
Stage V1: 12/12 closed  (100%)
Stage V2: 17/24 closed   (71%)  ← 5 FAILING, 2 NOT RUN
Stage V2S: 3/6  closed   (50%)
Stage V3:  0/4  closed    (0%)  ← all UNIMPLEMENTED
```

#### Report B: Stage Gate Readiness

Gate condition: all testpoints at stage S and all stages below S must be CLOSED before a
milestone sign-off. Report signals go/no-go per stage:

```
V1 GATE: ✅ PASS (12/12 closed)
V2 GATE: ❌ FAIL — 7 gaps remaining
V2S GATE: ❌ FAIL — requires V2 first
V3 GATE: ❌ FAIL — requires V2S first
```

Optionally, show the "critical path" — the failing testpoints that block the earliest gate.

#### Report C: Coverage Closure per Testpoint

For testpoints that declare associated covergroups, report UCIS coverage percentages:

| Testpoint | Stage | Coverage Groups | Coverage % | Status |
|---|---|---|---|---|
| `smoke` | V1 | `timer_cg` | 100% | CLOSED |
| `modes` | V2 | `modes_cg`, `key_cg` | 73% / 45% | GAP |
| `errors` | V2 | `err_cg` | 0% | NOT STARTED |

This links the test-pass view (Report A) with coverage closure: a test can pass without
achieving functional coverage goals if the covergroup is under-constrained.

#### Report D: Regression Delta (Latest vs Previous)

Compare testpoint status between the current regression and the immediately prior regression
(or any named baseline stored in the history buckets):

- **Newly CLOSED**: testpoints that passed this run but failed last run → progress
- **Newly FAILING**: testpoints that passed before but fail now → regressions requiring triage
- **Coverage delta**: covergroups that crossed a goal threshold (e.g. 90% → 100%) or regressed

This is the primary report for the engineer reviewing a nightly regression: focus on what
changed, not the static state.

#### Report E: Historical Stage Progression

Using the merged historical NCDB and the versioned testplan:

- Plot testpoint closure rate over time for each stage (V1, V2, V2S, V3)
- Mark the date when each stage gate was first fully closed
- Identify periods of regression (closure rate dropped)

```
V1 Closure over time:
100% ┤                               ╭──────────────── V1 milestone (2026-01-15)
 80% ┤                    ╭──────────╯
 60% ┤         ╭──────────╯
 40% ┤╭────────╯
  0% ┼──────────────────────────────────────────────────────►
     Jan 1          Jan 8          Jan 15         Jan 22
```

#### Report F: Testpoint Reliability (History-Augmented)

For testpoints whose tests have poor historical reliability (high `flake_score` or low
`grade_score` from `test_stats.bin`), flag that closure claims are less trustworthy:

| Testpoint | Stage | Tests | Flake Score | Closure Confidence |
|---|---|---|---|---|
| `smoke` | V1 | `uart_smoke` | 0.02 | HIGH |
| `timeout` | V2 | `uart_timeout` | 0.41 | LOW ⚠️ |

A testpoint is considered "confidently closed" only when its tests consistently pass across
multiple seeds and runs (low flake, long green streak). A single passing run with `flake_score
> 0.3` should not be counted as closure.

#### Report G: Unexercised Coverage Groups

From the testplan `covergroups` list, identify:

- Covergroups with zero UCIS hits in the latest regression: unreached design states
- Covergroups with hits below the SV `at_least` goal: partially covered
- Covergroups not present in the UCIS database at all: testbench may not yet implement them

#### Report H: Test Budget by Stage

From CPU time data in `test_stats.bin` (mean CPU time × runs):

| Stage | Testpoints | Tests | Est. CPU Hours | % of Total Budget |
|---|---|---|---|---|
| V1 | 12 | 8 | 14 h | 12% |
| V2 | 24 | 31 | 87 h | 73% |
| V2S | 6 | 9 | 14 h | 12% |
| V3 | 4 | 0 | — | — |

This identifies which verification stages dominate simulation cost and allows informed
decisions about regression time allocation or test pruning.

---

### 9.5 Implementation Notes

- **Testplan data is stored in the NCDB ZIP** as `testplan.json`. It is read-only after
  import; a new import (with updated testplan) creates a new snapshot. The previous snapshot
  is retained for delta comparison.

- **The UCIS join key** is `test_name` (testplan `tests` list entry) ↔ UCIS logical history
  node name (`UCIS_STR_TEST_NAME`). If exact matching fails, a fallback stripping seed
  suffixes (`_\d+$`) is applied. Failures to match are reported as `NOT RUN`.

- **Stage data is not in UCIS**: stage-gated reports are produced by the report layer joining
  `testplan.json` data with UCIS query results. No UCIS schema changes are required.

- **Covergroup matching** uses the testplan covergroup `name` field matched against UCIS
  scope `name` within the DUT instance hierarchy. Ambiguous matches (same name in multiple
  instances) are resolved by DUT-level scope path if available.

- **Historical data sourcing**: Report E (Stage Progression) requires the merged NCDB with
  bucket history. The report framework should detect whether the binary history store (Part 2)
  is present and fall back to `history.json` for databases that have not been upgraded.

- **Standalone testplan mode**: `compute_closure()` and all report generators accept a
  `Testplan` loaded from a standalone file (`Testplan.load(path)`) in exactly the same way
  they accept one retrieved from an embedded ZIP member (`db.getTestplan()`). No API
  difference exists between the two modes. This enables cross-analysis workflows such as
  applying a new testplan revision against an already-built NCDB, or retroactively mapping
  a testplan against legacy databases that pre-date testplan embedding.

---

## Part 10: PyUCIS-Native Testplan Embedding in NCDB

### 10.1 Design Principles

The embedding follows the established NCDB member pattern: a single new ZIP member
(`testplan.json`) with a dedicated `TestplanReader`/`TestplanWriter` pair, lazily loaded
through `NcdbUCIS`, and written through `NcdbWriter`. No changes to the UCIS standard
interface (`ucis.py`) are needed — all testplan API is an NCDB extension.

Two usage modes are explicitly supported:

**Mode A — Embedded**: the testplan is stored as `testplan.json` inside the NCDB ZIP and
retrieved via `db.getTestplan()`. The plan travels with the database.

**Mode B — Standalone**: the testplan is kept as a separate `testplan.json` file and loaded
directly with `Testplan.load(path)`. Analysis functions (`compute_closure()`,
`stage_gate_status()`, report generators) accept a `Testplan` object and a UCIS database
object as independent arguments, so both modes use identical downstream code.

Design constraints:
- The UCIS API (`db.historyNodes()`, `db.scopes()`, etc.) is unchanged.
- Testplan data does not pollute history nodes or the scope tree.
- Opening a database without a testplan has zero overhead.
- All testplan operations are O(1) after cold-start load (~1 ms).
- The ZIP member is omitted if no testplan was ever set (sparse, like `toggle.bin`).

---

### 10.2 Python Data Model

New file: **`src/ucis/ncdb/testplan.py`**

```python
from __future__ import annotations
import json, re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class CovergroupEntry:
    name: str           # covergroup name; must match SV covergroup scope name
    desc: str = ""


@dataclass
class Testpoint:
    name: str                       # testpoint identifier (snake_case)
    stage: str                      # "V1" | "V2" | "V2S" | "V3" | custom
    desc: str = ""
    tests: list[str] = field(default_factory=list)   # post-expansion test names
    tags:  list[str] = field(default_factory=list)
    na:    bool = False              # tests: ["N/A"] — intentionally unmapped
    source_template: str = ""        # original wildcard template before expansion


@dataclass
class Testplan:
    format_version:   int = 1
    source_file:      str = ""       # path to source .hjson (informational)
    import_timestamp: str = ""       # ISO-8601 UTC when embedded in the CDB

    testpoints:  list[Testpoint]      = field(default_factory=list)
    covergroups: list[CovergroupEntry] = field(default_factory=list)

    # ── In-memory indices (built lazily by _build_indices()) ──────────────

    _tp_by_name:   dict = field(default_factory=dict, repr=False, compare=False)
    _tp_by_test:   dict = field(default_factory=dict, repr=False, compare=False)
    _tp_by_cg:     dict = field(default_factory=dict, repr=False, compare=False)
    _indexed:      bool = field(default=False,        repr=False, compare=False)

    # ── Index building ────────────────────────────────────────────────────

    def _build_indices(self) -> None:
        """Build O(1) lookup tables from the testpoints list. Called lazily."""
        self._tp_by_name.clear()
        self._tp_by_test.clear()
        self._tp_by_cg.clear()
        for tp in self.testpoints:
            self._tp_by_name[tp.name] = tp
            for t in tp.tests:
                self._tp_by_test[t] = tp
        for cg in self.covergroups:
            # Map the covergroup back to every testpoint that owns it
            # (Covergroups are listed per-testplan, not per-testpoint in OpenTitan format,
            #  but the testpoints may reference them by naming convention.)
            pass
        self._indexed = True

    def _ensure_indexed(self) -> None:
        if not self._indexed:
            self._build_indices()

    # ── Public query API ──────────────────────────────────────────────────

    def getTestpoint(self, name: str) -> Optional[Testpoint]:
        """Return the testpoint with this name, or None."""
        self._ensure_indexed()
        return self._tp_by_name.get(name)

    def testpointForTest(self, test_name: str) -> Optional[Testpoint]:
        """Return the testpoint that owns *test_name*.

        Match order:
        1. Exact match: test_name in testpoint.tests
        2. Seed-suffix strip: strip trailing ``_\\d+`` and retry
        3. Wildcard: testpoint.tests entry ending ``_*`` prefix-matches test_name
        """
        self._ensure_indexed()
        tp = self._tp_by_test.get(test_name)
        if tp is not None:
            return tp
        # Strategy 2: strip seed suffix  (e.g. "uart_smoke_12345" → "uart_smoke")
        stripped = re.sub(r'_\d+$', '', test_name)
        if stripped != test_name:
            tp = self._tp_by_test.get(stripped)
            if tp is not None:
                return tp
        # Strategy 3: wildcard entries ("foo_*" matches "foo_bar")
        for pattern, tp in self._tp_by_test.items():
            if pattern.endswith('_*') and test_name.startswith(pattern[:-1]):
                return tp
        return None

    def testpointsForStage(self, stage: str) -> list[Testpoint]:
        """Return all testpoints targeting *stage* (e.g. "V2")."""
        return [tp for tp in self.testpoints if tp.stage == stage]

    def stages(self) -> list[str]:
        """Return the ordered unique stages present in the testplan."""
        _ORDER = {"V1": 0, "V2": 1, "V2S": 2, "V3": 3}
        seen = dict.fromkeys(tp.stage for tp in self.testpoints)
        return sorted(seen, key=lambda s: _ORDER.get(s, 99))

    # ── Serialization ─────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "format_version":   self.format_version,
            "source_file":      self.source_file,
            "import_timestamp": self.import_timestamp,
            "testpoints": [
                {
                    "name":            tp.name,
                    "stage":           tp.stage,
                    "desc":            tp.desc,
                    "tests":           tp.tests,
                    "tags":            tp.tags,
                    "na":              tp.na,
                    "source_template": tp.source_template,
                }
                for tp in self.testpoints
            ],
            "covergroups": [
                {"name": cg.name, "desc": cg.desc}
                for cg in self.covergroups
            ],
        }

    def serialize(self) -> bytes:
        return json.dumps(self.to_dict(), separators=(',', ':')).encode()

    @classmethod
    def from_dict(cls, d: dict) -> "Testplan":
        tp = cls(
            format_version=d.get("format_version", 1),
            source_file=d.get("source_file", ""),
            import_timestamp=d.get("import_timestamp", ""),
        )
        for rec in d.get("testpoints", []):
            tp.testpoints.append(Testpoint(
                name=rec["name"],
                stage=rec.get("stage", ""),
                desc=rec.get("desc", ""),
                tests=rec.get("tests", []),
                tags=rec.get("tags", []),
                na=rec.get("na", False),
                source_template=rec.get("source_template", ""),
            ))
        for rec in d.get("covergroups", []):
            tp.covergroups.append(CovergroupEntry(
                name=rec["name"], desc=rec.get("desc", "")
            ))
        return tp

    @classmethod
    def from_bytes(cls, data: bytes) -> "Testplan":
        return cls.from_dict(json.loads(data.decode()))

    @classmethod
    def load(cls, path: str) -> "Testplan":
        """Load a testplan from a standalone JSON file (Mode B)."""
        with open(path, "rb") as f:
            return cls.from_bytes(f.read())

    def save(self, path: str) -> None:
        """Write this testplan to a standalone JSON file (Mode B)."""
        with open(path, "wb") as f:
            f.write(self.serialize())
```

---

### 10.3 ZIP Member: `testplan.json`

A single new optional ZIP member added to the NCDB ZIP archive:

```
testplan.json   ← Testplan serialized as compact JSON (separators=(',',':'))
                  Compression: ZIP_DEFLATE (same as other JSON members)
                  Omitted entirely if no testplan has been set on the database
```

**Size estimate**: 500 testpoints × ~250 bytes/testpoint uncompressed ≈ 125 KB raw, ~20 KB
compressed. Negligible relative to `scope_tree.bin` or `counts.bin`.

The member stores the testplan **snapshot at the time it was imported into the CDB**: all
`import_testplans` references resolved, all wildcards expanded to final test names,
`tests: ["N/A"]` represented as `na: true` with the tests list empty.

---

### 10.4 NcdbUCIS Extension

The `NcdbUCIS` class gains a testplan lazy-load unit alongside the existing `history` and
`scopes` units:

```python
# In NcdbUCIS.__init__():
self._loaded_testplan: bool = False
self._testplan: Optional["Testplan"] = None  # None = "not present in file"
self._testplan_dirty: bool = False           # True if setTestplan() was called

# New public methods:

def getTestplan(self) -> Optional["Testplan"]:
    """Return the embedded Testplan, or None if none is stored."""
    self._ensure_testplan()
    return self._testplan

def setTestplan(self, tp: "Testplan") -> None:
    """Embed *tp* in this database.  Written on the next write() call."""
    from .testplan import Testplan
    if tp.import_timestamp == "":
        from datetime import datetime, timezone
        tp.import_timestamp = datetime.now(timezone.utc).isoformat()
    self._testplan = tp
    self._testplan_dirty = True
    self._loaded_testplan = True

# New internal method:

def _ensure_testplan(self) -> None:
    if self._loaded_testplan:
        return
    self._loaded_testplan = True
    self._read_zip()                        # populates _zf_cache if empty
    raw = self._zf_cache.get(MEMBER_TESTPLAN)
    if raw:
        from .testplan import Testplan
        self._testplan = Testplan.from_bytes(raw)
```

The `_read_zip()` call is already cached (`_zf_cache`), so calling `_ensure_testplan()` after
`_ensure_history()` adds no I/O. The testplan is the lightest unit to load.

---

### 10.5 New Constant

```python
# In src/ucis/ncdb/constants.py:
MEMBER_TESTPLAN = "testplan.json"
```

---

### 10.6 NcdbWriter Integration

```python
# In NcdbWriter.write(), after writing other optional members:
from .constants import MEMBER_TESTPLAN
testplan = getattr(db, '_testplan', None)
if testplan is not None:
    zf.writestr(MEMBER_TESTPLAN, testplan.serialize())
```

The testplan is written only if one was set on the db object. This preserves the sparse
member pattern — databases without testplans are byte-identical to today's output.

---

### 10.7 NcdbReader Integration

```python
# In NcdbReader.read(), after loading optional members:
from .constants import MEMBER_TESTPLAN
from .testplan import Testplan
if MEMBER_TESTPLAN in names:
    db._testplan = Testplan.from_bytes(zf.read(MEMBER_TESTPLAN))
    db._loaded_testplan = True
```

`NcdbReader` returns a `MemUCIS` (not an `NcdbUCIS`), so the testplan is attached directly
as a `_testplan` attribute. Code that uses `db.getTestplan()` should check for this attribute
with `getattr(db, '_testplan', None)` as a fallback for non-`NcdbUCIS` databases.

A thin mixin or helper function is preferred:

```python
# src/ucis/ncdb/testplan.py  (additional helper)
def get_testplan(db) -> Optional[Testplan]:
    """Retrieve testplan from any UCIS db object (NcdbUCIS or MemUCIS)."""
    if hasattr(db, 'getTestplan'):
        return db.getTestplan()
    return getattr(db, '_testplan', None)

def set_testplan(db, tp: Testplan) -> None:
    """Attach testplan to any UCIS db object."""
    if hasattr(db, 'setTestplan'):
        db.setTestplan(tp)
    else:
        tp.import_timestamp = tp.import_timestamp or \
            datetime.now(timezone.utc).isoformat()
        db._testplan = tp
```

---

### 10.8 NcdbMerger Integration

The merger must propagate testplan data without silently losing it:

#### Same-schema fast path (`_merge_same_schema`)

All inputs share a schema hash, meaning they were generated from the same DUT build with
the same testplan. Read `testplan.json` from the first source that has one and copy it
verbatim to the output (no deserialization needed — raw bytes copy):

```python
# In _merge_same_schema(), after writing MEMBER_SOURCES:
testplan_bytes = None
for src in sources:
    with zipfile.ZipFile(src) as zf:
        if MEMBER_TESTPLAN in zf.namelist():
            testplan_bytes = zf.read(MEMBER_TESTPLAN)
            break
if testplan_bytes is not None:
    zf_out.writestr(MEMBER_TESTPLAN, testplan_bytes)
```

The `import_timestamp` in the testplan is intentionally left as-is (it records when the plan
was first embedded, not when this merge happened).

#### Cross-schema path (`_merge_cross_schema`)

Different schemas may mean different DUTs, different testplan versions, or both. Strategy:

1. Collect all unique `(source_file, import_timestamp)` pairs from input testplans.
2. If all inputs have **identical JSON bytes** → copy verbatim to output.
3. If inputs differ in `import_timestamp` only → take the most recent (highest timestamp).
4. If inputs have **different `source_file`** values → emit a warning and omit the testplan
   from the merged output (merging incompatible DUT plans is undefined).

```python
def _merge_testplans(self, sources: list[str]) -> Optional[bytes]:
    """Return merged testplan bytes, or None with a warning if incompatible."""
    candidates = {}  # source_file → (import_timestamp, bytes)
    for src in sources:
        with zipfile.ZipFile(src) as zf:
            if MEMBER_TESTPLAN not in zf.namelist():
                continue
            raw = zf.read(MEMBER_TESTPLAN)
            d = json.loads(raw)
            sf = d.get("source_file", "")
            ts = d.get("import_timestamp", "")
            if sf not in candidates or ts > candidates[sf][0]:
                candidates[sf] = (ts, raw)
    if len(candidates) == 0:
        return None
    if len(candidates) == 1:
        return next(iter(candidates.values()))[1]
    import warnings
    warnings.warn(
        f"Merging databases with different testplans "
        f"({list(candidates)}); testplan omitted from output.",
        stacklevel=3,
    )
    return None
```

---

### 10.9 Testpoint Closure Computation

The closure computation lives in a standalone module (not inside `Testplan`) so that it can
be used without importing the scope tree:

New file: **`src/ucis/ncdb/testplan_closure.py`**

```python
from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
from typing import Optional

from ucis.history_node_kind import HistoryNodeKind
from ucis.test_status_t import TestStatusT
from .testplan import Testplan, Testpoint


class TPStatus(Enum):
    CLOSED        = "CLOSED"        # all mapped tests passed
    PARTIAL       = "PARTIAL"       # some passed, some failed
    FAILING       = "FAILING"       # all mapped tests ran and failed
    NOT_RUN       = "NOT_RUN"       # none of the mapped tests appear in the DB
    NA            = "N/A"           # testpoint intentionally unmapped
    UNIMPLEMENTED = "UNIMPLEMENTED" # tests list is empty (plan written, test not yet)


@dataclass
class TestpointResult:
    testpoint: Testpoint
    status:    TPStatus
    matched_tests: list[str]        # test names that matched from the DB
    pass_count:    int = 0
    fail_count:    int = 0


def compute_closure(testplan: Testplan, db) -> list[TestpointResult]:
    """Compute pass/fail closure for every testpoint against *db*.

    Args:
        testplan: The Testplan embedded in (or associated with) *db*.
        db:       Any UCIS database (NcdbUCIS, MemUCIS, …).

    Returns:
        One TestpointResult per testpoint, in testplan order.
    """
    # Build test-name → status lookup from history nodes (O(N_tests))
    test_status: dict[str, TestStatusT] = {}
    for node in db.historyNodes(HistoryNodeKind.TEST):
        name = node.getLogicalName()
        test_status[name] = node.getTestStatus()

    results = []
    for tp in testplan.testpoints:
        if tp.na:
            results.append(TestpointResult(tp, TPStatus.NA, []))
            continue
        if not tp.tests:
            results.append(TestpointResult(tp, TPStatus.UNIMPLEMENTED, []))
            continue

        matched, passes, fails = [], 0, 0
        for pattern in tp.tests:
            # Exact match
            if pattern in test_status:
                matched.append(pattern)
                if test_status[pattern] == TestStatusT.OK:
                    passes += 1
                else:
                    fails += 1
                continue
            # Seed-suffix strip
            import re
            stripped = re.sub(r'_\d+$', '', pattern)
            if stripped in test_status:
                matched.append(stripped)
                if test_status[stripped] == TestStatusT.OK:
                    passes += 1
                else:
                    fails += 1
                continue
            # Wildcard prefix
            if pattern.endswith('_*'):
                prefix = pattern[:-1]
                for tname, tstatus in test_status.items():
                    if tname.startswith(prefix):
                        matched.append(tname)
                        if tstatus == TestStatusT.OK:
                            passes += 1
                        else:
                            fails += 1

        if not matched:
            status = TPStatus.NOT_RUN
        elif fails == 0:
            status = TPStatus.CLOSED
        elif passes == 0:
            status = TPStatus.FAILING
        else:
            status = TPStatus.PARTIAL

        results.append(TestpointResult(tp, status, matched, passes, fails))
    return results


def stage_gate_status(results: list[TestpointResult],
                      stage: str, testplan: Testplan) -> dict:
    """Determine whether the stage gate for *stage* is met.

    A stage gate passes when ALL testpoints at that stage and all stages
    below it in the standard ordering are CLOSED (or N/A).

    Returns a dict:
        {
          "gate":    stage,
          "pass":    bool,
          "by_stage": { stage: {"total": N, "closed": N, "gaps": [...]} }
        }
    """
    _ORDER = {"V1": 0, "V2": 1, "V2S": 2, "V3": 3}
    gate_level = _ORDER.get(stage, 99)
    by_stage: dict = {}
    for r in results:
        s = r.testpoint.stage
        if _ORDER.get(s, 99) > gate_level:
            continue
        entry = by_stage.setdefault(s, {"total": 0, "closed": 0, "gaps": []})
        entry["total"] += 1
        if r.status in (TPStatus.CLOSED, TPStatus.NA):
            entry["closed"] += 1
        else:
            entry["gaps"].append(r.testpoint.name)
    gate_pass = all(e["closed"] == e["total"] for e in by_stage.values())
    return {"gate": stage, "pass": gate_pass, "by_stage": by_stage}
```

---

### 10.10 Covergroup Join

For Report C (coverage per testpoint), the join between testplan `covergroups` entries and
UCIS scope nodes uses a DFS helper:

```python
# src/ucis/ncdb/testplan_closure.py  (additional helper)

from ucis.scope_type_t import ScopeTypeT

def find_covergroup_scopes(db, cg_name: str) -> list:
    """Return all UCIS scope nodes whose name matches *cg_name* and whose
    scope type is COVERGROUP (or COVERINSTANCE).  Requires scope tree loaded.
    """
    results = []
    _CG_TYPES = {int(ScopeTypeT.COVERGROUP), int(ScopeTypeT.COVERINSTANCE)}

    def _dfs(scope):
        try:
            st = int(scope.getScopeType())
        except Exception:
            st = -1
        if st in _CG_TYPES and scope.getScopeName() == cg_name:
            results.append(scope)
        try:
            for child in scope.scopes(ScopeTypeT.ALL):
                _dfs(child)
        except Exception:
            pass

    _dfs(db)
    return results
```

**Efficiency note**: this is O(total_scopes). For repeated calls across many covergroups,
build a name → scope index once:

```python
def build_covergroup_index(db) -> dict[str, list]:
    """Build a dict mapping covergroup name → list of matching scope nodes."""
    index: dict[str, list] = {}
    _CG_TYPES = {int(ScopeTypeT.COVERGROUP), int(ScopeTypeT.COVERINSTANCE)}

    def _dfs(scope):
        try:
            if int(scope.getScopeType()) in _CG_TYPES:
                name = scope.getScopeName()
                index.setdefault(name, []).append(scope)
        except Exception:
            pass
        try:
            for child in scope.scopes(ScopeTypeT.ALL):
                _dfs(child)
        except Exception:
            pass

    _dfs(db)
    return index
```

---

### 10.11 OpenTitan Hjson Import

A convenience function converts an OpenTitan `.hjson` testplan file into a `Testplan`
object ready for embedding:

New file: **`src/ucis/ncdb/testplan_hjson.py`**

```python
"""Import an OpenTitan-format Hjson testplan into a Testplan object."""

from __future__ import annotations
import re
from datetime import datetime, timezone
from typing import Optional
from .testplan import Testplan, Testpoint, CovergroupEntry


def import_hjson(hjson_path: str,
                 substitutions: Optional[dict] = None) -> Testplan:
    """Parse *hjson_path* and return a fully resolved Testplan.

    Args:
        hjson_path:     Path to the .hjson testplan file.
        substitutions:  Dict of wildcard substitutions, e.g.
                        {"name": "uart", "intf": ["", "_jtag"]}.
                        Applied to ``tests`` lists that contain ``{key}``
                        patterns (OpenTitan wildcard expansion).
    """
    try:
        import hjson
    except ImportError:
        import json as hjson   # fallback: .hjson without comments

    with open(hjson_path) as f:
        raw = hjson.load(f)

    subs = substitutions or {}
    dut_name = raw.get("name", "")
    if dut_name and "name" not in subs:
        subs["name"] = dut_name

    tp = Testplan(
        source_file=hjson_path,
        import_timestamp=datetime.now(timezone.utc).isoformat(),
    )

    for rec in raw.get("testpoints", []):
        raw_tests = rec.get("tests", [])
        # Expand wildcards
        expanded = _expand_tests(raw_tests, subs)
        na = raw_tests == ["N/A"]
        source_template = ",".join(raw_tests) if raw_tests != expanded else ""
        tp.testpoints.append(Testpoint(
            name=rec["name"],
            stage=rec.get("stage", ""),
            desc=rec.get("desc", ""),
            tests=[] if na else expanded,
            tags=rec.get("tags", []),
            na=na,
            source_template=source_template,
        ))

    for rec in raw.get("covergroups", []):
        tp.covergroups.append(CovergroupEntry(
            name=rec["name"], desc=rec.get("desc", "")
        ))

    return tp


def _expand_tests(test_list: list[str], subs: dict) -> list[str]:
    """Expand ``{key}`` wildcards in test names using *subs*.

    If a substitution value is a list, the cartesian product is computed.
    """
    if not subs:
        return [t for t in test_list if t != "N/A"]
    results = []
    for template in test_list:
        if template == "N/A":
            continue
        expanded = _expand_template(template, subs)
        results.extend(expanded)
    return results


def _expand_template(template: str, subs: dict) -> list[str]:
    """Recursively expand a single test name template."""
    m = re.search(r'\{(\w+)\}', template)
    if not m:
        return [template]
    key = m.group(1)
    values = subs.get(key, [""])
    if isinstance(values, str):
        values = [values]
    result = []
    for v in values:
        expanded = template.replace(f"{{{key}}}", v, 1)
        result.extend(_expand_template(expanded, subs))
    return result
```

---

### 10.12 Files to Create / Modify

#### New Files

| File | Purpose |
|---|---|
| `src/ucis/ncdb/testplan.py` | `Testplan`, `Testpoint`, `CovergroupEntry` data model + serialization + query API |
| `src/ucis/ncdb/testplan_closure.py` | `compute_closure()`, `stage_gate_status()`, `find_covergroup_scopes()`, `build_covergroup_index()` |
| `src/ucis/ncdb/testplan_hjson.py` | `import_hjson()` — OpenTitan Hjson → `Testplan` converter |

#### Modified Files

| File | Change |
|---|---|
| `src/ucis/ncdb/constants.py` | Add `MEMBER_TESTPLAN = "testplan.json"` |
| `src/ucis/ncdb/ncdb_ucis.py` | Add `_loaded_testplan`, `_testplan`, `_testplan_dirty` fields; add `getTestplan()`, `setTestplan()`, `_ensure_testplan()` methods |
| `src/ucis/ncdb/ncdb_writer.py` | Write `testplan.json` if `getattr(db, '_testplan', None)` is set |
| `src/ucis/ncdb/ncdb_reader.py` | Read `testplan.json` if present, attach to returned `MemUCIS` |
| `src/ucis/ncdb/ncdb_merger.py` | Call `_merge_testplans()` in both fast and cross-schema paths; write result if non-None |

#### No UCIS interface changes

`src/ucis/ucis.py` and all non-NCDB backends (`xml/`, `sqlite/`, `mem/`) are unchanged.
The testplan feature is explicitly NCDB-native.

---

### 10.13 Usage Examples

```python
from ucis.ncdb.ncdb_ucis import NcdbUCIS
from ucis.ncdb.testplan import get_testplan
from ucis.ncdb.testplan_hjson import import_hjson
from ucis.ncdb.testplan_closure import compute_closure, stage_gate_status

# ── Embedding a testplan into a new CDB ──────────────────────────────────
db = NcdbUCIS("regression.cdb")
tp = import_hjson("hw/ip/uart/data/uart_testplan.hjson",
                  substitutions={"name": "uart", "intf": ["", "_jtag"]})
db.setTestplan(tp)
db.write("regression_with_plan.cdb")

# ── Reading back and computing closure ───────────────────────────────────
db2 = NcdbUCIS("regression_with_plan.cdb")
tp2 = db2.getTestplan()                   # lazy load; no scope tree needed

results = compute_closure(tp2, db2)       # triggers history load only
for r in results:
    print(f"{r.testpoint.name:30s}  {r.testpoint.stage}  {r.status.value}")

# ── Stage gate check ─────────────────────────────────────────────────────
gate = stage_gate_status(results, "V2", tp2)
if gate["pass"]:
    print("V2 gate: PASS")
else:
    for stage, info in gate["by_stage"].items():
        print(f"  {stage}: {info['closed']}/{info['total']} — gaps: {info['gaps']}")

# ── Works with any db that has a testplan attached ───────────────────────
tp3 = get_testplan(db)   # works for NcdbUCIS, MemUCIS, any db with _testplan

# ── Mode B: standalone testplan file cross-analyzed against an NCDB ──────
# Use this when the testplan was never embedded, or when you want to apply
# a different testplan revision against an already-built database.
from ucis.ncdb.testplan import Testplan

tp_ext = Testplan.load("hw/ip/uart/data/uart_testplan.json")

db_legacy = NcdbUCIS("old_regression.cdb")  # no embedded testplan
results_ext = compute_closure(tp_ext, db_legacy)
for r in results_ext:
    print(f"{r.testpoint.name:30s}  {r.testpoint.stage}  {r.status.value}")

# ── Mode B: save a resolved testplan to a standalone file ────────────────
tp_resolved = import_hjson("hw/ip/uart/data/uart_testplan.hjson",
                            substitutions={"name": "uart", "intf": ["", "_jtag"]})
tp_resolved.save("artifacts/uart_testplan_resolved.json")
# Later: Testplan.load("artifacts/uart_testplan_resolved.json")
```

---

### 10.14 Lazy-Load Dependency Map

```
NcdbUCIS._ensure_testplan()  ──► reads testplan.json from _zf_cache
                                  ↑ triggers _read_zip() if cache empty
                                  (no dependency on history or scopes)

compute_closure(tp, db)      ──► calls db.historyNodes()
                                  ↑ triggers _ensure_history()
                                  (no dependency on scopes)

build_covergroup_index(db)   ──► calls db.scopes()
                                  ↑ triggers _ensure_scopes()
                                  (heaviest load — only for coverage reports)
```

The testplan can be read and queried without loading either the history nodes or the scope
tree. Report A (Testpoint Closure Summary) loads only `testplan.json` + `history.json` —
the two lightest members.

---

### 10.15 Standalone Testplan Mode (Mode B) — Cross-Analysis Workflow

In Mode B the testplan is **not** stored inside the NCDB. This is the expected flow when
performing analysis between a `testplan.json` file and an NCDB:

```
Input A: uart_testplan.json      ← standalone testplan (from RTL repo, CI artifact, etc.)
Input B: regression.cdb          ← NCDB produced by simulation run (may have no embedded plan)

Step 1: tp = Testplan.load("uart_testplan.json")
Step 2: db = NcdbUCIS("regression.cdb")
Step 3: results = compute_closure(tp, db)
Step 4: gate   = stage_gate_status(results, "V2", tp)
```

#### When to use Mode B

| Scenario | Mode |
|---|---|
| Testplan is embedded at import time and travels with the CDB | A (embedded) |
| Testplan lives in RTL repo; CDB produced by CI without plan injection | B (standalone) |
| Retro-fitting plan coverage onto pre-existing legacy databases | B (standalone) |
| Comparing multiple testplan revisions against the same frozen NCDB | B (standalone) |
| Ad-hoc analysis during bring-up before a canonical plan exists | B (standalone) |
| Post-silicon debug: map chip-test results against a verification plan | B (standalone) |

#### Producing a standalone testplan file

From a raw OpenTitan Hjson file:

```python
from ucis.ncdb.testplan_hjson import import_hjson
from ucis.ncdb.testplan import Testplan

tp = import_hjson("hw/ip/uart/data/uart_testplan.hjson",
                  substitutions={"name": "uart", "intf": ["", "_jtag"]})
tp.save("artifacts/uart_testplan.json")   # save for later reuse
```

Or convert from an already-embedded plan to a standalone copy for sharing:

```python
db = NcdbUCIS("regression.cdb")
tp = db.getTestplan()
if tp:
    tp.save("artifacts/uart_testplan.json")
```

#### Selecting which testplan to use at analysis time

`compute_closure()` accepts a `Testplan` object from either source; the caller decides
the priority:

```python
def get_analysis_testplan(db, standalone_path=None):
    """Return a Testplan for analysis, preferring standalone over embedded."""
    if standalone_path:
        return Testplan.load(standalone_path)
    tp = get_testplan(db)
    if tp:
        return tp
    raise ValueError("No testplan available: provide --testplan <path> or embed one in the CDB")
```

This keeps the policy decision in the caller (CLI, script, or notebook) rather than in the
library, so both modes remain fully supported without hidden precedence rules.

---

## Part 11: Competitive Analysis — Matching and Exceeding the State of Practice

### 11.1 Industry Landscape

The three dominant commercial EDA verification management platforms and their regression reporting
capabilities are surveyed here, along with CI/CD-era test reporting tools (Allure, Grafana,
TestRail, Zephyr Scale), and 2024–2025 AI/ML trends.

#### 11.1.1 Cadence Verisium Manager (formerly vManager)

Cadence positions Verisium Manager as an MDV (Metric-Driven Verification) execution platform.

| Capability | Details |
|---|---|
| Hierarchical vPlan | Testpoints organized as a tree; each node has pass/fail/coverage status |
| Real-time coverage merge | Incremental merge visible in dashboards *during* regression |
| Failure clustering/buckets | Automated log similarity clustering → N failures → K buckets |
| Failure signature linking | Representative waveform (FSDB) linked to each bucket |
| Pass/fail trend dashboards | Per-testpoint pass rate over time; regression δ view |
| Farm utilization metrics | CPU hours, parallel job efficiency |
| Owner/priority on testpoints | Engineer assignment and priority fields |
| Jenkins/GitLab CI integration | Pipeline plugins; automatic post-regression summaries |
| REST API + Python API | Programmatic report generation |
| Requirements traceability | Jira, Jama, IBM DOORS via OSLC adapters |
| Email summary reports | Configurable post-regression email with key metrics |
| Waiver management | Mark bins "not applicable" with rationale; tracked separately |
| AI-assisted triage | ML clustering; root-cause suggestion from log patterns |

Key insight: Cadence's differentiator is *live* coverage merging (see coverage grow in real time as
tests complete) and tightly coupled waveform debug from failure buckets.

#### 11.1.2 Synopsys VC ExecMan + VSO.ai

VC ExecMan is the regression orchestration layer. VSO.ai is the AI analytics overlay introduced
in 2023–2024.

| Capability | Details |
|---|---|
| Hierarchical Verification Plan (HVP) | Tree of goals with coverage-linked metrics |
| Per-test coverage contribution | Unique bins hit by each test; identifies redundant tests |
| Minimum test set (MTS) computation | Greedy set cover to minimize regression time at target coverage |
| Unreachable coverage detection | Constraint-conflict or dead-code identification |
| ML-based test prioritization | Rank tests by predicted coverage ROI; 2–10× regression speedup (NVIDIA, AMD claims) |
| Targeted rerun scheduling | Automatically reruns failed/low-coverage tests with adjusted seeds |
| Predictive closure timeline | "At current rate, coverage closure in N days" |
| Phase-aware analytics | Testbench bring-up → bug hunting → signoff: different optimization objectives |
| SQL API for custom reports | ad-hoc queries against the regression DB |
| Coverage root cause analysis (auto) | Pinpoints why bins are uncovered; generates actionable hints |
| Integration with Verdi/waveforms | Failure → waveform handoff |
| Customer-reported speedup | 2–10× regression reduction; 10× faster coverage hole closure |

Key insight: VSO.ai's *minimum test set* and *per-test coverage contribution* are the most
technically differentiated features. They require per-test coverage bins (contrib data), which
NCDB already stores in `contrib/*.bin`.

#### 11.1.3 Siemens Questa VRM + Verification IQ

Siemens uses an RMDB (Regression Management DB) as the central store and Verification IQ as the
analytics UI layer.

| Capability | Details |
|---|---|
| Hierarchical testplan (UCDB-backed) | Testplan integrated into UCDB as first-class objects |
| Testplan Author | GUI-assisted testplan creation with coverage scope linking |
| OSLC integration | Polarion, Jama, Jira bi-directional traceability |
| Functional safety traceability | ISO 26262, DO-254 reports; audit trails with signoff stamps |
| Live UCDB merge during regression | Coverage visible before regression completes |
| ML-assisted failure bucketing | Log analysis + assertion clustering |
| Web dashboards | Executive and engineer views; drilldown |
| Regression delta report | Compares current vs previous regression; new failures highlighted |
| Closure forecasting | Trend-based prediction |
| Email/Slack notifications | Configurable alert rules |
| Cost/schedule tracking | Test budget vs actuals by stage |

Key insight: Siemens leads on *functional safety compliance reporting* (ISO 26262) and on
embedding testplan data inside the UCDB itself rather than a sidecar file — closest to our
`testplan.json` ZIP member design.

#### 11.1.4 CI/CD Era Tools (Allure, Grafana, TestRail, Zephyr Scale)

These tools are prominent in software verification but are increasingly used in hardware projects
running on CI infrastructure.

| Tool | Strengths | Gaps vs EDA needs |
|---|---|---|
| Allure Report | Rich HTML output; CI integration; flaky test identification; trend view | No coverage metrics; no seed/testpoint concept |
| Grafana | Fully custom dashboards; alerting; time-series metrics | Requires custom data pipeline; no EDA-native data |
| TestRail | Full test case management; requirements traceability; compliance reports | No coverage metrics; no simulation-native integration |
| Zephyr Scale | Jira-native; agile sprint alignment; regression cycles | No coverage metrics; weak EDA toolchain integration |

Key patterns across all CI tools: pass/fail rate over time, flaky test detection, trend
dashboards, and CI pipeline integration are table-stakes features.

---

### 11.2 Feature Gap Analysis

For each feature class, we assess: **Present in our design**, **Absent (gap)**, or **Not
applicable**.

| Feature | Commercial EDA | Our Design (Parts 1–10) | Gap? |
|---|---|---|---|
| Testplan hierarchy | ✓ (all three) | ✓ Part 9.3 / 10.2 | No |
| Coverage per testpoint | ✓ (all three) | ✓ Report C (9.4) | No |
| Stage gate readiness | ✓ (vPlan stages) | ✓ Report B (9.4) + 10.9 | No |
| Testpoint pass rate trend (history) | ✓ | ✓ Report F (9.4) via history | No |
| Regression delta report | ✓ (all three) | ✓ Report D (9.4) | No |
| Historical stage progression | ✓ | ✓ Report E (9.4) | No |
| Per-test coverage contribution | ✓ VSO.ai, vManager | **Partial** — contrib/*.bin exists, no compute_contribution() API | **Gap** |
| Minimum test set computation | ✓ VSO.ai | **Absent** | **Gap** |
| Failure clustering/buckets | ✓ (all three) | **Absent** | **Gap** |
| Failure-to-waveform linking | ✓ vManager, VRM | Absent (out of pyucis scope) | N/A |
| Predictive closure timeline | ✓ VSO.ai, VRM | **Absent** | **Gap** |
| Unreachable bin detection | ✓ VSO.ai | Absent (simulator-level) | N/A |
| Waiver management | ✓ (all three) | **Absent** | **Gap** |
| Real-time/live merge | ✓ vManager, VRM | Absent (batch only) | Low priority |
| Requirements ALM traceability | ✓ (all three) | **Absent** | **Gap** |
| Functional safety (ISO 26262) | ✓ Siemens | **Absent** | **Gap** |
| ML-based test prioritization | ✓ VSO.ai | **Absent** | **Gap** |
| Targeted rerun scheduling | ✓ VSO.ai, ExecMan | Absent (scheduler is external) | N/A |
| CI/CD pipeline integration | ✓ (all three) | **Absent** | **Gap** |
| Flaky test identification | ✓ + CI tools | ✓ flake_score in history design | No |
| CUSUM change-point detection | **Absent** in all three | ✓ Part 6 | **Exceed** |
| Seed-correlated failure analytics | **Absent** | ✓ seed_id in history buckets | **Exceed** |
| Per-test coverage provenance audit | **Absent** | ✓ squash_log.bin | **Exceed** |
| Confidence-weighted closure | **Absent** | ✓ flake_score gates signoff | **Exceed** |
| Open, inspectable format | **Absent** | ✓ ZIP+JSON; no license required | **Exceed** |
| Cross-simulator UCIS interop | Proprietary formats | ✓ standard UCIS API | **Exceed** |
| Stage gate + flake score integration | **Absent** | ✓ combined in compute_closure() | **Exceed** |

---

### 11.3 Features to Add to Match Commercial Tools

The following features are absent from our design but are expected by professional users who
have used commercial tools. They should be added to the design and eventually implemented.

#### 11.3.1 Per-Test Coverage Contribution Report (Report I)

**What**: Rank all tests in a regression by the number of *unique* coverage bins they contribute
— bins that no other test hit. Identify redundant tests (zero unique contribution).

**How (in NCDB)**: `contrib/*.bin` stores per-test bin hit vectors. A set-cover query over these
vectors yields unique contribution per test. The result is a ranked list suitable for regression
pruning.

```
Report I: Per-Test Coverage Contribution

Test                  Total Bins Hit   Unique Bins   Redundant?
--------------------  ---------------  ------------  ----------
smoke_basic_0          12840            3210          No
directed_arith_0        8901             401          No
directed_arith_1        8820               0          YES (fully covered by directed_arith_0)
rand_full_0            45000            8100          No
...

Suggested pruning: remove 14 tests with 0 unique contribution → save ~12% regression time
```

**Design addition**: `compute_contribution(db)` function in `testplan_closure.py` that iterates
`contrib/*.bin` and computes unique bins per test. Returns `List[TestContribution]` with
`test_name`, `total_bins`, `unique_bins`, `unique_fraction`.

#### 11.3.2 Minimum Test Set Report (Report J)

**What**: Given a target coverage threshold (e.g., 95%), compute the smallest subset of tests
that achieves that threshold. This is the set-cover problem; a greedy approximation is O(n·m)
in tests × bins.

**How**: Greedy algorithm: repeatedly select the test with the highest unique-contribution count
on remaining uncovered bins until the threshold is met or no further coverage is possible.

```
Report J: Minimum Test Set for 95% Closure

  Original regression: 420 tests, 18.2 CPU-hours
  Minimum test set:     87 tests,  4.1 CPU-hours (77% reduction)

  Included tests (top 10 by contribution):
    rand_full_0          → 12.4% of total bins (unique)
    rand_full_1          →  6.1%
    directed_fsm_0       →  4.8%
    ...

  Coverage achieved: 95.3%  (target: 95.0%)
  Excluded: 333 tests with <0.01% unique contribution each
```

**Design addition**: `compute_minimum_test_set(db, target_coverage=0.95)` in
`testplan_closure.py`. Returns `MinimumTestSet` with `included_tests`, `excluded_tests`,
`achieved_coverage`, `cpu_hours_saved`.

#### 11.3.3 Waiver Management (ZIP member `waivers.json`)

**What**: Coverage bins that are intentionally uncovered should be marked with a rationale
and approver, and excluded from closure calculations. This is required for ISO 26262 and
other compliance workflows.

**Format**: New ZIP member `waivers.json` with the following schema:

```json
{
  "schema_version": 1,
  "waivers": [
    {
      "id": "W-001",
      "scope_pattern": "top.dut.arith.covergroup_t.*",
      "bin_pattern": "overflow_corner",
      "rationale": "Hardware prevents this condition by design (see spec §3.4.2)",
      "approver": "jane.doe@example.com",
      "approved_at": "2024-11-15",
      "expires_at": null,
      "status": "active"
    }
  ]
}
```

**Impact on closure**: `compute_closure()` accepts an optional `waivers: List[Waiver]` argument.
Waived bins are excluded from denominator and reported separately in all closure metrics.

**New file**: `src/ucis/ncdb/waivers.py` — `Waiver` dataclass, `WaiverSet.load()`,
`WaiverSet.save()`, `WaiverSet.matches_scope(scope_path, bin_name)`.

**NcdbUCIS extension**: Add `getWaivers()` / `setWaivers()` analogous to testplan.

#### 11.3.4 Predictive Closure Timeline (Report K)

**What**: Given historical coverage growth trend over successive regressions, estimate when
coverage will reach the target if the current rate is maintained.

**How**: Fit a logarithmic or asymptotic curve to the (regression_number, coverage_pct) series
stored in history. Extrapolate to the target coverage. Report confidence interval.

```
Report K: Predictive Closure Timeline

  Current coverage:  78.4% (target: 95.0%)
  Regressions so far: 34
  Trend model: logarithmic fit  R²=0.94

  Projection (95% CI):
    Optimistic (upper CI):  +8 regressions
    Median estimate:        +14 regressions
    Pessimistic (lower CI): +23 regressions

  Warning: coverage growth rate has been declining since regression #28
  (CUSUM change point detected; see Section 6 change-point analysis).
```

**Design addition**: `compute_closure_forecast(history_series, target=0.95)` function in
`testplan_closure.py`. Takes a `List[(regression_id, coverage_pct)]`, returns `Forecast`
with `median_regressions_to_target`, `ci_lower`, `ci_upper`, `model_fit_r2`, `warning`.

#### 11.3.5 CI/CD Integration — JUnit XML and GitHub Annotations Export

**What**: Export regression results in JUnit XML format (testpoint pass/fail as test cases)
so that CI/CD systems (GitHub Actions, GitLab CI, Jenkins) can display native pass/fail
annotations and trend graphs.

**How**: Map each testpoint to a JUnit `<testcase>`. Stage → `<testsuite>`. Failures → `<failure>`
with message. Duration → `time=` attribute.

**Design addition**: `testplan_export.py` with:
- `export_junit_xml(results: List[TestpointResult], output_path: str)` — writes JUnit XML
- `export_github_annotations(results)` — writes GitHub Actions `::error::` / `::warning::` lines
- `export_summary_markdown(results, history)` — writes GitHub Actions Job Summary markdown

#### 11.3.6 Requirements Traceability Link (ALM Integration)

**What**: Each testpoint can carry a link to an external ALM item (Jira issue, Polarion
requirement, GitHub issue). The end-of-regression report then includes traceability from
coverage point → testpoint → requirement → sign-off status.

**How**: Add optional `requirements` field to `Testpoint` dataclass:

```python
@dataclass
class RequirementLink:
    system: str          # "jira", "github", "polarion", "jama"
    project: str         # "PROJ"
    item_id: str         # "PROJ-1234"
    url: str             # full URL (optional)

@dataclass
class Testpoint:
    ...
    requirements: List[RequirementLink] = field(default_factory=list)
```

Report output: traceability matrix (requirement → testpoints that cover it → closure status).
No live sync with ALM tools needed for v1; links are maintained in `testplan.json`.

#### 11.3.7 Functional Safety Traceability Report (Report L)

**What**: ISO 26262 and DO-254 require a documented claim that each safety requirement has
been verified. Generate a traceability matrix in CSV or PDF-friendly form.

```
Report L: Functional Safety Traceability Matrix

Requirement ID  Description                   Testpoints          Status    Evidence
--------------  ----------------------------  ------------------  --------  --------
ISO-FUNC-001    Overflow detection            tp_arith_overflow   CLOSED    merged.cdb@reg_042
ISO-FUNC-002    Reset recovery < 3 cycles     tp_reset_timing     OPEN      —
...
```

**Design addition**: `export_safety_matrix(results, waivers, output_path, format="csv")`
in `testplan_export.py`.

---

### 11.4 Opportunities to Exceed Commercial Tools

The following capabilities are *absent from all three commercial platforms* or are only
partially implemented. They represent genuine differentiation opportunities.

#### 11.4.1 Seed-Correlated Failure Analytics

**What commercial tools do**: Record pass/fail per run. Some expose the seed value as metadata.
None correlate *which seeds systematically produce failures* vs. which seeds expose rare bugs.

**What we uniquely offer**: The binary history design (Part 2) stores `seed_id` per run as a
32-bit field in the bucket record. This enables:

- **Seed reliability score**: For a given test, what fraction of seeds result in pass? A test
  passing on seed 0 but failing on seeds > 1e8 indicates a seed-dependent bug.
- **Seed range heat-map**: Bin seeds by value range; identify if certain seed regions reliably
  expose a failure. (EDA-unique: commercial tools do not expose this.)
- **Seed reuse recommendation**: For signoff regressions, prefer seeds with historically high
  pass rates for "stable validation", plus seeds in the high-failure-rate range for "stress
  regression".

**Report M: Seed Reliability Analysis**
```
Test: rand_arith_*

Seed range [0, 1M]:       pass rate 99.2% (stable)
Seed range [1M, 10M]:     pass rate 94.1% (moderate stress)
Seed range [100M, 200M]:  pass rate 71.3% ← HIGH FAILURE ZONE

Recommended signoff seeds: {42, 1234, 9999}  (historically 100% pass)
Stress regression seeds:   {100000001, 100500000, 101234567} (expose most bugs)
```

#### 11.4.2 CUSUM Change-Point Detection with RTL Commit Correlation

**What commercial tools do**: Show coverage trend over time. None apply statistical
process control (SPC) to detect *when* coverage growth stalled or *when* test reliability
degraded.

**What we uniquely offer** (already in Part 6 design):
- CUSUM algorithm applied per-testpoint pass rate series
- Change-point mapped to regression number → can be correlated with RTL commit history
- Alert: "Test X reliability dropped at regression #47; closest RTL commit: [hash]"

This enables *root-cause attribution at the RTL commit level* without any ML, purely from
the history database. No commercial tool offers this for individual testpoint reliability.

#### 11.4.3 Confidence-Weighted Coverage Closure

**What commercial tools do**: Report coverage as a simple percentage. A bin hit by a test
that has a 30% pass rate is counted the same as a bin hit by a 100%-reliable test.

**What we uniquely offer**: Weight coverage by the reliability of the tests that hit it.

```
Standard closure:   92.4%
Confidence-weighted closure: 87.1%  ← bins hit only by flaky tests are discounted

Confidence-weighted closure is recommended for signoff claims.
Bins with weight < 0.5 (hit only by tests with flake_score > 0.5):
  top.dut.fsm.state_machine_t → state_c_to_d: weight=0.31 (unreliable)
```

This gives a *conservative* closure claim that accounts for test reliability. Commercial
tools have no equivalent concept. It requires both coverage data and historical pass-rate
data — exactly what our merged NCDB provides.

#### 11.4.4 Coverage Provenance Audit Trail

**What commercial tools do**: Show current coverage. No tool records *which regression
contributed which bins* in the merged database, and with which squash policy.

**What we uniquely offer** (Part 3/4 design): `squash_log.bin` records the exact merge
parameters (squash policy, threshold, regression IDs) used to build each version of
`counts.bin`. An auditor can answer:

> "This bin was closed in regression #38 with squash policy `threshold=3,window=10`; if we
> applied a stricter policy (`threshold=5`), it would still be closed (hit 7 times)."

This is unique to our design and directly supports signoff claims in compliance workflows.

#### 11.4.5 Open Format — No Vendor Lock-In

**What commercial tools do**: Store data in proprietary binary databases. Customers cannot
access data outside the vendor's tools. Tool upgrades may break existing data.

**What we uniquely offer**:
- Everything is in a ZIP file with JSON metadata and documented binary layouts.
- Any Python program can read and process the data with zero licensing cost.
- Users can write custom reports, scripts, and integrations without a vendor API contract.
- The UCIS API layer means data is portable across simulators (VCS, Xcelium, Riviera-PRO,
  Verilator) — commercial tools are all simulator-specific.

#### 11.4.6 Stage Gate + Flake Score Integration

**What commercial tools do**: V-plan stages are pass/fail based on count of tests run and
static coverage thresholds. Flaky tests are identified separately, never integrated into
gate criteria.

**What we uniquely offer**: `compute_closure()` (Part 10.9) returns a `TPStatus` that
incorporates both the testpoint's coverage metric and the flake_score of the tests that
exercised it. A stage gate can require not just coverage but *reliable* coverage:

```python
gate_V2 = stage_gate_status(
    results, stage="V2", testplan=tp,
    require_flake_score_below=0.2,   # gate fails if covering tests are unreliable
    require_coverage_pct=90.0
)
```

No commercial tool integrates test reliability into stage gate logic.

---

### 11.5 Summary Comparison Table

| Dimension | Cadence Verisium | Synopsys VSO.ai | Siemens VRM/VIQ | **PyUCIS (our design)** |
|---|---|---|---|---|
| Testplan hierarchy | ✓ | ✓ | ✓ | ✓ |
| Coverage per testpoint | ✓ | ✓ | ✓ | ✓ |
| Stage gate | ✓ | ✓ | ✓ | ✓ |
| Testpoint trend (history) | ✓ | ✓ | ✓ | ✓ |
| Regression delta | ✓ | ✓ | ✓ | ✓ |
| Failure clustering | ✓ | ✓ | ✓ | ✗ (gap) |
| Per-test contribution ranking | ✓ | ✓ VSO.ai | ✓ | ✗→ **add** |
| Minimum test set | ✗ | ✓ VSO.ai | ✗ | ✗→ **add** |
| Predictive closure timeline | ✗ | ✓ | ✓ | ✗→ **add** |
| Waiver management | ✓ | ✓ | ✓ | ✗→ **add** |
| ALM requirements traceability | ✓ | ✓ | ✓ OSLC | ✗→ **add (links only)** |
| ISO 26262 safety reports | ✗ | ✗ | ✓ | ✗→ **add (export only)** |
| CI/CD JUnit export | ✗ | ✗ | ✗ | ✗→ **add** |
| Live/incremental merge | ✓ | ✓ | ✓ | ✗ (low priority) |
| CUSUM change-point detection | ✗ | ✗ | ✗ | ✓ **unique** |
| Seed-correlated failure analytics | ✗ | ✗ | ✗ | ✓ **unique** |
| Confidence-weighted closure | ✗ | ✗ | ✗ | ✓ **unique** |
| Coverage provenance audit trail | ✗ | ✗ | ✗ | ✓ **unique** |
| Stage gate + flake score | ✗ | ✗ | ✗ | ✓ **unique** |
| Open format / no lock-in | ✗ | ✗ | ✗ | ✓ **unique** |
| Cross-simulator UCIS portability | ✗ | ✗ | ✗ | ✓ **unique** |
| Zero license cost | ✗ | ✗ | ✗ | ✓ **unique** |

---

### 11.6 Revised Report Catalog

Combining the original 8 reports (Part 9.4) with new reports from the competitive analysis:

| ID | Name | Source Data | Priority |
|---|---|---|---|
| A | Testpoint Closure Summary | testplan + current UCIS | P0 |
| B | Stage Gate Readiness | testplan + current UCIS | P0 |
| C | Coverage per Testpoint | testplan + covergroup scopes | P0 |
| D | Regression Delta | current vs previous UCIS | P0 |
| E | Historical Stage Progression | history + testplan | P1 |
| F | Testpoint Reliability (flake rate) | history + testplan | P1 |
| G | Unexercised Covergroup Report | current UCIS + testplan | P1 |
| H | Test Budget by Stage | testplan (counts/weights) | P2 |
| I | Per-Test Coverage Contribution | contrib/*.bin | P1 |
| J | Minimum Test Set | contrib/*.bin + target | P2 |
| K | Predictive Closure Timeline | history (coverage series) | P2 |
| L | Functional Safety Traceability Matrix | testplan + requirements links | P2 |
| M | Seed Reliability Analysis | history (seed_id series) | P2 |

P0 = essential for v1; P1 = high value, implement in v1 if time allows; P2 = future work.

---

## References

- Atlassian "Flakinator": https://www.atlassian.com/blog/atlassian-engineering/taming-test-flakiness-how-we-built-a-scalable-tool-to-detect-and-manage-flaky-tests
- Google flaky test mitigation: https://talent500.com/blog/google-flaky-test-mitigation-strategies/
- Cadence Verisium Manager: https://www.cadence.com/en_US/home/tools/system-design-and-verification/ai-driven-verification/verisium-manager.html
- Synopsys VC ExecMan: https://www.synopsys.com/verification/soc-verification-automation/vc-execution-manager.html
- Synopsys VSO.ai: https://www.synopsys.com/ai/ai-powered-eda/vso-ai.html
- Siemens Questa VRM + Verification IQ: https://eda.sw.siemens.com/en-US/eda/questa/vrm/
- Seed Selector algorithm: https://link.springer.com/chapter/10.1007/978-3-031-53960-2_22 (42%+ regression speedup via seed value ranking)
- Time series columnar encoding: https://www.vldb.org/pvldb/vol15/p2148-song.pdf
- CUSUM control charts: standard statistical process control literature
- OpenTitan testplanner: https://opentitan.org/book/util/dvsim/doc/testplanner.html
- UCIS 1.0 LRM: Section 4.3 (History Nodes), Table 4-2 (History Node Types), Table 4-3 (Pre-defined Attributes)
- JUnit XML schema: https://github.com/testmoapp/junitxml
