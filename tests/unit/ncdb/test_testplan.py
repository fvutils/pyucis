"""Unit tests for src/ucis/ncdb/testplan.py."""
from __future__ import annotations

import json

import pytest

from ucis.ncdb.testplan import (
    CovergroupEntry,
    RequirementLink,
    Testplan,
    Testpoint,
    get_testplan,
    set_testplan,
)


# ── construction helpers ──────────────────────────────────────────────────────

def _make_plan() -> Testplan:
    tp = Testplan(source_file="uart.hjson")
    tp.add_testpoint(Testpoint(name="uart_reset",   stage="V1",
                               tests=["uart_smoke", "uart_init_*"]))
    tp.add_testpoint(Testpoint(name="uart_loopback", stage="V2",
                               tests=["uart_loopback_42", "uart_loopback_99"]))
    tp.add_testpoint(Testpoint(name="uart_na",       stage="V2",
                               na=True, tests=[]))
    tp.covergroups.append(CovergroupEntry(name="cg_uart_reset",
                                          desc="Reset coverage"))
    return tp


# ── basic construction ────────────────────────────────────────────────────────

class TestTestplanConstruction:
    def test_empty_plan(self):
        plan = Testplan()
        assert plan.format_version == 1
        assert plan.testpoints == []
        assert plan.covergroups == []

    def test_add_testpoint_invalidates_index(self):
        plan = Testplan()
        plan._indexed = True          # simulate already indexed
        plan.add_testpoint(Testpoint(name="t1", stage="V1"))
        assert plan._indexed is False

    def test_stages_ordered(self):
        plan = _make_plan()
        assert plan.stages() == ["V1", "V2"]

    def test_stages_custom_sorted_last(self):
        plan = Testplan()
        plan.add_testpoint(Testpoint(name="a", stage="V3"))
        plan.add_testpoint(Testpoint(name="b", stage="V1"))
        plan.add_testpoint(Testpoint(name="c", stage="CUSTOM"))
        assert plan.stages() == ["V1", "V3", "CUSTOM"]

    def test_testpoints_for_stage(self):
        plan = _make_plan()
        v1 = plan.testpointsForStage("V1")
        assert len(v1) == 1
        assert v1[0].name == "uart_reset"


# ── lookup ────────────────────────────────────────────────────────────────────

class TestTestpointLookup:
    def test_get_testpoint_by_name(self):
        plan = _make_plan()
        tp = plan.getTestpoint("uart_reset")
        assert tp is not None
        assert tp.name == "uart_reset"

    def test_get_testpoint_unknown(self):
        plan = _make_plan()
        assert plan.getTestpoint("nonexistent") is None

    def test_testpoint_for_test_exact(self):
        plan = _make_plan()
        tp = plan.testpointForTest("uart_smoke")
        assert tp is not None
        assert tp.name == "uart_reset"

    def test_testpoint_for_test_seed_strip(self):
        plan = _make_plan()
        # "uart_smoke_12345" → strip → "uart_smoke" → exact
        tp = plan.testpointForTest("uart_smoke_12345")
        assert tp is not None
        assert tp.name == "uart_reset"

    def test_testpoint_for_test_wildcard(self):
        plan = _make_plan()
        # "uart_init_*" matches "uart_init_fast"
        tp = plan.testpointForTest("uart_init_fast")
        assert tp is not None
        assert tp.name == "uart_reset"

    def test_testpoint_for_test_no_match(self):
        plan = _make_plan()
        assert plan.testpointForTest("spi_whatever") is None

    def test_testpoint_for_test_na_testpoint(self):
        plan = _make_plan()
        # na testpoint has no tests so nothing maps to it
        tp = plan.getTestpoint("uart_na")
        assert tp is not None
        assert tp.na is True
        assert plan.testpointForTest("uart_na") is None

    def test_wildcard_does_not_match_seed_strip_candidate(self):
        # Seed-strip (strategy 2) has higher priority than wildcard (strategy 3)
        plan = Testplan()
        plan.add_testpoint(Testpoint(name="exact", stage="V1",
                                     tests=["foo_bar"]))         # exact of stripped
        plan.add_testpoint(Testpoint(name="wild",  stage="V1",
                                     tests=["foo_*"]))           # wildcard
        tp = plan.testpointForTest("foo_bar_42")  # strip→foo_bar wins
        assert tp.name == "exact"


# ── serialization round-trip ──────────────────────────────────────────────────

class TestTestplanSerialization:
    def test_to_dict_keys(self):
        plan = _make_plan()
        d = plan.to_dict()
        assert "format_version" in d
        assert "testpoints" in d
        assert "covergroups" in d

    def test_serialize_is_compact_json(self):
        plan = _make_plan()
        data = plan.serialize()
        assert isinstance(data, bytes)
        # compact separators: no space after ',' or ':'
        text = data.decode()
        assert ", " not in text
        assert ": " not in text

    def test_roundtrip_all_fields(self):
        plan = Testplan(format_version=1, source_file="x.hjson",
                        import_timestamp="2024-01-01T00:00:00+00:00")
        plan.add_testpoint(Testpoint(
            name="tp1", stage="V2", desc="desc",
            tests=["t1", "t_*"], tags=["tag1"],
            na=False, source_template="t_{x}",
            requirements=[RequirementLink(system="ALM", project="P",
                                          item_id="REQ-1", url="http://x")],
        ))
        plan.covergroups.append(CovergroupEntry(name="cg1", desc="cg desc"))
        data = plan.serialize()
        plan2 = Testplan.from_bytes(data)
        assert plan2.format_version == 1
        assert plan2.source_file == "x.hjson"
        assert plan2.import_timestamp == "2024-01-01T00:00:00+00:00"
        assert len(plan2.testpoints) == 1
        tp2 = plan2.testpoints[0]
        assert tp2.name == "tp1"
        assert tp2.stage == "V2"
        assert tp2.tests == ["t1", "t_*"]
        assert tp2.tags == ["tag1"]
        assert tp2.source_template == "t_{x}"
        assert len(tp2.requirements) == 1
        req = tp2.requirements[0]
        assert req.system == "ALM"
        assert req.item_id == "REQ-1"
        assert len(plan2.covergroups) == 1

    def test_from_dict_missing_optional_fields(self):
        d = {"testpoints": [{"name": "tp", "stage": "V1"}]}
        plan = Testplan.from_dict(d)
        assert plan.format_version == 1
        assert plan.source_file == ""
        tp = plan.testpoints[0]
        assert tp.desc == ""
        assert tp.tests == []
        assert tp.na is False

    def test_from_bytes_roundtrip(self):
        plan = _make_plan()
        plan2 = Testplan.from_bytes(plan.serialize())
        assert len(plan2.testpoints) == len(plan.testpoints)
        assert plan2.covergroups[0].name == "cg_uart_reset"

    def test_save_and_load(self, tmp_path):
        plan = _make_plan()
        path = str(tmp_path / "plan.json")
        plan.save(path)
        plan2 = Testplan.load(path)
        assert plan2.source_file == "uart.hjson"
        assert len(plan2.testpoints) == 3


# ── stamp_import_time ─────────────────────────────────────────────────────────

class TestStampImportTime:
    def test_sets_non_empty_timestamp(self):
        plan = Testplan()
        assert plan.import_timestamp == ""
        plan.stamp_import_time()
        assert plan.import_timestamp != ""
        assert "T" in plan.import_timestamp  # ISO-8601 format


# ── module-level helpers ──────────────────────────────────────────────────────

class TestModuleHelpers:
    def test_get_testplan_from_duck_typed_db(self):
        class FakeDB:
            def getTestplan(self):
                return "my_plan"
        assert get_testplan(FakeDB()) == "my_plan"

    def test_get_testplan_returns_none_without_method(self):
        assert get_testplan(object()) is None

    def test_set_testplan_duck_typed(self):
        stored = []
        class FakeDB:
            def setTestplan(self, tp):
                stored.append(tp)
        set_testplan(FakeDB(), "plan_obj")
        assert stored == ["plan_obj"]

    def test_set_testplan_raises_without_method(self):
        with pytest.raises(TypeError):
            set_testplan(object(), "plan")
