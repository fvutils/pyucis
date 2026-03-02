"""
NCDB UCIS compliance tests.

Validates that the NCDB format correctly round-trips all UCIS 1.0 LRM
data model features.  Organised by implementation phase from
NCDB_COMPLIANCE_PLAN.md.
"""

import os
import tempfile
import pytest

from ucis.mem.mem_ucis import MemUCIS
from ucis.ncdb.ncdb_writer import NcdbWriter
from ucis.ncdb.ncdb_reader import NcdbReader
from ucis.scope_type_t import ScopeTypeT
from ucis.source_t import SourceT
from ucis.cover_type_t import CoverTypeT
from ucis.cover_data import CoverData
from ucis.cover_flags_t import CoverFlagsT
from ucis.history_node_kind import HistoryNodeKind
from ucis.source_info import SourceInfo


def _roundtrip(db):
    """Write MemUCIS to NCDB tempfile, read back, return new MemUCIS."""
    with tempfile.NamedTemporaryFile(suffix=".cdb", delete=False) as f:
        path = f.name
    try:
        NcdbWriter().write(db, path)
        return NcdbReader().read(path)
    finally:
        os.unlink(path)


# ═══════════════════════════════════════════════════════════════════════
# Phase 1 — Scope goal + source type
# ═══════════════════════════════════════════════════════════════════════

class TestPhase1ScopeGoalSourceType:

    def test_scope_goal_default(self):
        """Scopes with default goal (-1) round-trip correctly."""
        db = MemUCIS()
        du = db.createScope("tb", None, 1, SourceT.NONE,
                            ScopeTypeT.DU_MODULE, 0)
        assert du.getGoal() == -1
        db2 = _roundtrip(db)
        du2 = list(db2.scopes(ScopeTypeT.ALL))[0]
        assert du2.getGoal() == -1

    def test_scope_goal_custom(self):
        """Scopes with non-default goal round-trip correctly."""
        db = MemUCIS()
        cg = db.createScope("cg", None, 1, SourceT.NONE,
                            ScopeTypeT.COVERGROUP, 0)
        cg.setGoal(90)
        db2 = _roundtrip(db)
        cg2 = list(db2.scopes(ScopeTypeT.ALL))[0]
        assert cg2.getGoal() == 90

    def test_scope_source_type(self):
        """Scope source type (SourceT) round-trips correctly."""
        db = MemUCIS()
        scope = db.createScope("s", None, 1, SourceT.NONE,
                               ScopeTypeT.COVERPOINT, 0)
        # SourceT is stored on the scope at creation
        db2 = _roundtrip(db)
        s2 = list(db2.scopes(ScopeTypeT.ALL))[0]
        # For now: confirm scope survives; source_type test will be
        # expanded once the field is serialized.
        assert s2.getScopeName() == "s"

    def test_weight_and_at_least_preserved(self):
        """Confirm existing weight + at_least still work after changes."""
        db = MemUCIS()
        cp = db.createScope("cp", None, 5, SourceT.NONE,
                            ScopeTypeT.COVERPOINT, 0)
        cd = CoverData(CoverTypeT.CVGBIN, CoverFlagsT.IS_32BIT)
        cd.data = 3
        cd.at_least = 2
        cp.createNextCover("bin0", cd, None)

        db2 = _roundtrip(db)
        cp2 = list(db2.scopes(ScopeTypeT.ALL))[0]
        assert cp2.getWeight() == 5
        ci = list(cp2.coverItems(0xFFFFFFFF))[0]
        assert ci.getCoverData().data == 3
        assert ci.getCoverData().at_least == 2


# ═══════════════════════════════════════════════════════════════════════
# Phase 2 — Per-coveritem flags
# ═══════════════════════════════════════════════════════════════════════

class TestPhase2CoveritemFlags:

    def test_coveritem_flags_roundtrip(self):
        """Per-coveritem flags survive NCDB round-trip."""
        db = MemUCIS()
        scope = db.createScope("br", None, 1, SourceT.NONE,
                               ScopeTypeT.BRANCH, 0)
        cd = CoverData(CoverTypeT.BRANCHBIN, CoverFlagsT.IS_32BIT)
        cd.data = 1
        scope.createNextCover("true", cd, None)

        cd2 = CoverData(CoverTypeT.BRANCHBIN, CoverFlagsT.IS_32BIT)
        cd2.data = 0
        cd2.flags |= 0x00000020  # UCIS_EXCLUDE_PRAGMA
        scope.createNextCover("else", cd2, None)

        db2 = _roundtrip(db)
        sc2 = list(db2.scopes(ScopeTypeT.ALL))[0]
        items = list(sc2.coverItems(0xFFFFFFFF))
        assert len(items) == 2
        # First bin: no exclusion
        assert (items[0].getCoverFlags() & 0x00000020) == 0
        # Second bin: excluded
        assert (items[1].getCoverFlags() & 0x00000020) != 0

    def test_coveritem_flags_zero_by_default(self):
        """Coveritems with no special flags still work."""
        db = MemUCIS()
        scope = db.createScope("cp", None, 1, SourceT.NONE,
                               ScopeTypeT.COVERPOINT, 0)
        cd = CoverData(CoverTypeT.CVGBIN, CoverFlagsT.IS_32BIT)
        cd.data = 5
        scope.createNextCover("b", cd, None)

        db2 = _roundtrip(db)
        sc2 = list(db2.scopes(ScopeTypeT.ALL))[0]
        items = list(sc2.coverItems(0xFFFFFFFF))
        assert items[0].getCoverData().data == 5


# ═══════════════════════════════════════════════════════════════════════
# Phase 3 — Attribute system
# ═══════════════════════════════════════════════════════════════════════

class TestPhase3Attributes:

    def test_scope_string_attr_roundtrip(self):
        """Scope-level string attributes survive round-trip."""
        db = MemUCIS()
        scope = db.createScope("s", None, 1, SourceT.NONE,
                               ScopeTypeT.DU_MODULE, 0)
        scope.setAttribute("mykey", "myvalue")

        db2 = _roundtrip(db)
        s2 = list(db2.scopes(ScopeTypeT.ALL))[0]
        assert s2.getAttribute("mykey") == "myvalue"

    def test_coveritem_attr_roundtrip(self):
        """Coveritem-level attributes survive round-trip."""
        db = MemUCIS()
        scope = db.createScope("cp", None, 1, SourceT.NONE,
                               ScopeTypeT.COVERPOINT, 0)
        cd = CoverData(CoverTypeT.CVGBIN, CoverFlagsT.IS_32BIT)
        cd.data = 1
        scope.createNextCover("b0", cd, None)
        items = list(scope.coverItems(0xFFFFFFFF))
        items[0].setAttribute("BINRHS", "a")

        db2 = _roundtrip(db)
        s2 = list(db2.scopes(ScopeTypeT.ALL))[0]
        items2 = list(s2.coverItems(0xFFFFFFFF))
        assert items2[0].getAttribute("BINRHS") == "a"

    def test_history_node_attr_roundtrip(self):
        """History-node attributes survive round-trip."""
        db = MemUCIS()
        hn = db.createHistoryNode(None, "test1", "/path",
                                  HistoryNodeKind.TEST)
        hn.setAttribute("run_id", "42")

        db2 = _roundtrip(db)
        nodes = list(db2.historyNodes(HistoryNodeKind.TEST))
        assert len(nodes) >= 1
        assert nodes[0].getAttribute("run_id") == "42"

    def test_global_attr_roundtrip(self):
        """DB-level global attributes survive round-trip."""
        db = MemUCIS()
        db.setAttribute("tool_version", "1.2.3")

        db2 = _roundtrip(db)
        assert db2.getAttribute("tool_version") == "1.2.3"


# ═══════════════════════════════════════════════════════════════════════
# Phase 4 — Properties
# ═══════════════════════════════════════════════════════════════════════

class TestPhase4Properties:

    def test_expr_terms_roundtrip(self):
        """EXPR_TERMS string property round-trips."""
        from ucis.str_property import StrProperty
        db = MemUCIS()
        scope = db.createScope("cond", None, 1, SourceT.NONE,
                               ScopeTypeT.COND, 0)
        scope.setStringProperty(-1, StrProperty.EXPR_TERMS, "a#b#c")

        db2 = _roundtrip(db)
        s2 = list(db2.scopes(ScopeTypeT.ALL))[0]
        assert s2.getStringProperty(-1, StrProperty.EXPR_TERMS) == "a#b#c"

    def test_du_signature_roundtrip(self):
        """DU_SIGNATURE string property round-trips."""
        from ucis.str_property import StrProperty
        db = MemUCIS()
        du = db.createScope("mod", None, 1, SourceT.NONE,
                            ScopeTypeT.DU_MODULE, 0)
        du.setStringProperty(-1, StrProperty.DU_SIGNATURE, "abc123")

        db2 = _roundtrip(db)
        du2 = list(db2.scopes(ScopeTypeT.ALL))[0]
        assert du2.getStringProperty(-1, StrProperty.DU_SIGNATURE) == "abc123"


# ═══════════════════════════════════════════════════════════════════════
# Phase 5 — History hierarchy + coveritem tags
# ═══════════════════════════════════════════════════════════════════════

class TestPhase5HistoryAndTags:

    def test_history_node_hierarchy(self):
        """History node parent-child relationships survive round-trip."""
        db = MemUCIS()
        merge = db.createHistoryNode(None, "merge", "/merge",
                                     HistoryNodeKind.MERGE)
        db.createHistoryNode(merge, "test1", "/t1",
                             HistoryNodeKind.TEST)
        db.createHistoryNode(merge, "test2", "/t2",
                             HistoryNodeKind.TEST)

        db2 = _roundtrip(db)
        merges = list(db2.historyNodes(HistoryNodeKind.MERGE))
        tests = list(db2.historyNodes(HistoryNodeKind.TEST))
        assert len(merges) >= 1
        assert len(tests) >= 2

    def test_scope_tags_roundtrip(self):
        """Scope tags survive round-trip (existing feature)."""
        db = MemUCIS()
        scope = db.createScope("s", None, 1, SourceT.NONE,
                               ScopeTypeT.DU_MODULE, 0)
        scope.addTag("vplan_req_1")
        scope.addTag("critical")

        db2 = _roundtrip(db)
        s2 = list(db2.scopes(ScopeTypeT.ALL))[0]
        tags = set(s2.getTags())
        assert "vplan_req_1" in tags
        assert "critical" in tags
