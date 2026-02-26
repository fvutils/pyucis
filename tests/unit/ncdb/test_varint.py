"""Unit tests for ucis.ncdb.varint (LEB128 encode/decode)."""

import pytest
from ucis.ncdb.varint import encode_varint, decode_varint, encode_varints, decode_varints


ROUND_TRIP_CASES = [
    0, 1, 127, 128, 255, 256,
    16383, 16384,
    2**32 - 1, 2**32,
    2**64 - 1,
]


@pytest.mark.parametrize("value", ROUND_TRIP_CASES)
def test_round_trip(value):
    encoded = encode_varint(value)
    decoded, offset = decode_varint(encoded)
    assert decoded == value
    assert offset == len(encoded)


def test_single_byte_range():
    """Values 0–127 should encode to exactly 1 byte."""
    for v in range(128):
        assert len(encode_varint(v)) == 1


def test_two_byte_range():
    """Values 128–16383 should encode to exactly 2 bytes."""
    for v in (128, 129, 16383):
        assert len(encode_varint(v)) == 2


def test_negative_raises():
    with pytest.raises(ValueError):
        encode_varint(-1)


def test_decode_offset():
    """decode_varint respects a non-zero starting offset."""
    buf = bytes([0x00]) + encode_varint(300) + bytes([0xFF])
    value, new_off = decode_varint(buf, 1)
    assert value == 300


def test_encode_decode_sequence():
    values = [0, 1, 128, 16384, 2**32]
    buf = encode_varints(values)
    decoded, offset = decode_varints(buf, len(values))
    assert decoded == values
    assert offset == len(buf)


def test_decode_short_buffer_raises():
    with pytest.raises(ValueError):
        decode_varint(b"\x80")  # continuation bit set but buffer ends
