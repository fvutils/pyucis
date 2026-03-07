"""Unit tests for SquashLog (squash_log.bin)."""
import pytest
from ucis.ncdb.squash_log import SquashLog


def test_append_single_entry():
    log = SquashLog()
    log.append(ts=1700000000, policy=1, from_run=0, to_run=9,
               num_runs=10, pass_runs=9)
    assert log.num_squashes == 1
    entries = log.entries()
    e = entries[0]
    assert e.ts        == 1700000000
    assert e.policy    == 1
    assert e.from_run  == 0
    assert e.to_run    == 9
    assert e.num_runs  == 10
    assert e.pass_runs == 9


def test_append_multiple():
    log = SquashLog()
    for i in range(5):
        log.append(ts=1700000000 + i * 86400, policy=1,
                   from_run=i * 10, to_run=i * 10 + 9,
                   num_runs=10, pass_runs=10)
    assert log.num_squashes == 5
    entries = log.entries()
    assert entries[4].from_run == 40


def test_serialize_deserialize_empty():
    log = SquashLog()
    log2 = SquashLog.deserialize(log.serialize())
    assert log2.num_squashes == 0


def test_serialize_deserialize_multiple():
    log = SquashLog()
    log.append(ts=1700000000, policy=1, from_run=0,  to_run=9,  num_runs=10, pass_runs=9)
    log.append(ts=1700086400, policy=1, from_run=10, to_run=19, num_runs=10, pass_runs=8)
    log.append(ts=1700172800, policy=1, from_run=20, to_run=29, num_runs=10, pass_runs=7)
    data = log.serialize()
    log2 = SquashLog.deserialize(data)
    assert log2.num_squashes == 3
    entries = log2.entries()
    assert entries[2].to_run    == 29
    assert entries[2].pass_runs == 7


def test_all_policy_values():
    log = SquashLog()
    for policy in range(4):
        log.append(ts=1700000000 + policy * 86400, policy=policy,
                   from_run=0, to_run=9, num_runs=10, pass_runs=10 - policy)
    entries = log.entries()
    policies = [e.policy for e in entries]
    assert policies == [0, 1, 2, 3]


def test_bad_magic_raises():
    data = b"\x00\x00\x00\x00" + b"\x00" * 8
    with pytest.raises(ValueError, match="Bad magic"):
        SquashLog.deserialize(data)
