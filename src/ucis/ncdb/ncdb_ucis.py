"""
NcdbUCIS — lazy-loading UCIS wrapper for NCDB files.

NcdbUCIS defers all scope-tree and count parsing until the database is first
accessed.  This avoids upfront parsing cost when only a subset of the data
is needed (e.g. reading history nodes without loading 60K+ scope records).

Usage::

    db = NcdbUCIS("coverage.cdb")
    # No parsing yet
    for hn in db.historyNodes(HistoryNodeKind.TEST):
        ...                          # only history.json is parsed here
    for scope in db.scopes(...):
        ...                          # scope_tree + counts parsed on first call
"""

import zipfile
import json

from ucis.mem.mem_ucis import MemUCIS
from ucis.history_node_kind import HistoryNodeKind

from .constants import (
    MEMBER_MANIFEST, MEMBER_STRINGS, MEMBER_SCOPE_TREE,
    MEMBER_COUNTS, MEMBER_HISTORY, MEMBER_SOURCES,
    MEMBER_ATTRS, MEMBER_TAGS, MEMBER_PROPERTIES,
    MEMBER_TOGGLE, MEMBER_FSM, MEMBER_CROSS, MEMBER_DESIGN_UNITS,
    MEMBER_CONTRIB_DIR, MEMBER_FORMAL,
    NCDB_FORMAT,
)
from .manifest import Manifest


class NcdbUCIS(MemUCIS):
    """Lazy-loading UCIS backed by an NCDB .cdb file.

    The file is kept closed until first access.  After loading, the decoded
    MemUCIS state is merged into *self* so that all existing MemUCIS methods
    work transparently.

    The lazy-loading covers two independent units:
    - **history**: loaded when ``historyNodes()`` is first called.
    - **scopes**: loaded when ``scopes()`` or any scope-creation method is
      called for the first time.

    Once loaded, a unit is never re-read.
    """

    def __init__(self, path: str):
        super().__init__()
        self._ncdb_path = path
        self._loaded_history = False
        self._loaded_scopes = False
        self._loaded_attrs = False
        self._du_index: dict = {}   # name → DU scope (populated after _ensure_scopes)
        self._zf_cache: dict = {}   # member name → bytes (populated on first open)

    # ── Public extra API ──────────────────────────────────────────────────

    @property
    def path(self) -> str:
        return self._ncdb_path

    def preload(self) -> 'NcdbUCIS':
        """Eagerly load all data from the NCDB file.  Returns self."""
        self._ensure_history()
        self._ensure_scopes()
        return self

    def getDesignUnit(self, name: str):
        """Return the DU scope with *name*, or None if not found."""
        self._ensure_scopes()
        return self._du_index.get(name)

    # ── MemUCIS overrides — trigger lazy loads ─────────────────────────

    def historyNodes(self, kind: HistoryNodeKind):
        self._ensure_history()
        return super().historyNodes(kind)

    def createHistoryNode(self, *args, **kwargs):
        self._ensure_history()
        return super().createHistoryNode(*args, **kwargs)

    def scopes(self, mask):
        self._ensure_scopes()
        return super().scopes(mask)

    def createScope(self, *args, **kwargs):
        self._ensure_scopes()
        return super().createScope(*args, **kwargs)

    def createInstance(self, *args, **kwargs):
        self._ensure_scopes()
        return super().createInstance(*args, **kwargs)

    # ── Internal loading helpers ───────────────────────────────────────

    def _read_zip(self) -> None:
        """Read all ZIP members into the byte cache (called at most once)."""
        if self._zf_cache:
            return
        with zipfile.ZipFile(self._ncdb_path, "r") as zf:
            names = zf.namelist()
            for name in names:
                self._zf_cache[name] = zf.read(name)

    def _ensure_history(self) -> None:
        if self._loaded_history:
            return
        self._loaded_history = True
        self._read_zip()
        _load_history(self, self._zf_cache.get(MEMBER_HISTORY, b''))

    def _ensure_scopes(self) -> None:
        if self._loaded_scopes:
            return
        self._loaded_scopes = True
        self._read_zip()
        data = self._zf_cache

        manifest = Manifest.from_bytes(data[MEMBER_MANIFEST])
        if manifest.format != NCDB_FORMAT:
            raise ValueError(
                f"Expected NCDB format, got '{manifest.format}'")
        self.setPathSeparator(manifest.path_separator)

        from .string_table import StringTable
        from .scope_tree import ScopeTreeReader
        from .counts import CountsReader
        from .sources import SourcesReader
        from .ncdb_reader import _fixup_instance_du_links

        string_table = StringTable.from_bytes(data[MEMBER_STRINGS])
        file_handles = SourcesReader().deserialize(data.get(MEMBER_SOURCES, b'[]'))
        counts_iter  = iter(CountsReader().deserialize(data[MEMBER_COUNTS]))

        ScopeTreeReader(string_table, file_handles).read(
            data[MEMBER_SCOPE_TREE], self, counts_iter)

        for fh in file_handles:
            self.createFileHandle(fh.getFileName(), None)

        _fixup_instance_du_links(self)

        # Attrs / tags / properties (optional)
        attrs_data   = data.get(MEMBER_ATTRS,   b'')
        tags_data    = data.get(MEMBER_TAGS,    b'')
        props_data   = data.get(MEMBER_PROPERTIES, b'')
        toggle_data  = data.get(MEMBER_TOGGLE,  b'')
        fsm_data     = data.get(MEMBER_FSM,     b'')
        cross_data   = data.get(MEMBER_CROSS,   b'')
        du_data      = data.get(MEMBER_DESIGN_UNITS, b'')

        if attrs_data:
            from .attrs import AttrsReader
            AttrsReader().deserialize(attrs_data, self)
        if tags_data:
            from .tags import TagsReader
            TagsReader().deserialize(tags_data, self)
        if props_data:
            from .properties import PropertiesReader
            PropertiesReader().apply(self, props_data)
        if toggle_data:
            from .toggle import ToggleReader
            ToggleReader().apply(self, toggle_data)
        from .fsm import FsmReader
        FsmReader().apply(self, fsm_data)
        if cross_data:
            from .cross import CrossReader
            CrossReader().apply(self, cross_data)
        from .design_units import DesignUnitsReader
        self._du_index = DesignUnitsReader().build_index(du_data, self)

        # Per-test contributions (optional)
        contrib_members = {
            name: data[name] for name in data if name.startswith(MEMBER_CONTRIB_DIR)
        }
        if contrib_members:
            from .contrib import ContribReader
            ContribReader().apply(self, contrib_members)

        # Formal verification data (optional)
        formal_data = data.get(MEMBER_FORMAL, b'')
        if formal_data:
            from .formal import FormalReader
            FormalReader().apply(self, formal_data)


def _load_history(db: MemUCIS, history_bytes: bytes) -> None:
    """Deserialize history.json and populate *db* with history nodes."""
    from .history import HistoryReader
    nodes = HistoryReader().deserialize(history_bytes)
    for node in nodes:
        hn = db.createHistoryNode(
            None, node.getLogicalName(), node.getPhysicalName(), node.getKind())
        if node.getTestStatus() is not None:
            hn.setTestStatus(node.getTestStatus())
        if node.getSimTime() is not None and node.getSimTime() >= 0:
            hn.setSimTime(node.getSimTime())
        if node.getTimeUnit() is not None:
            hn.setTimeUnit(node.getTimeUnit())
        if node.getRunCwd() is not None:
            hn.setRunCwd(node.getRunCwd())
        if node.getCpuTime() is not None and node.getCpuTime() >= 0:
            hn.setCpuTime(node.getCpuTime())
        if node.getSeed() is not None:
            hn.setSeed(node.getSeed())
        if node.getCmd() is not None:
            hn.setCmd(node.getCmd())
        if node.getArgs() is not None:
            hn.setArgs(node.getArgs())
        if node.getDate() is not None:
            hn.setDate(node.getDate())
        if node.getUserName() is not None:
            hn.setUserName(node.getUserName())
        if node.getToolCategory() is not None:
            hn.setToolCategory(node.getToolCategory())
        if node.getVendorId() is not None:
            hn.setVendorId(node.getVendorId())
        if node.getVendorTool() is not None:
            hn.setVendorTool(node.getVendorTool())
        if node.getVendorToolVersion() is not None:
            hn.setVendorToolVersion(node.getVendorToolVersion())
        if node.getComment() is not None:
            hn.setComment(node.getComment())
