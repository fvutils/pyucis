"""
NcdbReader — deserialize an NCDB .cdb ZIP file into a MemUCIS model.
"""

import zipfile
import json

from .string_table import StringTable
from .scope_tree import ScopeTreeReader
from .counts import CountsReader
from .history import HistoryReader
from .sources import SourcesReader
from .attrs import AttrsReader
from .tags import TagsReader
from .properties import PropertiesReader
from .toggle import ToggleReader
from .fsm import FsmReader
from .cross import CrossReader
from .contrib import ContribReader
from .formal import FormalReader
from .coveritem_flags import CoveritemFlagsReader
from .design_units import DesignUnitsReader
from .manifest import Manifest
from .constants import (
    MEMBER_MANIFEST, MEMBER_STRINGS, MEMBER_SCOPE_TREE,
    MEMBER_COUNTS, MEMBER_HISTORY, MEMBER_SOURCES,
    MEMBER_ATTRS, MEMBER_TAGS, MEMBER_PROPERTIES, MEMBER_TOGGLE, MEMBER_FSM,
    MEMBER_CROSS, MEMBER_DESIGN_UNITS, MEMBER_CONTRIB_DIR, MEMBER_FORMAL,
    NCDB_FORMAT,
    MEMBER_COVERITEM_FLAGS,
)

from ucis.mem.mem_ucis import MemUCIS
from ucis.history_node_kind import HistoryNodeKind
from ucis.scope_type_t import ScopeTypeT


def _fixup_instance_du_links(db: MemUCIS) -> None:
    """Link INSTANCE scope DU references to real DU scopes in the same parent.

    When scope_tree decodes INSTANCE scopes whose DU was serialized *after*
    them, a detached placeholder DU is used temporarily.  This function
    replaces those placeholders with the actual DU sibling scopes.
    """
    from ucis.mem.mem_instance_scope import MemInstanceScope

    def _fix_parent(parent):
        # Build name → DU map from real (attached) children
        du_map = {}
        for child in parent.scopes(ScopeTypeT.ALL):
            if ScopeTypeT.DU_ANY(child.getScopeType()):
                du_map[child.getScopeName()] = child

        # Replace placeholder DU refs on INSTANCE scopes
        for child in parent.scopes(ScopeTypeT.ALL):
            if isinstance(child, MemInstanceScope):
                du = child.m_du_scope
                if du is not None and du.m_parent is None:
                    # Detached placeholder — replace with real DU if available
                    real_du = du_map.get(child.getScopeName())
                    if real_du is not None:
                        child.m_du_scope = real_du
            # Recurse
            _fix_parent(child)

    _fix_parent(db)


class NcdbReader:
    """Read an NCDB .cdb ZIP file and return a populated MemUCIS."""

    def read(self, path: str) -> MemUCIS:
        with zipfile.ZipFile(path, "r") as zf:
            names = zf.namelist()
            manifest_bytes    = zf.read(MEMBER_MANIFEST)
            strings_bytes     = zf.read(MEMBER_STRINGS)
            scope_tree_bytes  = zf.read(MEMBER_SCOPE_TREE)
            counts_bytes      = zf.read(MEMBER_COUNTS)
            history_bytes     = zf.read(MEMBER_HISTORY)
            sources_bytes     = zf.read(MEMBER_SOURCES)
            attrs_bytes  = zf.read(MEMBER_ATTRS)       if MEMBER_ATTRS       in names else b''
            tags_bytes   = zf.read(MEMBER_TAGS)        if MEMBER_TAGS        in names else b''
            props_bytes  = zf.read(MEMBER_PROPERTIES)  if MEMBER_PROPERTIES  in names else b''
            toggle_bytes = zf.read(MEMBER_TOGGLE)        if MEMBER_TOGGLE        in names else b''
            fsm_bytes    = zf.read(MEMBER_FSM)           if MEMBER_FSM           in names else b''
            cross_bytes  = zf.read(MEMBER_CROSS)         if MEMBER_CROSS         in names else b''
            du_bytes     = zf.read(MEMBER_DESIGN_UNITS)  if MEMBER_DESIGN_UNITS  in names else b''
            formal_bytes = zf.read(MEMBER_FORMAL)         if MEMBER_FORMAL         in names else b''
            ci_flags_bytes = zf.read(MEMBER_COVERITEM_FLAGS) if MEMBER_COVERITEM_FLAGS in names else b''
            # Collect all contrib/* members
            contrib_members = {
                n: zf.read(n) for n in names if n.startswith(MEMBER_CONTRIB_DIR)
            }

        manifest = Manifest.from_bytes(manifest_bytes)
        if manifest.format != NCDB_FORMAT:
            raise ValueError(
                f"Expected NCDB format, got '{manifest.format}'")

        # Strings
        string_table = StringTable.from_bytes(strings_bytes)

        # Source file handles
        file_handles = SourcesReader().deserialize(sources_bytes)

        # Counts (as a flat iterator)
        counts = CountsReader().deserialize(counts_bytes)
        counts_iter = iter(counts)

        # Build MemUCIS
        db = MemUCIS()
        db.setPathSeparator(manifest.path_separator)

        # Rebuild scope tree
        st_reader = ScopeTreeReader(string_table, file_handles)
        st_reader.read(scope_tree_bytes, db, counts_iter)

        # Fix up INSTANCE scope DU links: replace detached placeholder DUs with
        # real DU scopes that were written as separate top-level entries.
        _fixup_instance_du_links(db)

        # Apply optional attrs, tags, typed properties, toggle and FSM metadata
        if tags_bytes:
            TagsReader().deserialize(tags_bytes, db)
        if props_bytes:
            PropertiesReader().apply(db, props_bytes)
        if toggle_bytes:
            ToggleReader().apply(db, toggle_bytes)
        # FSM reader always runs (rebuilds _states/_transitions from cover items)
        FsmReader().apply(db, fsm_bytes)
        if cross_bytes:
            CrossReader().apply(db, cross_bytes)

        # Build design-unit index (available via db._du_index after this)
        db._du_index = DesignUnitsReader().build_index(du_bytes, db)

        # Per-test contributions (optional)
        ContribReader().apply(db, contrib_members)

        # Formal verification data (optional)
        if formal_bytes:
            FormalReader().apply(db, formal_bytes)
        if ci_flags_bytes:
            CoveritemFlagsReader().deserialize(ci_flags_bytes, db)

        # Register source files as file handles in db
        for fh in file_handles:
            db.createFileHandle(fh.getFileName(), None)

        # History nodes
        history_nodes = HistoryReader().deserialize(history_bytes)
        for node in history_nodes:
            hn = db.createHistoryNode(
                None,
                node.getLogicalName(),
                node.getPhysicalName(),
                node.getKind(),
            )
            # Copy all fields
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
            if node.getCompulsory() is not None:
                hn.setCompulsory(node.getCompulsory())
            if node.getDate() is not None:
                hn.setDate(node.getDate())
            if node.getUserName() is not None:
                hn.setUserName(node.getUserName())
            if node.getCost() is not None and node.getCost() >= 0:
                hn.setCost(node.getCost())
            if node.getToolCategory() is not None:
                hn.setToolCategory(node.getToolCategory())
            if node.getVendorId() is not None:
                hn.setVendorId(node.getVendorId())
            if node.getVendorTool() is not None:
                hn.setVendorTool(node.getVendorTool())
            if node.getVendorToolVersion() is not None:
                hn.setVendorToolVersion(node.getVendorToolVersion())
            if node.getSameTests() is not None and node.getSameTests() >= 0:
                hn.setSameTests(node.getSameTests())
            if node.getComment() is not None:
                hn.setComment(node.getComment())

        if attrs_bytes:
            AttrsReader().deserialize(attrs_bytes, db)

        return db
