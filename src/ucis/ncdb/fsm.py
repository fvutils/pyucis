"""
fsm.json — FSM scope metadata serialization.

The FSM state/transition names and hit counts are already encoded in
scope_tree.bin as FSMBIN cover items inside FSM_STATES / FSM_TRANS sub-scopes.
What is NOT encoded there:

  1. The numeric state-value/index for each state
     (UCIS_INTPROP_FSM_STATEVAL — maps state names to RTL enumeration values).
  2. The MemFSMScope._states and ._transitions dicts are empty after
     deserialisation because the scope-tree reader only creates cover items.

This module handles both:

  * FsmWriter — serializes non-sequential state indices to fsm.json (sparse;
    absent when all indices match the default 0, 1, 2, … sequence).
  * FsmReader — rebuilds _states/_transitions from the existing cover items
    in FSM_STATES/FSM_TRANS sub-scopes, then applies any stored index overrides.

Format (sparse):
  {"version": 1, "entries": [
    {"fsm_idx": <int>, "states": [{"name": "<str>", "index": <int>}, ...]},
    ...
  ]}

Only FSM scopes whose state indices differ from 0, 1, 2, … are included.
DFS index (fsm_idx) corresponds to dfs_scope_list() order.
"""

import json

from ucis.scope_type_t import ScopeTypeT
from ucis.cover_type_t import CoverTypeT

from .dfs_util import dfs_scope_list

_VERSION = 1


def _fsm_scopes(db):
    """Yield (dfs_idx, scope) for every FSM scope in DFS order."""
    for idx, scope in enumerate(dfs_scope_list(db)):
        if scope.getScopeType() == ScopeTypeT.FSM:
            yield idx, scope


class FsmWriter:
    """Serialize FSM state-index overrides to fsm.json bytes.

    Returns empty bytes when all state indices follow the default
    0, 1, 2, … sequence (the common case).
    """

    def serialize(self, db) -> bytes:
        entries = []
        for fsm_idx, scope in _fsm_scopes(db):
            # Collect state indices from the _states dict (MemFSMScope).
            states_dict = getattr(scope, '_states', None)
            if not states_dict:
                continue
            state_entries = []
            for i, (name, state) in enumerate(states_dict.items()):
                idx = getattr(state, 'index', i)
                if idx != i:  # non-sequential → store
                    state_entries.append({"name": name, "index": idx})
            if state_entries:
                entries.append({"fsm_idx": fsm_idx, "states": state_entries})

        if not entries:
            return b""
        payload = {"version": _VERSION, "entries": entries}
        return json.dumps(payload, separators=(',', ':')).encode()


class FsmReader:
    """Rebuild MemFSMScope._states/_transitions and apply stored index overrides.

    Called after the scope tree has been fully deserialized.  Requires that
    FSM_STATES and FSM_TRANS sub-scopes already hold the correct FSMBIN cover
    items (guaranteed by scope_tree.py).
    """

    def apply(self, db, data: bytes) -> None:
        # Build index override map from stored JSON (may be empty)
        index_overrides: dict = {}  # fsm_idx -> {state_name -> index}
        if data:
            payload = json.loads(data.decode())
            if payload.get("version") != _VERSION:
                raise ValueError(
                    f"Unsupported fsm.json version: {payload.get('version')}")
            for entry in payload.get("entries", []):
                idx_map = {s["name"]: s["index"]
                           for s in entry.get("states", [])}
                index_overrides[entry["fsm_idx"]] = idx_map

        # Rebuild _states / _transitions for every MemFSMScope
        for fsm_idx, scope in _fsm_scopes(db):
            if not (hasattr(scope, '_states') and hasattr(scope, '_transitions')):
                continue
            self._rebuild(scope, index_overrides.get(fsm_idx, {}))

    def _rebuild(self, fsm_scope, index_overrides: dict) -> None:
        """Populate _states/_transitions from existing cover items."""
        from ucis.mem.mem_fsm_scope import MemFSMState, MemFSMTransition

        # Locate the mandatory sub-scopes
        states_scope = getattr(fsm_scope, '_states_scope', None)
        trans_scope  = getattr(fsm_scope, '_trans_scope', None)

        if states_scope is None or trans_scope is None:
            # Fall back: find by scope type
            for child in fsm_scope.scopes(ScopeTypeT.ALL):
                if child.getScopeType() == ScopeTypeT.FSM_STATES:
                    states_scope = child
                elif child.getScopeType() == ScopeTypeT.FSM_TRANS:
                    trans_scope = child

        if states_scope is None:
            return

        # Rebuild _states from FSM_STATES cover items
        fsm_scope._states = {}
        for i, ci in enumerate(states_scope.coverItems(CoverTypeT.ALL)):
            name = ci.getName()
            override_idx = index_overrides.get(name, i)
            state = MemFSMState(name, override_idx)
            state.visit_count = ci.getCoverData().data
            fsm_scope._states[name] = state

        # Rebuild _transitions from FSM_TRANS cover items
        fsm_scope._transitions = {}
        if trans_scope is not None:
            for ci in trans_scope.coverItems(CoverTypeT.ALL):
                name = ci.getName()
                if "->" not in name:
                    continue
                from_name, to_name = name.split("->", 1)
                from_state = fsm_scope._states.get(from_name)
                to_state   = fsm_scope._states.get(to_name)
                if from_state is None or to_state is None:
                    continue
                trans = MemFSMTransition(from_state, to_state)
                trans.count = ci.getCoverData().data
                fsm_scope._transitions[(from_name, to_name)] = trans
