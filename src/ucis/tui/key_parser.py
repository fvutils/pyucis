"""
Key input parser for TUI - buffered approach to prevent fragmentation.

Reads all available data after select(), processes buffer completely.
Only waits with select() if sequence ends with ESC (ambiguous case).
"""
from typing import Optional, Callable
import select


class KeyParser:
    """Parse raw terminal input into logical key names using buffered reading."""
    
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
        self.buffer = ""  # Buffer for unprocessed input
    
    def parse_key(self) -> Optional[str]:
        """
        Parse next key from input.
        
        Strategy:
        1. Check if data available with select (with small timeout or blocking)
        2. Read ALL available data at once into buffer
        3. Process buffer
        4. Only use select with delay if sequence ends with ESC (ambiguous)
        
        Returns:
            Key name string ('up', 'down', 'esc', 'enter', etc.) or None for ignored sequences
        """
        # If buffer is empty, read available data
        if not self.buffer:
            # Check if data is available (with small timeout to not busy-loop)
            # For real terminal in raw mode, data arrives when user presses key
            if not self.select_fn(0.1):  # Wait up to 100ms for key press
                return None
            
            # Data is available - read ALL of it at once (not just 1 char!)
            data = self.read_fn(100)
            if not data:
                return None
            self.buffer = data
        
        # Process buffer
        return self._parse_from_buffer()
    
    def _parse_from_buffer(self) -> Optional[str]:
        """Parse next key from the internal buffer."""
        if not self.buffer:
            return None
        
        # Handle escape sequences
        if self.buffer[0] == '\x1b':
            # Check for complete ESC[ sequences
            if len(self.buffer) >= 3 and self.buffer[1] == '[':
                ch3 = self.buffer[2]
                
                # Arrow keys, Home, End
                if ch3 == 'A':
                    self.buffer = self.buffer[3:]
                    return 'up'
                elif ch3 == 'B':
                    self.buffer = self.buffer[3:]
                    return 'down'
                elif ch3 == 'C':
                    self.buffer = self.buffer[3:]
                    return 'right'
                elif ch3 == 'D':
                    self.buffer = self.buffer[3:]
                    return 'left'
                elif ch3 == 'H':
                    self.buffer = self.buffer[3:]
                    return 'home'
                elif ch3 == 'F':
                    self.buffer = self.buffer[3:]
                    return 'end'
                
                # Page Up/Down (ESC[5~ or ESC[6~)
                elif ch3 in ['5', '6']:
                    if len(self.buffer) >= 4 and self.buffer[3] == '~':
                        result = 'pageup' if ch3 == '5' else 'pagedown'
                        self.buffer = self.buffer[4:]
                        return result
                    # Incomplete sequence ESC[5 or ESC[6 without ~
                    # Wait to see if ~ arrives
                    if self.select_fn(0.2):
                        more = self.read_fn(10)
                        if more:
                            self.buffer += more
                            return self._parse_from_buffer()
                    # Timeout - incomplete, discard
                    self.buffer = ""
                    return None
            
            # Incomplete ESC[ without third character
            elif len(self.buffer) == 2 and self.buffer[1] == '[':
                # Wait for third character
                if self.select_fn(0.2):
                    more = self.read_fn(10)
                    if more:
                        self.buffer += more
                        return self._parse_from_buffer()
                # Timeout - incomplete, discard
                self.buffer = ""
                return None
            
            # Buffer ends with ESC - AMBIGUOUS CASE
            # Could be standalone ESC or start of escape sequence
            elif len(self.buffer) == 1:
                # Only case where we wait with delay
                if self.select_fn(0.2):
                    # More data coming - it's an escape sequence
                    more = self.read_fn(100)
                    if more:
                        self.buffer += more
                        return self._parse_from_buffer()
                
                # Timeout - it's a standalone ESC key
                self.buffer = self.buffer[1:]
                return 'esc'
            
            # ESC followed by something other than '[' or lone ESC
            # Treat as standalone ESC and process rest later
            else:
                self.buffer = self.buffer[1:]
                return 'esc'
        
        # Special characters
        ch = self.buffer[0]
        self.buffer = self.buffer[1:]
        
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

