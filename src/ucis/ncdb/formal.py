"""
formal.bin — formal verification data serialization.

Stores per-coveritem formal results (status, proof radius, witness file path)
for assertion scopes.  Only non-default entries are serialized (sparse).

Format (JSON, gzip-compressed):
  {"version": 1, "entries": [
    {"idx": <bin_index>, "status": <int>, "radius": <int>, "witness": "<str>"},
    ...
  ]}

Default values (omitted from JSON):
  status  = 0  (FormalStatusT.NONE)
  radius  = 0
  witness = null (absent)

The bin_index is the flat DFS coveritem index — same ordering as counts.bin.
"""

import json

from .constants import MEMBER_FORMAL

_VERSION = 1
_DEFAULT_STATUS  = 0   # FormalStatusT.NONE
_DEFAULT_RADIUS  = 0


class FormalWriter:
    """Serialize formal data from MemUCIS._formal_data to formal.bin bytes."""

    def serialize(self, db) -> bytes:
        """Return JSON bytes for all non-default formal entries.

        Returns empty bytes when no formal data is present.
        """
        formal_data = getattr(db, '_formal_data', {})
        entries = []
        for bin_index, fd in sorted(formal_data.items()):
            status  = fd.get('status',  _DEFAULT_STATUS)
            radius  = fd.get('radius',  _DEFAULT_RADIUS)
            witness = fd.get('witness', None)
            # Skip fully-default entries
            if status == _DEFAULT_STATUS and radius == _DEFAULT_RADIUS and witness is None:
                continue
            entry = {"idx": bin_index}
            if status != _DEFAULT_STATUS:
                entry["status"] = status
            if radius != _DEFAULT_RADIUS:
                entry["radius"] = radius
            if witness is not None:
                entry["witness"] = witness
            entries.append(entry)
        if not entries:
            return b""
        payload = {"version": _VERSION, "entries": entries}
        return json.dumps(payload, separators=(',', ':')).encode()


class FormalReader:
    """Deserialize formal.bin and populate MemUCIS._formal_data."""

    def apply(self, db, data: bytes) -> None:
        """Parse *data* (formal.bin bytes) and call db.set_formal_data().

        No-op when *data* is empty.
        """
        if not data:
            return
        payload = json.loads(data.decode())
        if payload.get("version") != _VERSION:
            return
        for entry in payload.get("entries", []):
            bin_index = entry["idx"]
            db.set_formal_data(
                bin_index,
                status  = entry.get("status"),
                radius  = entry.get("radius"),
                witness = entry.get("witness"),
            )
