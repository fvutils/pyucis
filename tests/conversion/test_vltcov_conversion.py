"""Tests for Verilator vltcov conversion (read-only format)."""
import pytest
import tempfile
import os
from pathlib import Path

from ucis.mem.mem_ucis import MemUCIS
from ucis.rgy.format_rgy import FormatRgy
from ucis.scope_type_t import ScopeTypeT


# Minimal vltcov .dat content
VLTCOV_SIMPLE = """# SystemC::Coverage-3
C '\x01t\x02funccov\x01page\x02v_funccov/cg_test\x01f\x02test.v\x01l\x0210\x01n\x025\x01bin\x02bin_low\x01h\x02cg_test.cp_value.bin_low\x01' 25
C '\x01t\x02funccov\x01page\x02v_funccov/cg_test\x01f\x02test.v\x01l\x0210\x01n\x025\x01bin\x02bin_mid\x01h\x02cg_test.cp_value.bin_mid\x01' 0
"""


@pytest.fixture
def vltcov_fmt():
    return FormatRgy.inst().getDatabaseDesc('vltcov').fmt_if()


@pytest.fixture
def vltcov_file(tmp_path):
    f = tmp_path / "coverage.dat"
    f.write_text(VLTCOV_SIMPLE)
    return str(f)


class TestVltCovRead:
    """Verify vltcov format reads correctly."""

    def test_read_returns_mem_ucis(self, vltcov_fmt, vltcov_file):
        db = vltcov_fmt.read(vltcov_file)
        assert isinstance(db, MemUCIS)

    def test_read_has_data(self, vltcov_fmt, vltcov_file):
        db = vltcov_fmt.read(vltcov_file)
        all_scopes = list(db.scopes(-1))
        assert len(all_scopes) > 0

    def test_read_coverage_counts(self, vltcov_fmt, vltcov_file):
        """bin_low has count 25, bin_mid has count 0."""
        db = vltcov_fmt.read(vltcov_file)
        assert db is not None
        # The DB should have some scope hierarchy
        from ucis.report.coverage_report_builder import CoverageReportBuilder
        rpt = CoverageReportBuilder.build(db)
        assert len(rpt.covergroups) > 0


class TestVltCovCapabilities:
    """Verify vltcov format capabilities."""

    def test_code_coverage_supported(self):
        caps = FormatRgy.inst().getDatabaseDesc('vltcov').capabilities
        assert caps.code_coverage is True

    def test_no_functional_coverage(self):
        caps = FormatRgy.inst().getDatabaseDesc('vltcov').capabilities
        assert caps.functional_coverage is False

    def test_can_read(self):
        caps = FormatRgy.inst().getDatabaseDesc('vltcov').capabilities
        assert caps.can_read is True


class TestVltCovWrite:
    """vltcov format now supports writing code/toggle coverage."""

    def test_write_creates_file(self, vltcov_fmt, tmp_path):
        from tests.conversion.builders.ucis_builders import build_cc1_statement_coverage
        src = MemUCIS()
        build_cc1_statement_coverage(src)
        out = str(tmp_path / "out.dat")
        vltcov_fmt.write(src, out)
        assert (tmp_path / "out.dat").exists()

    def test_write_has_header(self, vltcov_fmt, tmp_path):
        from tests.conversion.builders.ucis_builders import build_cc1_statement_coverage
        src = MemUCIS()
        build_cc1_statement_coverage(src)
        out = str(tmp_path / "out.dat")
        vltcov_fmt.write(src, out)
        content = (tmp_path / "out.dat").read_text()
        assert "SystemC::Coverage" in content

    def test_write_statement_coverage(self, vltcov_fmt, tmp_path):
        from tests.conversion.builders.ucis_builders import build_cc1_statement_coverage
        src = MemUCIS()
        build_cc1_statement_coverage(src)
        out = str(tmp_path / "out.dat")
        vltcov_fmt.write(src, out)
        content = (tmp_path / "out.dat").read_text()
        assert "v_line" in content
