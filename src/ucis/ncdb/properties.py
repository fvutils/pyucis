"""
properties.json — typed UCIS scope/coveritem/history property serialization.

Format: JSON object
  {"version": 1, "entries": [
    {"kind": "scope", "idx": <int>, "key": <int>, "type": "str"|"int"|"real", "value": <val>},
    ...
  ]}

Only objects that have at least one explicitly-set property are included (sparse).

Scope entries use the DFS index from dfs_scope_list().
Coveritem and history entries are not yet implemented.

String properties are serialized from MemObj._str_properties when the scope
is a MemObj subclass.  For non-MemObj scopes (e.g. SqliteScope), only
StrProperty.COMMENT is queried via the standard getStringProperty() API.
"""

import json

from ucis.str_property import StrProperty
from ucis.ncdb.dfs_util import dfs_scope_list

_VERSION = 1

# Fallback: non-MemObj scopes — probe only COMMENT (the common case).
_PROBE_STR_PROPERTIES = (StrProperty.COMMENT,)


class PropertiesWriter:
    """Serialize scope properties to properties.json bytes."""

    def serialize(self, db) -> bytes:
        scopes = dfs_scope_list(db)
        entries = []
        for idx, scope in enumerate(scopes):
            sp = self._get_str_properties(scope)
            for key, val in sp:
                entries.append({
                    "kind": "scope",
                    "idx":  idx,
                    "key":  int(key),
                    "type": "str",
                    "value": val,
                })
        if not entries:
            return b""
        payload = {"version": _VERSION, "entries": entries}
        return json.dumps(payload, separators=(',', ':')).encode()

    def _get_str_properties(self, scope):
        """Yield (StrProperty, value) pairs that are explicitly set on *scope*."""
        # Fast path: MemObj subclasses store string properties in a plain dict.
        sp_dict = getattr(scope, '_str_properties', None)
        if sp_dict is not None:
            for k, v in sp_dict.items():
                if v is not None:
                    yield (k, v)
            return
        # Slow path: probe via public API for a small set of common properties.
        for prop in _PROBE_STR_PROPERTIES:
            try:
                val = scope.getStringProperty(-1, prop)
            except Exception:
                val = None
            if val is not None:
                yield (prop, val)


class PropertiesReader:
    """Deserialize properties.json and apply properties to the scope tree."""

    def apply(self, db, data: bytes) -> None:
        if not data:
            return
        payload = json.loads(data.decode())
        if payload.get("version") != _VERSION:
            raise ValueError(
                f"Unsupported properties.json version: {payload.get('version')}")
        entries = payload.get("entries", [])
        if not entries:
            return
        scopes = dfs_scope_list(db)
        for entry in entries:
            kind = entry.get("kind")
            if kind != "scope":
                continue  # coveritem / history not yet supported
            idx = entry["idx"]
            if idx >= len(scopes):
                continue
            scope = scopes[idx]
            prop_type = entry.get("type", "str")
            key_int   = entry["key"]
            value     = entry["value"]
            if prop_type == "str":
                try:
                    prop = StrProperty(key_int)
                    scope.setStringProperty(-1, prop, value)
                except (ValueError, Exception):
                    pass
