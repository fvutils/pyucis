"""
Gaps View - Display uncovered items for test planning.
"""
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ucis.tui.views.base_view import BaseView
from ucis.cover_type_t import CoverTypeT


class GapItem:
    """Represents an uncovered or low-coverage item."""
    
    def __init__(self, name, scope_type, coverage, hits, goal, path):
        self.name = name
        self.scope_type = scope_type
        self.coverage = coverage
        self.hits = hits
        self.goal = goal
        self.path = path


class GapsView(BaseView):
    """
    Gaps view showing uncovered and low-coverage items.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.threshold = 100.0  # Show items below 100% coverage
        self.gaps = []
        self.selected_index = 0
        self.scroll_offset = 0
        self._last_filter = None
        self._collect_gaps()
    
    def on_enter(self):
        """Reload gaps if filter has changed."""
        super().on_enter()
        current_filter = self.model.get_test_filter()
        if current_filter != self._last_filter:
            self._last_filter = current_filter
            self.gaps = []
            self.selected_index = 0
            self.scroll_offset = 0
            self._collect_gaps()
    
    def _collect_gaps(self):
        """Collect all gaps from the database via the common metrics layer."""
        self.gaps = []

        try:
            cp_stats = self.model.metrics.coverpoint_stats()
            for cp in cp_stats:
                if cp.coverage_pct < self.threshold:
                    self.gaps.append(GapItem(
                        name=cp.name,
                        scope_type="Coverpoint",
                        coverage=cp.coverage_pct,
                        hits=cp.bins.covered,
                        goal=cp.bins.total,
                        path=cp.path,
                    ))
        except Exception:
            pass

        # Sort by coverage (lowest first)
        self.gaps.sort(key=lambda g: g.coverage)
    
    def render(self):
        """Render the gaps view."""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="stats", size=5),
            Layout(name="table", ratio=1)
        )
        
        # Header
        title = Text("Coverage Gaps", style="bold cyan", justify="center")
        subtitle = Text(f"Items below {self.threshold:.0f}% coverage", style="dim", justify="center")
        header_panel = Panel(
            title + Text("\n") + subtitle,
            border_style="cyan"
        )
        layout["header"].update(header_panel)
        
        # Stats
        stats_content = self._render_stats()
        layout["stats"].update(Panel(stats_content, title="Gap Statistics", border_style="yellow"))
        
        # Table
        table_content = self._render_table()
        layout["table"].update(Panel(table_content, title="Gaps List", border_style="red"))
        
        return layout
    
    def _render_stats(self):
        """Render gap statistics."""
        total_gaps = len(self.gaps)
        zero_coverage = len([g for g in self.gaps if g.coverage == 0])
        partial_coverage = len([g for g in self.gaps if 0 < g.coverage < 100])
        
        text = Text()
        text.append(f"Total Gaps: ", style="bold")
        text.append(f"{total_gaps}\n", style="yellow")
        text.append(f"Zero Coverage: ", style="bold")
        text.append(f"{zero_coverage}\n", style="red")
        text.append(f"Partial Coverage: ", style="bold")
        text.append(f"{partial_coverage}", style="yellow")
        
        return text
    
    def _render_table(self):
        """Render the gaps table."""
        if not self.gaps:
            return Text("No gaps found! 🎉", style="bold green", justify="center")
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Name", style="white", width=30)
        table.add_column("Type", style="cyan", width=12)
        table.add_column("Coverage", justify="right", width=10)
        table.add_column("Hits/Goal", justify="right", width=12)
        table.add_column("Path", style="dim", width=40)
        
        # Show a window of items around the selection
        visible_start = max(0, self.selected_index - 5)
        visible_end = min(len(self.gaps), visible_start + 15)
        
        for i in range(visible_start, visible_end):
            gap = self.gaps[i]
            
            # Highlight selected row
            name_style = "bold reverse" if i == self.selected_index else ""
            
            # Color based on coverage
            if gap.coverage == 0:
                cov_color = "red"
            elif gap.coverage < 50:
                cov_color = "yellow"
            else:
                cov_color = "green"
            
            coverage_text = Text(f"{gap.coverage:.1f}%", style=cov_color)
            
            table.add_row(
                Text(gap.name, style=name_style),
                gap.scope_type,
                coverage_text,
                f"{gap.hits}/{gap.goal}",
                gap.path
            )
        
        # Add navigation hint
        if visible_end < len(self.gaps):
            table.add_row("", "", "", "", f"... {len(self.gaps) - visible_end} more items")
        
        return table
    
    def handle_key(self, key: str) -> bool:
        """Handle gaps-specific keys."""
        if key == 'down':
            self.selected_index = min(len(self.gaps) - 1, self.selected_index + 1)
            return True
        elif key == 'up':
            self.selected_index = max(0, self.selected_index - 1)
            return True
        elif key == 'pagedown':
            self.selected_index = min(len(self.gaps) - 1, self.selected_index + 10)
            return True
        elif key == 'pageup':
            self.selected_index = max(0, self.selected_index - 10)
            return True
        elif key == 'home':
            self.selected_index = 0
            return True
        elif key == 'end':
            self.selected_index = len(self.gaps) - 1
            return True
        
        return False
