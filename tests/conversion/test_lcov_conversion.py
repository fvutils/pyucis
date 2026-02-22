"""Tests for LCOV format conversion (write-only format)."""
import pytest
from pathlib import Path

from ucis.mem.mem_ucis import MemUCIS
from ucis.rgy.format_rgy import FormatRgy
from ucis.conversion.conversion_context import ConversionContext


@pytest.fixture
def lcov_fmt():
    return FormatRgy.inst().getDatabaseDesc('lcov').fmt_if()


class TestLcovRegistration:
    """LCOV must be registered in the format registry."""

    def test_lcov_is_registered(self):
        desc = FormatRgy.inst().getDatabaseDesc('lcov')
        assert desc is not None

    def test_lcov_caps_write_only(self):
        caps = FormatRgy.inst().getDatabaseDesc('lcov').capabilities
        assert caps.can_write is True
        assert caps.can_read is False

    def test_lcov_caps_not_lossless(self):
        assert FormatRgy.inst().getDatabaseDesc('lcov').capabilities.lossless is False


class TestLcovWrite:
    """Test LCOV write path."""

    def test_write_creates_file(self, lcov_fmt, tmp_path):
        from tests.conversion.builders.ucis_builders import build_fc1_single_covergroup
        src = MemUCIS()
        build_fc1_single_covergroup(src)
        out = str(tmp_path / "coverage.info")
        lcov_fmt.write(src, out)
        assert Path(out).exists()
        assert Path(out).stat().st_size > 0

    def test_write_contains_lcov_markers(self, lcov_fmt, tmp_path):
        from tests.conversion.builders.ucis_builders import build_fc1_single_covergroup
        src = MemUCIS()
        build_fc1_single_covergroup(src)
        out = str(tmp_path / "coverage.info")
        lcov_fmt.write(src, out)
        content = Path(out).read_text()
        assert "end_of_record" in content

    def test_write_all_fc_builders(self, lcov_fmt, tmp_path):
        """All functional-coverage builders produce valid LCOV output."""
        from tests.conversion.builders.ucis_builders import ALL_BUILDERS
        # Only test FC builders (code coverage not represented in LCOV functional path)
        fc_builders = [(b, v) for b, v in ALL_BUILDERS
                       if b.__name__.startswith("build_fc") or
                          b.__name__.startswith("build_sm")]
        for build_fn, _ in fc_builders:
            src = MemUCIS()
            build_fn(src)
            out = str(tmp_path / f"{build_fn.__name__}.info")
            lcov_fmt.write(src, out)  # must not raise

    def test_write_with_context(self, lcov_fmt, tmp_path):
        """ConversionContext accepts warnings from LCOV writer."""
        from tests.conversion.builders.ucis_builders import build_fc1_single_covergroup
        ctx = ConversionContext()
        src = MemUCIS()
        build_fc1_single_covergroup(src)
        out = str(tmp_path / "cov.info")
        lcov_fmt.write(src, out, ctx)
        # LCOV warns about functional coverage mapping
        assert len(ctx.warnings) >= 1

    def test_write_with_history_name(self, lcov_fmt, tmp_path):
        from tests.conversion.builders.ucis_builders import build_sm4_history_node
        src = MemUCIS()
        build_sm4_history_node(src)
        out = str(tmp_path / "hist.info")
        lcov_fmt.write(src, out)
        content = Path(out).read_text()
        # Test name from history node should appear
        assert "TN:" in content


class TestLcovReadNotSupported:
    """LCOV read is not implemented."""

    def test_read_raises(self, lcov_fmt, tmp_path):
        f = tmp_path / "dummy.info"
        f.write_text("TN:test\nend_of_record\n")
        with pytest.raises(NotImplementedError):
            lcov_fmt.read(str(f))
