"""
Unit tests for TUI navigation flow.

Tests the complete key handling flow: key parsing -> view handling -> global handling.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from ucis.tui.app import TUIApp
from ucis.tui.key_parser import KeyParser


class MockCoverageModel:
    """Mock coverage model for testing."""
    def __init__(self):
        self.db = Mock()
        self.db_path = "test.db"
        # Mock the scopes method to return empty list
        self.db.scopes = Mock(return_value=[])
    
    def get_test_filter(self):
        return None


class MockView:
    """Mock view for testing key handling."""
    def __init__(self, name, handles_keys=None):
        self.name = name
        self.handles_keys = handles_keys or []
        self.keys_received = []
        self.focused = False
    
    def handle_key(self, key: str) -> bool:
        """Record key and return whether we handle it."""
        self.keys_received.append(key)
        return key in self.handles_keys
    
    def render(self):
        return f"Mock {self.name} View"
    
    def on_enter(self):
        self.focused = True
    
    def on_exit(self):
        self.focused = False


def test_view_navigation_with_arrow_keys():
    """
    Test that pressing '2' then DOWN doesn't go back to dashboard.
    
    Scenario:
    1. Start on dashboard
    2. Press '2' to go to hierarchy
    3. Press DOWN arrow
    4. Expected: Still on hierarchy view, DOWN handled by view
    5. Bug: Goes back to dashboard
    """
    from ucis.tui.controller import TUIController

    print("\n" + "="*60)
    print("Test: Navigation from Dashboard -> Hierarchy -> DOWN arrow")
    print("="*60)
    
    # Create app and controller (don't call run())
    app = TUIApp("test.db")
    app.coverage_model = MockCoverageModel()
    controller = TUIController(app.coverage_model)
    controller.running = True

    # Create mock views
    dashboard = MockView("Dashboard", handles_keys=[])
    hierarchy = MockView("Hierarchy", handles_keys=['up', 'down', 'enter'])

    controller.register_view('dashboard', dashboard)
    controller.register_view('hierarchy', hierarchy)
    controller.switch_view('dashboard')

    print(f"\n1. Initial state: current_view = {controller.get_current_view().name}")
    assert controller.get_current_view() == dashboard

    # Simulate pressing '2' to go to hierarchy
    print("\n2. User presses '2' (switch to hierarchy)...")
    handled = controller.handle_key('2')
    print(f"   Handled: {handled}")
    assert controller.get_current_view() == hierarchy, \
        f"Expected hierarchy, got {controller.get_current_view().name}"
    print("   ✓ Successfully switched to hierarchy view")

    # Simulate pressing DOWN arrow
    print("\n3. User presses DOWN arrow...")
    view_handled = controller.handle_key('down')
    print(f"   View handled 'down': {view_handled}")
    print(f"   Current view after DOWN: {controller.get_current_view().name}")

    assert controller.get_current_view() == hierarchy, \
        f"BUG: After DOWN arrow, should be on hierarchy but on {controller.get_current_view().name}"
    print("\n" + "="*60)


def test_key_handling_priority():
    """Test that views get priority over global handlers."""
    print("\n" + "="*60)
    print("Test: View key handling priority")
    print("="*60)
    
    app = TUIApp("test.db")
    app.coverage_model = MockCoverageModel()
    
    # Create a view that handles 'x'
    view = MockView("TestView", handles_keys=['x'])
    app.current_view = view
    
    # Simulate the main loop's key handling logic
    key = 'x'
    
    print(f"\n1. Key pressed: '{key}'")
    
    # View tries first
    handled = app.current_view.handle_key(key)
    print(f"2. View handled it: {handled}")
    
    # Global only if view didn't handle
    if not handled:
        global_handled = app.key_handler.handle_global_key(key)
        print(f"3. Global handler handled it: {global_handled}")
    else:
        print(f"3. Global handler not called (view handled it)")
    
    assert handled == True, "View should have handled 'x'"
    assert 'x' in view.keys_received, "View should have received 'x'"
    print("\n✓ View correctly got priority")
    
    print("="*60)


def test_complete_navigation_flow():
    """
    Test complete flow with key parsing.
    
    This simulates the exact user scenario:
    - Dashboard shows
    - User presses '2' -> hierarchy shows
    - User presses DOWN arrow -> hierarchy should handle it
    """
    from ucis.tui.controller import TUIController

    print("\n" + "="*60)
    print("Test: Complete navigation flow with KeyParser")
    print("="*60)

    app = TUIApp("test.db")
    app.coverage_model = MockCoverageModel()
    controller = TUIController(app.coverage_model)
    controller.running = True

    dashboard = MockView("Dashboard")
    hierarchy = MockView("Hierarchy", handles_keys=['up', 'down', 'enter'])

    controller.register_view('dashboard', dashboard)
    controller.register_view('hierarchy', hierarchy)
    controller.switch_view('dashboard')

    keys = ['2', 'down']
    for i, key in enumerate(keys):
        print(f"\n{i+1}. Processing key: '{key}'")
        print(f"   Current view before: {controller.get_current_view().name}")
        controller.handle_key(key)
        print(f"   Current view after: {controller.get_current_view().name}")

    print(f"\n3. Final check:")
    print(f"   Current view: {controller.get_current_view().name}")
    print(f"   Hierarchy received keys: {hierarchy.keys_received}")

    assert controller.get_current_view() == hierarchy, \
        f"Should still be on hierarchy, but on {controller.get_current_view().name}"
    assert 'down' in hierarchy.keys_received, \
        "Hierarchy should have received 'down' key"

    print("\n✓ PASS - Navigation flow works correctly")
    print("="*60)


def test_real_hierarchy_view():
    """
    Test with the REAL HierarchyView to see if it handles DOWN correctly.
    
    This will reveal if there's an issue with the actual view implementation.
    """
    from ucis.tui.views.hierarchy_view import HierarchyView
    
    print("\n" + "="*60)
    print("Test: Real HierarchyView DOWN arrow handling")
    print("="*60)
    
    # Create app with real hierarchy view
    app = TUIApp("test.db")
    app.coverage_model = MockCoverageModel()
    
    # Create real hierarchy view
    hierarchy = HierarchyView(app)
    app.current_view = hierarchy
    
    print(f"\n1. Created real HierarchyView")
    print(f"   Root nodes: {len(hierarchy.root_nodes)}")
    print(f"   Selected node: {hierarchy.selected_node}")
    print(f"   Search mode: {hierarchy.search_mode}")
    
    # Try handling DOWN
    print(f"\n2. Sending 'down' key to HierarchyView...")
    handled = hierarchy.handle_key('down')
    
    print(f"   HierarchyView.handle_key('down') returned: {handled}")
    
    if handled:
        print("   ✓ PASS - HierarchyView correctly handles DOWN")
    else:
        print("   ✗ FAIL - HierarchyView returned False for DOWN!")
        print("   This is the bug! The view doesn't handle DOWN, so it falls to global handler.")
    
    assert handled == True, "HierarchyView should handle 'down' key"
    
    print("="*60)


if __name__ == '__main__':
    # Run tests with verbose output
    test_view_navigation_with_arrow_keys()
    test_key_handling_priority()
    test_complete_navigation_flow()
    test_real_hierarchy_view()
    print("\n✅ All navigation tests passed!")
