"""
Test database manager functionality.
"""
import pytest
import tempfile
import os
from pathlib import Path

from ucis.mcp.db_manager import DatabaseManager, DatabaseHandle


class TestDatabaseManager:
    """Test DatabaseManager class."""
    
    def setup_method(self):
        """Setup for each test."""
        self.db_manager = DatabaseManager()
    
    def test_generate_id(self):
        """Test ID generation."""
        id1 = self.db_manager._generate_id()
        id2 = self.db_manager._generate_id()
        
        assert id1 == "db_1"
        assert id2 == "db_2"
        assert id1 != id2
    
    def test_detect_format_xml(self):
        """Test XML format detection."""
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as f:
            f.write(b'<?xml version="1.0"?><root></root>')
            temp_path = f.name
        
        try:
            format_type = self.db_manager._detect_format(temp_path)
            assert format_type == 'xml'
        finally:
            os.unlink(temp_path)
    
    def test_detect_format_yaml(self):
        """Test YAML format detection."""
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            f.write(b'---\nucis: test\n')
            temp_path = f.name
        
        try:
            format_type = self.db_manager._detect_format(temp_path)
            assert format_type == 'yaml'
        finally:
            os.unlink(temp_path)
    
    def test_detect_format_from_extension(self):
        """Test format detection from file extension."""
        # Just check extension-based detection without file content
        assert self.db_manager._detect_format("test.xml") == "xml"
        assert self.db_manager._detect_format("test.yaml") == "yaml"
        assert self.db_manager._detect_format("test.yml") == "yaml"
        assert self.db_manager._detect_format("test.ucis") == "ucis"
    
    def test_list_databases_empty(self):
        """Test listing databases when none are open."""
        databases = self.db_manager.list_databases()
        assert databases == []
    
    def test_get_database_not_found(self):
        """Test getting non-existent database."""
        db = self.db_manager.get_database("nonexistent")
        assert db is None
    
    def test_close_database_not_found(self):
        """Test closing non-existent database."""
        result = self.db_manager.close_database("nonexistent")
        assert result is False
    
    def test_close_all(self):
        """Test closing all databases."""
        # Manually add some fake handles
        self.db_manager._databases["db_1"] = DatabaseHandle(
            "db_1", None, "/fake/path1.xml", "xml"
        )
        self.db_manager._databases["db_2"] = DatabaseHandle(
            "db_2", None, "/fake/path2.xml", "xml"
        )
        
        assert len(self.db_manager._databases) == 2
        
        self.db_manager.close_all()
        assert len(self.db_manager._databases) == 0


class TestDatabaseHandle:
    """Test DatabaseHandle class."""
    
    def test_database_handle_creation(self):
        """Test creating a database handle."""
        handle = DatabaseHandle("db_1", None, "/path/to/db.xml", "xml", "r")
        
        assert handle.db_id == "db_1"
        assert handle.path == "/path/to/db.xml"
        assert handle.format_type == "xml"
        assert handle.mode == "r"
        assert handle.metadata == {}
    
    def test_database_handle_to_dict(self):
        """Test converting handle to dictionary."""
        handle = DatabaseHandle("db_1", None, "/path/to/db.xml", "xml", "r")
        handle.metadata = {"size": 1024}
        
        result = handle.to_dict()
        
        assert result["id"] == "db_1"
        assert result["path"] == "/path/to/db.xml"
        assert result["format"] == "xml"
        assert result["mode"] == "r"
        assert result["metadata"]["size"] == 1024
