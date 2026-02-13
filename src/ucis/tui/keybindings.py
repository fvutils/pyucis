"""
Keyboard event handling for the TUI.
"""


class KeyHandler:
    """Handles global keyboard shortcuts."""
    
    def __init__(self, app):
        """
        Initialize key handler.
        
        Args:
            app: Reference to the TUIApp instance
        """
        self.app = app
    
    def handle_global_key(self, key: str) -> bool:
        """
        Handle global keyboard shortcuts.
        
        Args:
            key: Key string from input
            
        Returns:
            True if key was handled, False otherwise
        """
        # Quit
        if key in ('q', 'Q', 'ctrl+c'):
            self.app.quit()
            return True
        
        # Help
        if key in ('?', 'F1'):
            self.app.status_bar.set_message("Help not yet implemented", "warning")
            return True
        
        # Refresh
        if key == 'ctrl+r':
            self.app.status_bar.set_message("Refreshing database...", "info")
            # TODO: Reload database
            return True
        
        # View switching (numbers)
        view_map = {
            '1': 'dashboard',
        }
        
        if key in view_map:
            self.app.switch_view(view_map[key])
            return True
        
        # Back/Escape
        if key in ('backspace', 'esc'):
            self.app.go_back()
            return True
        
        return False
