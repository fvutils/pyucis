"""Unit tests for TestRegistry (test_registry.bin)."""
import pytest
from ucis.ncdb.test_registry import TestRegistry


def test_assign_run_id_increments():
    reg = TestRegistry()
    assert reg.assign_run_id() == 0
    assert reg.assign_run_id() == 1
    assert reg.assign_run_id() == 2


def test_assign_run_id_survives_roundtrip():
    reg = TestRegistry()
    reg.assign_run_id(); reg.assign_run_id()
    reg2 = TestRegistry.deserialize(reg.serialize())
    assert reg2.assign_run_id() == 2


def test_lookup_name_id_new():
    reg = TestRegistry()
    nid = reg.lookup_name_id("uart_smoke")
    assert nid == 0
    assert reg.num_names == 1


def test_lookup_name_id_existing():
    reg = TestRegistry()
    nid1 = reg.lookup_name_id("uart_smoke")
    nid2 = reg.lookup_name_id("uart_smoke")
    assert nid1 == nid2


def test_name_heap_insertion_order():
    """name_ids are assigned by insertion order and never shift."""
    reg = TestRegistry()
    reg.lookup_name_id("zebra")
    reg.lookup_name_id("apple")
    reg.lookup_name_id("mango")
    assert reg.name_for_id(0) == "zebra"
    assert reg.name_for_id(1) == "apple"
    assert reg.name_for_id(2) == "mango"


def test_name_id_stable_after_insert():
    """Inserting a new name does NOT shift any existing name_id."""
    reg = TestRegistry()
    id_mango = reg.lookup_name_id("mango")    # id 0
    id_apple = reg.lookup_name_id("apple")    # id 1 (insertion order)
    assert id_mango == 0
    assert id_apple == 1
    # Looking them up again returns the SAME ids
    assert reg.lookup_name_id("mango") == 0
    assert reg.lookup_name_id("apple") == 1


def test_lookup_seed_id_new():
    reg = TestRegistry()
    sid = reg.lookup_seed_id("12345")
    assert sid == 0
    assert reg.num_seeds == 1


def test_lookup_seed_id_existing():
    reg = TestRegistry()
    sid1 = reg.lookup_seed_id("99999")
    sid2 = reg.lookup_seed_id("99999")
    assert sid1 == sid2


def test_seed_id_insertion_order():
    """Seeds are stored in insertion order (not sorted)."""
    reg = TestRegistry()
    reg.lookup_seed_id("zzz")
    reg.lookup_seed_id("aaa")
    assert reg.seed_for_id(0) == "zzz"
    assert reg.seed_for_id(1) == "aaa"


def test_seed_id_roundtrip():
    reg = TestRegistry()
    reg.lookup_seed_id("abc123")
    reg2 = TestRegistry.deserialize(reg.serialize())
    assert reg2.seed_for_id(0) == "abc123"


def test_serialize_deserialize_empty():
    reg = TestRegistry()
    reg2 = TestRegistry.deserialize(reg.serialize())
    assert reg2.num_names == 0
    assert reg2.num_seeds == 0
    assert reg2.next_run_id == 0


def test_serialize_deserialize_names_and_seeds():
    reg = TestRegistry(next_run_id=5)
    names = ["test_z", "test_a", "test_m"]
    for n in names:
        reg.lookup_name_id(n)
    reg.lookup_seed_id("1"); reg.lookup_seed_id("2")
    data = reg.serialize()
    reg2 = TestRegistry.deserialize(data)
    assert reg2.next_run_id == 5
    assert reg2.num_names == 3
    assert reg2.num_seeds == 2
    # Names and seeds preserved in insertion order
    assert reg2.name_for_id(0) == "test_z"   # insertion order
    assert reg2.name_for_id(1) == "test_a"
    assert reg2.name_for_id(2) == "test_m"
    assert reg2.seed_for_id(0) == "1"
    assert reg2.seed_for_id(1) == "2"


def test_serialize_deserialize_1000_names():
    reg = TestRegistry()
    for i in range(1000):
        reg.lookup_name_id(f"test_{i:04d}")
    data = reg.serialize()
    reg2 = TestRegistry.deserialize(data)
    assert reg2.num_names == 1000
    # Spot-check a few
    for i in range(1000):
        name = f"test_{i:04d}"
        assert reg2.name_for_id(reg2.lookup_name_id(name)) == name


def test_bad_magic_raises():
    data = b"\x00\x00\x00\x00" + b"\x00" * 20   # ≥ header size (17 bytes)
    with pytest.raises(ValueError, match="Bad magic"):
        TestRegistry.deserialize(data)
