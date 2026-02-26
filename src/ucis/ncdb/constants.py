"""
NCDB format constants: magic bytes, member names, type enums, defaults.

All values defined here must match the COVERAGE_FILE_FORMAT_DESIGN.md spec
(including the Addendum for V2 encoding).
"""

from ucis.cover_type_t import CoverTypeT
from ucis.scope_type_t import ScopeTypeT

# ── Format identity ────────────────────────────────────────────────────────

NCDB_FORMAT = "NCDB"
NCDB_VERSION = "1.0"
NCDB_GENERATOR = "pyucis-ncdb"

# ── CDB file header magic ──────────────────────────────────────────────────

SQLITE_MAGIC = b"SQLite format 3\x00"   # 16 bytes
ZIP_SIGNATURES = (b"PK\x03\x04", b"PK\x05\x06")  # normal and empty ZIP

# ── ZIP member names ───────────────────────────────────────────────────────

MEMBER_MANIFEST    = "manifest.json"
MEMBER_STRINGS     = "strings.bin"
MEMBER_SCOPE_TREE  = "scope_tree.bin"
MEMBER_COUNTS      = "counts.bin"
MEMBER_HISTORY     = "history.json"
MEMBER_SOURCES     = "sources.json"
MEMBER_ATTRS       = "attrs.bin"
MEMBER_TAGS        = "tags.json"
MEMBER_TOGGLE      = "toggle.bin"
MEMBER_FSM         = "fsm.bin"
MEMBER_CROSS       = "cross.bin"
MEMBER_FORMAL      = "formal.bin"
MEMBER_DESIGN_UNITS = "design_units.json"
MEMBER_PROPERTIES  = "properties.json"
MEMBER_CONTRIB_DIR = "contrib/"

# ── V2 scope_tree.bin encoding markers ────────────────────────────────────

SCOPE_MARKER_REGULAR     = 0x00
SCOPE_MARKER_TOGGLE_PAIR = 0x01

# ── V2 presence bitfield bits ─────────────────────────────────────────────

PRESENCE_FLAGS      = 0x01  # has non-default flags
PRESENCE_SOURCE     = 0x02  # has source info (file_id, line, token)
PRESENCE_WEIGHT     = 0x04  # has non-default weight (≠1)
PRESENCE_AT_LEAST   = 0x08  # coveritem at_least override at scope level
PRESENCE_CVG_OPTS   = 0x10  # has covergroup options

# ── counts.bin encoding modes ─────────────────────────────────────────────

COUNTS_MODE_UINT32 = 0   # fixed 4-byte little-endian per count
COUNTS_MODE_VARINT = 1   # LEB128 varint per count

# ── Toggle pair implicit bin names ────────────────────────────────────────

TOGGLE_BIN_0_TO_1 = "0 -> 1"
TOGGLE_BIN_1_TO_0 = "1 -> 0"

# ── V2 type-level defaults table ──────────────────────────────────────────
# Maps CoverTypeT → (flags, at_least, weight)
# Used by reader to reconstruct coveritem objects without per-item storage.

COVER_TYPE_DEFAULTS: dict = {
    CoverTypeT.TOGGLEBIN:  (0, 0, 1),
    CoverTypeT.STMTBIN:    (0, 0, 1),
    CoverTypeT.BRANCHBIN:  (0, 0, 1),
    CoverTypeT.CONDBIN:    (0, 0, 1),
    CoverTypeT.EXPRBIN:    (0, 0, 1),
    CoverTypeT.FSMBIN:     (0, 0, 1),
    CoverTypeT.CVGBIN:     (0, 1, 1),
    CoverTypeT.DEFAULTBIN: (0, 0, 1),
    CoverTypeT.IGNOREBIN:  (0, 0, 1),
    CoverTypeT.ILLEGALBIN: (0, 0, 1),
    CoverTypeT.BLOCKBIN:   (0, 0, 1),
    CoverTypeT.COVERBIN:   (0, 0, 1),
    CoverTypeT.ASSERTBIN:  (0, 0, 1),
    CoverTypeT.PASSBIN:    (0, 0, 1),
    CoverTypeT.FAILBIN:    (0, 0, 1),
}

# ── Scope-type → implicit child cover type mapping ────────────────────────
# When a REGULAR scope has children whose cover type is structurally implied
# by the parent scope type (e.g. BRANCH → TOGGLEBIN).

SCOPE_TO_COVER_TYPE: dict = {
    ScopeTypeT.TOGGLE:     CoverTypeT.TOGGLEBIN,
    ScopeTypeT.BRANCH:     CoverTypeT.TOGGLEBIN,
    ScopeTypeT.EXPR:       CoverTypeT.BRANCHBIN,
    ScopeTypeT.COND:       CoverTypeT.CONDBIN,
    ScopeTypeT.BLOCK:      CoverTypeT.STMTBIN,
    ScopeTypeT.COVBLOCK:   CoverTypeT.BLOCKBIN,
    ScopeTypeT.FSM:        CoverTypeT.FSMBIN,
    ScopeTypeT.FSM_STATES: CoverTypeT.FSMBIN,
    ScopeTypeT.FSM_TRANS:  CoverTypeT.FSMBIN,
    ScopeTypeT.COVERPOINT: CoverTypeT.CVGBIN,
    ScopeTypeT.CROSS:      CoverTypeT.DEFAULTBIN,
    ScopeTypeT.CVGBINSCOPE:       CoverTypeT.CVGBIN,
    ScopeTypeT.ILLEGALBINSCOPE:   CoverTypeT.ILLEGALBIN,
    ScopeTypeT.IGNOREBINSCOPE:    CoverTypeT.IGNOREBIN,
    ScopeTypeT.COVER:      CoverTypeT.COVERBIN,
    ScopeTypeT.ASSERT:     CoverTypeT.ASSERTBIN,
}
