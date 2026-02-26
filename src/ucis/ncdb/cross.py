"""
cross.json — CROSS scope coverpoint-link serialization.

A UCIS CROSS scope records which coverpoints it crosses.  The coverpoint
references (by object) are lost after scope-tree deserialization because
scope_tree.bin only stores names and structure.  This module persists the
links and restores them by navigating the reconstructed scope tree by path.

Format:
  {"version": 1, "entries": [
    {"idx": <int>, "crossed": ["<sibling_name>", ...]},
    ...
  ]}

*idx* is the DFS index of the CROSS scope.  *crossed* contains the
getScopeName() value of each crossed coverpoint (they must be siblings of
the CROSS scope inside the same COVERINSTANCE or COVERGROUP).
"""

import json

from ucis.scope_type_t import ScopeTypeT

from .dfs_util import dfs_scope_list

_VERSION = 1


class CrossWriter:
    """Serialize CROSS scope coverpoint links to cross.json bytes."""

    def serialize(self, db) -> bytes:
        entries = []
        for idx, scope in enumerate(dfs_scope_list(db)):
            if scope.getScopeType() != ScopeTypeT.CROSS:
                continue
            n = 0
            try:
                n = scope.getNumCrossedCoverpoints()
            except Exception:
                pass
            if n == 0:
                continue
            crossed = [scope.getIthCrossedCoverpoint(i).getScopeName()
                       for i in range(n)]
            entries.append({"idx": idx, "crossed": crossed})

        if not entries:
            return b""
        payload = {"version": _VERSION, "entries": entries}
        return json.dumps(payload, separators=(',', ':')).encode()


class CrossReader:
    """Rebuild CROSS scope coverpoint links from cross.json bytes."""

    def apply(self, db, data: bytes) -> None:
        if not data:
            return
        payload = json.loads(data.decode())
        if payload.get("version") != _VERSION:
            raise ValueError(
                f"Unsupported cross.json version: {payload.get('version')}")
        entries = payload.get("entries", [])
        if not entries:
            return

        scopes = dfs_scope_list(db)
        for entry in entries:
            idx = entry["idx"]
            if idx >= len(scopes):
                continue
            cross_scope = scopes[idx]
            if cross_scope.getScopeType() != ScopeTypeT.CROSS:
                continue

            crossed_names = entry.get("crossed", [])
            if not crossed_names:
                continue

            # Find the parent container and resolve siblings by name
            parent = cross_scope.m_parent if hasattr(cross_scope, 'm_parent') else None
            if parent is None:
                continue

            # Build name → scope map from siblings
            sibling_map = {}
            for sib in parent.scopes(ScopeTypeT.ALL):
                sibling_map[sib.getScopeName()] = sib

            resolved = [sibling_map[name] for name in crossed_names
                        if name in sibling_map]
            if hasattr(cross_scope, 'coverpoints'):
                cross_scope.coverpoints = resolved
