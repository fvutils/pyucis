"""Testplan Closure View — TUI view showing testpoint closure status.

Shows all testpoints with their stage, closure status, and pass/fail
counts.  Includes a stage gate summary header and supports scrolling,
sorting, and a detail panel for the selected testpoint.
"""

from rich.align import Align
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ucis.tui.views.base_view import BaseView


_STATUS_STYLE = {
    "CLOSED":    "green",
    "PARTIAL":   "yellow",
    "FAILING":   "red",
    "NOT_RUN":   "dim",
    "N/A":       "dim",
    "UNIMP":     "dim",
}

_STATUS_ICON = {
    "CLOSED":  "✓",
    "PARTIAL": "~",
    "FAILING": "✗",
    "NOT_RUN": "?",
    "N/A":     "—",
    "UNIMP":   "-",
}


class TestplanView(BaseView):
    """TUI view for testplan closure status (key '8')."""

    def __init__(self, app):
        super().__init__(app)
        self.results = []
        self.summary = None
        self.selected_index = 0
        self.scroll_offset = 0
        self.visible_rows = 20
        self._loaded = False

    def on_enter(self):
        super().on_enter()
        if not self._loaded:
            self._load_closure()

    def _load_closure(self):
        """Load testplan closure results from the model."""
        self.results = []
        self.summary = None
        try:
            data = self.model.get_testplan_closure()
            self.results = data.get("results", [])
            self.summary = data.get("summary", None)
        except Exception:
            pass
        self._loaded = True
        self.selected_index = 0
        self.scroll_offset = 0

    def _adjust_scroll(self):
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.visible_rows:
            self.scroll_offset = self.selected_index - self.visible_rows + 1

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render(self):
        layout = Layout()

        if not self.results:
            return Panel(
                Align.center(
                    Text(
                        "No testplan found.\n\n"
                        "Embed one with:\n"
                        "  pyucis testplan import coverage.cdb uart.hjson",
                        style="dim",
                    ),
                    vertical="middle",
                ),
                title="[bold]Testplan Closure[/bold]",
            )

        has_summary = self.summary is not None
        header_size = 7 if has_summary else 3
        layout.split_column(
            Layout(name="header", size=header_size),
            Layout(name="body", ratio=1),
            Layout(name="detail", size=8),
        )

        layout["header"].update(self._render_header())
        layout["body"].update(self._render_table())
        layout["detail"].update(self._render_detail())
        return layout

    def _render_header(self):
        lines = []
        if self.summary is not None:
            total = self.summary.get("total", 0)
            closed = self.summary.get("total_closed", 0)
            na = self.summary.get("total_na", 0)
            pct = round(100.0 * closed / (total - na), 1) if (total - na) > 0 else 0.0
            lines.append(
                f"[bold]Testplan Closure[/bold]  "
                f"{closed}/{total - na} testpoints closed ({pct:.1f}%)  "
                f"[dim]{na} N/A[/dim]"
            )
            by_stage = self.summary.get("by_stage", {})
            stage_parts = []
            for stage, entry in sorted(by_stage.items()):
                c, t = entry.get("closed", 0), entry.get("total", 0)
                p = entry.get("pct", 0.0)
                colour = "green" if p >= 100 else ("yellow" if p > 0 else "red")
                stage_parts.append(f"[{colour}]{stage}: {c}/{t}[/{colour}]")
            lines.append("  " + "  |  ".join(stage_parts))
        else:
            lines.append("[bold]Testplan Closure[/bold]")
        lines.append(
            "[dim]↑↓ navigate  r refresh  q back[/dim]"
        )
        return Panel("\n".join(lines), style="bold")

    def _render_table(self):
        table = Table(
            show_header=True,
            header_style="bold cyan",
            expand=True,
            show_lines=False,
        )
        table.add_column("", width=2, no_wrap=True)
        table.add_column("Testpoint", ratio=3, no_wrap=True)
        table.add_column("Stage", width=6, no_wrap=True)
        table.add_column("Status", width=12, no_wrap=True)
        table.add_column("Pass", width=6, justify="right", no_wrap=True)
        table.add_column("Fail", width=6, justify="right", no_wrap=True)

        visible_end = min(
            self.scroll_offset + self.visible_rows, len(self.results)
        )
        for i in range(self.scroll_offset, visible_end):
            r = self.results[i]
            is_sel = i == self.selected_index
            sel_marker = "▶" if is_sel else " "
            tp_name = r.get("testpoint", "?")
            stage = r.get("stage", "?")
            status = r.get("status", "NOT_RUN")
            pc = str(r.get("pass_count", 0))
            fc = str(r.get("fail_count", 0))

            icon = _STATUS_ICON.get(status, "?")
            style = _STATUS_STYLE.get(status, "")
            if is_sel:
                style = "reverse " + style

            table.add_row(
                sel_marker,
                tp_name,
                stage,
                f"{icon} {status}",
                pc,
                fc,
                style=style if not is_sel else None,
            )

        if len(self.results) > self.visible_rows:
            shown_end = min(self.scroll_offset + self.visible_rows, len(self.results))
            scroll_info = (
                f"[dim] {shown_end}/{len(self.results)} shown[/dim]"
            )
            return Panel(table, subtitle=scroll_info)
        return Panel(table)

    def _render_detail(self):
        if not self.results or self.selected_index >= len(self.results):
            return Panel(Text("No testpoint selected", style="dim"), title="Detail")

        r = self.results[self.selected_index]
        tp_name = r.get("testpoint", "?")
        stage   = r.get("stage", "?")
        status  = r.get("status", "NOT_RUN")
        tests   = r.get("matched_tests", [])
        desc    = r.get("desc", "")

        lines = [
            f"[bold]{tp_name}[/bold]  [{stage}]  {_STATUS_ICON.get(status, '?')} {status}",
        ]
        if desc:
            lines.append(f"[dim]{desc}[/dim]")
        if tests:
            lines.append("Tests: " + ", ".join(tests[:6])
                         + ("…" if len(tests) > 6 else ""))
        else:
            lines.append("[dim]No tests matched[/dim]")

        return Panel("\n".join(lines), title="[dim]Detail[/dim]")

    # ------------------------------------------------------------------
    # Key handling
    # ------------------------------------------------------------------

    def handle_key(self, key: str) -> bool:
        if key in ("up", "k") and self.results:
            if self.selected_index > 0:
                self.selected_index -= 1
                self._adjust_scroll()
            return True
        if key in ("down", "j") and self.results:
            if self.selected_index < len(self.results) - 1:
                self.selected_index += 1
                self._adjust_scroll()
            return True
        if key in ("home",):
            self.selected_index = 0
            self.scroll_offset = 0
            return True
        if key in ("end",):
            self.selected_index = max(0, len(self.results) - 1)
            self._adjust_scroll()
            return True
        if key in ("r", "R"):
            self._loaded = False
            self._load_closure()
            return True
        return False
