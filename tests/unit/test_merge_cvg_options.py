'''
DbMerger must carry covergroup, coverpoint and cross options from the
source databases into the merged database, rather than leaving the
merged scopes at their constructor defaults (issue #50). Covers the
generic DbMerger and the SqliteMerger paths used by `ucis merge` and
`ucis convert` for SQLite output.
'''
import logging
import os
import pytest
from ucis import UCIS_OTHER, UCIS_DU_MODULE, UCIS_INSTANCE, UCIS_VLOG, \
    UCIS_INST_ONCE, UCIS_SCOPE_UNDER_DU
from ucis.cover_type_t import CoverTypeT
from ucis.mem.mem_factory import MemFactory
from ucis.merge.db_merger import DbMerger
from ucis.scope_type_t import ScopeTypeT
from ucis.source_info import SourceInfo
from ucis.sqlite.sqlite_ucis import SqliteUCIS
from ucis.xml.xml_factory import XmlFactory


def _build_db(auto_bin_max=0, at_least=0, comment="cp comment", db=None):
    if db is None:
        db = MemFactory.create()
    file = db.createFileHandle("dummy", os.getcwd())
    srcinfo = SourceInfo(file, 0, 0)
    du = db.createScope("top", srcinfo, 1, UCIS_OTHER, UCIS_DU_MODULE,
                        UCIS_INST_ONCE | UCIS_SCOPE_UNDER_DU)
    inst = db.createInstance("top", None, 1, UCIS_OTHER, UCIS_INSTANCE,
                             du, UCIS_INST_ONCE)

    cg = inst.createCovergroup("cg", SourceInfo(file, 3, 0), 1, UCIS_OTHER)
    cg.setGoal(90)
    cg.setAtLeast(at_least)
    cg.setAutoBinMax(auto_bin_max)
    cg.setPerInstance(False)
    cg.setMergeInstances(False)
    cg.setGetInstCoverage(True)
    cg.setComment("cg comment")

    cp_l = []
    for name in ("cp", "cp2"):
        cp = cg.createCoverpoint(name, SourceInfo(file, 4, 0), 1, UCIS_VLOG)
        cp.setGoal(80)
        cp.setAtLeast(at_least)
        cp.setAutoBinMax(auto_bin_max)
        cp.setDetectOverlap(False)
        cp.setStrobe(1)
        cp.setComment(comment)
        cp.createBin("a", SourceInfo(file, 4, 0), at_least, 5, "a")
        cp_l.append(cp)

    cr = cg.createCross("cr", SourceInfo(file, 5, 0), 1, UCIS_VLOG, cp_l)
    cr.setGoal(70)
    cr.setAtLeast(at_least)
    cr.setComment("cr comment")
    cr.createBin("<a,a>", SourceInfo(file, 5, 0), at_least, 2, "<a,a>")

    cg_i = cg.createCoverInstance("cg_i", SourceInfo(file, 6, 0), 1, UCIS_OTHER)
    cg_i.setAtLeast(at_least)
    cg_i.setAutoBinMax(auto_bin_max)
    cg_i.setPerInstance(False)
    cp = cg_i.createCoverpoint("cp", SourceInfo(file, 4, 0), 1, UCIS_VLOG)
    cp.setAtLeast(at_least)
    cp.setAutoBinMax(auto_bin_max)
    cp.createBin("a", SourceInfo(file, 4, 0), at_least, 5, "a")
    return db


def _find(scope, path):
    # The DU and the instance are both named "top", so backtrack
    name, _, rest = path.partition(".")
    for s in scope.scopes(ScopeTypeT.ALL):
        if s.getScopeName() == name:
            found = _find(s, rest) if rest else s
            if found is not None:
                return found
    return None


def _merge(*src_l):
    dst = MemFactory.create()
    DbMerger().merge(dst, list(src_l))
    return dst


def _merge_mem_to_sqlite(src):
    # `ucis convert` to SQLite: SqliteMerger with an in-memory source
    dst = SqliteUCIS()
    dst.merge(src)
    return dst


def _merge_sqlite_to_sqlite(src):
    # `ucis merge` of SQLite inputs: SqliteMerger with a SQLite source
    sqlite_src = _build_db(db=SqliteUCIS())
    dst = SqliteUCIS()
    dst.merge(sqlite_src)
    return dst


MERGES = {
    "db_merger": _merge,
    "mem_to_sqlite": _merge_mem_to_sqlite,
    "sqlite_to_sqlite": _merge_sqlite_to_sqlite,
}


@pytest.fixture(params=list(MERGES))
def merge(request):
    return MERGES[request.param]


class TestMergeCvgOptions:

    def test_covergroup_options(self, merge):
        cg = _find(merge(_build_db()), "top.cg")
        assert cg.getGoal() == 90
        assert cg.getAtLeast() == 0
        assert cg.getAutoBinMax() == 0
        assert cg.getPerInstance() is False
        assert cg.getMergeInstances() is False
        assert cg.getGetInstCoverage() is True
        assert cg.getComment() == "cg comment"

    def test_coverpoint_options(self, merge):
        cp = _find(merge(_build_db()), "top.cg.cp")
        assert cp.getGoal() == 80
        assert cp.getAtLeast() == 0
        assert cp.getAutoBinMax() == 0
        assert cp.getDetectOverlap() is False
        assert cp.getStrobe() == 1
        assert cp.getComment() == "cp comment"

    def test_cross_options(self, merge):
        cr = _find(merge(_build_db()), "top.cg.cr")
        assert cr.getGoal() == 70
        assert cr.getAtLeast() == 0
        assert cr.getComment() == "cr comment"

    def test_coverinstance_options(self, merge):
        dst = merge(_build_db())
        cg_i = _find(dst, "top.cg.cg_i")
        assert cg_i.getAtLeast() == 0
        assert cg_i.getAutoBinMax() == 0
        assert cg_i.getPerInstance() is False
        cp = _find(dst, "top.cg.cg_i.cp")
        assert cp.getAtLeast() == 0
        assert cp.getAutoBinMax() == 0

    def test_counts_still_merged(self):
        cp = _find(_merge(_build_db(), _build_db()), "top.cg.cp")
        bins = list(cp.coverItems(CoverTypeT.CVGBIN))
        assert [b.getCoverData().data for b in bins] == [10]

    def test_first_source_wins_with_warning(self, caplog):
        with caplog.at_level(logging.WARNING, logger="ucis.merge.db_merger"):
            dst = _merge(_build_db(auto_bin_max=0),
                         _build_db(auto_bin_max=16))
        assert _find(dst, "top.cg.cp").getAutoBinMax() == 0
        assert any("AutoBinMax" in r.getMessage() for r in caplog.records)

    def test_agreeing_sources_do_not_warn(self, caplog):
        with caplog.at_level(logging.WARNING, logger="ucis.merge.db_merger"):
            _merge(_build_db(), _build_db())
        assert caplog.records == []

    def test_merge_then_xml_roundtrip(self, tmp_path):
        # The end-to-end symptom from #48: merged, written to XML, read
        # back by another tool, and auto_bin_max must still be 0.
        path = str(tmp_path / "merged.xml")
        XmlFactory.write(_merge(_build_db()), path)
        cp = _find(XmlFactory.read(path), "top.cg.cp")
        assert cp.getAutoBinMax() == 0
        assert cp.getAtLeast() == 0
