# NCDB C Accelerator

Optional cffi-based C extension that accelerates varint encoding/decoding
by ~10× and element-wise array addition for the NCDB merge path.

## What it accelerates

| Function | Python time (10K values) | C time | Speedup |
|----------|--------------------------|--------|---------|
| `encode_varints` | 1.3 ms | 0.15 ms | 9× |
| `decode_varints` | 1.5 ms | 0.10 ms | 14× |

End-to-end merge speedup vs SQLite with C accel: **10–32×** (BM1–BM6).

## Build

```bash
pip install cffi          # already a project dependency
python -m ucis.ncdb._accel._ncdb_accel_build
```

This compiles `ncdb_accel.c` and writes `_ncdb_accel.cpython-<ver>-<arch>.so`
in this directory.  The shared library is loaded at runtime by `__init__.py`.

## Usage

The accelerator is transparent — `varint.py` and `counts.py` automatically
use it when available:

```python
from ucis.ncdb._accel import HAS_ACCEL
print(HAS_ACCEL)   # True if the .so was found
```

## Fallback

If the `.so` is missing or cffi is unavailable, all operations fall back to
pure Python silently.  All tests pass in both modes.

## Prerequisites

- `cffi` (already in `requirements.txt`)
- A C compiler (`gcc` or `clang`) on `PATH`
- Linux/macOS — Windows support requires MSVC or MinGW
