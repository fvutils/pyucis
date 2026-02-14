"""
Test TUI code coverage support.
"""
import pytest
from pathlib import Path
from ucis.tui.models.coverage_model import CoverageModel
from ucis.cover_type_t import CoverTypeT


def test_coverage_model_get_coverage_types():
    """Test getting list of coverage types from database."""
    # Use the Verilator example database
    db_path = Path(__file__).parent.parent / "examples" / "verilator" / "coverage" / "coverage.cdb"
    
    if not db_path.exists():
        pytest.skip(f"Test database not found: {db_path}")
    
    model = CoverageModel(str(db_path))
    
    # Get coverage types
    types = model.get_coverage_types()
    
    # Should have line, branch, and toggle coverage
    assert len(types) >= 3
    assert CoverTypeT.STMTBIN in types
    assert CoverTypeT.BRANCHBIN in types
    assert CoverTypeT.TOGGLEBIN in types
    
    model.close()


def test_coverage_model_get_code_coverage_summary():
    """Test getting code coverage summary."""
    db_path = Path(__file__).parent.parent / "examples" / "verilator" / "coverage" / "coverage.cdb"
    
    if not db_path.exists():
        pytest.skip(f"Test database not found: {db_path}")
    
    model = CoverageModel(str(db_path))
    
    # Get code coverage summary
    summary = model.get_code_coverage_summary()
    
    # Should have line coverage
    assert summary['line']['total'] > 0
    assert summary['line']['covered'] > 0
    assert 0 <= summary['line']['coverage'] <= 100
    
    # Should have branch coverage
    assert summary['branch']['total'] > 0
    assert summary['branch']['covered'] > 0
    assert 0 <= summary['branch']['coverage'] <= 100
    
    # Should have toggle coverage
    assert summary['toggle']['total'] > 0
    assert summary['toggle']['covered'] > 0
    assert 0 <= summary['toggle']['coverage'] <= 100
    
    model.close()


def test_coverage_model_get_coverage_by_type():
    """Test getting coverage for specific type."""
    db_path = Path(__file__).parent.parent / "examples" / "verilator" / "coverage" / "coverage.cdb"
    
    if not db_path.exists():
        pytest.skip(f"Test database not found: {db_path}")
    
    model = CoverageModel(str(db_path))
    
    # Get line coverage
    line_cov = model.get_coverage_by_type(CoverTypeT.STMTBIN)
    assert line_cov['type'] == CoverTypeT.STMTBIN
    assert line_cov['total'] > 0
    assert line_cov['covered'] > 0
    assert 0 <= line_cov['coverage'] <= 100
    
    # Get branch coverage
    branch_cov = model.get_coverage_by_type(CoverTypeT.BRANCHBIN)
    assert branch_cov['type'] == CoverTypeT.BRANCHBIN
    assert branch_cov['total'] > 0
    assert branch_cov['covered'] > 0
    assert 0 <= branch_cov['coverage'] <= 100
    
    model.close()


def test_coverage_model_caching():
    """Test that coverage queries are cached."""
    db_path = Path(__file__).parent.parent / "examples" / "verilator" / "coverage" / "coverage.cdb"
    
    if not db_path.exists():
        pytest.skip(f"Test database not found: {db_path}")
    
    model = CoverageModel(str(db_path))
    
    # First call populates cache
    types1 = model.get_coverage_types()
    summary1 = model.get_code_coverage_summary()
    
    # Second call should use cache (same object)
    types2 = model.get_coverage_types()
    summary2 = model.get_code_coverage_summary()
    
    assert types1 is types2
    assert summary1 is summary2
    
    model.close()


def test_code_coverage_view_file_detail():
    """Test code coverage view file detail functionality."""
    db_path = Path(__file__).parent.parent / "examples" / "verilator" / "coverage" / "coverage.cdb"
    
    if not db_path.exists():
        pytest.skip(f"Test database not found: {db_path}")
    
    # Create model
    model = CoverageModel(str(db_path))
    
    # Mock app
    class MockApp:
        def __init__(self, coverage_model):
            self.coverage_model = coverage_model
    
    app = MockApp(model)
    
    # Import view
    from ucis.tui.views.code_coverage_view import CodeCoverageView
    
    # Create view
    view = CodeCoverageView(app)
    
    # Should have loaded files
    assert len(view.file_coverage) > 0
    
    # Select first file
    view.selected_file = view.file_coverage[0]
    view.view_mode = 'detail'
    
    # Load source
    view._load_source_file()
    
    # Should have source lines or coverage data
    assert len(view.source_lines) > 0 or len(view.selected_file.lines) > 0
    
    # Test rendering detail view
    layout = view._render_file_detail()
    assert layout is not None
    
    # Test scrolling
    initial_offset = view.detail_scroll_offset
    view._handle_detail_keys('down')
    assert view.detail_scroll_offset >= initial_offset
    
    # Test return to list
    view._handle_detail_keys('esc')
    assert view.view_mode == 'list'
    assert view.selected_file is None
    
    model.close()
