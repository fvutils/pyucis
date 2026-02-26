"""
toggle.json — TOGGLE scope metadata serialization.

Persists per-toggle-scope fields that are not encoded in scope_tree.bin:
  - canonical name   (full hierarchical signal path)
  - toggle metric    (ToggleMetricT enum value)
  - toggle type      (ToggleTypeT enum value)
  - toggle direction (ToggleDirT enum value)

Format:
  {"version": 1, "entries": [
    {"idx": <int>, "canonical": "<str>", "metric": <int>,
     "type": <int>, "dir": <int>},
    ...
  ]}

Only TOGGLE scopes with at least one non-default value are included (sparse).
DFS index corresponds to dfs_scope_list() order (same as scope_tree.bin).
"""

import json

from ucis.scope_type_t import ScopeTypeT
from ucis.toggle_dir_t import ToggleDirT
from ucis.toggle_metric_t import ToggleMetricT
from ucis.toggle_type_t import ToggleTypeT

from .dfs_util import dfs_scope_list

_VERSION = 1

# MemToggleScope defaults — matching __init__ in mem_toggle_scope.py
_DEFAULT_METRIC = int(ToggleMetricT._2STOGGLE)
_DEFAULT_TYPE   = int(ToggleTypeT.NET)
_DEFAULT_DIR    = int(ToggleDirT.INTERNAL)


class ToggleWriter:
    """Serialize TOGGLE-scope metadata to toggle.json bytes."""

    def serialize(self, db) -> bytes:
        scopes  = dfs_scope_list(db)
        entries = []
        for idx, scope in enumerate(scopes):
            if scope.getScopeType() != ScopeTypeT.TOGGLE:
                continue
            entry = self._build_entry(idx, scope)
            if entry:
                entries.append(entry)
        if not entries:
            return b""
        payload = {"version": _VERSION, "entries": entries}
        return json.dumps(payload, separators=(',', ':')).encode()

    def _build_entry(self, idx, scope) -> dict:
        entry = {"idx": idx}
        changed = False

        # Canonical name — stored on MemToggleScope as _canonical_name
        canonical = None
        if hasattr(scope, '_canonical_name'):
            canonical = scope._canonical_name
        elif hasattr(scope, 'getCanonicalName'):
            canonical = scope.getCanonicalName()
        scope_name = scope.getScopeName()
        if canonical and canonical != scope_name:
            entry["canonical"] = canonical
            changed = True

        # Toggle metric
        metric = None
        if hasattr(scope, '_toggle_metric') and scope._toggle_metric is not None:
            metric = int(scope._toggle_metric)
        elif hasattr(scope, 'getToggleMetric'):
            try:
                val = scope.getToggleMetric()
                metric = int(val) if val is not None else None
            except Exception:
                pass
        if metric is not None and metric != _DEFAULT_METRIC:
            entry["metric"] = metric
            changed = True

        # Toggle type
        ttype = None
        if hasattr(scope, '_toggle_type') and scope._toggle_type is not None:
            ttype = int(scope._toggle_type)
        elif hasattr(scope, 'getToggleType'):
            try:
                val = scope.getToggleType()
                ttype = int(val) if val is not None else None
            except Exception:
                pass
        if ttype is not None and ttype != _DEFAULT_TYPE:
            entry["type"] = ttype
            changed = True

        # Toggle direction
        tdir = None
        if hasattr(scope, '_toggle_dir') and scope._toggle_dir is not None:
            tdir = int(scope._toggle_dir)
        elif hasattr(scope, 'getToggleDir'):
            try:
                val = scope.getToggleDir()
                tdir = int(val) if val is not None else None
            except Exception:
                pass
        if tdir is not None and tdir != _DEFAULT_DIR:
            entry["dir"] = tdir
            changed = True

        return entry if changed else None


class ToggleReader:
    """Deserialize toggle.json bytes and apply metadata to TOGGLE scopes."""

    def apply(self, db, data: bytes) -> None:
        if not data:
            return
        payload = json.loads(data.decode())
        if payload.get("version") != _VERSION:
            raise ValueError(
                f"Unsupported toggle.json version: {payload.get('version')}")
        entries = payload.get("entries", [])
        if not entries:
            return
        scopes = dfs_scope_list(db)
        for entry in entries:
            idx = entry["idx"]
            if idx >= len(scopes):
                continue
            scope = scopes[idx]
            if scope.getScopeType() != ScopeTypeT.TOGGLE:
                continue
            if "canonical" in entry and hasattr(scope, 'setCanonicalName'):
                scope.setCanonicalName(entry["canonical"])
            if "metric" in entry and hasattr(scope, 'setToggleMetric'):
                try:
                    scope.setToggleMetric(ToggleMetricT(entry["metric"]))
                except (ValueError, Exception):
                    pass
            if "type" in entry and hasattr(scope, 'setToggleType'):
                try:
                    scope.setToggleType(ToggleTypeT(entry["type"]))
                except (ValueError, Exception):
                    pass
            if "dir" in entry and hasattr(scope, 'setToggleDir'):
                try:
                    scope.setToggleDir(ToggleDirT(entry["dir"]))
                except (ValueError, Exception):
                    pass
