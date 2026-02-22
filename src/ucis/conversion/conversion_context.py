"""
ConversionContext — carries state for a single UCIS format conversion.

Provides:
- Warning collection (+ strict mode that turns warnings into errors)
- Progress notification via a pluggable ConversionListener
"""
from __future__ import annotations

from typing import List, Optional

from ucis.conversion.conversion_error import ConversionError
from ucis.conversion.conversion_listener import ConversionListener


class _PhaseContext:
    """Context manager that brackets a conversion phase."""

    def __init__(self, ctx: "ConversionContext", name: str, total: Optional[int]):
        self._ctx = ctx
        self._name = name
        self._total = total

    def __enter__(self):
        self._ctx._listener.on_phase_start(self._name, self._total)
        return self

    def __exit__(self, *_):
        self._ctx._listener.on_phase_end()


class ConversionContext:
    """State carrier for a single UCIS format conversion.

    Args:
        strict: If True, :meth:`warn` raises :class:`ConversionError` instead
            of appending to :attr:`warnings`.
        listener: Progress listener to drive.  Defaults to a no-op
            :class:`~ucis.conversion.conversion_listener.ConversionListener`.

    Example::

        ctx = ConversionContext(strict=False,
                                listener=LoggingConversionListener())

        covergroups = list(db.scopes(ScopeTypeT.COVERGROUP))
        with ctx.phase("Writing covergroups", total=len(covergroups)):
            for cg in covergroups:
                self._write_covergroup(cg, ctx)
                ctx.item(cg.getScopeName())

        ctx.complete()
    """

    def __init__(
        self,
        strict: bool = False,
        listener: Optional[ConversionListener] = None,
    ):
        self.strict: bool = strict
        self.warnings: List[str] = []
        self._listener: ConversionListener = listener or ConversionListener()
        self._items_converted: int = 0

    # ------------------------------------------------------------------
    # Warning helpers
    # ------------------------------------------------------------------

    def warn(self, message: str):
        """Record a lossless-conversion warning.

        Appends *message* to :attr:`warnings` and notifies the listener.
        If :attr:`strict` is ``True``, raises :class:`ConversionError` instead.

        Args:
            message: Human-readable description of the unsupported feature.

        Raises:
            ConversionError: When ``strict=True``.
        """
        self.warnings.append(message)
        self._listener.on_warning(message)
        if self.strict:
            raise ConversionError(message)

    def summarize(self) -> str:
        """Return a formatted summary of all warnings emitted so far."""
        if not self.warnings:
            return "No conversion warnings."
        lines = [f"Conversion warnings ({len(self.warnings)}):"]
        for w in self.warnings:
            lines.append(f"  WARNING: {w}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Progress helpers
    # ------------------------------------------------------------------

    def phase(self, name: str, total: Optional[int] = None) -> _PhaseContext:
        """Return a context manager that brackets a named conversion phase.

        Args:
            name: Human-readable phase name (e.g. "Writing covergroups").
            total: Expected item count for this phase, or ``None`` if unknown.

        Example::

            with ctx.phase("Reading bins", total=len(bins)):
                for b in bins:
                    process(b)
                    ctx.item(b.name)
        """
        return _PhaseContext(self, name, total)

    def item(self, description: Optional[str] = None, advance: int = 1):
        """Signal that one or more items have been processed.

        Args:
            description: Optional label for the current item.
            advance: Number of items completed (default 1).
        """
        self._items_converted += advance
        self._listener.on_item(description, advance)

    def complete(self):
        """Signal that the conversion is fully done."""
        self._listener.on_complete(len(self.warnings), self._items_converted)
