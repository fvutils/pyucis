"""
Hotspots View - Identify high-priority coverage improvement targets.
"""
from typing import List, Tuple
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ucis.tui.views.base_view import BaseView
from ucis.cover_type_t import CoverTypeT


class Hotspot:
    """Represents a high-priority coverage target."""
    
    def __init__(self, name, hotspot_type, coverage, items_remaining, priority, reason, path):
        self.name = name
        self.hotspot_type = hotspot_type  # "low_coverage", "near_complete", "high_value"
        self.coverage = coverage
        self.items_remaining = items_remaining
        self.priority = priority  # P0, P1, P2, P3
        self.reason = reason
        self.path = path


class HotspotsView(BaseView):
    """
    Hotspots view for identifying high-value improvement opportunities.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.threshold_low = 50.0  # Below this is "low coverage"
        self.threshold_near = 90.0  # Above this is "near complete"
        self.hotspots = []
        self.selected_index = 0
        self.current_category = "all"  # all, low, near, high_value
        self._analyze_hotspots()
    
    def _analyze_hotspots(self):
        """Analyze the database to identify hotspots."""
        from ucis.scope_type_t import ScopeTypeT
        
        self.hotspots = []
        
        def visit_scope(scope, path=""):
            scope_type = scope.getScopeType()
            scope_name = scope.getScopeName()
            current_path = f"{path}/{scope_name}" if path else scope_name
            
            # Analyze covergroups
            if scope_type == ScopeTypeT.COVERGROUP:
                total_bins = 0
                covered_bins = 0
                
                # Count bins across all coverpoints
                try:
                    for cp in scope.scopes(ScopeTypeT.COVERPOINT):
                        for bin_idx in cp.coverItems(CoverTypeT.CVGBIN):
                            total_bins += 1
                            cover_data = bin_idx.getCoverData()
                            if cover_data and cover_data.data > 0:
                                covered_bins += 1
                except:
                    pass
                
                if total_bins > 0:
                    coverage = (covered_bins / total_bins) * 100
                    uncovered = total_bins - covered_bins
                    
                    # Low coverage hotspot (high impact)
                    if coverage < self.threshold_low:
                        priority = "P0" if coverage < 25 else "P1"
                        hotspot = Hotspot(
                            name=scope_name,
                            hotspot_type="low_coverage",
                            coverage=coverage,
                            items_remaining=uncovered,
                            priority=priority,
                            reason=f"{uncovered} bins uncovered, low overall coverage",
                            path=current_path
                        )
                        self.hotspots.append(hotspot)
                    
                    # Near-complete hotspot (low hanging fruit)
                    elif coverage >= self.threshold_near and coverage < 100:
                        priority = "P1" if uncovered <= 3 else "P2"
                        hotspot = Hotspot(
                            name=scope_name,
                            hotspot_type="near_complete",
                            coverage=coverage,
                            items_remaining=uncovered,
                            priority=priority,
                            reason=f"Only {uncovered} bins to complete",
                            path=current_path
                        )
                        self.hotspots.append(hotspot)
            
            # Analyze coverpoints with zero coverage
            elif scope_type == ScopeTypeT.COVERPOINT:
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
                
                if total_bins > 0 and covered_bins == 0:
                    # High-value: completely untested coverpoint
                    hotspot = Hotspot(
                        name=scope_name,
                        hotspot_type="high_value",
                        coverage=0.0,
                        items_remaining=total_bins,
                        priority="P1",
                        reason="Completely untested coverpoint",
                        path=current_path
                    )
                    self.hotspots.append(hotspot)
            
            # Recurse
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
        
        # Sort by priority then coverage
        priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
        self.hotspots.sort(key=lambda h: (priority_order.get(h.priority, 4), h.coverage))
    
    def render(self):
        """Render the hotspots view."""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1)
        )
        
        # Header
        title = Text("Coverage Hotspots", style="bold cyan", justify="center")
        subtitle = Text("High-priority improvement targets", style="dim", justify="center")
        header_panel = Panel(
            title + Text("\n") + subtitle,
            border_style="cyan"
        )
        layout["header"].update(header_panel)
        
        # Body - split into categories and details
        layout["body"].split_row(
            Layout(name="categories", ratio=1),
            Layout(name="hotspots", ratio=2)
        )
        
        # Categories summary
        categories_content = self._render_categories()
        layout["body"]["categories"].update(
            Panel(categories_content, title="Categories", border_style="yellow")
        )
        
        # Hotspots table
        hotspots_content = self._render_hotspots_table()
        layout["body"]["hotspots"].update(
            Panel(hotspots_content, title="Priority Targets", border_style="red")
        )
        
        return layout
    
    def _render_categories(self):
        """Render hotspot categories summary."""
        low_cov = [h for h in self.hotspots if h.hotspot_type == "low_coverage"]
        near_complete = [h for h in self.hotspots if h.hotspot_type == "near_complete"]
        high_value = [h for h in self.hotspots if h.hotspot_type == "high_value"]
        
        p0_count = len([h for h in self.hotspots if h.priority == "P0"])
        p1_count = len([h for h in self.hotspots if h.priority == "P1"])
        p2_count = len([h for h in self.hotspots if h.priority == "P2"])
        
        table = Table.grid(padding=(0, 1))
        table.add_column(style="bold", justify="left")
        table.add_column(justify="right")
        
        table.add_row("", "")
        table.add_row(Text("By Priority:", style="bold green"), "")
        table.add_row(Text("  P0 (Critical)", style="red"), str(p0_count))
        table.add_row(Text("  P1 (High)", style="yellow"), str(p1_count))
        table.add_row(Text("  P2 (Medium)", style="cyan"), str(p2_count))
        
        table.add_row("", "")
        table.add_row(Text("By Type:", style="bold green"), "")
        table.add_row(Text("  Low Coverage", style="red"), str(len(low_cov)))
        table.add_row(Text("  Near Complete", style="green"), str(len(near_complete)))
        table.add_row(Text("  Untested", style="yellow"), str(len(high_value)))
        
        table.add_row("", "")
        table.add_row(Text("Total Hotspots:", style="bold yellow"), str(len(self.hotspots)))
        
        return table
    
    def _render_hotspots_table(self):
        """Render the hotspots table."""
        if not self.hotspots:
            return Text("No hotspots found! Coverage looks great! 🎉", 
                       style="bold green", justify="center")
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Pri", style="bold", width=4)
        table.add_column("Name", style="white", width=25)
        table.add_column("Type", style="cyan", width=15)
        table.add_column("Cov%", justify="right", width=7)
        table.add_column("Left", justify="right", width=6)
        table.add_column("Reason", style="dim", width=35)
        
        # Show a window of items
        visible_start = max(0, self.selected_index - 5)
        visible_end = min(len(self.hotspots), visible_start + 15)
        
        for i in range(visible_start, visible_end):
            hotspot = self.hotspots[i]
            
            # Highlight selected
            name_style = "bold reverse" if i == self.selected_index else ""
            
            # Priority color
            pri_color = {
                "P0": "red",
                "P1": "yellow",
                "P2": "cyan",
                "P3": "blue"
            }.get(hotspot.priority, "white")
            
            # Coverage color
            if hotspot.coverage == 0:
                cov_color = "red"
            elif hotspot.coverage < 50:
                cov_color = "yellow"
            else:
                cov_color = "green"
            
            # Type formatting
            type_display = {
                "low_coverage": "Low Cov",
                "near_complete": "Near Done",
                "high_value": "Untested"
            }.get(hotspot.hotspot_type, hotspot.hotspot_type)
            
            table.add_row(
                Text(hotspot.priority, style=pri_color),
                Text(hotspot.name, style=name_style),
                type_display,
                Text(f"{hotspot.coverage:.0f}%", style=cov_color),
                str(hotspot.items_remaining),
                hotspot.reason
            )
        
        if visible_end < len(self.hotspots):
            table.add_row("", "", "", "", "", f"... {len(self.hotspots) - visible_end} more")
        
        return table
    
    def handle_key(self, key: str) -> bool:
        """Handle hotspots-specific keys."""
        if key == 'down':
            self.selected_index = min(len(self.hotspots) - 1, self.selected_index + 1)
            return True
        elif key == 'up':
            self.selected_index = max(0, self.selected_index - 1)
            return True
        elif key == 'pagedown':
            self.selected_index = min(len(self.hotspots) - 1, self.selected_index + 10)
            return True
        elif key == 'pageup':
            self.selected_index = max(0, self.selected_index - 10)
            return True
        elif key == 'home':
            self.selected_index = 0
            return True
        elif key == 'end':
            self.selected_index = len(self.hotspots) - 1
            return True
        
        return False
