"""
Integration tests for TUI navigation with real app components.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from ucis.tui.controller import TUIController
from ucis.tui.views.hierarchy_view import HierarchyView
from ucis.tui.app import TUIApp
import tempfile
import os


class MockApp:
    """Mock TUI app for basic testing."""
    
    def __init__(self):
        self.console = Mock()
        self.status_bar = Mock()
        self.coverage_model = Mock()
        self.controller = None
        
        # Mock coverage model methods
        self.coverage_model.get_coverage_summary.return_value = {
            'line': {'covered': 100, 'total': 200, 'percentage': 50.0},
            'branch': {'covered': 50, 'total': 100, 'percentage': 50.0},
        }
        self.coverage_model.get_top_level_scopes.return_value = [
            {'name': 'scope1', 'type': 'module', 'coverage': 50.0},
            {'name': 'scope2', 'type': 'module', 'coverage': 75.0},
            {'name': 'scope3', 'type': 'module', 'coverage': 25.0},
        ]
        
        # Mock db for HierarchyView
        mock_scope1 = Mock()
        mock_scope1.name = 'scope1'
        mock_scope1.get_type.return_value = 1  # Module type
        mock_scope1.get_coverage.return_value = 50.0
        mock_scope1.children.return_value = []
        
        mock_scope2 = Mock()
        mock_scope2.name = 'scope2'
        mock_scope2.get_type.return_value = 1
        mock_scope2.get_coverage.return_value = 75.0
        mock_scope2.children.return_value = []
        
        mock_scope3 = Mock()
        mock_scope3.name = 'scope3'
        mock_scope3.get_type.return_value = 1
        mock_scope3.get_coverage.return_value = 25.0
        mock_scope3.children.return_value = []
        
        mock_db = Mock()
        mock_db.scopes.return_value = [mock_scope1, mock_scope2, mock_scope3]
        self.coverage_model.db = mock_db


def test_hierarchy_navigation_after_page_switch():
    """
    Test that reproduces user's bug scenario:
    1. Start on dashboard (page 1)
    2. Press '2' to go to hierarchy (page 2)
    3. Press DOWN arrow
    4. Expected: Stay on page 2 with second item selected
    5. Bug: Goes back to dashboard (page 1)
    """
    # Create mock app and controller
    app = MockApp()
    controller = TUIController(app.coverage_model, on_quit=lambda: None)
    app.controller = controller
    
    # Create real hierarchy view
    hierarchy_view = HierarchyView(app)
    
    # Register views
    dashboard_view = Mock()
    dashboard_view.handle_key = Mock(return_value=False)
    dashboard_view.on_enter = Mock()
    dashboard_view.on_exit = Mock()
    
    controller.register_view("dashboard", dashboard_view)
    controller.register_view("hierarchy", hierarchy_view)
    
    # Step 1: Start on dashboard
    controller.switch_view("dashboard")
    state = controller.get_state_debug()
    assert state['current_view'] == 'dashboard', f"Should start on dashboard, got {state['current_view']}"
    
    # Step 2: Press '2' to go to hierarchy
    handled = controller.handle_key('2')
    state = controller.get_state_debug()
    assert state['current_view'] == 'hierarchy', f"After '2', should be on hierarchy, got {state['current_view']}"
    
    # Get initial selected node
    initial_node = hierarchy_view.selected_node
    
    # Step 3: Press DOWN arrow
    handled = controller.handle_key('down')
    state = controller.get_state_debug()
    
    # This is the critical assertion - we should still be on hierarchy
    assert state['current_view'] == 'hierarchy', \
        f"After DOWN on hierarchy, should stay on hierarchy, but got {state['current_view']}"
    
    # Additional checks - node should have changed
    new_node = hierarchy_view.selected_node
    assert new_node != initial_node, \
        f"After DOWN, selected_node should change from {initial_node} to different node"
    
    print("✓ Navigation test passed: DOWN arrow correctly stays on hierarchy page")


def test_complete_user_scenario():
    """
    Test the complete scenario user described:
    <2> ; <DOWN> should keep page 2 with second item selected
    """
    # Create mock app and controller
    app = MockApp()
    controller = TUIController(app.coverage_model, on_quit=lambda: None)
    app.controller = controller
    
    # Create real hierarchy view
    hierarchy_view = HierarchyView(app)
    
    # Register views
    dashboard_view = Mock()
    dashboard_view.handle_key = Mock(return_value=False)
    dashboard_view.on_enter = Mock()
    dashboard_view.on_exit = Mock()
    
    controller.register_view("dashboard", dashboard_view)
    controller.register_view("hierarchy", hierarchy_view)
    
    # Simulate key sequence: <2> ; <DOWN>
    controller.switch_view("dashboard")
    
    print("\n=== Starting navigation sequence ===")
    
    # Press '2'
    print("Pressing '2'...")
    controller.handle_key('2')
    state = controller.get_state_debug()
    print(f"  Current view: {state['current_view']}")
    print(f"  Selected node: {hierarchy_view.selected_node}")
    
    initial_node = hierarchy_view.selected_node
    
    # Press DOWN
    print("Pressing 'down'...")
    controller.handle_key('down')
    state = controller.get_state_debug()
    print(f"  Current view: {state['current_view']}")
    print(f"  Selected node: {hierarchy_view.selected_node}")
    
    # Verify final state
    assert state['current_view'] == 'hierarchy', \
        f"Expected to stay on hierarchy, but view is {state['current_view']}"
    assert hierarchy_view.selected_node != initial_node, \
        f"Expected selected_node to change, but still {hierarchy_view.selected_node}"
    
    print("✓ Complete scenario test passed")


def test_arrow_navigation_without_view_switch():
    """
    Test that arrow keys work correctly without any view switching.
    """
    app = MockApp()
    controller = TUIController(app.coverage_model, on_quit=lambda: None)
    app.controller = controller
    
    # Create real hierarchy view
    hierarchy_view = HierarchyView(app)
    controller.register_view("hierarchy", hierarchy_view)
    
    # Switch to hierarchy and test navigation
    controller.switch_view("hierarchy")
    
    # Get initial node
    initial_node = hierarchy_view.selected_node
    assert initial_node is not None, "Should have a selected node initially"
    
    # Press DOWN
    controller.handle_key('down')
    node_after_down = hierarchy_view.selected_node
    assert node_after_down != initial_node, "Node should change after DOWN"
    
    # Press DOWN again
    controller.handle_key('down')
    node_after_down2 = hierarchy_view.selected_node
    assert node_after_down2 != node_after_down, "Node should change after second DOWN"
    
    # Press UP
    controller.handle_key('up')
    node_after_up = hierarchy_view.selected_node
    assert node_after_up == node_after_down, "UP should go back to previous node"
    
    print("✓ Arrow navigation test passed")


def test_user_reported_bug_dashboard_after_down():
    """
    Test to reproduce user's exact observation using REAL TUIApp:
    User reports that <2> ; <DOWN> results in Dashboard being shown.
    
    This test uses the real TUIApp to observe actual controller behavior.
    """
    print("\n" + "=" * 70)
    print("DIAGNOSTIC TEST: Testing with REAL TUIApp")
    print("=" * 70)
    
    # Use a real test database
    db_path = os.path.join(os.path.dirname(__file__), '..', 'test_vlt.cdb')
    if not os.path.exists(db_path):
        print(f"WARNING: Test database not found at {db_path}")
        print("Creating minimal test setup instead...")
        # Fall back to mock test
        app = MockApp()
        controller = TUIController(app.coverage_model, on_quit=lambda: None)
        app.controller = controller
        hierarchy_view = HierarchyView(app)
        dashboard_view = Mock()
        dashboard_view.handle_key = Mock(return_value=False)
        dashboard_view.on_enter = Mock()
        dashboard_view.on_exit = Mock()
        controller.register_view("dashboard", dashboard_view)
        controller.register_view("hierarchy", hierarchy_view)
    else:
        # Create REAL TUIApp but don't run the event loop
        print(f"Using real database: {db_path}")
        app = TUIApp(db_path)
        
        # Initialize the app's internal state without starting the event loop
        from ucis.tui.models.coverage_model import CoverageModel
        app.coverage_model = CoverageModel(db_path, None)
        app.controller = TUIController(app.coverage_model, on_quit=app._on_quit)
        app.controller.running = True
        app._initialize_views()
        
        print(f"✓ Real app initialized")
        print(f"  Controller: {app.controller}")
        print(f"  Registered views: {list(app.controller.views.keys())}")
    
    controller = app.controller
    
    # Start on dashboard
    print(f"\n1. Starting on dashboard...")
    controller.switch_view("dashboard")
    state = controller.get_state_debug()
    print(f"   Current view: {state['current_view']}")
    assert state['current_view'] == 'dashboard', f"Should start on dashboard, got {state['current_view']}"
    
    # Press '2' to switch to hierarchy
    print(f"\n2. Pressing '2' (switch to hierarchy)...")
    controller.handle_key('2')
    state = controller.get_state_debug()
    print(f"   Current view: {state['current_view']}")
    print(f"   View history: {state['view_history']}")
    assert state['current_view'] == 'hierarchy', f"After '2', should be on hierarchy, got {state['current_view']}"
    
    # Press DOWN arrow
    print(f"\n3. Pressing 'down' arrow...")
    result = controller.handle_key('down')
    state = controller.get_state_debug()
    print(f"   handle_key returned: {result}")
    print(f"   Current view: {state['current_view']}")
    print(f"   View history: {state['view_history']}")
    
    # Get hierarchy view to check its state
    hierarchy_view = controller.get_current_view()
    if hierarchy_view:
        print(f"   Current view type: {type(hierarchy_view).__name__}")
        if hasattr(hierarchy_view, 'selected_node'):
            print(f"   Selected node: {hierarchy_view.selected_node}")
    
    # Check if we can observe Dashboard (user's reported behavior)
    print("\n" + "=" * 70)
    if state['current_view'] == 'dashboard':
        print("✓ BUG REPRODUCED: Observed Dashboard after <2><DOWN>")
        print("  This matches user's reported behavior")
        print("  ** THIS IS THE BUG WE NEED TO FIX **")
        # Assert to mark this as the expected bug behavior
        assert False, "BUG CONFIRMED: DOWN arrow incorrectly switches to dashboard"
    else:
        print(f"✗ Bug NOT reproduced: Current view is '{state['current_view']}'")
        print("  Expected: dashboard (user's bug)")
        print(f"  Actual: {state['current_view']}")
        print("  This means the controller logic is correct!")
        print("  If user still sees the bug, it may be:")
        print("    - KeyParser returning wrong key string")
        print("    - Terminal timing issue")
        print("    - View initialization problem")
    print("=" * 70)


def test_user_reported_bug_with_fragmented_keys():
    """
    Test the ACTUAL bug observed by user:
    KeyParser is fragmenting DOWN arrow into: 'esc', '[', 'B'
    
    User's debug output shows:
    [DEBUG] _get_key_input returned: '2'
    [DEBUG] _get_key_input returned: 'esc'  <-- This triggers go_back()!
    [DEBUG] _get_key_input returned: '['
    [DEBUG] _get_key_input returned: 'B'
    
    The 'esc' key gets processed by the controller's global handler,
    which switches back to dashboard. That's the bug!
    """
    print("\n" + "=" * 70)
    print("TEST: Reproducing ACTUAL bug with fragmented arrow key")
    print("=" * 70)
    
    # Use real app
    db_path = os.path.join(os.path.dirname(__file__), '..', 'test_vlt.cdb')
    app = TUIApp(db_path)
    
    # Initialize without running event loop
    from ucis.tui.models.coverage_model import CoverageModel
    app.coverage_model = CoverageModel(db_path, None)
    app.controller = TUIController(app.coverage_model, on_quit=app._on_quit)
    app.controller.running = True
    app._initialize_views()
    
    controller = app.controller
    
    # Start on dashboard
    print("\n1. Starting on dashboard")
    controller.switch_view("dashboard")
    state = controller.get_state_debug()
    print(f"   Current view: {state['current_view']}")
    
    # Press '2'
    print("\n2. Pressing '2'")
    controller.handle_key('2')
    state = controller.get_state_debug()
    print(f"   Current view: {state['current_view']}")
    assert state['current_view'] == 'hierarchy'
    
    # Now simulate what ACTUALLY happens - fragmented arrow key
    print("\n3. User presses DOWN arrow, but KeyParser fragments it...")
    
    # First fragment: 'esc'
    print("   Fragment 1: 'esc' (KeyParser returns this first)")
    controller.handle_key('esc')
    state = controller.get_state_debug()
    print(f"   After 'esc': current_view = {state['current_view']}")
    
    # This is the bug!
    if state['current_view'] == 'dashboard':
        print("   ✓ BUG REPRODUCED!")
        print("   'esc' triggered go_back() and switched to dashboard")
        print("   User sees dashboard (wrong!)")
    else:
        print(f"   Current view is {state['current_view']}")
    
    # Second fragment: '['
    print("   Fragment 2: '[' (processed as separate key)")
    controller.handle_key('[')
    state = controller.get_state_debug()
    print(f"   After '[': current_view = {state['current_view']}")
    
    # Third fragment: 'B'
    print("   Fragment 3: 'B' (processed as separate key)")
    controller.handle_key('B')
    state = controller.get_state_debug()
    print(f"   After 'B': current_view = {state['current_view']}")
    
    print("\n" + "=" * 70)
    print("CONCLUSION:")
    print("  The bug is in KeyParser - it's fragmenting escape sequences")
    print("  instead of recognizing them as a single key.")
    print("  'esc' alone triggers controller.go_back() → dashboard")
    print("=" * 70)
    
    # Assert the bug
    assert state['current_view'] == 'dashboard', \
        "Bug confirmed: fragmented arrow key causes dashboard switch"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
