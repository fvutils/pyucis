"""
Deduplicated string table for the NCDB format.

Strings are stored once in strings.bin; all other members reference them
by integer index.  The table is length-prefixed, null-terminated UTF-8.

Binary layout of strings.bin:
  [count: varint]
  [len_0: varint][bytes_0: UTF-8]
  [len_1: varint][bytes_1: UTF-8]
  ...

Indices are 0-based.  Index 0 is always the empty string "".
"""

import io
from .varint import encode_varint, decode_varint


class StringTable:
    """Build, serialize and deserialize the NCDB string table."""

    def __init__(self):
        self._strings: list[str] = []
        self._index: dict[str, int] = {}

    # ── Building ──────────────────────────────────────────────────────────

    def add(self, s: str) -> int:
        """Return the index for *s*, adding it if not already present."""
        if s is None:
            s = ""
        if s not in self._index:
            idx = len(self._strings)
            self._strings.append(s)
            self._index[s] = idx
        return self._index[s]

    def get(self, idx: int) -> str:
        """Return the string at *idx*."""
        return self._strings[idx]

    def __len__(self) -> int:
        return len(self._strings)

    def __iter__(self):
        return iter(self._strings)

    # ── Serialization ─────────────────────────────────────────────────────

    def serialize(self) -> bytes:
        """Encode the string table to bytes."""
        buf = io.BytesIO()
        buf.write(encode_varint(len(self._strings)))
        for s in self._strings:
            encoded = s.encode("utf-8")
            buf.write(encode_varint(len(encoded)))
            buf.write(encoded)
        return buf.getvalue()

    @classmethod
    def from_bytes(cls, data: bytes) -> "StringTable":
        """Decode a string table from bytes."""
        table = cls()
        offset = 0
        count, offset = decode_varint(data, offset)
        for _ in range(count):
            length, offset = decode_varint(data, offset)
            s = data[offset: offset + length].decode("utf-8")
            offset += length
            table.add(s)
        return table
