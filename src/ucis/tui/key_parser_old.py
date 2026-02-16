"""
Key input parser for TUI - extracted for testability.

Handles escape sequences, special characters, and distinguishes
standalone ESC from arrow keys and other escape sequences.
"""
from typing import Optional, Callable
import select


class KeyParser:
    """Parse raw terminal input into logical key names."""
    
    def __init__(self, read_fn: Callable[[int], str], select_fn: Optional[Callable] = None):
        """
        Initialize key parser.
        
        Args:
            read_fn: Function to read n characters from input (e.g., sys.stdin.read)
            select_fn: Function to check if input is available (for testing)
                      If None, uses select.select with fd 0
        """
        self.read_fn = read_fn
        self.select_fn = select_fn or (lambda timeout: select.select([0], [], [], timeout)[0])
    
    def parse_key(self) -> Optional[str]:
        """
        Parse next key from input.
        
        Returns:
            Key name string ('up', 'down', 'esc', 'enter', etc.) or None for ignored sequences
        """
        ch = self.read_fn(1)
        
        # Handle escape sequences (arrow keys, function keys, etc.)
        if ch == '\x1b':  # ESC
            # Check if more input is available
            # Longer timeout (200ms) to handle terminal latency and screen updates
            if self.select_fn(0.2):
                ch2 = self.read_fn(1)
                if ch2 == '[':
                    # For escape sequences starting with ESC[, wait for the next character
                    if self.select_fn(0.2):
                        ch3 = self.read_fn(1)
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
                            if self.select_fn(0.1):
                                self.read_fn(1)  # Read the ~ that follows
                            return 'pageup' if ch3 == '5' else 'pagedown'
                        # Unknown escape sequence - ignore it
                        return None
                    else:
                        # Incomplete escape sequence ESC[ without continuation
                        # This shouldn't happen with real terminals, ignore it
                        return None
                else:
                    # ESC followed by something other than '['
                    # Could be Alt+key combination, but for now treat as standalone ESC
                    return 'esc'
            else:
                # Timeout waiting for data after ESC
                # This means it's a standalone ESC key, not an escape sequence
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
