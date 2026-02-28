"""
LEB128 (unsigned) varint encoding/decoding.

Used throughout the NCDB format for compact integer serialization.

The bulk functions encode_varints() and decode_varints() are accelerated by
a C extension when available (see ucis.ncdb._accel).  The single-value
functions encode_varint() and decode_varint() remain in pure Python for use
by scope_tree.py which needs them inline.
"""


def encode_varint(value: int) -> bytes:
    """Encode a non-negative integer as unsigned LEB128 bytes."""
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
    return bytes(result)


def decode_varint(buf: bytes, offset: int = 0):
    """Decode an unsigned LEB128 varint from buf starting at offset.

    Returns:
        (value, new_offset) — the decoded integer and the offset of the
        first byte after the varint.
    """
    result = 0
    shift = 0
    while True:
        if offset >= len(buf):
            raise ValueError("Buffer too short for varint")
        byte = buf[offset]
        offset += 1
        result |= (byte & 0x7F) << shift
        shift += 7
        if not (byte & 0x80):
            break
    return result, offset


# ── Bulk encode/decode — use C accelerator when available ─────────────────

try:
    from ucis.ncdb._accel import (
        encode_varints as _accel_encode,
        decode_varints as _accel_decode,
    )
    _HAVE_ACCEL = True
except Exception:
    _HAVE_ACCEL = False


def encode_varints(values) -> bytes:
    """Encode a sequence of non-negative integers as concatenated LEB128."""
    if _HAVE_ACCEL:
        return _accel_encode(values)
    return b"".join(encode_varint(v) for v in values)


def decode_varints(buf: bytes, count: int, offset: int = 0):
    """Decode *count* consecutive LEB128 varints from buf.

    Returns:
        (list_of_values, new_offset)
    """
    if _HAVE_ACCEL:
        return _accel_decode(buf, count, offset)
    values = []
    for _ in range(count):
        v, offset = decode_varint(buf, offset)
        values.append(v)
    return values, offset
