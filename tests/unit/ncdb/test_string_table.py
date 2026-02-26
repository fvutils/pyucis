"""Unit tests for ucis.ncdb.string_table."""

import pytest
from ucis.ncdb.string_table import StringTable


def test_empty_table():
    st = StringTable()
    data = st.serialize()
    st2 = StringTable.from_bytes(data)
    assert len(st2) == 0


def test_single_string():
    st = StringTable()
    idx = st.add("hello")
    assert idx == 0
    assert st.get(0) == "hello"
    st2 = StringTable.from_bytes(st.serialize())
    assert st2.get(0) == "hello"


def test_deduplication():
    st = StringTable()
    i1 = st.add("foo")
    i2 = st.add("bar")
    i3 = st.add("foo")
    assert i1 == i3
    assert i1 != i2


def test_large_table():
    st = StringTable()
    strings = [f"signal_{i}" for i in range(1000)] + ["signal_0"] * 500
    indices = [st.add(s) for s in strings]
    # Unique strings
    unique = list(dict.fromkeys(strings))
    assert len(st) == len(unique)
    # Round-trip
    st2 = StringTable.from_bytes(st.serialize())
    for s in unique:
        assert st2.get(st.add(s)) == s


def test_unicode():
    st = StringTable()
    idx = st.add("信号_test")
    st2 = StringTable.from_bytes(st.serialize())
    assert st2.get(idx) == "信号_test"


def test_none_becomes_empty():
    st = StringTable()
    idx = st.add(None)
    assert st.get(idx) == ""
