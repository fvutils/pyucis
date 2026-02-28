"""
design_units.json — design unit (DU) name-to-scope index.

Provides a fast lookup table mapping DU scope names to their DFS indices so
tools can locate design units without scanning the full scope tree.

Format:
  {"version": 1, "units": [
    {"name": "<str>", "idx": <int>, "type": <int>},
    ...
  ]}

Only DU_ANY scopes are included.  *idx* is the DFS index from dfs_scope_list().
"""

import json

from ucis.scope_type_t import ScopeTypeT

from .dfs_util import dfs_scope_list

_VERSION = 1


class DesignUnitsWriter:
    """Serialize DU scope index to design_units.json bytes."""

    def serialize(self, db) -> bytes:
        units = []
        for idx, scope in enumerate(dfs_scope_list(db)):
            scope_type = scope.getScopeType()
            if ScopeTypeT.DU_ANY(scope_type):
                units.append({
                    "name": scope.getScopeName(),
                    "idx":  idx,
                    "type": int(scope_type),
                })
        if not units:
            return b""
        payload = {"version": _VERSION, "units": units}
        return json.dumps(payload, separators=(',', ':')).encode()


class DesignUnitsReader:
    """Deserialize design_units.json and build a name → scope lookup."""

    def build_index(self, data: bytes, db) -> dict:
        """Return a {name: scope} dict from design_units.json *data*.

        Falls back to scanning dfs_scope_list() when *data* is empty so the
        method always returns a usable index.
        """
        if data:
            payload = json.loads(data.decode())
            if payload.get("version") == _VERSION:
                scopes = dfs_scope_list(db)
                index = {}
                for entry in payload.get("units", []):
                    idx = entry["idx"]
                    if idx < len(scopes):
                        index[entry["name"]] = scopes[idx]
                return index

        # Fallback: linear scan (used when design_units.json absent)
        index = {}
        for scope in dfs_scope_list(db):
            if ScopeTypeT.DU_ANY(scope.getScopeType()):
                index[scope.getScopeName()] = scope
        return index
