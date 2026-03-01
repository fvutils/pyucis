"""
scope_tree.bin — scope hierarchy V2 encoding/decoding.

Writer:  DFS walk of UCIS scope tree → binary bytes + populates StringTable.
Reader:  binary bytes + StringTable → reconstructed MemUCIS scope tree.

V2 encoding (from Addendum §A.2):
  - BRANCH scopes with exactly 2 TOGGLEBIN children encoded as TOGGLE_PAIR
    (2-byte record: marker + name_ref varint).
  - REGULAR scopes use a presence bitfield to omit default fields.
  - Coveritem records contain only the name_ref (type from parent scope).
  - Counts are NOT stored here; they are written separately to counts.bin
    in DFS order (toggle pairs contribute 2 counts each).
"""

import io
import struct

from ucis.cover_data import CoverData
from ucis.cover_type_t import CoverTypeT
from ucis.scope_type_t import ScopeTypeT
from ucis.source_t import SourceT
from ucis.source_info import SourceInfo

from .varint import encode_varint, decode_varint
from .constants import (
    SCOPE_MARKER_REGULAR, SCOPE_MARKER_TOGGLE_PAIR,
    PRESENCE_FLAGS, PRESENCE_SOURCE, PRESENCE_WEIGHT, PRESENCE_AT_LEAST,
    PRESENCE_GOAL, PRESENCE_SOURCE_TYPE,
    TOGGLE_BIN_0_TO_1, TOGGLE_BIN_1_TO_0,
    COVER_TYPE_DEFAULTS,
)


# ──────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────

def _is_toggle_pair(scope) -> bool:
    """True if *scope* is a BRANCH with exactly 2 TOGGLEBIN children."""
    if scope.getScopeType() != ScopeTypeT.BRANCH:
        return False
    cover_items = list(scope.coverItems(CoverTypeT.ALL))
    if len(cover_items) != 2:
        return False
    child_scopes = list(scope.scopes(ScopeTypeT.ALL))
    if len(child_scopes) != 0:
        return False
    names = {ci.getName() for ci in cover_items}
    return names == {TOGGLE_BIN_0_TO_1, TOGGLE_BIN_1_TO_0}


# ──────────────────────────────────────────────────────────────────────────
# Writer
# ──────────────────────────────────────────────────────────────────────────

class ScopeTreeWriter:
    """Serialize a UCIS scope tree to scope_tree.bin bytes.

    Also populates the *string_table* and *counts_list* as a side-effect.
    After calling write(), use string_table for strings.bin and
    counts_list for counts.bin.

    Also tracks file handles so that sources.json can be written
    consistently with the source IDs embedded in scope_tree.bin.
    """

    def __init__(self, string_table, file_handles: list = None):
        """
        Args:
            string_table: StringTable instance to populate with names.
            file_handles: Mutable list; file handles will be appended in the
                order they are first encountered.  The index in this list
                becomes the file_id stored in scope_tree.bin.
        """
        self._st = string_table
        self._file_handles = file_handles if file_handles is not None else []
        self._fh_index: dict = {}   # filename → int id
        self.counts_list: list = []  # hit counts in DFS order
        self._buf = io.BytesIO()

    # ── Public API ────────────────────────────────────────────────────────

    def write(self, db) -> bytes:
        """Walk *db* (UCIS root) and return the serialized scope_tree.bin bytes."""
        self._buf = io.BytesIO()
        for scope in db.scopes(ScopeTypeT.ALL):
            self._write_scope(scope)
        return self._buf.getvalue()

    # ── Internal DFS ──────────────────────────────────────────────────────

    def _write_scope(self, scope):
        if _is_toggle_pair(scope):
            self._write_toggle_pair(scope)
        else:
            self._write_regular_scope(scope)

    def _write_toggle_pair(self, scope):
        name_ref = self._st.add(scope.getScopeName())
        self._buf.write(bytes([SCOPE_MARKER_TOGGLE_PAIR]))
        self._buf.write(encode_varint(name_ref))
        # Two implicit coveritems: "0 -> 1" then "1 -> 0"
        cover_items = {ci.getName(): ci for ci in scope.coverItems(CoverTypeT.ALL)}
        for name in (TOGGLE_BIN_0_TO_1, TOGGLE_BIN_1_TO_0):
            ci = cover_items.get(name)
            self.counts_list.append(ci.getCoverData().data if ci else 0)

    def _write_regular_scope(self, scope):
        scope_type = scope.getScopeType()
        name_ref   = self._st.add(scope.getScopeName())

        # Collect source info
        srcinfo  = scope.getSourceInfo()
        has_src  = (srcinfo is not None
                    and srcinfo.file is not None
                    and srcinfo.line >= 0)
        has_flags  = (hasattr(scope, 'm_flags') and scope.m_flags != 0)
        weight     = scope.getWeight() if hasattr(scope, 'getWeight') else 1
        has_weight = (weight is not None and weight != 1)
        goal       = scope.getGoal() if hasattr(scope, 'getGoal') else -1
        has_goal   = (goal is not None and goal != -1)

        source_type = getattr(scope, 'm_source_type', None)
        has_source_type = (source_type is not None
                           and int(source_type) != int(SourceT.NONE))

        # Cover items under this scope
        cover_items = list(scope.coverItems(CoverTypeT.ALL))
        num_coveritems = len(cover_items)

        # Determine child cover type — always read from the actual first cover
        # item.  SCOPE_TO_COVER_TYPE was an optimisation hint but BRANCH scopes
        # can carry either BRANCHBIN (regular branch) or TOGGLEBIN (toggle pair,
        # which is handled by _write_toggle_pair before reaching here), so using
        # a fixed mapping would misidentify the type.
        child_cover_type_val = 0
        if num_coveritems > 0:
            child_cover_type_val = int(cover_items[0].getCoverData().type)

        # at_least override (non-default for this scope's cover type)
        at_least_override = None
        if num_coveritems > 0 and cover_items:
            defaults = COVER_TYPE_DEFAULTS.get(
                CoverTypeT(child_cover_type_val),
                (0, 0, 1))
            default_at_least = defaults[1]
            first_cd = cover_items[0].getCoverData()
            if hasattr(first_cd, 'at_least') and first_cd.at_least != default_at_least:
                at_least_override = first_cd.at_least
        has_at_least = (at_least_override is not None)

        # Presence bitfield
        presence = 0
        if has_flags:  presence |= PRESENCE_FLAGS
        if has_src:    presence |= PRESENCE_SOURCE
        if has_weight: presence |= PRESENCE_WEIGHT
        if has_at_least: presence |= PRESENCE_AT_LEAST
        if has_goal:     presence |= PRESENCE_GOAL
        if has_source_type: presence |= PRESENCE_SOURCE_TYPE

        # Count child sub-scopes
        child_scopes = list(scope.scopes(ScopeTypeT.ALL))

        w = self._buf.write
        w(bytes([SCOPE_MARKER_REGULAR]))
        w(encode_varint(int(scope_type)))
        w(encode_varint(name_ref))
        w(encode_varint(presence))

        if has_flags:
            w(encode_varint(int(scope.m_flags)))
        if has_src:
            file_id = self._get_file_id(srcinfo.file)
            w(encode_varint(file_id))
            w(encode_varint(max(0, srcinfo.line)))
            w(encode_varint(max(0, srcinfo.token)))
        if has_weight:
            w(encode_varint(weight))
        if has_at_least:
            w(encode_varint(at_least_override))
        if has_goal:
            w(encode_varint(goal))
        if has_source_type:
            w(encode_varint(int(source_type)))

        w(encode_varint(len(child_scopes)))
        w(encode_varint(num_coveritems))

        if num_coveritems > 0:
            w(encode_varint(child_cover_type_val))
            # Write coveritem names and accumulate counts
            for ci in cover_items:
                name_ref_ci = self._st.add(ci.getName())
                w(encode_varint(name_ref_ci))
                self.counts_list.append(ci.getCoverData().data)

        # Recurse into child scopes
        for child in child_scopes:
            self._write_scope(child)

    def _get_file_id(self, file_handle) -> int:
        if file_handle is None:
            return 0
        fname = file_handle.getFileName()
        if fname not in self._fh_index:
            fid = len(self._file_handles)
            self._file_handles.append(file_handle)
            self._fh_index[fname] = fid
        return self._fh_index[fname]


# ──────────────────────────────────────────────────────────────────────────
# Reader
# ──────────────────────────────────────────────────────────────────────────

class ScopeTreeReader:
    """Deserialize scope_tree.bin bytes into UCIS scope tree under *parent*.

    Reconstructs MemScope-based objects.  Cover item data (hit counts) come
    from the separate *counts_iter* iterator so that scope_tree.bin and
    counts.bin stay decoupled.
    """

    def __init__(self, string_table, file_handles: list):
        self._st = string_table
        self._fh = file_handles  # indexed by file_id

    def read(self, data: bytes, parent, counts_iter) -> int:
        """Populate *parent* with decoded scopes; return total coveritems read."""
        offset = 0
        total = 0
        while offset < len(data):
            consumed, n = self._read_scope(data, offset, parent, counts_iter)
            offset = consumed
            total += n
        return total

    # ── Internal ──────────────────────────────────────────────────────────

    def _read_scope(self, data: bytes, offset: int, parent, counts_iter):
        """Decode one scope record at *offset*, attach to *parent*.

        Returns (new_offset, coveritems_count).
        """
        marker = data[offset]
        offset += 1

        if marker == SCOPE_MARKER_TOGGLE_PAIR:
            return self._read_toggle_pair(data, offset, parent, counts_iter)
        else:
            return self._read_regular_scope(data, offset, parent, counts_iter)

    def _read_toggle_pair(self, data: bytes, offset: int, parent, counts_iter):
        name_ref, offset = decode_varint(data, offset)
        name = self._st.get(name_ref)

        # Consume two counts
        count_0to1 = next(counts_iter, 0)
        count_1to0 = next(counts_iter, 0)

        scope = parent.createScope(
            name, None, 1, SourceT.NONE, ScopeTypeT.BRANCH, 0)

        # Create the two implicit TOGGLEBIN coveritems
        for (bin_name, count) in ((TOGGLE_BIN_0_TO_1, count_0to1),
                                   (TOGGLE_BIN_1_TO_0, count_1to0)):
            cd = CoverData(CoverTypeT.TOGGLEBIN,
                           COVER_TYPE_DEFAULTS.get(CoverTypeT.TOGGLEBIN, (0,0,1))[0])
            cd.data = count
            scope.createNextCover(bin_name, cd, None)

        return offset, 2

    def _read_regular_scope(self, data: bytes, offset: int, parent, counts_iter):
        scope_type_val, offset = decode_varint(data, offset)
        name_ref,       offset = decode_varint(data, offset)
        presence,       offset = decode_varint(data, offset)

        name       = self._st.get(name_ref)
        scope_type = ScopeTypeT(scope_type_val)

        flags  = 0
        srcinfo = None
        weight  = 1
        at_least_override = None

        if presence & PRESENCE_FLAGS:
            flags, offset = decode_varint(data, offset)
        if presence & PRESENCE_SOURCE:
            file_id, offset = decode_varint(data, offset)
            line,    offset = decode_varint(data, offset)
            token,   offset = decode_varint(data, offset)
            fh = self._fh[file_id] if file_id < len(self._fh) else None
            srcinfo = SourceInfo(fh, line, token)
        if presence & PRESENCE_WEIGHT:
            weight, offset = decode_varint(data, offset)
        if presence & PRESENCE_AT_LEAST:
            at_least_override, offset = decode_varint(data, offset)
        goal = -1
        if presence & PRESENCE_GOAL:
            goal, offset = decode_varint(data, offset)
        source_type_val = int(SourceT.NONE)
        if presence & PRESENCE_SOURCE_TYPE:
            source_type_val, offset = decode_varint(data, offset)

        num_children,   offset = decode_varint(data, offset)
        num_coveritems, offset = decode_varint(data, offset)

        child_cover_type = None
        if num_coveritems > 0:
            ctv, offset = decode_varint(data, offset)
            child_cover_type = CoverTypeT(ctv)
            defaults = COVER_TYPE_DEFAULTS.get(child_cover_type, (0, 0, 1))
            at_least = at_least_override if at_least_override is not None else defaults[1]

        if scope_type == ScopeTypeT.INSTANCE:
            # createInstance() requires a DU reference; find the matching DU
            # that was already serialized (DU scopes precede INSTANCE in DFS).
            du_scope = None
            for sibling in parent.scopes(ScopeTypeT.ALL):
                if (ScopeTypeT.DU_ANY(sibling.getScopeType())
                        and sibling.getScopeName() == name):
                    du_scope = sibling
                    break
            if du_scope is None:
                # DU not yet in parent (INSTANCE precedes DU in source ordering).
                # Create a detached placeholder so createInstance() can succeed
                # without adding an extra scope to parent's children.
                from ucis.mem.mem_scope import MemScope as _MemScope
                du_scope = _MemScope(
                    None, name, srcinfo, weight, SourceT.NONE, ScopeTypeT.DU_MODULE, flags)
            scope = parent.createInstance(
                name, srcinfo, weight, SourceT.NONE, scope_type, du_scope, flags)
        else:
            scope = parent.createScope(name, srcinfo, weight, SourceT.NONE, scope_type, flags)

        if goal != -1 and hasattr(scope, 'setGoal'):
            scope.setGoal(goal)
        if source_type_val != int(SourceT.NONE) and hasattr(scope, 'm_source_type'):
            scope.m_source_type = SourceT(source_type_val)

        # Coveritems
        for _ in range(num_coveritems):
            ci_name_ref, offset = decode_varint(data, offset)
            ci_name = self._st.get(ci_name_ref)
            count = next(counts_iter, 0)
            default_flags = COVER_TYPE_DEFAULTS.get(child_cover_type, (0, 0, 1))[0]
            cd = CoverData(child_cover_type, default_flags)
            cd.data = count
            if at_least_override is not None or (child_cover_type and
                    COVER_TYPE_DEFAULTS.get(child_cover_type, (0,0,1))[1] != 0):
                cd.at_least = at_least if 'at_least' in dir() else 0
            scope.createNextCover(ci_name, cd, None)

        # Child scopes
        for _ in range(num_children):
            offset, _ = self._read_scope(data, offset, scope, counts_iter)

        return offset, num_coveritems
