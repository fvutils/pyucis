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

v2 binary history (if present in any source) is merged correctly:
  - TestRegistry names/seeds are unioned; stable name_id remaps are computed
  - TestStatsTable counters are summed and derived scores recomputed
  - Bucket files are decoded, name_ids remapped, re-encoded and sealed
  - BucketIndex is rebuilt; run_ids are offset to keep them disjoint
  - ContribIndex entries are remapped and concatenated
  - SquashLog entries are concatenated (no run_id adjustment needed)
"""

import zipfile
import json
import struct
import math
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from .ncdb_reader import NcdbReader
from .ncdb_writer import NcdbWriter
from .manifest import Manifest
from .counts import CountsReader, CountsWriter
from .history import HistoryWriter, HistoryReader
from .constants import (
    MEMBER_MANIFEST, MEMBER_STRINGS, MEMBER_SCOPE_TREE,
    MEMBER_COUNTS, MEMBER_HISTORY, MEMBER_SOURCES,
    MEMBER_TEST_REGISTRY, MEMBER_TEST_STATS,
    MEMBER_BUCKET_INDEX, MEMBER_CONTRIB_INDEX, MEMBER_SQUASH_LOG,
    HISTORY_BUCKET_DIR, HISTORY_FORMAT_V2,
    HIST_STATUS_OK, HIST_STATUS_FAIL,
    MEMBER_TESTPLAN, MEMBER_WAIVERS,
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

        # Determine if any source has v2 binary history
        any_v2 = any(m.history_format == HISTORY_FORMAT_V2 for m in manifests)
        history_format = HISTORY_FORMAT_V2 if any_v2 else first_manifest.history_format

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
            history_format=history_format,
        )

        # Read schema members verbatim from first source
        with zipfile.ZipFile(sources[0], "r") as zf:
            zf_names = zf.namelist()
            strings_bytes    = zf.read(MEMBER_STRINGS)
            scope_tree_bytes = zf.read(MEMBER_SCOPE_TREE)
            sources_bytes    = zf.read(MEMBER_SOURCES)
            # Gather existing contrib/* members from all sources (copy verbatim)
            contrib_members_all: Dict[str, bytes] = {}

        for src in sources:
            with zipfile.ZipFile(src, "r") as zf:
                for n_member in zf.namelist():
                    if n_member.startswith("contrib/"):
                        contrib_members_all[n_member] = zf.read(n_member)

        counts_bytes  = CountsWriter().serialize(merged_counts)
        history_bytes = HistoryWriter().serialize(all_history)

        # Merge v2 binary history if present in any source
        v2_members: Dict[str, bytes] = {}
        if any_v2:
            v2_members = self._merge_v2_history(sources, manifests)

        # Merge testplan and waivers
        testplan_bytes = self._merge_testplans(sources)
        waivers_bytes  = self._merge_waivers(sources)

        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(MEMBER_MANIFEST,   new_manifest.serialize())
            zf.writestr(MEMBER_STRINGS,    strings_bytes)
            zf.writestr(MEMBER_SCOPE_TREE, scope_tree_bytes)
            zf.writestr(MEMBER_COUNTS,     counts_bytes)
            zf.writestr(MEMBER_HISTORY,    history_bytes)
            zf.writestr(MEMBER_SOURCES,    sources_bytes)
            for member_name, member_bytes in contrib_members_all.items():
                zf.writestr(member_name, member_bytes)
            for member_name, member_bytes in v2_members.items():
                zf.writestr(member_name, member_bytes,
                            compress_type=zipfile.ZIP_STORED)
            if testplan_bytes:
                zf.writestr(MEMBER_TESTPLAN, testplan_bytes)
            if waivers_bytes:
                zf.writestr(MEMBER_WAIVERS, waivers_bytes)

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

    # ── v2 binary history merge ───────────────────────────────────────────

    def _merge_v2_history(self, sources: List[str],
                          manifests: List[Manifest]) -> Dict[str, bytes]:
        """Merge v2 binary history from all sources; return member-name → bytes."""
        from .test_registry import TestRegistry
        from .test_stats import TestStatsTable, TestStatsEntry
        from .bucket_index import BucketIndex
        from .contrib_index import ContribIndex, POLICY_PASS_ONLY
        from .squash_log import SquashLog
        from .history_buckets import BucketWriter, BucketReader

        # --- Step 1: load per-source v2 state ---
        src_states = []
        for src, mf in zip(sources, manifests):
            if mf.history_format == HISTORY_FORMAT_V2:
                src_states.append(self._read_v2_state(src))
            else:
                # Source has no v2 history — use empty state
                src_states.append({
                    'registry': TestRegistry(),
                    'stats': TestStatsTable(),
                    'bucket_index': BucketIndex(),
                    'buckets': {},   # seq → compressed_bytes
                    'contrib_index': ContribIndex(merge_policy=POLICY_PASS_ONLY),
                    'squash_log': SquashLog(),
                })

        # --- Step 2: build merged registry (union of all names/seeds) ---
        # Two-pass approach: first insert ALL names/seeds so the sorted order
        # is final, then recompute remaps against the stable merged registry.
        merged_reg = TestRegistry()

        # Pass 1: insert all names and seeds to finalise the merged registry
        for state in src_states:
            reg = state['registry']
            for name in reg._names:
                merged_reg.lookup_name_id(name)
            for seed in reg._seeds:
                merged_reg.lookup_seed_id(seed)

        # Pass 2: build per-source remaps against the now-stable merged registry
        name_remaps: List[Dict[int, int]] = []
        seed_remaps: List[Dict[int, int]] = []
        for state in src_states:
            reg = state['registry']
            n_remap: Dict[int, int] = {
                old_id: merged_reg._name_to_id[name]
                for old_id, name in enumerate(reg._names)
            }
            s_remap: Dict[int, int] = {
                old_id: merged_reg._seed_to_id[seed]
                for old_id, seed in enumerate(reg._seeds)
            }
            name_remaps.append(n_remap)
            seed_remaps.append(s_remap)

        # --- Step 3: compute run_id offsets (disjoint run_id ranges) ---
        run_id_offsets: List[int] = []
        offset = 0
        for state in src_states:
            run_id_offsets.append(offset)
            offset += state['registry'].next_run_id
        # Advance the merged registry's counter
        for _ in range(offset):
            merged_reg.assign_run_id()

        # --- Step 4: merge TestStatsTable ---
        from .test_stats import TestStatsEntry as _TSEntry
        merged_stats = TestStatsTable()
        # Ensure enough slots
        for _ in range(merged_reg.num_names):
            merged_stats._entries.append(
                _TSEntry(name_id=len(merged_stats._entries)))

        for src_idx, state in enumerate(src_states):
            n_remap = name_remaps[src_idx]
            src_stats = state['stats']
            for old_id, src_entry in enumerate(src_stats._entries):
                if src_entry.total_runs == 0:
                    continue
                new_id = n_remap.get(old_id, old_id)
                _merge_stats_entry(merged_stats._entries[new_id], src_entry, new_id)

        # --- Step 5: merge bucket files ---
        merged_buckets: Dict[int, bytes] = {}
        merged_bidx = BucketIndex()
        new_seq = 0

        for src_idx, state in enumerate(src_states):
            n_remap = name_remaps[src_idx]
            s_remap = seed_remaps[src_idx]
            rid_offset = run_id_offsets[src_idx]
            src_bidx = state['bucket_index']

            for bidx_entry in src_bidx._entries:
                old_seq = bidx_entry.bucket_seq
                compressed = state['buckets'].get(old_seq)
                if compressed is None:
                    continue
                # Remap name_ids in bucket if registry changed
                if n_remap or s_remap:
                    compressed = _remap_bucket(compressed, n_remap, s_remap)
                merged_buckets[new_seq] = compressed
                # Remap name_ids in the index entry
                min_nid = n_remap.get(bidx_entry.min_name_id, bidx_entry.min_name_id)
                max_nid = n_remap.get(bidx_entry.max_name_id, bidx_entry.max_name_id)
                merged_bidx.add_bucket(
                    new_seq, bidx_entry.ts_start, bidx_entry.ts_end,
                    bidx_entry.num_records, bidx_entry.fail_count,
                    min(min_nid, max_nid), max(min_nid, max_nid),
                )
                new_seq += 1

        # --- Step 6: merge ContribIndex ---
        merged_cidx = ContribIndex(merge_policy=POLICY_PASS_ONLY)
        for src_idx, state in enumerate(src_states):
            n_remap = name_remaps[src_idx]
            rid_offset = run_id_offsets[src_idx]
            ci = state['contrib_index']
            for entry in ci._entries:
                merged_cidx.add_entry(
                    run_id=entry.run_id + rid_offset,
                    name_id=n_remap.get(entry.name_id, entry.name_id),
                    status=entry.status,
                    flags=entry.flags,
                )
            # Advance watermark
            if ci.squash_watermark > 0:
                merged_cidx.set_squash_watermark(
                    max(merged_cidx.squash_watermark,
                        ci.squash_watermark + rid_offset))

        # --- Step 7: merge SquashLog (append-only, no run_id adjustment) ---
        merged_slog = SquashLog()
        for state in src_states:
            for entry in state['squash_log'].entries():
                merged_slog.append(
                    ts=entry.ts, policy=entry.policy,
                    from_run=entry.from_run, to_run=entry.to_run,
                    num_runs=entry.num_runs, pass_runs=entry.pass_runs,
                )

        # --- Assemble output members ---
        result: Dict[str, bytes] = {}
        result[MEMBER_TEST_REGISTRY] = merged_reg.serialize()
        result[MEMBER_TEST_STATS]    = merged_stats.serialize()
        result[MEMBER_BUCKET_INDEX]  = merged_bidx.serialize()
        result[MEMBER_CONTRIB_INDEX] = merged_cidx.serialize()
        result[MEMBER_SQUASH_LOG]    = merged_slog.serialize()
        for seq, data in merged_buckets.items():
            result[f"{HISTORY_BUCKET_DIR}{seq:06d}.bin"] = data

        return result

    def _read_v2_state(self, path: str) -> dict:
        """Read all v2 binary history members from a .cdb ZIP."""
        from .test_registry import TestRegistry
        from .test_stats import TestStatsTable
        from .bucket_index import BucketIndex
        from .contrib_index import ContribIndex, POLICY_PASS_ONLY
        from .squash_log import SquashLog

        with zipfile.ZipFile(path, "r") as zf:
            names = zf.namelist()

            def _read(member):
                return zf.read(member) if member in names else b''

            reg_data   = _read(MEMBER_TEST_REGISTRY)
            stats_data = _read(MEMBER_TEST_STATS)
            bidx_data  = _read(MEMBER_BUCKET_INDEX)
            cidx_data  = _read(MEMBER_CONTRIB_INDEX)
            slog_data  = _read(MEMBER_SQUASH_LOG)

            # Read all bucket files: history/NNNNNN.bin (not the index)
            buckets: Dict[int, bytes] = {}
            for n in names:
                if (n.startswith(HISTORY_BUCKET_DIR) and n.endswith(".bin")
                        and n != MEMBER_BUCKET_INDEX):
                    basename = n[len(HISTORY_BUCKET_DIR):]
                    try:
                        seq = int(basename.split(".")[0])
                        buckets[seq] = zf.read(n)
                    except ValueError:
                        pass

        return {
            'registry':     TestRegistry.deserialize(reg_data) if reg_data else TestRegistry(),
            'stats':        TestStatsTable.deserialize(stats_data) if stats_data else TestStatsTable(),
            'bucket_index': BucketIndex.deserialize(bidx_data) if bidx_data else BucketIndex(),
            'buckets':      buckets,
            'contrib_index': (ContribIndex.deserialize(cidx_data) if cidx_data
                              else ContribIndex(merge_policy=POLICY_PASS_ONLY)),
            'squash_log':   SquashLog.deserialize(slog_data) if slog_data else SquashLog(),
        }

    # ── Helpers ───────────────────────────────────────────────────────────

    def _merge_testplans(self, sources: list):
        """Return merged testplan bytes, or None if sources disagree.

        Strategy:
        1. If no source has a testplan → return None.
        2. If all sources with a testplan share the same ``source_file`` →
           return the bytes from whichever has the most recent ``import_timestamp``.
        3. If sources have different ``source_file`` values → emit a warning
           and return None (incompatible plans).
        """
        import warnings
        candidates = {}   # source_file → (import_timestamp, raw_bytes)
        for src in sources:
            with zipfile.ZipFile(src, "r") as zf:
                if MEMBER_TESTPLAN not in zf.namelist():
                    continue
                raw = zf.read(MEMBER_TESTPLAN)
                import json as _json
                d = _json.loads(raw)
                sf = d.get("source_file", "")
                ts = d.get("import_timestamp", "")
                if sf not in candidates or ts > candidates[sf][0]:
                    candidates[sf] = (ts, raw)
        if not candidates:
            return None
        if len(candidates) == 1:
            return next(iter(candidates.values()))[1]
        warnings.warn(
            f"Merging databases with different testplans "
            f"({list(candidates.keys())}); testplan omitted from output.",
            stacklevel=4,
        )
        return None

    def _merge_waivers(self, sources: list):
        """Return merged waivers bytes (union of all unique waiver ids).

        Waivers from all sources are combined; if two sources have a waiver
        with the same id, the one with the most recent ``approved_at`` wins.
        Returns None if no source has waivers.
        """
        import json as _json
        merged: dict = {}   # id → waiver dict
        any_found = False
        for src in sources:
            with zipfile.ZipFile(src, "r") as zf:
                if MEMBER_WAIVERS not in zf.namelist():
                    continue
                any_found = True
                raw = zf.read(MEMBER_WAIVERS)
                d = _json.loads(raw)
                for w in d.get("waivers", []):
                    wid = w.get("id", "")
                    existing = merged.get(wid)
                    if existing is None or w.get("approved_at", "") > existing.get("approved_at", ""):
                        merged[wid] = w
        if not any_found:
            return None
        out = {"format_version": 1, "waivers": list(merged.values())}
        return _json.dumps(out, separators=(',', ':')).encode()

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


# ── Module-level helpers ──────────────────────────────────────────────────


def _merge_stats_entry(dst, src, new_name_id: int) -> None:
    """Accumulate *src* TestStatsEntry into *dst* in place."""
    dst.name_id = new_name_id

    if src.first_ts > 0 and (dst.first_ts == 0 or src.first_ts < dst.first_ts):
        dst.first_ts = src.first_ts
    dst.last_ts = max(dst.last_ts, src.last_ts)
    dst.last_green_ts = max(dst.last_green_ts, src.last_green_ts)

    prev_total = dst.total_runs
    dst.total_runs       += src.total_runs
    dst.pass_count       += src.pass_count
    dst.fail_count       += src.fail_count
    dst.error_count      += src.error_count
    dst.transition_count += src.transition_count

    # Welford merge: combine two running means and M2 accumulators (Chan's formula)
    if src.total_runs > 0 and dst.total_runs > 0:
        n_a, n_b = prev_total, src.total_runs
        n_ab = n_a + n_b
        if n_ab > 0:
            delta = src.mean_cpu_time - dst.mean_cpu_time
            dst.mean_cpu_time = (n_a * dst.mean_cpu_time + n_b * src.mean_cpu_time) / n_ab
            dst.m2_cpu_time   = (dst.m2_cpu_time + src.m2_cpu_time
                                 + delta * delta * n_a * n_b / n_ab)

    # Recompute derived scores from accumulated counters
    if dst.total_runs > 0:
        dst.flake_score = dst.transition_count / max(dst.total_runs - 1, 1)
        dst.fail_rate   = dst.fail_count / dst.total_runs
    else:
        dst.flake_score = 0.0
        dst.fail_rate   = 0.0

    pass_rate = dst.pass_count / dst.total_runs if dst.total_runs else 1.0
    stability = 1.0 - dst.flake_score
    speed = max(0.0, 1.0 - dst.mean_cpu_time / 3600.0) if dst.mean_cpu_time > 0 else 1.0
    dst.grade_score = pass_rate * stability * speed

    # Take worst-case streak (most negative or most positive)
    if abs(src.streak) > abs(dst.streak):
        dst.streak = src.streak

    # Take max CUSUM
    dst.cusum_value = max(dst.cusum_value, src.cusum_value)
    dst.total_seeds_seen = max(dst.total_seeds_seen, src.total_seeds_seen)


def _remap_bucket(compressed: bytes, n_remap: Dict[int, int],
                  s_remap: Dict[int, int]) -> bytes:
    """Decode a compressed bucket, remap name_ids and seed_ids, re-encode.

    If neither remap changes any ID, the original compressed bytes are
    returned unchanged to avoid redundant work.
    """
    from .history_buckets import BucketReader, BucketWriter

    reader = BucketReader(compressed)
    all_recs = list(reader.all_records())

    # Check if any remapping is actually needed
    needs_remap = any(
        n_remap.get(r.name_id, r.name_id) != r.name_id
        or s_remap.get(r.seed_id, r.seed_id) != r.seed_id
        for r in all_recs
    )
    if not needs_remap:
        return compressed

    writer = BucketWriter()
    # Sort by (new_name_id, ts) for correct columnar layout
    remapped = sorted(
        all_recs,
        key=lambda r: (n_remap.get(r.name_id, r.name_id), r.ts),
    )
    for rec in remapped:
        writer.add(
            name_id=n_remap.get(rec.name_id, rec.name_id),
            seed_id=s_remap.get(rec.seed_id, rec.seed_id),
            ts=rec.ts,
            status=rec.status,
            flags=rec.flags,
        )
    return writer.seal(use_lzma=True)

