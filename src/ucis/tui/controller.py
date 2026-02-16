"""
TUI Controller - Core application state and logic.

Manages navigation, view state, and key routing without any UI dependencies.
This allows unit testing of all navigation logic.
"""
from typing import Dict, List, Optional, Callable


class TUIController:
    """
    Controller for TUI application state and navigation logic.
    
    This class is UI-agnostic and fully testable. It manages:
    - Current view/page state
    - View switching and navigation
    - Key routing (view first, then global)
    - View history for back navigation
    """
    
    def __init__(self, coverage_model, on_quit: Optional[Callable] = None):
        """
        Initialize TUI controller.
        
        Args:
            coverage_model: Coverage data model
            on_quit: Optional callback to call when quitting
        """
        self.coverage_model = coverage_model
        self.on_quit = on_quit
        
        # State
        self.current_view_name: Optional[str] = None
        self.views: Dict[str, any] = {}  # view_name -> view instance
        self.view_history: List[str] = []
        self.show_help = False
        self.running = False
        
        # Status messages
        self.status_message = ""
        self.status_type = "info"  # "info", "error", "success"
    
    def register_view(self, name: str, view):
        """Register a view with the controller."""
        self.views[name] = view
    
    def switch_view(self, view_name: str) -> bool:
        """
        Switch to a different view.
        
        Args:
            view_name: Name of the view to switch to
            
        Returns:
            True if switch was successful, False otherwise
        """
        if view_name not in self.views:
            self.set_status(f"Unknown view: {view_name}", "error")
            return False
        
        # Call on_exit for current view
        if self.current_view_name and self.current_view_name in self.views:
            current_view = self.views[self.current_view_name]
            if hasattr(current_view, 'on_exit'):
                current_view.on_exit()
            self.view_history.append(self.current_view_name)
        
        # Switch view
        self.current_view_name = view_name
        new_view = self.views[view_name]
        if hasattr(new_view, 'on_enter'):
            new_view.on_enter()
        
        self.set_status(f"Switched to {view_name} view", "info")
        return True
    
    def get_current_view(self):
        """Get the current view instance."""
        if self.current_view_name:
            return self.views.get(self.current_view_name)
        return None
    
    def go_back(self):
        """Go back to previous view or dashboard."""
        # For now, simple implementation - go to dashboard
        self.switch_view("dashboard")
    
    def quit(self):
        """Quit the application."""
        self.running = False
        if self.on_quit:
            self.on_quit()
    
    def set_status(self, message: str, msg_type: str = "info"):
        """Set status bar message."""
        self.status_message = message
        self.status_type = msg_type
    
    def handle_key(self, key: str) -> bool:
        """
        Handle a key press through the controller.
        
        This implements the key routing logic:
        1. If help is shown, any key closes it
        2. Give current view first chance to handle key
        3. If view doesn't handle it, try global keys
        
        Args:
            key: Key string from parser
            
        Returns:
            True if key was handled, False otherwise
        """
        # Help overlay handling
        if self.show_help:
            self.show_help = False
            return True
        
        # Give view first chance to handle key
        current_view = self.get_current_view()
        if current_view and hasattr(current_view, 'handle_key'):
            if current_view.handle_key(key):
                return True
        
        # If view didn't handle it, try global keys
        return self._handle_global_key(key)
    
    def _handle_global_key(self, key: str) -> bool:
        """
        Handle global keyboard shortcuts.
        
        Args:
            key: Key string from input
            
        Returns:
            True if key was handled, False otherwise
        """
        # Quit
        if key in ('q', 'Q', 'ctrl+c'):
            self.quit()
            return True
        
        # Help
        if key in ('?', 'F1'):
            self.show_help = True
            return True
        
        # Refresh
        if key == 'ctrl+r':
            self.set_status("Refreshing database...", "info")
            # TODO: Reload database
            return True
        
        # View switching (numbers)
        view_map = {
            '1': 'dashboard',
            '2': 'hierarchy',
            '3': 'gaps',
            '4': 'hotspots',
            '5': 'metrics',
            '6': 'code_coverage',
            '7': 'test_history',
        }
        
        if key in view_map:
            return self.switch_view(view_map[key])
        
        # Clear test filter
        if key in ('c', 'C'):
            if self.coverage_model.get_test_filter():
                self.coverage_model.clear_test_filter()
                self.set_status("Test filter cleared", "info")
                return True
        
        # Back/Escape
        if key in ('backspace', 'esc'):
            self.go_back()
            return True
        
        return False
    
    def get_state_debug(self) -> Dict:
        """
        Get current state for debugging/testing.
        
        Returns:
            Dictionary with current state information
        """
        return {
            'current_view': self.current_view_name,
            'view_history': self.view_history.copy(),
            'show_help': self.show_help,
            'running': self.running,
            'status_message': self.status_message,
            'status_type': self.status_type,
        }
