# UCIS C API - Native Implementation

This directory contains the native C implementation of the UCIS 1.0 API using SQLite3 as the backend storage.

## Build Instructions

```bash
# First time: download SQLite3
bash fetch_sqlite3.sh

# Build the library
make

# Run tests
make test

# Or run individual test suites
cd test
python3 test_basic.py
python3 test_scopes.py
```

## Current Status

### ✅ Phase 1: Foundation (Complete)
- Database lifecycle (open/close/write)
- Schema initialization
- Handle management
- SQLite3 integration

### ✅ Phase 2: Scope Hierarchy (Complete)
- Scope creation and management
- Parent-child relationships
- Scope iteration with filtering
- Scope attributes

### 🔄 Phase 3: Coverage Items (In Progress)
- Coverage item creation
- Coverage data management
- Coverage iteration

## API Functions Implemented

### Database Operations
- `ucis_Open()` - Open/create database
- `ucis_Close()` - Close database
- `ucis_Write()` - Write to file
- `ucis_GetAPIVersion()` - Get version
- `ucis_GetLastError()` - Get error message

### Scope Operations
- `ucis_CreateScope()` - Create scope with full parameters
- `ucis_CreateInstance()` - Create instance (convenience)
- `ucis_GetScopeName()` - Get scope name
- `ucis_GetScopeType()` - Get scope type
- `ucis_GetParent()` - Get parent scope
- `ucis_SetScopeWeight()` - Set weight
- `ucis_SetScopeGoal()` - Set goal
- `ucis_SetScopeFlags()` - Set flags
- `ucis_ScopeIterate()` - Iterate scopes with filtering

### Coverage Operations (Stubs)
- `ucis_CoverIterate()` - Ready for implementation

### History Operations (Stubs)
- `ucis_HistoryNodeIterate()` - Ready for implementation

## Files

| File | Purpose | Lines |
|------|---------|-------|
| `ucis.h` | Public API declarations | ~200 |
| `ucis_types.h` | Type definitions | ~150 |
| `ucis_impl.h` | Internal structures | ~80 |
| `ucis_api.c` | Database lifecycle | ~150 |
| `ucis_handle.c` | Handle management | ~100 |
| `ucis_util.c` | Utility functions | ~50 |
| `ucis_schema.c` | Schema initialization | ~200 |
| `ucis_scope.c` | Scope operations | ~300 |
| `ucis_iterator.c` | Iteration logic | ~200 |
| `sqlite3.c` | SQLite amalgamation | ~250k |

## Testing

All tests use Python with ctypes to load and exercise the shared library:

```python
import ctypes
libucis = ctypes.CDLL("./libucis.so")

# Define function signatures
libucis.ucis_Open.argtypes = [ctypes.c_char_p]
libucis.ucis_Open.restype = ctypes.c_void_p

# Use the API
db = libucis.ucis_Open(b"test.ucisdb")
# ...
libucis.ucis_Close(db)
```

### Test Coverage

- **test_basic.py** - Database lifecycle, schema validation
- **test_scopes.py** - Scope creation, hierarchy, iteration
- **test_coverage.py** - Coverage items (planned)
- **test_history.py** - History nodes (planned)

## Design Decisions

1. **Opaque Handles**: All API types are opaque pointers backed by a handle table
2. **Prepared Statements**: Cached for performance
3. **Foreign Keys**: Enabled for referential integrity
4. **WAL Mode**: Enabled for better concurrency
5. **Handle Caching**: Frequently-accessed data cached in handle entries
6. **Type Safety**: Handle validation on every API call

## Performance Notes

- Handle lookups: O(1) via pointer arithmetic
- Scope iteration: Indexed on parent_id
- Name lookups: Cached after first access
- Bulk operations: Use transactions for efficiency

## Memory Management

- Caller responsible for closing handles
- Internal caching freed on handle deallocation
- No memory leaks detected (verified with valgrind)

## License

Apache 2.0 (same as parent project)
