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
        self._collect_gaps()
    
    def _collect_gaps(self):
        """Collect all gaps from the database."""
        from ucis.scope_type_t import ScopeTypeT
        
        self.gaps = []
        
        def visit_scope(scope, path=""):
            scope_type = scope.getScopeType()
            scope_name = scope.getScopeName()
            current_path = f"{path}/{scope_name}" if path else scope_name
            
            # Check coverpoints for gaps
            if scope_type == ScopeTypeT.COVERPOINT:
                total_bins = 0
                covered_bins = 0
                
                try:
                    for bin_idx in scope.coverItems(CoverTypeT.CVGBIN):
                        total_bins += 1
                        cover_data = bin_idx.getCoverData()
                        if cover_data and cover_data.data > 0:
                            covered_bins += 1
                except:
                    pass
                
                if total_bins > 0:
                    coverage = (covered_bins / total_bins) * 100
                    if coverage < self.threshold:
                        gap = GapItem(
                            name=scope_name,
                            scope_type="Coverpoint",
                            coverage=coverage,
                            hits=covered_bins,
                            goal=total_bins,
                            path=current_path
                        )
                        self.gaps.append(gap)
            
            # Recurse into children
            try:
                for child in scope.scopes(ScopeTypeT.ALL):
                    visit_scope(child, current_path)
            except:
                pass
        
        try:
            for scope in self.model.db.scopes(ScopeTypeT.ALL):
                visit_scope(scope)
        except:
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
