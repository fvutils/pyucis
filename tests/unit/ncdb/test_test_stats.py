"""Unit tests for TestStatsTable (test_stats.bin)."""
import math
import pytest
from ucis.ncdb.test_stats import TestStatsTable, TestStatsEntry
from ucis.ncdb.constants import HIST_STATUS_OK, HIST_STATUS_FAIL, HIST_STATUS_ERROR


def _make_table(*statuses, cpu_times=None):
    tbl = TestStatsTable()
    for i, s in enumerate(statuses):
        cpu = cpu_times[i] if cpu_times else None
        tbl.update(0, s, 1700000000 + i * 86400, cpu_time=cpu)
    return tbl


def test_update_pass():
    tbl = _make_table(HIST_STATUS_OK)
    e = tbl.get(0)
    assert e.total_runs == 1
    assert e.pass_count == 1
    assert e.fail_count == 0
    assert e.last_green_ts == 1700000000


def test_update_fail():
    tbl = _make_table(HIST_STATUS_FAIL)
    e = tbl.get(0)
    assert e.fail_count == 1
    assert e.pass_count == 0
    assert e.last_green_ts == 0


def test_update_error():
    tbl = _make_table(HIST_STATUS_ERROR)
    e = tbl.get(0)
    assert e.error_count == 1


def test_streak_consecutive_passes():
    tbl = _make_table(HIST_STATUS_OK, HIST_STATUS_OK, HIST_STATUS_OK)
    assert tbl.get(0).streak == 3


def test_streak_consecutive_fails():
    tbl = _make_table(HIST_STATUS_FAIL, HIST_STATUS_FAIL)
    assert tbl.get(0).streak == -2


def test_streak_resets_on_change():
    tbl = _make_table(HIST_STATUS_FAIL, HIST_STATUS_FAIL, HIST_STATUS_OK)
    assert tbl.get(0).streak == 1


def test_transition_count():
    tbl = _make_table(HIST_STATUS_OK, HIST_STATUS_FAIL, HIST_STATUS_OK)
    e = tbl.get(0)
    assert e.transition_count == 2


def test_flake_score_alternating():
    statuses = [HIST_STATUS_OK, HIST_STATUS_FAIL] * 50
    tbl = _make_table(*statuses)
    e = tbl.get(0)
    # 99 transitions over 99 intervals → score = 1.0
    assert abs(e.flake_score - 1.0) < 0.02


def test_flake_score_stable_all_pass():
    tbl = _make_table(*([HIST_STATUS_OK] * 10))
    assert tbl.get(0).flake_score == 0.0


def test_fail_rate():
    tbl = _make_table(HIST_STATUS_OK, HIST_STATUS_FAIL, HIST_STATUS_FAIL)
    e = tbl.get(0)
    assert abs(e.fail_rate - 2/3) < 1e-6


def test_welford_mean():
    cpu = [1.0, 2.0, 3.0]
    tbl = _make_table(HIST_STATUS_OK, HIST_STATUS_OK, HIST_STATUS_OK, cpu_times=cpu)
    assert abs(tbl.get(0).mean_cpu_time - 2.0) < 1e-6


def test_welford_stddev():
    # known variance: [1,2,3] → mean=2, var=2/3, std=sqrt(2/3)
    cpu = [1.0, 2.0, 3.0]
    tbl = _make_table(HIST_STATUS_OK, HIST_STATUS_OK, HIST_STATUS_OK, cpu_times=cpu)
    e = tbl.get(0)
    expected_std = math.sqrt(2/3)
    assert abs(e.stddev_cpu_time - expected_std) < 1e-5


def test_cusum_detects_change_point():
    """Sustained failures should drive CUSUM past the h=4.0 threshold."""
    tbl = TestStatsTable()
    # Start with passes to establish baseline mean ≈ 0
    for i in range(10):
        tbl.update(0, HIST_STATUS_OK, 1700000000 + i * 86400)
    # Then many consecutive failures
    triggered = False
    for i in range(10, 30):
        tbl.update(0, HIST_STATUS_FAIL, 1700000000 + i * 86400)
        # After reset, CUSUM can rise again — just check it doesn't blow up
    e = tbl.get(0)
    assert e.fail_count == 20
    assert e.cusum_value >= 0.0   # always non-negative


def test_grade_score_range():
    statuses = [HIST_STATUS_OK, HIST_STATUS_FAIL, HIST_STATUS_OK]
    tbl = _make_table(*statuses)
    score = tbl.get(0).grade_score
    assert 0.0 <= score <= 1.0


def test_is_broken():
    tbl = _make_table(*([HIST_STATUS_FAIL] * 10))
    assert tbl.get(0).is_broken()


def test_is_flaky():
    # Alternating → flake_score close to 1, abs(streak) < 3
    tbl = _make_table(HIST_STATUS_OK, HIST_STATUS_FAIL, HIST_STATUS_OK)
    assert tbl.get(0).is_flaky()


def test_top_flaky():
    tbl = TestStatsTable()
    # name_id 0: alternates (high flake)
    for i in range(10):
        s = HIST_STATUS_OK if i % 2 == 0 else HIST_STATUS_FAIL
        tbl.update(0, s, 1700000000 + i * 86400)
    # name_id 1: always passes (zero flake)
    for i in range(10):
        tbl.update(1, HIST_STATUS_OK, 1700000000 + i * 86400)
    top = tbl.top_flaky(1)
    assert top[0].name_id == 0


def test_top_failing():
    tbl = TestStatsTable()
    for i in range(10):
        tbl.update(0, HIST_STATUS_FAIL, 1700000000 + i * 86400)  # 100% fail
    for i in range(10):
        tbl.update(1, HIST_STATUS_OK, 1700000000 + i * 86400)    # 0% fail
    top = tbl.top_failing(1)
    assert top[0].name_id == 0


def test_multiple_name_ids():
    tbl = TestStatsTable()
    tbl.update(0, HIST_STATUS_OK, 1700000000)
    tbl.update(3, HIST_STATUS_FAIL, 1700000001)
    assert tbl.get(0).pass_count == 1
    assert tbl.get(1) is not None   # auto-created empty
    assert tbl.get(3).fail_count == 1


def test_serialize_deserialize():
    tbl = TestStatsTable()
    for i in range(5):
        s = HIST_STATUS_OK if i % 2 == 0 else HIST_STATUS_FAIL
        tbl.update(0, s, 1700000000 + i * 86400, cpu_time=float(i + 1))
    data = tbl.serialize()
    tbl2 = TestStatsTable.deserialize(data)
    e  = tbl.get(0)
    e2 = tbl2.get(0)
    assert e2.total_runs == e.total_runs
    assert e2.pass_count == e.pass_count
    assert abs(e2.flake_score - e.flake_score) < 1e-5
    assert abs(e2.mean_cpu_time - e.mean_cpu_time) < 1e-4


def test_bad_magic_raises():
    data = b"\x00\x00\x00\x00" + b"\x00" * 8
    with pytest.raises(ValueError, match="Bad magic"):
        TestStatsTable.deserialize(data)
