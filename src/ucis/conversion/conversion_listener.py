"""
Conversion progress listener interface.

Provides a pluggable observer for conversion progress events so callers can
drive any UI (rich progress bar, logging, silent) without the converter
knowing about the display layer.
"""
import logging
from typing import Optional


class ConversionListener:
    """No-op base class for conversion progress listeners.

    All methods have default no-op implementations so callers only override
    what they care about.  Thread-safety is the caller's responsibility.

    Override this class (or use the provided subclasses) and pass an instance
    to ``ConversionContext(listener=...)`` to receive progress events.
    """

    def on_phase_start(self, phase: str, total: Optional[int] = None):
        """A named conversion phase is starting.

        Args:
            phase: Human-readable phase name, e.g. "Reading covergroups".
            total: Expected number of items in this phase, or None if unknown.
        """

    def on_item(self, description: Optional[str] = None, advance: int = 1):
        """One or more items in the current phase have been processed.

        Args:
            description: Optional label for the current item (e.g. scope name).
            advance: Number of items completed since the last call (default 1).
        """

    def on_phase_end(self):
        """The current phase has completed."""

    def on_warning(self, message: str):
        """A lossless-conversion warning was emitted.

        Called in addition to (not instead of) appending to ctx.warnings.

        Args:
            message: The warning text.
        """

    def on_complete(self, warnings: int, items_converted: int):
        """The entire conversion is done.

        Args:
            warnings: Total number of warnings emitted.
            items_converted: Total number of UCIS items processed.
        """


class LoggingConversionListener(ConversionListener):
    """Conversion listener that emits Python logging calls.

    Phases and items are logged at INFO level; warnings at WARNING level.

    Args:
        logger: Logger to use.  Defaults to ``ucis.conversion``.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self._log = logger or logging.getLogger("ucis.conversion")
        self._phase: Optional[str] = None
        self._total: Optional[int] = None
        self._count: int = 0

    def on_phase_start(self, phase: str, total: Optional[int] = None):
        self._phase = phase
        self._total = total
        self._count = 0
        total_str = f"/{total}" if total is not None else ""
        self._log.info("phase=%s total=%s", phase, total_str or "unknown")

    def on_item(self, description: Optional[str] = None, advance: int = 1):
        self._count += advance
        total_str = f"/{self._total}" if self._total is not None else ""
        self._log.info("item=%s [%d%s]", description or "", self._count, total_str)

    def on_phase_end(self):
        self._log.info("phase_end=%s", self._phase)

    def on_warning(self, message: str):
        self._log.warning("%s", message)

    def on_complete(self, warnings: int, items_converted: int):
        self._log.info(
            "complete items=%d warnings=%d", items_converted, warnings
        )
