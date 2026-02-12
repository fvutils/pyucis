"""
Tests for HTML formatter
"""
import pytest
import tempfile
import os
from io import StringIO
from ucis.mem.mem_factory import MemFactory
from ucis.formatters.format_html import HtmlFormatter
from ucis.source_info import SourceInfo
from ucis import UCIS_OTHER, UCIS_DU_MODULE


class TestHtmlFormatter:
    """Test HTML formatter functionality."""
    
    def test_basic_html_generation(self):
        """Test basic HTML report generation."""
        # Create a simple UCIS database
        db = MemFactory.create()
        
        # Create a simple scope with coverage
        scope = db.createScope("top", None, 1, UCIS_OTHER, UCIS_DU_MODULE, 0)
        
        # Generate HTML
        formatter = HtmlFormatter(include_source=False, compress=False)
        output = StringIO()
        formatter.format(db, output)
        
        html = output.getvalue()
        
        # Verify HTML structure
        assert '<!DOCTYPE html>' in html
        assert '<html' in html
        assert '<head>' in html
        assert '<body>' in html
        assert 'UCIS Coverage Report' in html
        assert 'coverage-data' in html
        
    def test_metadata_extraction(self):
        """Test metadata extraction from database."""
        db = MemFactory.create()
        
        formatter = HtmlFormatter(compress=False)
        output = StringIO()
        formatter.format(db, output)
        
        html = output.getvalue()
        
        # Check for metadata presence
        assert 'metadata' in html
        assert 'ucis_version' in html
        assert 'generator' in html
        assert 'pyucis' in html
        
    def test_summary_calculation(self):
        """Test coverage summary calculation."""
        db = MemFactory.create()
        
        # Create scope
        scope = db.createScope("top", None, 1, UCIS_OTHER, UCIS_DU_MODULE, 0)
        
        formatter = HtmlFormatter(compress=False)
        output = StringIO()
        formatter.format(db, output)
        
        html = output.getvalue()
        
        # Verify summary data is present
        assert 'summary' in html
        assert 'total_items' in html
        assert 'covered_items' in html
        assert 'uncovered_items' in html
        
    def test_scope_hierarchy_extraction(self):
        """Test extraction of scope hierarchy."""
        db = MemFactory.create()
        
        # Create hierarchy
        top = db.createScope("top", None, 1, UCIS_OTHER, UCIS_DU_MODULE, 0)
        
        formatter = HtmlFormatter(compress=False)
        output = StringIO()
        formatter.format(db, output)
        
        html = output.getvalue()
        
        # Verify scopes section is present
        assert 'scopes' in html
        
    def test_compress_option(self):
        """Test JSON compression option."""
        db = MemFactory.create()
        scope = db.createScope("top", None, 1, UCIS_OTHER, UCIS_DU_MODULE, 0)
        
        # Test with compression
        formatter_compressed = HtmlFormatter(compress=True)
        output_compressed = StringIO()
        formatter_compressed.format(db, output_compressed)
        html_compressed = output_compressed.getvalue()
        
        # Test without compression
        formatter_uncompressed = HtmlFormatter(compress=False)
        output_uncompressed = StringIO()
        formatter_uncompressed.format(db, output_uncompressed)
        html_uncompressed = output_uncompressed.getvalue()
        
        # Compressed version should have data-compressed="true"
        assert 'data-compressed="true"' in html_compressed
        assert 'data-compressed="false"' in html_uncompressed
        
    def test_file_output(self):
        """Test writing to actual file."""
        db = MemFactory.create()
        scope = db.createScope("top", None, 1, UCIS_OTHER, UCIS_DU_MODULE, 0)
        
        # Write to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            temp_path = f.name
            formatter = HtmlFormatter(compress=False)
            formatter.format(db, f)
        
        try:
            # Verify file was created and has content
            assert os.path.exists(temp_path)
            
            with open(temp_path, 'r') as f:
                html = f.read()
                assert '<!DOCTYPE html>' in html
                assert 'UCIS Coverage Report' in html
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_cover_type_names(self):
        """Test cover type name conversion."""
        from ucis.cover_type_t import CoverTypeT
        
        formatter = HtmlFormatter()
        
        assert formatter._get_cover_type_name(CoverTypeT.STMTBIN) == 'line'
        assert formatter._get_cover_type_name(CoverTypeT.BRANCHBIN) == 'branch'
        assert formatter._get_cover_type_name(CoverTypeT.TOGGLEBIN) == 'toggle'
        assert formatter._get_cover_type_name(CoverTypeT.CVGBIN) == 'functional'
    
    def test_language_detection(self):
        """Test source language detection from file extensions."""
        formatter = HtmlFormatter()
        
        assert formatter._detect_language('file.v') == 'verilog'
        assert formatter._detect_language('file.sv') == 'systemverilog'
        assert formatter._detect_language('file.vhd') == 'vhdl'
        assert formatter._detect_language('file.vhdl') == 'vhdl'
        assert formatter._detect_language('file.c') == 'c'
        assert formatter._detect_language('file.cpp') == 'cpp'
        assert formatter._detect_language('file.xyz') == 'unknown'
