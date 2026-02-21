"""Tests for UCIS XML conversion (read and write)."""
import os
import pytest
import tempfile

from ucis.mem.mem_ucis import MemUCIS
from ucis.rgy.format_rgy import FormatRgy
from ucis.conversion.conversion_context import ConversionContext
from ucis.conversion.conversion_listener import ConversionListener
from tests.conversion.builders.ucis_builders import ALL_BUILDERS

# Builders whose features are NOT yet round-trippable through XML (writer gap)
_XML_WRITER_UNIMPLEMENTED = {
}

@pytest.fixture
def xml_fmt():
    return FormatRgy.inst().getDatabaseDesc('xml').fmt_if()


@pytest.fixture
def tmp_xml(tmp_path):
    return str(tmp_path / "test.xml")


class TestXmlWrite:
    """Write UCIS features to XML and verify the file is non-empty valid XML."""

    @pytest.mark.parametrize("build_fn,verify_fn", ALL_BUILDERS,
                             ids=[b.__name__.replace("build_", "") for b, _ in ALL_BUILDERS])
    def test_write_roundtrip(self, xml_fmt, tmp_xml, build_fn, verify_fn):
        """Build a feature DB, write to XML, read back, verify."""
        test_id = build_fn.__name__.replace("build_", "")
        if test_id in _XML_WRITER_UNIMPLEMENTED:
            pytest.xfail("XML writer does not yet support code/toggle coverage output")

        # Build source
        src = MemUCIS()
        build_fn(src)

        # Write
        xml_fmt.write(src, tmp_xml)
        assert os.path.exists(tmp_xml)
        assert os.path.getsize(tmp_xml) > 0

        # Read back
        dst = xml_fmt.read(tmp_xml)
        assert dst is not None

        # Verify
        verify_fn(dst)

    def test_write_creates_valid_xml(self, xml_fmt, tmp_xml, tmp_path):
        """Written file starts with UCIS XML structure."""
        from tests.conversion.builders.ucis_builders import build_fc1_single_covergroup
        src = MemUCIS()
        build_fc1_single_covergroup(src)
        xml_fmt.write(src, tmp_xml)
        content = open(tmp_xml).read()
        assert "UCIS" in content
        assert "covergroup" in content.lower() or "coverGroup" in content

    def test_write_with_context(self, xml_fmt, tmp_xml):
        """ConversionContext wires through without error."""
        from tests.conversion.builders.ucis_builders import build_fc1_single_covergroup
        ctx = ConversionContext()
        src = MemUCIS()
        build_fc1_single_covergroup(src)
        xml_fmt.write(src, tmp_xml, ctx)
        assert os.path.exists(tmp_xml)
        # XML is lossless — no warnings expected
        assert len(ctx.warnings) == 0


class TestXmlRead:
    """Read existing XML files and check the produced MemUCIS."""

    def test_read_returns_mem_ucis(self, xml_fmt, tmp_xml):
        """read() returns a MemUCIS (not XmlUCIS) after decoupling."""
        from tests.conversion.builders.ucis_builders import build_fc1_single_covergroup
        src = MemUCIS()
        build_fc1_single_covergroup(src)
        xml_fmt.write(src, tmp_xml)

        db = xml_fmt.read(tmp_xml)
        # After P2 decoupling, should be a plain MemUCIS (or subclass that IS a MemUCIS)
        assert isinstance(db, MemUCIS)

    def test_create_returns_mem_ucis(self, xml_fmt):
        """create() returns MemUCIS after P2 decoupling."""
        db = xml_fmt.create()
        assert isinstance(db, MemUCIS)


class TestXmlCapabilities:
    """XML format capabilities are lossless."""

    def test_xml_is_lossless(self):
        caps = FormatRgy.inst().getDatabaseDesc('xml').capabilities
        assert caps.lossless is True

    def test_xml_supports_all_features(self):
        caps = FormatRgy.inst().getDatabaseDesc('xml').capabilities
        assert caps.functional_coverage is True
        assert caps.code_coverage is True
        assert caps.toggle_coverage is True
        assert caps.fsm_coverage is True
        assert caps.history_nodes is True
