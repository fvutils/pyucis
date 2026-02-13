#!/usr/bin/env python3
"""
Test the TUI by loading a database and printing info.
Does not require interactive terminal.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_tui(db_path):
    """Test TUI functionality without running the interactive loop."""
    from ucis.tui.models.coverage_model import CoverageModel
    from ucis.tui.views.dashboard_view import DashboardView
    from ucis.tui.views.hierarchy_view import HierarchyView
    from ucis.tui.views.gaps_view import GapsView
    from ucis.tui.views.hotspots_view import HotspotsView
    from ucis.tui.views.metrics_view import MetricsView
    
    print("=" * 70)
    print("PyUCIS TUI - Functionality Test")
    print("=" * 70)
    print()
    
    # Load coverage model
    print(f"Loading database: {db_path}")
    model = CoverageModel(db_path)
    print("✓ Coverage model loaded")
    
    # Get summary
    summary = model.get_summary()
    print()
    print("Database Summary:")
    print(f"  Covergroups: {summary['covergroups']}")
    print(f"  Coverpoints: {summary['coverpoints']}")
    print(f"  Total bins: {summary['total_bins']}")
    print(f"  Covered bins: {summary['covered_bins']}")
    print(f"  Overall coverage: {summary['overall_coverage']:.1f}%")
    
    # Test each view can be created
    print()
    print("Testing views...")
    
    class MockApp:
        def __init__(self):
            self.coverage_model = model
    
    app = MockApp()
    
    views = [
        ("Dashboard", DashboardView),
        ("Hierarchy", HierarchyView),
        ("Gaps", GapsView),
        ("Hotspots", HotspotsView),
        ("Metrics", MetricsView),
    ]
    
    for name, view_class in views:
        try:
            view = view_class(app)
            print(f"  ✓ {name} view initialized")
        except Exception as e:
            print(f"  ✗ {name} view failed: {e}")
            import traceback
            traceback.print_exc()
    
    print()
    print("=" * 70)
    print("Test Complete!")
    print()
    print("To run the interactive TUI:")
    print(f"  pyucis view {db_path}")
    print()
    print("Or:")
    print(f"  PYTHONPATH=src python -m ucis.tui {db_path}")
    print("=" * 70)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_tui.py <database.xml>")
        print()
        print("Creating demo database...")
        # Create a demo database
        from scripts.demo_tui import create_demo_database
        db_path = create_demo_database()
    else:
        db_path = sys.argv[1]
    
    test_tui(db_path)
