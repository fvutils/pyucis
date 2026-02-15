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
    
    def render(self, current_view=None, coverage_model=None) -> RenderableType:
        """
        Render the status bar.
        
        Args:
            current_view: Current active view
            coverage_model: Coverage model to check for filter status
            
        Returns:
            Rich Text object
        """
        text = Text()
        
        # Shortcuts - context-sensitive
        if current_view == "hierarchy":
            shortcuts = [
                ("[↑↓]", "Navigate"),
                ("[Enter]", "Toggle"),
                ("[E]", "Expand All"),
                ("[C]", "Collapse All"),
                ("[/]", "Search"),
                ("[1-5]", "Views"),
                ("[?]", "Help"),
                ("[q]", "Quit"),
            ]
        else:
            shortcuts = [
                ("[1]", "Dashboard"),
                ("[2]", "Hierarchy"),
                ("[3]", "Gaps"),
                ("[4]", "Hotspots"),
                ("[5]", "Metrics"),
                ("[6]", "Code Cov"),
                ("[7]", "Tests"),
                ("[?]", "Help"),
                ("[q]", "Quit"),
            ]
        
        for key, desc in shortcuts:
            text.append(key, style="bold cyan")
            text.append(f" {desc}  ", style="dim")
        
        # Show filter status
        if coverage_model and coverage_model.get_test_filter():
            test_filter = coverage_model.get_test_filter()
            text.append(" | ", style="dim")
            text.append("Filter: ", style="bold yellow")
            text.append(test_filter, style="yellow")
        
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
