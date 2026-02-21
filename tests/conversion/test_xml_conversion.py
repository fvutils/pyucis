"""Tests for UCIS XML conversion (read and write)."""
import os
import pytest
import tempfile

from ucis.mem.mem_ucis import MemUCIS
from ucis.rgy.format_rgy import FormatRgy
from ucis.conversion.conversion_context import ConversionContext
from ucis.conversion.conversion_listener import ConversionListener
from ucis.xml import validate_ucis_xml
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


@pytest.fixture
def schema_validate():
    """Fixture that returns a function to validate XML against the UCIS schema."""
    def _validate(filepath):
        result = validate_ucis_xml(filepath)
        assert result is True, f"XML failed schema validation: {filepath}"
    return _validate


class TestXmlWrite:
    """Write UCIS features to XML and verify the file is non-empty valid XML."""

    @pytest.mark.parametrize("build_fn,verify_fn", ALL_BUILDERS,
                             ids=[b.__name__.replace("build_", "") for b, _ in ALL_BUILDERS])
    def test_write_roundtrip(self, xml_fmt, tmp_xml, schema_validate, build_fn, verify_fn):
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

        # Schema validation
        schema_validate(tmp_xml)

        # Read back
        dst = xml_fmt.read(tmp_xml)
        assert dst is not None

        # Verify
        verify_fn(dst)

    def test_write_creates_valid_xml(self, xml_fmt, tmp_xml, schema_validate, tmp_path):
        """Written file starts with UCIS XML structure and passes schema."""
        from tests.conversion.builders.ucis_builders import build_fc1_single_covergroup
        src = MemUCIS()
        build_fc1_single_covergroup(src)
        xml_fmt.write(src, tmp_xml)
        content = open(tmp_xml).read()
        assert "UCIS" in content
        assert "covergroup" in content.lower() or "coverGroup" in content
        schema_validate(tmp_xml)

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

    def test_all_builders_schema_valid(self, xml_fmt, tmp_xml, schema_validate):
        """Every builder must produce schema-valid XML."""
        from tests.conversion.builders.ucis_builders import ALL_BUILDERS
        src = MemUCIS()
        for build_fn, _ in ALL_BUILDERS:
            build_fn(src)
        xml_fmt.write(src, tmp_xml)
        schema_validate(tmp_xml)

    def test_source_file_ids_consistent(self, xml_fmt, tmp_xml):
        """Every <id file="X"> value must match a <sourceFiles id="X"> entry."""
        from lxml import etree
        from tests.conversion.builders.ucis_builders import build_cc1_statement_coverage
        src = MemUCIS()
        build_cc1_statement_coverage(src)
        xml_fmt.write(src, tmp_xml)

        tree = etree.parse(tmp_xml)
        root = tree.getroot()
        # Strip namespaces
        for elem in root.getiterator():
            if hasattr(elem.tag, 'find'):
                i = elem.tag.find('}')
                if i >= 0:
                    elem.tag = elem.tag[i+1:]

        declared_ids = {int(e.get("id")) for e in root.iter("sourceFiles")}
        referenced_ids = {int(e.get("file")) for e in root.iter("id")}

        missing = referenced_ids - declared_ids
        assert not missing, (
            f"<id file=...> references undeclared sourceFiles ids: {missing}; "
            f"declared={declared_ids}"
        )


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

    @pytest.mark.parametrize("fixture_file,verify_fn", [
        ("toggle_2state.xml",   "verify_cc5_toggle_coverage"),
        ("fsm_example.xml",     "verify_cc7_fsm_coverage"),
        ("assertion_cover.xml", "verify_as1_cover_assertion"),
        ("block_statement.xml", "verify_cc1_statement_coverage"),
        ("branch_nested.xml",   "verify_cc2_branch_coverage"),
    ])
    def test_read_golden_file(self, xml_fmt, fixture_file, verify_fn):
        """Read a hand-crafted golden XML file and verify coverage content."""
        import importlib
        builders = importlib.import_module("tests.conversion.builders.ucis_builders")
        verify_func = getattr(builders, verify_fn)
        fixture_path = os.path.join(
            os.path.dirname(__file__), "fixtures", "xml", fixture_file)
        db = xml_fmt.read(fixture_path)
        verify_func(db)


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
