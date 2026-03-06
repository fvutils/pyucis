"""
history/NNNNNN.bin — columnar bounded bucket files for test-run records.

Each bucket stores up to HISTORY_BUCKET_MAX_RECORDS test-run records in a
columnar layout optimised for DEFLATE/LZMA compression.  Records within a
bucket are sorted by (name_id, ts).

Binary layout (little-endian, stored compressed inside the ZIP)::

    Header:
      magic           u32   0x48445942  ('HDYB')
      version         u8    1
      num_records     u32
      num_names       u16   unique name_ids in this bucket
      ts_base         u32   unix timestamp of first record

    Name index  (num_names entries, sorted by name_id):
      name_id         u32
      start_row       u32   first record index for this name
      count           u16   number of records for this name

    Seed dictionary (local — enables 1-byte seed references):
      num_seeds       u16
      seed_ids        u32[num_seeds]   global seed_ids from test_registry

    Columns (independent arrays — each compresses optimally):
      seeds[]         u8[num_records]   index into local seed dictionary
      ts_deltas[]     varint[num_records]  seconds since ts_base, delta per name group
      status_flags[]  u8[num_records]   nibble-packed (high=status, low=flags)

Status nibble values: 0=OK 1=FAIL 2=ERROR 3=FATAL 4=COMPILE
Flag bits: bit0=seed_is_hash  bit1=is_rerun  bit2=has_coverage  bit3=was_squashed
"""

from __future__ import annotations

import struct
import zipfile
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple

from ucis.ncdb.constants import (
    HISTORY_BUCKET_MAX_RECORDS,
    HIST_STATUS_OK,
)
from ucis.ncdb.varint import decode_varints, encode_varints

MAGIC   = 0x48445942   # 'HDYB'
VERSION = 1

# Bucket header: magic(4) version(1) num_records(4) num_names(2) pad(1) ts_base(4) = 16 bytes
_BUCKET_HDR  = struct.Struct("<IBIHxI")
# Name index entry: name_id(4) start_row(4) count(2) pad(2) = 12 bytes
_BUCKET_NAME = struct.Struct("<IIHxx")


@dataclass
class BucketRecord:
    """One decoded test-run record from a bucket file."""
    name_id:      int
    seed_id:      int   # global seed_id from test_registry
    ts:           int   # unix timestamp
    status:       int   # HIST_STATUS_*
    flags:        int   # HIST_FLAG_* bits


class BucketWriter:
    """Accumulates test-run records in memory and serialises them on demand.

    Example::

        w = BucketWriter()
        w.add(name_id=0, seed_id=0, ts=1700000000, status=HIST_STATUS_OK, flags=0)
        data = w.seal()   # returns compressed bytes ready for ZIP storage
    """

    def __init__(self) -> None:
        self._records: List[BucketRecord] = []
        # local seed dict: global seed_id → local index (u8, max 255 seeds/bucket)
        self._seed_local: Dict[int, int] = {}
        self._seed_ids: List[int] = []   # local_idx → global seed_id

    def add(self, name_id: int, seed_id: int, ts: int,
            status: int, flags: int) -> None:
        """Append one test-run record.

        Args:
            name_id:  Integer name_id from TestRegistry.
            seed_id:  Integer seed_id from TestRegistry.
            ts:       Unix timestamp.
            status:   HIST_STATUS_* constant.
            flags:    Combination of HIST_FLAG_* bits.
        """
        if seed_id not in self._seed_local:
            idx = len(self._seed_ids)
            if idx >= 255:
                raise OverflowError("Bucket seed dictionary full (255 entries max)")
            self._seed_local[seed_id] = idx
            self._seed_ids.append(seed_id)
        self._records.append(BucketRecord(name_id=name_id, seed_id=seed_id,
                                          ts=ts, status=status, flags=flags))

    @property
    def num_records(self) -> int:
        return len(self._records)

    def is_full(self) -> bool:
        return len(self._records) >= HISTORY_BUCKET_MAX_RECORDS

    def seal(self, use_lzma: bool = True) -> bytes:
        """Serialise and compress the bucket.

        Args:
            use_lzma: If True, attempt LZMA compression; fall back to
                      DEFLATE level 9 if liblzma is unavailable.

        Returns:
            Compressed bytes ready to store as a ZIP member.
        """
        raw = self._encode()
        return _compress(raw, high_quality=True, use_lzma=use_lzma)

    def seal_fast(self) -> bytes:
        """Serialise with fast (DEFLATE level 1) compression for the current-day bucket."""
        raw = self._encode()
        return _compress(raw, high_quality=False, use_lzma=False)

    def _encode(self) -> bytes:
        # Sort records by (name_id, ts)
        records = sorted(self._records, key=lambda r: (r.name_id, r.ts))
        if not records:
            ts_base = 0
        else:
            ts_base = records[0].ts

        # Build name index
        name_groups: Dict[int, List[int]] = {}  # name_id → list of row indices
        for i, r in enumerate(records):
            name_groups.setdefault(r.name_id, []).append(i)

        sorted_names = sorted(name_groups.keys())
        name_index_entries: List[Tuple[int, int, int]] = []
        start_row = 0
        for nid in sorted_names:
            cnt = len(name_groups[nid])
            name_index_entries.append((nid, start_row, cnt))
            start_row += cnt

        num_names = len(sorted_names)
        num_records = len(records)

        # Columns
        seed_col = bytearray()
        ts_delta_values = []
        status_flags_col = bytearray()

        prev_ts_per_name: Dict[int, int] = {}
        for r in records:
            seed_col.append(self._seed_local[r.seed_id])
            prev_ts = prev_ts_per_name.get(r.name_id, ts_base)
            delta = r.ts - prev_ts
            ts_delta_values.append(delta)
            prev_ts_per_name[r.name_id] = r.ts
            sf = ((r.status & 0x0F) << 4) | (r.flags & 0x0F)
            status_flags_col.append(sf)

        ts_delta_col = encode_varints(ts_delta_values)

        # Header: 16 bytes
        header = _BUCKET_HDR.pack(MAGIC, VERSION, num_records, num_names, ts_base)

        # Name index: 12 bytes each
        name_idx_bytes = b""
        for nid, sr, cnt in name_index_entries:
            name_idx_bytes += _BUCKET_NAME.pack(nid, sr, cnt)

        # Seed dict
        num_seeds = len(self._seed_ids)
        seed_dict = struct.pack("<H", num_seeds)
        if self._seed_ids:
            seed_dict += struct.pack(f"<{num_seeds}I", *self._seed_ids)

        return header + name_idx_bytes + seed_dict + bytes(seed_col) + ts_delta_col + bytes(status_flags_col)


class BucketReader:
    """Reads and decodes a compressed bucket file.

    Args:
        data: Compressed bytes as stored in the ZIP archive.

    Example::

        reader = BucketReader(compressed_data)
        for rec in reader.records_for_name(name_id=3):
            print(rec.ts, rec.status)
    """

    def __init__(self, data: bytes) -> None:
        raw = _decompress(data)
        self._parse(raw)

    def _parse(self, raw: bytes) -> None:
        magic, version, num_records, num_names, ts_base = _BUCKET_HDR.unpack_from(raw, 0)
        if magic != MAGIC:
            raise ValueError(f"Bad bucket magic 0x{magic:08X}")
        if version != VERSION:
            raise ValueError(f"Unsupported bucket version {version}")

        self._num_records = num_records
        self._ts_base     = ts_base

        offset = _BUCKET_HDR.size

        # Name index
        self._name_index: List[Tuple[int, int, int]] = []
        for _ in range(num_names):
            nid, sr, cnt = _BUCKET_NAME.unpack_from(raw, offset)
            self._name_index.append((nid, sr, cnt))
            offset += _BUCKET_NAME.size

        # Seed dict
        num_seeds, = struct.unpack_from("<H", raw, offset)
        offset += 2
        if num_seeds:
            seed_ids = list(struct.unpack_from(f"<{num_seeds}I", raw, offset))
            offset += 4 * num_seeds
        else:
            seed_ids = []
        self._seed_ids = seed_ids  # local_idx → global seed_id

        # Columns
        self._seed_col        = raw[offset: offset + num_records]
        offset += num_records
        ts_delta_vals, offset = decode_varints(raw, num_records, offset)
        self._status_flags    = raw[offset: offset + num_records]

        # Reconstruct timestamps
        prev_ts_per_name: Dict[int, int] = {}
        self._records: List[BucketRecord] = []

        # Build name_id per row from name index
        row_name: List[int] = [0] * num_records
        for nid, sr, cnt in self._name_index:
            for i in range(cnt):
                row_name[sr + i] = nid

        for row in range(num_records):
            nid = row_name[row]
            prev_ts = prev_ts_per_name.get(nid, ts_base)
            ts = prev_ts + ts_delta_vals[row]
            prev_ts_per_name[nid] = ts

            local_seed = self._seed_col[row]
            seed_id = self._seed_ids[local_seed] if local_seed < len(self._seed_ids) else 0
            sf = self._status_flags[row]
            status = (sf >> 4) & 0x0F
            flags  = sf & 0x0F

            self._records.append(BucketRecord(
                name_id=nid, seed_id=seed_id, ts=ts, status=status, flags=flags
            ))

    def records_for_name(self, name_id: int) -> List[BucketRecord]:
        """Return all records for *name_id* via binary search on the name index.

        Returns:
            List of BucketRecord (may be empty if name_id not in this bucket).
        """
        # Binary search on sorted name index
        lo, hi = 0, len(self._name_index)
        while lo < hi:
            mid = (lo + hi) // 2
            if self._name_index[mid][0] < name_id:
                lo = mid + 1
            else:
                hi = mid
        if lo >= len(self._name_index) or self._name_index[lo][0] != name_id:
            return []
        _, start_row, count = self._name_index[lo]
        return self._records[start_row: start_row + count]

    def all_records(self) -> Iterable[BucketRecord]:
        """Iterate over all records in row order."""
        return iter(self._records)

    @property
    def num_records(self) -> int:
        return self._num_records


# ── compression helpers ───────────────────────────────────────────────────

def _compress(data: bytes, high_quality: bool, use_lzma: bool) -> bytes:
    """Compress *data* using the best available method.

    For the current-day (mutable) bucket: DEFLATE level 1 (fast).
    For sealed buckets: LZMA if available, else DEFLATE level 9.
    """
    import io
    import zlib

    if not high_quality:
        return zlib.compress(data, level=1)

    if use_lzma:
        try:
            import lzma
            return lzma.compress(data, format=lzma.FORMAT_XZ)
        except (ImportError, lzma.LZMAError):
            pass

    return zlib.compress(data, level=9)


def _decompress(data: bytes) -> bytes:
    """Decompress *data*, auto-detecting LZMA vs DEFLATE."""
    import zlib

    # LZMA/XZ magic: 0xFD 0x37 0x7A 0x58 0x5A 0x00
    if data[:6] == b"\xfd7zXZ\x00":
        try:
            import lzma
            return lzma.decompress(data, format=lzma.FORMAT_XZ)
        except ImportError:
            raise RuntimeError("lzma module not available; cannot decompress sealed bucket")

    return zlib.decompress(data)
