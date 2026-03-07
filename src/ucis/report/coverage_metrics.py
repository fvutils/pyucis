"""
Common coverage metrics layer.

``CoverageMetrics`` is the single source of truth for all coverage number
computation in pyucis.  Every consumer — TUI views, CLI ``show`` commands,
and report formatters — should obtain aggregated numbers from this class
rather than implementing their own UCIS tree walks or SQL queries.

Design principles
-----------------
* **Correct bin semantics**: a bin is *covered* when ``cover_data >= at_least``
  (UCIS LRM §5.3).  Using ``cover_data > 0`` is wrong when ``at_least > 1``.
* **Correct traversal**: functional coverage is derived from
  ``CoverageReportBuilder``, which walks ``INSTANCE → COVERGROUP → COVERPOINT``,
  preventing double-counting of type-level vs instance-level covergroup scopes.
* **SQLite fast paths** are used for performance but must produce results
  identical to the API path.
* **Caching** is simple dict-based; call ``invalidate()`` whenever the
  database filter changes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ucis.ucis import UCIS
    from ucis.report.coverage_report import CoverageReport


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class BinStats:
    """Aggregated bin counts for a coverage scope or type."""
    total: int = 0
    covered: int = 0

    @property
    def uncovered(self) -> int:
        return self.total - self.covered

    @property
    def coverage_pct(self) -> float:
        if self.total == 0:
            return 0.0
        return self.covered / self.total * 100.0

    def __add__(self, other: 'BinStats') -> 'BinStats':
        return BinStats(self.total + other.total, self.covered + other.covered)


@dataclass
class BinDetail:
    """Raw data for a single bin — used in detail/bin-listing views."""
    name: str
    count: int
    at_least: int
    is_ignore: bool = False
    is_illegal: bool = False

    @property
    def covered(self) -> bool:
        return self.count >= self.at_least


@dataclass
class CoverpointStats:
    """Coverage summary for a single coverpoint."""
    name: str
    path: str                    # slash-joined scope path from DB root
    bins: BinStats = field(default_factory=BinStats)
    bin_details: List[BinDetail] = field(default_factory=list)
    weight: int = 1

    @property
    def coverage_pct(self) -> float:
        return self.bins.coverage_pct


@dataclass
class CrossStats:
    """Coverage summary for a single cross."""
    name: str
    path: str
    bins: BinStats = field(default_factory=BinStats)
    weight: int = 1

    @property
    def coverage_pct(self) -> float:
        return self.bins.coverage_pct


@dataclass
class CovergroupStats:
    """Coverage summary for a covergroup (type-level or instance-level)."""
    name: str
    path: str
    coverage_pct: float = 0.0   # weighted over child coverpoints/crosses
    bins: BinStats = field(default_factory=BinStats)
    weight: int = 1


@dataclass
class FileCoverageStats:
    """Per-source-file code-coverage statistics."""
    file_id: int
    file_path: str
    line:   BinStats = field(default_factory=BinStats)
    branch: BinStats = field(default_factory=BinStats)
    toggle: BinStats = field(default_factory=BinStats)
    expr:   BinStats = field(default_factory=BinStats)
    cond:   BinStats = field(default_factory=BinStats)
    fsm:    BinStats = field(default_factory=BinStats)
    block:  BinStats = field(default_factory=BinStats)

    @property
    def overall(self) -> BinStats:
        result = BinStats()
        for attr in ('line', 'branch', 'toggle', 'expr', 'cond', 'fsm', 'block'):
            result = result + getattr(self, attr)
        return result


@dataclass
class TestInfo:
    """Identity and contribution metadata for one test run."""
    history_id: int        # internal DB id (-1 for non-SQLite backends)
    name: str
    status: str            # "PASSED" | "FAILED" | "UNKNOWN"
    date: str
    total_items: int = 0   # bins hit by this test  (SQLite only, else 0)
    unique_items: int = 0  # bins *only* hit by this test (SQLite only, else 0)


# ---------------------------------------------------------------------------
# CoverageMetrics
# ---------------------------------------------------------------------------

class CoverageMetrics:
    """
    Single source of truth for all coverage metric computation.

    Instantiate once per database and pass the instance to every consumer
    (TUI CoverageModel, show commands, report formatters).

    Parameters
    ----------
    db:
        Any object implementing the ``UCIS`` interface (MemUCIS, SqliteUCIS,
        XmlUCIS, …).
    """

    def __init__(self, db: 'UCIS'):
        self._db = db
        self._cache: Dict[str, object] = {}

    # ------------------------------------------------------------------ cache

    def invalidate(self):
        """Discard all cached results (e.g. after changing a test filter)."""
        self._cache.clear()

    def _cached(self, key: str, compute):
        if key not in self._cache:
            self._cache[key] = compute()
        return self._cache[key]

    # --------------------------------------------------------------- hierarchy

    @property
    def report(self) -> 'CoverageReport':
        """
        ``CoverageReport`` built via ``CoverageReportBuilder``.

        This is the canonical hierarchical representation of functional
        coverage.  All functional-coverage numbers in this class are derived
        from this object to guarantee consistency with the text / JSON / HTML
        report formatters.
        """
        return self._cached('report', self._build_report)

    def _build_report(self) -> 'CoverageReport':
        from ucis.report.coverage_report_builder import CoverageReportBuilder
        return CoverageReportBuilder.build(self._db)

    # ------------------------------------------ functional coverage (CVGBIN)

    def functional_bins(self) -> BinStats:
        """
        Aggregate ``BinStats`` for all functional-coverage bins (CVGBIN).

        A bin is counted as *covered* when ``count >= at_least`` — matching
        the UCIS LRM and the text-report formatter.
        """
        return self._cached('functional_bins', self._compute_functional_bins)

    def _compute_functional_bins(self) -> BinStats:
        # Derive directly from the canonical CoverageReport so that the
        # traversal (INSTANCE → COVERGROUP → COVERPOINT) is identical to what
        # the text / JSON reports use.  This also means the SQLite fast path
        # is not needed here — CoverageReportBuilder already handles both
        # backends efficiently.
        total = 0
        covered = 0
        for cg in self.report.covergroups:
            t, c = self._count_bins_in_cg(cg)
            total += t
            covered += c
        return BinStats(total=total, covered=covered)

    def _count_bins_in_cg(self, cg) -> tuple:
        """
        Recursively count (total, covered) bins in a CoverageReport.Covergroup.

        Mirrors CoverageReportBuilder.build_covergroup() semantics: when
        type-level coverpoints/crosses exist on the CG, only those are
        counted (the sub-instance COVERINSTANCE groups hold the same bins
        and would double-count if also visited).
        """
        total = 0
        covered = 0
        if cg.coverpoints or cg.crosses:
            # Type-level coverpoints are present — use them only
            for cp in cg.coverpoints:
                for b in cp.bins:
                    total += 1
                    if b.hit:
                        covered += 1
            for cr in cg.crosses:
                for b in cr.bins:
                    total += 1
                    if b.hit:
                        covered += 1
        else:
            # No type-level coverpoints — aggregate over sub-instances
            for sub in cg.covergroups:
                t, c = self._count_bins_in_cg(sub)
                total += t
                covered += c
        return total, covered

    def covergroup_stats(self) -> List[CovergroupStats]:
        """One ``CovergroupStats`` per top-level covergroup."""
        return self._cached('covergroup_stats', self._compute_covergroup_stats)

    def _compute_covergroup_stats(self) -> List[CovergroupStats]:
        result = []
        for cg in self.report.covergroups:
            t, c = self._count_bins_in_cg(cg)
            result.append(CovergroupStats(
                name=cg.name,
                path=cg.instname,
                coverage_pct=cg.coverage,
                bins=BinStats(total=t, covered=c),
                weight=cg.weight,
            ))
        return result

    def coverpoint_stats(self, include_bins: bool = False) -> List[CoverpointStats]:
        """
        Flat list of ``CoverpointStats`` for every coverpoint in the database.

        Parameters
        ----------
        include_bins:
            When ``True``, populate ``CoverpointStats.bin_details`` with
            per-bin data.  Slightly more expensive; not needed for summary views.
        """
        cache_key = f'coverpoint_stats_{include_bins}'
        return self._cached(cache_key,
                            lambda: self._compute_coverpoint_stats(include_bins))

    def _compute_coverpoint_stats(self, include_bins: bool) -> List[CoverpointStats]:
        result = []

        def _walk_cg(cg, path_prefix: str):
            cg_path = f'{path_prefix}/{cg.name}' if path_prefix else cg.name
            if cg.coverpoints or cg.crosses:
                # Type-level coverpoints/crosses present — use them
                for cp in cg.coverpoints:
                    total = len(cp.bins)
                    covered = sum(1 for b in cp.bins if b.hit)
                    details = []
                    if include_bins:
                        for b in cp.bins:
                            details.append(BinDetail(
                                name=b.name, count=b.count, at_least=b.goal))
                        for b in cp.ignore_bins:
                            details.append(BinDetail(
                                name=b.name, count=b.count, at_least=b.goal,
                                is_ignore=True))
                        for b in cp.illegal_bins:
                            details.append(BinDetail(
                                name=b.name, count=b.count, at_least=b.goal,
                                is_illegal=True))
                    result.append(CoverpointStats(
                        name=cp.name,
                        path=f'{cg_path}/{cp.name}',
                        bins=BinStats(total=total, covered=covered),
                        bin_details=details,
                        weight=cp.weight,
                    ))
            else:
                # No type-level coverpoints — recurse into sub-instances only
                for sub in cg.covergroups:
                    _walk_cg(sub, cg_path)

        for cg in self.report.covergroups:
            _walk_cg(cg, '')
        return result

    def cross_stats(self) -> List[CrossStats]:
        """Flat list of ``CrossStats`` for every cross in the database."""
        return self._cached('cross_stats', self._compute_cross_stats)

    def _compute_cross_stats(self) -> List[CrossStats]:
        result = []

        def _walk_cg(cg, path_prefix: str):
            cg_path = f'{path_prefix}/{cg.name}' if path_prefix else cg.name
            for cr in cg.crosses:
                total = len(cr.bins)
                covered = sum(1 for b in cr.bins if b.hit)
                result.append(CrossStats(
                    name=cr.name,
                    path=f'{cg_path}/{cr.name}',
                    bins=BinStats(total=total, covered=covered),
                    weight=cr.weight,
                ))
            for sub in cg.crosses:
                pass   # crosses do not nest
            for sub in cg.covergroups:
                _walk_cg(sub, cg_path)

        for cg in self.report.covergroups:
            _walk_cg(cg, '')
        return result

    # --------------------------------------- code coverage (STMT/BRANCH/etc.)

    def coverage_types_present(self) -> List:
        """``CoverTypeT`` values that have at least one item in the database."""
        return self._cached('coverage_types', self._compute_coverage_types)

    def _compute_coverage_types(self):
        from ucis.cover_type_t import CoverTypeT

        # SQLite fast path
        if hasattr(self._db, 'conn'):
            try:
                rows = self._db.conn.execute(
                    'SELECT DISTINCT cover_type FROM coveritems ORDER BY cover_type'
                ).fetchall()
                result = []
                for r in rows:
                    if r[0] is None:
                        continue
                    try:
                        result.append(CoverTypeT(r[0]))
                    except ValueError:
                        pass
                return result
            except Exception:
                pass

        # API fallback
        from ucis.scope_type_t import ScopeTypeT
        found = set()
        all_types = [
            CoverTypeT.CVGBIN, CoverTypeT.STMTBIN, CoverTypeT.BRANCHBIN,
            CoverTypeT.TOGGLEBIN, CoverTypeT.EXPRBIN, CoverTypeT.CONDBIN,
            CoverTypeT.FSMBIN, CoverTypeT.BLOCKBIN,
        ]

        def _visit(scope):
            for ct in all_types:
                if ct not in found:
                    try:
                        if next(iter(scope.coverItems(ct)), None) is not None:
                            found.add(ct)
                    except Exception:
                        pass
            for child in scope.scopes(ScopeTypeT.ALL):
                _visit(child)

        for scope in self._db.scopes(ScopeTypeT.ALL):
            _visit(scope)

        return sorted(found, key=lambda t: int(t))

    def bins_by_type(self, cov_type, test_filter: Optional[str] = None) -> BinStats:
        """
        ``BinStats`` for a single ``CoverTypeT``.

        For functional bins (``CVGBIN``), prefer ``functional_bins()`` which
        derives from the canonical traversal.  This method uses direct DB
        queries and is primarily intended for code-coverage types.

        Parameters
        ----------
        test_filter:
            Logical name of a test; when given, only items contributed by
            that test are counted.  SQLite only; ignored on other backends.
        """
        from ucis.cover_type_t import CoverTypeT

        # For CVGBIN with no filter, use the canonical computation.
        if cov_type == CoverTypeT.CVGBIN and test_filter is None:
            return self.functional_bins()

        cache_key = f'bins_by_type_{int(cov_type)}_{test_filter}'
        return self._cached(cache_key,
                            lambda: self._query_bins_by_type(cov_type, test_filter))

    def _query_bins_by_type(self, cov_type, test_filter: Optional[str]) -> BinStats:
        from ucis.scope_type_t import ScopeTypeT

        # SQLite fast path
        if hasattr(self._db, 'conn'):
            try:
                conn = self._db.conn
                if test_filter:
                    row = conn.execute(
                        """SELECT COUNT(*),
                                  SUM(CASE WHEN ci.cover_data >= ci.at_least THEN 1 ELSE 0 END)
                           FROM coveritems ci
                           JOIN coveritem_tests ct ON ct.cover_id = ci.cover_id
                           JOIN history_nodes hn ON hn.history_id = ct.history_id
                           WHERE (ci.cover_type & ?) != 0
                             AND hn.logical_name = ?""",
                        (int(cov_type), test_filter)
                    ).fetchone()
                else:
                    row = conn.execute(
                        """SELECT COUNT(*),
                                  SUM(CASE WHEN cover_data >= at_least THEN 1 ELSE 0 END)
                           FROM coveritems
                           WHERE (cover_type & ?) != 0""",
                        (int(cov_type),)
                    ).fetchone()
                return BinStats(total=row[0] or 0, covered=row[1] or 0)
            except Exception:
                pass

        # API fallback
        total = 0
        covered = 0

        def _visit(scope):
            nonlocal total, covered
            try:
                for item in scope.coverItems(cov_type):
                    total += 1
                    cd = item.getCoverData()
                    if cd and cd.data >= cd.at_least:
                        covered += 1
            except Exception:
                pass
            try:
                for child in scope.scopes(ScopeTypeT.ALL):
                    _visit(child)
            except Exception:
                pass

        for scope in self._db.scopes(ScopeTypeT.ALL):
            _visit(scope)

        return BinStats(total=total, covered=covered)

    def code_coverage_by_type(self) -> Dict:
        """
        Per-type ``BinStats`` for all non-functional coverage item types
        (STMTBIN, BRANCHBIN, TOGGLEBIN, EXPRBIN, CONDBIN, FSMBIN, BLOCKBIN).
        """
        return self._cached('code_coverage_by_type', self._compute_code_coverage)

    def _compute_code_coverage(self) -> Dict:
        from ucis.cover_type_t import CoverTypeT
        code_types = [
            CoverTypeT.STMTBIN, CoverTypeT.BRANCHBIN, CoverTypeT.TOGGLEBIN,
            CoverTypeT.EXPRBIN, CoverTypeT.CONDBIN, CoverTypeT.FSMBIN,
            CoverTypeT.BLOCKBIN,
        ]

        # SQLite fast path — single query for all types
        if hasattr(self._db, 'conn'):
            try:
                rows = self._db.conn.execute(
                    """SELECT cover_type,
                              COUNT(*) AS total,
                              SUM(CASE WHEN cover_data >= at_least THEN 1 ELSE 0 END) AS covered
                       FROM coveritems
                       GROUP BY cover_type"""
                ).fetchall()
                int_to_type = {int(ct): ct for ct in code_types}
                result = {ct: BinStats() for ct in code_types}
                for row in rows:
                    ct = int_to_type.get(row[0])
                    if ct is not None:
                        result[ct] = BinStats(total=row[1] or 0, covered=row[2] or 0)
                return result
            except Exception:
                pass

        # API fallback
        result = {}
        for ct in code_types:
            result[ct] = self._query_bins_by_type(ct, test_filter=None)
        return result

    def file_coverage(self, test_filter: Optional[str] = None) -> List[FileCoverageStats]:
        """
        Per-source-file code-coverage statistics.

        Requires a SQLite backend; returns an empty list for other backends.

        Parameters
        ----------
        test_filter:
            Restrict counts to items contributed by the named test.
        """
        cache_key = f'file_coverage_{test_filter}'
        return self._cached(cache_key, lambda: self._compute_file_coverage(test_filter))

    def _compute_file_coverage(self, test_filter: Optional[str]) -> List[FileCoverageStats]:
        if not hasattr(self._db, 'conn'):
            return []

        from ucis.cover_type_t import CoverTypeT
        STMT   = int(CoverTypeT.STMTBIN)
        BRANCH = int(CoverTypeT.BRANCHBIN)
        TOGGLE = int(CoverTypeT.TOGGLEBIN)
        EXPR   = int(CoverTypeT.EXPRBIN)
        COND   = int(CoverTypeT.CONDBIN)
        FSM    = int(CoverTypeT.FSMBIN)
        BLOCK  = int(CoverTypeT.BLOCKBIN)

        conn = self._db.conn

        try:
            if test_filter:
                # Get covered item IDs for this test first
                rows = conn.execute(
                    """SELECT ci.cover_id FROM coveritems ci
                       JOIN coveritem_tests ct ON ct.cover_id = ci.cover_id
                       JOIN history_nodes hn ON hn.history_id = ct.history_id
                       WHERE hn.logical_name = ?""",
                    (test_filter,)
                ).fetchall()
                if not rows:
                    return []
                id_csv = ','.join(str(r[0]) for r in rows)
                filter_clause = f'AND ci.cover_id IN ({id_csv})'
            else:
                filter_clause = ''

            def _stat(type_int: int, rows_by_file: dict, file_id: int) -> BinStats:
                row = rows_by_file.get((file_id, type_int))
                if row is None:
                    return BinStats()
                return BinStats(total=row[0], covered=row[1])

            # One query: group by (file_id, cover_type)
            sql = f"""
                SELECT
                    f.file_id,
                    f.file_path,
                    ci.cover_type,
                    COUNT(*) AS total,
                    SUM(CASE WHEN ci.cover_data >= ci.at_least THEN 1 ELSE 0 END) AS covered
                FROM files f
                JOIN coveritems ci ON f.file_id = ci.source_file_id
                WHERE ci.cover_type IN (?,?,?,?,?,?,?)
                {filter_clause}
                GROUP BY f.file_id, f.file_path, ci.cover_type
                ORDER BY f.file_path
            """
            rows = conn.execute(sql, (STMT, BRANCH, TOGGLE, EXPR, COND, FSM, BLOCK)).fetchall()

            # Build {file_id → FileCoverageStats}
            files: Dict[int, FileCoverageStats] = {}
            file_paths: Dict[int, str] = {}
            by_file_type: Dict[tuple, tuple] = {}
            for row in rows:
                fid = row[0]
                file_paths[fid] = row[1]
                by_file_type[(fid, row[2])] = (row[3], row[4])

            for fid, fpath in file_paths.items():
                fcs = FileCoverageStats(
                    file_id=fid,
                    file_path=fpath,
                    line=BinStats(*by_file_type.get((fid, STMT),   (0, 0))),
                    branch=BinStats(*by_file_type.get((fid, BRANCH), (0, 0))),
                    toggle=BinStats(*by_file_type.get((fid, TOGGLE), (0, 0))),
                    expr=BinStats(*by_file_type.get((fid, EXPR),   (0, 0))),
                    cond=BinStats(*by_file_type.get((fid, COND),   (0, 0))),
                    fsm=BinStats(*by_file_type.get((fid, FSM),    (0, 0))),
                    block=BinStats(*by_file_type.get((fid, BLOCK),  (0, 0))),
                )
                files[fid] = fcs

            return sorted(files.values(), key=lambda f: f.file_path)
        except Exception:
            return []

    # ------------------------------------------------------------------ tests

    def tests(self) -> List[TestInfo]:
        """
        All tests with identity and (where available) contribution metadata.

        ``total_items`` and ``unique_items`` are populated only for SQLite
        backends; they are 0 for XML / memory backends.
        """
        return self._cached('tests', self._compute_tests)

    def _compute_tests(self) -> List[TestInfo]:
        from ucis.history_node_kind import HistoryNodeKind
        try:
            from ucis import UCIS_TESTSTATUS_OK
        except ImportError:
            UCIS_TESTSTATUS_OK = 1

        result: List[TestInfo] = []

        # SQLite path: use test-coverage API for contribution data
        if hasattr(self._db, 'conn'):
            try:
                from ucis.sqlite.sqlite_test_coverage import SqliteTestCoverage
                api = SqliteTestCoverage(self._db)
                contribs = api.get_all_test_contributions()
                contrib_map = {c.test_name: c for c in contribs}

                for node in self._db.historyNodes(HistoryNodeKind.TEST):
                    name = node.getLogicalName() or 'Unknown'
                    contrib = contrib_map.get(name)

                    status = 'UNKNOWN'
                    try:
                        raw = node.getTestStatus()
                        status = 'PASSED' if raw == UCIS_TESTSTATUS_OK else 'FAILED'
                    except Exception:
                        pass

                    date = 'Unknown'
                    try:
                        d = node.getDate()
                        if d:
                            date = str(d)
                    except Exception:
                        pass

                    result.append(TestInfo(
                        history_id=getattr(node, 'history_id', -1),
                        name=name,
                        status=status,
                        date=date,
                        total_items=contrib.total_items if contrib else 0,
                        unique_items=contrib.unique_items if contrib else 0,
                    ))
                return result
            except Exception:
                pass

        # API fallback (no contribution data)
        try:
            for node in self._db.historyNodes(HistoryNodeKind.TEST):
                name = node.getLogicalName() or 'Unknown'

                status = 'UNKNOWN'
                try:
                    raw = node.getTestStatus()
                    status = 'PASSED' if raw == UCIS_TESTSTATUS_OK else 'FAILED'
                except Exception:
                    pass

                date = 'Unknown'
                try:
                    d = node.getDate()
                    if d:
                        date = str(d)
                except Exception:
                    pass

                result.append(TestInfo(
                    history_id=-1,
                    name=name,
                    status=status,
                    date=date,
                ))
        except Exception:
            pass

        return result

    # -------------------------------------------------------- summary helpers

    def summary(self) -> Dict:
        """
        High-level summary dict — backward-compatible replacement for
        ``CoverageModel.get_summary()``.

        ``total_bins`` / ``covered_bins`` reflect ALL coverage items in the DB
        (functional + code coverage).  When the database contains functional
        coverage (CVGBIN), ``overall_coverage`` is derived from functional
        bins only (to preserve UCIS semantics); otherwise it is derived from
        all available items.
        """
        return self._cached('summary', self._compute_summary)

    def _compute_summary(self) -> Dict:
        fb = self.functional_bins()
        cg_stats = self.covergroup_stats()
        cp_stats = self.coverpoint_stats()

        if fb.total > 0:
            # Use functional coverage as the primary metric
            return {
                'overall_coverage': fb.coverage_pct,
                'total_bins': fb.total,
                'covered_bins': fb.covered,
                'covergroups': len(cg_stats),
                'coverpoints': len(cp_stats),
            }
        else:
            # No functional coverage — aggregate code coverage items
            total = 0
            covered = 0
            from ucis.cover_type_t import CoverTypeT
            code_types = [
                CoverTypeT.STMTBIN, CoverTypeT.BRANCHBIN, CoverTypeT.TOGGLEBIN,
                CoverTypeT.EXPRBIN, CoverTypeT.CONDBIN, CoverTypeT.FSMBIN,
                CoverTypeT.BLOCKBIN,
            ]
            for ct in code_types:
                bs = self.bins_by_type(ct)
                total += bs.total
                covered += bs.covered
            pct = (covered / total * 100.0) if total > 0 else 0.0
            return {
                'overall_coverage': pct,
                'total_bins': total,
                'covered_bins': covered,
                'covergroups': 0,
                'coverpoints': 0,
            }

    def database_info(self) -> Dict:
        """
        Database metadata — backward-compatible replacement for
        ``CoverageModel.get_database_info()``.
        """
        return {
            'path': getattr(self._db, 'db_path',
                            getattr(self._db, '_db_path', '')),
            'format': 'UCIS',
            'test_count': len(self.tests()),
        }
