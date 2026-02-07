"""
Show Hierarchy Command

Displays the hierarchical structure of the UCIS database.
"""
from typing import Any, Dict, List
from ucis.cmd.show_base import ShowBase


class ShowHierarchy(ShowBase):
    """
    Display scope hierarchy.
    
    Shows:
    - Design unit hierarchy
    - Instance hierarchy
    - Scope structure with types
    """
    
    def get_data(self) -> Dict[str, Any]:
        """
        Extract hierarchy information from the database.
        
        Returns:
            Dictionary containing hierarchy structure
        """
        from ucis.scope_type_t import ScopeTypeT
        
        # Get root scopes
        hierarchy = []
        
        # Traverse top-level scopes
        for scope in self.db.scopes(ScopeTypeT.INSTANCE):
            scope_data = self._traverse_scope(scope, depth=0)
            if scope_data:
                hierarchy.append(scope_data)
        
        result = {
            "database": self.args.db,
            "hierarchy": hierarchy,
            "summary": {
                "total_scopes": self._count_scopes(hierarchy),
            }
        }
        
        return result
    
    def _traverse_scope(self, scope, depth: int) -> Dict[str, Any]:
        """Recursively traverse scope hierarchy."""
        max_depth = getattr(self.args, 'max_depth', None)
        
        # Check depth limit
        if max_depth is not None and depth >= max_depth:
            return None
        
        scope_data = {
            "name": scope.getScopeName(),
            "type": self._get_scope_type_name(scope.m_type),
            "depth": depth,
        }
        
        # Add coverage if available
        try:
            from ucis.cover_type_t import CoverTypeT
            cover_data = scope.getCoverData(0, CoverTypeT.CVGFLAG)
            if cover_data:
                scope_data["coverage"] = cover_data.getPercentage() if hasattr(cover_data, 'getPercentage') else None
        except:
            pass
        
        # Get children
        children = []
        try:
            from ucis.scope_type_t import ScopeTypeT
            for child in scope.scopes(ScopeTypeT.ALL):
                child_data = self._traverse_scope(child, depth + 1)
                if child_data:
                    children.append(child_data)
        except:
            pass
        
        if children:
            scope_data["children"] = children
            scope_data["child_count"] = len(children)
        
        return scope_data
    
    def _get_scope_type_name(self, scope_type) -> str:
        """Convert scope type to human-readable name."""
        from ucis.scope_type_t import ScopeTypeT
        
        type_names = {
            ScopeTypeT.INSTANCE: "instance",
            ScopeTypeT.DU_MODULE: "module",
            ScopeTypeT.DU_PACKAGE: "package",
            ScopeTypeT.DU_PROGRAM: "program",
            ScopeTypeT.DU_INTERFACE: "interface",
            ScopeTypeT.COVERGROUP: "covergroup",
            ScopeTypeT.COVERPOINT: "coverpoint",
            ScopeTypeT.CROSS: "cross",
        }
        
        return type_names.get(scope_type, f"unknown_{scope_type}")
    
    def _count_scopes(self, hierarchy: List[Dict[str, Any]]) -> int:
        """Recursively count all scopes."""
        count = len(hierarchy)
        for item in hierarchy:
            if "children" in item:
                count += self._count_scopes(item["children"])
        return count
