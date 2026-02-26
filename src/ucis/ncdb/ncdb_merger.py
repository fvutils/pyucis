"""
NcdbMerger — merge one or more NCDB .cdb files into a target .cdb file.

Two merge paths:

  Same-schema fast merge (all sources share the same schema_hash):
    Counts arrays are added element-wise.  The scope tree and string
    table from the first source are reused verbatim.  This is O(bins)
    and requires no scope-tree parsing beyond reading the manifest.

  Cross-schema merge (schemas differ):
    Each source is loaded into memory via NcdbReader → MemUCIS.
    The existing generic DbMerger handles the structural union.
    The result is written as a new NCDB file via NcdbWriter.

History nodes from all sources are accumulated in the output.  A new
MERGE HistoryNode is appended to record the operation.
"""

import zipfile
import json
import struct
from datetime import datetime, timezone
from typing import List

from .ncdb_reader import NcdbReader
from .ncdb_writer import NcdbWriter
from .manifest import Manifest
from .counts import CountsReader, CountsWriter
from .history import HistoryWriter, HistoryReader
from .constants import (
    MEMBER_MANIFEST, MEMBER_STRINGS, MEMBER_SCOPE_TREE,
    MEMBER_COUNTS, MEMBER_HISTORY, MEMBER_SOURCES,
)
from ucis.ncdb._accel import add_uint32_arrays as _add_arrays, HAS_ACCEL as _HAS_ACCEL

from ucis.history_node_kind import HistoryNodeKind
from ucis.mem.mem_history_node import MemHistoryNode


class NcdbMerger:
    """Merge N NCDB source files into a single NCDB target file."""

    def merge(self, sources: List[str], target: str) -> None:
        """Merge *sources* into *target*.

        Args:
            sources: List of input .cdb (NCDB) file paths.
            target:  Output .cdb file path (will be overwritten).
        """
        if not sources:
            raise ValueError("No source files provided")

        # Read manifests to determine merge path
        manifests = [self._read_manifest(s) for s in sources]
        hashes = [m.schema_hash for m in manifests]

        all_same = len(set(hashes)) == 1

        if all_same:
            self._merge_same_schema(sources, manifests, target)
        else:
            self._merge_cross_schema(sources, target)

    # ── Same-schema fast path ─────────────────────────────────────────────

    def _merge_same_schema(self, sources, manifests, target):
        """Element-wise counts addition; reuse scope tree from first source."""
        # Load counts from all sources and add them
        all_counts = [self._read_counts(s) for s in sources]
        n = len(all_counts[0])
        for counts in all_counts:
            if len(counts) != n:
                raise ValueError(
                    f"Count array length mismatch: expected {n}, got {len(counts)}")
        merged_counts = list(map(sum, zip(*all_counts)))
        if _HAS_ACCEL and len(all_counts) == 2:
            # For two-source merges use the C element-wise adder
            merged_counts = _add_arrays(all_counts[0], all_counts[1])

        # Gather all history nodes from all sources
        all_history = []
        for s in sources:
            all_history.extend(self._read_history(s))

        # Add a MERGE history node
        merge_node = self._make_merge_node(target, sources)
        all_history.append(merge_node)

        # Build new manifest using first source's schema data
        first_manifest = manifests[0]
        new_manifest = Manifest(
            format=first_manifest.format,
            version=first_manifest.version,
            ucis_version=first_manifest.ucis_version,
            created=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            path_separator=first_manifest.path_separator,
            scope_count=first_manifest.scope_count,
            coveritem_count=n,
            test_count=sum(1 for h in all_history
                           if h.getKind() == HistoryNodeKind.TEST),
            total_hits=sum(merged_counts),
            covered_bins=sum(1 for c in merged_counts if c > 0),
            schema_hash=first_manifest.schema_hash,
            generator=first_manifest.generator,
        )

        # Read schema members verbatim from first source
        with zipfile.ZipFile(sources[0], "r") as zf:
            strings_bytes    = zf.read(MEMBER_STRINGS)
            scope_tree_bytes = zf.read(MEMBER_SCOPE_TREE)
            sources_bytes    = zf.read(MEMBER_SOURCES)

        counts_bytes  = CountsWriter().serialize(merged_counts)
        history_bytes = HistoryWriter().serialize(all_history)

        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(MEMBER_MANIFEST,   new_manifest.serialize())
            zf.writestr(MEMBER_STRINGS,    strings_bytes)
            zf.writestr(MEMBER_SCOPE_TREE, scope_tree_bytes)
            zf.writestr(MEMBER_COUNTS,     counts_bytes)
            zf.writestr(MEMBER_HISTORY,    history_bytes)
            zf.writestr(MEMBER_SOURCES,    sources_bytes)

    # ── Cross-schema fallback ─────────────────────────────────────────────

    def _merge_cross_schema(self, sources, target):
        """Load all sources into MemUCIS and use generic DbMerger."""
        from ucis.merge.db_merger import DbMerger
        from ucis.mem.mem_ucis import MemUCIS

        dbs = [NcdbReader().read(s) for s in sources]
        out_db = MemUCIS()

        # Collect all history from sources for the output
        all_history_nodes = []
        for db in dbs:
            try:
                all_history_nodes.extend(
                    list(db.historyNodes(HistoryNodeKind.TEST)) +
                    list(db.historyNodes(HistoryNodeKind.MERGE))
                )
            except Exception:
                all_history_nodes.extend(list(db.historyNodes(HistoryNodeKind.TEST)))

        DbMerger().merge(out_db, dbs)

        # Re-add history nodes to out_db
        for node in all_history_nodes:
            hn = out_db.createHistoryNode(
                None, node.getLogicalName(), node.getPhysicalName(), node.getKind())
            hn.setTestStatus(node.getTestStatus())

        # Add MERGE node
        merge_node = self._make_merge_node(target, sources)
        out_db.createHistoryNode(
            None,
            merge_node.getLogicalName(),
            merge_node.getPhysicalName(),
            merge_node.getKind(),
        )

        NcdbWriter().write(out_db, target)

        for db in dbs:
            db.close()

    # ── Helpers ───────────────────────────────────────────────────────────

    def _read_manifest(self, path: str) -> Manifest:
        with zipfile.ZipFile(path, "r") as zf:
            return Manifest.from_bytes(zf.read(MEMBER_MANIFEST))

    def _read_counts(self, path: str) -> list:
        with zipfile.ZipFile(path, "r") as zf:
            return CountsReader().deserialize(zf.read(MEMBER_COUNTS))

    def _read_history(self, path: str) -> list:
        with zipfile.ZipFile(path, "r") as zf:
            return HistoryReader().deserialize(zf.read(MEMBER_HISTORY))

    def _make_merge_node(self, target: str, sources: List[str]) -> MemHistoryNode:
        node = MemHistoryNode(
            parent=None,
            logicalname=target,
            physicalname=target,
            kind=HistoryNodeKind.MERGE,
        )
        node.setDate(int(datetime.now(timezone.utc).timestamp()))
        node.setToolCategory("ncdb-merger")
        node.setComment(f"Merged from: {', '.join(sources)}")
        return node
