"""
DFS traversal utility — shared between attrs/tags/properties serializers.

Produces a flat list of (scope, dfs_index) pairs in the same DFS order
that scope_tree.py uses for encoding, so that index-based serializers
(attrs.json, tags.json, properties.bin) can map directly to scope_tree
offsets without re-reading the binary.
"""

from ucis.scope_type_t import ScopeTypeT
from ucis.cover_type_t import CoverTypeT

from .constants import TOGGLE_BIN_0_TO_1, TOGGLE_BIN_1_TO_0


def _is_toggle_pair(scope) -> bool:
    """Match the toggle-pair detection logic in scope_tree.py."""
    if scope.getScopeType() != ScopeTypeT.BRANCH:
        return False
    cover_items = list(scope.coverItems(CoverTypeT.ALL))
    if len(cover_items) != 2:
        return False
    if list(scope.scopes(ScopeTypeT.ALL)):
        return False
    names = {ci.getName() for ci in cover_items}
    return names == {TOGGLE_BIN_0_TO_1, TOGGLE_BIN_1_TO_0}


def dfs_scope_list(db) -> list:
    """Return all scopes in DFS order (matches scope_tree.bin encoding).

    Toggle-pair BRANCH scopes are included (they appear in scope_tree.bin
    as TOGGLE_PAIR records but still occupy one DFS slot each).
    """
    result = []

    def _visit(scope):
        result.append(scope)
        if not _is_toggle_pair(scope):
            for child in scope.scopes(ScopeTypeT.ALL):
                _visit(child)

    for top_scope in db.scopes(ScopeTypeT.ALL):
        _visit(top_scope)

    return result
