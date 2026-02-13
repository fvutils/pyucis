"""
Metrics View - Statistical analysis and coverage distribution.
"""
from typing import Dict, List
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align

from ucis.tui.views.base_view import BaseView
from ucis.cover_type_t import CoverTypeT


class MetricsView(BaseView):
    """
    Metrics view for statistical analysis of coverage data.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.metrics = {}
        self._calculate_metrics()
    
    def _calculate_metrics(self):
        """Calculate comprehensive metrics."""
        from ucis.scope_type_t import ScopeTypeT
        
        self.metrics = {
            'total_covergroups': 0,
            'total_coverpoints': 0,
            'total_bins': 0,
            'covered_bins': 0,
            'zero_hit_bins': 0,
            'covergroup_coverage': [],  # List of coverage percentages
            'coverpoint_coverage': [],
            'bin_hit_distribution': {
                '0': 0,
                '1-10': 0,
                '11-100': 0,
                '100+': 0
            }
        }
        
        def visit_scope(scope):
            scope_type = scope.getScopeType()
            
            if scope_type == ScopeTypeT.COVERGROUP:
                self.metrics['total_covergroups'] += 1
                
                # Calculate covergroup coverage
                total = 0
                covered = 0
                
                try:
                    for cp in scope.scopes(ScopeTypeT.COVERPOINT):
                        self.metrics['total_coverpoints'] += 1
                        
                        cp_total = 0
                        cp_covered = 0
                        
                        for bin_idx in cp.coverItems(CoverTypeT.CVGBIN):
                            total += 1
                            cp_total += 1
                            self.metrics['total_bins'] += 1
                            
                            cover_data = bin_idx.getCoverData()
                            count = cover_data.data if cover_data else 0
                            
                            if count > 0:
                                covered += 1
                                cp_covered += 1
                                self.metrics['covered_bins'] += 1
                                
                                # Hit distribution
                                if count <= 10:
                                    self.metrics['bin_hit_distribution']['1-10'] += 1
                                elif count <= 100:
                                    self.metrics['bin_hit_distribution']['11-100'] += 1
                                else:
                                    self.metrics['bin_hit_distribution']['100+'] += 1
                            else:
                                self.metrics['zero_hit_bins'] += 1
                                self.metrics['bin_hit_distribution']['0'] += 1
                        
                        # Coverpoint coverage
                        if cp_total > 0:
                            cp_cov = (cp_covered / cp_total) * 100
                            self.metrics['coverpoint_coverage'].append(cp_cov)
                
                except:
                    pass
                
                # Covergroup coverage
                if total > 0:
                    cg_cov = (covered / total) * 100
                    self.metrics['covergroup_coverage'].append(cg_cov)
            
            # Recurse
            try:
                for child in scope.scopes(ScopeTypeT.ALL):
                    visit_scope(child)
            except:
                pass
        
        try:
            for scope in self.model.db.scopes(ScopeTypeT.ALL):
                visit_scope(scope)
        except:
            pass
    
    def render(self):
        """Render the metrics view."""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1)
        )
        
        # Header
        title = Text("Coverage Metrics & Statistics", style="bold cyan", justify="center")
        header_panel = Panel(title, border_style="cyan")
        layout["header"].update(header_panel)
        
        # Body - 2x2 grid
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        layout["body"]["left"].split_column(
            Layout(name="summary"),
            Layout(name="distribution")
        )
        
        layout["body"]["right"].split_column(
            Layout(name="statistics"),
            Layout(name="quality")
        )
        
        # Render panels
        layout["body"]["left"]["summary"].update(
            Panel(self._render_summary(), title="Overall Summary", border_style="green")
        )
        layout["body"]["left"]["distribution"].update(
            Panel(self._render_distribution(), title="Hit Distribution", border_style="yellow")
        )
        layout["body"]["right"]["statistics"].update(
            Panel(self._render_statistics(), title="Statistics", border_style="blue")
        )
        layout["body"]["right"]["quality"].update(
            Panel(self._render_quality(), title="Quality Indicators", border_style="magenta")
        )
        
        return layout
    
    def _render_summary(self):
        """Render overall summary."""
        overall_cov = 0
        if self.metrics['total_bins'] > 0:
            overall_cov = (self.metrics['covered_bins'] / self.metrics['total_bins']) * 100
        
        table = Table.grid(padding=(0, 2))
        table.add_column(style="cyan", justify="right")
        table.add_column(style="white bold")
        
        table.add_row("Overall Coverage:", f"{overall_cov:.1f}%")
        table.add_row("", "")
        table.add_row("Covergroups:", str(self.metrics['total_covergroups']))
        table.add_row("Coverpoints:", str(self.metrics['total_coverpoints']))
        table.add_row("Total Bins:", str(self.metrics['total_bins']))
        table.add_row("", "")
        table.add_row("Covered Bins:", Text(str(self.metrics['covered_bins']), style="green"))
        table.add_row("Uncovered Bins:", Text(str(self.metrics['zero_hit_bins']), style="red"))
        
        return table
    
    def _render_distribution(self):
        """Render hit count distribution."""
        dist = self.metrics['bin_hit_distribution']
        total = sum(dist.values())
        
        if total == 0:
            return Text("No data", style="dim")
        
        table = Table(show_header=True, header_style="bold yellow")
        table.add_column("Hit Count", style="cyan")
        table.add_column("Bins", justify="right")
        table.add_column("Percentage", justify="right")
        table.add_column("Bar", width=20)
        
        for range_name, count in dist.items():
            pct = (count / total) * 100
            bar_len = int((count / total) * 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            
            # Color based on range
            if range_name == '0':
                color = "red"
            elif range_name == '1-10':
                color = "yellow"
            else:
                color = "green"
            
            table.add_row(
                range_name,
                str(count),
                f"{pct:.1f}%",
                Text(bar, style=color)
            )
        
        return table
    
    def _render_statistics(self):
        """Render statistical measures."""
        cg_cov = self.metrics['covergroup_coverage']
        cp_cov = self.metrics['coverpoint_coverage']
        
        def calc_stats(data):
            if not data:
                return 0, 0, 0, 0
            return (
                sum(data) / len(data),  # mean
                sorted(data)[len(data) // 2],  # median
                min(data),  # min
                max(data)  # max
            )
        
        cg_mean, cg_median, cg_min, cg_max = calc_stats(cg_cov)
        cp_mean, cp_median, cp_min, cp_max = calc_stats(cp_cov)
        
        table = Table.grid(padding=(0, 1))
        table.add_column(style="bold", width=18)
        table.add_column(style="cyan", justify="right", width=8)
        table.add_column(style="cyan", justify="right", width=8)
        
        table.add_row("", "CvrGrp", "CvrPt")
        table.add_row("Mean:", f"{cg_mean:.1f}%", f"{cp_mean:.1f}%")
        table.add_row("Median:", f"{cg_median:.1f}%", f"{cp_median:.1f}%")
        table.add_row("Min:", f"{cg_min:.1f}%", f"{cp_min:.1f}%")
        table.add_row("Max:", f"{cg_max:.1f}%", f"{cp_max:.1f}%")
        
        return table
    
    def _render_quality(self):
        """Render quality indicators."""
        # Coverage completeness tiers
        cg_cov = self.metrics['covergroup_coverage']
        
        complete_100 = len([c for c in cg_cov if c == 100])
        high_80plus = len([c for c in cg_cov if 80 <= c < 100])
        med_50plus = len([c for c in cg_cov if 50 <= c < 80])
        low = len([c for c in cg_cov if c < 50])
        
        total_cg = len(cg_cov) if cg_cov else 1
        
        table = Table.grid(padding=(0, 2))
        table.add_column(style="bold")
        table.add_column(justify="right")
        table.add_column(justify="right", style="dim")
        
        table.add_row(
            Text("Complete (100%)", style="green"),
            str(complete_100),
            f"({complete_100 / total_cg * 100:.0f}%)"
        )
        table.add_row(
            Text("High (80-99%)", style="cyan"),
            str(high_80plus),
            f"({high_80plus / total_cg * 100:.0f}%)"
        )
        table.add_row(
            Text("Medium (50-79%)", style="yellow"),
            str(med_50plus),
            f"({med_50plus / total_cg * 100:.0f}%)"
        )
        table.add_row(
            Text("Low (<50%)", style="red"),
            str(low),
            f"({low / total_cg * 100:.0f}%)"
        )
        
        # Additional quality metrics
        table.add_row("", "", "")
        
        avg_bins_per_cp = self.metrics['total_bins'] / max(1, self.metrics['total_coverpoints'])
        zero_hit_ratio = (self.metrics['zero_hit_bins'] / max(1, self.metrics['total_bins'])) * 100
        
        table.add_row(
            "Avg bins/coverpoint:",
            f"{avg_bins_per_cp:.1f}",
            ""
        )
        table.add_row(
            "Zero-hit ratio:",
            f"{zero_hit_ratio:.1f}%",
            Text("⚠" if zero_hit_ratio > 50 else "✓", style="yellow" if zero_hit_ratio > 50 else "green")
        )
        
        return table
    
    def handle_key(self, key: str) -> bool:
        """Handle metrics-specific keys."""
        # Metrics view is mostly read-only
        return False
