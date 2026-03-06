"""
squash_log.bin — append-only audit trail of squash operations.

Each squash event is recorded permanently so coverage provenance can be
reconstructed: "was counts.bin built from passing tests only?"

Binary layout (little-endian)::

    magic         u32   0x53514C47  ('SQLG')
    version       u8    1
    num_squashes  u32

    entries[num_squashes]:
      ts          u32   unix timestamp of squash
      policy      u8    0=all  1=pass_only  2=exclude_error_and_rerun  3=strict
      _pad        u8[3]
      from_run    u32   first run_id included in squash
      to_run      u32   new squash_watermark after this operation
      num_runs    u32   total runs considered
      pass_runs   u32   passing runs included in counts.bin contribution

24 bytes per entry.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import List

MAGIC   = 0x53514C47   # 'SQLG'
VERSION = 1

_HDR   = struct.Struct("<IBI")          # magic, version, num_squashes
_ENTRY = struct.Struct("<IB3xIIII")     # ts, policy, pad(3), from_run, to_run, num_runs, pass_runs
assert _ENTRY.size == 24  # 4+1+3+4+4+4+4 = 24


@dataclass
class SquashLogEntry:
    """One recorded squash operation."""
    ts:        int   # unix timestamp
    policy:    int   # POLICY_* constant from contrib_index
    from_run:  int   # first run_id included
    to_run:    int   # new squash_watermark
    num_runs:  int   # total runs considered
    pass_runs: int   # passing runs contributing to counts.bin


class SquashLog:
    """In-memory representation of ``squash_log.bin``.

    Entries are append-only — never modified or deleted after writing.

    Example::

        log = SquashLog()
        log.append(ts=1700000000, policy=1, from_run=0, to_run=99,
                   num_runs=100, pass_runs=95)
        data = log.serialize()
        log2 = SquashLog.deserialize(data)
    """

    def __init__(self) -> None:
        self._entries: List[SquashLogEntry] = []

    def append(self, ts: int, policy: int, from_run: int, to_run: int,
               num_runs: int, pass_runs: int) -> None:
        """Record a squash event.

        Args:
            ts:        Unix timestamp of the squash.
            policy:    Merge policy applied (POLICY_* from contrib_index).
            from_run:  First run_id included in this squash.
            to_run:    New squash_watermark after this operation.
            num_runs:  Total run_ids considered during squash.
            pass_runs: Number of passing runs whose contrib was included.
        """
        self._entries.append(SquashLogEntry(
            ts=ts, policy=policy, from_run=from_run, to_run=to_run,
            num_runs=num_runs, pass_runs=pass_runs,
        ))

    def entries(self) -> List[SquashLogEntry]:
        """Return all squash log entries in chronological order."""
        return list(self._entries)

    @property
    def num_squashes(self) -> int:
        return len(self._entries)

    # ── serialization ─────────────────────────────────────────────────────

    def serialize(self) -> bytes:
        """Encode the log to bytes for storage in the ZIP archive."""
        header = _HDR.pack(MAGIC, VERSION, len(self._entries))
        rows = b""
        for e in self._entries:
            rows += _ENTRY.pack(e.ts, e.policy, e.from_run, e.to_run,
                                e.num_runs, e.pass_runs)
        return header + rows

    @classmethod
    def deserialize(cls, data: bytes) -> "SquashLog":
        """Reconstruct a SquashLog from raw bytes.

        Raises:
            ValueError: if magic or version is wrong.
        """
        magic, version, num_squashes = _HDR.unpack_from(data, 0)
        if magic != MAGIC:
            raise ValueError(f"Bad magic 0x{magic:08X}, expected 0x{MAGIC:08X}")
        if version != VERSION:
            raise ValueError(f"Unsupported squash_log version {version}")

        log = cls()
        offset = _HDR.size
        for _ in range(num_squashes):
            ts, policy, from_run, to_run, num_runs, pass_runs = \
                _ENTRY.unpack_from(data, offset)
            offset += _ENTRY.size
            log._entries.append(SquashLogEntry(
                ts=ts, policy=policy, from_run=from_run, to_run=to_run,
                num_runs=num_runs, pass_runs=pass_runs,
            ))
        return log
