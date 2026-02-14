"""
Code Coverage View - File-level code coverage browser.
"""
from typing import List, Dict, Any, Optional
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align

from ucis.tui.views.base_view import BaseView
from ucis.cover_type_t import CoverTypeT
from ucis.scope_type_t import ScopeTypeT


class FileCoverageInfo:
    """Information about coverage for a single file."""
    
    def __init__(self, file_id: int, file_path: str):
        self.file_id = file_id
        self.file_path = file_path
        self.line_total = 0
        self.line_covered = 0
        self.branch_total = 0
        self.branch_covered = 0
        self.toggle_total = 0
        self.toggle_covered = 0
        self.lines = {}  # line_no -> hits
    
    @property
    def line_coverage(self) -> float:
        if self.line_total == 0:
            return 0.0
        return (self.line_covered / self.line_total) * 100
    
    @property
    def overall_coverage(self) -> float:
        total = self.line_total + self.branch_total + self.toggle_total
        covered = self.line_covered + self.branch_covered + self.toggle_covered
        if total == 0:
            return 0.0
        return (covered / total) * 100


class CodeCoverageView(BaseView):
    """
    Code coverage view showing file-level coverage statistics.
    
    Keyboard shortcuts:
    - Up/Down: Navigate files or scroll lines
    - Enter: View file details
    - PageUp/PageDown: Scroll file detail view
    - L: Sort by line coverage
    - O: Sort by overall coverage
    - N: Sort by name
    - ESC: Return to file list
    - U: Jump to next uncovered line
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.file_coverage: List[FileCoverageInfo] = []
        self.current_index = 0
        self.scroll_offset = 0
        self.sort_mode = 'coverage'  # 'coverage', 'line', 'name'
        self.selected_file: Optional[FileCoverageInfo] = None
        self.view_mode = 'list'  # 'list' or 'detail'
        self.detail_scroll_offset = 0  # For scrolling in detail view
        self.source_lines: List[str] = []  # Cached source file lines
        self._load_file_coverage()
    
    def _load_file_coverage(self):
        """Load file coverage information from database."""
        # For SQLite databases, query directly for better performance
        if hasattr(self.model.db, 'conn'):
            self._load_file_coverage_sql()
        else:
            self._load_file_coverage_api()
    
    def _load_file_coverage_sql(self):
        """Load file coverage using direct SQL queries (for SqliteUCIS)."""
        import sqlite3
        
        # Get database connection from SqliteUCIS
        conn = self.model.db.conn
        cursor = conn.cursor()
        
        try:
            # Query file coverage statistics
            cursor.execute("""
                SELECT 
                    f.file_id,
                    f.file_path,
                    COUNT(CASE WHEN ci.cover_type = 32 THEN 1 END) as line_total,
                    SUM(CASE WHEN ci.cover_type = 32 AND ci.cover_data > 0 THEN 1 ELSE 0 END) as line_covered,
                    COUNT(CASE WHEN ci.cover_type = 64 THEN 1 END) as branch_total,
                    SUM(CASE WHEN ci.cover_type = 64 AND ci.cover_data > 0 THEN 1 ELSE 0 END) as branch_covered,
                    COUNT(CASE WHEN ci.cover_type = 512 THEN 1 END) as toggle_total,
                    SUM(CASE WHEN ci.cover_type = 512 AND ci.cover_data > 0 THEN 1 ELSE 0 END) as toggle_covered
                FROM files f
                JOIN coveritems ci ON f.file_id = ci.source_file_id
                WHERE ci.cover_type IN (32, 64, 512)
                GROUP BY f.file_id, f.file_path
                ORDER BY f.file_path
            """)
            
            for row in cursor.fetchall():
                file_id, file_path, line_total, line_covered, branch_total, branch_covered, toggle_total, toggle_covered = row
                
                file_info = FileCoverageInfo(file_id, file_path)
                file_info.line_total = line_total or 0
                file_info.line_covered = line_covered or 0
                file_info.branch_total = branch_total or 0
                file_info.branch_covered = branch_covered or 0
                file_info.toggle_total = toggle_total or 0
                file_info.toggle_covered = toggle_covered or 0
                
                # Load line-level coverage
                cursor.execute("""
                    SELECT source_line, cover_data
                    FROM coveritems
                    WHERE source_file_id = ? AND cover_type = 32
                    ORDER BY source_line
                """, (file_id,))
                
                for line_row in cursor.fetchall():
                    line_no, hits = line_row
                    if line_no not in file_info.lines:
                        file_info.lines[line_no] = 0
                    file_info.lines[line_no] = max(file_info.lines[line_no], hits or 0)
                
                self.file_coverage.append(file_info)
        
        except Exception as e:
            # Fall back to API method if SQL fails
            print(f"Warning: SQL query failed, falling back to API: {e}")
            self._load_file_coverage_api()
            return
        
        self._sort_files()
    
    def _load_file_coverage_api(self):
        """Load file coverage using PyUCIS API (fallback)."""
        file_data = {}  # file_id -> FileCoverageInfo
        
        def visit_scope(scope):
            """Visit scope and collect coverage items."""
            # Check all code coverage types
            for cov_type in [CoverTypeT.STMTBIN, CoverTypeT.BRANCHBIN, CoverTypeT.TOGGLEBIN]:
                try:
                    for item in scope.coverItems(cov_type):
                        # Get source information
                        source_info = item.getSourceInfo()
                        if not source_info:
                            continue
                        
                        file_id = source_info.getFileNum()
                        line_no = source_info.getLineNo()
                        
                        # Get file path
                        if file_id not in file_data:
                            try:
                                file_handle = self.model.db.getFileHandle(file_id)
                                if file_handle:
                                    file_path = file_handle.getFileName()
                                    file_data[file_id] = FileCoverageInfo(file_id, file_path)
                            except:
                                continue
                        
                        if file_id not in file_data:
                            continue
                        
                        file_info = file_data[file_id]
                        
                        # Count coverage by type
                        cover_data = item.getCoverData()
                        is_covered = (cover_data and cover_data.data > 0)
                        
                        if cov_type == CoverTypeT.STMTBIN:
                            file_info.line_total += 1
                            if is_covered:
                                file_info.line_covered += 1
                            # Track line-level hits
                            if line_no not in file_info.lines:
                                file_info.lines[line_no] = 0
                            if cover_data:
                                file_info.lines[line_no] = max(file_info.lines[line_no], cover_data.data)
                        elif cov_type == CoverTypeT.BRANCHBIN:
                            file_info.branch_total += 1
                            if is_covered:
                                file_info.branch_covered += 1
                        elif cov_type == CoverTypeT.TOGGLEBIN:
                            file_info.toggle_total += 1
                            if is_covered:
                                file_info.toggle_covered += 1
                except:
                    pass
            
            # Visit children
            try:
                for child in scope.scopes(ScopeTypeT.ALL):
                    visit_scope(child)
            except:
                pass
        
        # Walk all scopes
        if self.model.db:
            for scope in self.model.db.scopes(ScopeTypeT.ALL):
                visit_scope(scope)
        
        # Convert to list and sort
        self.file_coverage = list(file_data.values())
        self._sort_files()
    
    def _sort_files(self):
        """Sort files based on current sort mode."""
        if self.sort_mode == 'coverage':
            # Sort by overall coverage (ascending - worst first)
            self.file_coverage.sort(key=lambda f: f.overall_coverage)
        elif self.sort_mode == 'line':
            # Sort by line coverage (ascending)
            self.file_coverage.sort(key=lambda f: f.line_coverage)
        elif self.sort_mode == 'name':
            # Sort by name (ascending)
            self.file_coverage.sort(key=lambda f: f.file_path)
        
        # Reset selection if out of bounds
        if self.current_index >= len(self.file_coverage):
            self.current_index = 0
    
    def render(self):
        """Render the code coverage view."""
        if self.view_mode == 'detail' and self.selected_file:
            return self._render_file_detail()
        else:
            return self._render_file_list()
    
    def _render_file_list(self):
        """Render the file list view."""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=3)
        )
        
        # Header
        title = Text("Code Coverage by File", style="bold cyan", justify="center")
        sort_info = {
            'coverage': "Overall Coverage",
            'line': "Line Coverage",
            'name': "File Name"
        }
        subtitle = Text(f"Sorted by: {sort_info[self.sort_mode]}", style="dim", justify="center")
        header_panel = Panel(
            Align.center(title + Text("\n") + subtitle),
            border_style="cyan"
        )
        layout["header"].update(header_panel)
        
        # Body - file table
        file_table = self._render_file_table()
        layout["body"].update(Panel(file_table, border_style="cyan"))
        
        # Footer - instructions
        footer_text = Text()
        footer_text.append("↑↓", style="bold cyan")
        footer_text.append(" Navigate  ", style="dim")
        footer_text.append("Enter", style="bold cyan")
        footer_text.append(" View Details  ", style="dim")
        footer_text.append("L", style="bold cyan")
        footer_text.append(" Sort by Line  ", style="dim")
        footer_text.append("O", style="bold cyan")
        footer_text.append(" Sort by Overall  ", style="dim")
        footer_text.append("N", style="bold cyan")
        footer_text.append(" Sort by Name", style="dim")
        layout["footer"].update(Panel(Align.center(footer_text), border_style="blue"))
        
        return layout
    
    def _render_file_table(self):
        """Render the file coverage table."""
        if not self.file_coverage:
            return Text("No code coverage data found in database", style="dim italic", justify="center")
        
        table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 1))
        table.add_column("File", style="white", width=40, no_wrap=True)
        table.add_column("Lines", justify="right", width=12)
        table.add_column("Line %", justify="right", width=10)
        table.add_column("Branches", justify="right", width=12)
        table.add_column("Toggles", justify="right", width=12)
        table.add_column("Overall", justify="right", width=10)
        table.add_column("Status", width=20)
        
        # Determine visible range
        visible_rows = 20  # TODO: Make this dynamic based on terminal height
        start_idx = self.scroll_offset
        end_idx = min(start_idx + visible_rows, len(self.file_coverage))
        
        for idx in range(start_idx, end_idx):
            file_info = self.file_coverage[idx]
            
            # Highlight selected row
            is_selected = (idx == self.current_index)
            row_style = "bold reverse" if is_selected else ""
            
            # Color based on coverage
            overall_pct = file_info.overall_coverage
            if overall_pct >= 90:
                status_color = "green"
            elif overall_pct >= 70:
                status_color = "yellow"
            else:
                status_color = "red"
            
            # Progress bar
            bar_width = 15
            filled = int((overall_pct / 100) * bar_width)
            bar = "█" * filled + "░" * (bar_width - filled)
            
            # Format line coverage
            line_str = f"{file_info.line_covered}/{file_info.line_total}"
            line_pct = f"{file_info.line_coverage:.1f}%"
            
            # Format branch and toggle
            branch_str = f"{file_info.branch_covered}/{file_info.branch_total}" if file_info.branch_total > 0 else "-"
            toggle_str = f"{file_info.toggle_covered}/{file_info.toggle_total}" if file_info.toggle_total > 0 else "-"
            
            # Overall percentage
            overall_str = f"{overall_pct:.1f}%"
            
            table.add_row(
                file_info.file_path,
                line_str,
                Text(line_pct, style=status_color),
                branch_str,
                toggle_str,
                Text(overall_str, style=f"bold {status_color}"),
                Text(bar, style=status_color),
                style=row_style
            )
        
        # Add summary row
        if self.file_coverage:
            total_line_items = sum(f.line_total for f in self.file_coverage)
            covered_line_items = sum(f.line_covered for f in self.file_coverage)
            total_branch = sum(f.branch_total for f in self.file_coverage)
            covered_branch = sum(f.branch_covered for f in self.file_coverage)
            total_toggle = sum(f.toggle_total for f in self.file_coverage)
            covered_toggle = sum(f.toggle_covered for f in self.file_coverage)
            
            total_items = total_line_items + total_branch + total_toggle
            covered_items = covered_line_items + covered_branch + covered_toggle
            overall_pct = (covered_items / total_items * 100) if total_items > 0 else 0
            
            if overall_pct >= 90:
                color = "green"
            elif overall_pct >= 70:
                color = "yellow"
            else:
                color = "red"
            
            bar_width = 15
            filled = int((overall_pct / 100) * bar_width)
            bar = "█" * filled + "░" * (bar_width - filled)
            
            table.add_row(
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                style="dim"
            )
            table.add_row(
                f"Total ({len(self.file_coverage)} files)",
                f"{covered_line_items}/{total_line_items}",
                Text(f"{covered_line_items/total_line_items*100:.1f}%" if total_line_items > 0 else "0%", style=color),
                f"{covered_branch}/{total_branch}" if total_branch > 0 else "-",
                f"{covered_toggle}/{total_toggle}" if total_toggle > 0 else "-",
                Text(f"{overall_pct:.1f}%", style=f"bold {color}"),
                Text(bar, style=color),
                style="bold"
            )
        
        return table
    
    def _render_file_detail(self):
        """Render detailed file view with line-by-line coverage."""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=3)
        )
        
        # Header
        title = Text(f"File: {self.selected_file.file_path}", style="bold cyan")
        stats = Text(f" | Lines: {self.selected_file.line_covered}/{self.selected_file.line_total} ({self.selected_file.line_coverage:.1f}%)", style="dim")
        layout["header"].update(Panel(Align.center(title + stats), border_style="cyan"))
        
        # Body - line-by-line coverage
        detail_table = self._render_line_coverage_table()
        layout["body"].update(Panel(detail_table, border_style="cyan"))
        
        # Footer - instructions
        footer_text = Text()
        footer_text.append("↑↓", style="bold cyan")
        footer_text.append(" Scroll  ", style="dim")
        footer_text.append("PgUp/PgDn", style="bold cyan")
        footer_text.append(" Page  ", style="dim")
        footer_text.append("U", style="bold cyan")
        footer_text.append(" Next Uncovered  ", style="dim")
        footer_text.append("ESC", style="bold cyan")
        footer_text.append(" Back to List", style="dim")
        layout["footer"].update(Panel(Align.center(footer_text), border_style="blue"))
        
        return layout
    
    def _render_line_coverage_table(self):
        """Render line-by-line coverage table."""
        if not self.selected_file:
            return Text("No file selected", style="dim italic")
        
        # Load source file if not already loaded
        if not self.source_lines:
            self._load_source_file()
        
        table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 1))
        table.add_column("Line", justify="right", width=6, style="dim")
        table.add_column("Hits", justify="right", width=8)
        table.add_column("Source Code", style="white", no_wrap=False)
        
        # Determine visible range
        visible_rows = 25  # TODO: Make dynamic based on terminal height
        start_line = self.detail_scroll_offset
        
        if self.source_lines:
            # Have source code - show with coverage
            end_line = min(start_line + visible_rows, len(self.source_lines))
            
            for line_idx in range(start_line, end_line):
                line_no = line_idx + 1
                source = self.source_lines[line_idx].rstrip()
                
                # Get hit count for this line
                hits = self.selected_file.lines.get(line_no, None)
                
                # Determine styling
                if hits is None:
                    # Not executable
                    line_style = "dim"
                    hits_str = "-"
                    hits_style = "dim"
                elif hits > 0:
                    # Covered
                    line_style = "green"
                    hits_str = str(hits)
                    hits_style = "bold green"
                else:
                    # Not covered
                    line_style = "red"
                    hits_str = "0"
                    hits_style = "bold red"
                
                # Truncate very long lines
                if len(source) > 100:
                    source = source[:97] + "..."
                
                table.add_row(
                    str(line_no),
                    Text(hits_str, style=hits_style),
                    Text(source, style=line_style)
                )
        else:
            # No source code - show line numbers with coverage only
            line_numbers = sorted(self.selected_file.lines.keys())
            end_idx = min(start_line + visible_rows, len(line_numbers))
            
            for idx in range(start_line, end_idx):
                if idx >= len(line_numbers):
                    break
                line_no = line_numbers[idx]
                hits = self.selected_file.lines[line_no]
                
                # Determine styling
                if hits > 0:
                    hits_str = str(hits)
                    hits_style = "bold green"
                    msg_style = "green"
                else:
                    hits_str = "0"
                    hits_style = "bold red"
                    msg_style = "red"
                
                table.add_row(
                    str(line_no),
                    Text(hits_str, style=hits_style),
                    Text("<source not available>", style=f"{msg_style} italic")
                )
        
        # Add scroll indicator if needed
        if self.source_lines:
            total_lines = len(self.source_lines)
            if total_lines > visible_rows:
                table.add_row(
                    "",
                    "",
                    Text(f"[Showing lines {start_line+1}-{min(start_line+visible_rows, total_lines)} of {total_lines}]", style="dim italic")
                )
        
        return table
    
    def _load_source_file(self):
        """Load source file content."""
        if not self.selected_file:
            return
        
        # Try to load from file system
        # First try relative to database path
        import os
        db_dir = os.path.dirname(self.model.db_path)
        file_path = os.path.join(db_dir, self.selected_file.file_path)
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    self.source_lines = f.readlines()
                return
            except Exception as e:
                pass
        
        # Try in examples/verilator directory (for testing)
        alt_path = os.path.join(db_dir, '..', self.selected_file.file_path)
        if os.path.exists(alt_path):
            try:
                with open(alt_path, 'r', encoding='utf-8', errors='replace') as f:
                    self.source_lines = f.readlines()
                return
            except Exception as e:
                pass
        
        # Source file not found
        self.source_lines = []
    
    def handle_key(self, key: str) -> bool:
        """Handle key presses for code coverage view."""
        if self.view_mode == 'detail':
            return self._handle_detail_keys(key)
        else:
            return self._handle_list_keys(key)
    
    def _handle_list_keys(self, key: str) -> bool:
        """Handle keys in file list mode."""
        if not self.file_coverage:
            return False
        
        # Navigation
        if key == 'up' and self.current_index > 0:
            self.current_index -= 1
            if self.current_index < self.scroll_offset:
                self.scroll_offset = self.current_index
            return True
        
        elif key == 'down' and self.current_index < len(self.file_coverage) - 1:
            self.current_index += 1
            visible_rows = 20
            if self.current_index >= self.scroll_offset + visible_rows:
                self.scroll_offset = self.current_index - visible_rows + 1
            return True
        
        # View detail
        elif key == 'enter':
            if 0 <= self.current_index < len(self.file_coverage):
                self.selected_file = self.file_coverage[self.current_index]
                self.view_mode = 'detail'
                self.detail_scroll_offset = 0  # Reset scroll
                self.source_lines = []  # Clear cached source
            return True
        
        # Sorting
        elif key in ('l', 'L'):
            self.sort_mode = 'line'
            self._sort_files()
            return True
        
        elif key in ('o', 'O'):
            self.sort_mode = 'coverage'
            self._sort_files()
            return True
        
        elif key in ('n', 'N'):
            self.sort_mode = 'name'
            self._sort_files()
            return True
        
        return False
    
    def _handle_detail_keys(self, key: str) -> bool:
        """Handle keys in file detail mode."""
        # Return to list
        if key == 'esc':
            self.view_mode = 'list'
            self.selected_file = None
            self.source_lines = []
            self.detail_scroll_offset = 0
            return True
        
        # Scrolling
        max_lines = len(self.source_lines) if self.source_lines else len(self.selected_file.lines)
        visible_rows = 25
        
        if key == 'up' and self.detail_scroll_offset > 0:
            self.detail_scroll_offset -= 1
            return True
        
        elif key == 'down' and self.detail_scroll_offset < max(0, max_lines - visible_rows):
            self.detail_scroll_offset += 1
            return True
        
        elif key == 'pageup':
            self.detail_scroll_offset = max(0, self.detail_scroll_offset - visible_rows)
            return True
        
        elif key == 'pagedown':
            self.detail_scroll_offset = min(max(0, max_lines - visible_rows), self.detail_scroll_offset + visible_rows)
            return True
        
        elif key == 'home':
            self.detail_scroll_offset = 0
            return True
        
        elif key == 'end':
            self.detail_scroll_offset = max(0, max_lines - visible_rows)
            return True
        
        # Jump to next uncovered line
        elif key in ('u', 'U'):
            self._jump_to_next_uncovered()
            return True
        
        return False
    
    def _jump_to_next_uncovered(self):
        """Jump to the next uncovered line."""
        if not self.selected_file:
            return
        
        # Get all uncovered lines
        uncovered_lines = sorted([line_no for line_no, hits in self.selected_file.lines.items() if hits == 0])
        
        if not uncovered_lines:
            return  # All lines covered
        
        # Find next uncovered line after current scroll position
        current_line = self.detail_scroll_offset + 1
        for line_no in uncovered_lines:
            if line_no > current_line:
                # Found next uncovered line
                self.detail_scroll_offset = max(0, line_no - 1)
                return
        
        # Wrap around to first uncovered line
        if uncovered_lines:
            self.detail_scroll_offset = max(0, uncovered_lines[0] - 1)
