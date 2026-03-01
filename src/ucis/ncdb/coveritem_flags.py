"""
coveritem_flags.bin — per-coveritem flag serialization.

Stores non-zero coveritem flags (exclusion, type-qualified) as sparse
delta-encoded (coveritem_dfs_index, flags) pairs.

Format:
    version:     varint (1)
    num_entries: varint
    per entry:
        delta_idx: varint  (coveritem DFS index delta from previous)
        flags:     varint  (ucisFlagsT value)
"""

from ucis.cover_type_t import CoverTypeT
from ucis.scope_type_t import ScopeTypeT

from .varint import encode_varint, decode_varint
from .dfs_util import dfs_scope_list

_VERSION = 1
_COVER_ALL = 0xFFFFFFFF


class CoveritemFlagsWriter:
    """Serialize non-zero coveritem flags to binary bytes."""

    def serialize(self, db) -> bytes:
        entries = []
        global_ci_idx = 0
        scopes = dfs_scope_list(db)
        for scope in scopes:
            for ci in scope.coverItems(_COVER_ALL):
                flags = ci.getCoverFlags()
                if flags != 0:
                    entries.append((global_ci_idx, flags))
                global_ci_idx += 1

        if not entries:
            return b""

        buf = bytearray()
        buf.extend(encode_varint(_VERSION))
        buf.extend(encode_varint(len(entries)))
        prev_idx = 0
        for ci_idx, flags in entries:
            buf.extend(encode_varint(ci_idx - prev_idx))
            buf.extend(encode_varint(flags))
            prev_idx = ci_idx
        return bytes(buf)


class CoveritemFlagsReader:
    """Deserialize coveritem_flags.bin and apply to scope tree."""

    def deserialize(self, data: bytes, db) -> None:
        if not data:
            return

        offset = 0
        version, offset = decode_varint(data, offset)
        if version != _VERSION:
            return

        num_entries, offset = decode_varint(data, offset)
        if num_entries == 0:
            return

        entries = []
        prev_idx = 0
        for _ in range(num_entries):
            delta, offset = decode_varint(data, offset)
            flags, offset = decode_varint(data, offset)
            ci_idx = prev_idx + delta
            entries.append((ci_idx, flags))
            prev_idx = ci_idx

        scopes = dfs_scope_list(db)
        global_ci_idx = 0
        entry_pos = 0
        for scope in scopes:
            for ci in scope.coverItems(_COVER_ALL):
                if entry_pos < len(entries) and entries[entry_pos][0] == global_ci_idx:
                    ci.setCoverFlags(entries[entry_pos][1])
                    entry_pos += 1
                global_ci_idx += 1
