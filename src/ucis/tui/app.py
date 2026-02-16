"""
Main TUI Application class.

Orchestrates the terminal UI, manages views, handles global keyboard input.
"""
from typing import Dict, Optional, List
from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
import os

from ucis.tui.models.coverage_model import CoverageModel
from ucis.tui.views.base_view import BaseView
from ucis.tui.views.dashboard_view import DashboardView
from ucis.tui.components.status_bar import StatusBar
from ucis.tui.components.help_overlay import HelpOverlay
from ucis.tui.keybindings import KeyHandler
from ucis.tui.key_parser import KeyParser
from ucis.tui.controller import TUIController

_file = None

class TUIApp:
    """
    Main TUI application orchestrator.
    
    Manages views, handles navigation, processes keyboard input.
    """
    
    def __init__(self, db_path: str, input_format: Optional[str] = None):
        """
        Initialize the TUI application.
        
        Args:
            db_path: Path to the UCIS database file
            input_format: Optional database format (auto-detect if None)
        """
        self.db_path = db_path
        self.input_format = input_format
        self.console = Console()
        self.coverage_model = None
        self.controller = None  # Will be initialized in run()
        self.status_bar = StatusBar()
        self.help_overlay = HelpOverlay()
        self.key_parser = None  # Initialized in run()
        
    def run(self):
        """Main event loop."""
        # Show loading message
        with self.console.status("[bold green]Loading coverage database...") as status:
            self.coverage_model = CoverageModel(self.db_path, self.input_format)
            
            # Create controller
            self.controller = TUIController(self.coverage_model, on_quit=self._on_quit)
            self.controller.running = True
            
            # Initialize views and register with controller
            self._initialize_views()
        
        # Switch to dashboard view
        self.controller.switch_view("dashboard")
        
        # Main render loop
        try:
            with Live(self._render(), console=self.console, screen=True, auto_refresh=False) as live:
                self.live = live
                
                while self.controller.running:
                    # Get keyboard input (this will set raw mode internally)
                    key = self._get_key_input()
                    
                    if key:
                        # Let controller handle the key
                        self.controller.handle_key(key)
                        
                        # Refresh display
                        live.update(self._render(), refresh=True)
        finally:
            self.console.clear()
    
    def _on_quit(self):
        """Callback when controller quits."""
        # Can add cleanup here if needed
        pass
    
    def _initialize_views(self):
        """Initialize all available views."""
        from ucis.tui.views.hierarchy_view import HierarchyView
        from ucis.tui.views.gaps_view import GapsView
        from ucis.tui.views.hotspots_view import HotspotsView
        from ucis.tui.views.metrics_view import MetricsView
        from ucis.tui.views.code_coverage_view import CodeCoverageView
        from ucis.tui.views.test_history_view import TestHistoryView
        
        # Create views and register with controller
        views = {
            "dashboard": DashboardView(self),
            "hierarchy": HierarchyView(self),
            "gaps": GapsView(self),
            "hotspots": HotspotsView(self),
            "metrics": MetricsView(self),
            "code_coverage": CodeCoverageView(self),
            "test_history": TestHistoryView(self),
        }
        
        for name, view in views.items():
            self.controller.register_view(name, view)
    
    def _render(self) -> Layout:
        """
        Render the current view with status bar.
        
        Returns:
            Rich Layout containing the view and status bar
        """
        # If help is shown, render help overlay
        if self.controller.show_help:
            return self.help_overlay.render()
        
        layout = Layout()
        layout.split_column(
            Layout(name="main", ratio=1),
            Layout(name="status", size=1)
        )
        
        # Render current view
        current_view = self.controller.get_current_view()
        if current_view:
            layout["main"].update(current_view.render())
        else:
            layout["main"].update(Panel("No view active"))
        
        # Render status bar
        layout["status"].update(self.status_bar.render(current_view, self.coverage_model))
        
        return layout
    
    def _get_key_input(self) -> Optional[str]:
        """
        Get keyboard input from the user.
        
        Sets terminal to raw mode, reads a key using KeyParser, then restores.
        KeyParser now uses buffered reading to prevent escape sequence fragmentation.
        
        Returns:
            Key string or None if no input
        """
        import sys
        import termios
        import tty
        import select
        
        # Save terminal settings
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        try:
            # Set raw mode for reading
            tty.setraw(fd)
            
            # Create KeyParser if not already created
            if self.key_parser is None:
                self.key_parser = KeyParser(
                    read_fn=lambda n: os.read(fd, n).decode('utf-8', errors='ignore'),
                    select_fn=lambda timeout: select.select([fd], [], [], timeout)[0]
                )
            
            # Parse the key (KeyParser will read all available data)
            key = self.key_parser.parse_key()
            
            # DEBUG: Log key for troubleshooting
            # Uncomment to debug key parsing issues:
            # if key: print(f"\n[DEBUG] _get_key_input returned: {repr(key)}", flush=True)
            
            return key
            
        finally:
            # Restore terminal settings so Rich can render properly
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
