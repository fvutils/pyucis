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
    MEMBER_TEST_REGISTRY, MEMBER_TEST_STATS,
    MEMBER_BUCKET_INDEX, MEMBER_CONTRIB_INDEX, MEMBER_SQUASH_LOG,
    HISTORY_BUCKET_DIR, HISTORY_FORMAT_V2,
    MEMBER_TESTPLAN, MEMBER_WAIVERS,
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

    _DU_MASK = 0x000000001F000000
    _INSTANCE_VAL = int(ScopeTypeT.INSTANCE)

    def _fix_parent(parent):
        children = parent.m_children if hasattr(parent, 'm_children') else list(parent.scopes(ScopeTypeT.ALL))
        du_map = {}
        instances = []
        for child in children:
            st = int(child.getScopeType())
            if st & _DU_MASK:
                du_map[child.getScopeName()] = child
            if st == _INSTANCE_VAL:
                instances.append(child)
            _fix_parent(child)
        for child in instances:
            du = child.m_du_scope
            if du is not None and du.m_parent is None:
                real_du = du_map.get(child.getScopeName())
                if real_du is not None:
                    child.m_du_scope = real_du

    _fix_parent(db)


class NcdbReader:
    """Read an NCDB .cdb ZIP file and return a populated MemUCIS."""

    def read(self, path: str) -> MemUCIS:
        with zipfile.ZipFile(path, "r") as zf:
            names = zf.namelist()
            # Read all members into a dict for uniform access
            zf_data = {n: zf.read(n) for n in names}

        manifest_bytes    = zf_data[MEMBER_MANIFEST]
        strings_bytes     = zf_data[MEMBER_STRINGS]
        scope_tree_bytes  = zf_data[MEMBER_SCOPE_TREE]
        counts_bytes      = zf_data[MEMBER_COUNTS]
        history_bytes     = zf_data[MEMBER_HISTORY]
        sources_bytes     = zf_data[MEMBER_SOURCES]
        attrs_bytes  = zf_data.get(MEMBER_ATTRS,             b'')
        tags_bytes   = zf_data.get(MEMBER_TAGS,              b'')
        props_bytes  = zf_data.get(MEMBER_PROPERTIES,        b'')
        toggle_bytes = zf_data.get(MEMBER_TOGGLE,            b'')
        fsm_bytes    = zf_data.get(MEMBER_FSM,               b'')
        cross_bytes  = zf_data.get(MEMBER_CROSS,             b'')
        du_bytes     = zf_data.get(MEMBER_DESIGN_UNITS,      b'')
        formal_bytes = zf_data.get(MEMBER_FORMAL,            b'')
        ci_flags_bytes = zf_data.get(MEMBER_COVERITEM_FLAGS, b'')
        # Collect all contrib/* members
        contrib_members = {
            n: zf_data[n] for n in names if n.startswith(MEMBER_CONTRIB_DIR)
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

        # v2 binary history members (optional — present only in v2 archives)
        if manifest.history_format == HISTORY_FORMAT_V2:
            _load_v2_history(db, {name: zf_data.get(name, b'')
                                  for name in (MEMBER_TEST_REGISTRY,
                                               MEMBER_TEST_STATS,
                                               MEMBER_BUCKET_INDEX,
                                               MEMBER_CONTRIB_INDEX,
                                               MEMBER_SQUASH_LOG)},
                             {n: d for n, d in zf_data.items()
                              if n.startswith(HISTORY_BUCKET_DIR)
                              and n.endswith(".bin")
                              and n != MEMBER_BUCKET_INDEX})

        # Testplan (optional)
        testplan_raw = zf_data.get(MEMBER_TESTPLAN, b'')
        if testplan_raw:
            from .testplan import Testplan
            db._testplan = Testplan.from_bytes(testplan_raw)
            db._loaded_testplan = True

        # Waivers (optional)
        waivers_raw = zf_data.get(MEMBER_WAIVERS, b'')
        if waivers_raw:
            from .waivers import WaiverSet
            db._waivers = WaiverSet.from_bytes(waivers_raw)
            db._loaded_waivers = True

        return db


def _load_v2_history(db: MemUCIS, v2_members: dict, bucket_data: dict) -> None:
    """Attach v2 binary history state to *db* (a MemUCIS).

    Uses the same deserialization logic as NcdbUCIS._load_v2_history, but
    attaches the resulting objects as attributes on a plain MemUCIS so that
    callers using NcdbReader (not NcdbUCIS) can access v2 data via the same
    attribute names.
    """
    from .test_registry import TestRegistry
    from .test_stats import TestStatsTable
    from .bucket_index import BucketIndex
    from .contrib_index import ContribIndex, POLICY_PASS_ONLY
    from .squash_log import SquashLog

    reg_data = v2_members.get(MEMBER_TEST_REGISTRY, b'')
    db._test_registry = TestRegistry.deserialize(reg_data) if reg_data else TestRegistry()

    stats_data = v2_members.get(MEMBER_TEST_STATS, b'')
    db._test_stats = TestStatsTable.deserialize(stats_data) if stats_data else TestStatsTable()

    bidx_data = v2_members.get(MEMBER_BUCKET_INDEX, b'')
    db._bucket_index = BucketIndex.deserialize(bidx_data) if bidx_data else BucketIndex()

    cidx_data = v2_members.get(MEMBER_CONTRIB_INDEX, b'')
    db._contrib_index = (ContribIndex.deserialize(cidx_data) if cidx_data
                         else ContribIndex(merge_policy=POLICY_PASS_ONLY))

    slog_data = v2_members.get(MEMBER_SQUASH_LOG, b'')
    db._squash_log = SquashLog.deserialize(slog_data) if slog_data else SquashLog()

    db._sealed_buckets = {}
    for member, data in bucket_data.items():
        basename = member[len(HISTORY_BUCKET_DIR):]
        try:
            seq = int(basename.split(".")[0])
            db._sealed_buckets[seq] = data
        except ValueError:
            pass
