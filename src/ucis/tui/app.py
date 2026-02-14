"""
Main TUI Application class.

Orchestrates the terminal UI, manages views, handles global keyboard input.
"""
from typing import Dict, Optional, List
from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel

from ucis.tui.models.coverage_model import CoverageModel
from ucis.tui.views.base_view import BaseView
from ucis.tui.views.dashboard_view import DashboardView
from ucis.tui.components.status_bar import StatusBar
from ucis.tui.components.help_overlay import HelpOverlay
from ucis.tui.keybindings import KeyHandler


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
        self.current_view: Optional[BaseView] = None
        self.views: Dict[str, BaseView] = {}
        self.view_history: List[str] = []
        self.running = False
        self.key_handler = KeyHandler(self)
        self.status_bar = StatusBar()
        self.help_overlay = HelpOverlay()
        self.show_help = False
        
    def run(self):
        """Main event loop."""
        self.running = True
        
        # Show loading message
        with self.console.status("[bold green]Loading coverage database...") as status:
            self.coverage_model = CoverageModel(self.db_path, self.input_format)
            self._initialize_views()
        
        # Switch to dashboard view
        self.switch_view("dashboard")
        
        # Main render loop
        try:
            with Live(self._render(), console=self.console, screen=True, auto_refresh=False) as live:
                self.live = live
                while self.running:
                    # Get keyboard input
                    key = self._get_key_input()
                    
                    if key:
                        # If help is shown, any key closes it
                        if self.show_help:
                            self.show_help = False
                            live.update(self._render(), refresh=True)
                            continue
                        
                        # Handle global keys first
                        if self.key_handler.handle_global_key(key):
                            pass  # Handled globally
                        # Then view-specific keys
                        elif self.current_view:
                            self.current_view.handle_key(key)
                        
                        # Refresh display
                        live.update(self._render(), refresh=True)
        finally:
            self.console.clear()
    
    def _initialize_views(self):
        """Initialize all available views."""
        from ucis.tui.views.hierarchy_view import HierarchyView
        from ucis.tui.views.gaps_view import GapsView
        from ucis.tui.views.hotspots_view import HotspotsView
        from ucis.tui.views.metrics_view import MetricsView
        from ucis.tui.views.code_coverage_view import CodeCoverageView
        
        self.views["dashboard"] = DashboardView(self)
        self.views["hierarchy"] = HierarchyView(self)
        self.views["gaps"] = GapsView(self)
        self.views["hotspots"] = HotspotsView(self)
        self.views["metrics"] = MetricsView(self)
        self.views["code_coverage"] = CodeCoverageView(self)
    
    def _render(self) -> Layout:
        """
        Render the current view with status bar.
        
        Returns:
            Rich Layout containing the view and status bar
        """
        # If help is shown, render help overlay
        if self.show_help:
            return self.help_overlay.render()
        
        layout = Layout()
        layout.split_column(
            Layout(name="main", ratio=1),
            Layout(name="status", size=1)
        )
        
        # Render current view
        if self.current_view:
            layout["main"].update(self.current_view.render())
        else:
            layout["main"].update(Panel("No view active"))
        
        # Render status bar
        layout["status"].update(self.status_bar.render(self.current_view))
        
        return layout
    
    def _get_key_input(self) -> Optional[str]:
        """
        Get keyboard input from the user.
        
        Returns:
            Key string or None if no input
        """
        import sys
        import termios
        import tty
        
        # Save terminal settings
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            
            # Handle escape sequences (arrow keys, function keys, etc.)
            if ch == '\x1b':  # ESC
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A':
                        return 'up'
                    elif ch3 == 'B':
                        return 'down'
                    elif ch3 == 'C':
                        return 'right'
                    elif ch3 == 'D':
                        return 'left'
                    elif ch3 == 'H':
                        return 'home'
                    elif ch3 == 'F':
                        return 'end'
                    elif ch3 in ['5', '6']:  # Page Up/Down
                        sys.stdin.read(1)  # Read the ~ that follows
                        return 'pageup' if ch3 == '5' else 'pagedown'
                return 'esc'
            
            # Handle special characters
            if ch == '\r' or ch == '\n':
                return 'enter'
            elif ch == '\x7f' or ch == '\x08':
                return 'backspace'
            elif ch == '\t':
                return 'tab'
            elif ch == ' ':
                return 'space'
            elif ch == '\x03':  # Ctrl+C
                return 'ctrl+c'
            elif ch == '\x12':  # Ctrl+R
                return 'ctrl+r'
            elif ch == '\x13':  # Ctrl+S
                return 'ctrl+s'
            elif ch == '\x06':  # Ctrl+F
                return 'ctrl+f'
            elif ord(ch) >= 1 and ord(ch) <= 26:
                # Other Ctrl combinations
                return f'ctrl+{chr(ord(ch) + 96)}'
            
            return ch
            
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    def switch_view(self, view_name: str):
        """
        Switch to a different view.
        
        Args:
            view_name: Name of the view to switch to
        """
        if view_name not in self.views:
            self.status_bar.set_message(f"Unknown view: {view_name}", "error")
            return
        
        # Call on_exit for current view
        if self.current_view:
            self.current_view.on_exit()
            self.view_history.append(self.current_view.__class__.__name__)
        
        # Switch view
        self.current_view = self.views[view_name]
        self.current_view.on_enter()
        
        self.status_bar.set_message(f"Switched to {view_name} view", "info")
    
    def go_back(self):
        """Go back to previous view."""
        if self.view_history:
            # Simple implementation - just go to dashboard for now
            self.switch_view("dashboard")
    
    def quit(self):
        """Quit the application."""
        self.running = False
