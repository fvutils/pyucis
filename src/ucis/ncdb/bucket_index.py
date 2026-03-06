"""
history/bucket_index.bin — index mapping bucket sequence numbers to date
ranges and aggregate counts.

This 24-byte-per-entry index allows regression trend queries and targeted
bucket reads without opening individual bucket files.

Binary layout (little-endian)::

    magic         u32   0x42494458  ('BIDX')
    version       u8    1
    num_buckets   u32

    entries[num_buckets]:     sorted by bucket_seq
      bucket_seq   u32
      ts_start     u32   unix timestamp of first record in bucket
      ts_end       u32   unix timestamp of last record in bucket
      num_records  u32
      fail_count   u32   enables pass-rate trend without opening bucket
      min_name_id  u32
      max_name_id  u32

24 bytes per entry.  3650 entries (10 years) ≈ 87 KB.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import List, Optional, Tuple

MAGIC   = 0x42494458   # 'BIDX'
VERSION = 1

_HDR   = struct.Struct("<IBI")    # magic, version, num_buckets
_ENTRY = struct.Struct("<IIIIIII")  # 7 × u32 = 28 bytes ... wait, design says 24 bytes
# Design: bucket_seq(4) ts_start(4) ts_end(4) num_records(4) fail_count(4) min_name_id(4) max_name_id(4) = 28 bytes
# The design doc says "24 bytes/entry" but lists 7 fields × 4 bytes = 28. We use 28 (correct).
assert _ENTRY.size == 28


@dataclass
class BucketIndexEntry:
    """One entry in the bucket index."""
    bucket_seq:  int
    ts_start:    int
    ts_end:      int
    num_records: int
    fail_count:  int
    min_name_id: int
    max_name_id: int

    @property
    def pass_rate(self) -> float:
        if self.num_records == 0:
            return 1.0
        return (self.num_records - self.fail_count) / self.num_records


class BucketIndex:
    """In-memory representation of ``history/bucket_index.bin``.

    Example::

        idx = BucketIndex()
        idx.add_bucket(seq=0, ts_start=1700000000, ts_end=1700086399,
                       num_records=5000, fail_count=12,
                       min_name_id=0, max_name_id=99)
        data = idx.serialize()
        idx2 = BucketIndex.deserialize(data)
    """

    def __init__(self) -> None:
        self._entries: List[BucketIndexEntry] = []

    def add_bucket(self, seq: int, ts_start: int, ts_end: int,
                   num_records: int, fail_count: int,
                   min_name_id: int, max_name_id: int) -> None:
        """Add or update the index entry for bucket *seq*.

        Entries are kept sorted by *seq*.
        """
        entry = BucketIndexEntry(
            bucket_seq=seq, ts_start=ts_start, ts_end=ts_end,
            num_records=num_records, fail_count=fail_count,
            min_name_id=min_name_id, max_name_id=max_name_id,
        )
        # Replace existing or insert in sorted order
        for i, e in enumerate(self._entries):
            if e.bucket_seq == seq:
                self._entries[i] = entry
                return
            if e.bucket_seq > seq:
                self._entries.insert(i, entry)
                return
        self._entries.append(entry)

    def buckets_in_range(self, ts_from: int, ts_to: int) -> List[BucketIndexEntry]:
        """Return entries whose time range overlaps [ts_from, ts_to]."""
        return [e for e in self._entries
                if e.ts_end >= ts_from and e.ts_start <= ts_to]

    def buckets_for_name(self, name_id: int,
                         ts_from: Optional[int] = None,
                         ts_to:   Optional[int] = None) -> List[BucketIndexEntry]:
        """Return entries that may contain records for *name_id*.

        Filters by ``min_name_id ≤ name_id ≤ max_name_id`` and optionally
        by time range.
        """
        results = []
        for e in self._entries:
            if e.min_name_id > name_id or e.max_name_id < name_id:
                continue
            if ts_from is not None and e.ts_end < ts_from:
                continue
            if ts_to is not None and e.ts_start > ts_to:
                continue
            results.append(e)
        return results

    def pass_rate_series(self) -> List[Tuple[int, float]]:
        """Return ``(ts_start, pass_rate)`` pairs for all buckets in order."""
        return [(e.ts_start, e.pass_rate) for e in self._entries]

    @property
    def num_buckets(self) -> int:
        return len(self._entries)

    def next_seq(self) -> int:
        """Return the sequence number for the next new bucket."""
        if not self._entries:
            return 0
        return self._entries[-1].bucket_seq + 1

    # ── serialization ─────────────────────────────────────────────────────

    def serialize(self) -> bytes:
        """Encode the index to bytes for storage in the ZIP archive."""
        header = _HDR.pack(MAGIC, VERSION, len(self._entries))
        rows = b""
        for e in self._entries:
            rows += _ENTRY.pack(e.bucket_seq, e.ts_start, e.ts_end,
                                e.num_records, e.fail_count,
                                e.min_name_id, e.max_name_id)
        return header + rows

    @classmethod
    def deserialize(cls, data: bytes) -> "BucketIndex":
        """Reconstruct a BucketIndex from raw bytes.

        Raises:
            ValueError: if magic or version is wrong.
        """
        magic, version, num_buckets = _HDR.unpack_from(data, 0)
        if magic != MAGIC:
            raise ValueError(f"Bad magic 0x{magic:08X}, expected 0x{MAGIC:08X}")
        if version != VERSION:
            raise ValueError(f"Unsupported bucket_index version {version}")

        idx = cls()
        offset = _HDR.size
        for _ in range(num_buckets):
            fields = _ENTRY.unpack_from(data, offset)
            offset += _ENTRY.size
            idx._entries.append(BucketIndexEntry(
                bucket_seq=fields[0], ts_start=fields[1], ts_end=fields[2],
                num_records=fields[3], fail_count=fields[4],
                min_name_id=fields[5], max_name_id=fields[6],
            ))
        return idx
