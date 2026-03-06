"""
test_stats.bin — per-test aggregate metrics table.

One fixed-size 64-byte record per unique test, indexed by ``name_id`` from
``test_registry.bin``.  All fields are maintained incrementally — O(1) update
per new test run — so aggregate queries (top flaky tests, fail rate, etc.)
need only this file, never the per-bucket records.

Binary layout of the file header (little-endian)::

    magic       u32   0x54535441  ('TSTA')
    version     u8    1
    num_tests   u32

Followed by ``num_tests`` 64-byte entries (indexed by name_id):

    total_runs          u32
    pass_count          u32
    fail_count          u32
    error_count         u32
    first_ts            u32   unix timestamp of first ever run
    last_ts             u32   unix timestamp of most recent run
    last_green_ts       u32   unix timestamp of last passing run
    transition_count    u32   consecutive status changes (flake signal)
    streak              i16   positive = consecutive passes, negative = fails
    last_status         u8    most recent run status (HIST_STATUS_*)
    _pad                u8
    flake_score         f32   transition_count / max(total_runs-1, 1)  ∈ [0,1]
    fail_rate           f32   fail_count / total_runs                  ∈ [0,1]
    mean_cpu_time       f32   Welford online mean (seconds)
    m2_cpu_time         f32   Welford M2 accumulator
    cusum_value         f32   running CUSUM statistic
    cusum_ref_mean      f32   μ₀ used for CUSUM
    grade_score         f32   composite effectiveness score [0,1]
    total_seeds_seen    u16   unique seeds ever seen for this test
    _reserved           u8[6]

Total: 72 bytes per entry.
"""

from __future__ import annotations

import math
import struct
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from ucis.ncdb.constants import (
    HIST_STATUS_FAIL, HIST_STATUS_OK,
)

MAGIC   = 0x54535441   # 'TSTA'
VERSION = 1

# CUSUM parameters
_CUSUM_K = 0.5   # allowance (half the detectable shift in σ units)
_CUSUM_H = 4.0   # decision threshold (triggers change-point detection)

_HDR   = struct.Struct("<IBI")      # magic, version, num_tests
_ENTRY = struct.Struct("<8I hBB 7f H6s")
# Field breakdown: 8×u32=32, i16+u8+u8=4, 7×f32=28, u16=2, 6s=6  → 72 bytes per entry
assert _ENTRY.size == 72, f"Entry size is {_ENTRY.size}, expected 72"


@dataclass
class TestStatsEntry:
    """Aggregate metrics for one test (one name_id)."""

    name_id:          int   = 0
    total_runs:       int   = 0
    pass_count:       int   = 0
    fail_count:       int   = 0
    error_count:      int   = 0
    first_ts:         int   = 0
    last_ts:          int   = 0
    last_green_ts:    int   = 0
    transition_count: int   = 0
    streak:           int   = 0   # signed: + = passes, - = fails
    last_status:      int   = HIST_STATUS_OK
    flake_score:      float = 0.0
    fail_rate:        float = 0.0
    mean_cpu_time:    float = 0.0
    m2_cpu_time:      float = 0.0
    cusum_value:      float = 0.0
    cusum_ref_mean:   float = 0.0
    grade_score:      float = 0.0
    total_seeds_seen: int   = 0
    _known_seeds:     set   = field(default_factory=set, repr=False, compare=False)

    # ── Derived properties ───────────────────────────────────────────────

    @property
    def stddev_cpu_time(self) -> float:
        """Standard deviation of CPU time from Welford M2 accumulator."""
        if self.total_runs < 2:
            return 0.0
        return math.sqrt(self.m2_cpu_time / self.total_runs)

    def days_since_last_pass(self, now: Optional[int] = None) -> float:
        if self.last_green_ts == 0:
            return float("inf")
        t = now if now is not None else int(time.time())
        return (t - self.last_green_ts) / 86400.0

    def is_broken(self) -> bool:
        """Definitively broken: streak ≤ -5 and flake_score < 0.1."""
        return self.streak <= -5 and self.flake_score < 0.1

    def is_flaky(self) -> bool:
        """Likely flaky: abs(streak) < 3 and flake_score > 0.3."""
        return abs(self.streak) < 3 and self.flake_score > 0.3


class TestStatsTable:
    """In-memory representation of ``test_stats.bin``.

    Entries are indexed by ``name_id``; new entries are appended automatically
    when :meth:`update` is called with a previously unseen *name_id*.

    Example::

        tbl = TestStatsTable()
        tbl.update(name_id=0, status=HIST_STATUS_OK, ts=1700000000)
        tbl.update(name_id=0, status=HIST_STATUS_FAIL, ts=1700086400)
        print(tbl.get(0).flake_score)   # 1.0 (alternates every run)

        data = tbl.serialize()
        tbl2 = TestStatsTable.deserialize(data)
    """

    def __init__(self) -> None:
        self._entries: List[TestStatsEntry] = []

    # ── public API ───────────────────────────────────────────────────────────

    def update(self, name_id: int, status: int, ts: int,
               cpu_time: Optional[float] = None,
               seed_id: Optional[int] = None) -> None:
        """Incorporate one new test run into the aggregate statistics.

        Args:
            name_id:  Integer name_id from TestRegistry.
            status:   HIST_STATUS_* constant.
            ts:       Unix timestamp of this run.
            cpu_time: Wall/CPU time in seconds (optional).
            seed_id:  seed_id from TestRegistry (optional, for seed diversity).
        """
        self._ensure(name_id)
        e = self._entries[name_id]

        e.total_runs += 1
        if e.total_runs == 1:
            e.first_ts = ts
            e.cusum_ref_mean = 1.0 if status == HIST_STATUS_FAIL else 0.0

        e.last_ts = max(e.last_ts, ts)

        if status == HIST_STATUS_OK:
            e.pass_count += 1
            e.last_green_ts = max(e.last_green_ts, ts)
        elif status == HIST_STATUS_FAIL:
            e.fail_count += 1
        else:
            e.error_count += 1

        # Streak tracking
        if status == HIST_STATUS_OK:
            e.streak = e.streak + 1 if e.streak >= 0 else 1
        else:
            e.streak = e.streak - 1 if e.streak <= 0 else -1

        # Transition count (flake signal)
        if e.total_runs > 1 and status != e.last_status:
            e.transition_count += 1

        e.last_status = status

        # Derived rates
        e.flake_score = e.transition_count / max(e.total_runs - 1, 1)
        e.fail_rate   = e.fail_count / e.total_runs

        # Welford online mean/variance for cpu_time
        if cpu_time is not None:
            delta = cpu_time - e.mean_cpu_time
            e.mean_cpu_time += delta / e.total_runs
            e.m2_cpu_time   += delta * (cpu_time - e.mean_cpu_time)

        # CUSUM update
        x = 1.0 if status == HIST_STATUS_FAIL else 0.0
        e.cusum_value = max(0.0, e.cusum_value + x - (e.cusum_ref_mean + _CUSUM_K))
        # Change-point detected: reset (caller may log the timestamp)
        if e.cusum_value > _CUSUM_H:
            e.cusum_value = 0.0

        # Seed diversity
        if seed_id is not None:
            e._known_seeds.add(seed_id)
            e.total_seeds_seen = len(e._known_seeds)

        # Composite grade: (pass_rate) × (stability) × (speed_factor)
        pass_rate   = e.pass_count / e.total_runs
        stability   = 1.0 - e.flake_score
        # Speed factor: normalize by mean_cpu_time capped at 3600 s
        if e.mean_cpu_time > 0:
            speed = max(0.0, 1.0 - e.mean_cpu_time / 3600.0)
        else:
            speed = 1.0
        e.grade_score = pass_rate * stability * speed

    def get(self, name_id: int) -> Optional[TestStatsEntry]:
        """Return the entry for *name_id*, or None if not present."""
        if name_id < len(self._entries):
            return self._entries[name_id]
        return None

    def top_flaky(self, n: int = 20) -> List[TestStatsEntry]:
        """Return the top-*n* entries sorted by ``flake_score`` descending."""
        return sorted(self._entries, key=lambda e: e.flake_score, reverse=True)[:n]

    def top_failing(self, n: int = 20,
                    flake_threshold: float = 0.1) -> List[TestStatsEntry]:
        """Return the top-*n* consistently-failing tests.

        Filters to entries with ``fail_rate > 0`` and
        ``flake_score < flake_threshold`` (distinguishes broken from flaky).
        """
        candidates = [e for e in self._entries
                      if e.fail_rate > 0 and e.flake_score < flake_threshold]
        return sorted(candidates, key=lambda e: e.fail_rate, reverse=True)[:n]

    @property
    def num_tests(self) -> int:
        return len(self._entries)

    # ── serialization ────────────────────────────────────────────────────────

    def serialize(self) -> bytes:
        """Encode the table to bytes for storage in the ZIP archive."""
        header = _HDR.pack(MAGIC, VERSION, len(self._entries))
        rows = b""
        for e in self._entries:
            rows += _ENTRY.pack(
                e.total_runs, e.pass_count, e.fail_count, e.error_count,
                e.first_ts, e.last_ts, e.last_green_ts, e.transition_count,
                e.streak, e.last_status, 0,            # _pad
                e.flake_score, e.fail_rate,
                e.mean_cpu_time, e.m2_cpu_time,
                e.cusum_value, e.cusum_ref_mean,
                e.grade_score,
                e.total_seeds_seen,
                b"\x00" * 6,                           # _reserved
            )
        return header + rows

    @classmethod
    def deserialize(cls, data: bytes) -> "TestStatsTable":
        """Reconstruct a TestStatsTable from raw bytes.

        Args:
            data: Bytes previously produced by :meth:`serialize`.

        Raises:
            ValueError: if the magic number or version is wrong.
        """
        magic, version, num_tests = _HDR.unpack_from(data, 0)
        if magic != MAGIC:
            raise ValueError(f"Bad magic 0x{magic:08X}, expected 0x{MAGIC:08X}")
        if version != VERSION:
            raise ValueError(f"Unsupported test_stats version {version}")

        tbl = cls()
        offset = _HDR.size
        for name_id in range(num_tests):
            fields = _ENTRY.unpack_from(data, offset)
            offset += _ENTRY.size
            (total_runs, pass_count, fail_count, error_count,
             first_ts, last_ts, last_green_ts, transition_count,
             streak, last_status, _pad,
             flake_score, fail_rate,
             mean_cpu_time, m2_cpu_time,
             cusum_value, cusum_ref_mean,
             grade_score,
             total_seeds_seen,
             _reserved) = fields

            e = TestStatsEntry(
                name_id=name_id,
                total_runs=total_runs,
                pass_count=pass_count,
                fail_count=fail_count,
                error_count=error_count,
                first_ts=first_ts,
                last_ts=last_ts,
                last_green_ts=last_green_ts,
                transition_count=transition_count,
                streak=streak,
                last_status=last_status,
                flake_score=flake_score,
                fail_rate=fail_rate,
                mean_cpu_time=mean_cpu_time,
                m2_cpu_time=m2_cpu_time,
                cusum_value=cusum_value,
                cusum_ref_mean=cusum_ref_mean,
                grade_score=grade_score,
                total_seeds_seen=total_seeds_seen,
            )
            tbl._entries.append(e)
        return tbl

    # ── internal ─────────────────────────────────────────────────────────────

    def _ensure(self, name_id: int) -> None:
        while len(self._entries) <= name_id:
            nid = len(self._entries)
            self._entries.append(TestStatsEntry(name_id=nid))
