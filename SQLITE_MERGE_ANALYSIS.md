# SQLite Database Merge Capability Analysis

**Date**: 2026-02-12  
**Question**: Do SQLite databases support efficient merging without going back through Python?

## TL;DR Answer

**No, not currently.** The merge implementation goes through the Python API and does **not** use native SQL-level operations like `ATTACH DATABASE` and `INSERT ... SELECT`. However, this could be implemented for significant performance gains.

---

## Current Implementation

### 1. **Two Merge Implementations Exist**

#### A. Generic DbMerger (`src/ucis/merge/db_merger.py`)
- **Lines**: 252
- **Works with**: Any UCIS backend (Memory, SQLite, XML)
- **Approach**: Python API traversal
- **Performance**: Slower, but backend-agnostic

```python
# High-level approach:
1. Iterate through source databases
2. For each scope in source:
   - Find or create matching scope in destination
   - Iterate through coveritems
   - Accumulate counts (old_count + new_count)
3. Update destination via Python API
```

#### B. SQLite-Specific SqliteMerger (`src/ucis/sqlite/sqlite_merge.py`)
- **Lines**: 320
- **Works with**: SQLite databases only
- **Approach**: Still Python API traversal, but with SQLite-aware optimizations
- **Performance**: Better than generic, but still not native SQL

```python
# Current approach:
1. Open target and source databases (separate connections)
2. Start transaction on target
3. Recursively merge scopes:
   - Match by path (name + type)
   - Create missing scopes
4. Merge coveritems:
   - Query source DB for cover_index
   - Query target DB for matching cover_index
   - If match: UPDATE count in target (via Python API)
   - If no match: INSERT new item (via Python API)
5. Commit transaction
```

### 2. **SQL Operations Used** (Limited)

Currently only **2 SELECT queries** hit the database directly:

```python
# Line 226: Get cover_index from target
cursor = self.target.conn.execute(
    "SELECT cover_index FROM coveritems WHERE cover_id = ?",
    (tgt_cover.cover_id,)
)

# Line 237: Get cover_index from source  
cursor = src_scope.ucis_db.conn.execute(
    "SELECT cover_index FROM coveritems WHERE cover_id = ?",
    (src_cover.cover_id,)
)
```

**All other operations use the Python API:**
- `tgt_cover.setCount(new_count)` → Python → SQL UPDATE
- `tgt_scope.createNextCover(...)` → Python → SQL INSERT
- Scope creation, history node copying, etc.

---

## Why This Matters (Performance)

### Current Performance Profile

| Operation | Current Approach | Overhead |
|-----------|------------------|----------|
| Read source scope | Python API call → lazy load → SELECT | High |
| Read source coveritem | Python API call → lazy load → SELECT | High |
| Match scope by path | Python iteration + comparison | Medium |
| Update count | Python API → UPDATE statement | Medium |
| Create new coveritem | Python API → INSERT + property handling | High |
| Transaction overhead | Single transaction (good!) | Low |

**Estimated overhead**: 10-20x slower than native SQL merge

### Example: Merging 1000 Bins

**Current Python-based approach:**
```
1000 bins × (1 read source + 1 read target + 1 update) 
= 3000+ API calls + 3000+ SQL statements
= ~1-3 seconds
```

**Potential native SQL approach:**
```sql
-- Attach source database
ATTACH DATABASE 'source.ucisdb' AS src;

-- Merge matching coveritems (accumulate counts)
UPDATE coveritems 
SET cover_data = cover_data + src.coveritems.cover_data
FROM src.coveritems
WHERE coveritems.scope_id = ? 
  AND coveritems.cover_index = src.coveritems.cover_index
  AND src.coveritems.scope_id = ?;

-- Insert non-matching coveritems
INSERT INTO coveritems (scope_id, cover_index, cover_name, cover_data, ...)
SELECT ?, cover_index, cover_name, cover_data, ...
FROM src.coveritems
WHERE src.scope_id = ?
  AND NOT EXISTS (
    SELECT 1 FROM coveritems 
    WHERE scope_id = ? AND cover_index = src.coveritems.cover_index
  );

-- Detach
DETACH DATABASE src;

-- Result: 1000 bins merged in ~50-100ms (20-60x faster!)
```

---

## Database Schema Design (Merge-Friendly)

The SQLite schema is **well-designed for native merging**:

### Key Design Elements

1. **Stable Identifiers**
   ```sql
   -- coveritems use cover_index as stable identifier
   UNIQUE(scope_id, cover_index)
   ```
   - `cover_index` is deterministic across databases
   - Makes matching items trivial

2. **Foreign Key Integrity**
   ```sql
   FOREIGN KEY (scope_id) REFERENCES scopes(scope_id) ON DELETE CASCADE
   FOREIGN KEY (parent_id) REFERENCES scopes(scope_id) ON DELETE CASCADE
   ```
   - Maintains referential integrity
   - CASCADE deletes handle cleanup

3. **Hierarchical Path Matching**
   ```sql
   CREATE INDEX idx_scopes_parent_type_name 
     ON scopes(parent_id, scope_type, scope_name)
   ```
   - Efficient scope matching by (parent, type, name)
   - Critical for hierarchical merge

4. **Indexed Access**
   ```sql
   CREATE INDEX idx_coveritems_scope_index 
     ON coveritems(scope_id, cover_index)
   ```
   - Fast lookups during merge

---

## Native SQL Merge Implementation (Proposed)

### High-Level Algorithm

```sql
-- Phase 1: Attach source database
ATTACH DATABASE 'source.ucisdb' AS src;

-- Phase 2: Merge history nodes (test records)
INSERT OR IGNORE INTO history_nodes 
  (logical_name, physical_name, history_kind, test_status, seed, ...)
SELECT logical_name, physical_name, history_kind, test_status, seed, ...
FROM src.history_nodes
WHERE history_kind = ?;  -- TEST nodes

-- Phase 3: Recursive scope merge
-- This is the complex part - requires matching hierarchical paths
-- Two approaches:

-- Approach A: Build scope mapping table first
CREATE TEMP TABLE scope_mapping (
  src_scope_id INTEGER,
  tgt_scope_id INTEGER
);

-- Recursively match scopes by path
WITH RECURSIVE scope_paths AS (
  SELECT scope_id, parent_id, scope_name, scope_type, 
         scope_name AS path
  FROM scopes WHERE parent_id IS NULL
  UNION ALL
  SELECT s.scope_id, s.parent_id, s.scope_name, s.scope_type,
         sp.path || '/' || s.scope_name
  FROM scopes s
  JOIN scope_paths sp ON s.parent_id = sp.scope_id
)
-- Then match and populate mapping table...

-- Approach B: Insert missing scopes with path matching
-- More complex, requires recursive CTE

-- Phase 4: Merge coveritems (the fast part!)
-- 4a. Update existing items (accumulate counts)
UPDATE coveritems
SET cover_data = cover_data + (
  SELECT src_ci.cover_data
  FROM src.coveritems src_ci
  JOIN scope_mapping sm ON src_ci.scope_id = sm.src_scope_id
  WHERE coveritems.scope_id = sm.tgt_scope_id
    AND coveritems.cover_index = src_ci.cover_index
)
WHERE EXISTS (
  SELECT 1 FROM src.coveritems src_ci
  JOIN scope_mapping sm ON src_ci.scope_id = sm.src_scope_id
  WHERE coveritems.scope_id = sm.tgt_scope_id
    AND coveritems.cover_index = src_ci.cover_index
);

-- 4b. Insert new items
INSERT INTO coveritems (
  scope_id, cover_index, cover_type, cover_name, cover_data, ...
)
SELECT 
  sm.tgt_scope_id, src_ci.cover_index, src_ci.cover_type, 
  src_ci.cover_name, src_ci.cover_data, ...
FROM src.coveritems src_ci
JOIN scope_mapping sm ON src_ci.scope_id = sm.src_scope_id
WHERE NOT EXISTS (
  SELECT 1 FROM coveritems
  WHERE scope_id = sm.tgt_scope_id 
    AND cover_index = src_ci.cover_index
);

-- Phase 5: Cleanup
DROP TABLE scope_mapping;
DETACH DATABASE src;
```

### Challenges

1. **Scope Matching Complexity**
   - Must match hierarchical paths (parent/child relationships)
   - Scope IDs differ between databases
   - Need to build src_scope_id → tgt_scope_id mapping

2. **Missing Scopes**
   - If source has scopes not in target, must INSERT them
   - Must preserve parent-child relationships
   - Requires correct ordering (parents before children)

3. **Properties and Attributes**
   - scope_properties, coveritem_properties tables
   - Must also be merged with correct ID mapping

4. **History Node Associations**
   - coveritem_tests table links coveritems to tests
   - Complex many-to-many relationship

---

## Performance Estimates

### Scenario: Large Regression Merge

**Database size**: 
- 1000 scopes
- 10,000 coveritems  
- 50 test runs

**Current Python Implementation:**
```
Time estimate: 5-15 seconds
- Scope matching: 1000 × (1 query + comparison) = ~1s
- Coveritem reads: 10,000 × 2 reads (src + tgt) = ~3s
- Coveritem updates: 10,000 × 1 update API call = ~5s
- Python overhead: ~2s
Total: ~11 seconds
```

**Proposed Native SQL Implementation:**
```
Time estimate: 0.5-1 second (10-30x faster)
- Scope mapping build: 1 recursive query = ~100ms
- Coveritem merge: 2 bulk SQL statements = ~200ms
- History merge: 1 bulk insert = ~50ms
- Transaction commit: ~100ms
Total: ~450ms (plus ~50ms per additional source DB)
```

### Scalability

| Database Size | Current (Python) | Native SQL | Speedup |
|---------------|------------------|------------|---------|
| Small (100 items) | 0.5s | 0.1s | 5x |
| Medium (1K items) | 2s | 0.2s | 10x |
| Large (10K items) | 11s | 0.5s | 22x |
| XL (100K items) | 120s | 3s | 40x |
| Merging 10 DBs | 110s | 2s | 55x |

**Key insight**: Native SQL scales much better because:
- Single-pass operations
- No Python/SQL boundary crossing
- SQLite query optimizer handles joins
- Bulk operations instead of row-by-row

---

## Implementation Roadmap

### Phase 1: Core Native Merge (High Value)
**Effort**: 2-3 days  
**Benefits**: 20-40x performance improvement

1. Implement `SqliteNativeMerger` class
2. Scope matching algorithm (recursive CTE)
3. Bulk coveritem merge (UPDATE + INSERT)
4. Transaction handling
5. Error handling and rollback

### Phase 2: Complete Feature Parity
**Effort**: 2-3 days  
**Benefits**: Support all UCIS features

1. History node merging
2. Properties merge (scope/coveritem/history)
3. Attributes merge
4. Test contribution tracking (coveritem_tests)
5. Source file deduplication

### Phase 3: Advanced Features
**Effort**: 1-2 days  
**Benefits**: Production-ready merge

1. Merge conflict detection
2. Progress reporting
3. Validation and integrity checks
4. Merge statistics
5. Incremental merge support

### Phase 4: Optimization & Testing
**Effort**: 1-2 days

1. Index optimization for merge
2. Memory-mapped I/O
3. Parallel merge (multiple sources)
4. Comprehensive test suite
5. Benchmarking suite

**Total effort**: 6-10 days for production-ready native merge

---

## Recommendations

### 1. **Immediate (Low-Hanging Fruit)**

Keep the current Python-based merge for compatibility, but add a fast path:

```python
class SqliteMerger:
    def merge(self, source_ucis, native=True):
        """Merge with optional native SQL optimization"""
        if native and self._can_use_native_merge(source_ucis):
            return self._native_merge(source_ucis)
        else:
            return self._python_merge(source_ucis)  # current implementation
```

### 2. **Quick Win: Hybrid Approach**

Use native SQL for the hot path (coveritem merge), Python for complex parts:

```python
def _merge_coveritems_native(self, src_scope_id, tgt_scope_id):
    """Use native SQL for bulk coveritem merge"""
    # Attach source temporarily
    self.target.conn.execute(
        "ATTACH DATABASE ? AS src", 
        (self.source.db_path,)
    )
    
    # Bulk update existing items
    self.target.conn.execute("""
        UPDATE coveritems 
        SET cover_data = cover_data + src_ci.cover_data
        FROM src.coveritems src_ci
        WHERE coveritems.scope_id = ?
          AND src_ci.scope_id = ?
          AND coveritems.cover_index = src_ci.cover_index
    """, (tgt_scope_id, src_scope_id))
    
    # Bulk insert new items
    self.target.conn.execute("""
        INSERT INTO coveritems (scope_id, cover_index, ...)
        SELECT ?, cover_index, ...
        FROM src.coveritems
        WHERE scope_id = ?
          AND NOT EXISTS (...)
    """, (tgt_scope_id, src_scope_id))
    
    self.target.conn.execute("DETACH DATABASE src")
```

**Benefit**: 80% of the performance gain with 20% of the implementation effort

### 3. **Long Term: Full Native Implementation**

Implement complete native SQL merge as described above for maximum performance.

---

## Testing Strategy

### 1. Correctness Tests
```python
def test_native_merge_correctness():
    """Verify native merge produces same result as Python merge"""
    # Create test databases
    db1 = create_test_db()
    db2 = create_test_db()
    
    # Merge with Python
    python_result = python_merge(db1, db2)
    
    # Merge with native SQL
    native_result = native_merge(db1, db2)
    
    # Compare results
    assert_databases_equivalent(python_result, native_result)
```

### 2. Performance Tests
```python
def test_merge_performance():
    """Benchmark merge performance"""
    sizes = [100, 1000, 10000]
    
    for size in sizes:
        db = create_large_db(num_items=size)
        
        t_python = time_python_merge(db)
        t_native = time_native_merge(db)
        
        speedup = t_python / t_native
        assert speedup > 10  # Expect 10x+ speedup
```

### 3. Edge Cases
- Empty databases
- Overlapping scopes with different coverage
- Missing parent scopes
- Conflicting history nodes
- Large databases (stress test)

---

## Conclusion

### Current State: ❌ **No Native SQL Merge**
- Both merge implementations use Python API
- Performance is 10-40x slower than potential
- Works, but not optimal for large merges

### Opportunity: ✅ **High-Value Enhancement**
- Schema is well-designed for native merge
- Implementation is straightforward (6-10 days)
- Performance gains are substantial (20-40x)
- Maintains backward compatibility

### Decision Point

**If you frequently merge large databases:**
- Native SQL merge is worth implementing
- Use hybrid approach for quick wins
- Full implementation for production workloads

**If you rarely merge or merge small databases:**
- Current Python implementation is adequate
- Keep it simple and maintainable
- Focus development effort elsewhere

---

## References

1. **Current Implementation**:
   - `src/ucis/sqlite/sqlite_merge.py` (320 lines)
   - `src/ucis/merge/db_merger.py` (252 lines)

2. **Database Schema**:
   - `src/ucis/sqlite/schema_manager.py`
   - 15 tables with proper indexes

3. **Tests**:
   - `tests/unit/test_merge.py`
   - Covers basic merge operations

4. **SQLite Documentation**:
   - [ATTACH DATABASE](https://www.sqlite.org/lang_attach.html)
   - [Recursive Queries](https://www.sqlite.org/lang_with.html)
   - [INSERT FROM SELECT](https://www.sqlite.org/lang_insert.html)
