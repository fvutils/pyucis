"""Unit tests for Verilator coverage parser."""

import pytest
import sys
import os

# Add source to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))

from ucis.vltcov.vlt_parser import VltParser
from ucis.vltcov.vlt_coverage_item import VltCoverageItem


class TestVltParser:
    """Test VltParser class."""
    
    def test_parser_initialization(self):
        """Test parser can be instantiated."""
        parser = VltParser()
        assert parser is not None
        assert parser.items == []
    
    def test_decode_compact_string_simple(self):
        """Test decoding simple compact string."""
        parser = VltParser()
        
        # Simple example: type=funccov, file=test.v, line=19
        compact = '\x01t\x02funccov\x01f\x02test.v\x01l\x0219\x01'
        result = parser.decode_compact_string(compact)
        
        assert result['t'] == 'funccov'
        assert result['f'] == 'test.v'
        assert result['l'] == '19'
    
    def test_decode_compact_string_functional_coverage(self):
        """Test decoding functional coverage compact string."""
        parser = VltParser()
        
        # Functional coverage with covergroup and bin
        compact = '\x01t\x02funccov\x01page\x02v_funccov/cg1\x01f\x02test.v\x01l\x0219\x01bin\x02low\x01h\x02cg1.cp\x01'
        result = parser.decode_compact_string(compact)
        
        assert result['t'] == 'funccov'
        assert result['page'] == 'v_funccov/cg1'
        assert result['f'] == 'test.v'
        assert result['l'] == '19'
        assert result['bin'] == 'low'
        assert result['h'] == 'cg1.cp'
    
    def test_decode_compact_string_with_hierarchy(self):
        """Test decoding with hierarchy path."""
        parser = VltParser()
        
        compact = '\x01t\x02line\x01f\x02test.v\x01l\x02100\x01h\x02top.mod1.mod2\x01'
        result = parser.decode_compact_string(compact)
        
        assert result['t'] == 'line'
        assert result['h'] == 'top.mod1.mod2'
    
    def test_decode_compact_string_empty(self):
        """Test decoding empty string."""
        parser = VltParser()
        result = parser.decode_compact_string('')
        assert result == {}
    
    def test_parse_line_valid(self):
        """Test parsing valid coverage line."""
        parser = VltParser()
        
        line = "C '\x01t\x02line\x01f\x02test.v\x01l\x0242\x01' 10"
        item = parser.parse_line(line)
        
        assert item is not None
        assert item.coverage_type == 'line'
        assert item.filename == 'test.v'
        assert item.lineno == 42
        assert item.hit_count == 10
    
    def test_parse_line_functional_coverage(self):
        """Test parsing functional coverage line."""
        parser = VltParser()
        
        line = "C '\x01t\x02funccov\x01page\x02v_funccov/cg1\x01bin\x02bin_low\x01f\x02test.v\x01l\x0119\x01h\x02cg1.cp.bin_low\x01' 42"
        item = parser.parse_line(line)
        
        assert item is not None
        assert item.is_functional_coverage
        assert item.covergroup_name == 'cg1'
        assert item.bin_name == 'bin_low'
        assert item.hit_count == 42
    
    def test_parse_line_zero_hits(self):
        """Test parsing line with zero hits."""
        parser = VltParser()
        
        line = "C '\x01t\x02line\x01f\x02test.v\x01l\x0110\x01' 0"
        item = parser.parse_line(line)
        
        assert item is not None
        assert item.hit_count == 0
    
    def test_parse_line_invalid_format(self):
        """Test parsing invalid line format."""
        parser = VltParser()
        
        # Missing quotes
        line = "C test 10"
        item = parser.parse_line(line)
        assert item is None
        
        # Missing C prefix
        line = "'test' 10"
        item = parser.parse_line(line)
        assert item is None
    
    def test_parse_line_header(self):
        """Test parsing header line."""
        parser = VltParser()
        
        line = "# SystemC::Coverage-3"
        item = parser.parse_line(line)
        assert item is None


class TestVltCoverageItem:
    """Test VltCoverageItem class."""
    
    def test_item_initialization(self):
        """Test item can be created."""
        item = VltCoverageItem(
            filename='test.v',
            lineno=10,
            coverage_type='line',
            hit_count=5
        )
        
        assert item.filename == 'test.v'
        assert item.lineno == 10
        assert item.coverage_type == 'line'
        assert item.hit_count == 5
    
    def test_is_functional_coverage(self):
        """Test functional coverage detection."""
        item = VltCoverageItem(page='v_funccov/cg1')
        assert item.is_functional_coverage
        
        item = VltCoverageItem(page='v_line')
        assert not item.is_functional_coverage
    
    def test_is_line_coverage(self):
        """Test line coverage detection."""
        item = VltCoverageItem(coverage_type='line')
        assert item.is_line_coverage
        
        item = VltCoverageItem(page='v_line')
        assert item.is_line_coverage
        
        item = VltCoverageItem(coverage_type='branch')
        assert not item.is_line_coverage
    
    def test_is_branch_coverage(self):
        """Test branch coverage detection."""
        item = VltCoverageItem(coverage_type='branch')
        assert item.is_branch_coverage
        
        item = VltCoverageItem(page='v_branch')
        assert item.is_branch_coverage
    
    def test_is_toggle_coverage(self):
        """Test toggle coverage detection."""
        item = VltCoverageItem(coverage_type='toggle')
        assert item.is_toggle_coverage
        
        item = VltCoverageItem(page='v_toggle')
        assert item.is_toggle_coverage
    
    def test_covergroup_name_extraction(self):
        """Test covergroup name extraction."""
        item = VltCoverageItem(page='v_funccov/my_covergroup')
        assert item.covergroup_name == 'my_covergroup'
        
        item = VltCoverageItem(page='v_line')
        assert item.covergroup_name is None
    
    def test_repr(self):
        """Test string representation."""
        item = VltCoverageItem(
            filename='test.v',
            lineno=10,
            coverage_type='line',
            hit_count=5
        )
        
        repr_str = repr(item)
        assert 'test.v' in repr_str
        assert '10' in repr_str
        assert 'line' in repr_str
        assert '5' in repr_str


class TestVltParserWithFile:
    """Test parser with actual file data."""
    
    def test_parse_file_not_found(self):
        """Test parsing non-existent file."""
        parser = VltParser()
        with pytest.raises(FileNotFoundError):
            parser.parse_file('/nonexistent/file.dat')
    
    def test_parse_file_with_test_data(self, tmp_path):
        """Test parsing file with test data."""
        # Create test file
        test_file = tmp_path / "test.dat"
        test_file.write_text("""# SystemC::Coverage-3
C '\x01t\x02line\x01f\x02test.v\x01l\x0210\x01' 5
C '\x01t\x02line\x01f\x02test.v\x01l\x0220\x01' 0
C '\x01t\x02funccov\x01page\x02v_funccov/cg1\x01bin\x02low\x01' 42
""")
        
        parser = VltParser()
        items = parser.parse_file(str(test_file))
        
        assert len(items) == 3
        
        # Check first item
        assert items[0].coverage_type == 'line'
        assert items[0].lineno == 10
        assert items[0].hit_count == 5
        
        # Check second item
        assert items[1].hit_count == 0
        
        # Check functional coverage item
        assert items[2].is_functional_coverage
        assert items[2].bin_name == 'low'
        assert items[2].hit_count == 42
    
    def test_parse_file_empty(self, tmp_path):
        """Test parsing empty file."""
        test_file = tmp_path / "empty.dat"
        test_file.write_text("# SystemC::Coverage-3\n")
        
        parser = VltParser()
        items = parser.parse_file(str(test_file))
        
        assert len(items) == 0
    
    def test_parse_file_with_comments(self, tmp_path):
        """Test file with comments and blank lines."""
        test_file = tmp_path / "test.dat"
        test_file.write_text("""# SystemC::Coverage-3
# This is a comment

C '\x01t\x02line\x01f\x02test.v\x01l\x0110\x01' 5

# Another comment
C '\x01t\x02line\x01f\x02test.v\x01l\x0220\x01' 3
""")
        
        parser = VltParser()
        items = parser.parse_file(str(test_file))
        
        # Should only parse actual coverage lines
        assert len(items) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
