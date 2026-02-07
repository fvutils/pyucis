"""
MCP tools implementation for PyUCIS.

Each tool corresponds to an MCP tool that agents can invoke.
"""
from typing import Any, Dict, Optional
import json


class ToolImplementations:
    """Implementation of all MCP tools."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    async def open_database(self, path: str, format_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Open a UCIS database.
        
        Args:
            path: Path to database file
            format_type: Database format (xml, yaml, ucis). Auto-detect if None.
        
        Returns:
            Database handle information
        """
        try:
            handle = self.db_manager.open_database(path, format_type)
            return {
                "success": True,
                "database": handle.to_dict()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def close_database(self, db_id: str) -> Dict[str, Any]:
        """
        Close a UCIS database.
        
        Args:
            db_id: Database ID to close
        
        Returns:
            Success status
        """
        success = self.db_manager.close_database(db_id)
        return {
            "success": success,
            "message": "Database closed" if success else "Database not found"
        }
    
    async def list_databases(self) -> Dict[str, Any]:
        """
        List all open databases.
        
        Returns:
            List of open databases
        """
        databases = self.db_manager.list_databases()
        return {
            "success": True,
            "databases": databases,
            "count": len(databases)
        }
    
    async def get_database_info(self, db_id: str) -> Dict[str, Any]:
        """
        Get detailed database information.
        
        Args:
            db_id: Database ID
        
        Returns:
            Database metadata and statistics
        """
        handle = self.db_manager.get_database(db_id)
        if not handle:
            return {
                "success": False,
                "error": f"Database not found: {db_id}"
            }
        
        return {
            "success": True,
            "database": handle.to_dict()
        }
    
    async def get_coverage_summary(self, db_id: str) -> Dict[str, Any]:
        """
        Get overall coverage summary.
        
        Args:
            db_id: Database ID
        
        Returns:
            Coverage summary with percentages by type
        """
        handle = self.db_manager.get_database(db_id)
        if not handle:
            return {
                "success": False,
                "error": f"Database not found: {db_id}"
            }
        
        try:
            from ucis.cmd.show.show_summary import ShowSummary
            
            show_cmd = ShowSummary(handle.db_obj)
            data = show_cmd.get_data()
            
            return {
                "success": True,
                "summary": data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_coverage_gaps(self, db_id: str, threshold: Optional[float] = None) -> Dict[str, Any]:
        """
        Get coverage gaps (uncovered or low-coverage items).
        
        Args:
            db_id: Database ID
            threshold: Coverage threshold (0-100). Items below this are included.
        
        Returns:
            List of coverage gaps
        """
        handle = self.db_manager.get_database(db_id)
        if not handle:
            return {
                "success": False,
                "error": f"Database not found: {db_id}"
            }
        
        try:
            from ucis.cmd.show.show_gaps import ShowGaps
            
            show_cmd = ShowGaps(handle.db_obj, threshold=threshold)
            data = show_cmd.get_data()
            
            return {
                "success": True,
                "gaps": data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_covergroups(self, db_id: str, include_bins: bool = False) -> Dict[str, Any]:
        """
        Get covergroup information.
        
        Args:
            db_id: Database ID
            include_bins: Include detailed bin information
        
        Returns:
            List of covergroups with details
        """
        handle = self.db_manager.get_database(db_id)
        if not handle:
            return {
                "success": False,
                "error": f"Database not found: {db_id}"
            }
        
        try:
            from ucis.cmd.show.show_covergroups import ShowCovergroups
            
            show_cmd = ShowCovergroups(handle.db_obj, include_bins=include_bins)
            data = show_cmd.get_data()
            
            return {
                "success": True,
                "covergroups": data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_tests(self, db_id: str) -> Dict[str, Any]:
        """
        Get test execution information.
        
        Args:
            db_id: Database ID
        
        Returns:
            List of tests with execution details
        """
        handle = self.db_manager.get_database(db_id)
        if not handle:
            return {
                "success": False,
                "error": f"Database not found: {db_id}"
            }
        
        try:
            from ucis.cmd.show.show_tests import ShowTests
            
            show_cmd = ShowTests(handle.db_obj)
            data = show_cmd.get_data()
            
            return {
                "success": True,
                "tests": data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_hierarchy(self, db_id: str, max_depth: Optional[int] = None) -> Dict[str, Any]:
        """
        Get design hierarchy.
        
        Args:
            db_id: Database ID
            max_depth: Maximum depth to traverse
        
        Returns:
            Hierarchical structure of design
        """
        handle = self.db_manager.get_database(db_id)
        if not handle:
            return {
                "success": False,
                "error": f"Database not found: {db_id}"
            }
        
        try:
            from ucis.cmd.show.show_hierarchy import ShowHierarchy
            
            show_cmd = ShowHierarchy(handle.db_obj, max_depth=max_depth)
            data = show_cmd.get_data()
            
            return {
                "success": True,
                "hierarchy": data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_metrics(self, db_id: str) -> Dict[str, Any]:
        """
        Get coverage metrics and statistics.
        
        Args:
            db_id: Database ID
        
        Returns:
            Coverage metrics with analysis
        """
        handle = self.db_manager.get_database(db_id)
        if not handle:
            return {
                "success": False,
                "error": f"Database not found: {db_id}"
            }
        
        try:
            from ucis.cmd.show.show_metrics import ShowMetrics
            
            show_cmd = ShowMetrics(handle.db_obj)
            data = show_cmd.get_data()
            
            return {
                "success": True,
                "metrics": data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_bins(self, db_id: str, covergroup: Optional[str] = None, 
                      coverpoint: Optional[str] = None, min_hits: Optional[int] = None,
                      max_hits: Optional[int] = None, sort_by: Optional[str] = None) -> Dict[str, Any]:
        """
        Get bin-level coverage details.
        
        Args:
            db_id: Database ID
            covergroup: Filter by covergroup name
            coverpoint: Filter by coverpoint name
            min_hits: Minimum hit count
            max_hits: Maximum hit count
            sort_by: Sort by 'count' or 'name'
        
        Returns:
            Bin details
        """
        handle = self.db_manager.get_database(db_id)
        if not handle:
            return {
                "success": False,
                "error": f"Database not found: {db_id}"
            }
        
        try:
            from ucis.cmd.show.show_bins import ShowBins
            
            show_cmd = ShowBins(handle.db_obj, covergroup=covergroup, coverpoint=coverpoint,
                              min_hits=min_hits, max_hits=max_hits, sort_by=sort_by)
            data = show_cmd.get_data()
            
            return {
                "success": True,
                "bins": data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def compare_databases(self, db_id: str, compare_db_id: str) -> Dict[str, Any]:
        """
        Compare two databases.
        
        Args:
            db_id: Baseline database ID
            compare_db_id: Comparison database ID
        
        Returns:
            Comparison results
        """
        handle1 = self.db_manager.get_database(db_id)
        handle2 = self.db_manager.get_database(compare_db_id)
        
        if not handle1:
            return {
                "success": False,
                "error": f"Baseline database not found: {db_id}"
            }
        if not handle2:
            return {
                "success": False,
                "error": f"Comparison database not found: {compare_db_id}"
            }
        
        try:
            from ucis.cmd.show.show_compare import ShowCompare
            
            show_cmd = ShowCompare(handle1.db_obj, handle2.db_obj)
            data = show_cmd.get_data()
            
            return {
                "success": True,
                "comparison": data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_hotspots(self, db_id: str, threshold: float = 80.0, limit: int = 10) -> Dict[str, Any]:
        """
        Identify coverage hotspots and high-value targets.
        
        Args:
            db_id: Database ID
            threshold: Coverage threshold (default: 80)
            limit: Max items per category (default: 10)
        
        Returns:
            Coverage hotspots
        """
        handle = self.db_manager.get_database(db_id)
        if not handle:
            return {
                "success": False,
                "error": f"Database not found: {db_id}"
            }
        
        try:
            from ucis.cmd.show.show_hotspots import ShowHotspots
            
            show_cmd = ShowHotspots(handle.db_obj, threshold=threshold, limit=limit)
            data = show_cmd.get_data()
            
            return {
                "success": True,
                "hotspots": data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_code_coverage(self, db_id: str, output_format: str = "json") -> Dict[str, Any]:
        """
        Get code coverage with support for multiple export formats.
        
        Args:
            db_id: Database ID
            output_format: Format (json, lcov, cobertura, jacoco, clover)
        
        Returns:
            Code coverage data
        """
        handle = self.db_manager.get_database(db_id)
        if not handle:
            return {
                "success": False,
                "error": f"Database not found: {db_id}"
            }
        
        try:
            from ucis.cmd.show.show_code_coverage import ShowCodeCoverage
            
            show_cmd = ShowCodeCoverage(handle.db_obj, output_format=output_format)
            data = show_cmd.get_data()
            
            return {
                "success": True,
                "code_coverage": data,
                "format": output_format
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_assertions(self, db_id: str) -> Dict[str, Any]:
        """
        Get assertion coverage information.
        
        Args:
            db_id: Database ID
        
        Returns:
            Assertion coverage details
        """
        handle = self.db_manager.get_database(db_id)
        if not handle:
            return {
                "success": False,
                "error": f"Database not found: {db_id}"
            }
        
        try:
            from ucis.cmd.show.show_assertions import ShowAssertions
            
            show_cmd = ShowAssertions(handle.db_obj)
            data = show_cmd.get_data()
            
            return {
                "success": True,
                "assertions": data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_toggle_coverage(self, db_id: str) -> Dict[str, Any]:
        """
        Get toggle coverage information.
        
        Args:
            db_id: Database ID
        
        Returns:
            Toggle coverage details
        """
        handle = self.db_manager.get_database(db_id)
        if not handle:
            return {
                "success": False,
                "error": f"Database not found: {db_id}"
            }
        
        try:
            from ucis.cmd.show.show_toggle import ShowToggle
            
            show_cmd = ShowToggle(handle.db_obj)
            data = show_cmd.get_data()
            
            return {
                "success": True,
                "toggle": data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
