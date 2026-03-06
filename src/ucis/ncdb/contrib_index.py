"""
contrib_index.bin — pass-only merge support index.

Every test run that produced coverage data has an 8-byte entry here.  Status
is cached so merge decisions require no bucket scanning.

Binary layout (little-endian)::

    magic            u32   0x43494458  ('CIDX')
    version          u8    1
    merge_policy     u8    0=all  1=pass_only  2=exclude_error_and_rerun  3=strict
    squash_watermark u32   highest run_id already baked into counts.bin
    num_active       u32   number of entries (not yet squashed)

    entries[num_active]:   sorted by run_id
      run_id    u32
      name_id   u16
      status    u8
      flags     u8         bit0=is_rerun  bit1=first_attempt_passed

8 bytes per entry.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import List

from ucis.ncdb.constants import (
    HIST_STATUS_OK,
    HIST_FLAG_IS_RERUN,
)

MAGIC   = 0x43494458   # 'CIDX'
VERSION = 1

# Merge policies
POLICY_ALL                   = 0
POLICY_PASS_ONLY             = 1
POLICY_EXCLUDE_ERROR_RERUN   = 2
POLICY_STRICT                = 3   # exclude coverage from tests that only pass on retry

# contrib_index entry flags
FLAG_IS_RERUN              = 0x01
FLAG_FIRST_ATTEMPT_PASSED  = 0x02

_HDR   = struct.Struct("<IBBII")   # magic, version, policy, watermark, num_active
_ENTRY = struct.Struct("<IHBB")    # run_id, name_id, status, flags


@dataclass
class ContribIndexEntry:
    """One entry in the contrib index."""
    run_id:               int
    name_id:              int
    status:               int
    flags:                int

    @property
    def is_rerun(self) -> bool:
        return bool(self.flags & FLAG_IS_RERUN)

    @property
    def first_attempt_passed(self) -> bool:
        return bool(self.flags & FLAG_FIRST_ATTEMPT_PASSED)


class ContribIndex:
    """In-memory representation of ``contrib_index.bin``.

    Example::

        ci = ContribIndex()
        ci.add_entry(run_id=0, name_id=0, status=HIST_STATUS_OK, flags=0)
        ci.add_entry(run_id=1, name_id=1, status=HIST_STATUS_FAIL, flags=0)
        passing = ci.passing_run_ids(policy=POLICY_PASS_ONLY)   # [0]
    """

    def __init__(self, merge_policy: int = POLICY_PASS_ONLY,
                 squash_watermark: int = 0) -> None:
        self.merge_policy     = merge_policy
        self.squash_watermark = squash_watermark
        self._entries: List[ContribIndexEntry] = []

    def add_entry(self, run_id: int, name_id: int,
                  status: int, flags: int) -> None:
        """Append a new contrib entry.  Entries are kept sorted by run_id."""
        entry = ContribIndexEntry(run_id=run_id, name_id=name_id,
                                  status=status, flags=flags)
        # Append in order (run_ids are monotonically increasing in normal use)
        if self._entries and self._entries[-1].run_id >= run_id:
            # Insert in sorted position if out of order (e.g. after merge)
            for i, e in enumerate(self._entries):
                if e.run_id > run_id:
                    self._entries.insert(i, entry)
                    return
        self._entries.append(entry)

    def passing_run_ids(self, policy: int = POLICY_PASS_ONLY) -> List[int]:
        """Return run_ids that pass the given merge policy filter.

        Policies:
            POLICY_ALL                 — all entries
            POLICY_PASS_ONLY           — status == OK
            POLICY_EXCLUDE_ERROR_RERUN — status == OK
            POLICY_STRICT              — status == OK and not (is_rerun and not first_attempt_passed)
        """
        result = []
        for e in self._entries:
            if policy == POLICY_ALL:
                result.append(e.run_id)
            elif policy == POLICY_PASS_ONLY:
                if e.status == HIST_STATUS_OK:
                    result.append(e.run_id)
            elif policy == POLICY_EXCLUDE_ERROR_RERUN:
                if e.status == HIST_STATUS_OK:
                    result.append(e.run_id)
            elif policy == POLICY_STRICT:
                if e.status == HIST_STATUS_OK:
                    # Exclude coverage from tests that only ever pass on retry
                    if e.is_rerun and not e.first_attempt_passed:
                        continue
                    result.append(e.run_id)
        return result

    def set_squash_watermark(self, run_id: int) -> None:
        """Advance the squash watermark to *run_id*."""
        self.squash_watermark = run_id

    def remove_entries_up_to(self, run_id: int) -> None:
        """Remove all entries with run_id ≤ *run_id* (called after squash)."""
        self._entries = [e for e in self._entries if e.run_id > run_id]

    def max_run_id(self) -> int:
        """Return the highest run_id in active entries, or squash_watermark."""
        if self._entries:
            return max(e.run_id for e in self._entries)
        return self.squash_watermark

    @property
    def num_active(self) -> int:
        return len(self._entries)

    # ── serialization ─────────────────────────────────────────────────────

    def serialize(self) -> bytes:
        """Encode the index to bytes for storage in the ZIP archive."""
        header = _HDR.pack(MAGIC, VERSION, self.merge_policy,
                           self.squash_watermark, len(self._entries))
        rows = b""
        for e in self._entries:
            rows += _ENTRY.pack(e.run_id, e.name_id, e.status, e.flags)
        return header + rows

    @classmethod
    def deserialize(cls, data: bytes) -> "ContribIndex":
        """Reconstruct a ContribIndex from raw bytes.

        Raises:
            ValueError: if magic or version is wrong.
        """
        magic, version, merge_policy, squash_watermark, num_active = \
            _HDR.unpack_from(data, 0)
        if magic != MAGIC:
            raise ValueError(f"Bad magic 0x{magic:08X}, expected 0x{MAGIC:08X}")
        if version != VERSION:
            raise ValueError(f"Unsupported contrib_index version {version}")

        ci = cls(merge_policy=merge_policy, squash_watermark=squash_watermark)
        offset = _HDR.size
        for _ in range(num_active):
            run_id, name_id, status, flags = _ENTRY.unpack_from(data, offset)
            offset += _ENTRY.size
            ci._entries.append(ContribIndexEntry(
                run_id=run_id, name_id=name_id, status=status, flags=flags
            ))
        return ci
