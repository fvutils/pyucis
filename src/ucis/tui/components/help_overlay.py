"""
Help Overlay - Display keyboard shortcuts and usage information.
"""
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align


class HelpOverlay:
    """
    Help overlay showing keyboard shortcuts and features.
    """
    
    def __init__(self):
        pass
    
    def render(self):
        """Render the help overlay."""
        content = self._create_help_content()
        
        return Panel(
            content,
            title="[bold cyan]PyUCIS TUI - Help[/bold cyan]",
            subtitle="Press any key to close",
            border_style="cyan",
            padding=(1, 2)
        )
    
    def _create_help_content(self):
        """Create the help content with sections."""
        # Global shortcuts
        global_table = Table(show_header=True, header_style="bold yellow", box=None, padding=(0, 2))
        global_table.add_column("Key", style="cyan", width=15)
        global_table.add_column("Action", style="white")
        
        global_table.add_row("q, Ctrl+C", "Quit application")
        global_table.add_row("?, F1", "Show this help")
        global_table.add_row("Ctrl+R", "Refresh database")
        global_table.add_row("C", "Clear test filter")
        global_table.add_row("Ctrl+F", "Global search (coming soon)")
        global_table.add_row("Esc, Backspace", "Go back / Cancel")
        
        # View switching
        view_table = Table(show_header=True, header_style="bold yellow", box=None, padding=(0, 2))
        view_table.add_column("Key", style="cyan", width=15)
        view_table.add_column("View", style="white")
        
        view_table.add_row("1", "Dashboard - Coverage overview")
        view_table.add_row("2", "Hierarchy - Design tree navigation")
        view_table.add_row("3", "Gaps - Uncovered items")
        view_table.add_row("4", "Hotspots - Priority analysis (coming soon)")
        view_table.add_row("5", "Metrics - Statistics (coming soon)")
        view_table.add_row("6", "Code Coverage - File-level code coverage")
        view_table.add_row("7", "Test History - Test contribution analysis")
        
        # Navigation
        nav_table = Table(show_header=True, header_style="bold yellow", box=None, padding=(0, 2))
        nav_table.add_column("Key", style="cyan", width=15)
        nav_table.add_column("Action", style="white")
        
        nav_table.add_row("↑/↓", "Navigate up/down")
        nav_table.add_row("←/→", "Collapse/expand tree (Hierarchy)")
        nav_table.add_row("PgUp/PgDn", "Page up/down")
        nav_table.add_row("Home/End", "Jump to start/end")
        nav_table.add_row("Enter", "Select/expand item (toggle in Hierarchy)")
        nav_table.add_row("Space", "Toggle selection")
        nav_table.add_row("E", "Expand all (Hierarchy view)")
        nav_table.add_row("C", "Collapse all (Hierarchy view)")
        nav_table.add_row("/", "Search/filter (Hierarchy view)")
        
        # View-specific
        view_specific_table = Table(show_header=True, header_style="bold yellow", box=None, padding=(0, 2))
        view_specific_table.add_column("View", style="cyan", width=15)
        view_specific_table.add_column("Description", style="white")
        
        view_specific_table.add_row("Dashboard", "High-level coverage summary with statistics")
        view_specific_table.add_row("Hierarchy", "Navigate design structure (E=expand all, C=collapse all, /=search)")
        view_specific_table.add_row("Gaps", "Find uncovered bins, sort by coverage %")
        view_specific_table.add_row("Test History", "View tests (N/D/C/U=sort, F=filter)")
        
        # Color coding
        color_table = Table(show_header=True, header_style="bold yellow", box=None, padding=(0, 2))
        color_table.add_column("Coverage Range", style="cyan", width=20)
        color_table.add_column("Color", style="white")
        
        color_table.add_row("0-50%", Text("Red (Critical)", style="red"))
        color_table.add_row("50-80%", Text("Yellow (Needs attention)", style="yellow"))
        color_table.add_row("80-100%", Text("Green (Good)", style="green"))
        color_table.add_row("100%", Text("Cyan (Complete)", style="cyan"))
        
        # Combine sections
        text = Text()
        
        text.append("GLOBAL SHORTCUTS\n", style="bold green")
        sections = [
            ("GLOBAL SHORTCUTS", global_table),
            ("VIEW SWITCHING", view_table),
            ("NAVIGATION", nav_table),
            ("VIEW DESCRIPTIONS", view_specific_table),
            ("COVERAGE COLOR CODING", color_table),
        ]
        
        content_parts = []
        for title, table in sections:
            section = Text()
            section.append(f"\n{title}\n", style="bold green")
            content_parts.append(section)
            content_parts.append(table)
        
        # Add footer
        footer = Text()
        footer.append("\n\n")
        footer.append("PyUCIS TUI v0.1.0", style="dim")
        footer.append(" | ", style="dim")
        footer.append("Python API for UCIS Coverage Data", style="dim")
        footer.append("\n")
        footer.append("Documentation: https://github.com/fvutils/pyucis", style="dim italic")
        content_parts.append(footer)
        
        # Combine all parts
        from rich.console import Group
        return Group(*content_parts)
