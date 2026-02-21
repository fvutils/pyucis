"""Tests for FormatCapabilities and format registry."""
import pytest
from ucis.rgy.format_rgy import FormatRgy
from ucis.rgy.format_if_db import FormatCapabilities, FormatDbFlags


class TestFormatCapabilities:
    """Verify FormatCapabilities is registered correctly for each format."""

    @pytest.fixture(autouse=True)
    def rgy(self):
        self.rgy = FormatRgy.inst()

    def _caps(self, name) -> FormatCapabilities:
        desc = self.rgy.getDatabaseDesc(name)
        assert desc is not None, f"Format '{name}' not registered"
        return desc.capabilities

    # --- XML ---
    def test_xml_caps_lossless(self):
        assert self._caps('xml').lossless is True

    def test_xml_caps_functional(self):
        assert self._caps('xml').functional_coverage is True

    def test_xml_caps_code(self):
        assert self._caps('xml').code_coverage is True

    def test_xml_caps_toggle(self):
        assert self._caps('xml').toggle_coverage is True

    def test_xml_caps_can_read_write(self):
        c = self._caps('xml')
        assert c.can_read is True
        assert c.can_write is True

    # --- SQLite ---
    def test_sqlite_caps_lossless(self):
        assert self._caps('sqlite').lossless is True

    def test_sqlite_caps_can_read_write(self):
        c = self._caps('sqlite')
        assert c.can_read is True
        assert c.can_write is True

    # --- YAML ---
    def test_yaml_caps_functional_only(self):
        c = self._caps('yaml')
        assert c.functional_coverage is True
        assert c.code_coverage is False

    def test_yaml_caps_no_lossless(self):
        assert self._caps('yaml').lossless is False

    # --- cocotb ---
    def test_cocotb_caps_functional(self):
        c = self._caps('cocotb-yaml')
        assert c.functional_coverage is True

    def test_cocotb_caps_can_read(self):
        assert self._caps('cocotb-yaml').can_read is True

    def test_cocotb_caps_can_write(self):
        assert self._caps('cocotb-yaml').can_write is True

    # --- avl ---
    def test_avl_caps_functional(self):
        c = self._caps('avl-json')
        assert c.functional_coverage is True

    def test_avl_caps_can_read(self):
        assert self._caps('avl-json').can_read is True

    def test_avl_caps_can_write(self):
        assert self._caps('avl-json').can_write is True

    # --- vltcov ---
    def test_vltcov_caps_code(self):
        c = self._caps('vltcov')
        assert c.code_coverage is True

    def test_vltcov_caps_no_functional(self):
        assert self._caps('vltcov').functional_coverage is False

    def test_vltcov_caps_can_write(self):
        assert self._caps('vltcov').can_write is True


class TestFormatCapabilitiesDefaults:
    """Verify FormatCapabilities dataclass defaults are all False."""

    def test_defaults_all_false(self):
        c = FormatCapabilities()
        assert c.can_read is False
        assert c.can_write is False
        assert c.functional_coverage is False
        assert c.code_coverage is False
        assert c.toggle_coverage is False
        assert c.fsm_coverage is False
        assert c.cross_coverage is False
        assert c.assertions is False
        assert c.history_nodes is False
        assert c.design_hierarchy is False
        assert c.ignore_illegal_bins is False
        assert c.lossless is False
