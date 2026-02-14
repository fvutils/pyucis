"""
Hierarchy View - Navigate design structure and coverage hierarchy.
"""
from typing import List, Optional
from rich.layout import Layout
from rich.panel import Panel
from rich.tree import Tree
from rich.table import Table
from rich.text import Text

from ucis.tui.views.base_view import BaseView


class HierarchyNode:
    """Represents a node in the coverage hierarchy."""
    
    def __init__(self, scope, parent=None):
        self.scope = scope
        self.parent = parent
        self.children = []
        self.expanded = False
        self.name = scope.getScopeName() if scope else "root"
        self.scope_type = scope.getScopeType() if scope else None
        
    def get_coverage(self):
        """Calculate coverage for this node."""
        try:
            from ucis.scope_type_t import ScopeTypeT
            from ucis.cover_type_t import CoverTypeT
            total = 0
            covered = 0
            
            # If this is a coverpoint, count bins
            if self.scope_type == ScopeTypeT.COVERPOINT:
                for bin_idx in self.scope.coverItems(CoverTypeT.CVGBIN):
                    total += 1
                    cover_data = bin_idx.getCoverData()
                    if cover_data and cover_data.data > 0:
                        covered += 1
            
            # Otherwise aggregate from children
            else:
                for child in self.children:
                    c_total, c_covered = child.get_coverage()
                    total += c_total
                    covered += c_covered
            
            return total, covered
        except:
            return 0, 0
    
    def get_coverage_percent(self):
        """Get coverage percentage."""
        total, covered = self.get_coverage()
        if total == 0:
            return 0.0
        return (covered / total) * 100


class HierarchyView(BaseView):
    """
    Hierarchy view for navigating the design structure.
    
    Keyboard shortcuts:
    - Up/Down: Navigate nodes
    - Enter: Toggle expand/collapse
    - Left/Right: Collapse/expand node
    - E: Expand all nodes
    - C: Collapse all nodes
    - /: Search/filter
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.root_nodes = []
        self.current_index = 0
        self.scroll_offset = 0
        self.selected_node = None
        self.search_filter = ""  # Current search filter
        self.search_mode = False  # Whether in search mode
        self._build_hierarchy()
        
    def _build_hierarchy(self):
        """Build the hierarchy tree from the database."""
        from ucis.scope_type_t import ScopeTypeT
        
        try:
            for scope in self.model.db.scopes(ScopeTypeT.ALL):
                node = self._build_node(scope)
                self.root_nodes.append(node)
                
            if self.root_nodes:
                self.selected_node = self.root_nodes[0]
        except Exception as e:
            pass
    
    def _build_node(self, scope, parent=None):
        """Recursively build hierarchy nodes."""
        from ucis.scope_type_t import ScopeTypeT
        
        node = HierarchyNode(scope, parent)
        
        try:
            for child_scope in scope.scopes(ScopeTypeT.ALL):
                child_node = self._build_node(child_scope, node)
                node.children.append(child_node)
        except:
            pass
        
        return node
    
    def render(self):
        """Render the hierarchy view."""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1)
        )
        
        # Header
        title = Text("Hierarchy View", style="bold cyan", justify="center")
        header_panel = Panel(title, border_style="cyan")
        layout["header"].update(header_panel)
        
        # Body - split into left tree and right details
        layout["body"].split_row(
            Layout(name="tree", ratio=2),
            Layout(name="details", ratio=3)
        )
        
        # Render tree
        tree_content = self._render_tree()
        tree_title = "Coverage Tree"
        if self.search_mode:
            tree_title += f" [SEARCH: {self.search_filter}_]"
        layout["body"]["tree"].update(Panel(tree_content, title=tree_title, border_style="green"))
        
        # Render details
        details_content = self._render_details()
        layout["body"]["details"].update(Panel(details_content, title="Details", border_style="blue"))
        
        return layout
    
    def _render_tree(self):
        """Render the coverage hierarchy tree with scrolling support."""
        from rich.console import Console
        from rich.text import Text
        
        # Get flattened list of visible nodes
        flat_list = self._flatten_tree()
        
        if not flat_list:
            return Text("No items to display", style="dim italic")
        
        # Calculate available height dynamically based on terminal size
        # Get terminal height from app's console
        terminal_height = self.app.console.height if hasattr(self.app, 'console') else 40
        
        # Account for overhead:
        # - Header panel: ~3 lines
        # - Status bar: ~1 line
        # - Panel borders: ~4 lines (top and bottom for body panels)
        # - Scroll indicators: ~2 lines
        # - Status text: ~2 lines
        overhead = 12
        available_height = max(10, terminal_height - overhead)
        
        visible_rows = available_height  # Number of tree nodes to show at once
        
        # Update scroll offset to keep selected node visible
        if self.selected_node in flat_list:
            selected_idx = flat_list.index(self.selected_node)
            
            # Adjust scroll_offset to keep selection visible
            if selected_idx < self.scroll_offset:
                # Selected item is above visible area
                self.scroll_offset = selected_idx
            elif selected_idx >= self.scroll_offset + visible_rows:
                # Selected item is below visible area
                self.scroll_offset = selected_idx - visible_rows + 1
        
        # Clamp scroll offset
        self.scroll_offset = max(0, min(self.scroll_offset, max(0, len(flat_list) - visible_rows)))
        
        # Build display text for visible window
        lines = []
        start_idx = self.scroll_offset
        end_idx = min(start_idx + visible_rows, len(flat_list))
        
        for idx in range(start_idx, end_idx):
            node = flat_list[idx]
            line = self._format_tree_line(node, is_selected=(node == self.selected_node))
            lines.append(line)
        
        # Add scroll indicators
        if self.scroll_offset > 0:
            lines.insert(0, Text("▲ More items above...", style="dim italic"))
        if end_idx < len(flat_list):
            lines.append(Text("▼ More items below...", style="dim italic"))
        
        # Add status line
        if len(flat_list) > visible_rows:
            status = Text(f"\n[Showing {start_idx+1}-{end_idx} of {len(flat_list)} items]", style="dim italic")
            lines.append(status)
        
        # Combine all lines
        result = Text()
        for line in lines:
            result.append(line)
            result.append("\n")
        
        return result
    
    def _format_tree_line(self, node, is_selected=False):
        """Format a single tree line."""
        from ucis.scope_type_t import ScopeTypeT
        
        # Calculate depth by walking up parent chain
        depth = 0
        current = node
        while current.parent:
            depth += 1
            current = current.parent
        
        # Get icon based on scope type
        icons = {
            ScopeTypeT.INSTANCE: "🎯",
            ScopeTypeT.COVERGROUP: "📋",
            ScopeTypeT.COVERPOINT: "📊",
            ScopeTypeT.DU_MODULE: "🔧",
            ScopeTypeT.PACKAGE: "📦",
        }
        icon = icons.get(node.scope_type, "•")
        
        # Get coverage
        coverage_pct = node.get_coverage_percent()
        
        # Color based on coverage
        if coverage_pct >= 80:
            color = "green"
        elif coverage_pct >= 50:
            color = "yellow"
        else:
            color = "red"
        
        # Build line with indentation
        line = Text()
        
        # Indentation
        line.append("  " * depth)
        
        # Selection indicator
        if is_selected:
            line.append("➤ ", style="bold cyan on blue")
        else:
            line.append("  ")
        
        # Icon and name
        name_style = "bold white on blue" if is_selected else ""
        line.append(f"{icon} {node.name} ", style=name_style)
        
        # Coverage percentage
        coverage_style = f"{color} on blue" if is_selected else color
        line.append(f"({coverage_pct:.1f}%)", style=coverage_style)
        
        # Expand/collapse indicator
        if node.children:
            if node.expanded:
                line.append(" [-]", style="dim on blue" if is_selected else "dim")
            else:
                line.append(" [+]", style="dim on blue" if is_selected else "dim")
        
        return line
    
    def _render_details(self):
        """Render details for the selected node."""
        if not self.selected_node:
            return Text("No node selected", style="dim")
        
        node = self.selected_node
        
        # Create details table
        table = Table.grid(padding=(0, 2))
        table.add_column(style="cyan", justify="right")
        table.add_column(style="white")
        
        table.add_row("Name:", node.name)
        table.add_row("Type:", str(node.scope_type))
        
        total, covered = node.get_coverage()
        coverage_pct = node.get_coverage_percent()
        
        table.add_row("Coverage:", f"{coverage_pct:.1f}%")
        table.add_row("Total Items:", str(total))
        table.add_row("Covered:", str(covered))
        table.add_row("Uncovered:", str(total - covered))
        
        # If it's a coverpoint, show bins
        from ucis.scope_type_t import ScopeTypeT
        from ucis.cover_type_t import CoverTypeT
        if node.scope_type == ScopeTypeT.COVERPOINT:
            table.add_row("", "")
            table.add_row("Bins:", "")
            
            try:
                for i, bin_idx in enumerate(node.scope.coverItems(CoverTypeT.CVGBIN)):
                    if i >= 10:  # Limit to first 10 bins
                        table.add_row("", f"... and {total - 10} more")
                        break
                    
                    bin_name = bin_idx.getName() if hasattr(bin_idx, 'getName') else f"bin_{i}"
                    cover_data = bin_idx.getCoverData()
                    count = cover_data.data if cover_data else 0
                    status = "✓" if count > 0 else "✗"
                    color = "green" if count > 0 else "red"
                    
                    table.add_row(
                        "",
                        Text(f"{status} {bin_name}: {count} hits", style=color)
                    )
            except:
                pass
        
        return table
    
    def _matches_filter(self, node):
        """Check if node matches the current search filter."""
        if not self.search_filter:
            return True
        
        filter_lower = self.search_filter.lower()
        
        # Check node name
        if filter_lower in node.name.lower():
            return True
        
        # Check any children (recursive)
        for child in node.children:
            if self._matches_filter(child):
                return True
        
        return False
    
    def _expand_all(self):
        """Expand all nodes in the tree."""
        def expand_node(node):
            node.expanded = True
            for child in node.children:
                expand_node(child)
        
        for root in self.root_nodes:
            expand_node(root)
    
    def _collapse_all(self):
        """Collapse all nodes in the tree."""
        def collapse_node(node):
            node.expanded = False
            for child in node.children:
                collapse_node(child)
        
        for root in self.root_nodes:
            collapse_node(root)
    
    def handle_key(self, key: str) -> bool:
        """Handle hierarchy-specific keys."""
        # Search mode handling
        if self.search_mode:
            if key == 'enter' or key == 'escape':
                self.search_mode = False
                return True
            elif key == 'backspace':
                self.search_filter = self.search_filter[:-1]
                return True
            elif len(key) == 1 and key.isprintable():
                self.search_filter += key
                return True
            return True
        
        # Normal mode handling
        if key == '/':
            self.search_mode = True
            self.search_filter = ""
            return True
        elif key == 'e' or key == 'E':
            self._expand_all()
            return True
        elif key == 'c' or key == 'C':
            self._collapse_all()
            return True
        elif key == 'down':
            self._move_selection(1)
            return True
        elif key == 'up':
            self._move_selection(-1)
            return True
        elif key == 'right' and self.selected_node:
            self.selected_node.expanded = True
            return True
        elif key == 'left' and self.selected_node:
            self.selected_node.expanded = False
            return True
        elif key == 'enter' and self.selected_node:
            # Toggle expansion
            self.selected_node.expanded = not self.selected_node.expanded
            return True
        
        return False
    
    def _move_selection(self, delta):
        """Move selection up or down."""
        # Flatten the tree to navigate
        flat_list = self._flatten_tree()
        
        if not flat_list:
            return
        
        try:
            current_idx = flat_list.index(self.selected_node)
            new_idx = max(0, min(len(flat_list) - 1, current_idx + delta))
            self.selected_node = flat_list[new_idx]
        except ValueError:
            self.selected_node = flat_list[0]
    
    def _flatten_tree(self):
        """Flatten the tree for navigation (only visible nodes)."""
        result = []
        
        def flatten_node(node):
            # Apply search filter
            if self.search_filter and not self._matches_filter(node):
                return
            
            result.append(node)
            # Only recurse if node is expanded
            if node.children and node.expanded:
                for child in node.children:
                    flatten_node(child)
        
        for root in self.root_nodes:
            flatten_node(root)
        
        return result
