"""
Unit tests for TUI key parser.

Tests escape sequence handling, timing issues, and edge cases.
"""
import pytest
from ucis.tui.key_parser import KeyParser


class MockInput:
    """Mock input stream for testing."""
    
    def __init__(self, data: str):
        """
        Initialize mock input.
        
        Args:
            data: String of characters to return from reads
        """
        self.data = data
        self.pos = 0
        self.available_at = {}  # position -> bool (simulate select timing)
    
    def read(self, n: int) -> str:
        """Read n characters from mock input."""
        result = self.data[self.pos:self.pos + n]
        self.pos += n
        return result
    
    def set_available_at(self, pos: int, available: bool):
        """Set whether data is 'available' (for select) at a given position."""
        self.available_at[pos] = available
    
    def select(self, timeout: float) -> bool:
        """Mock select - return whether more data is available."""
        # Check if we have explicit availability setting for this position
        if self.pos in self.available_at:
            return self.available_at[self.pos]
        # Default: available if there's more data
        return self.pos < len(self.data)


def test_standalone_esc():
    """Test standalone ESC key press."""
    mock = MockInput('\x1b')
    mock.set_available_at(1, False)  # No more data after ESC
    
    parser = KeyParser(mock.read, mock.select)
    assert parser.parse_key() == 'esc'


def test_arrow_down():
    """Test DOWN arrow key (ESC[B)."""
    mock = MockInput('\x1b[B')
    
    parser = KeyParser(mock.read, mock.select)
    assert parser.parse_key() == 'down'


def test_arrow_up():
    """Test UP arrow key (ESC[A)."""
    mock = MockInput('\x1b[A')
    
    parser = KeyParser(mock.read, mock.select)
    assert parser.parse_key() == 'up'


def test_arrow_right():
    """Test RIGHT arrow key (ESC[C)."""
    mock = MockInput('\x1b[C')
    
    parser = KeyParser(mock.read, mock.select)
    assert parser.parse_key() == 'right'


def test_arrow_left():
    """Test LEFT arrow key (ESC[D)."""
    mock = MockInput('\x1b[D')
    
    parser = KeyParser(mock.read, mock.select)
    assert parser.parse_key() == 'left'


def test_page_up():
    """Test Page Up key (ESC[5~)."""
    mock = MockInput('\x1b[5~')
    
    parser = KeyParser(mock.read, mock.select)
    assert parser.parse_key() == 'pageup'


def test_page_down():
    """Test Page Down key (ESC[6~)."""
    mock = MockInput('\x1b[6~')
    
    parser = KeyParser(mock.read, mock.select)
    assert parser.parse_key() == 'pagedown'


def test_home():
    """Test Home key (ESC[H)."""
    mock = MockInput('\x1b[H')
    
    parser = KeyParser(mock.read, mock.select)
    assert parser.parse_key() == 'home'


def test_end():
    """Test End key (ESC[F)."""
    mock = MockInput('\x1b[F')
    
    parser = KeyParser(mock.read, mock.select)
    assert parser.parse_key() == 'end'


def test_enter():
    """Test Enter key."""
    mock1 = MockInput('\r')
    parser1 = KeyParser(mock1.read, mock1.select)
    assert parser1.parse_key() == 'enter'
    
    mock2 = MockInput('\n')
    parser2 = KeyParser(mock2.read, mock2.select)
    assert parser2.parse_key() == 'enter'


def test_regular_character():
    """Test regular character."""
    mock = MockInput('a')
    parser = KeyParser(mock.read, mock.select)
    assert parser.parse_key() == 'a'


def test_space():
    """Test space key."""
    mock = MockInput(' ')
    parser = KeyParser(mock.read, mock.select)
    assert parser.parse_key() == 'space'


def test_ctrl_c():
    """Test Ctrl+C."""
    mock = MockInput('\x03')
    parser = KeyParser(mock.read, mock.select)
    assert parser.parse_key() == 'ctrl+c'


def test_incomplete_escape_sequence_no_bracket():
    """Test ESC followed by timeout (no bracket) - should be standalone ESC."""
    mock = MockInput('\x1b')
    # Simulate: ESC pressed, then timeout (no more data)
    mock.set_available_at(1, False)
    
    parser = KeyParser(mock.read, mock.select)
    assert parser.parse_key() == 'esc'


def test_incomplete_escape_sequence_with_bracket():
    """Test ESC[ followed by timeout - should return None (ignore)."""
    mock = MockInput('\x1b[')
    # Simulate: ESC and [ arrive, but then timeout
    mock.set_available_at(2, False)
    
    parser = KeyParser(mock.read, mock.select)
    result = parser.parse_key()
    assert result is None  # Should ignore incomplete sequence


def test_esc_then_separate_down_arrow():
    """Test ESC key press, THEN separate DOWN arrow - simulates user scenario."""
    # First parse: standalone ESC
    mock1 = MockInput('\x1b')
    mock1.set_available_at(1, False)  # No more data after ESC
    parser1 = KeyParser(mock1.read, mock1.select)
    assert parser1.parse_key() == 'esc'
    
    # Second parse: DOWN arrow
    mock2 = MockInput('\x1b[B')
    parser2 = KeyParser(mock2.read, mock2.select)
    assert parser2.parse_key() == 'down'


def test_delayed_arrow_sequence():
    """Test arrow key that arrives with delay between ESC and [."""
    mock = MockInput('\x1b[B')
    # Simulate timing: ESC arrives, [ arrives after delay
    # If this returns 'esc', that's the bug!
    
    parser = KeyParser(mock.read, mock.select)
    result = parser.parse_key()
    
    # Should be 'down', not 'esc'
    assert result == 'down'


def test_very_delayed_arrow_sequence():
    """Test arrow key with buffered reading - should work even with delays."""
    mock = MockInput('\x1b[B')
    # Simulate: ESC and [ arrive, then B arrives after delay
    mock.set_available_at(2, False)  # B not immediately available
    
    parser = KeyParser(mock.read, mock.select)
    result = parser.parse_key()
    
    # With buffered reading, we read ESC[ together, then wait for B
    # Should successfully return 'down'
    assert result == 'down'


def test_sequence_with_all_data_available():
    """Test that complete sequences work when all data is immediately available."""
    sequences = [
        ('\x1b[A', 'up'),
        ('\x1b[B', 'down'),
        ('\x1b[C', 'right'),
        ('\x1b[D', 'left'),
        ('\x1b[H', 'home'),
        ('\x1b[F', 'end'),
        ('\x1b[5~', 'pageup'),
        ('\x1b[6~', 'pagedown'),
    ]
    
    for seq, expected in sequences:
        mock = MockInput(seq)
        parser = KeyParser(mock.read, mock.select)
        result = parser.parse_key()
        assert result == expected, f"Sequence {repr(seq)} should return {expected}, got {result}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
