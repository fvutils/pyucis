"""Parser for Verilator SystemC::Coverage-3 format."""

import re
from typing import List, Optional, Dict
from pathlib import Path
from .vlt_coverage_item import VltCoverageItem


class VltParser:
    """Parser for Verilator coverage .dat files."""
    
    # Known keys in Verilator coverage format
    KNOWN_KEYS = ['f', 'l', 'n', 't', 'page', 'o', 'h', 'bin', 'S']
    
    def __init__(self):
        self.items: List[VltCoverageItem] = []
    
    def parse_file(self, filename: str) -> List[VltCoverageItem]:
        """Parse a Verilator coverage .dat file.
        
        Args:
            filename: Path to the .dat file
            
        Returns:
            List of coverage items
        """
        self.items = []
        
        with open(filename, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip header
                if line.startswith('# SystemC::Coverage'):
                    continue
                
                # Skip empty lines
                if not line:
                    continue
                
                # Parse coverage line
                item = self.parse_line(line)
                if item:
                    self.items.append(item)
                else:
                    print(f"Warning: Failed to parse line {line_num}: {line}")
        
        return self.items
    
    def parse_line(self, line: str) -> Optional[VltCoverageItem]:
        """Parse a single coverage line.
        
        Format: C 'compact_key_value_pairs' hit_count
        Example: C 'ftest.vl19n4tlinepagev_lineht' 1
        
        Args:
            line: Coverage line to parse
            
        Returns:
            VltCoverageItem or None if parsing fails
        """
        # Match pattern: C 'content' number
        match = re.match(r"C\s+'([^']*)'\s+(\d+)", line)
        if not match:
            return None
        
        compact_str = match.group(1)
        hit_count = int(match.group(2))
        
        # Decode compact string
        attrs = self.decode_compact_string(compact_str)
        
        # Helper to safely parse integers
        def safe_int(value_str, default=0):
            if value_str and value_str.isdigit():
                return int(value_str)
            return default
        
        # Create coverage item
        item = VltCoverageItem(
            filename=attrs.get('f', ''),
            lineno=safe_int(attrs.get('l', ''), 0),
            colno=safe_int(attrs.get('n', ''), 0),
            coverage_type=attrs.get('t', ''),
            page=attrs.get('page', ''),
            hierarchy=attrs.get('h', ''),
            comment=attrs.get('o', ''),
            bin_name=attrs.get('bin', ''),
            hit_count=hit_count,
            attributes=attrs,
            line_range=attrs.get('S', '')
        )
        
        return item
    
    def decode_compact_string(self, compact: str) -> Dict[str, str]:
        """Decode Verilator's compact key-value string.
        
        Verilator uses embedded ASCII control characters as delimiters:
        - \001 (ASCII 1): Start marker / key separator
        - \002 (ASCII 2): Key-value separator
        
        Format: \001key\002value\001key\002value\001...
        
        Example:
            '\001f\002test.v\001l\00219\001t\002line\001' 
            -> {'f': 'test.v', 'l': '19', 't': 'line'}
        
        Args:
            compact: Compact string from coverage file
            
        Returns:
            Dictionary of key-value pairs
        """
        result = {}
        pos = 0
        length = len(compact)
        
        while pos < length:
            # Look for start marker (\001)
            if compact[pos] == '\001':
                pos += 1  # Skip the marker
                
                # Extract key (until \002)
                key_start = pos
                while pos < length and compact[pos] != '\002':
                    pos += 1
                
                if pos >= length:
                    break  # Incomplete key
                
                key = compact[key_start:pos]
                pos += 1  # Skip the \002 separator
                
                # Extract value (until next \001 or end of string)
                value_start = pos
                while pos < length and compact[pos] != '\001':
                    pos += 1
                
                value = compact[value_start:pos]
                result[key] = value
                
                # pos is now at next \001 or end of string
            else:
                # Unexpected character, skip it
                pos += 1
        
        return result


def parse_verilator_coverage(filename: str) -> List[VltCoverageItem]:
    """Convenience function to parse a Verilator coverage file.
    
    Args:
        filename: Path to the .dat file
        
    Returns:
        List of coverage items
    """
    parser = VltParser()
    return parser.parse_file(filename)
