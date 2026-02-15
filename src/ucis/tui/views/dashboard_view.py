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
        
        # Check if filtering is active
        test_filter = self.model.get_test_filter()
        if test_filter:
            subtitle = Text(f"{db_info['path']} | ", style="dim", justify="center")
            subtitle.append(f"Filtering by: {test_filter}", style="bold yellow")
            subtitle.append(" (Press C to clear)", style="dim italic")
        else:
            subtitle = Text(f"{db_info['path']}", style="dim", justify="center")
        
        header_panel = Panel(
            Align.center(title + Text("\n") + subtitle),
            border_style="cyan"
        )
        layout["header"].update(header_panel)
        
        # Body - split into sections
        layout["body"].split_column(
            Layout(name="coverage_by_type", ratio=2),
            Layout(name="bottom", ratio=1)
        )
        
        # Top - coverage by type table
        coverage_table = self._render_coverage_by_type()
        layout["body"]["coverage_by_type"].update(Panel(coverage_table, title="Coverage by Type", border_style="cyan"))
        
        # Bottom - split into left and right for legacy and stats
        layout["body"]["bottom"].split_row(
            Layout(name="functional", ratio=1),
            Layout(name="stats", ratio=1)
        )
        
        # Left bottom - functional coverage summary (legacy bins)
        summary = self.model.get_summary()
        functional_content = self._render_functional_summary(summary)
        layout["body"]["bottom"]["functional"].update(Panel(functional_content, title="Functional Coverage", border_style="green"))
        
        # Right bottom - statistics
        stats_content = self._render_statistics(summary, db_info)
        layout["body"]["bottom"]["stats"].update(Panel(stats_content, title="Database Info", border_style="blue"))
        
        return layout
    
    def _render_coverage_by_type(self):
        """Render coverage table by type."""
        from ucis.cover_type_t import CoverTypeT
        
        table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 1))
        table.add_column("Coverage Type", style="cyan", width=20)
        table.add_column("Total", justify="right", width=10)
        table.add_column("Covered", justify="right", width=10)
        table.add_column("Coverage %", justify="right", width=12)
        table.add_column("Progress", width=30)
        
        # Get available types
        types = self.model.get_coverage_types()
        
        # Type name mapping
        type_names = {
            CoverTypeT.CVGBIN: ("Functional (Bins)", "💎"),
            CoverTypeT.STMTBIN: ("Line/Statement", "📝"),
            CoverTypeT.BRANCHBIN: ("Branch", "🔀"),
            CoverTypeT.TOGGLEBIN: ("Toggle", "⚡"),
            CoverTypeT.EXPRBIN: ("Expression", "🧮"),
            CoverTypeT.CONDBIN: ("Condition", "❓"),
            CoverTypeT.FSMBIN: ("FSM", "🔄"),
            CoverTypeT.BLOCKBIN: ("Block", "🧱"),
        }
        
        if not types:
            return Text("No coverage data found", style="dim italic")
        
        total_items = 0
        total_covered = 0
        
        for cov_type in types:
            info = self.model.get_coverage_by_type(cov_type)
            type_name, icon = type_names.get(cov_type, (f"Type {int(cov_type)}", "❔"))
            
            total_items += info['total']
            total_covered += info['covered']
            
            # Color based on coverage
            coverage = info['coverage']
            if coverage >= 90:
                color = "green"
            elif coverage >= 70:
                color = "yellow"
            else:
                color = "red"
            
            # Progress bar
            bar_width = 20
            filled = int((coverage / 100) * bar_width)
            bar = "█" * filled + "░" * (bar_width - filled)
            
            table.add_row(
                f"{icon} {type_name}",
                str(info['total']),
                str(info['covered']),
                Text(f"{coverage:.1f}%", style=f"bold {color}"),
                Text(bar, style=color)
            )
        
        # Add summary row if multiple types
        if len(types) > 1:
            overall_coverage = (total_covered / total_items * 100) if total_items > 0 else 0
            if overall_coverage >= 90:
                color = "green"
            elif overall_coverage >= 70:
                color = "yellow"
            else:
                color = "red"
            
            bar_width = 20
            filled = int((overall_coverage / 100) * bar_width)
            bar = "█" * filled + "░" * (bar_width - filled)
            
            table.add_row(
                "",
                "",
                "",
                "",
                "",
                style="dim"
            )
            table.add_row(
                "Overall Total",
                str(total_items),
                str(total_covered),
                Text(f"{overall_coverage:.1f}%", style=f"bold {color}"),
                Text(bar, style=color),
                style="bold"
            )
        
        return table
    
    def _render_functional_summary(self, summary):
        """Render functional coverage summary (legacy bins view)."""
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
        text.append(f"\nBin Coverage: ", style="bold")
        text.append(f"{coverage:.1f}%\n", style=f"bold {color}")
        
        # Progress bar
        bar_width = 30
        filled = int((coverage / 100) * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        text.append(f"{bar}\n\n", style=color)
        
        # Item counts
        text.append(f"Covered: {summary['covered_bins']} / {summary['total_bins']}\n", style="dim")
        text.append(f"Covergroups: {summary['covergroups']}\n", style="dim")
        
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
