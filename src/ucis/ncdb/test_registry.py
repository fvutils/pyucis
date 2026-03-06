"""
test_registry.bin — global test-name / seed-id / run-id registry.

Stores each unique test base-name and seed string exactly once and assigns
stable integer IDs that survive ZIP rewrites and merges.  Also holds the
global monotonically-increasing ``run_id`` counter.

Binary layout (little-endian)::

    magic            u32   0x54535452  ('TSTR')
    version          u8    1
    next_run_id      u32
    num_names        u32
    num_seeds        u32
    name_offsets     u32[num_names]    byte offsets into name_heap
    seed_offsets     u32[num_seeds]    byte offsets into seed_heap
    name_heap        bytes             null-terminated UTF-8, in name_id order
    seed_heap        bytes             null-terminated UTF-8, in seed_id order

name_ids are assigned by **insertion order** (first seen = id 0) and are
stable: inserting a new name never shifts existing name_ids.  This ensures
that all bucket files and stats entries remain valid across incremental updates.
Seeds behave identically.
"""

from __future__ import annotations

import struct
from typing import List, Optional

MAGIC   = 0x54535452   # 'TSTR'
VERSION = 1

_HDR = struct.Struct("<IBIII")   # magic, version, next_run_id, num_names, num_seeds


class TestRegistry:
    """In-memory representation of ``test_registry.bin``.

    name_ids and seed_ids are assigned by **insertion order** and are stable:
    adding a new name never changes the id of an existing name.

    Args:
        next_run_id: Starting value for the run-id counter (default 0).

    Example::

        reg = TestRegistry()
        name_id = reg.lookup_name_id("uart_smoke")
        seed_id = reg.lookup_seed_id("12345")
        run_id  = reg.assign_run_id()
        data    = reg.serialize()
        reg2    = TestRegistry.deserialize(data)
    """

    def __init__(self, next_run_id: int = 0) -> None:
        self._next_run_id: int = next_run_id
        # insertion-order list of name strings — index == name_id (STABLE)
        self._names: List[str] = []
        # insertion-order list of seed strings — index == seed_id
        self._seeds: List[str] = []
        # fast reverse-lookup dicts
        self._name_to_id: dict = {}
        self._seed_to_id: dict = {}

    # ── run-id ──────────────────────────────────────────────────────────────

    def assign_run_id(self) -> int:
        """Return the next run_id and advance the counter."""
        rid = self._next_run_id
        self._next_run_id += 1
        return rid

    @property
    def next_run_id(self) -> int:
        return self._next_run_id

    # ── name_id ─────────────────────────────────────────────────────────────

    def lookup_name_id(self, name: str) -> int:
        """Return the name_id for *name*, assigning one if this is a new name.

        name_ids are assigned by insertion order and are stable — inserting a
        new name never changes the id of any existing name.
        """
        if name in self._name_to_id:
            return self._name_to_id[name]
        nid = len(self._names)
        self._names.append(name)
        self._name_to_id[name] = nid
        return nid

    def name_for_id(self, name_id: int) -> str:
        """Return the name string for *name_id*.

        Raises:
            IndexError: if *name_id* is out of range.
        """
        return self._names[name_id]

    @property
    def num_names(self) -> int:
        return len(self._names)

    # ── seed_id ─────────────────────────────────────────────────────────────

    def lookup_seed_id(self, seed: str) -> int:
        """Return the seed_id for *seed*, assigning one if this is a new seed.

        Integer seeds should be passed as their decimal string representation.
        """
        if seed in self._seed_to_id:
            return self._seed_to_id[seed]
        sid = len(self._seeds)
        self._seeds.append(seed)
        self._seed_to_id[seed] = sid
        return sid

    def seed_for_id(self, seed_id: int) -> str:
        """Return the seed string for *seed_id*.

        Raises:
            IndexError: if *seed_id* is out of range.
        """
        return self._seeds[seed_id]

    @property
    def num_seeds(self) -> int:
        return len(self._seeds)

    # ── serialization ───────────────────────────────────────────────────────

    def serialize(self) -> bytes:
        """Encode the registry to bytes for storage in the ZIP archive."""
        # Build string heaps
        name_heap = b"".join(n.encode() + b"\x00" for n in self._names)
        seed_heap = b"".join(s.encode() + b"\x00" for s in self._seeds)

        # Compute offset tables
        name_offsets: List[int] = []
        off = 0
        for n in self._names:
            name_offsets.append(off)
            off += len(n.encode()) + 1

        seed_offsets: List[int] = []
        off = 0
        for s in self._seeds:
            seed_offsets.append(off)
            off += len(s.encode()) + 1

        header = _HDR.pack(MAGIC, VERSION, self._next_run_id,
                           len(self._names), len(self._seeds))
        offsets = (
            struct.pack(f"<{len(name_offsets)}I", *name_offsets)
            if name_offsets else b""
        )
        offsets += (
            struct.pack(f"<{len(seed_offsets)}I", *seed_offsets)
            if seed_offsets else b""
        )
        return header + offsets + name_heap + seed_heap

    @classmethod
    def deserialize(cls, data: bytes) -> "TestRegistry":
        """Reconstruct a TestRegistry from raw bytes.

        Args:
            data: Bytes previously produced by :meth:`serialize`.

        Returns:
            A fully populated TestRegistry instance.

        Raises:
            ValueError: if the magic number or version is wrong.
        """
        magic, version, next_run_id, num_names, num_seeds = _HDR.unpack_from(data, 0)
        if magic != MAGIC:
            raise ValueError(f"Bad magic 0x{magic:08X}, expected 0x{MAGIC:08X}")
        if version != VERSION:
            raise ValueError(f"Unsupported test_registry version {version}")

        offset = _HDR.size

        # Offset tables
        name_offsets = list(struct.unpack_from(f"<{num_names}I", data, offset))
        offset += 4 * num_names
        seed_offsets = list(struct.unpack_from(f"<{num_seeds}I", data, offset))
        offset += 4 * num_seeds

        heap_start = offset

        def _read_string(heap_base: int, str_offset: int) -> str:
            start = heap_base + str_offset
            end = data.index(b"\x00", start)
            return data[start:end].decode()

        # Build name and seed heaps — sizes needed to find seed heap base
        name_heap_size = 0
        names = []
        for i in range(num_names):
            s = _read_string(heap_start, name_offsets[i])
            names.append(s)
            name_heap_size += len(s.encode()) + 1

        seed_heap_base = heap_start + name_heap_size
        seeds = []
        for i in range(num_seeds):
            seeds.append(_read_string(seed_heap_base, seed_offsets[i]))

        reg = cls(next_run_id=next_run_id)
        # Restore directly — names are in name_id (insertion) order
        reg._names = names
        reg._name_to_id = {n: i for i, n in enumerate(names)}
        reg._seeds = seeds
        reg._seed_to_id = {s: i for i, s in enumerate(seeds)}
        return reg
