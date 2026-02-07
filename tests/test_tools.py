"""
Test MCP tool implementations.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch

from ucis.mcp.tools import ToolImplementations
from ucis.mcp.db_manager import DatabaseManager, DatabaseHandle


@pytest.mark.asyncio
class TestToolImplementations:
    """Test tool implementations."""
    
    def setup_method(self):
        """Setup for each test."""
        self.db_manager = DatabaseManager()
        self.tools = ToolImplementations(self.db_manager)
    
    async def test_open_database_not_found(self):
        """Test opening non-existent database."""
        result = await self.tools.open_database("/nonexistent/path.xml")
        
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower()
    
    async def test_close_database_not_found(self):
        """Test closing non-existent database."""
        result = await self.tools.close_database("nonexistent")
        
        assert result["success"] is False
        assert "not found" in result["message"].lower()
    
    async def test_list_databases_empty(self):
        """Test listing databases when none are open."""
        result = await self.tools.list_databases()
        
        assert result["success"] is True
        assert result["count"] == 0
        assert result["databases"] == []
    
    async def test_list_databases_with_handles(self):
        """Test listing databases with open handles."""
        # Add fake handles
        handle1 = DatabaseHandle("db_1", None, "/path/to/db1.xml", "xml")
        handle2 = DatabaseHandle("db_2", None, "/path/to/db2.xml", "xml")
        
        self.db_manager._databases["db_1"] = handle1
        self.db_manager._databases["db_2"] = handle2
        
        result = await self.tools.list_databases()
        
        assert result["success"] is True
        assert result["count"] == 2
        assert len(result["databases"]) == 2
    
    async def test_get_database_info_not_found(self):
        """Test getting info for non-existent database."""
        result = await self.tools.get_database_info("nonexistent")
        
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower()
    
    async def test_get_database_info_success(self):
        """Test getting database info successfully."""
        # Add fake handle
        handle = DatabaseHandle("db_1", None, "/path/to/db.xml", "xml")
        handle.metadata = {"size": 1024}
        self.db_manager._databases["db_1"] = handle
        
        result = await self.tools.get_database_info("db_1")
        
        assert result["success"] is True
        assert "database" in result
        assert result["database"]["id"] == "db_1"
    
    async def test_get_coverage_summary_no_db(self):
        """Test getting coverage summary for non-existent database."""
        result = await self.tools.get_coverage_summary("nonexistent")
        
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower()
    
    async def test_get_coverage_gaps_no_db(self):
        """Test getting coverage gaps for non-existent database."""
        result = await self.tools.get_coverage_gaps("nonexistent")
        
        assert result["success"] is False
        assert "error" in result
    
    async def test_get_covergroups_no_db(self):
        """Test getting covergroups for non-existent database."""
        result = await self.tools.get_covergroups("nonexistent")
        
        assert result["success"] is False
        assert "error" in result
    
    async def test_get_tests_no_db(self):
        """Test getting tests for non-existent database."""
        result = await self.tools.get_tests("nonexistent")
        
        assert result["success"] is False
        assert "error" in result
    
    async def test_get_hierarchy_no_db(self):
        """Test getting hierarchy for non-existent database."""
        result = await self.tools.get_hierarchy("nonexistent")
        
        assert result["success"] is False
        assert "error" in result
    
    async def test_get_metrics_no_db(self):
        """Test getting metrics for non-existent database."""
        result = await self.tools.get_metrics("nonexistent")
        
        assert result["success"] is False
        assert "error" in result
