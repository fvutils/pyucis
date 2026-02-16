"""
Unit tests for TUIController.

These tests verify navigation and state management independent of UI.
"""
import pytest
from unittest.mock import Mock
from ucis.tui.controller import TUIController


class MockView:
    """Mock view for testing."""
    def __init__(self, name, handles_keys=None):
        self.name = name
        self.handles_keys = handles_keys or []
        self.keys_received = []
        self.enter_called = False
        self.exit_called = False
    
    def handle_key(self, key: str) -> bool:
        """Record key and return whether we handle it."""
        self.keys_received.append(key)
        return key in self.handles_keys
    
    def on_enter(self):
        self.enter_called = True
    
    def on_exit(self):
        self.exit_called = True


@pytest.fixture
def mock_model():
    """Create mock coverage model."""
    model = Mock()
    model.get_test_filter = Mock(return_value=None)
    return model


@pytest.fixture
def controller(mock_model):
    """Create controller with mock model."""
    return TUIController(mock_model)


def test_initial_state(controller):
    """Test controller initial state."""
    assert controller.current_view_name is None
    assert len(controller.views) == 0
    assert len(controller.view_history) == 0
    assert controller.show_help == False


def test_register_and_switch_view(controller):
    """Test view registration and switching."""
    dashboard = MockView("Dashboard")
    hierarchy = MockView("Hierarchy")
    
    controller.register_view("dashboard", dashboard)
    controller.register_view("hierarchy", hierarchy)
    
    # Switch to dashboard
    assert controller.switch_view("dashboard") == True
    assert controller.current_view_name == "dashboard"
    assert dashboard.enter_called == True
    
    # Switch to hierarchy
    assert controller.switch_view("hierarchy") == True
    assert controller.current_view_name == "hierarchy"
    assert dashboard.exit_called == True
    assert hierarchy.enter_called == True


def test_view_navigation_with_number_keys(controller):
    """Test pressing number keys to switch views."""
    dashboard = MockView("Dashboard")
    hierarchy = MockView("Hierarchy")
    
    controller.register_view("dashboard", dashboard)
    controller.register_view("hierarchy", hierarchy)
    controller.switch_view("dashboard")
    
    print("\n" + "="*60)
    print("Test: Number key navigation")
    print("="*60)
    
    # Press '2' to go to hierarchy
    print("\n1. Current view:", controller.current_view_name)
    print("2. Pressing '2' to switch to hierarchy...")
    
    handled = controller.handle_key('2')
    
    print(f"   Key handled: {handled}")
    print(f"   Current view: {controller.current_view_name}")
    
    assert handled == True, "Key '2' should be handled"
    assert controller.current_view_name == "hierarchy", \
        f"Should be on hierarchy, but on {controller.current_view_name}"
    
    print("   ✓ Successfully switched to hierarchy")
    print("="*60)


def test_arrow_key_navigation_stays_in_view(controller):
    """
    CRITICAL TEST: This should reproduce the user's bug.
    
    Scenario: <2> (go to hierarchy) then <DOWN> (navigate within)
    Expected: Stay on hierarchy
    Bug: Goes back to dashboard
    """
    dashboard = MockView("Dashboard")
    hierarchy = MockView("Hierarchy", handles_keys=['up', 'down', 'enter'])
    
    controller.register_view("dashboard", dashboard)
    controller.register_view("hierarchy", hierarchy)
    controller.switch_view("dashboard")
    
    print("\n" + "="*60)
    print("Test: User Bug Reproduction - <2> then <DOWN>")
    print("="*60)
    
    # Step 1: Press '2' to go to hierarchy
    print("\n1. Starting view:", controller.current_view_name)
    print("2. User presses '2' (switch to hierarchy)...")
    
    controller.handle_key('2')
    print(f"   After '2': current_view = {controller.current_view_name}")
    assert controller.current_view_name == "hierarchy"
    
    # Step 2: Press DOWN arrow
    print("\n3. User presses DOWN arrow (navigate in hierarchy)...")
    print(f"   Before DOWN: current_view = {controller.current_view_name}")
    
    handled = controller.handle_key('down')
    
    print(f"   DOWN handled: {handled}")
    print(f"   Keys received by hierarchy: {hierarchy.keys_received}")
    print(f"   After DOWN: current_view = {controller.current_view_name}")
    
    # Check state
    state = controller.get_state_debug()
    print(f"\n4. State dump:")
    for key, value in state.items():
        print(f"   {key}: {value}")
    
    # The assertion that should pass but might be failing
    if controller.current_view_name == "hierarchy":
        print("\n   ✓ PASS - Still on hierarchy after DOWN")
    else:
        print(f"\n   ✗ FAIL - Bug reproduced! Now on {controller.current_view_name}")
        print(f"   This means DOWN was not handled by the view!")
    
    assert controller.current_view_name == "hierarchy", \
        f"BUG: Should be on hierarchy but on {controller.current_view_name}"
    assert 'down' in hierarchy.keys_received, \
        "Hierarchy should have received the 'down' key"
    
    print("="*60)


def test_view_handles_key_before_global(controller):
    """Test that views get priority over global handlers."""
    view = MockView("TestView", handles_keys=['x', 'esc'])
    controller.register_view("test", view)
    controller.switch_view("test")
    
    # View handles 'x'
    handled = controller.handle_key('x')
    assert handled == True
    assert 'x' in view.keys_received
    
    # View also handles 'esc' (so it shouldn't go back)
    view_before = controller.current_view_name
    handled = controller.handle_key('esc')
    assert handled == True
    assert 'esc' in view.keys_received
    assert controller.current_view_name == view_before, \
        "View handled esc, so shouldn't navigate away"


def test_complete_navigation_sequence(controller):
    """Test complete sequence: Dashboard -> Hierarchy -> Navigate -> Back."""
    dashboard = MockView("Dashboard")
    hierarchy = MockView("Hierarchy", handles_keys=['up', 'down', 'left', 'right', 'enter'])
    gaps = MockView("Gaps")
    
    for name, view in [('dashboard', dashboard), ('hierarchy', hierarchy), ('gaps', gaps)]:
        controller.register_view(name, view)
    
    print("\n" + "="*60)
    print("Test: Complete Navigation Sequence")
    print("="*60)
    
    # Start on dashboard
    controller.switch_view("dashboard")
    print(f"1. Start: {controller.current_view_name}")
    assert controller.current_view_name == "dashboard"
    
    # Go to hierarchy (press 2)
    controller.handle_key('2')
    print(f"2. After '2': {controller.current_view_name}")
    assert controller.current_view_name == "hierarchy"
    
    # Navigate with DOWN (should stay in hierarchy)
    controller.handle_key('down')
    print(f"3. After 'down': {controller.current_view_name}")
    assert controller.current_view_name == "hierarchy", "DOWN should not leave hierarchy"
    
    # Navigate with UP (should stay in hierarchy)
    controller.handle_key('up')
    print(f"4. After 'up': {controller.current_view_name}")
    assert controller.current_view_name == "hierarchy", "UP should not leave hierarchy"
    
    # Go to gaps (press 3)
    controller.handle_key('3')
    print(f"5. After '3': {controller.current_view_name}")
    assert controller.current_view_name == "gaps"
    
    # Go back to dashboard (press 1)
    controller.handle_key('1')
    print(f"6. After '1': {controller.current_view_name}")
    assert controller.current_view_name == "dashboard"
    
    print("\n✓ All navigation steps worked correctly")
    print("="*60)


def test_quit_handling(controller):
    """Test that quit keys work."""
    quit_called = False
    
    def on_quit():
        nonlocal quit_called
        quit_called = True
    
    controller.on_quit = on_quit
    controller.running = True
    
    # Press 'q' to quit
    controller.handle_key('q')
    
    assert quit_called == True
    assert controller.running == False


def test_help_overlay(controller):
    """Test help overlay toggle."""
    assert controller.show_help == False
    
    # Press '?' to show help
    controller.handle_key('?')
    assert controller.show_help == True
    
    # Any key closes help
    controller.handle_key('x')
    assert controller.show_help == False


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
