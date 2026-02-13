"""
Status bar component for the TUI.
"""
from rich.console import RenderableType
from rich.text import Text


class StatusBar:
    """
    Status bar showing keyboard shortcuts and messages.
    """
    
    def __init__(self):
        self.message = ""
        self.message_type = "info"
    
    def render(self, current_view=None) -> RenderableType:
        """
        Render the status bar.
        
        Args:
            current_view: Current active view
            
        Returns:
            Rich Text object
        """
        text = Text()
        
        # Shortcuts
        shortcuts = [
            ("[1]", "Dashboard"),
            ("[?]", "Help"),
            ("[q]", "Quit"),
        ]
        
        for key, desc in shortcuts:
            text.append(key, style="bold cyan")
            text.append(f" {desc}  ", style="dim")
        
        # Message (if any)
        if self.message:
            text.append(" | ", style="dim")
            
            style = "green" if self.message_type == "info" else "red" if self.message_type == "error" else "yellow"
            text.append(self.message, style=style)
        
        return text
    
    def set_message(self, message: str, msg_type: str = "info"):
        """
        Set a temporary status message.
        
        Args:
            message: Message to display
            msg_type: Type of message (info, warning, error)
        """
        self.message = message
        self.message_type = msg_type
    
    def clear_message(self):
        """Clear the status message."""
        self.message = ""
