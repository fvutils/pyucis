"""
UCIS feature builder and verifier functions for conversion tests.

Each ``build_*`` function populates a UCIS database with exactly one class of
UCIS feature and returns the same db.  The paired ``verify_*`` function asserts
that the expected feature is present and correct in any given database.

ALL_BUILDERS is the canonical list used by parametrize decorators.
"""

from typing import Callable, List, Tuple

from ucis import (
    UCIS_VLOG, UCIS_OTHER, UCIS_INSTANCE, UCIS_DU_MODULE,
    UCIS_SCOPE_UNDER_DU, UCIS_INST_ONCE, UCIS_HISTORYNODE_TEST,
    UCIS_TESTSTATUS_OK, UCIS_CVGBIN, UCIS_IGNOREBIN, UCIS_ILLEGALBIN,
    UCIS_ENABLED_STMT, UCIS_ENABLED_BRANCH, UCIS_ENABLED_TOGGLE,
    UCIS_STMTBIN, UCIS_BRANCHBIN, UCIS_TOGGLEBIN,
)
from ucis.cover_data import CoverData
from ucis.cover_type_t import CoverTypeT
from ucis.history_node_kind import HistoryNodeKind
from ucis.scope_type_t import ScopeTypeT
from ucis.source_info import SourceInfo
from ucis.ucis import UCIS

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _make_du_inst(db: UCIS, du_name: str = "work.top", inst_name: str = "top"):
    """Create a minimal DU + instance hierarchy. Returns (fh, du, inst)."""
    fh = db.createFileHandle("top.sv", "/project/rtl")
    du = db.createScope(
        du_name, SourceInfo(fh, 1, 0), 1, UCIS_VLOG, UCIS_DU_MODULE,
        UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE
    )
    inst = db.createInstance(
        inst_name, SourceInfo(fh, 1, 0), 1, UCIS_VLOG, UCIS_INSTANCE,
        du, UCIS_INST_ONCE
    )
    return fh, du, inst


def _add_test_history(db: UCIS, name: str = "test_basic"):
    """Add a single test history node. Returns the node."""
    node = db.createHistoryNode(None, name, "./run.sh", UCIS_HISTORYNODE_TEST)
    node.setTestStatus(UCIS_TESTSTATUS_OK)
    node.setToolCategory("simulator")
    node.setDate("20240101120000")
    node.setSeed("42")
    return node


def _find_scope(db: UCIS, scope_type, name: str):
    """Recursively search db for a scope with given type and name."""
    def _search(scope):
        for child in scope.scopes(scope_type):
            if child.getScopeName() == name:
                return child
        for child in scope.scopes(ScopeTypeT.ALL):
            result = _search(child)
            if result:
                return result
        return None
    return _search(db)


# ---------------------------------------------------------------------------
# FC-1: Single covergroup, single coverpoint, normal bins
# ---------------------------------------------------------------------------

def build_fc1_single_covergroup(db: UCIS) -> UCIS:
    """FC-1: One covergroup with one coverpoint and three normal bins."""
    _add_test_history(db)
    fh, du, inst = _make_du_inst(db)
    cg = inst.createCovergroup("cg_fc1", SourceInfo(fh, 10, 0), 1, UCIS_VLOG)
    cp = cg.createCoverpoint("cp_state", SourceInfo(fh, 11, 0), 1, UCIS_VLOG)
    cp.createBin("idle",  SourceInfo(fh, 12, 0), 1,  5, "0", UCIS_CVGBIN)
    cp.createBin("run",   SourceInfo(fh, 13, 0), 1, 10, "1", UCIS_CVGBIN)
    cp.createBin("done",  SourceInfo(fh, 14, 0), 1,  0, "2", UCIS_CVGBIN)
    return db


def verify_fc1_single_covergroup(db: UCIS):
    insts = list(db.scopes(ScopeTypeT.INSTANCE))
    assert len(insts) >= 1, "No instance scopes found"
    inst = next(i for i in insts if i.getScopeName() == "top")
    cgs = list(inst.scopes(ScopeTypeT.COVERGROUP))
    assert len(cgs) == 1
    cg = cgs[0]
    assert cg.getScopeName() == "cg_fc1"
    cps = list(cg.scopes(ScopeTypeT.COVERPOINT))
    assert len(cps) == 1
    cp = cps[0]
    assert cp.getScopeName() == "cp_state"
    bins = list(cp.coverItems(CoverTypeT.CVGBIN))
    assert len(bins) == 3
    names = {b.getName() for b in bins}
    assert names == {"idle", "run", "done"}
    counts = {b.getName(): b.getCoverData().data for b in bins}
    assert counts["idle"] == 5
    assert counts["run"] == 10
    assert counts["done"] == 0


# ---------------------------------------------------------------------------
# FC-2: Multiple covergroups
# ---------------------------------------------------------------------------

def build_fc2_multiple_covergroups(db: UCIS) -> UCIS:
    """FC-2: Two covergroups under the same instance."""
    _add_test_history(db)
    fh, du, inst = _make_du_inst(db)

    cg1 = inst.createCovergroup("cg_addr", SourceInfo(fh, 10, 0), 1, UCIS_VLOG)
    cp1 = cg1.createCoverpoint("addr", SourceInfo(fh, 11, 0), 1, UCIS_VLOG)
    cp1.createBin("low",  SourceInfo(fh, 12, 0), 1, 3, "0:127",   UCIS_CVGBIN)
    cp1.createBin("high", SourceInfo(fh, 13, 0), 1, 7, "128:255", UCIS_CVGBIN)

    cg2 = inst.createCovergroup("cg_op", SourceInfo(fh, 20, 0), 1, UCIS_VLOG)
    cp2 = cg2.createCoverpoint("opcode", SourceInfo(fh, 21, 0), 1, UCIS_VLOG)
    cp2.createBin("read",  SourceInfo(fh, 22, 0), 1, 5, "0", UCIS_CVGBIN)
    cp2.createBin("write", SourceInfo(fh, 23, 0), 1, 8, "1", UCIS_CVGBIN)
    return db


def verify_fc2_multiple_covergroups(db: UCIS):
    insts = list(db.scopes(ScopeTypeT.INSTANCE))
    inst = next(i for i in insts if i.getScopeName() == "top")
    cgs = {cg.getScopeName(): cg for cg in inst.scopes(ScopeTypeT.COVERGROUP)}
    assert "cg_addr" in cgs
    assert "cg_op" in cgs


# ---------------------------------------------------------------------------
# FC-5: Ignore bins
# ---------------------------------------------------------------------------

def build_fc5_ignore_bins(db: UCIS) -> UCIS:
    """FC-5: Coverpoint with normal and ignore bins."""
    _add_test_history(db)
    fh, du, inst = _make_du_inst(db)
    cg = inst.createCovergroup("cg_fc5", SourceInfo(fh, 10, 0), 1, UCIS_VLOG)
    cp = cg.createCoverpoint("cp_val", SourceInfo(fh, 11, 0), 1, UCIS_VLOG)
    cp.createBin("valid",  SourceInfo(fh, 12, 0), 1, 5, "0:3",  UCIS_CVGBIN)
    cp.createBin("ignore", SourceInfo(fh, 13, 0), 1, 2, "4:7",  UCIS_IGNOREBIN)
    return db


def verify_fc5_ignore_bins(db: UCIS):
    insts = list(db.scopes(ScopeTypeT.INSTANCE))
    inst = next(i for i in insts if i.getScopeName() == "top")
    cg = next(cg for cg in inst.scopes(ScopeTypeT.COVERGROUP)
              if cg.getScopeName() == "cg_fc5")
    cp = next(iter(cg.scopes(ScopeTypeT.COVERPOINT)))
    normal = list(cp.coverItems(CoverTypeT.CVGBIN))
    ignore = list(cp.coverItems(CoverTypeT.IGNOREBIN))
    assert len(normal) == 1
    assert len(ignore) == 1
    assert normal[0].getName() == "valid"
    assert ignore[0].getName() == "ignore"


# ---------------------------------------------------------------------------
# FC-6: Illegal bins
# ---------------------------------------------------------------------------

def build_fc6_illegal_bins(db: UCIS) -> UCIS:
    """FC-6: Coverpoint with normal and illegal bins."""
    _add_test_history(db)
    fh, du, inst = _make_du_inst(db)
    cg = inst.createCovergroup("cg_fc6", SourceInfo(fh, 10, 0), 1, UCIS_VLOG)
    cp = cg.createCoverpoint("cp_mode", SourceInfo(fh, 11, 0), 1, UCIS_VLOG)
    cp.createBin("ok",      SourceInfo(fh, 12, 0), 1, 5, "0:1",  UCIS_CVGBIN)
    cp.createBin("illegal", SourceInfo(fh, 13, 0), 1, 0, "2:3",  UCIS_ILLEGALBIN)
    return db


def verify_fc6_illegal_bins(db: UCIS):
    insts = list(db.scopes(ScopeTypeT.INSTANCE))
    inst = next(i for i in insts if i.getScopeName() == "top")
    cg = next(cg for cg in inst.scopes(ScopeTypeT.COVERGROUP)
              if cg.getScopeName() == "cg_fc6")
    cp = next(iter(cg.scopes(ScopeTypeT.COVERPOINT)))
    normal  = list(cp.coverItems(CoverTypeT.CVGBIN))
    illegal = list(cp.coverItems(CoverTypeT.ILLEGALBIN))
    assert len(normal) == 1
    assert len(illegal) == 1
    assert illegal[0].getName() == "illegal"


# ---------------------------------------------------------------------------
# FC-4: Cross coverage (2-way)
# ---------------------------------------------------------------------------

def build_fc4_cross_coverage(db: UCIS) -> UCIS:
    """FC-4: Two coverpoints and a 2-way cross between them."""
    _add_test_history(db)
    fh, du, inst = _make_du_inst(db)
    cg = inst.createCovergroup("cg_fc4", SourceInfo(fh, 10, 0), 1, UCIS_VLOG)
    cp_a = cg.createCoverpoint("cp_a", SourceInfo(fh, 11, 0), 1, UCIS_VLOG)
    cp_a.createBin("a0", SourceInfo(fh, 12, 0), 1, 3, "0", UCIS_CVGBIN)
    cp_a.createBin("a1", SourceInfo(fh, 13, 0), 1, 5, "1", UCIS_CVGBIN)

    cp_b = cg.createCoverpoint("cp_b", SourceInfo(fh, 14, 0), 1, UCIS_VLOG)
    cp_b.createBin("b0", SourceInfo(fh, 15, 0), 1, 4, "0", UCIS_CVGBIN)
    cp_b.createBin("b1", SourceInfo(fh, 16, 0), 1, 2, "1", UCIS_CVGBIN)

    cross = cg.createCross("cross_ab", SourceInfo(fh, 17, 0), 1, UCIS_VLOG,
                           [cp_a, cp_b])
    cross.createBin("a0_b0", SourceInfo(fh, 18, 0), 1, 2, "a0 b0", UCIS_CVGBIN)
    cross.createBin("a1_b1", SourceInfo(fh, 19, 0), 1, 1, "a1 b1", UCIS_CVGBIN)
    return db


def verify_fc4_cross_coverage(db: UCIS):
    insts = list(db.scopes(ScopeTypeT.INSTANCE))
    inst = next(i for i in insts if i.getScopeName() == "top")
    cg = next(cg for cg in inst.scopes(ScopeTypeT.COVERGROUP)
              if cg.getScopeName() == "cg_fc4")
    cps = list(cg.scopes(ScopeTypeT.COVERPOINT))
    assert len(cps) == 2
    crosses = list(cg.scopes(ScopeTypeT.CROSS))
    assert len(crosses) == 1
    assert crosses[0].getScopeName() == "cross_ab"


# ---------------------------------------------------------------------------
# SM-1: Design hierarchy (DU + instance)
# ---------------------------------------------------------------------------

def build_sm1_design_hierarchy(db: UCIS) -> UCIS:
    """SM-1: DU_MODULE with one instance, minimal content."""
    _add_test_history(db)
    fh, du, inst = _make_du_inst(db, "work.counter", "dut")
    # Add a covergroup so the hierarchy isn't empty
    cg = inst.createCovergroup("cg_dummy", SourceInfo(fh, 5, 0), 1, UCIS_VLOG)
    cp = cg.createCoverpoint("cp_dummy", SourceInfo(fh, 6, 0), 1, UCIS_VLOG)
    cp.createBin("b0", SourceInfo(fh, 7, 0), 1, 1, "0", UCIS_CVGBIN)
    return db


def verify_sm1_design_hierarchy(db: UCIS):
    insts = list(db.scopes(ScopeTypeT.INSTANCE))
    assert len(insts) >= 1
    inst = next(i for i in insts if i.getScopeName() == "dut")
    assert inst is not None
    du = inst.getInstanceDu()
    assert du is not None
    assert du.getScopeName() == "work.counter"


# ---------------------------------------------------------------------------
# SM-4: History node (single test)
# ---------------------------------------------------------------------------

def build_sm4_history_node(db: UCIS) -> UCIS:
    """SM-4: One test history node with TestData."""
    node = _add_test_history(db, "test_smoke")
    fh, du, inst = _make_du_inst(db)
    cg = inst.createCovergroup("cg_sm4", SourceInfo(fh, 1, 0), 1, UCIS_VLOG)
    cp = cg.createCoverpoint("cp_sm4", SourceInfo(fh, 2, 0), 1, UCIS_VLOG)
    cp.createBin("b", SourceInfo(fh, 3, 0), 1, 1, "0", UCIS_CVGBIN)
    return db


def verify_sm4_history_node(db: UCIS):
    nodes = db.getHistoryNodes(HistoryNodeKind.TEST)
    assert len(nodes) >= 1
    node = next(n for n in nodes if n.getLogicalName() == "test_smoke")
    assert node.getTestStatus() == UCIS_TESTSTATUS_OK


# ---------------------------------------------------------------------------
# SM-5: Multiple history nodes
# ---------------------------------------------------------------------------

def build_sm5_multiple_history_nodes(db: UCIS) -> UCIS:
    """SM-5: Two test history nodes representing a merged database."""
    for name in ("test_a", "test_b"):
        node = db.createHistoryNode(None, name, f"./{name}.sh", UCIS_HISTORYNODE_TEST)
        node.setTestStatus(UCIS_TESTSTATUS_OK)
        node.setToolCategory("simulator")
        node.setDate("20240101120000")
    fh, du, inst = _make_du_inst(db)
    cg = inst.createCovergroup("cg_sm5", SourceInfo(fh, 1, 0), 1, UCIS_VLOG)
    cp = cg.createCoverpoint("cp_sm5", SourceInfo(fh, 2, 0), 1, UCIS_VLOG)
    cp.createBin("b", SourceInfo(fh, 3, 0), 1, 1, "0", UCIS_CVGBIN)
    return db


def verify_sm5_multiple_history_nodes(db: UCIS):
    nodes = db.getHistoryNodes(HistoryNodeKind.TEST)
    assert len(nodes) >= 2
    names = {n.getLogicalName() for n in nodes}
    assert "test_a" in names
    assert "test_b" in names


# ---------------------------------------------------------------------------
# CC-1: Statement coverage
# ---------------------------------------------------------------------------

def build_cc1_statement_coverage(db: UCIS) -> UCIS:
    """CC-1: Module instance with statement coverage bins."""
    _add_test_history(db)
    fh = db.createFileHandle("alu.sv", "/project/rtl")
    du = db.createScope(
        "work.alu", SourceInfo(fh, 1, 0), 1, UCIS_VLOG, UCIS_DU_MODULE,
        UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE | UCIS_ENABLED_STMT
    )
    inst = db.createInstance(
        "alu_inst", SourceInfo(fh, 1, 0), 1, UCIS_VLOG, UCIS_INSTANCE,
        du, UCIS_INST_ONCE
    )
    block = inst.createScope(
        "always_blk", SourceInfo(fh, 10, 0), 1, UCIS_VLOG,
        ScopeTypeT.BLOCK, UCIS_ENABLED_STMT
    )
    cd = CoverData(CoverTypeT.STMTBIN, 0)
    cd.data = 7
    block.createNextCover("stmt_10", cd, SourceInfo(fh, 10, 0))
    return db


def verify_cc1_statement_coverage(db: UCIS):
    insts = list(db.scopes(ScopeTypeT.INSTANCE))
    assert len(insts) >= 1
    inst = next(i for i in insts if i.getScopeName() == "alu_inst")
    blocks = list(inst.scopes(ScopeTypeT.BLOCK))
    assert len(blocks) >= 1
    stmts = list(blocks[0].coverItems(CoverTypeT.STMTBIN))
    assert len(stmts) >= 1
    assert stmts[0].getCoverData().data == 7


# ---------------------------------------------------------------------------
# CC-2: Branch coverage
# ---------------------------------------------------------------------------

def build_cc2_branch_coverage(db: UCIS) -> UCIS:
    """CC-2: Module instance with branch coverage bins."""
    _add_test_history(db)
    fh = db.createFileHandle("ctrl.sv", "/project/rtl")
    du = db.createScope(
        "work.ctrl", SourceInfo(fh, 1, 0), 1, UCIS_VLOG, UCIS_DU_MODULE,
        UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE | UCIS_ENABLED_BRANCH
    )
    inst = db.createInstance(
        "ctrl_inst", SourceInfo(fh, 1, 0), 1, UCIS_VLOG, UCIS_INSTANCE,
        du, UCIS_INST_ONCE
    )
    branch = inst.createScope(
        "if_20", SourceInfo(fh, 20, 0), 1, UCIS_VLOG,
        ScopeTypeT.BRANCH, UCIS_ENABLED_BRANCH
    )
    cd_t = CoverData(CoverTypeT.BRANCHBIN, 0); cd_t.data = 5
    cd_f = CoverData(CoverTypeT.BRANCHBIN, 0); cd_f.data = 3
    branch.createNextCover("true_arm",  cd_t, SourceInfo(fh, 20, 0))
    branch.createNextCover("false_arm", cd_f, SourceInfo(fh, 21, 0))
    return db


def verify_cc2_branch_coverage(db: UCIS):
    insts = list(db.scopes(ScopeTypeT.INSTANCE))
    inst = next(i for i in insts if i.getScopeName() == "ctrl_inst")
    branches = list(inst.scopes(ScopeTypeT.BRANCH))
    assert len(branches) >= 1
    arms = list(branches[0].coverItems(CoverTypeT.BRANCHBIN))
    assert len(arms) == 2
    counts = {arm.getName(): arm.getCoverData().data for arm in arms}
    assert counts["true_arm"] == 5
    assert counts["false_arm"] == 3


# ---------------------------------------------------------------------------
# CC-5: Toggle coverage
# ---------------------------------------------------------------------------

def build_cc5_toggle_coverage(db: UCIS) -> UCIS:
    """CC-5: Signal toggle coverage (0→1 and 1→0 bins)."""
    _add_test_history(db)
    fh = db.createFileHandle("sig.sv", "/project/rtl")
    du = db.createScope(
        "work.sig", SourceInfo(fh, 1, 0), 1, UCIS_VLOG, UCIS_DU_MODULE,
        UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE | UCIS_ENABLED_TOGGLE
    )
    inst = db.createInstance(
        "sig_inst", SourceInfo(fh, 1, 0), 1, UCIS_VLOG, UCIS_INSTANCE,
        du, UCIS_INST_ONCE
    )
    # Use createScope with TOGGLE type so coverItems works correctly
    toggle = inst.createScope(
        "clk", SourceInfo(fh, 5, 0), 1, UCIS_VLOG,
        ScopeTypeT.TOGGLE, UCIS_ENABLED_TOGGLE
    )
    cd_01 = CoverData(CoverTypeT.TOGGLEBIN, 0); cd_01.data = 100
    cd_10 = CoverData(CoverTypeT.TOGGLEBIN, 0); cd_10.data = 99
    toggle.createNextCover("0to1", cd_01, SourceInfo(fh, 5, 0))
    toggle.createNextCover("1to0", cd_10, SourceInfo(fh, 5, 0))
    return db


def verify_cc5_toggle_coverage(db: UCIS):
    insts = list(db.scopes(ScopeTypeT.INSTANCE))
    inst = next(i for i in insts if i.getScopeName() == "sig_inst")
    toggles = list(inst.scopes(ScopeTypeT.TOGGLE))
    assert len(toggles) >= 1
    bins = list(toggles[0].coverItems(CoverTypeT.TOGGLEBIN))
    assert len(bins) == 2
    counts = {b.getName(): b.getCoverData().data for b in bins}
    assert counts["0to1"] == 100
    assert counts["1to0"] == 99


# ---------------------------------------------------------------------------
# Master list
# ---------------------------------------------------------------------------

ALL_BUILDERS: List[Tuple[Callable, Callable]] = [
    (build_fc1_single_covergroup,   verify_fc1_single_covergroup),
    (build_fc2_multiple_covergroups, verify_fc2_multiple_covergroups),
    (build_fc4_cross_coverage,      verify_fc4_cross_coverage),
    (build_fc5_ignore_bins,         verify_fc5_ignore_bins),
    (build_fc6_illegal_bins,        verify_fc6_illegal_bins),
    (build_sm1_design_hierarchy,    verify_sm1_design_hierarchy),
    (build_sm4_history_node,        verify_sm4_history_node),
    (build_sm5_multiple_history_nodes, verify_sm5_multiple_history_nodes),
    (build_cc1_statement_coverage,  verify_cc1_statement_coverage),
    (build_cc2_branch_coverage,     verify_cc2_branch_coverage),
    (build_cc5_toggle_coverage,     verify_cc5_toggle_coverage),
]
