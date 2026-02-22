"""Tests for cocotb YAML/XML conversion (read-only formats)."""
import pytest
from pathlib import Path

from ucis.mem.mem_ucis import MemUCIS
from ucis.rgy.format_rgy import FormatRgy
from ucis.scope_type_t import ScopeTypeT

FIXTURES = Path(__file__).parent.parent / "fixtures" / "cocotb_avl"
COCOTB_YAML = FIXTURES / "sample_cocotb_coverage.yml"
COCOTB_XML = FIXTURES / "sample_cocotb_coverage.xml"


@pytest.fixture
def cocotb_yaml_fmt():
    return FormatRgy.inst().getDatabaseDesc('cocotb-yaml').fmt_if()


@pytest.fixture
def cocotb_xml_fmt():
    return FormatRgy.inst().getDatabaseDesc('cocotb-xml').fmt_if()


class TestCocotbYamlRead:
    """Verify cocotb-yaml format reads correctly."""

    def test_read_returns_mem_ucis(self, cocotb_yaml_fmt):
        db = cocotb_yaml_fmt.read(str(COCOTB_YAML))
        assert isinstance(db, MemUCIS)

    def test_read_has_covergroups(self, cocotb_yaml_fmt):
        db = cocotb_yaml_fmt.read(str(COCOTB_YAML))
        cgs = list(db.scopes(ScopeTypeT.COVERGROUP))
        # cocotb YAML nests covergroups under instances; check via report
        from ucis.report.coverage_report_builder import CoverageReportBuilder
        rpt = CoverageReportBuilder.build(db)
        assert len(rpt.covergroups) > 0

    def test_read_coverage_data_present(self, cocotb_yaml_fmt):
        db = cocotb_yaml_fmt.read(str(COCOTB_YAML))
        assert db is not None
        # Verify there are some scopes
        all_scopes = list(db.scopes(-1))
        assert len(all_scopes) > 0


class TestCocotbXmlRead:
    """Verify cocotb-xml format reads correctly."""

    def test_read_returns_mem_ucis(self, cocotb_xml_fmt):
        db = cocotb_xml_fmt.read(str(COCOTB_XML))
        assert isinstance(db, MemUCIS)

    def test_read_has_data(self, cocotb_xml_fmt):
        db = cocotb_xml_fmt.read(str(COCOTB_XML))
        assert db is not None


class TestCocotbCapabilities:
    """Verify cocotb format capabilities."""

    def test_yaml_functional_only(self):
        caps = FormatRgy.inst().getDatabaseDesc('cocotb-yaml').capabilities
        assert caps.functional_coverage is True
        assert caps.code_coverage is False

    def test_xml_functional_only(self):
        caps = FormatRgy.inst().getDatabaseDesc('cocotb-xml').capabilities
        assert caps.functional_coverage is True
        assert caps.code_coverage is False

    def test_both_can_read(self):
        for fmt in ('cocotb-yaml', 'cocotb-xml'):
            caps = FormatRgy.inst().getDatabaseDesc(fmt).capabilities
            assert caps.can_read is True


class TestCocotbWrite:
    """cocotb formats now support writing."""

    def test_yaml_write_creates_file(self, cocotb_yaml_fmt, tmp_path):
        from tests.conversion.builders.ucis_builders import build_fc1_single_covergroup
        src = MemUCIS()
        build_fc1_single_covergroup(src)
        out = str(tmp_path / "out.yml")
        cocotb_yaml_fmt.write(src, out)
        assert (tmp_path / "out.yml").exists()

    def test_yaml_write_has_bins(self, cocotb_yaml_fmt, tmp_path):
        from tests.conversion.builders.ucis_builders import build_fc1_single_covergroup
        src = MemUCIS()
        build_fc1_single_covergroup(src)
        out = str(tmp_path / "out.yml")
        cocotb_yaml_fmt.write(src, out)
        import yaml
        with open(out) as f:
            data = yaml.safe_load(f)
        # Should have at least one path with bins:_hits
        has_bins = any('bins:_hits' in str(v) for v in data.values() if isinstance(v, dict))
        assert has_bins

    def test_xml_write_creates_file(self, cocotb_xml_fmt, tmp_path):
        from tests.conversion.builders.ucis_builders import build_fc1_single_covergroup
        src = MemUCIS()
        build_fc1_single_covergroup(src)
        out = str(tmp_path / "out.xml")
        cocotb_xml_fmt.write(src, out)
        assert (tmp_path / "out.xml").exists()

    @pytest.mark.xfail(reason="cocotb-xml round-trip: writer emits abs_name not matching reader expectations")
    def test_xml_roundtrip(self, cocotb_xml_fmt, tmp_path):
        from tests.conversion.builders.ucis_builders import build_fc1_single_covergroup, verify_fc1_single_covergroup
        src = MemUCIS()
        build_fc1_single_covergroup(src)
        out = str(tmp_path / "out.xml")
        cocotb_xml_fmt.write(src, out)
        dst = cocotb_xml_fmt.read(out)
        verify_fc1_single_covergroup(dst)
