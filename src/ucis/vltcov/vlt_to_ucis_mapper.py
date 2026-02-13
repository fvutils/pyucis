"""Map Verilator coverage items to UCIS database structure."""

from typing import List, Dict, Optional
from collections import defaultdict
from ucis import (
    UCIS, 
    ucis_CreateScope,
    ucis_CreateFileHandle,
    UCIS_VLOG,
    UCIS_OTHER,
    UCIS_INSTANCE,
    UCIS_DU_MODULE,
    UCIS_BLOCK,
    UCIS_BRANCH,
    UCIS_TOGGLE,
    UCIS_COVERGROUP,
    UCIS_COVERPOINT,
    UCIS_CVGBIN,
    UCIS_STMTBIN,
    UCIS_BRANCHBIN,
    UCIS_TOGGLEBIN,
    UCIS_ENABLED_STMT,
    UCIS_ENABLED_BRANCH,
    UCIS_ENABLED_TOGGLE,
    UCIS_INST_ONCE,
    UCIS_SCOPE_UNDER_DU,
)
from ucis.source_info import SourceInfo
from ucis.cover_data import CoverData
from ucis.scope import Scope

from .vlt_coverage_item import VltCoverageItem


class VltToUcisMapper:
    """Maps Verilator coverage items to UCIS database structure."""
    
    def __init__(self, db: UCIS):
        """Initialize mapper with target UCIS database.
        
        Args:
            db: Target UCIS database
        """
        self.db = db
        self.scope_cache: Dict[str, Scope] = {}
        self.file_cache: Dict[str, int] = {}
        self.du_scope: Optional[Scope] = None
        
    def map_items(self, items: List[VltCoverageItem]):
        """Map all coverage items to UCIS.
        
        Args:
            items: List of parsed Verilator coverage items
        """
        # Group items for efficient processing
        groups = self._group_items(items)
        
        # Create design unit scope if needed
        if items:
            self._create_design_unit()
        
        # Process each group
        for key, group_items in groups.items():
            coverage_type, hierarchy = key
            
            if coverage_type == 'funccov':
                self._map_functional_coverage(group_items)
            elif coverage_type == 'line':
                self._map_line_coverage(group_items)
            elif coverage_type == 'branch':
                self._map_branch_coverage(group_items)
            elif coverage_type == 'toggle':
                self._map_toggle_coverage(group_items)
    
    def _group_items(self, items: List[VltCoverageItem]) -> Dict[tuple, List[VltCoverageItem]]:
        """Group items by coverage type and hierarchy.
        
        Args:
            items: List of coverage items
            
        Returns:
            Dictionary mapping (coverage_type, hierarchy) to list of items
        """
        groups = defaultdict(list)
        
        for item in items:
            if item.is_functional_coverage:
                key = ('funccov', item.hierarchy)
            elif item.is_line_coverage:
                key = ('line', item.hierarchy)
            elif item.is_branch_coverage:
                key = ('branch', item.hierarchy)
            elif item.is_toggle_coverage:
                key = ('toggle', item.hierarchy)
            else:
                key = ('other', item.hierarchy)
            
            groups[key].append(item)
        
        return groups
    
    def _create_design_unit(self):
        """Create top-level design unit scope."""
        if self.du_scope is not None:
            return self.du_scope
        
        srcinfo = SourceInfo(None, 0, 0)  # Use None for no file
        self.du_scope = ucis_CreateScope(
            self.db,
            None,  # DUs never have a parent
            "verilator_design",
            srcinfo,
            1,  # weight
            UCIS_VLOG,
            UCIS_DU_MODULE,
            UCIS_ENABLED_STMT | UCIS_ENABLED_BRANCH | UCIS_ENABLED_TOGGLE |
            UCIS_INST_ONCE | UCIS_SCOPE_UNDER_DU
        )
        
        return self.du_scope
    
    def _get_or_create_instance_scope(self, hierarchy: str) -> Scope:
        """Get or create instance scope for hierarchy path.
        
        Args:
            hierarchy: Module hierarchy path (e.g., "top.mod1.mod2")
            
        Returns:
            Instance scope
        """
        if hierarchy in self.scope_cache:
            return self.scope_cache[hierarchy]
        
        # Split hierarchy and create nested scopes
        parts = hierarchy.split('.') if hierarchy else ['top']
        parent = self.du_scope
        path = ""
        
        for i, part in enumerate(parts):
            path = '.'.join(parts[:i+1]) if i > 0 else part
            
            if path not in self.scope_cache:
                srcinfo = SourceInfo(None, 0, 0)  # Use None for instance scopes
                # Use createInstance for instance scopes
                scope = self.db.createInstance(
                    part,
                    srcinfo,
                    1,  # weight
                    UCIS_OTHER,  # source language
                    UCIS_INSTANCE,  # scope type
                    parent,  # type scope (parent)
                    UCIS_INST_ONCE  # flags
                )
                self.scope_cache[path] = scope
            
            parent = self.scope_cache[path]
        
        return parent
    
    def _get_file_handle(self, filename: str):
        """Get or create file handle for filename.
        
        Args:
            filename: Source file path
            
        Returns:
            File handle object
        """
        if filename in self.file_cache:
            return self.file_cache[filename]
        
        # Extract directory and filename
        import os
        dirname = os.path.dirname(filename) if os.path.dirname(filename) else "."
        file_handle = self.db.createFileHandle(filename, dirname)
        self.file_cache[filename] = file_handle
        
        return file_handle
    
    def _map_line_coverage(self, items: List[VltCoverageItem]):
        """Map line coverage items to UCIS.
        
        NOTE: Code coverage scopes (BLOCK, BRANCH, TOGGLE) are currently not
        fully supported in the MemUCIS implementation. This is a PyUCIS limitation,
        not a Verilator import issue. For now, code coverage items are skipped.
        
        Args:
            items: Line coverage items
        """
        if not items:
            return
        
        # TODO: Implement code coverage mapping when PyUCIS adds support
        # Code coverage needs to be under instances, but MemInstance doesn't
        # support BLOCK/BRANCH/TOGGLE scope types yet.
        pass
    
    def _map_branch_coverage(self, items: List[VltCoverageItem]):
        """Map branch coverage items to UCIS.
        
        NOTE: Code coverage scopes are currently not fully supported in MemUCIS.
        Skipping branch coverage for now.
        
        Args:
            items: Branch coverage items
        """
        # TODO: Implement when PyUCIS adds code coverage scope support
        pass
    
    def _map_toggle_coverage(self, items: List[VltCoverageItem]):
        """Map toggle coverage items to UCIS.
        
        NOTE: Code coverage scopes are currently not fully supported in MemUCIS.
        Skipping toggle coverage for now.
        
        Args:
            items: Toggle coverage items
        """
        # TODO: Implement when PyUCIS adds code coverage scope support
        pass
    
    def _map_functional_coverage(self, items: List[VltCoverageItem]):
        """Map functional coverage items to UCIS.
        
        Args:
            items: Functional coverage items
        """
        if not items:
            return
        
        # Group by covergroup
        by_covergroup = defaultdict(list)
        for item in items:
            cg_name = item.covergroup_name
            if cg_name:
                by_covergroup[cg_name].append(item)
        
        for cg_name, cg_items in by_covergroup.items():
            # Get instance scope (use first item's hierarchy)
            hier = cg_items[0].hierarchy.split('.')[0] if '.' in cg_items[0].hierarchy else "top"
            inst_scope = self._get_or_create_instance_scope(hier)
            
            # Get file handle
            file_handle = self._get_file_handle(cg_items[0].filename) if cg_items[0].filename else None
            
            # Create covergroup scope
            cg_scope = ucis_CreateScope(
                self.db,
                inst_scope,
                cg_name,
                SourceInfo(file_handle, cg_items[0].lineno, 0),
                1,
                UCIS_VLOG,
                UCIS_COVERGROUP,
                0
            )
            
            # Group bins by coverpoint (extracted from hierarchy)
            by_coverpoint = defaultdict(list)
            for item in cg_items:
                # Try to extract coverpoint from hierarchy (e.g., "cg1.cp_data3.__auto[0]")
                parts = item.hierarchy.split('.')
                if len(parts) >= 2:
                    cp_name = parts[1]  # Use second part as coverpoint name
                else:
                    cp_name = "default_cp"
                by_coverpoint[cp_name].append(item)
            
            # Create coverpoints and bins
            for cp_name, cp_items in by_coverpoint.items():
                # Get file handle for coverpoint
                cp_file_handle = self._get_file_handle(cp_items[0].filename) if cp_items[0].filename else None
                
                cp_scope = ucis_CreateScope(
                    self.db,
                    cg_scope,
                    cp_name,
                    SourceInfo(cp_file_handle, cp_items[0].lineno, 0),
                    1,
                    UCIS_VLOG,
                    UCIS_COVERPOINT,
                    0
                )
                
                # Add bins
                for item in cp_items:
                    item_file_handle = self._get_file_handle(item.filename) if item.filename else None
                    srcinfo = SourceInfo(item_file_handle, item.lineno, item.colno)
                    cover_data = CoverData(UCIS_CVGBIN, 0)
                    cover_data.data = item.hit_count
                    cp_scope.createNextCover(
                        item.bin_name if item.bin_name else f"bin_{item.lineno}",
                        cover_data,
                        srcinfo
                    )
