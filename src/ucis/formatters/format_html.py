"""
HTML Interactive Report Formatter

Generates a single-file interactive HTML coverage report for UCIS data.
The report includes hierarchical navigation, filtering, visualization,
and source code viewing capabilities.
"""
import json
import base64
import gzip
from typing import TextIO, Dict, List, Any, Optional
from ucis.scope_type_t import ScopeTypeT
from ucis.cover_type_t import CoverTypeT


class HtmlFormatter:
    """
    Format UCIS data as interactive HTML report.
    
    Generates a self-contained HTML file with:
    - Embedded coverage data (JSON, optionally compressed)
    - Interactive UI (Alpine.js)
    - Visualizations (D3.js)
    - Source code viewer (Prism.js)
    """
    
    def __init__(self, 
                 include_source: bool = True,
                 compress: bool = True,
                 theme: str = 'light'):
        """
        Initialize HTML formatter.
        
        Args:
            include_source: Embed source file contents in report
            compress: Compress JSON data with gzip
            theme: Default theme ('light' or 'dark')
        """
        self.include_source = include_source
        self.compress = compress
        self.theme = theme
    
    def format(self, db, output: TextIO):
        """
        Generate single-file HTML report.
        
        Args:
            db: UCIS database
            output: Output file/stream
        """
        # 1. Extract coverage data
        data = self._build_coverage_data(db)
        
        # 2. Optionally embed source files
        if self.include_source:
            data['sources'] = self._extract_sources(db)
        
        # 3. Prepare data for embedding
        if self.compress:
            data_json = self._compress_json(data)
            data_attr = 'data-compressed="true"'
        else:
            data_json = json.dumps(data, indent=2)
            data_attr = 'data-compressed="false"'
        
        # 4. Render HTML template
        html = self._render_template(data_json, data_attr, self.theme)
        
        # 5. Write output
        output.write(html)
    
    def _build_coverage_data(self, db) -> Dict[str, Any]:
        """
        Extract coverage data from UCIS database.
        
        Returns:
            Dictionary with coverage data in JSON-serializable format
        """
        data = {
            'metadata': self._extract_metadata(db),
            'summary': self._calculate_summary(db),
            'scopes': self._extract_scopes(db),
        }
        return data
    
    def _extract_metadata(self, db) -> Dict[str, Any]:
        """Extract database metadata."""
        return {
            'ucis_version': '1.0',
            'generator': 'pyucis',
            'timestamp': self._get_timestamp(),
            'test_name': self._get_test_name(db),
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _get_test_name(self, db) -> Optional[str]:
        """Get test name from database if available."""
        # Try to get test data
        try:
            if hasattr(db, 'tests'):
                for test in db.tests():
                    if hasattr(test, 'getTestName'):
                        return test.getTestName()
        except:
            pass
        return None
    
    def _calculate_summary(self, db) -> Dict[str, Any]:
        """Calculate overall coverage summary."""
        summary = {
            'total_coverage': 0.0,
            'coverage_by_type': {},
            'total_items': 0,
            'covered_items': 0,
            'uncovered_items': 0,
        }
        
        # Calculate coverage by type
        type_stats = {}
        
        # Iterate through all scopes (use None to get all)
        try:
            for scope in db.scopes(None):
                self._accumulate_coverage(scope, type_stats)
        except:
            # If scopes() doesn't work with None, try without it
            pass
        
        # Calculate percentages
        for cov_type, stats in type_stats.items():
            if stats['total'] > 0:
                stats['percentage'] = (stats['covered'] / stats['total']) * 100
            else:
                stats['percentage'] = 0.0
            summary['coverage_by_type'][cov_type] = stats['percentage']
            summary['total_items'] += stats['total']
            summary['covered_items'] += stats['covered']
        
        summary['uncovered_items'] = summary['total_items'] - summary['covered_items']
        
        if summary['total_items'] > 0:
            summary['total_coverage'] = (summary['covered_items'] / summary['total_items']) * 100
        
        return summary
    
    def _accumulate_coverage(self, scope, type_stats: Dict):
        """Recursively accumulate coverage statistics."""
        # Process cover items in this scope
        for cover_item in scope.coverItems():
            cov_type = self._get_cover_type_name(cover_item.getType())
            
            if cov_type not in type_stats:
                type_stats[cov_type] = {'total': 0, 'covered': 0}
            
            type_stats[cov_type]['total'] += 1
            
            # Check if covered
            cover_data = cover_item.getCoverData()
            if cover_data and cover_data.data > 0:
                type_stats[cov_type]['covered'] += 1
        
        # Recurse into child scopes
        try:
            for child in scope.scopes(None):
                self._accumulate_coverage(child, type_stats)
        except:
            pass
    
    def _get_cover_type_name(self, cover_type: CoverTypeT) -> str:
        """Convert cover type enum to string."""
        type_names = {
            CoverTypeT.CVGBIN: 'functional',
            CoverTypeT.STMTBIN: 'line',
            CoverTypeT.BRANCHBIN: 'branch',
            CoverTypeT.EXPRBIN: 'expression',
            CoverTypeT.CONDBIN: 'condition',
            CoverTypeT.TOGGLEBIN: 'toggle',
            CoverTypeT.BLOCKBIN: 'block',
            CoverTypeT.FSMBIN: 'fsm',
        }
        return type_names.get(cover_type, 'other')
    
    def _extract_scopes(self, db) -> List[Dict[str, Any]]:
        """Extract scope hierarchy."""
        scopes = []
        scope_id = [0]  # Use list to maintain reference
        
        try:
            for scope in db.scopes(None):
                scope_data = self._extract_scope(scope, scope_id)
                if scope_data:
                    scopes.append(scope_data)
        except:
            pass
        
        return scopes
    
    def _extract_scope(self, scope, scope_id: List[int]) -> Optional[Dict[str, Any]]:
        """Extract single scope with recursion."""
        current_id = f"scope_{scope_id[0]}"
        scope_id[0] += 1
        
        scope_type = scope.getScopeType()
        scope_data = {
            'id': current_id,
            'name': scope.getScopeName(),
            'type': self._get_scope_type_name(scope_type),
            'coverage': self._calculate_scope_coverage(scope),
            'weight': scope.getWeight(),
            'children': [],
            'coveritems': [],
            'bins': [],  # For coverpoint bins
        }
        
        # Extract source location if available
        source_info = scope.getSourceInfo()
        if source_info:
            scope_data['source'] = {
                'file': source_info.getFileName(),
                'line': source_info.getLineNum(),
                'column': source_info.getToken(),
            }
        
        # For coverpoints, extract bin details
        if scope_type == ScopeTypeT.COVERPOINT:
            scope_data['bins'] = self._extract_coverpoint_bins(scope)
            
            # Add coverpoint-specific attributes
            try:
                scope_data['at_least'] = scope.getAtLeast() if hasattr(scope, 'getAtLeast') else 1
            except:
                scope_data['at_least'] = 1
        
        # Extract child scopes
        try:
            for child in scope.scopes(None):
                child_data = self._extract_scope(child, scope_id)
                if child_data:
                    scope_data['children'].append(child_data)
        except:
            pass
        
        # Extract cover items (non-bin items)
        for cover_item in scope.coverItems():
            item_data = self._extract_cover_item(cover_item)
            if item_data:
                scope_data['coveritems'].append(item_data)
        
        return scope_data
    
    def _get_scope_type_name(self, scope_type: ScopeTypeT) -> str:
        """Convert scope type enum to string."""
        return scope_type.name
    
    def _calculate_scope_coverage(self, scope) -> float:
        """Calculate coverage percentage for a scope."""
        total = 0
        covered = 0
        
        # Count cover items
        for cover_item in scope.coverItems():
            total += 1
            cover_data = cover_item.getCoverData()
            if cover_data and cover_data.data > 0:
                covered += 1
        
        # Recurse into children
        try:
            for child in scope.scopes(None):
                child_total, child_covered = self._count_coverage(child)
                total += child_total
                covered += child_covered
        except:
            pass
        
        if total > 0:
            return (covered / total) * 100
        return 0.0
    
    def _count_coverage(self, scope) -> tuple:
        """Count total and covered items recursively."""
        total = 0
        covered = 0
        
        for cover_item in scope.coverItems():
            total += 1
            cover_data = cover_item.getCoverData()
            if cover_data and cover_data.data > 0:
                covered += 1
        
        try:
            for child in scope.scopes(None):
                child_total, child_covered = self._count_coverage(child)
                total += child_total
                covered += child_covered
        except:
            pass
        
        return total, covered
    
    def _extract_cover_item(self, cover_item) -> Optional[Dict[str, Any]]:
        """Extract cover item data."""
        cover_data = cover_item.getCoverData()
        if not cover_data:
            return None
        
        item_data = {
            'name': cover_item.getName(),
            'type': self._get_cover_type_name(cover_item.getType()),
            'hits': cover_data.data,
            'goal': cover_data.at_least if hasattr(cover_data, 'at_least') else 1,
            'status': 'covered' if cover_data.data > 0 else 'uncovered',
        }
        
        # Extract source location if available
        source_info = cover_item.getSourceInfo()
        if source_info:
            item_data['source'] = {
                'file': source_info.getFileName(),
                'line': source_info.getLineNum(),
                'column': source_info.getToken(),
            }
        
        return item_data
    
    def _extract_coverpoint_bins(self, coverpoint) -> List[Dict[str, Any]]:
        """Extract bin information from a coverpoint scope."""
        bins = []
        
        try:
            # Iterate through all bin types
            bin_mask = CoverTypeT.CVGBIN | CoverTypeT.IGNOREBIN | CoverTypeT.ILLEGALBIN
            for bin_idx in coverpoint.coverItems(bin_mask):
                cover_data = bin_idx.getCoverData()
                if not cover_data:
                    continue
                
                bin_type = cover_data.type
                hits = cover_data.data
                
                # Determine goal (at_least threshold)
                try:
                    goal = coverpoint.getAtLeast() if hasattr(coverpoint, 'getAtLeast') else 1
                except:
                    goal = 1
                
                # Check if goal is set on the bin itself
                if hasattr(cover_data, 'goal') and cover_data.goal is not None:
                    goal = cover_data.goal
                
                # Determine bin status
                if bin_type == CoverTypeT.IGNOREBIN:
                    status = 'ignored'
                elif bin_type == CoverTypeT.ILLEGALBIN:
                    status = 'illegal' if hits > 0 else 'ok'
                else:  # CVGBIN
                    status = 'covered' if hits >= goal else 'uncovered'
                
                bin_data = {
                    'name': bin_idx.getName(),
                    'type': self._get_bin_type_name(bin_type),
                    'hits': hits,
                    'goal': goal,
                    'status': status,
                    'weight': cover_data.weight if hasattr(cover_data, 'weight') else 1,
                }
                
                # Extract source location if available
                source_info = bin_idx.getSourceInfo()
                if source_info:
                    bin_data['source'] = {
                        'file': source_info.getFileName(),
                        'line': source_info.getLineNum(),
                        'column': source_info.getToken(),
                    }
                
                bins.append(bin_data)
        except Exception as e:
            # Silently handle errors (scope might not support coverItems)
            pass
        
        return bins
    
    def _get_bin_type_name(self, bin_type: CoverTypeT) -> str:
        """Convert bin type enum to human-readable string."""
        if bin_type == CoverTypeT.CVGBIN:
            return 'bin'
        elif bin_type == CoverTypeT.IGNOREBIN:
            return 'ignore_bin'
        elif bin_type == CoverTypeT.ILLEGALBIN:
            return 'illegal_bin'
        elif bin_type == CoverTypeT.DEFAULTBIN:
            return 'default_bin'
        else:
            return 'unknown'
    
    def _extract_sources(self, db) -> Dict[str, Dict[str, Any]]:
        """Extract source file information."""
        sources = {}
        
        # Collect all unique source files
        source_files = set()
        
        def collect_sources(scope):
            source_info = scope.getSourceInfo()
            if source_info:
                file_path = source_info.getFileName()
                if file_path:
                    source_files.add(file_path)
            
            try:
                for child in scope.scopes(None):
                    collect_sources(child)
            except:
                pass
            
            for cover_item in scope.coverItems():
                source_info = cover_item.getSourceInfo()
                if source_info:
                    file_path = source_info.getFileName()
                    if file_path:
                        source_files.add(file_path)
        
        try:
            for scope in db.scopes(None):
                collect_sources(scope)
        except:
            pass
        
        # For now, just record file paths (actual source loading would require file system access)
        for file_path in source_files:
            sources[file_path] = {
                'path': file_path,
                'language': self._detect_language(file_path),
                'content': None,  # Could be populated if files are accessible
            }
        
        return sources
    
    def _detect_language(self, file_path: str) -> str:
        """Detect source language from file extension."""
        if file_path.endswith('.v'):
            return 'verilog'
        elif file_path.endswith('.sv'):
            return 'systemverilog'
        elif file_path.endswith('.vhd') or file_path.endswith('.vhdl'):
            return 'vhdl'
        elif file_path.endswith('.c'):
            return 'c'
        elif file_path.endswith('.cpp') or file_path.endswith('.cc'):
            return 'cpp'
        return 'unknown'
    
    def _compress_json(self, data: Dict) -> str:
        """Compress JSON data with gzip and base64 encode."""
        json_str = json.dumps(data, separators=(',', ':'))
        json_bytes = json_str.encode('utf-8')
        compressed = gzip.compress(json_bytes, compresslevel=9)
        encoded = base64.b64encode(compressed).decode('ascii')
        return encoded
    
    def _render_template(self, data_json: str, data_attr: str, theme: str) -> str:
        """Render HTML template with embedded data."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UCIS Coverage Report</title>
    <style>
        {self._get_css()}
    </style>
</head>
<body>
    <div id="app" x-data="coverageApp">
        <header>
            <h1>🎯 UCIS Coverage Report</h1>
            <div class="header-meta" x-text="'Generated: ' + (data.metadata?.timestamp || 'N/A') + ' | Generator: ' + (data.metadata?.generator || 'pyucis')"></div>
            
            <!-- Navigation Tabs -->
            <nav>
                <button class="nav-tab" :class="{{ 'active': currentView === 'summary' }}" @click="switchView('summary')">Summary</button>
                <button class="nav-tab" :class="{{ 'active': currentView === 'hierarchy' }}" @click="switchView('hierarchy')">Hierarchy</button>
                <button class="nav-tab" :class="{{ 'active': currentView === 'gaps' }}" @click="switchView('gaps')">Coverage Gaps</button>
                <button class="nav-tab" :class="{{ 'active': currentView === 'types' }}" @click="switchView('types')">By Type</button>
                <button class="nav-tab" :class="{{ 'active': currentView === 'visualizations' }}" @click="switchView('visualizations')">📊 Charts</button>
            </nav>
        </header>
        
        <main>
            <!-- Summary View -->
            <div x-show="currentView === 'summary'" class="card">
                <h2>📊 Coverage Summary</h2>
                
                <div class="metric-grid">
                    <div class="metric">
                        <div class="metric-label">Total Coverage</div>
                        <div class="metric-value" :class="{{ 
                            'success': totalCoverage >= 80, 
                            'warning': totalCoverage >= 50 && totalCoverage < 80, 
                            'danger': totalCoverage < 50 
                        }}" x-text="formatCoverage(totalCoverage)"></div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Total Items</div>
                        <div class="metric-value" x-text="totalItems.toLocaleString()"></div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Covered</div>
                        <div class="metric-value success" x-text="coveredItems.toLocaleString()"></div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Uncovered</div>
                        <div class="metric-value danger" x-text="uncoveredItems.toLocaleString()"></div>
                    </div>
                </div>
                
                <h3>Overall Progress</h3>
                <div class="progress-bar">
                    <div class="progress-fill" :style="'width: ' + totalCoverage + '%'" x-text="formatCoverage(totalCoverage)"></div>
                </div>
            </div>
            
            <!-- Hierarchy View -->
            <div x-show="currentView === 'hierarchy'" class="card">
                <h2>🏗️ Design Hierarchy</h2>
                
                <!-- Filters -->
                <div class="filters">
                    <div class="filter-group">
                        <label class="filter-label">Search</label>
                        <input type="text" class="filter-input" placeholder="Search scopes..." x-model="searchQuery">
                    </div>
                    
                    <div class="filter-group">
                        <label class="filter-label">Status</label>
                        <select class="filter-select" x-model="filterStatus">
                            <option value="all">All</option>
                            <option value="covered">Covered</option>
                            <option value="uncovered">Uncovered</option>
                            <option value="partial">Partial</option>
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <label class="filter-label">Min Coverage</label>
                        <input type="number" class="filter-input" style="width: 80px;" min="0" max="100" x-model.number="filterThreshold">
                    </div>
                    
                    <div class="filter-group" style="justify-content: flex-end;">
                        <label class="filter-label">&nbsp;</label>
                        <button class="btn btn-secondary" @click="resetFilters()">Reset</button>
                    </div>
                </div>
                
                <!-- Tree Controls -->
                <div class="tree-controls">
                    <button class="btn btn-primary" @click="expandAllScopes()">Expand All</button>
                    <button class="btn btn-secondary" @click="collapseAllScopes()">Collapse All</button>
                </div>
                
                <!-- Tree View -->
                <div class="tree">
                    <template x-if="filteredScopes.length === 0">
                        <div class="text-center" style="padding: 2rem; color: #999;">
                            No scopes match the current filters
                        </div>
                    </template>
                    
                    <!-- Recursive tree rendering -->
                    <template x-for="scope in filteredScopes" :key="scope.id">
                        <div>
                            <div class="tree-item" 
                                 :class="{{ 'selected': selectedScope?.id === scope.id }}"
                                 @click="selectScope(scope)"
                                 style="padding-left: 0.5rem;">
                                <span class="tree-toggle" 
                                      @click.stop="toggleScope(scope.id)"
                                      x-show="scope.children && scope.children.length > 0"
                                      x-text="isScopeExpanded(scope.id) ? '▼' : '▶'"></span>
                                <span class="tree-icon" x-text="getScopeIcon(scope.type)"></span>
                                <span class="tree-name" x-text="scope.name"></span>
                                <span class="tree-type" style="color: #999; font-size: 0.8rem; margin-left: 0.5rem;" x-text="'(' + scope.type + ')'"></span>
                                <span class="tree-coverage" 
                                      :class="getCoverageClass(scope.coverage)"
                                      x-text="formatCoverage(scope.coverage)"></span>
                            </div>
                            
                            <!-- First level children -->
                            <template x-if="isScopeExpanded(scope.id) && scope.children && scope.children.length > 0">
                                <div class="tree-children">
                                    <template x-for="child1 in scope.children" :key="child1.id">
                                        <div>
                                            <div class="tree-item" 
                                                 :class="{{ 'selected': selectedScope?.id === child1.id }}"
                                                 @click="selectScope(child1)"
                                                 style="padding-left: 2rem;">
                                                <span class="tree-toggle" 
                                                      @click.stop="toggleScope(child1.id)"
                                                      x-show="child1.children && child1.children.length > 0"
                                                      x-text="isScopeExpanded(child1.id) ? '▼' : '▶'"></span>
                                                <span class="tree-icon" x-text="getScopeIcon(child1.type)"></span>
                                                <span class="tree-name" x-text="child1.name"></span>
                                                <span class="tree-type" style="color: #999; font-size: 0.8rem; margin-left: 0.5rem;" x-text="'(' + child1.type + ')'"></span>
                                                <span class="tree-coverage" 
                                                      :class="getCoverageClass(child1.coverage)"
                                                      x-text="formatCoverage(child1.coverage)"></span>
                                            </div>
                                            
                                            <!-- Second level children -->
                                            <template x-if="isScopeExpanded(child1.id) && child1.children && child1.children.length > 0">
                                                <div class="tree-children">
                                                    <template x-for="child2 in child1.children" :key="child2.id">
                                                        <div>
                                                            <div class="tree-item" 
                                                                 :class="{{ 'selected': selectedScope?.id === child2.id }}"
                                                                 @click="selectScope(child2)"
                                                                 style="padding-left: 3.5rem;">
                                                                <span class="tree-toggle" 
                                                                      @click.stop="toggleScope(child2.id)"
                                                                      x-show="child2.children && child2.children.length > 0"
                                                                      x-text="isScopeExpanded(child2.id) ? '▼' : '▶'"></span>
                                                                <span class="tree-icon" x-text="getScopeIcon(child2.type)"></span>
                                                                <span class="tree-name" x-text="child2.name"></span>
                                                                <span class="tree-type" style="color: #999; font-size: 0.8rem; margin-left: 0.5rem;" x-text="'(' + child2.type + ')'"></span>
                                                                <span class="tree-coverage" 
                                                                      :class="getCoverageClass(child2.coverage)"
                                                                      x-text="formatCoverage(child2.coverage)"></span>
                                                            </div>
                                                            
                                                            <!-- Third level children -->
                                                            <template x-if="isScopeExpanded(child2.id) && child2.children && child2.children.length > 0">
                                                                <div class="tree-children">
                                                                    <template x-for="child3 in child2.children" :key="child3.id">
                                                                        <div class="tree-item" 
                                                                             :class="{{ 'selected': selectedScope?.id === child3.id }}"
                                                                             @click="selectScope(child3)"
                                                                             style="padding-left: 5rem;">
                                                                            <span class="tree-icon" x-text="getScopeIcon(child3.type)"></span>
                                                                            <span class="tree-name" x-text="child3.name"></span>
                                                                            <span class="tree-type" style="color: #999; font-size: 0.8rem; margin-left: 0.5rem;" x-text="'(' + child3.type + ')'"></span>
                                                                            <span class="tree-coverage" 
                                                                                  :class="getCoverageClass(child3.coverage)"
                                                                                  x-text="formatCoverage(child3.coverage)"></span>
                                                                        </div>
                                                                    </template>
                                                                </div>
                                                            </template>
                                                        </div>
                                                    </template>
                                                </div>
                                            </template>
                                        </div>
                                    </template>
                                </div>
                            </template>
                        </div>
                    </template>
                </div>
                
                <!-- Bin Details Panel (shown when coverpoint selected) -->
                <div x-show="selectedScope && selectedScope.type === 'COVERPOINT' && selectedScope.bins && selectedScope.bins.length > 0" 
                     class="card" style="margin-top: 1rem;">
                    <h3>📊 Coverpoint Bins: <span x-text="selectedScope?.name"></span></h3>
                    <p class="mb-2" style="color: #666;">
                        <span x-text="selectedScope?.bins?.length || 0"></span> bins | 
                        At Least: <span x-text="selectedScope?.at_least || 1"></span>
                    </p>
                    
                    <table class="bin-table">
                        <thead>
                            <tr>
                                <th>Bin Name</th>
                                <th>Type</th>
                                <th>Hits</th>
                                <th>Goal</th>
                                <th>Status</th>
                                <th>Coverage</th>
                            </tr>
                        </thead>
                        <tbody>
                            <template x-for="bin in selectedScope.bins" :key="bin.name">
                                <tr :class="getBinRowClass(bin)">
                                    <td class="bin-name" x-text="bin.name"></td>
                                    <td class="bin-type">
                                        <span class="badge" 
                                              :class="{{
                                                  'badge-info': bin.type === 'bin',
                                                  'badge-warning': bin.type === 'ignore_bin',
                                                  'badge-danger': bin.type === 'illegal_bin'
                                              }}"
                                              x-text="bin.type"></span>
                                    </td>
                                    <td class="bin-hits" x-text="bin.hits.toLocaleString()"></td>
                                    <td class="bin-goal" x-text="bin.goal"></td>
                                    <td class="bin-status">
                                        <span class="badge"
                                              :class="{{
                                                  'badge-success': bin.status === 'covered',
                                                  'badge-danger': bin.status === 'uncovered' || bin.status === 'illegal',
                                                  'badge-secondary': bin.status === 'ignored',
                                                  'badge-success': bin.status === 'ok'
                                              }}"
                                              x-text="bin.status"></span>
                                    </td>
                                    <td class="bin-coverage">
                                        <div class="progress-bar-small">
                                            <div class="progress-fill-small" 
                                                 :class="{{
                                                     'success': bin.hits >= bin.goal,
                                                     'warning': bin.hits > 0 && bin.hits < bin.goal,
                                                     'danger': bin.hits === 0
                                                 }}"
                                                 :style="'width: ' + Math.min(100, (bin.hits / bin.goal * 100)) + '%'">
                                            </div>
                                        </div>
                                        <span class="coverage-percent" x-text="Math.min(100, (bin.hits / bin.goal * 100)).toFixed(0) + '%'"></span>
                                    </td>
                                </tr>
                            </template>
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Coverage Gaps View -->
            <div x-show="currentView === 'gaps'" class="card">
                <h2>⚠️ Coverage Gaps</h2>
                <p class="mb-2">Showing items with less than 100% coverage</p>
                
                <div class="tree">
                    <template x-for="scope in filteredScopes.filter(s => s.coverage < 100)" :key="scope.id">
                        <div class="tree-item">
                            <span class="tree-icon">⚠️</span>
                            <span class="tree-name" x-text="scope.name"></span>
                            <span class="tree-coverage coverage-low" x-text="formatCoverage(scope.coverage)"></span>
                        </div>
                    </template>
                </div>
            </div>
            
            <!-- By Type View -->
            <div x-show="currentView === 'types'" class="card">
                <h2>📈 Coverage by Type</h2>
                
                <ul class="coverage-list">
                    <template x-for="(percentage, type) in coverageByType" :key="type">
                        <li class="coverage-item">
                            <span class="coverage-name" x-text="type"></span>
                            <span class="coverage-value" x-text="percentage.toFixed(1) + '%'"></span>
                        </li>
                    </template>
                </ul>
            </div>
            
            <!-- Visualizations View -->
            <div x-show="currentView === 'visualizations'">
                <div class="card">
                    <h2>📊 Coverage by Type</h2>
                    <div id="pie-chart" class="chart-container"></div>
                </div>
                
                <div class="card">
                    <h2>📉 Top Coverage Gaps (Lowest Coverage)</h2>
                    <div id="bar-chart" class="chart-container"></div>
                </div>
                
                <div class="card">
                    <h2>🗺️ Coverage Treemap</h2>
                    <p class="mb-2">Hierarchical view of coverage. Larger boxes = more items. Color indicates coverage %.</p>
                    <div id="treemap-chart" class="chart-container"></div>
                </div>
            </div>
        </main>
    </div>
    
    <!-- Coverage Data -->
    <script id="coverage-data" type="application/json" {data_attr}>
{data_json}
    </script>
    
    <!-- Application -->
    <script>
        {self._get_javascript()}
    </script>
</body>
</html>"""
    
    def _get_css(self) -> str:
        """Get CSS styles."""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }
        
        h1 {
            font-size: 1.8rem;
            font-weight: 600;
        }
        
        .header-meta {
            font-size: 0.9rem;
            opacity: 0.9;
            margin-top: 0.5rem;
        }
        
        nav {
            display: flex;
            gap: 0.5rem;
            margin-top: 1rem;
            flex-wrap: wrap;
        }
        
        .nav-tab {
            padding: 0.5rem 1rem;
            background: rgba(255,255,255,0.1);
            border: none;
            color: white;
            cursor: pointer;
            border-radius: 4px;
            transition: background 0.2s;
        }
        
        .nav-tab:hover {
            background: rgba(255,255,255,0.2);
        }
        
        .nav-tab.active {
            background: rgba(255,255,255,0.3);
            font-weight: bold;
        }
        
        main {
            max-width: 1400px;
            margin: 2rem auto;
            padding: 0 2rem;
        }
        
        .card {
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        h2 {
            margin-bottom: 1rem;
            color: #2c3e50;
            border-bottom: 2px solid #667eea;
            padding-bottom: 0.5rem;
        }
        
        h3 {
            margin: 1.5rem 0 0.75rem 0;
            color: #555;
        }
        
        /* Charts */
        .chart-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem;
            margin: 1.5rem 0;
        }
        
        .chart-container {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            min-height: 300px;
        }
        
        .chart-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 1rem;
            text-align: center;
        }
        
        .chart {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .chart svg {
            overflow: visible;
        }
        
        .tooltip {
            position: absolute;
            padding: 0.5rem 0.75rem;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            border-radius: 4px;
            font-size: 0.85rem;
            pointer-events: none;
            z-index: 1000;
            white-space: nowrap;
        }
        
        /* Metrics */
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
        }
        
        .metric {
            padding: 1rem;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 6px;
            text-align: center;
        }
        
        .metric-label {
            font-size: 0.85rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #2c3e50;
            margin-top: 0.25rem;
        }
        
        .metric-value.success { color: #27ae60; }
        .metric-value.warning { color: #f39c12; }
        .metric-value.danger { color: #e74c3c; }
        
        /* Progress bars */
        .progress-bar {
            background: #ecf0f1;
            border-radius: 10px;
            height: 24px;
            overflow: hidden;
            margin: 0.5rem 0;
        }
        
        .progress-fill {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 8px;
            color: white;
            font-weight: bold;
            font-size: 0.85rem;
        }
        
        /* Filters */
        .filters {
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
            align-items: center;
        }
        
        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }
        
        .filter-label {
            font-size: 0.85rem;
            color: #666;
            font-weight: 500;
        }
        
        .filter-input, .filter-select {
            padding: 0.5rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 0.9rem;
        }
        
        .filter-input:focus, .filter-select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5568d3;
        }
        
        .btn-secondary {
            background: #95a5a6;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #7f8c8d;
        }
        
        /* Tree view */
        .tree-controls {
            margin-bottom: 1rem;
            display: flex;
            gap: 0.5rem;
        }
        
        .tree {
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
        }
        
        .tree-item {
            padding: 0.4rem 0.5rem;
            margin: 0.15rem 0;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.2s;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .tree-item:hover {
            background: #f8f9fa;
        }
        
        .tree-item.selected {
            background: #e3f2fd;
            border-left: 3px solid #667eea;
        }
        
        .tree-toggle {
            cursor: pointer;
            user-select: none;
            width: 16px;
            height: 16px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: #666;
        }
        
        .tree-icon {
            margin-right: 0.25rem;
        }
        
        .tree-name {
            flex: 1;
        }
        
        .tree-coverage {
            font-weight: bold;
            padding: 0.15rem 0.4rem;
            border-radius: 3px;
            font-size: 0.85rem;
        }
        
        .coverage-high { background: #d4edda; color: #155724; }
        .coverage-medium { background: #fff3cd; color: #856404; }
        .coverage-low { background: #f8d7da; color: #721c24; }
        
        .tree-children {
            margin-left: 1.5rem;
        }
        
        /* Coverage type list */
        .coverage-list {
            list-style: none;
        }
        
        .coverage-item {
            padding: 0.75rem;
            margin: 0.5rem 0;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .coverage-name {
            font-weight: 500;
            text-transform: capitalize;
        }
        
        .coverage-value {
            font-weight: bold;
            color: #667eea;
        }
        
        /* Bin table */
        .bin-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
            font-size: 0.9rem;
        }
        
        .bin-table thead {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .bin-table th {
            padding: 0.75rem;
            text-align: left;
            font-weight: 600;
        }
        
        .bin-table td {
            padding: 0.75rem;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .bin-table tbody tr:hover {
            background: #f8f9fa;
        }
        
        .bin-table tbody tr.bin-illegal {
            background: #ffebee;
        }
        
        .bin-table tbody tr.bin-covered {
            background: #e8f5e9;
        }
        
        .bin-name {
            font-family: 'Courier New', monospace;
            font-weight: 500;
        }
        
        .bin-hits, .bin-goal {
            text-align: right;
            font-family: 'Courier New', monospace;
        }
        
        .bin-coverage {
            min-width: 150px;
        }
        
        .progress-bar-small {
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            position: relative;
            display: inline-block;
            width: 80px;
            margin-right: 0.5rem;
            vertical-align: middle;
        }
        
        .progress-fill-small {
            height: 100%;
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .progress-fill-small.success {
            background: linear-gradient(90deg, #27ae60, #2ecc71);
        }
        
        .progress-fill-small.warning {
            background: linear-gradient(90deg, #f39c12, #f1c40f);
        }
        
        .progress-fill-small.danger {
            background: linear-gradient(90deg, #e74c3c, #c0392b);
        }
        
        .coverage-percent {
            font-size: 0.85rem;
            font-weight: 600;
            color: #666;
        }
        
        .badge {
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .badge-success {
            background: #27ae60;
            color: white;
        }
        
        .badge-danger {
            background: #e74c3c;
            color: white;
        }
        
        .badge-warning {
            background: #f39c12;
            color: white;
        }
        
        .badge-info {
            background: #3498db;
            color: white;
        }
        
        .badge-secondary {
            background: #95a5a6;
            color: white;
        }
        
        /* Source code viewer */
        .source-viewer {
            background: #282c34;
            border-radius: 8px;
            overflow: hidden;
            margin: 1rem 0;
        }
        
        .source-header {
            background: #21252b;
            padding: 0.75rem 1rem;
            color: #abb2bf;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            border-bottom: 1px solid #181a1f;
        }
        
        .source-code {
            overflow-x: auto;
            max-height: 600px;
            overflow-y: auto;
        }
        
        .code-line {
            display: flex;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            line-height: 1.5;
        }
        
        .code-line:hover {
            background: rgba(255, 255, 255, 0.05);
        }
        
        .line-number {
            flex-shrink: 0;
            width: 50px;
            padding: 0.1rem 0.75rem;
            text-align: right;
            color: #5c6370;
            background: #282c34;
            user-select: none;
            border-right: 1px solid #181a1f;
        }
        
        .line-coverage {
            flex-shrink: 0;
            width: 40px;
            padding: 0.1rem 0.5rem;
            text-align: center;
            font-size: 0.75rem;
            font-weight: bold;
        }
        
        .line-coverage.covered {
            background: #1e7e34;
            color: #a8e6cf;
        }
        
        .line-coverage.uncovered {
            background: #8b0000;
            color: #ffb3b3;
        }
        
        .line-coverage.partial {
            background: #856404;
            color: #ffd966;
        }
        
        .line-content {
            flex: 1;
            padding: 0.1rem 1rem;
            color: #abb2bf;
            white-space: pre;
        }
        
        /* D3 chart styles */
        .arc text {
            font-size: 12px;
            font-weight: bold;
            fill: white;
            text-anchor: middle;
        }
        
        .bar-label {
            font-size: 12px;
            fill: #333;
        }
        
        .axis text {
            font-size: 11px;
            fill: #666;
        }
        
        .axis path,
        .axis line {
            stroke: #ddd;
        }
        
        /* Treemap */
        .treemap-cell {
            stroke: white;
            stroke-width: 2;
            cursor: pointer;
        }
        
        .treemap-cell:hover {
            stroke: #667eea;
            stroke-width: 3;
        }
        
        .treemap-label {
            font-size: 11px;
            fill: white;
            pointer-events: none;
            text-anchor: middle;
        }
        
        /* Utility */
        .hidden {
            display: none !important;
        }
        
        .text-center {
            text-align: center;
        }
        
        .mt-1 { margin-top: 0.5rem; }
        .mt-2 { margin-top: 1rem; }
        .mb-1 { margin-bottom: 0.5rem; }
        .mb-2 { margin-bottom: 1rem; }
        """
    
    def _get_javascript(self) -> str:
        """Get JavaScript application code."""
        return """
        // Alpine.js (v3.x) - Lightweight reactive framework
        // D3.js (v7.x) - Data visualization
        // Using CDN for simplicity - can be inlined in production
        
        document.addEventListener('alpine:init', () => {
            Alpine.data('coverageApp', () => ({
                // State
                currentView: 'summary',
                searchQuery: '',
                filterType: 'all',
                filterStatus: 'all',
                filterThreshold: 0,
                selectedScope: null,
                expandedScopes: {},
                
                // Data (loaded from JSON)
                data: {},
                
                // Chart instances
                charts: {},
                
                // Initialize
                init() {
                    this.loadData();
                    this.expandAllScopes();
                    
                    // Wait for D3 to load then render charts
                    this.$nextTick(() => {
                        setTimeout(() => this.renderCharts(), 500);
                    });
                },
                
                // Load coverage data from embedded JSON
                loadData() {
                    const dataElement = document.getElementById('coverage-data');
                    const isCompressed = dataElement.getAttribute('data-compressed') === 'true';
                    
                    if (isCompressed) {
                        // TODO: Decompress with pako.js
                        console.warn('Compressed data not yet supported');
                        this.data = { summary: {}, scopes: [] };
                    } else {
                        this.data = JSON.parse(dataElement.textContent);
                    }
                    
                    console.log('Coverage data loaded:', this.data);
                },
                
                // View switching
                switchView(view) {
                    this.currentView = view;
                    if (view === 'visualizations') {
                        this.$nextTick(() => this.renderCharts());
                    }
                },
                
                // Chart rendering
                renderCharts() {
                    if (typeof d3 === 'undefined') {
                        console.warn('D3.js not loaded yet');
                        return;
                    }
                    
                    this.renderPieChart();
                    this.renderBarChart();
                    this.renderTreemap();
                },
                
                renderPieChart() {
                    const container = document.getElementById('pie-chart');
                    if (!container || !this.data.summary?.coverage_by_type) return;
                    
                    // Clear existing
                    container.innerHTML = '';
                    
                    const data = Object.entries(this.data.summary.coverage_by_type).map(([key, value]) => ({
                        type: key,
                        coverage: value
                    }));
                    
                    const width = 400;
                    const height = 300;
                    const radius = Math.min(width, height) / 2 - 40;
                    
                    const svg = d3.select(container)
                        .append('svg')
                        .attr('width', width)
                        .attr('height', height)
                        .append('g')
                        .attr('transform', `translate(${width/2},${height/2})`);
                    
                    const color = d3.scaleOrdinal()
                        .domain(data.map(d => d.type))
                        .range(['#667eea', '#764ba2', '#f39c12', '#27ae60', '#e74c3c', '#3498db']);
                    
                    const pie = d3.pie()
                        .value(d => d.coverage);
                    
                    const arc = d3.arc()
                        .innerRadius(0)
                        .outerRadius(radius);
                    
                    const arcs = svg.selectAll('arc')
                        .data(pie(data))
                        .enter()
                        .append('g');
                    
                    arcs.append('path')
                        .attr('d', arc)
                        .attr('fill', d => color(d.data.type))
                        .attr('stroke', 'white')
                        .attr('stroke-width', 2)
                        .on('mouseover', function(event, d) {
                            d3.select(this).style('opacity', 0.8);
                            showTooltip(event, `${d.data.type}: ${d.data.coverage.toFixed(1)}%`);
                        })
                        .on('mouseout', function() {
                            d3.select(this).style('opacity', 1);
                            hideTooltip();
                        });
                    
                    // Labels
                    arcs.append('text')
                        .attr('transform', d => `translate(${arc.centroid(d)})`)
                        .attr('text-anchor', 'middle')
                        .attr('fill', 'white')
                        .attr('font-weight', 'bold')
                        .attr('font-size', '12px')
                        .text(d => d.data.coverage > 5 ? d.data.type : '');
                },
                
                renderBarChart() {
                    const container = document.getElementById('bar-chart');
                    if (!container || !this.data.scopes) return;
                    
                    // Clear existing
                    container.innerHTML = '';
                    
                    // Get top 10 lowest coverage scopes
                    const allScopes = this.flattenScopes(this.data.scopes);
                    const sortedScopes = allScopes
                        .sort((a, b) => a.coverage - b.coverage)
                        .slice(0, 10);
                    
                    if (sortedScopes.length === 0) return;
                    
                    const margin = {top: 20, right: 20, bottom: 60, left: 150};
                    const width = 600 - margin.left - margin.right;
                    const height = 300 - margin.top - margin.bottom;
                    
                    const svg = d3.select(container)
                        .append('svg')
                        .attr('width', width + margin.left + margin.right)
                        .attr('height', height + margin.top + margin.bottom)
                        .append('g')
                        .attr('transform', `translate(${margin.left},${margin.top})`);
                    
                    const x = d3.scaleLinear()
                        .domain([0, 100])
                        .range([0, width]);
                    
                    const y = d3.scaleBand()
                        .domain(sortedScopes.map(d => d.name))
                        .range([0, height])
                        .padding(0.2);
                    
                    // Bars
                    svg.selectAll('rect')
                        .data(sortedScopes)
                        .enter()
                        .append('rect')
                        .attr('x', 0)
                        .attr('y', d => y(d.name))
                        .attr('width', d => x(d.coverage))
                        .attr('height', y.bandwidth())
                        .attr('fill', d => d.coverage >= 80 ? '#27ae60' : d.coverage >= 50 ? '#f39c12' : '#e74c3c')
                        .on('mouseover', function(event, d) {
                            d3.select(this).style('opacity', 0.8);
                            showTooltip(event, `${d.name}: ${d.coverage.toFixed(1)}%`);
                        })
                        .on('mouseout', function() {
                            d3.select(this).style('opacity', 1);
                            hideTooltip();
                        });
                    
                    // Axes
                    svg.append('g')
                        .attr('class', 'axis')
                        .attr('transform', `translate(0,${height})`)
                        .call(d3.axisBottom(x).ticks(5));
                    
                    svg.append('g')
                        .attr('class', 'axis')
                        .call(d3.axisLeft(y));
                    
                    // Labels
                    svg.selectAll('.bar-label')
                        .data(sortedScopes)
                        .enter()
                        .append('text')
                        .attr('class', 'bar-label')
                        .attr('x', d => x(d.coverage) + 5)
                        .attr('y', d => y(d.name) + y.bandwidth() / 2)
                        .attr('dy', '0.35em')
                        .text(d => d.coverage.toFixed(1) + '%');
                },
                
                renderTreemap() {
                    const container = document.getElementById('treemap-chart');
                    if (!container || !this.data.scopes) return;
                    
                    // Clear existing
                    container.innerHTML = '';
                    
                    const width = 800;
                    const height = 400;
                    
                    // Build hierarchy - give each scope a size value
                    const hierarchyData = {
                        name: 'root',
                        children: this.data.scopes
                    };
                    
                    const root = d3.hierarchy(hierarchyData)
                        .sum(d => {
                            // Give each scope a size based on its weight or default to 1
                            // Only count if it doesn't have children (leaf nodes)
                            if (!d.children || d.children.length === 0) {
                                return d.weight || 1;
                            }
                            return 0;
                        })
                        .sort((a, b) => b.value - a.value);
                    
                    // Check if we have any data
                    if (root.value === 0) {
                        container.innerHTML = '<div style="padding: 2rem; text-align: center; color: #999;">No data available for treemap visualization</div>';
                        return;
                    }
                    
                    const treemap = d3.treemap()
                        .size([width, height])
                        .padding(2)
                        .round(true);
                    
                    treemap(root);
                    
                    const svg = d3.select(container)
                        .append('svg')
                        .attr('width', width)
                        .attr('height', height);
                    
                    const color = d3.scaleLinear()
                        .domain([0, 50, 100])
                        .range(['#e74c3c', '#f39c12', '#27ae60']);
                    
                    const leaves = root.leaves();
                    
                    const cell = svg.selectAll('g')
                        .data(leaves)
                        .enter()
                        .append('g')
                        .attr('transform', d => `translate(${d.x0},${d.y0})`);
                    
                    cell.append('rect')
                        .attr('class', 'treemap-cell')
                        .attr('width', d => d.x1 - d.x0)
                        .attr('height', d => d.y1 - d.y0)
                        .attr('fill', d => color(d.data.coverage || 0))
                        .attr('stroke', '#fff')
                        .attr('stroke-width', 2)
                        .on('mouseover', function(event, d) {
                            d3.select(this).attr('stroke', '#333').attr('stroke-width', 3);
                            showTooltip(event, `${d.data.name}: ${(d.data.coverage || 0).toFixed(1)}%`);
                        })
                        .on('mouseout', function() {
                            d3.select(this).attr('stroke', '#fff').attr('stroke-width', 2);
                            hideTooltip();
                        });
                    
                    cell.append('text')
                        .attr('class', 'treemap-label')
                        .attr('x', 4)
                        .attr('y', 16)
                        .attr('font-size', '11px')
                        .attr('fill', '#fff')
                        .attr('font-weight', 'bold')
                        .text(d => {
                            const cellWidth = d.x1 - d.x0;
                            const cellHeight = d.y1 - d.y0;
                            // Only show label if cell is big enough
                            if (cellWidth > 60 && cellHeight > 20) {
                                return d.data.name;
                            }
                            return '';
                        })
                        .each(function(d) {
                            // Truncate text if too long for cell
                            const cellWidth = d.x1 - d.x0;
                            const text = d3.select(this);
                            const textLength = text.node().getComputedTextLength();
                            if (textLength > cellWidth - 8) {
                                let label = d.data.name;
                                while (text.node().getComputedTextLength() > cellWidth - 8 && label.length > 0) {
                                    label = label.slice(0, -1);
                                    text.text(label + '...');
                                }
                            }
                        });
                    
                    // Add coverage percentage on second line if cell is tall enough
                    cell.append('text')
                        .attr('class', 'treemap-label')
                        .attr('x', 4)
                        .attr('y', 30)
                        .attr('font-size', '10px')
                        .attr('fill', '#fff')
                        .text(d => {
                            const cellWidth = d.x1 - d.x0;
                            const cellHeight = d.y1 - d.y0;
                            if (cellWidth > 60 && cellHeight > 35) {
                                return (d.data.coverage || 0).toFixed(1) + '%';
                            }
                            return '';
                        });
                },
                
                flattenScopes(scopes) {
                    let result = [];
                    scopes.forEach(scope => {
                        result.push(scope);
                        if (scope.children && scope.children.length > 0) {
                            result = result.concat(this.flattenScopes(scope.children));
                        }
                    });
                    return result;
                },
                
                // Tree navigation
                toggleScope(scopeId) {
                    this.expandedScopes[scopeId] = !this.expandedScopes[scopeId];
                },
                
                isScopeExpanded(scopeId) {
                    return this.expandedScopes[scopeId] === true;
                },
                
                selectScope(scope) {
                    this.selectedScope = scope;
                },
                
                expandAllScopes() {
                    if (!this.data.scopes) return;
                    
                    const expandAll = (scopes) => {
                        scopes.forEach(scope => {
                            this.expandedScopes[scope.id] = true;
                            if (scope.children && scope.children.length > 0) {
                                expandAll(scope.children);
                            }
                        });
                    };
                    
                    expandAll(this.data.scopes);
                },
                
                collapseAllScopes() {
                    this.expandedScopes = {};
                },
                
                // Filtering
                get filteredScopes() {
                    if (!this.data.scopes) return [];
                    
                    return this.filterScopesRecursive(this.data.scopes);
                },
                
                filterScopesRecursive(scopes) {
                    return scopes.filter(scope => {
                        // Filter by coverage threshold
                        if (scope.coverage < this.filterThreshold) {
                            return false;
                        }
                        
                        // Filter by search query
                        if (this.searchQuery && !scope.name.toLowerCase().includes(this.searchQuery.toLowerCase())) {
                            return false;
                        }
                        
                        // Filter by status
                        if (this.filterStatus !== 'all') {
                            if (this.filterStatus === 'covered' && scope.coverage < 100) {
                                return false;
                            }
                            if (this.filterStatus === 'uncovered' && scope.coverage > 0) {
                                return false;
                            }
                            if (this.filterStatus === 'partial' && (scope.coverage === 0 || scope.coverage === 100)) {
                                return false;
                            }
                        }
                        
                        return true;
                    }).map(scope => {
                        // Recursively filter children
                        if (scope.children && scope.children.length > 0) {
                            return {
                                ...scope,
                                children: this.filterScopesRecursive(scope.children)
                            };
                        }
                        return scope;
                    });
                },
                
                resetFilters() {
                    this.searchQuery = '';
                    this.filterType = 'all';
                    this.filterStatus = 'all';
                    this.filterThreshold = 0;
                },
                
                // Coverage helpers
                getCoverageClass(coverage) {
                    if (coverage >= 80) return 'coverage-high';
                    if (coverage >= 50) return 'coverage-medium';
                    return 'coverage-low';
                },
                
                formatCoverage(coverage) {
                    return coverage.toFixed(1) + '%';
                },
                
                // Bin helpers
                getBinRowClass(bin) {
                    if (bin.type === 'illegal_bin' && bin.hits > 0) {
                        return 'bin-illegal';
                    }
                    if (bin.status === 'covered') {
                        return 'bin-covered';
                    }
                    return '';
                },
                
                // Tree rendering helpers
                getScopeIcon(scopeType) {
                    const icons = {
                        'COVERGROUP': '📋',
                        'COVERPOINT': '🎯',
                        'DU_MODULE': '📦',
                        'MODULE': '📦',
                        'INSTANCE': '🔧',
                        'PACKAGE': '📚',
                        'CLASS': '🏛️',
                    };
                    return icons[scopeType] || '📄';
                },
                
                getScopeIndent(depth) {
                    return (depth * 1.5) + 'rem';
                },
                
                // Summary stats
                get totalCoverage() {
                    return this.data.summary?.total_coverage || 0;
                },
                
                get totalItems() {
                    return this.data.summary?.total_items || 0;
                },
                
                get coveredItems() {
                    return this.data.summary?.covered_items || 0;
                },
                
                get uncoveredItems() {
                    return this.data.summary?.uncovered_items || 0;
                },
                
                get coverageByType() {
                    return this.data.summary?.coverage_by_type || {};
                }
            }));
        });
        
        // Tooltip helpers
        let tooltip = null;
        
        function showTooltip(event, text) {
            if (!tooltip) {
                tooltip = d3.select('body')
                    .append('div')
                    .attr('class', 'tooltip')
                    .style('opacity', 0);
            }
            
            tooltip.transition()
                .duration(200)
                .style('opacity', 1);
            
            tooltip.html(text)
                .style('left', (event.pageX + 10) + 'px')
                .style('top', (event.pageY - 28) + 'px');
        }
        
        function hideTooltip() {
            if (tooltip) {
                tooltip.transition()
                    .duration(200)
                    .style('opacity', 0);
            }
        }
        
        // Load libraries from CDN
        (function() {
            // Alpine.js
            const alpineScript = document.createElement('script');
            alpineScript.src = 'https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js';
            alpineScript.defer = true;
            document.head.appendChild(alpineScript);
            
            // D3.js
            const d3Script = document.createElement('script');
            d3Script.src = 'https://cdn.jsdelivr.net/npm/d3@7';
            d3Script.onload = () => console.log('D3.js loaded');
            document.head.appendChild(d3Script);
        })();
        """
