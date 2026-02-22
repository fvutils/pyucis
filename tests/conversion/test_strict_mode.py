"""Tests for ConversionContext strict mode and warning behavior."""
import pytest

from ucis.mem.mem_ucis import MemUCIS
from ucis.conversion.conversion_context import ConversionContext
from ucis.conversion.conversion_error import ConversionError
from ucis.conversion.conversion_listener import ConversionListener


class TestStrictModeBasic:
    """Strict mode raises ConversionError on first warning."""

    def test_normal_mode_accumulates_warnings(self):
        ctx = ConversionContext(strict=False)
        ctx.warn("msg1")
        ctx.warn("msg2")
        ctx.warn("msg3")
        assert len(ctx.warnings) == 3

    def test_strict_mode_raises_on_first_warn(self):
        ctx = ConversionContext(strict=True)
        with pytest.raises(ConversionError) as exc_info:
            ctx.warn("unsupported feature X")
        assert "unsupported feature X" in str(exc_info.value)

    def test_strict_mode_error_contains_message(self):
        ctx = ConversionContext(strict=True)
        msg = "lcov does not support covergroup data"
        with pytest.raises(ConversionError, match="lcov"):
            ctx.warn(msg)

    def test_non_strict_no_exception(self):
        ctx = ConversionContext(strict=False)
        ctx.warn("toggle not supported in YAML")  # must not raise


class TestStrictModeWithListener:
    """Strict mode still notifies listener before raising."""

    def test_listener_called_before_raise(self):
        received = []
        l = ConversionListener()
        l.on_warning = lambda m: received.append(m)
        ctx = ConversionContext(strict=True, listener=l)
        with pytest.raises(ConversionError):
            ctx.warn("test msg")
        # Listener should have been called even in strict mode
        assert "test msg" in received


class TestConversionContextSummarize:
    """summarize() returns a human-readable string."""

    def test_summarize_no_warnings(self):
        ctx = ConversionContext()
        ctx.complete()
        s = ctx.summarize()
        assert isinstance(s, str)

    def test_summarize_with_warnings(self):
        ctx = ConversionContext()
        ctx.warn("first warning")
        ctx.warn("second warning")
        ctx.complete()
        s = ctx.summarize()
        assert "2" in s or "warning" in s.lower()


class TestConversionErrorType:
    """ConversionError is a proper exception type."""

    def test_is_exception(self):
        e = ConversionError("test")
        assert isinstance(e, Exception)

    def test_message_preserved(self):
        e = ConversionError("my message")
        assert "my message" in str(e)


class TestWarningViaLcovWriter:
    """Integration: LCOV writer uses ctx.warn() for covergroup data."""

    def test_lcov_warns_on_covergroup_data(self, tmp_path):
        from tests.conversion.builders.ucis_builders import build_fc1_single_covergroup
        from ucis.rgy.format_rgy import FormatRgy
        ctx = ConversionContext(strict=False)
        src = MemUCIS()
        build_fc1_single_covergroup(src)
        out = str(tmp_path / "cov.info")
        lcov_fmt = FormatRgy.inst().getDatabaseDesc('lcov').fmt_if()
        lcov_fmt.write(src, out, ctx)
        assert len(ctx.warnings) >= 1

    def test_lcov_strict_raises_on_covergroup(self, tmp_path):
        from tests.conversion.builders.ucis_builders import build_fc1_single_covergroup
        from ucis.rgy.format_rgy import FormatRgy
        ctx = ConversionContext(strict=True)
        src = MemUCIS()
        build_fc1_single_covergroup(src)
        out = str(tmp_path / "cov.info")
        lcov_fmt = FormatRgy.inst().getDatabaseDesc('lcov').fmt_if()
        with pytest.raises(ConversionError):
            lcov_fmt.write(src, out, ctx)
