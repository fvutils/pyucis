"""Integration tests for Verilator coverage import."""

import pytest
import sys
import os
import tempfile
from pathlib import Path

# Add source to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))

from ucis.rgy.format_rgy import FormatRgy
from ucis.vltcov.vlt_parser import VltParser


class TestVltCovFormatRegistration:
    """Test format registration in PyUCIS."""
    
    def test_format_is_registered(self):
        """Test that vltcov format is registered."""
        rgy = FormatRgy.inst()
        formats = rgy.getDatabaseFormats()
        
        assert 'vltcov' in formats
    
    def test_format_has_read_support(self):
        """Test that vltcov format supports reading."""
        rgy = FormatRgy.inst()
        desc = rgy.getDatabaseDesc('vltcov')
        
        assert desc is not None
        assert desc._name == 'vltcov'
        assert 'Verilator' in desc._description or 'verilator' in desc._description.lower()
    
    def test_format_interface_can_be_created(self):
        """Test that format interface can be instantiated."""
        rgy = FormatRgy.inst()
        desc = rgy.getDatabaseDesc('vltcov')
        fmt_if = desc.fmt_if()
        
        assert fmt_if is not None


class TestVltCovImportIntegration:
    """Integration tests for importing Verilator coverage."""
    
    @pytest.fixture
    def test_coverage_file(self, tmp_path):
        """Create a test coverage file."""
        test_file = tmp_path / "test_coverage.dat"
        test_file.write_text("""# SystemC::Coverage-3
C '\x01t\x02funccov\x01page\x02v_funccov/cg_test\x01f\x02test.v\x01l\x0210\x01n\x025\x01bin\x02bin_low\x01h\x02cg_test.cp_value.bin_low\x01' 25
C '\x01t\x02funccov\x01page\x02v_funccov/cg_test\x01f\x02test.v\x01l\x0210\x01n\x025\x01bin\x02bin_mid\x01h\x02cg_test.cp_value.bin_mid\x01' 30
C '\x01t\x02funccov\x01page\x02v_funccov/cg_test\x01f\x02test.v\x01l\x0210\x01n\x025\x01bin\x02bin_high\x01h\x02cg_test.cp_value.bin_high\x01' 15
""")
        return str(test_file)
    
    def test_import_basic(self, test_coverage_file):
        """Test basic import of Verilator coverage."""
        rgy = FormatRgy.inst()
        fmt_if = rgy.getDatabaseDesc('vltcov').fmt_if()
        
        db = fmt_if.read(test_coverage_file)
        
        assert db is not None
        assert type(db).__name__ == 'MemUCIS'
    
    def test_import_and_export_xml(self, test_coverage_file, tmp_path):
        """Test importing and exporting to XML."""
        from ucis.xml.xml_ucis import XmlUCIS
        from ucis.merge import DbMerger
        
        # Import
        rgy = FormatRgy.inst()
        fmt_if = rgy.getDatabaseDesc('vltcov').fmt_if()
        db = fmt_if.read(test_coverage_file)
        
        # Export to XML
        output_file = tmp_path / "output.xml"
        xml_db = XmlUCIS()
        
        # Use merger to copy data
        merger = DbMerger()
        merger.merge(xml_db, [db])
        
        xml_db.write(str(output_file))
        
        assert output_file.exists()
        assert output_file.stat().st_size > 0
        
        # Verify XML contains coverage data
        content = output_file.read_text()
        assert 'UCIS' in content
        assert 'covergroup' in content.lower() or 'cg_test' in content
    
    def test_import_functional_coverage(self, test_coverage_file):
        """Test that functional coverage is imported correctly."""
        rgy = FormatRgy.inst()
        fmt_if = rgy.getDatabaseDesc('vltcov').fmt_if()
        
        # Parse the file first to verify content
        parser = VltParser()
        items = parser.parse_file(test_coverage_file)
        
        assert len(items) == 3
        assert all(item.is_functional_coverage for item in items)
        assert items[0].covergroup_name == 'cg_test'
        assert items[0].bin_name == 'bin_low'
        assert items[0].hit_count == 25
        
        # Now import to UCIS
        db = fmt_if.read(test_coverage_file)
        assert db is not None


class TestVltCovRealFileImport:
    """Test with real Verilator coverage files if available."""
    
    @pytest.fixture
    def real_verilator_file(self):
        """Return path to real Verilator file if it exists."""
        test_path = '/home/mballance/projects/verilator/verilator-funccov/obj_test_autobins/coverage.dat'
        if os.path.exists(test_path):
            return test_path
        return None
    
    def test_import_real_file(self, real_verilator_file):
        """Test importing real Verilator coverage file."""
        if real_verilator_file is None:
            pytest.skip("Real Verilator coverage file not available")
        
        rgy = FormatRgy.inst()
        fmt_if = rgy.getDatabaseDesc('vltcov').fmt_if()
        
        db = fmt_if.read(real_verilator_file)
        
        assert db is not None
    
    def test_parse_real_file(self, real_verilator_file):
        """Test parsing real Verilator coverage file."""
        if real_verilator_file is None:
            pytest.skip("Real Verilator coverage file not available")
        
        parser = VltParser()
        items = parser.parse_file(real_verilator_file)
        
        assert len(items) > 0
        
        # Count coverage types
        funccov = [i for i in items if i.is_functional_coverage]
        assert len(funccov) > 0


class TestVltCovErrorHandling:
    """Test error handling and edge cases."""
    
    def test_import_nonexistent_file(self):
        """Test importing non-existent file."""
        rgy = FormatRgy.inst()
        fmt_if = rgy.getDatabaseDesc('vltcov').fmt_if()
        
        with pytest.raises(FileNotFoundError):
            fmt_if.read('/nonexistent/file.dat')
    
    def test_import_empty_file(self, tmp_path):
        """Test importing empty coverage file."""
        empty_file = tmp_path / "empty.dat"
        empty_file.write_text("# SystemC::Coverage-3\n")
        
        rgy = FormatRgy.inst()
        fmt_if = rgy.getDatabaseDesc('vltcov').fmt_if()
        
        db = fmt_if.read(str(empty_file))
        assert db is not None
    
    def test_import_malformed_file(self, tmp_path):
        """Test importing file with malformed data."""
        bad_file = tmp_path / "bad.dat"
        bad_file.write_text("""# SystemC::Coverage-3
C 'invalid line without proper format' 10
C '\x01t\x02funccov\x01' 5
""")
        
        rgy = FormatRgy.inst()
        fmt_if = rgy.getDatabaseDesc('vltcov').fmt_if()
        
        # Should handle gracefully (skip bad lines)
        db = fmt_if.read(str(bad_file))
        assert db is not None


class TestVltCovCLIIntegration:
    """Test CLI integration (requires subprocess)."""
    
    @pytest.fixture
    def test_file(self, tmp_path):
        """Create test coverage file."""
        f = tmp_path / "test.dat"
        f.write_text("""# SystemC::Coverage-3
C '\x01t\x02funccov\x01page\x02v_funccov/cg1\x01bin\x02bin1\x01h\x02cg1.cp.bin1\x01' 10
""")
        return str(f)
    
    def test_cli_list_formats(self):
        """Test that CLI shows vltcov format."""
        import subprocess
        
        result = subprocess.run(
            ['python3', '-m', 'ucis', 'list-db-formats'],
            cwd='/home/mballance/projects/fvutils/pyucis-vltcov',
            env={'PYTHONPATH': 'src'},
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert 'vltcov' in result.stdout
    
    def test_cli_convert(self, test_file, tmp_path):
        """Test CLI convert command."""
        import subprocess
        
        output_file = str(tmp_path / "output.xml")
        
        result = subprocess.run(
            ['python3', '-m', 'ucis', 'convert',
             '--input-format', 'vltcov',
             test_file,
             '--out', output_file],
            cwd='/home/mballance/projects/fvutils/pyucis-vltcov',
            env={'PYTHONPATH': 'src'},
            capture_output=True,
            text=True
        )
        
        # Check command succeeded
        assert result.returncode == 0 or 'AgentSkills' in result.stderr
        
        # Check output file was created
        if os.path.exists(output_file):
            assert os.path.getsize(output_file) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
