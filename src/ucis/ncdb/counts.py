"""
counts.bin — packed hit-count array serialization.

Two encoding modes:
  Mode 0 (COUNTS_MODE_UINT32): fixed 4-byte little-endian per count.
  Mode 1 (COUNTS_MODE_VARINT): LEB128 varint per count.

Binary layout:
  [mode:  1 byte]
  [count: varint]
  [data:  mode-dependent encoding of *count* integers]

The writer chooses varint mode when the varint-encoded size is smaller
than the fixed uint32 size (typically true when most counts are 0 or small).
"""

import array
import io

from .varint import encode_varint, decode_varint, encode_varints, decode_varints
from .constants import COUNTS_MODE_UINT32, COUNTS_MODE_VARINT


class CountsWriter:
    """Serialize a list of hit counts to counts.bin bytes."""

    def serialize(self, counts: list) -> bytes:
        """Choose the best encoding and return the serialized bytes."""
        n = len(counts)
        # Estimate varint size
        varint_bytes = encode_varints(counts)
        fixed_bytes  = n * 4

        # Force varint mode if any count exceeds uint32 max (4294967295)
        has_large = any(c > 0xFFFFFFFF for c in counts)

        if has_large or len(varint_bytes) < fixed_bytes:
            mode = COUNTS_MODE_VARINT
        else:
            mode = COUNTS_MODE_UINT32

        buf = io.BytesIO()
        buf.write(bytes([mode]))
        buf.write(encode_varint(n))

        if mode == COUNTS_MODE_VARINT:
            buf.write(varint_bytes)
        else:
            arr = array.array("I", counts)   # unsigned int (4 bytes)
            if arr.itemsize != 4:            # guard against exotic platforms
                for c in counts:
                    buf.write(c.to_bytes(4, "little"))
            else:
                arr.byteswap() if __import__("sys").byteorder == "big" else None
                buf.write(arr.tobytes())

        return buf.getvalue()


class CountsReader:
    """Deserialize hit counts from counts.bin bytes."""

    def deserialize(self, data: bytes) -> list:
        """Return a list of integers decoded from *data*."""
        if not data:
            return []
        offset = 0
        mode = data[offset]
        offset += 1
        count, offset = decode_varint(data, offset)

        if mode == COUNTS_MODE_VARINT:
            # Fast path: if all values fit in one byte (0–127), each byte IS
            # the value (high bit clear).  Covers the common small-count case.
            payload = data[offset:offset + count]
            if len(payload) == count and all(b < 0x80 for b in payload):
                return list(payload)
            # General path — use bulk decode (C-accelerated when available)
            values, _ = decode_varints(data, count, offset)
            return values
        else:  # UINT32
            import struct
            values = list(struct.unpack_from(f"<{count}I", data, offset))
            return values
