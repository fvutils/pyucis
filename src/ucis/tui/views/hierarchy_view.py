"""
Hierarchy View - Navigate design structure and coverage hierarchy.
"""
from typing import List
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ucis.tui.views.base_view import BaseView


class HierarchyNode:
    """Represents a node in the coverage hierarchy."""

    def __init__(self, scope_id: int, name: str, scope_type: int, scope=None, parent=None):
        self.scope_id = scope_id
        self.scope = scope
        self.parent = parent
        self.children: List["HierarchyNode"] = []
        self.expanded = False
        self.name = name if name else "root"
        self.scope_type = scope_type
        self.depth = 0
        self.total = 0
        self.covered = 0

    def get_coverage(self):
        """Get precomputed coverage for this node."""
        return self.total, self.covered

    def get_coverage_percent(self):
        """Get coverage percentage."""
        if self.total == 0:
            return 0.0
        return (self.covered / self.total) * 100


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
        self._all_nodes: List[HierarchyNode] = []
        self._nodes_by_id = {}
        self.search_filter = ""
        self.search_mode = False
        self._tree_version = 0
        self._flat_cache = None
        self._flat_cache_key = None
        self._filter_visible_ids = None
        self._filter_cache_key = None
        self._build_hierarchy()

    def _build_hierarchy(self):
        """Build the hierarchy tree from the database."""
        self.root_nodes = []
        self._all_nodes = []
        self._nodes_by_id = {}
        try:
            if getattr(self.model.db, "conn", None) is not None:
                self._build_hierarchy_sql()
            else:
                self._build_hierarchy_api()
            if self.root_nodes:
                self.selected_node = self.root_nodes[0]
        except Exception:
            pass
        self._invalidate_flat_cache()

    def _invalidate_flat_cache(self):
        self._tree_version += 1
        self._flat_cache = None
        self._flat_cache_key = None
        self._filter_visible_ids = None
        self._filter_cache_key = None

    def _build_hierarchy_sql(self):
        """Build hierarchy and coverage from SQL in one shot."""
        from ucis.cover_type_t import CoverTypeT
        from ucis.scope_type_t import ScopeTypeT

        conn = self.model.db.conn
        scope_rows = conn.execute(
            "SELECT scope_id, parent_id, scope_type, scope_name FROM scopes ORDER BY scope_id"
        ).fetchall()
        if not scope_rows:
            return

        root_scope_id = None
        for row in scope_rows:
            if row[1] is None:
                root_scope_id = row[0]
                break

        cp_stats = {
            row[0]: (row[1] or 0, row[2] or 0)
            for row in conn.execute(
                """SELECT scope_id,
                          COUNT(*) AS total,
                          SUM(CASE WHEN cover_data > 0 THEN 1 ELSE 0 END) AS covered
                   FROM coveritems
                   WHERE cover_type = ?
                   GROUP BY scope_id""",
                (int(CoverTypeT.CVGBIN),)
            ).fetchall()
        }

        toggle_stats = {
            row[0]: (row[1] or 0, row[2] or 0)
            for row in conn.execute(
                """SELECT scope_id,
                          COUNT(*) AS total,
                          SUM(CASE WHEN cover_data > 0 THEN 1 ELSE 0 END) AS covered
                   FROM coveritems
                   WHERE cover_type = ?
                   GROUP BY scope_id""",
                (int(CoverTypeT.TOGGLEBIN),)
            ).fetchall()
        }

        parent_map = {}
        for scope_id, parent_id, scope_type, scope_name in scope_rows:
            node = HierarchyNode(scope_id=scope_id, name=scope_name, scope_type=scope_type)
            self._nodes_by_id[scope_id] = node
            self._all_nodes.append(node)
            parent_map[scope_id] = parent_id
            if scope_type == int(ScopeTypeT.COVERPOINT):
                node.total, node.covered = cp_stats.get(scope_id, (0, 0))
            elif scope_type == int(ScopeTypeT.TOGGLE):
                node.total, node.covered = toggle_stats.get(scope_id, (0, 0))

        for scope_id, parent_id in parent_map.items():
            node = self._nodes_by_id[scope_id]
            if parent_id in self._nodes_by_id:
                parent = self._nodes_by_id[parent_id]
                node.parent = parent
                parent.children.append(node)

        if root_scope_id in self._nodes_by_id:
            self.root_nodes = list(self._nodes_by_id[root_scope_id].children)
            for node in self.root_nodes:
                node.parent = None
        else:
            self.root_nodes = [n for n in self._all_nodes if n.parent is None]

        stack = [(n, 0) for n in self.root_nodes]
        while stack:
            node, depth = stack.pop()
            node.depth = depth
            for child in node.children:
                stack.append((child, depth + 1))

        self._rollup_coverage_totals()

    def _build_hierarchy_api(self):
        """Build hierarchy using API traversal (fallback)."""
        from ucis.scope_type_t import ScopeTypeT
        from ucis.cover_type_t import CoverTypeT

        def build_node(scope, parent=None):
            node = HierarchyNode(
                scope_id=getattr(scope, "scope_id", -1),
                name=scope.getScopeName(),
                scope_type=scope.getScopeType(),
                scope=scope,
                parent=parent
            )
            node.depth = 0 if parent is None else parent.depth + 1
            self._all_nodes.append(node)
            self._nodes_by_id[node.scope_id] = node
            try:
                for child_scope in scope.scopes(ScopeTypeT.ALL):
                    child_node = build_node(child_scope, node)
                    node.children.append(child_node)
            except Exception:
                pass
            if node.scope_type == ScopeTypeT.COVERPOINT and node.scope is not None:
                total = 0
                covered = 0
                try:
                    for bin_idx in node.scope.coverItems(CoverTypeT.CVGBIN):
                        total += 1
                        cover_data = bin_idx.getCoverData()
                        if cover_data and cover_data.data > 0:
                            covered += 1
                except Exception:
                    pass
                node.total = total
                node.covered = covered
            elif node.scope_type == ScopeTypeT.TOGGLE and node.scope is not None:
                total = 0
                covered = 0
                try:
                    for bin_idx in node.scope.coverItems(CoverTypeT.TOGGLEBIN):
                        total += 1
                        cover_data = bin_idx.getCoverData()
                        if cover_data and cover_data.data > 0:
                            covered += 1
                except Exception:
                    pass
                node.total = total
                node.covered = covered
            return node

        try:
            for scope in self.model.db.scopes(ScopeTypeT.ALL):
                self.root_nodes.append(build_node(scope))
        except Exception:
            pass

        self._rollup_coverage_totals()

    def _rollup_coverage_totals(self):
        """Roll up precomputed coverage from leaves to roots once."""
        for root in self.root_nodes:
            stack = [(root, False)]
            while stack:
                node, visited = stack.pop()
                if visited:
                    if node.children:
                        node.total = sum(c.total for c in node.children)
                        node.covered = sum(c.covered for c in node.children)
                else:
                    stack.append((node, True))
                    for child in node.children:
                        stack.append((child, False))

    def render(self):
        """Render the hierarchy view."""
        layout = Layout()

        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1)
        )

        title = Text("Hierarchy View", style="bold cyan", justify="center")
        header_panel = Panel(title, border_style="cyan")
        layout["header"].update(header_panel)

        layout["body"].split_row(
            Layout(name="tree", ratio=2),
            Layout(name="details", ratio=3)
        )

        tree_content = self._render_tree()
        tree_title = "Coverage Tree"
        if self.search_mode:
            tree_title += f" [SEARCH: {self.search_filter}_]"
        layout["body"]["tree"].update(Panel(tree_content, title=tree_title, border_style="green"))

        details_content = self._render_details()
        layout["body"]["details"].update(Panel(details_content, title="Details", border_style="blue"))

        return layout

    def _render_tree(self):
        """Render the coverage hierarchy tree with scrolling support."""
        flat_list = self._flatten_tree()

        if not flat_list:
            return Text("No items to display", style="dim italic")

        terminal_height = self.app.console.height if hasattr(self.app, "console") else 40
        overhead = 12
        available_height = max(10, terminal_height - overhead)
        visible_rows = available_height

        if self.selected_node in flat_list:
            selected_idx = flat_list.index(self.selected_node)
            if selected_idx < self.scroll_offset:
                self.scroll_offset = selected_idx
            elif selected_idx >= self.scroll_offset + visible_rows:
                self.scroll_offset = selected_idx - visible_rows + 1

        self.scroll_offset = max(0, min(self.scroll_offset, max(0, len(flat_list) - visible_rows)))

        lines = []
        start_idx = self.scroll_offset
        end_idx = min(start_idx + visible_rows, len(flat_list))

        for idx in range(start_idx, end_idx):
            node = flat_list[idx]
            lines.append(self._format_tree_line(node, is_selected=(node == self.selected_node)))

        if self.scroll_offset > 0:
            lines.insert(0, Text("▲ More items above...", style="dim italic"))
        if end_idx < len(flat_list):
            lines.append(Text("▼ More items below...", style="dim italic"))
        if len(flat_list) > visible_rows:
            lines.append(Text(f"\n[Showing {start_idx+1}-{end_idx} of {len(flat_list)} items]", style="dim italic"))

        result = Text()
        for line in lines:
            result.append(line)
            result.append("\n")
        return result

    def _format_tree_line(self, node, is_selected=False):
        """Format a single tree line."""
        from ucis.scope_type_t import ScopeTypeT

        icons = {
            ScopeTypeT.INSTANCE: "🎯",
            ScopeTypeT.COVERGROUP: "📋",
            ScopeTypeT.COVERPOINT: "📊",
            ScopeTypeT.DU_MODULE: "🔧",
            ScopeTypeT.PACKAGE: "📦",
            ScopeTypeT.TOGGLE: "⇅",
        }
        icon = icons.get(node.scope_type, "•")

        coverage_pct = node.get_coverage_percent()
        if coverage_pct >= 80:
            color = "green"
        elif coverage_pct >= 50:
            color = "yellow"
        else:
            color = "red"

        line = Text()
        line.append("  " * node.depth)
        if is_selected:
            line.append("➤ ", style="bold cyan on blue")
        else:
            line.append("  ")

        name_style = "bold white on blue" if is_selected else ""
        line.append(f"{icon} {node.name} ", style=name_style)

        coverage_style = f"{color} on blue" if is_selected else color
        line.append(f"({coverage_pct:.1f}%)", style=coverage_style)

        if node.children:
            line.append(" [-]" if node.expanded else " [+]", style="dim on blue" if is_selected else "dim")
        return line

    def _scope_type_label(self, scope_type: int) -> str:
        """Return human-readable UCIS scope type name."""
        from ucis.scope_type_t import ScopeTypeT

        if scope_type is None:
            return "UNKNOWN"

        try:
            for t in ScopeTypeT:
                if int(t) == int(scope_type):
                    return f"UCIS_{t.name}"
        except Exception:
            pass

        try:
            parts = [f"UCIS_{t.name}" for t in ScopeTypeT if int(t) != 0 and (int(scope_type) & int(t)) == int(t)]
            if parts:
                return "|".join(parts)
        except Exception:
            pass

        return f"UNKNOWN(0x{int(scope_type):X})"

    def _render_details(self):
        """Render details for the selected node."""
        if not self.selected_node:
            return Text("No node selected", style="dim")

        node = self.selected_node
        table = Table.grid(padding=(0, 2))
        table.add_column(style="cyan", justify="right")
        table.add_column(style="white")

        table.add_row("Name:", node.name)
        table.add_row("Type:", self._scope_type_label(node.scope_type))

        total, covered = node.get_coverage()
        coverage_pct = node.get_coverage_percent()

        table.add_row("Coverage:", f"{coverage_pct:.1f}%")
        table.add_row("Total Items:", str(total))
        table.add_row("Covered:", str(covered))
        table.add_row("Uncovered:", str(total - covered))

        from ucis.scope_type_t import ScopeTypeT
        from ucis.cover_type_t import CoverTypeT
        if node.scope_type == ScopeTypeT.COVERPOINT:
            table.add_row("", "")
            table.add_row("Bins:", "")
            try:
                if hasattr(self.model.db, "conn"):
                    rows = self.model.db.conn.execute(
                        """SELECT cover_name, cover_data
                           FROM coveritems
                           WHERE scope_id = ? AND cover_type = ?
                           ORDER BY cover_index
                           LIMIT 11""",
                        (node.scope_id, int(CoverTypeT.CVGBIN))
                    ).fetchall()
                    for i, row in enumerate(rows[:10]):
                        bin_name = row[0] or f"bin_{i}"
                        count = row[1] or 0
                        status = "✓" if count > 0 else "✗"
                        color = "green" if count > 0 else "red"
                        table.add_row("", Text(f"{status} {bin_name}: {count} hits", style=color))
                    if len(rows) > 10:
                        table.add_row("", f"... and {max(0, total - 10)} more")
                elif node.scope is not None:
                    for i, bin_idx in enumerate(node.scope.coverItems(CoverTypeT.CVGBIN)):
                        if i >= 10:
                            table.add_row("", f"... and {max(0, total - 10)} more")
                            break
                        bin_name = bin_idx.getName() if hasattr(bin_idx, "getName") else f"bin_{i}"
                        cover_data = bin_idx.getCoverData()
                        count = cover_data.data if cover_data else 0
                        status = "✓" if count > 0 else "✗"
                        color = "green" if count > 0 else "red"
                        table.add_row("", Text(f"{status} {bin_name}: {count} hits", style=color))
                else:
                    table.add_row("", Text("No bin details available", style="dim"))
            except Exception:
                pass

        elif node.scope_type == ScopeTypeT.TOGGLE:
            table.add_row("", "")
            table.add_row("Transitions:", "")
            try:
                if hasattr(self.model.db, "conn"):
                    rows = self.model.db.conn.execute(
                        """SELECT cover_name, cover_data
                           FROM coveritems
                           WHERE scope_id = ? AND cover_type = ?
                           ORDER BY cover_index""",
                        (node.scope_id, int(CoverTypeT.TOGGLEBIN))
                    ).fetchall()
                    for row in rows:
                        tname = row[0] or "?"
                        count = row[1] or 0
                        status = "✓" if count > 0 else "✗"
                        color = "green" if count > 0 else "red"
                        table.add_row("", Text(f"{status} {tname}: {count}×", style=color))
                elif node.scope is not None:
                    for bin_idx in node.scope.coverItems(CoverTypeT.TOGGLEBIN):
                        tname = bin_idx.getName() if hasattr(bin_idx, "getName") else "?"
                        cover_data = bin_idx.getCoverData()
                        count = cover_data.data if cover_data else 0
                        status = "✓" if count > 0 else "✗"
                        color = "green" if count > 0 else "red"
                        table.add_row("", Text(f"{status} {tname}: {count}×", style=color))
                else:
                    table.add_row("", Text("No transition details available", style="dim"))
            except Exception:
                pass

        return table

    def _build_filter_visible_set(self):
        """Compute nodes to keep visible for current search text."""
        if not self.search_filter:
            self._filter_visible_ids = None
            self._filter_cache_key = ""
            return

        key = self.search_filter.lower()
        if self._filter_cache_key == key and self._filter_visible_ids is not None:
            return

        matched = {}
        for root in self.root_nodes:
            stack = [(root, False)]
            while stack:
                node, visited = stack.pop()
                if visited:
                    self_match = key in node.name.lower()
                    child_match = any(matched.get(ch.scope_id, False) for ch in node.children)
                    matched[node.scope_id] = self_match or child_match
                else:
                    stack.append((node, True))
                    for child in node.children:
                        stack.append((child, False))
        self._filter_visible_ids = {scope_id for scope_id, ok in matched.items() if ok}
        self._filter_cache_key = key

    def _expand_all(self):
        """Expand all nodes in the tree."""
        stack = list(self.root_nodes)
        while stack:
            node = stack.pop()
            node.expanded = True
            stack.extend(node.children)
        self._invalidate_flat_cache()

    def _collapse_all(self):
        """Collapse all nodes in the tree."""
        stack = list(self.root_nodes)
        while stack:
            node = stack.pop()
            node.expanded = False
            stack.extend(node.children)
        self._invalidate_flat_cache()

    def handle_key(self, key: str) -> bool:
        """Handle hierarchy-specific keys."""
        if self.search_mode:
            if key == "enter" or key == "escape":
                self.search_mode = False
                return True
            if key == "backspace":
                self.search_filter = self.search_filter[:-1]
                self._invalidate_flat_cache()
                return True
            if len(key) == 1 and key.isprintable():
                self.search_filter += key
                self._invalidate_flat_cache()
                return True
            return True

        if key == "/":
            self.search_mode = True
            self.search_filter = ""
            self._invalidate_flat_cache()
            return True
        if key == "e" or key == "E":
            self._expand_all()
            return True
        if key == "c" or key == "C":
            self._collapse_all()
            return True
        if key == "down":
            self._move_selection(1)
            return True
        if key == "up":
            self._move_selection(-1)
            return True
        if key == "right" and self.selected_node:
            self.selected_node.expanded = True
            self._invalidate_flat_cache()
            return True
        if key == "left" and self.selected_node:
            self.selected_node.expanded = False
            self._invalidate_flat_cache()
            return True
        if key == "enter" and self.selected_node:
            self.selected_node.expanded = not self.selected_node.expanded
            self._invalidate_flat_cache()
            return True

        return False

    def _move_selection(self, delta):
        """Move selection up or down."""
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
        key = (self._tree_version, self.search_filter)
        if self._flat_cache_key == key and self._flat_cache is not None:
            return self._flat_cache

        self._build_filter_visible_set()
        result = []

        def flatten_node(node):
            if self._filter_visible_ids is not None and node.scope_id not in self._filter_visible_ids:
                return
            result.append(node)
            if node.children and node.expanded:
                for child in node.children:
                    flatten_node(child)

        for root in self.root_nodes:
            flatten_node(root)

        self._flat_cache = result
        self._flat_cache_key = key
        return result
