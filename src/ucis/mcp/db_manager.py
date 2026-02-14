"""
Database handle management for MCP server.

Manages open UCIS databases, format detection, and resource cleanup.
"""
from typing import Dict, Optional, Any
import os
from pathlib import Path


class DatabaseHandle:
    """Represents an open UCIS database."""
    
    def __init__(self, db_id: str, db_obj: Any, path: str, format_type: str, mode: str = "r"):
        self.db_id = db_id
        self.db_obj = db_obj
        self.path = path
        self.format_type = format_type
        self.mode = mode
        self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Return dictionary representation."""
        return {
            "id": self.db_id,
            "path": self.path,
            "format": self.format_type,
            "mode": self.mode,
            "metadata": self.metadata
        }


class DatabaseManager:
    """Manages open UCIS databases for the MCP server."""
    
    def __init__(self):
        self._databases: Dict[str, DatabaseHandle] = {}
        self._next_id = 1
    
    def _generate_id(self) -> str:
        """Generate unique database ID."""
        db_id = f"db_{self._next_id}"
        self._next_id += 1
        return db_id
    
    def _detect_format(self, path: str) -> str:
        """Detect database format from file."""
        from pathlib import Path
        
        # If file doesn't exist, try extension-only detection
        if not os.path.exists(path):
            ext = Path(path).suffix.lower()
            if ext == '.xml':
                return 'xml'
            elif ext in ['.yaml', '.yml']:
                return 'yaml'
            elif ext in ['.cdb', '.db', '.sqlite', '.sqlite3']:
                return 'sqlite'
            elif ext == '.dat':
                return 'vltcov'
            elif ext == '.ucis':
                return 'ucis'
            return 'xml'  # Default
        
        # File exists - use full detection with content checking
        from ucis.rgy.format_rgy import FormatRgy
        
        rgy = FormatRgy.inst()
        detected = rgy.detectDatabaseFormat(path)
        
        return detected if detected else 'xml'  # Default to xml if detection fails
    
    def open_database(self, path: str, format_type: Optional[str] = None, mode: str = "r") -> DatabaseHandle:
        """
        Open a UCIS database.
        
        Args:
            path: Path to database file
            format_type: Format (xml, yaml, ucis). Auto-detect if None.
            mode: Open mode ('r' for read-only, 'w' for write)
        
        Returns:
            DatabaseHandle object
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Database file not found: {path}")
        
        if format_type is None:
            format_type = self._detect_format(path)
        
        # Import format handler
        from ucis.db_format_rgy import DbFormatRgy
        
        format_rgy = DbFormatRgy()
        db_format = format_rgy.get_db_format(format_type)
        
        if db_format is None:
            raise ValueError(f"Unknown database format: {format_type}")
        
        # Open database
        db_obj = db_format.read(path)
        
        # Create handle
        db_id = self._generate_id()
        handle = DatabaseHandle(db_id, db_obj, path, format_type, mode)
        
        # Store metadata
        handle.metadata = {
            "file_size": os.path.getsize(path),
            "file_mtime": os.path.getmtime(path),
        }
        
        self._databases[db_id] = handle
        return handle
    
    def get_database(self, db_id: str) -> Optional[DatabaseHandle]:
        """Get database handle by ID."""
        return self._databases.get(db_id)
    
    def close_database(self, db_id: str) -> bool:
        """
        Close a database.
        
        Returns:
            True if closed, False if not found
        """
        if db_id in self._databases:
            del self._databases[db_id]
            return True
        return False
    
    def list_databases(self) -> list[Dict[str, Any]]:
        """List all open databases."""
        return [handle.to_dict() for handle in self._databases.values()]
    
    def close_all(self):
        """Close all databases."""
        self._databases.clear()
