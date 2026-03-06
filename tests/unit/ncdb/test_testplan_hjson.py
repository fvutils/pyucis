"""Unit tests for src/ucis/ncdb/testplan_hjson.py."""
from __future__ import annotations

import json
import os
import pytest

from ucis.ncdb.testplan_hjson import (
    _expand_template,
    _expand_tests,
    import_hjson,
)
from ucis.ncdb.testplan import Testplan


# ── _expand_template ──────────────────────────────────────────────────────────

class TestExpandTemplate:
    def test_no_placeholders(self):
        assert _expand_template("uart_smoke", {}) == ["uart_smoke"]

    def test_scalar_substitution(self):
        assert _expand_template("test_{baud}", {"baud": "9600"}) == ["test_9600"]

    def test_list_substitution_cartesian(self):
        result = _expand_template("test_{baud}", {"baud": ["9600", "115200"]})
        assert result == ["test_9600", "test_115200"]

    def test_multiple_keys_cartesian_product(self):
        result = _expand_template("{mod}_{type}_test",
                                  {"mod": ["a", "b"], "type": ["x", "y"]})
        assert len(result) == 4
        assert "a_x_test" in result
        assert "b_y_test" in result

    def test_unknown_key_left_verbatim(self):
        result = _expand_template("test_{unknown}", {})
        assert result == ["test_{unknown}"]

    def test_mixed_known_unknown(self):
        result = _expand_template("{a}_{b}", {"a": "hello"})
        assert result == ["hello_{b}"]

    def test_duplicate_key_in_template(self):
        # {a} appears twice — should expand both consistently
        result = _expand_template("{a}_{a}", {"a": ["x", "y"]})
        assert set(result) == {"x_x", "y_y"}

    def test_no_subs_empty_dict(self):
        result = _expand_template("{x}", {})
        assert result == ["{x}"]


# ── _expand_tests ─────────────────────────────────────────────────────────────

class TestExpandTests:
    def test_flat_list_no_expansion(self):
        result = _expand_tests(["a", "b", "c"], {})
        assert result == ["a", "b", "c"]

    def test_with_expansion(self):
        result = _expand_tests(["{m}_test"], {"m": ["u", "v"]})
        assert result == ["u_test", "v_test"]

    def test_mixed_plain_and_template(self):
        result = _expand_tests(["plain", "{x}_test"], {"x": ["a", "b"]})
        assert result == ["plain", "a_test", "b_test"]


# ── import_hjson ──────────────────────────────────────────────────────────────

def _write_hjson(tmp_path, data: dict) -> str:
    path = str(tmp_path / "plan.json")
    with open(path, "w") as f:
        json.dump(data, f)
    return path


class TestImportHjson:
    def test_basic_import(self, tmp_path):
        path = _write_hjson(tmp_path, {
            "testpoints": [
                {"name": "uart_reset", "stage": "V1",
                 "tests": ["uart_smoke", "uart_init"]},
            ],
        })
        plan = import_hjson(path)
        assert isinstance(plan, Testplan)
        assert len(plan.testpoints) == 1
        tp = plan.testpoints[0]
        assert tp.name == "uart_reset"
        assert tp.stage == "V1"
        assert tp.tests == ["uart_smoke", "uart_init"]
        assert tp.na is False

    def test_na_testpoint(self, tmp_path):
        path = _write_hjson(tmp_path, {
            "testpoints": [
                {"name": "not_impl", "stage": "V2", "tests": ["N/A"]},
            ],
        })
        plan = import_hjson(path)
        tp = plan.testpoints[0]
        assert tp.na is True
        assert tp.tests == []

    def test_wildcard_expansion(self, tmp_path):
        path = _write_hjson(tmp_path, {
            "testpoints": [
                {"name": "tp", "stage": "V1",
                 "tests": ["{baud}_test"]},
            ],
        })
        plan = import_hjson(path, substitutions={"baud": ["9600", "115200"]})
        assert plan.testpoints[0].tests == ["9600_test", "115200_test"]

    def test_cartesian_expansion(self, tmp_path):
        path = _write_hjson(tmp_path, {
            "testpoints": [
                {"name": "tp", "stage": "V1",
                 "tests": ["{mod}_{intf}_test"]},
            ],
        })
        plan = import_hjson(path, substitutions={
            "mod": ["uart", "spi"],
            "intf": ["a", "b"],
        })
        assert len(plan.testpoints[0].tests) == 4

    def test_source_file_set(self, tmp_path):
        path = _write_hjson(tmp_path, {"testpoints": []})
        plan = import_hjson(path)
        assert os.path.isabs(plan.source_file)
        assert plan.source_file.endswith(".json")

    def test_covergroups_imported(self, tmp_path):
        path = _write_hjson(tmp_path, {
            "testpoints": [],
            "covergroups": [
                {"name": "cg_reset", "desc": "Reset coverage"},
            ],
        })
        plan = import_hjson(path)
        assert len(plan.covergroups) == 1
        assert plan.covergroups[0].name == "cg_reset"

    def test_optional_fields_defaults(self, tmp_path):
        path = _write_hjson(tmp_path, {
            "testpoints": [{"name": "tp", "stage": "V1", "tests": ["t"]}],
        })
        plan = import_hjson(path)
        tp = plan.testpoints[0]
        assert tp.desc == ""
        assert tp.tags == []

    def test_tags_preserved(self, tmp_path):
        path = _write_hjson(tmp_path, {
            "testpoints": [
                {"name": "tp", "stage": "V1", "tests": ["t"],
                 "tags": ["smoke", "regression"]},
            ],
        })
        plan = import_hjson(path, {})
        assert plan.testpoints[0].tags == ["smoke", "regression"]

    def test_source_template_recorded(self, tmp_path):
        path = _write_hjson(tmp_path, {
            "testpoints": [
                {"name": "tp", "stage": "V1", "tests": ["{x}_test"]},
            ],
        })
        plan = import_hjson(path, {"x": ["a", "b"]})
        # source_template captures the original template
        assert "{x}_test" in plan.testpoints[0].source_template

    def test_empty_testplan(self, tmp_path):
        path = _write_hjson(tmp_path, {})
        plan = import_hjson(path)
        assert plan.testpoints == []
        assert plan.covergroups == []
