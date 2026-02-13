"""
Dashboard View - Main overview of coverage statistics.
"""
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.align import Align
from rich.text import Text

from ucis.tui.views.base_view import BaseView


class DashboardView(BaseView):
    """
    Dashboard view showing high-level coverage overview.
    """
    
    def render(self):
        """Render the dashboard."""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1)
        )
        
        # Header
        title = Text("Coverage Dashboard", style="bold cyan", justify="center")
        db_info = self.model.get_database_info()
        subtitle = Text(f"{db_info['path']}", style="dim", justify="center")
        header_panel = Panel(
            Align.center(title + Text("\n") + subtitle),
            border_style="cyan"
        )
        layout["header"].update(header_panel)
        
        # Body - split into left and right
        layout["body"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=1)
        )
        
        # Left side - overall coverage
        summary = self.model.get_summary()
        left_content = self._render_coverage_summary(summary)
        layout["body"]["left"].update(Panel(left_content, title="Coverage Summary", border_style="green"))
        
        # Right side - statistics
        right_content = self._render_statistics(summary, db_info)
        layout["body"]["right"].update(Panel(right_content, title="Statistics", border_style="blue"))
        
        return layout
    
    def _render_coverage_summary(self, summary):
        """Render coverage summary with progress bars."""
        coverage = summary['overall_coverage']
        
        # Color based on coverage percentage
        if coverage >= 80:
            color = "green"
        elif coverage >= 50:
            color = "yellow"
        else:
            color = "red"
        
        # Create coverage display
        text = Text()
        text.append(f"\nOverall Coverage: ", style="bold")
        text.append(f"{coverage:.1f}%\n\n", style=f"bold {color}")
        
        # Progress bar
        bar_width = 40
        filled = int((coverage / 100) * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        text.append(f"{bar}\n\n", style=color)
        
        # Item counts
        text.append(f"Covered: {summary['covered_bins']} / {summary['total_bins']} bins\n", style="dim")
        
        return text
    
    def _render_statistics(self, summary, db_info):
        """Render statistics table."""
        table = Table.grid(padding=(0, 2))
        table.add_column(style="cyan", justify="right")
        table.add_column(style="white")
        
        table.add_row("Covergroups:", str(summary['covergroups']))
        table.add_row("Total Bins:", str(summary['total_bins']))
        table.add_row("Covered Bins:", str(summary['covered_bins']))
        table.add_row("Uncovered Bins:", str(summary['total_bins'] - summary['covered_bins']))
        table.add_row("Tests:", str(db_info['test_count']))
        
        return Align.left(table)
    
    def handle_key(self, key: str) -> bool:
        """Handle dashboard-specific keys."""
        # Dashboard has no specific key handling yet
        return False
