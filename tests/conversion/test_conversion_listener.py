"""Tests for ConversionListener, LoggingConversionListener, and ConversionContext progress."""
import logging
import pytest

from ucis.conversion.conversion_listener import ConversionListener, LoggingConversionListener
from ucis.conversion.conversion_context import ConversionContext
from ucis.conversion.conversion_error import ConversionError


class TestConversionListenerBase:
    """No-op base class — all methods callable without error."""

    def test_on_phase_start_noop(self):
        l = ConversionListener()
        l.on_phase_start("import", 10)  # should not raise

    def test_on_item_noop(self):
        l = ConversionListener()
        l.on_item("scope X", 1)

    def test_on_phase_end_noop(self):
        l = ConversionListener()
        l.on_phase_end()

    def test_on_warning_noop(self):
        l = ConversionListener()
        l.on_warning("lcov does not support covergroups")

    def test_on_complete_noop(self):
        l = ConversionListener()
        l.on_complete(3, 42)


class TestLoggingConversionListener:
    """LoggingConversionListener emits log records."""

    def test_warning_logged(self, caplog):
        with caplog.at_level(logging.WARNING, logger="ucis.conversion"):
            l = LoggingConversionListener()
            l.on_warning("test warning message")
        assert "test warning message" in caplog.text

    def test_complete_logged(self, caplog):
        with caplog.at_level(logging.INFO, logger="ucis.conversion"):
            l = LoggingConversionListener()
            l.on_complete(0, 5)
        assert caplog.text  # some message emitted

    def test_phase_start_logged(self, caplog):
        with caplog.at_level(logging.DEBUG, logger="ucis.conversion"):
            l = LoggingConversionListener()
            l.on_phase_start("export", 3)
        assert caplog.text


class TestConversionContextBasic:
    """ConversionContext carries settings and delegates to listener."""

    def test_default_not_strict(self):
        ctx = ConversionContext()
        assert ctx.strict is False

    def test_strict_mode(self):
        ctx = ConversionContext(strict=True)
        assert ctx.strict is True

    def test_warn_accumulates(self):
        ctx = ConversionContext()
        ctx.warn("msg1")
        ctx.warn("msg2")
        assert len(ctx.warnings) == 2
        assert "msg1" in ctx.warnings

    def test_warn_strict_raises(self):
        ctx = ConversionContext(strict=True)
        with pytest.raises(ConversionError):
            ctx.warn("unsupported feature")

    def test_warn_calls_listener(self):
        received = []
        l = ConversionListener()
        l.on_warning = lambda msg: received.append(msg)
        ctx = ConversionContext(listener=l)
        ctx.warn("hello")
        assert received == ["hello"]

    def test_default_listener_is_noop(self):
        ctx = ConversionContext()
        ctx.warn("irrelevant")  # must not raise


class TestConversionContextPhase:
    """ConversionContext.phase() context manager drives listener calls."""

    def test_phase_context_calls_start_end(self):
        events = []
        l = ConversionListener()
        l.on_phase_start = lambda name, total: events.append(("start", name, total))
        l.on_phase_end = lambda: events.append(("end",))
        ctx = ConversionContext(listener=l)
        with ctx.phase("import", total=5):
            pass
        assert events == [("start", "import", 5), ("end",)]

    def test_phase_item_calls_listener(self):
        items = []
        l = ConversionListener()
        l.on_item = lambda desc, adv: items.append((desc, adv))
        ctx = ConversionContext(listener=l)
        with ctx.phase("export", total=1):
            ctx.item("scope foo")
        assert items == [("scope foo", 1)]

    def test_phase_end_called_on_exception(self):
        events = []
        l = ConversionListener()
        l.on_phase_end = lambda: events.append("end")
        ctx = ConversionContext(listener=l)
        try:
            with ctx.phase("bad_phase"):
                raise RuntimeError("boom")
        except RuntimeError:
            pass
        assert "end" in events


class TestConversionContextComplete:
    """ConversionContext.complete() fires on_complete."""

    def test_complete_fires_listener(self):
        completed = []
        l = ConversionListener()
        l.on_complete = lambda w, n: completed.append((w, n))
        ctx = ConversionContext(listener=l)
        ctx.warn("w1")
        ctx.complete()
        assert completed == [(1, 0)]  # 1 warning, 0 items converted
