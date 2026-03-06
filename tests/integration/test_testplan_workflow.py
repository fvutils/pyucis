"""Integration tests for Phase 2: testplan embedding, closure, and waivers."""
from __future__ import annotations

import json
import os
import shutil
import tempfile

import pytest

from ucis.mem.mem_ucis import MemUCIS
from ucis.ncdb.constants import HIST_STATUS_FAIL, HIST_STATUS_OK
from ucis.ncdb.ncdb_merger import NcdbMerger
from ucis.ncdb.ncdb_reader import NcdbReader
from ucis.ncdb.ncdb_ucis import NcdbUCIS
from ucis.ncdb.ncdb_writer import NcdbWriter
from ucis.ncdb.testplan import CovergroupEntry, Testplan, Testpoint, get_testplan
from ucis.ncdb.testplan_closure import TPStatus, compute_closure, stage_gate_status
from ucis.ncdb.testplan_hjson import import_hjson
from ucis.ncdb.waivers import Waiver, WaiverSet


# ── helpers ───────────────────────────────────────────────────────────────────

@pytest.fixture()
def tmpdir_path():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


def _make_plan():
    plan = Testplan(source_file="uart.hjson")
    plan.add_testpoint(Testpoint(name="uart_reset", stage="V1",
                                  tests=["uart_smoke", "uart_init_*"]))
    plan.add_testpoint(Testpoint(name="uart_loopback", stage="V2",
                                  tests=["uart_loopback"]))
    plan.add_testpoint(Testpoint(name="uart_na", stage="V2", na=True))
    plan.covergroups.append(CovergroupEntry(name="cg_reset"))
    return plan


def _make_cdb(path, test_runs=None):
    NcdbWriter().write(MemUCIS(), path)
    db = NcdbUCIS(path)
    for name, seed, status, ts in (test_runs or []):
        db.add_test_run(name, seed=seed, status=status, ts=ts,
                        has_coverage=(status == HIST_STATUS_OK))
    tmp = path + ".tmp"
    NcdbWriter().write(db, tmp)
    os.replace(tmp, path)
    return path


# ── TestTestplanRoundTrip ─────────────────────────────────────────────────────

class TestTestplanRoundTrip:
    def test_set_and_get_testplan(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "a.cdb")
        NcdbWriter().write(MemUCIS(), path)
        db = NcdbUCIS(path)
        plan = _make_plan()
        db.setTestplan(plan)
        tp = db.getTestplan()
        assert tp is not None
        assert tp.source_file == "uart.hjson"
        assert len(tp.testpoints) == 3

    def test_testplan_survives_write_read(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "a.cdb")
        NcdbWriter().write(MemUCIS(), path)
        db = NcdbUCIS(path)
        db.setTestplan(_make_plan())
        tmp = path + ".tmp"
        NcdbWriter().write(db, tmp)
        os.replace(tmp, path)

        db2 = NcdbReader().read(path)
        plan2 = get_testplan(db2)
        assert plan2 is not None
        assert plan2.source_file == "uart.hjson"
        assert len(plan2.testpoints) == 3

    def test_testplan_member_in_zip(self, tmpdir_path):
        import zipfile
        path = os.path.join(tmpdir_path, "a.cdb")
        NcdbWriter().write(MemUCIS(), path)
        db = NcdbUCIS(path)
        db.setTestplan(_make_plan())
        tmp = path + ".tmp"
        NcdbWriter().write(db, tmp)
        os.replace(tmp, path)
        with zipfile.ZipFile(path, "r") as zf:
            assert "testplan.json" in zf.namelist()

    def test_no_testplan_no_member(self, tmpdir_path):
        import zipfile
        path = os.path.join(tmpdir_path, "a.cdb")
        NcdbWriter().write(MemUCIS(), path)
        with zipfile.ZipFile(path, "r") as zf:
            assert "testplan.json" not in zf.namelist()

    def test_stamp_import_time_set_on_setTestplan(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "a.cdb")
        NcdbWriter().write(MemUCIS(), path)
        db = NcdbUCIS(path)
        plan = _make_plan()
        assert plan.import_timestamp == ""
        db.setTestplan(plan)
        assert plan.import_timestamp != ""


# ── TestHjsonImport ───────────────────────────────────────────────────────────

class TestHjsonImport:
    def _write_hjson(self, d, data):
        path = os.path.join(d, "plan.json")
        with open(path, "w") as f:
            json.dump(data, f)
        return path

    def test_import_and_embed(self, tmpdir_path):
        hjson_path = self._write_hjson(tmpdir_path, {
            "testpoints": [
                {"name": "uart_reset", "stage": "V1", "tests": ["uart_smoke"]},
            ],
        })
        cdb = os.path.join(tmpdir_path, "a.cdb")
        NcdbWriter().write(MemUCIS(), cdb)
        db = NcdbUCIS(cdb)
        plan = import_hjson(hjson_path)
        db.setTestplan(plan)
        tmp = cdb + ".tmp"
        NcdbWriter().write(db, tmp)
        os.replace(tmp, cdb)

        db2 = NcdbReader().read(cdb)
        plan2 = get_testplan(db2)
        assert plan2 is not None
        assert plan2.testpoints[0].name == "uart_reset"

    def test_wildcard_expansion_preserved(self, tmpdir_path):
        hjson_path = self._write_hjson(tmpdir_path, {
            "testpoints": [
                {"name": "tp", "stage": "V1", "tests": ["{baud}_test"]},
            ],
        })
        plan = import_hjson(hjson_path, {"baud": ["9600", "115200"]})
        assert "9600_test" in plan.testpoints[0].tests
        assert "115200_test" in plan.testpoints[0].tests


# ── TestComputeClosureIntegration ─────────────────────────────────────────────

class TestComputeClosureIntegration:
    def test_closure_against_v2_history(self, tmpdir_path):
        path = _make_cdb(os.path.join(tmpdir_path, "a.cdb"), [
            ("uart_smoke", "1", HIST_STATUS_OK,   1700000000),
            ("uart_smoke", "2", HIST_STATUS_OK,   1700003600),
            ("uart_loopback", "1", HIST_STATUS_FAIL, 1700007200),
        ])
        db = NcdbUCIS(path)
        plan = _make_plan()
        results = compute_closure(plan, db)
        by_name = {r.testpoint.name: r for r in results}
        assert by_name["uart_reset"].status == TPStatus.CLOSED
        assert by_name["uart_loopback"].status == TPStatus.FAILING
        assert by_name["uart_na"].status == TPStatus.NA

    def test_stage_gate_passes_when_v1_closed(self, tmpdir_path):
        path = _make_cdb(os.path.join(tmpdir_path, "a.cdb"), [
            ("uart_smoke", "1", HIST_STATUS_OK, 1700000000),
        ])
        db = NcdbUCIS(path)
        plan = _make_plan()
        results = compute_closure(plan, db)
        gate = stage_gate_status(results, "V1", plan)
        assert gate["passed"] is True

    def test_stage_gate_blocked_by_failure(self, tmpdir_path):
        path = _make_cdb(os.path.join(tmpdir_path, "a.cdb"), [
            ("uart_smoke", "1", HIST_STATUS_FAIL, 1700000000),
        ])
        db = NcdbUCIS(path)
        plan = _make_plan()
        results = compute_closure(plan, db)
        gate = stage_gate_status(results, "V1", plan)
        assert gate["passed"] is False

    def test_not_run_testpoint(self, tmpdir_path):
        path = _make_cdb(os.path.join(tmpdir_path, "a.cdb"), [])
        db = NcdbUCIS(path)
        plan = _make_plan()
        results = compute_closure(plan, db)
        for r in results:
            if not r.testpoint.na:
                assert r.status == TPStatus.NOT_RUN


# ── TestWaiversRoundTrip ──────────────────────────────────────────────────────

class TestWaiversRoundTrip:
    def test_set_get_waivers(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "a.cdb")
        NcdbWriter().write(MemUCIS(), path)
        db = NcdbUCIS(path)
        ws = WaiverSet([Waiver(id="W1", scope_pattern="top/uart")])
        db.setWaivers(ws)
        ws2 = db.getWaivers()
        assert ws2 is not None
        assert len(ws2.waivers) == 1

    def test_waivers_survive_write_read(self, tmpdir_path):
        path = os.path.join(tmpdir_path, "a.cdb")
        NcdbWriter().write(MemUCIS(), path)
        db = NcdbUCIS(path)
        ws = WaiverSet([
            Waiver(id="W1", scope_pattern="top/uart", rationale="Known issue"),
            Waiver(id="W2", scope_pattern="top/spi"),
        ])
        db.setWaivers(ws)
        tmp = path + ".tmp"
        NcdbWriter().write(db, tmp)
        os.replace(tmp, path)

        db2 = NcdbReader().read(path)
        ws2 = getattr(db2, "_waivers", None)
        assert ws2 is not None
        assert len(ws2.waivers) == 2
        assert ws2.get("W1").rationale == "Known issue"

    def test_no_waivers_no_member(self, tmpdir_path):
        import zipfile
        path = os.path.join(tmpdir_path, "a.cdb")
        NcdbWriter().write(MemUCIS(), path)
        with zipfile.ZipFile(path, "r") as zf:
            assert "waivers.json" not in zf.namelist()


# ── TestMergeTestplan ─────────────────────────────────────────────────────────

class TestMergeTestplan:
    def test_same_testplan_propagated_to_merged(self, tmpdir_path):
        plan = _make_plan()
        for name in ("a.cdb", "b.cdb"):
            path = os.path.join(tmpdir_path, name)
            NcdbWriter().write(MemUCIS(), path)
            db = NcdbUCIS(path)
            db.setTestplan(plan)
            tmp = path + ".tmp"
            NcdbWriter().write(db, tmp)
            os.replace(tmp, path)

        merged = os.path.join(tmpdir_path, "merged.cdb")
        NcdbMerger().merge(
            [os.path.join(tmpdir_path, "a.cdb"),
             os.path.join(tmpdir_path, "b.cdb")],
            merged,
        )
        db_m = NcdbReader().read(merged)
        plan_m = get_testplan(db_m)
        assert plan_m is not None
        assert plan_m.source_file == "uart.hjson"

    def test_different_testplans_warning(self, tmpdir_path):
        for i, name in enumerate(("a.cdb", "b.cdb")):
            path = os.path.join(tmpdir_path, name)
            NcdbWriter().write(MemUCIS(), path)
            db = NcdbUCIS(path)
            plan = _make_plan()
            plan.source_file = f"plan_{i}.hjson"
            db.setTestplan(plan)
            tmp = path + ".tmp"
            NcdbWriter().write(db, tmp)
            os.replace(tmp, path)

        merged = os.path.join(tmpdir_path, "merged.cdb")
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            NcdbMerger().merge(
                [os.path.join(tmpdir_path, "a.cdb"),
                 os.path.join(tmpdir_path, "b.cdb")],
                merged,
            )
        assert any("testplan" in str(warning.message).lower() for warning in w)
        db_m = NcdbReader().read(merged)
        assert get_testplan(db_m) is None

    def test_waivers_merged_union(self, tmpdir_path):
        for i, cdb_name in enumerate(("a.cdb", "b.cdb")):
            path = os.path.join(tmpdir_path, cdb_name)
            NcdbWriter().write(MemUCIS(), path)
            db = NcdbUCIS(path)
            db.setWaivers(WaiverSet([
                Waiver(id=f"W{i}", scope_pattern=f"scope_{i}"),
            ]))
            tmp = path + ".tmp"
            NcdbWriter().write(db, tmp)
            os.replace(tmp, path)

        merged = os.path.join(tmpdir_path, "merged.cdb")
        NcdbMerger().merge(
            [os.path.join(tmpdir_path, "a.cdb"),
             os.path.join(tmpdir_path, "b.cdb")],
            merged,
        )
        db_m = NcdbReader().read(merged)
        ws = getattr(db_m, "_waivers", None)
        assert ws is not None
        ids = {w.id for w in ws.waivers}
        assert ids == {"W0", "W1"}
