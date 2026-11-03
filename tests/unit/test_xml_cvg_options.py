'''
Covergroup/coverpoint option values must survive an XML write/read round
trip unchanged. In particular, auto_bin_max=0 and at_least=0 are valid
(xsd:nonNegativeInteger) and must not be replaced by defaults (issue #48).
'''
import os
from ucis import UCIS_OTHER, UCIS_DU_MODULE, UCIS_INSTANCE, UCIS_VLOG, \
    UCIS_INST_ONCE, UCIS_SCOPE_UNDER_DU
from ucis.mem.mem_factory import MemFactory
from ucis.scope_type_t import ScopeTypeT
from ucis.source_info import SourceInfo
from ucis.xml import validate_ucis_xml
from ucis.xml.xml_factory import XmlFactory


def _build_db(cg_at_least=None, cp_auto_bin_max=None, cp_at_least=None):
    db = MemFactory.create()
    file = db.createFileHandle("dummy", os.getcwd())
    srcinfo = SourceInfo(file, 0, 0)
    du = db.createScope("top", srcinfo, 1, UCIS_OTHER, UCIS_DU_MODULE,
                        UCIS_INST_ONCE | UCIS_SCOPE_UNDER_DU)
    inst = db.createInstance("top", None, 1, UCIS_OTHER, UCIS_INSTANCE,
                             du, UCIS_INST_ONCE)
    cg = inst.createCovergroup("cg", SourceInfo(file, 3, 0), 1, UCIS_OTHER)
    if cg_at_least is not None:
        cg.setAtLeast(cg_at_least)
    cp = cg.createCoverpoint("cp", SourceInfo(file, 4, 0), 1, UCIS_VLOG)
    if cp_auto_bin_max is not None:
        cp.setAutoBinMax(cp_auto_bin_max)
    if cp_at_least is not None:
        cp.setAtLeast(cp_at_least)
    cp.createBin("a", SourceInfo(file, 4, 0), 1, 5, "a")
    return db


def _find(scope, name):
    for s in scope.scopes(ScopeTypeT.ALL):
        if s.getScopeName() == name:
            return s
        found = _find(s, name)
        if found is not None:
            return found
    return None


def _roundtrip(db, tmp_path):
    path = str(tmp_path / "cvg_options.xml")
    XmlFactory.write(db, path)
    with open(path) as fp:
        validate_ucis_xml(fp)
    return XmlFactory.read(path)


class TestXmlCvgOptions:

    def test_auto_bin_max_zero_preserved(self, tmp_path):
        rdb = _roundtrip(_build_db(cp_auto_bin_max=0), tmp_path)
        assert _find(rdb, "cp").getAutoBinMax() == 0

    def test_auto_bin_max_nondefault_preserved(self, tmp_path):
        rdb = _roundtrip(_build_db(cp_auto_bin_max=16), tmp_path)
        assert _find(rdb, "cp").getAutoBinMax() == 16

    def test_auto_bin_max_default(self, tmp_path):
        rdb = _roundtrip(_build_db(), tmp_path)
        assert _find(rdb, "cp").getAutoBinMax() == 64

    def test_auto_bin_max_negative_falls_back(self, tmp_path):
        rdb = _roundtrip(_build_db(cp_auto_bin_max=-1), tmp_path)
        assert _find(rdb, "cp").getAutoBinMax() == 64

    def test_at_least_zero_preserved(self, tmp_path):
        rdb = _roundtrip(_build_db(cg_at_least=0, cp_at_least=0), tmp_path)
        assert _find(rdb, "cp").getAtLeast() == 0

    def test_at_least_default(self, tmp_path):
        rdb = _roundtrip(_build_db(), tmp_path)
        assert _find(rdb, "cp").getAtLeast() == 1
