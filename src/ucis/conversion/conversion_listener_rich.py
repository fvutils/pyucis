"""
RichConversionListener — drives a rich.progress.Progress bar.

This module is intentionally separate from conversion_listener.py so that
``rich`` is NOT a hard dependency of pyucis.  Import this module only when
you know rich is available, or catch the ImportError at call time.

Usage::

    from ucis.conversion.conversion_listener_rich import RichConversionListener
    listener = RichConversionListener()
    ctx = ConversionContext(listener=listener)
"""
from typing import Optional

try:
    from rich.progress import (
        Progress,
        SpinnerColumn,
        BarColumn,
        TextColumn,
        TimeElapsedColumn,
        TaskID,
    )
    from rich.console import Console
    _RICH_AVAILABLE = True
except ImportError:
    _RICH_AVAILABLE = False

from ucis.conversion.conversion_listener import ConversionListener


class RichConversionListener(ConversionListener):
    """Conversion listener that drives a ``rich`` progress bar.

    Displays an indeterminate spinner when ``total`` is ``None``, or a
    determinate progress bar when the item count is known.  Warnings are
    printed inline using ``rich.console.Console``.

    Raises:
        ImportError: If the ``rich`` package is not installed.
    """

    def __init__(self):
        if not _RICH_AVAILABLE:
            raise ImportError(
                "The 'rich' package is required for RichConversionListener. "
                "Install it with:  pip install rich"
            )
        self._console = Console(stderr=True)
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("{task.completed}/{task.total}" ),
            TimeElapsedColumn(),
            console=self._console,
            transient=False,
        )
        self._task_id: Optional["TaskID"] = None
        self._progress.start()

    def on_phase_start(self, phase: str, total: Optional[int] = None):
        if self._task_id is not None:
            self._progress.remove_task(self._task_id)
        self._task_id = self._progress.add_task(
            phase, total=total if total is not None else float("inf")
        )

    def on_item(self, description: Optional[str] = None, advance: int = 1):
        if self._task_id is not None:
            self._progress.advance(self._task_id, advance)
            if description:
                self._progress.update(self._task_id, description=description)

    def on_phase_end(self):
        if self._task_id is not None:
            self._progress.update(self._task_id, completed=True)

    def on_warning(self, message: str):
        self._console.print(f"  [yellow]⚠[/yellow] {message}")

    def on_complete(self, warnings: int, items_converted: int):
        self._progress.stop()
        warn_str = f", {warnings} warning{'s' if warnings != 1 else ''}" if warnings else ""
        self._console.print(
            f"Done. {items_converted} items converted{warn_str}."
        )
