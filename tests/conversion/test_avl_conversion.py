"""Tests for AVL JSON conversion (read-only format)."""
import pytest
from pathlib import Path

from ucis.mem.mem_ucis import MemUCIS
from ucis.rgy.format_rgy import FormatRgy

FIXTURES = Path(__file__).parent.parent / "fixtures" / "cocotb_avl"
AVL_JSON = FIXTURES / "sample_avl_coverage.json"
AVL_JSON_DF = FIXTURES / "sample_avl_coverage_df.json"
AVL_JSON_TABLE = FIXTURES / "sample_avl_coverage_table.json"


@pytest.fixture
def avl_fmt():
    return FormatRgy.inst().getDatabaseDesc('avl-json').fmt_if()


class TestAvlJsonRead:
    """Verify AVL JSON format reads correctly."""

    def test_read_returns_mem_ucis(self, avl_fmt):
        db = avl_fmt.read(str(AVL_JSON))
        assert isinstance(db, MemUCIS)

    def test_read_df_format(self, avl_fmt):
        db = avl_fmt.read(str(AVL_JSON_DF))
        assert db is not None

    def test_read_table_format(self, avl_fmt):
        db = avl_fmt.read(str(AVL_JSON_TABLE))
        assert db is not None

    def test_read_has_coverage_data(self, avl_fmt):
        db = avl_fmt.read(str(AVL_JSON))
        # Should contain some scopes
        all_scopes = list(db.scopes(-1))
        assert len(all_scopes) > 0


class TestAvlCapabilities:
    """Verify AVL format capabilities."""

    def test_functional_coverage(self):
        caps = FormatRgy.inst().getDatabaseDesc('avl-json').capabilities
        assert caps.functional_coverage is True

    def test_no_code_coverage(self):
        caps = FormatRgy.inst().getDatabaseDesc('avl-json').capabilities
        assert caps.code_coverage is False

    def test_can_read(self):
        caps = FormatRgy.inst().getDatabaseDesc('avl-json').capabilities
        assert caps.can_read is True


class TestAvlWrite:
    """AVL JSON format now supports writing."""

    def test_write_creates_file(self, avl_fmt, tmp_path):
        from tests.conversion.builders.ucis_builders import build_fc1_single_covergroup
        src = MemUCIS()
        build_fc1_single_covergroup(src)
        out = str(tmp_path / "out.json")
        avl_fmt.write(src, out)
        assert (tmp_path / "out.json").exists()

    def test_write_has_covergroups(self, avl_fmt, tmp_path):
        from tests.conversion.builders.ucis_builders import build_fc1_single_covergroup
        src = MemUCIS()
        build_fc1_single_covergroup(src)
        out = str(tmp_path / "out.json")
        avl_fmt.write(src, out)
        import json
        with open(out) as f:
            data = json.load(f)
        assert "functional_coverage" in data
        assert "covergroups" in data["functional_coverage"]
        assert len(data["functional_coverage"]["covergroups"]) > 0

    def test_roundtrip_preserves_bins(self, avl_fmt, tmp_path):
        """Write then read back; bins should be present."""
        from tests.conversion.builders.ucis_builders import build_fc1_single_covergroup
        src = MemUCIS()
        build_fc1_single_covergroup(src)
        out = str(tmp_path / "out.json")
        avl_fmt.write(src, out)
        dst = avl_fmt.read(out)
        all_scopes = list(dst.scopes(-1))
        assert len(all_scopes) > 0
