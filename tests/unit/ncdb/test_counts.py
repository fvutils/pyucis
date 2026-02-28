"""Unit tests for ucis.ncdb.counts."""

import pytest
from ucis.ncdb.counts import CountsWriter, CountsReader


def _rt(values):
    """Round-trip helper."""
    data = CountsWriter().serialize(values)
    return CountsReader().deserialize(data)


def test_empty():
    assert _rt([]) == []


def test_all_zeros():
    result = _rt([0] * 100)
    assert result == [0] * 100


def test_all_ones():
    result = _rt([1] * 100)
    assert result == [1] * 100


def test_mixed():
    values = [0, 1, 2, 127, 128, 255, 256, 65535, 2**32 - 1]
    assert _rt(values) == values


def test_large_counts_use_uint32_mode():
    """When counts are large, uint32 mode is often more compact."""
    values = [2**31] * 200   # all near max uint32
    result = _rt(values)
    assert result == values


def test_small_counts_prefer_varint_mode():
    """Mostly-zero data should use varint (smaller)."""
    values = [0] * 1000 + [1, 2, 3]
    writer = CountsWriter()
    data = writer.serialize(values)
    # varint encoding: 1000 zeros at 1 byte each + 3 small = 1003 bytes
    # uint32: 1003 * 4 = 4012 bytes
    assert len(data) < 4012
    assert CountsReader().deserialize(data) == values
