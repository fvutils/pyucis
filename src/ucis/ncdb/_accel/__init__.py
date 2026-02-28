"""
_accel/__init__.py — transparent shim for the ncdb C accelerator.

Exports three functions that are used by varint.py and counts.py:
  - encode_varints(values) -> bytes
  - decode_varints(data, count, offset) -> (list[int], int)
  - add_uint32_arrays(a, b) -> list[int]

When the compiled extension (_ncdb_accel.so) is available, these delegate
to the C implementation.  When not available, they fall back to pure Python
so that the package works without a C compiler.

The boolean ``HAS_ACCEL`` indicates which path is active.
"""

from __future__ import annotations

import glob
import os
import struct

_HERE = os.path.dirname(os.path.abspath(__file__))

# ── Try to load the compiled extension ────────────────────────────────────

_lib = None
_ffi = None

try:
    import cffi as _cffi_mod
    _ffi = _cffi_mod.FFI()
    _ffi.cdef(r"""
        int  ncdb_encode_varints(const uint64_t *values, size_t count,
                                 uint8_t *out_buf, size_t out_cap);
        int  ncdb_decode_varints(const uint8_t *data, size_t data_len,
                                 size_t offset, size_t count,
                                 uint64_t *out_values);
        void ncdb_add_uint32_arrays(const uint32_t *a, const uint32_t *b,
                                    size_t count, uint32_t *out);
    """)
    _so_matches = sorted(glob.glob(os.path.join(_HERE, "_ncdb_accel*.so")))
    if _so_matches:
        _lib = _ffi.dlopen(_so_matches[-1])
except Exception:
    pass

HAS_ACCEL: bool = _lib is not None

# ── encode_varints ─────────────────────────────────────────────────────────

if HAS_ACCEL:
    def encode_varints(values) -> bytes:
        """Encode a sequence of non-negative ints as LEB128 (C-accelerated)."""
        n = len(values)
        # Upper bound: 10 bytes per uint64
        cap = max(n * 10, 16)
        arr = _ffi.new(f"uint64_t[]", list(values))
        buf = _ffi.new(f"uint8_t[]", cap)
        written = _lib.ncdb_encode_varints(arr, n, buf, cap)
        if written < 0:
            raise RuntimeError("ncdb_encode_varints: output buffer overflow")
        return bytes(_ffi.buffer(buf, written))
else:
    def encode_varints(values) -> bytes:
        """Encode a sequence of non-negative ints as LEB128 (pure Python)."""
        parts = []
        for value in values:
            if value < 0:
                raise ValueError(f"varint requires non-negative integer, got {value}")
            result = []
            while True:
                byte = value & 0x7F
                value >>= 7
                if value != 0:
                    byte |= 0x80
                result.append(byte)
                if value == 0:
                    break
            parts.append(bytes(result))
        return b"".join(parts)

# ── decode_varints ─────────────────────────────────────────────────────────

if HAS_ACCEL:
    def decode_varints(data: bytes, count: int, offset: int = 0):
        """Decode *count* LEB128 varints from *data* (C-accelerated).

        Returns (list[int], new_offset).
        """
        if count == 0:
            return [], offset
        n = len(data)
        c_data = _ffi.from_buffer(data)
        out = _ffi.new(f"uint64_t[]", count)
        new_off = _lib.ncdb_decode_varints(c_data, n, offset, count, out)
        if new_off < 0:
            raise ValueError("ncdb_decode_varints: buffer too short")
        return list(out), new_off
else:
    def decode_varints(data: bytes, count: int, offset: int = 0):
        """Decode *count* LEB128 varints from *data* (pure Python).

        Returns (list[int], new_offset).
        """
        values = []
        for _ in range(count):
            result = 0
            shift = 0
            while True:
                if offset >= len(data):
                    raise ValueError("Buffer too short for varint")
                byte = data[offset]
                offset += 1
                result |= (byte & 0x7F) << shift
                shift += 7
                if not (byte & 0x80):
                    break
            values.append(result)
        return values, offset

# ── add_uint32_arrays ──────────────────────────────────────────────────────

if HAS_ACCEL:
    def add_uint32_arrays(a, b) -> list:
        """Element-wise sum of two equal-length int sequences (C-accelerated)."""
        n = len(a)
        ca = _ffi.new("uint32_t[]", list(a))
        cb = _ffi.new("uint32_t[]", list(b))
        out = _ffi.new("uint32_t[]", n)
        _lib.ncdb_add_uint32_arrays(ca, cb, n, out)
        return list(out)
else:
    def add_uint32_arrays(a, b) -> list:
        """Element-wise sum of two equal-length int sequences (pure Python)."""
        return [x + y for x, y in zip(a, b)]
