"""SQLite bin thresholds must survive persistence and drive report coverage."""

import pytest

from ucis import (
    UCIS_DU_MODULE, UCIS_ENABLED_STMT, UCIS_INSTANCE, UCIS_INST_ONCE,
    UCIS_OTHER, UCIS_SCOPE_UNDER_DU, UCIS_VLOG,
)
from ucis.cover_data import CoverData
from ucis.cover_type_t import CoverTypeT
from ucis.mem.mem_factory import MemFactory
from ucis.report.coverage_metrics import CoverageMetrics
from ucis.report.coverage_report_builder import CoverageReportBuilder
from ucis.source_info import SourceInfo
from ucis.sqlite.sqlite_cover_index import SqliteCoverIndex
from ucis.sqlite.sqlite_ucis import SqliteUCIS


def _create_coverpoint(db):
    src = SourceInfo(db.createFileHandle("design.sv", "/rtl"), 1, 0)
    du = db.createScope(
        "work.top", src, 1, UCIS_OTHER, UCIS_DU_MODULE,
        UCIS_ENABLED_STMT | UCIS_INST_ONCE | UCIS_SCOPE_UNDER_DU,
    )
    inst = db.createInstance(
        "tb", None, 1, UCIS_OTHER, UCIS_INSTANCE, du, UCIS_INST_ONCE,
    )
    cg = inst.createCovergroup("cg", src, 1, UCIS_OTHER)
    return cg.createCoverpoint("cp", src, 1, UCIS_VLOG), src


def _report_bins(report):
    def visit(cg):
        for cp in cg.coverpoints:
            yield from cp.bins
        for child in cg.covergroups:
            yield from visit(child)
    return [b for cg in report.covergroups for b in visit(cg)]


@pytest.mark.parametrize("count", [0, 2, 4, 5, 6])
def test_bin_threshold_matches_memory_after_reopen(tmp_path, count):
    expected_hit = count >= 5
    memory = MemFactory.create()
    cp, src = _create_coverpoint(memory)
    cp.createBin("bin", src, 5, count, "bin")
    memory_bin = _report_bins(CoverageReportBuilder.build(memory))[0]
    assert memory_bin.hit == expected_hit

    db_path = str(tmp_path / "coverage.db")
    db = SqliteUCIS(db_path)
    try:
        cp, src = _create_coverpoint(db)
        cover = cp.createBin("bin", src, 5, count, "bin")
        cover_id = cover.cover_id
        assert cover.getCoverData().at_least == 5
        assert cover.getCoverData().goal == 1
    finally:
        db.close()

    db = SqliteUCIS(db_path)
    try:
        data = SqliteCoverIndex(db, cover_id).getCoverData()
        assert (data.data, data.at_least, data.goal) == (count, 5, 1)
        report_bin = _report_bins(CoverageReportBuilder.build(db))[0]
        assert report_bin.count == memory_bin.count
        assert report_bin.hit == memory_bin.hit
        assert CoverageMetrics(db).summary()["covered_bins"] == int(expected_hit)
    finally:
        db.close()


@pytest.mark.parametrize("threshold,goal", [(1, 0), (5, 1), (5, 9)])
def test_create_next_cover_keeps_threshold_separate_from_goal(tmp_path, threshold, goal):
    db_path = str(tmp_path / "coverage.db")
    db = SqliteUCIS(db_path)
    try:
        cp, src = _create_coverpoint(db)
        data = CoverData(CoverTypeT.CVGBIN, 0)
        data.at_least = threshold
        data.goal = goal
        data.data = 2
        cover = cp.createNextCover("bin", data, src)
        cover_id = cover.cover_id
        cover.incrementCover()
    finally:
        db.close()

    db = SqliteUCIS(db_path)
    try:
        data = SqliteCoverIndex(db, cover_id).getCoverData()
        assert (data.data, data.at_least, data.goal) == (3, threshold, goal)
    finally:
        db.close()


def test_read_bin_with_unset_goal():
    """Older databases may have a NULL goal independent of the hit threshold."""
    db = SqliteUCIS()
    try:
        cp, src = _create_coverpoint(db)
        cover = cp.createBin("bin", src, 5, 2, "bin")
        db.conn.execute(
            "UPDATE coveritems SET goal = NULL WHERE cover_id = ?",
            (cover.cover_id,),
        )
        data = SqliteCoverIndex(db, cover.cover_id).getCoverData()
        assert (data.data, data.at_least, data.goal) == (2, 5, 0)
    finally:
        db.close()
