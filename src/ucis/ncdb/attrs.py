"""
attrs.bin — user-defined attribute serialization.

Format v1 (legacy): JSON object
  {"version": 1, "entries": [{"idx": <int>, "attrs": {<key>: <val>}}, ...]}

Format v2 (current): JSON object with sections for scopes, coveritems,
history nodes, and global attrs.
  {"version": 2,
   "scopes": [{"idx": <int>, "attrs": {<key>: <val>}}, ...],
   "coveritems": [{"scope_idx": <int>, "ci_idx": <int>, "attrs": {...}}, ...],
   "history": [{"idx": <int>, "attrs": {...}}, ...],
   "global": {<key>: <val>}}
"""

import json

from .dfs_util import dfs_scope_list
from ucis.history_node_kind import HistoryNodeKind

_VERSION = 2
_COVER_ALL = 0xFFFFFFFF


class AttrsWriter:
    """Serialize user-defined attributes to attrs.bin bytes."""

    def serialize(self, db) -> bytes:
        scopes = dfs_scope_list(db)
        scope_entries = []
        for idx, scope in enumerate(scopes):
            if not hasattr(scope, 'getAttributes'):
                continue
            attrs = scope.getAttributes()
            if attrs:
                scope_entries.append({"idx": idx, "attrs": attrs})

        ci_entries = []
        for idx, scope in enumerate(scopes):
            try:
                items = list(scope.coverItems(_COVER_ALL))
            except Exception:
                continue
            for ci_idx, ci in enumerate(items):
                if not hasattr(ci, 'getAttributes'):
                    continue
                attrs = ci.getAttributes()
                if attrs:
                    ci_entries.append({
                        "scope_idx": idx, "ci_idx": ci_idx, "attrs": attrs
                    })

        hist_entries = []
        for kind in (HistoryNodeKind.TEST, HistoryNodeKind.MERGE):
            try:
                nodes = list(db.historyNodes(kind))
            except Exception:
                continue
            for hi, node in enumerate(nodes):
                if not hasattr(node, 'getAttributes'):
                    continue
                attrs = node.getAttributes()
                if attrs:
                    hist_entries.append({
                        "idx": hi, "kind": kind.name, "attrs": attrs
                    })

        global_attrs = {}
        if hasattr(db, 'getAttributes'):
            global_attrs = db.getAttributes()

        payload = {
            "version": _VERSION,
            "scopes": scope_entries,
            "coveritems": ci_entries,
            "history": hist_entries,
            "global": global_attrs,
        }
        return json.dumps(payload, separators=(',', ':')).encode()


class AttrsReader:
    """Deserialize attrs.bin bytes and apply attributes."""

    def deserialize(self, data: bytes, db) -> None:
        if not data:
            return
        payload = json.loads(data.decode())
        version = payload.get("version", 1)

        if version == 1:
            self._deserialize_v1(payload, db)
        elif version == 2:
            self._deserialize_v2(payload, db)

    def _deserialize_v1(self, payload, db):
        """Legacy v1: scope attrs only."""
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

    def _deserialize_v2(self, payload, db):
        """V2: scopes + coveritems + history + global."""
        scopes = dfs_scope_list(db)

        for entry in payload.get("scopes", []):
            idx = entry["idx"]
            if idx < len(scopes):
                scope = scopes[idx]
                for key, val in entry.get("attrs", {}).items():
                    if hasattr(scope, 'setAttribute'):
                        scope.setAttribute(key, val)

        for entry in payload.get("coveritems", []):
            scope_idx = entry["scope_idx"]
            ci_idx = entry["ci_idx"]
            if scope_idx < len(scopes):
                scope = scopes[scope_idx]
                try:
                    items = list(scope.coverItems(_COVER_ALL))
                    if ci_idx < len(items):
                        ci = items[ci_idx]
                        for key, val in entry.get("attrs", {}).items():
                            if hasattr(ci, 'setAttribute'):
                                ci.setAttribute(key, val)
                except Exception:
                    pass

        hist_nodes = {}
        for kind in (HistoryNodeKind.TEST, HistoryNodeKind.MERGE):
            try:
                hist_nodes[kind.name] = list(db.historyNodes(kind))
            except Exception:
                pass
        for entry in payload.get("history", []):
            kind_name = entry.get("kind", "TEST")
            idx = entry["idx"]
            nodes = hist_nodes.get(kind_name, [])
            if idx < len(nodes):
                node = nodes[idx]
                for key, val in entry.get("attrs", {}).items():
                    if hasattr(node, 'setAttribute'):
                        node.setAttribute(key, val)

        for key, val in payload.get("global", {}).items():
            if hasattr(db, 'setAttribute'):
                db.setAttribute(key, val)

    def apply(self, db, data: bytes) -> None:
        """Alias for deserialize (matches other readers' API)."""
        self.deserialize(data, db)
