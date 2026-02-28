"""
attrs.json — user-defined attribute serialization.

Format: JSON object
  {"version": 1, "entries": [{"idx": <int>, "attrs": {<key>: <val>}}, ...]}

Only scopes that have at least one attribute are included (sparse).
"""

import json

from .dfs_util import dfs_scope_list

_VERSION = 1


class AttrsWriter:
    """Serialize user-defined scope attributes to attrs.json bytes."""

    def serialize(self, db) -> bytes:
        scopes = dfs_scope_list(db)
        entries = []
        for idx, scope in enumerate(scopes):
            if not hasattr(scope, 'getAttributes'):
                continue
            attrs = scope.getAttributes()
            if attrs:
                entries.append({"idx": idx, "attrs": attrs})
        payload = {"version": _VERSION, "entries": entries}
        return json.dumps(payload, separators=(',', ':')).encode()


class AttrsReader:
    """Deserialize attrs.json bytes and apply attributes to scope tree."""

    def deserialize(self, data: bytes, db) -> None:
        if not data:
            return
        payload = json.loads(data.decode())
        if payload.get("version") != _VERSION:
            raise ValueError(f"Unsupported attrs.json version: {payload.get('version')}")
        entries = payload.get("entries", [])
        if not entries:
            return
        scopes = dfs_scope_list(db)
        for entry in entries:
            idx = entry["idx"]
            if idx < len(scopes):
                scope = scopes[idx]
                for key, val in entry.get("attrs", {}).items():
                    if hasattr(scope, 'setAttribute'):
                        scope.setAttribute(key, val)
