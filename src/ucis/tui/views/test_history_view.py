"""
Test History View - Display and interact with test history data.
"""
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.text import Text

from ucis.tui.views.base_view import BaseView


class TestHistoryView(BaseView):
    """
    Test History view showing all tests with contribution data.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.selected_index = 0
        self.scroll_offset = 0
        self.sort_by = "name"  # name, date, coverage, unique
        self.sort_ascending = True
        self.tests = []
        self.visible_rows = 20  # Will be adjusted dynamically
    
    def on_enter(self):
        """Called when view becomes active."""
        super().on_enter()
        self._load_tests()
    
    def _load_tests(self):
        """Load test data from the model."""
        self.tests = self.model.get_all_tests()
        self._apply_sort()
    
    def _apply_sort(self):
        """Sort tests based on current sort criteria."""
        if not self.tests:
            return
        
        reverse = not self.sort_ascending
        
        if self.sort_by == "name":
            self.tests.sort(key=lambda t: t.get('name', ''), reverse=reverse)
        elif self.sort_by == "date":
            self.tests.sort(key=lambda t: t.get('date', ''), reverse=reverse)
        elif self.sort_by == "coverage":
            self.tests.sort(key=lambda t: t.get('total_items', 0), reverse=reverse)
        elif self.sort_by == "unique":
            self.tests.sort(key=lambda t: t.get('unique_items', 0), reverse=reverse)
    
    def render(self):
        """Render the test history view."""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1)
        )
        
        # Header
        title = Text("Test History", style="bold cyan", justify="center")
        test_count = len(self.tests)
        subtitle = Text(f"{test_count} test(s) | Sort by: {self.sort_by} ({'↑' if self.sort_ascending else '↓'})", 
                       style="dim", justify="center")
        header_panel = Panel(
            Align.center(title + Text("\n") + subtitle),
            border_style="cyan"
        )
        layout["header"].update(header_panel)
        
        # Body - split into test list and details
        layout["body"].split_row(
            Layout(name="test_list", ratio=2),
            Layout(name="test_details", ratio=1)
        )
        
        # Test list table
        test_table = self._render_test_list()
        layout["body"]["test_list"].update(
            Panel(test_table, title="Tests", border_style="cyan")
        )
        
        # Test details panel
        details_panel = self._render_test_details()
        layout["body"]["test_details"].update(
            Panel(details_panel, title="Test Details", border_style="cyan")
        )
        
        return layout
    
    def _render_test_list(self) -> Table:
        """Render the test list table."""
        table = Table(show_header=True, header_style="bold magenta", box=None)
        table.add_column("", width=2)  # Selection indicator
        table.add_column("Test Name", style="cyan", no_wrap=False)
        table.add_column("Status", width=8, justify="center")
        table.add_column("Items", width=8, justify="right")
        table.add_column("Unique", width=8, justify="right")
        table.add_column("Value", width=8, justify="right")
        
        if not self.tests:
            table.add_row("", "[dim]No tests found[/dim]", "", "", "", "")
            return table
        
        # Calculate visible window
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.visible_rows, len(self.tests))
        
        for i in range(start_idx, end_idx):
            test = self.tests[i]
            
            # Selection indicator
            indicator = "→" if i == self.selected_index else " "
            
            # Test name
            name = test.get('name', 'Unknown')
            
            # Status (with color)
            status = test.get('status', 'UNKNOWN')
            if status == 'PASSED':
                status_str = "[green]✓ PASS[/green]"
            elif status == 'FAILED':
                status_str = "[red]✗ FAIL[/red]"
            else:
                status_str = "[yellow]? UNK[/yellow]"
            
            # Coverage metrics
            total_items = test.get('total_items', 0)
            unique_items = test.get('unique_items', 0)
            
            # Value indicator (percentage of unique coverage)
            if total_items > 0:
                unique_pct = (unique_items / total_items) * 100
                if unique_pct >= 10:
                    value_str = f"[green]{unique_pct:.1f}%[/green]"
                elif unique_pct > 0:
                    value_str = f"[yellow]{unique_pct:.1f}%[/yellow]"
                else:
                    value_str = "[red]0%[/red]"
            else:
                value_str = "[dim]-[/dim]"
            
            # Highlight selected row
            if i == self.selected_index:
                name = f"[bold]{name}[/bold]"
            
            table.add_row(
                indicator,
                name,
                status_str,
                str(total_items),
                str(unique_items),
                value_str
            )
        
        # Show scroll indicator if needed
        if len(self.tests) > self.visible_rows:
            showing = f"Showing {start_idx + 1}-{end_idx} of {len(self.tests)}"
            table.caption = showing
        
        return table
    
    def _render_test_details(self) -> Text:
        """Render the details panel for the selected test."""
        if not self.tests or self.selected_index >= len(self.tests):
            return Text("No test selected", style="dim")
        
        test = self.tests[self.selected_index]
        
        details = Text()
        details.append("Test: ", style="bold")
        details.append(f"{test.get('name', 'Unknown')}\n\n")
        
        details.append("Status: ", style="bold")
        status = test.get('status', 'UNKNOWN')
        if status == 'PASSED':
            details.append("✓ PASSED\n", style="green")
        elif status == 'FAILED':
            details.append("✗ FAILED\n", style="red")
        else:
            details.append("? UNKNOWN\n", style="yellow")
        
        details.append("\nDate: ", style="bold")
        details.append(f"{test.get('date', 'Unknown')}\n")
        
        details.append("\nCoverage:\n", style="bold")
        total = test.get('total_items', 0)
        unique = test.get('unique_items', 0)
        details.append(f"  Total items: {total}\n")
        details.append(f"  Unique items: {unique}\n")
        
        if total > 0:
            unique_pct = (unique / total) * 100
            details.append(f"  Unique %: {unique_pct:.1f}%\n")
        
        details.append("\n")
        
        # Value assessment
        if unique > 0:
            details.append("Value: ", style="bold")
            if unique >= total * 0.1:
                details.append("🌟 High value test\n", style="green")
                details.append("  Keep for regression\n", style="dim")
            else:
                details.append("⚠ Some unique coverage\n", style="yellow")
                details.append("  Consider for optimization\n", style="dim")
        else:
            details.append("Value: ", style="bold")
            details.append("⚠ Redundant test\n", style="red")
            details.append("  No unique coverage\n", style="dim")
            details.append("  Consider removing\n", style="dim")
        
        details.append("\n[dim]Press F to filter by this test[/dim]")
        
        return details
    
    def handle_key(self, key: str) -> bool:
        """Handle keyboard input."""
        if not self.tests:
            return False
        
        # Navigation
        if key == "up":
            self._move_selection(-1)
            return True
        elif key == "down":
            self._move_selection(1)
            return True
        elif key == "pageup":
            self._move_selection(-10)
            return True
        elif key == "pagedown":
            self._move_selection(10)
            return True
        elif key == "home":
            self.selected_index = 0
            self.scroll_offset = 0
            return True
        elif key == "end":
            self.selected_index = len(self.tests) - 1
            self._adjust_scroll()
            return True
        
        # Sorting
        elif key == "n":
            self._toggle_sort("name")
            return True
        elif key == "d":
            self._toggle_sort("date")
            return True
        elif key == "c":
            self._toggle_sort("coverage")
            return True
        elif key == "u":
            self._toggle_sort("unique")
            return True
        
        # Actions
        elif key in ("f", "F"):
            self._filter_by_test()
            return True
        
        return False
    
    def _move_selection(self, delta: int):
        """Move selection by delta, handling scrolling."""
        old_index = self.selected_index
        self.selected_index = max(0, min(len(self.tests) - 1, self.selected_index + delta))
        
        # Adjust scroll if needed
        if self.selected_index != old_index:
            self._adjust_scroll()
    
    def _adjust_scroll(self):
        """Adjust scroll offset to keep selection visible."""
        # Ensure selected item is visible
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.visible_rows:
            self.scroll_offset = self.selected_index - self.visible_rows + 1
        
        # Clamp scroll offset
        max_scroll = max(0, len(self.tests) - self.visible_rows)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))
    
    def _toggle_sort(self, sort_by: str):
        """Toggle sort by the given field."""
        if self.sort_by == sort_by:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_by = sort_by
            self.sort_ascending = True
        
        self._apply_sort()
        
        # Reset selection to top
        self.selected_index = 0
        self.scroll_offset = 0
    
    def _filter_by_test(self):
        """Filter all views by the selected test."""
        if not self.tests or self.selected_index >= len(self.tests):
            return
        
        test = self.tests[self.selected_index]
        test_name = test.get('name', '')
        
        # Set filter in model
        self.model.set_test_filter(test_name)
        
        # Update status bar
        self.app.status_bar.set_message(f"Filtering by test: {test_name}", "info")
        
        # Switch to dashboard to see filtered results
        self.app.switch_view("dashboard")
