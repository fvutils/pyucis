"""
tags.json — scope tag serialization.

Format: JSON object
  {"version": 1, "entries": [{"idx": <int>, "tags": [<tag>, ...]}, ...]}

Only scopes that have at least one tag are included (sparse).
"""

import json

from .dfs_util import dfs_scope_list

_VERSION = 1


class TagsWriter:
    """Serialize scope tags to tags.json bytes."""

    def serialize(self, db) -> bytes:
        scopes = dfs_scope_list(db)
        entries = []
        for idx, scope in enumerate(scopes):
            if not hasattr(scope, 'getTags'):
                continue
            tags = list(scope.getTags()) if scope.getTags() is not None else []
            if tags:
                entries.append({"idx": idx, "tags": tags})
        payload = {"version": _VERSION, "entries": entries}
        return json.dumps(payload, separators=(',', ':')).encode()


class TagsReader:
    """Deserialize tags.json bytes and apply tags to scope tree."""

    def deserialize(self, data: bytes, db) -> None:
        if not data:
            return
        payload = json.loads(data.decode())
        if payload.get("version") != _VERSION:
            raise ValueError(f"Unsupported tags.json version: {payload.get('version')}")
        entries = payload.get("entries", [])
        if not entries:
            return
        scopes = dfs_scope_list(db)
        for entry in entries:
            idx = entry["idx"]
            if idx < len(scopes):
                scope = scopes[idx]
                if hasattr(scope, 'addTag'):
                    for tag in entry.get("tags", []):
                        scope.addTag(tag)
