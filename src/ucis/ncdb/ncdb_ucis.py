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

Binary history v2 usage::

    db = NcdbUCIS("coverage.cdb")
    run_id = db.add_test_run("uart_smoke", seed="12345",
                             status=HIST_STATUS_OK, has_coverage=True)
    entry  = db.get_test_stats("uart_smoke")
    print(entry.flake_score)
"""

import time
import zipfile
import json
from typing import Dict, List, Optional

from ucis.mem.mem_ucis import MemUCIS
from ucis.history_node_kind import HistoryNodeKind

from .constants import (
    MEMBER_MANIFEST, MEMBER_STRINGS, MEMBER_SCOPE_TREE,
    MEMBER_COUNTS, MEMBER_HISTORY, MEMBER_SOURCES,
    MEMBER_ATTRS, MEMBER_TAGS, MEMBER_PROPERTIES,
    MEMBER_TOGGLE, MEMBER_FSM, MEMBER_CROSS, MEMBER_DESIGN_UNITS,
    MEMBER_CONTRIB_DIR, MEMBER_FORMAL,
    MEMBER_TEST_REGISTRY, MEMBER_TEST_STATS,
    MEMBER_BUCKET_INDEX, MEMBER_CONTRIB_INDEX, MEMBER_SQUASH_LOG,
    HISTORY_BUCKET_DIR, HISTORY_FORMAT_V2,
    HIST_FLAG_IS_RERUN, HIST_FLAG_HAS_COVERAGE,
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
    - **v2_history**: loaded on demand when any v2 API method is called.

    Once loaded, a unit is never re-read.
    """

    def __init__(self, path: str):
        super().__init__()
        self._ncdb_path = path
        self._loaded_history = False
        self._loaded_scopes = False
        self._loaded_attrs = False
        self._loaded_v2_history = False
        self._du_index: dict = {}   # name → DU scope (populated after _ensure_scopes)
        self._zf_cache: dict = {}   # member name → bytes (populated on first open)

        # Binary history v2 state (None until _ensure_v2_history() is called)
        self._test_registry = None
        self._test_stats = None
        self._bucket_index = None
        self._contrib_index = None
        self._squash_log = None
        self._current_bucket_writer = None
        self._sealed_buckets: Dict[int, bytes] = {}  # seq → compressed bytes
        self._history_v2_dirty: bool = False

        # Testplan lazy state
        self._loaded_testplan: bool = False
        self._testplan = None          # Optional[Testplan]
        self._testplan_dirty: bool = False

        # Waivers lazy state
        self._loaded_waivers: bool = False
        self._waivers = None           # Optional[WaiverSet]
        self._waivers_dirty: bool = False

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

    # ── Binary history v2 API ─────────────────────────────────────────────

    def add_test_run(self, name: str, seed="0", status: int = 0,
                     ts: Optional[int] = None,
                     cpu_time: Optional[float] = None,
                     has_coverage: bool = False,
                     is_rerun: bool = False) -> int:
        """Record one test run in the binary history store.

        Automatically upgrades the manifest to ``history_format = "v2"`` on
        first call (no explicit opt-in required).

        Args:
            name:         Test base-name (e.g. ``"uart_smoke"``).
            seed:         Test seed string or integer (converted to str).
            status:       One of the ``HIST_STATUS_*`` constants.
            ts:           Unix timestamp; defaults to ``int(time.time())``.
            cpu_time:     CPU/wall time in seconds (optional).
            has_coverage: True if this run produced coverage data.
            is_rerun:     True if this is a retry of a previously-failed run.

        Returns:
            The run_id assigned to this run.
        """
        self._ensure_v2_history()
        if ts is None:
            ts = int(time.time())
        seed_str = str(seed)

        name_id = self._test_registry.lookup_name_id(name)
        seed_id = self._test_registry.lookup_seed_id(seed_str)
        run_id  = self._test_registry.assign_run_id()

        self._test_stats.update(name_id, status, ts,
                                cpu_time=cpu_time, seed_id=seed_id)

        flags = 0
        if is_rerun:
            flags |= HIST_FLAG_IS_RERUN
        if has_coverage:
            flags |= HIST_FLAG_HAS_COVERAGE
        self._current_bucket_writer.add(name_id, seed_id, ts, status, flags)

        if self._current_bucket_writer.is_full():
            self._seal_current_bucket()

        if has_coverage:
            from .contrib_index import FLAG_IS_RERUN as CI_IS_RERUN
            ci_flags = CI_IS_RERUN if is_rerun else 0
            self._contrib_index.add_entry(run_id, name_id, status, ci_flags)

        self._history_v2_dirty = True
        return run_id

    def query_test_history(self, name: str,
                           ts_from: Optional[int] = None,
                           ts_to: Optional[int] = None) -> list:
        """Return all BucketRecord objects for *name* across all buckets.

        Args:
            name:    Test name to query.
            ts_from: Optional lower bound timestamp (inclusive).
            ts_to:   Optional upper bound timestamp (inclusive).

        Returns:
            List of :class:`~ucis.ncdb.history_buckets.BucketRecord`.
        """
        self._ensure_v2_history()
        if name not in self._test_registry._name_to_id:
            return []
        name_id = self._test_registry._name_to_id[name]

        candidate_buckets = self._bucket_index.buckets_for_name(
            name_id, ts_from=ts_from, ts_to=ts_to)

        results = []
        for entry in candidate_buckets:
            seq = entry.bucket_seq
            if seq in self._sealed_buckets:
                data = self._sealed_buckets[seq]
            else:
                # Load from ZIP on demand
                member = f"{HISTORY_BUCKET_DIR}{seq:06d}.bin"
                self._read_zip()
                if member not in self._zf_cache:
                    continue
                data = self._zf_cache[member]
            from .history_buckets import BucketReader
            reader = BucketReader(data)
            recs = reader.records_for_name(name_id)
            if ts_from is not None:
                recs = [r for r in recs if r.ts >= ts_from]
            if ts_to is not None:
                recs = [r for r in recs if r.ts <= ts_to]
            results.extend(recs)

        # Also check the current (unsaved) bucket
        if self._current_bucket_writer is not None and self._current_bucket_writer.num_records > 0:
            try:
                from .history_buckets import BucketReader
                data = self._current_bucket_writer.seal_fast()
                reader = BucketReader(data)
                recs = reader.records_for_name(name_id)
                if ts_from is not None:
                    recs = [r for r in recs if r.ts >= ts_from]
                if ts_to is not None:
                    recs = [r for r in recs if r.ts <= ts_to]
                results.extend(recs)
            except Exception:
                pass

        return results

    def get_test_stats(self, name: str):
        """Return the TestStatsEntry for *name*, or None if not seen.

        Returns:
            :class:`~ucis.ncdb.test_stats.TestStatsEntry` or None.
        """
        self._ensure_v2_history()
        if name not in self._test_registry._name_to_id:
            return None
        name_id = self._test_registry._name_to_id[name]
        entry = self._test_stats.get(name_id)
        if entry is not None and entry.total_runs == 0:
            return None
        return entry

    def top_flaky_tests(self, n: int = 20) -> list:
        """Return top-*n* flakiest tests.

        Returns:
            List of :class:`~ucis.ncdb.test_stats.TestStatsEntry`.
        """
        self._ensure_v2_history()
        return self._test_stats.top_flaky(n)

    def top_failing_tests(self, n: int = 20) -> list:
        """Return top-*n* consistently-failing tests.

        Returns:
            List of :class:`~ucis.ncdb.test_stats.TestStatsEntry`.
        """
        self._ensure_v2_history()
        return self._test_stats.top_failing(n)

    def squash_coverage(self, policy: int = 1) -> None:
        """Squash all active contrib entries into counts.bin contribution.

        Records the squash in the squash_log for provenance auditing.

        Args:
            policy: Merge policy constant from :mod:`~ucis.ncdb.contrib_index`.
        """
        self._ensure_v2_history()
        import time as _time
        from .contrib_index import ContribIndex
        passing = self._contrib_index.passing_run_ids(policy)
        watermark = self._contrib_index.max_run_id()
        from_run  = self._contrib_index.squash_watermark
        num_runs  = self._contrib_index.num_active

        self._squash_log.append(
            ts=int(_time.time()),
            policy=policy,
            from_run=from_run,
            to_run=watermark,
            num_runs=num_runs,
            pass_runs=len(passing),
        )
        self._contrib_index.remove_entries_up_to(watermark)
        self._contrib_index.set_squash_watermark(watermark)
        self._history_v2_dirty = True

    def get_v2_members(self) -> Dict[str, bytes]:
        """Return a dict of member-name → bytes for all v2 binary members.

        Called by NcdbWriter to include v2 data in the ZIP output.  Returns
        an empty dict if no v2 history has been recorded.
        """
        if not self._history_v2_dirty and self._test_registry is None:
            return {}
        if self._test_registry is None:
            return {}

        members: Dict[str, bytes] = {}
        members[MEMBER_TEST_REGISTRY] = self._test_registry.serialize()
        members[MEMBER_TEST_STATS]    = self._test_stats.serialize()
        members[MEMBER_CONTRIB_INDEX] = self._contrib_index.serialize()
        members[MEMBER_SQUASH_LOG]    = self._squash_log.serialize()

        # Sealed buckets (copy verbatim — already compressed)
        for seq, data in self._sealed_buckets.items():
            members[f"{HISTORY_BUCKET_DIR}{seq:06d}.bin"] = data

        # Current (open) bucket — fast DEFLATE; add synthetic index entry so
        # the merger (and reader) can discover it via bucket_index.
        from .bucket_index import BucketIndex
        out_bidx = self._bucket_index  # reference; we may replace below
        if self._current_bucket_writer is not None and \
                self._current_bucket_writer.num_records > 0:
            seq = self._bucket_index.next_seq()
            members[f"{HISTORY_BUCKET_DIR}{seq:06d}.bin"] = \
                self._current_bucket_writer.seal_fast()
            # Build a copy of bucket_index with the extra synthetic entry
            from .constants import HIST_STATUS_FAIL
            recs = self._current_bucket_writer._records
            ts_start    = min(r.ts for r in recs)
            ts_end      = max(r.ts for r in recs)
            fail_count  = sum(1 for r in recs if r.status == HIST_STATUS_FAIL)
            min_name_id = min(r.name_id for r in recs)
            max_name_id = max(r.name_id for r in recs)
            out_bidx = BucketIndex.deserialize(self._bucket_index.serialize())
            out_bidx.add_bucket(seq, ts_start, ts_end,
                                len(recs), fail_count,
                                min_name_id, max_name_id)

        members[MEMBER_BUCKET_INDEX] = out_bidx.serialize()
        return members

    # ── Testplan API ──────────────────────────────────────────────────────

    def getTestplan(self):
        """Return the embedded testplan, or ``None`` if none is stored.

        Returns:
            :class:`~ucis.ncdb.testplan.Testplan` or ``None``.
        """
        self._ensure_testplan()
        return self._testplan

    def setTestplan(self, tp) -> None:
        """Embed *tp* in this database.

        The testplan is written to ``testplan.json`` on the next
        :meth:`~ucis.ncdb.ncdb_writer.NcdbWriter.write` call.

        Args:
            tp: :class:`~ucis.ncdb.testplan.Testplan` instance.
        """
        if not tp.import_timestamp:
            tp.stamp_import_time()
        self._testplan = tp
        self._testplan_dirty = True
        self._loaded_testplan = True

    def _ensure_testplan(self) -> None:
        if self._loaded_testplan:
            return
        self._loaded_testplan = True
        self._read_zip()
        from .constants import MEMBER_TESTPLAN
        raw = self._zf_cache.get(MEMBER_TESTPLAN)
        if raw:
            from .testplan import Testplan
            self._testplan = Testplan.from_bytes(raw)

    # ── Waivers API ───────────────────────────────────────────────────────

    def getWaivers(self):
        """Return the embedded waiver set, or ``None`` if none is stored.

        Returns:
            :class:`~ucis.ncdb.waivers.WaiverSet` or ``None``.
        """
        self._ensure_waivers()
        return self._waivers

    def setWaivers(self, ws) -> None:
        """Embed *ws* in this database.

        Args:
            ws: :class:`~ucis.ncdb.waivers.WaiverSet` instance.
        """
        self._waivers = ws
        self._waivers_dirty = True
        self._loaded_waivers = True

    def _ensure_waivers(self) -> None:
        if self._loaded_waivers:
            return
        self._loaded_waivers = True
        self._read_zip()
        from .constants import MEMBER_WAIVERS
        raw = self._zf_cache.get(MEMBER_WAIVERS)
        if raw:
            from .waivers import WaiverSet
            self._waivers = WaiverSet.from_bytes(raw)

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

    def _ensure_v2_history(self) -> None:
        """Load v2 binary history from ZIP, or initialize empty state."""
        if self._loaded_v2_history:
            return
        self._loaded_v2_history = True
        self._read_zip()
        self._load_v2_history(self._zf_cache)

    def _load_v2_history(self, zf_cache: dict) -> None:
        """Deserialize v2 binary members from the ZIP cache dict."""
        from .test_registry import TestRegistry
        from .test_stats import TestStatsTable
        from .bucket_index import BucketIndex
        from .contrib_index import ContribIndex, POLICY_PASS_ONLY
        from .squash_log import SquashLog
        from .history_buckets import BucketWriter, BucketReader

        if MEMBER_TEST_REGISTRY in zf_cache:
            self._test_registry = TestRegistry.deserialize(
                zf_cache[MEMBER_TEST_REGISTRY])
        else:
            self._test_registry = TestRegistry()

        if MEMBER_TEST_STATS in zf_cache:
            self._test_stats = TestStatsTable.deserialize(
                zf_cache[MEMBER_TEST_STATS])
        else:
            self._test_stats = TestStatsTable()

        if MEMBER_BUCKET_INDEX in zf_cache:
            self._bucket_index = BucketIndex.deserialize(
                zf_cache[MEMBER_BUCKET_INDEX])
        else:
            self._bucket_index = BucketIndex()

        if MEMBER_CONTRIB_INDEX in zf_cache:
            self._contrib_index = ContribIndex.deserialize(
                zf_cache[MEMBER_CONTRIB_INDEX])
        else:
            self._contrib_index = ContribIndex(merge_policy=POLICY_PASS_ONLY)

        if MEMBER_SQUASH_LOG in zf_cache:
            self._squash_log = SquashLog.deserialize(zf_cache[MEMBER_SQUASH_LOG])
        else:
            self._squash_log = SquashLog()

        # Load sealed buckets into memory (verbatim compressed bytes)
        self._sealed_buckets = {}
        for member, data in zf_cache.items():
            if member.startswith(HISTORY_BUCKET_DIR) and member.endswith(".bin") \
                    and member != MEMBER_BUCKET_INDEX:
                # Parse seq from filename: "history/000001.bin" → 1
                basename = member[len(HISTORY_BUCKET_DIR):]
                try:
                    seq = int(basename.split(".")[0])
                    self._sealed_buckets[seq] = data
                except ValueError:
                    pass

        # Start a fresh current bucket (for new records written this session)
        self._current_bucket_writer = BucketWriter()

    def _seal_current_bucket(self) -> None:
        """Seal the current bucket and start a new one."""
        from .history_buckets import BucketWriter, BucketReader
        w = self._current_bucket_writer
        if w.num_records == 0:
            return
        seq = self._bucket_index.next_seq()
        data = w.seal(use_lzma=True)
        self._sealed_buckets[seq] = data

        # Build bucket index entry from reader
        reader = BucketReader(data)
        all_recs = list(reader.all_records())
        ts_start = min(r.ts for r in all_recs)
        ts_end   = max(r.ts for r in all_recs)
        fail_count = sum(1 for r in all_recs if r.status != 0)
        name_ids = [r.name_id for r in all_recs]
        self._bucket_index.add_bucket(
            seq, ts_start, ts_end,
            num_records=w.num_records,
            fail_count=fail_count,
            min_name_id=min(name_ids),
            max_name_id=max(name_ids),
        )
        self._current_bucket_writer = BucketWriter()


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
