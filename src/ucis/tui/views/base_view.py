"""
Abstract base class for all TUI views.
"""
from abc import ABC, abstractmethod
from typing import Any
from rich.console import RenderableType


class BaseView(ABC):
    """
    Abstract base class for all TUI views.
    
    Provides common interface for rendering and keyboard handling.
    """
    
    def __init__(self, app):
        """
        Initialize view.
        
        Args:
            app: Reference to the TUIApp instance
        """
        self.app = app
        self.focused = False
    
    @abstractmethod
    def render(self) -> RenderableType:
        """
        Render the view content.
        
        Returns:
            Rich renderable object
        """
        pass
    
    def handle_key(self, key: str) -> bool:
        """
        Handle key press.
        
        Args:
            key: Key string from input
            
        Returns:
            True if key was handled, False otherwise
        """
        return False
    
    def on_enter(self):
        """Called when view becomes active."""
        self.focused = True
    
    def on_exit(self):
        """Called when leaving view."""
        self.focused = False
    
    @property
    def model(self):
        """Convenience property to access coverage model."""
        return self.app.coverage_model
