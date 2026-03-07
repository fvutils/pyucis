"""Unit tests for ContribIndex (contrib_index.bin)."""
import pytest
from ucis.ncdb.contrib_index import (
    ContribIndex,
    POLICY_ALL, POLICY_PASS_ONLY, POLICY_EXCLUDE_ERROR_RERUN, POLICY_STRICT,
    FLAG_IS_RERUN, FLAG_FIRST_ATTEMPT_PASSED,
)
from ucis.ncdb.constants import HIST_STATUS_OK, HIST_STATUS_FAIL, HIST_STATUS_ERROR


def test_add_and_passing_run_ids_pass_only():
    ci = ContribIndex()
    ci.add_entry(0, 0, HIST_STATUS_OK,   0)
    ci.add_entry(1, 1, HIST_STATUS_FAIL, 0)
    ci.add_entry(2, 0, HIST_STATUS_OK,   0)
    assert ci.passing_run_ids(POLICY_PASS_ONLY) == [0, 2]


def test_policy_all():
    ci = ContribIndex()
    ci.add_entry(0, 0, HIST_STATUS_OK,   0)
    ci.add_entry(1, 0, HIST_STATUS_FAIL, 0)
    assert ci.passing_run_ids(POLICY_ALL) == [0, 1]


def test_policy_strict_excludes_rerun_without_first_pass():
    ci = ContribIndex()
    ci.add_entry(0, 0, HIST_STATUS_OK, 0)                          # normal pass → included
    ci.add_entry(1, 0, HIST_STATUS_OK, FLAG_IS_RERUN)              # rerun, first attempt failed → excluded
    ci.add_entry(2, 0, HIST_STATUS_OK,
                 FLAG_IS_RERUN | FLAG_FIRST_ATTEMPT_PASSED)        # rerun, first also passed → included
    assert ci.passing_run_ids(POLICY_STRICT) == [0, 2]


def test_policy_exclude_error_rerun_same_as_pass_only():
    ci = ContribIndex()
    ci.add_entry(0, 0, HIST_STATUS_OK,    0)
    ci.add_entry(1, 0, HIST_STATUS_ERROR, 0)
    assert ci.passing_run_ids(POLICY_EXCLUDE_ERROR_RERUN) == [0]


def test_squash_watermark_update():
    ci = ContribIndex(squash_watermark=0)
    ci.set_squash_watermark(99)
    assert ci.squash_watermark == 99


def test_remove_entries_after_squash():
    ci = ContribIndex()
    for run_id in range(10):
        ci.add_entry(run_id, 0, HIST_STATUS_OK, 0)
    ci.remove_entries_up_to(4)
    assert ci.num_active == 5
    remaining = [e.run_id for e in ci._entries]
    assert remaining == [5, 6, 7, 8, 9]


def test_max_run_id_from_entries():
    ci = ContribIndex()
    ci.add_entry(0, 0, HIST_STATUS_OK, 0)
    ci.add_entry(7, 0, HIST_STATUS_OK, 0)
    assert ci.max_run_id() == 7


def test_max_run_id_falls_back_to_watermark():
    ci = ContribIndex(squash_watermark=42)
    assert ci.max_run_id() == 42


def test_serialize_deserialize_empty():
    ci = ContribIndex()
    ci2 = ContribIndex.deserialize(ci.serialize())
    assert ci2.num_active == 0
    assert ci2.merge_policy == POLICY_PASS_ONLY


def test_serialize_deserialize_with_entries():
    ci = ContribIndex(merge_policy=POLICY_STRICT, squash_watermark=10)
    ci.add_entry(11, 0, HIST_STATUS_OK,   FLAG_IS_RERUN)
    ci.add_entry(12, 1, HIST_STATUS_FAIL, 0)
    data = ci.serialize()
    ci2 = ContribIndex.deserialize(data)
    assert ci2.merge_policy    == POLICY_STRICT
    assert ci2.squash_watermark == 10
    assert ci2.num_active == 2
    assert ci2._entries[0].run_id == 11
    assert ci2._entries[0].is_rerun is True
    assert ci2._entries[1].status  == HIST_STATUS_FAIL


def test_bad_magic_raises():
    data = b"\x00\x00\x00\x00" + b"\x00" * 20
    with pytest.raises(ValueError, match="Bad magic"):
        ContribIndex.deserialize(data)
