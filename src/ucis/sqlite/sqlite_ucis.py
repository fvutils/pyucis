# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
SQLite-backed UCIS database implementation
"""

import sqlite3
import os
from typing import Iterator, Dict
from datetime import datetime
import getpass

from ucis.ucis import UCIS
from ucis.scope import Scope
from ucis.history_node import HistoryNode
from ucis.history_node_kind import HistoryNodeKind
from ucis.file_handle import FileHandle
from ucis.scope_type_t import ScopeTypeT
from ucis.source_t import SourceT
from ucis.int_property import IntProperty

from ucis.sqlite.sqlite_scope import SqliteScope
from ucis.sqlite.sqlite_obj import SqliteObj
from ucis.sqlite.sqlite_history_node import SqliteHistoryNode
from ucis.sqlite.sqlite_file_handle import SqliteFileHandle
from ucis.sqlite import schema_manager


def _convert_to_sqlite(source_ucis: UCIS) -> 'SqliteUCIS':
    """
    Convert a non-SQLite UCIS database to SqliteUCIS.
    
    This creates a temporary in-memory SQLite database and copies all
    scopes, coverage items, and history nodes from the source.
    
    Args:
        source_ucis: The source UCIS database to convert
        
    Returns:
        A SqliteUCIS instance with the copied data
    """
    # Create in-memory SQLite database
    sqlite_db = SqliteUCIS()
    
    # Copy metadata
    sqlite_db.setWrittenBy(source_ucis.getWrittenBy())
    sqlite_db.setWrittenTime(source_ucis.getWrittenTime())
    
    # Copy file handles
    file_handle_map = {}
    if hasattr(source_ucis, 'file_handle_m'):
        for filename, src_fh in source_ucis.file_handle_m.items():
            file_handle_map[filename] = sqlite_db.createFileHandle(filename, None)
    
    # Copy history nodes
    for src_hist in source_ucis.historyNodes(-1):
        _copy_history_node(src_hist, sqlite_db, None)
    
    # Copy scopes recursively from root
    _copy_scope_recursive(source_ucis, sqlite_db, file_handle_map)
    
    return sqlite_db


def _copy_history_node(src_node, dst_db: 'SqliteUCIS', parent):
    """Copy a history node from source to destination database"""
    dst_node = dst_db.createHistoryNode(
        parent,
        src_node.getLogicalName(),
        src_node.getPhysicalName(),
        src_node.getKind()
    )
    
    # Copy metadata
    if hasattr(src_node, 'getTestStatus'):
        dst_node.setTestStatus(src_node.getTestStatus())
    if hasattr(src_node, 'getSeed'):
        dst_node.setSeed(src_node.getSeed())
    if hasattr(src_node, 'getCmd'):
        dst_node.setCmd(src_node.getCmd())
    if hasattr(src_node, 'getCpuTime'):
        dst_node.setCpuTime(src_node.getCpuTime())
    if hasattr(src_node, 'getDate'):
        dst_node.setDate(src_node.getDate())
    if hasattr(src_node, 'getUserName'):
        dst_node.setUserName(src_node.getUserName())
    
    return dst_node


def _copy_scope_recursive(src_scope, dst_scope, file_handle_map):
    """Recursively copy scopes and coverage items from source to destination"""
    
    # Copy coverage items for this scope
    for src_cover in src_scope.coverItems(-1):
        # Map source file handle to destination file handle
        src_info = src_cover.getSourceInfo()
        dst_info = src_info
        if src_info and src_info.file and hasattr(src_info.file, 'filename'):
            filename = src_info.file.filename
            if filename in file_handle_map:
                from ucis.source_info import SourceInfo
                dst_info = SourceInfo(
                    file_handle_map[filename],
                    src_info.line,
                    src_info.token
                )
        
        dst_scope.createNextCover(
            src_cover.getName(),
            src_cover.getCoverData(),
            dst_info
        )
    
    # Recursively copy child scopes
    for src_child in src_scope.scopes(-1):
        # Map source file handle to destination file handle
        src_info = src_child.getSourceInfo()
        dst_info = src_info
        if src_info and src_info.file and hasattr(src_info.file, 'filename'):
            filename = src_info.file.filename
            if filename in file_handle_map:
                from ucis.source_info import SourceInfo
                dst_info = SourceInfo(
                    file_handle_map[filename],
                    src_info.line,
                    src_info.token
                )
        
        # Get flags - MemScope stores it in m_flags but doesn't implement getFlags()
        try:
            flags = src_child.getFlags()
        except (NotImplementedError, AttributeError):
            flags = getattr(src_child, 'm_flags', 0)
        
        dst_child = dst_scope.createScope(
            src_child.getScopeName(),
            dst_info,
            src_child.getWeight(),
            0,  # source
            src_child.getScopeType(),
            flags
        )
        
        # Recursively copy children
        _copy_scope_recursive(src_child, dst_child, file_handle_map)


class SqliteUCIS(SqliteScope, UCIS):
    """SQLite-backed UCIS database"""
    
    def __init__(self, db_path: str = None):
        """
        Create or open a SQLite UCIS database
        
        Args:
            db_path: Path to database file. If None, creates in-memory database.
        """
        # Open or create database
        self.db_path = db_path if db_path else ":memory:"
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Check if schema exists
        is_new_db = not schema_manager.check_schema_exists(self.conn)
        
        if is_new_db:
            # Create schema
            schema_manager.create_schema(self.conn)
            schema_manager.initialize_metadata(self.conn)
            
            # Create root scope (use 0 as a special marker for root)
            cursor = self.conn.execute(
                """INSERT INTO scopes (parent_id, scope_type, scope_name, scope_flags, weight, goal)
                   VALUES (NULL, 0, '', 0, 1, 100)"""
            )
            root_scope_id = cursor.lastrowid
        else:
            # Existing database - run migrations if needed
            schema_manager.ensure_schema_current(self.conn)
            
            # Find root scope
            cursor = self.conn.execute(
                "SELECT scope_id FROM scopes WHERE parent_id IS NULL LIMIT 1"
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError("Database has no root scope")
            root_scope_id = row[0]
        
        # Initialize SqliteObj first to set up ucis_db reference
        SqliteObj.__init__(self, self)
        
        # Set scope attributes before calling Scope.__init__
        self.scope_id = root_scope_id
        self._loaded = False
        self._scope_name = None
        self._scope_type = None
        self._scope_flags = None
        self._weight = None
        self._goal = None
        self._parent_id = None
        self._source_info = None
        
        # Now call Scope.__init__ which calls setGoal
        Scope.__init__(self)
        
        # Call UCIS.__init__
        UCIS.__init__(self)
        
        # File handle cache
        self._file_handle_cache: Dict[str, SqliteFileHandle] = {}
        
        self._modified = False
    
    def getAPIVersion(self) -> str:
        """Get API version"""
        cursor = self.conn.execute(
            "SELECT value FROM db_metadata WHERE key = 'API_VERSION'"
        )
        row = cursor.fetchone()
        return row[0] if row else "1.0"
    
    def getWrittenBy(self) -> str:
        """Get written by user"""
        cursor = self.conn.execute(
            "SELECT value FROM db_metadata WHERE key = 'WRITTEN_BY'"
        )
        row = cursor.fetchone()
        return row[0] if row else getpass.getuser()
    
    def setWrittenBy(self, by: str):
        """Set written by user"""
        self.conn.execute(
            "INSERT OR REPLACE INTO db_metadata (key, value) VALUES ('WRITTEN_BY', ?)",
            (by,)
        )
        self._modified = True
    
    def getWrittenTime(self) -> int:
        """Get written time"""
        cursor = self.conn.execute(
            "SELECT value FROM db_metadata WHERE key = 'WRITTEN_TIME'"
        )
        row = cursor.fetchone()
        if row:
            return int(row[0])
        return int(datetime.now().timestamp())
    
    def setWrittenTime(self, time: int):
        """Set written time"""
        self.conn.execute(
            "INSERT OR REPLACE INTO db_metadata (key, value) VALUES ('WRITTEN_TIME', ?)",
            (str(time),)
        )
        self._modified = True
    
    def getDBVersion(self):
        """Get database version"""
        cursor = self.conn.execute(
            "SELECT value FROM db_metadata WHERE key = 'UCIS_VERSION'"
        )
        row = cursor.fetchone()
        return row[0] if row else "1.0"
    
    def getPathSeparator(self):
        """Get path separator"""
        cursor = self.conn.execute(
            "SELECT value FROM db_metadata WHERE key = 'PATH_SEPARATOR'"
        )
        row = cursor.fetchone()
        return row[0] if row else "/"
    
    def setPathSeparator(self, sep: str):
        """Set path separator"""
        self.conn.execute(
            "INSERT OR REPLACE INTO db_metadata (key, value) VALUES ('PATH_SEPARATOR', ?)",
            (sep,)
        )
        self._modified = True
    
    def isModified(self) -> bool:
        """Check if database has been modified"""
        return self._modified
    
    def modifiedSinceSim(self) -> bool:
        """Check if modified since simulation"""
        return self._modified
    
    def getNumTests(self) -> int:
        """Get number of test history nodes"""
        cursor = self.conn.execute(
            "SELECT COUNT(*) FROM history_nodes WHERE history_kind = ?",
            (HistoryNodeKind.TEST,)
        )
        row = cursor.fetchone()
        return row[0] if row else 0
    
    def createFileHandle(self, filename: str, workdir: str = None) -> FileHandle:
        """Create or get file handle"""
        if filename in self._file_handle_cache:
            return self._file_handle_cache[filename]
        
        # Check if file exists in database
        cursor = self.conn.execute(
            "SELECT file_id FROM files WHERE file_path = ?",
            (filename,)
        )
        row = cursor.fetchone()
        
        if row:
            file_id = row[0]
        else:
            # Create new file
            cursor = self.conn.execute(
                "INSERT INTO files (file_path) VALUES (?)",
                (filename,)
            )
            file_id = cursor.lastrowid
        
        file_handle = SqliteFileHandle(self, file_id, filename)
        self._file_handle_cache[filename] = file_handle
        return file_handle
    
    def createHistoryNode(self, parent, logicalname: str, 
                         physicalname: str = None, 
                         kind: HistoryNodeKind = None) -> HistoryNode:
        """Create a history node (test record)"""
        if kind is None:
            kind = HistoryNodeKind.TEST
        
        parent_id = None
        if parent is not None:
            if isinstance(parent, SqliteHistoryNode):
                parent_id = parent.history_id
            elif hasattr(parent, 'history_id'):
                parent_id = parent.history_id
        
        cursor = self.conn.execute(
            """INSERT INTO history_nodes (parent_id, history_kind, logical_name, physical_name, date, user_name)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (parent_id, kind, logicalname, physicalname, 
             datetime.now().isoformat(), getpass.getuser())
        )
        
        history_id = cursor.lastrowid
        self._modified = True
        
        return SqliteHistoryNode(self, history_id)
    
    def historyNodes(self, kind: HistoryNodeKind = None) -> Iterator[HistoryNode]:
        """Iterate history nodes"""
        if kind is None or kind == -1:
            cursor = self.conn.execute("SELECT history_id FROM history_nodes")
        else:
            cursor = self.conn.execute(
                "SELECT history_id FROM history_nodes WHERE history_kind = ?",
                (kind,)
            )
        
        for row in cursor:
            yield SqliteHistoryNode(self, row[0])
    
    def getSourceFiles(self):
        """Get list of source files"""
        # Not fully implemented yet
        return []
    
    def getCoverInstances(self):
        """Get list of coverage instances"""
        # Not fully implemented yet
        return []
    
    def write(self, file, scope=None, recurse=True, covertype=-1):
        """Write database (no-op for SQLite, already persistent)"""
        # SQLite writes are automatic, but we could trigger a checkpoint
        self.conn.commit()
    
    def close(self):
        """Close the database"""
        self.conn.commit()
        self.conn.close()
    
    def begin_transaction(self):
        """Begin a transaction"""
        if self.conn.in_transaction:
            return  # Already in transaction
        self.conn.execute("BEGIN")
    
    def commit(self):
        """Commit current transaction"""
        self.conn.execute("COMMIT")
        self._modified = True
    
    def rollback(self):
        """Rollback current transaction"""
        self.conn.execute("ROLLBACK")
    
    def getIntProperty(self, coverindex: int, property: IntProperty) -> int:
        """Get integer property with UCIS-specific handling"""
        if property == IntProperty.IS_MODIFIED:
            return 1 if self.isModified() else 0
        elif property == IntProperty.MODIFIED_SINCE_SIM:
            return 1 if self.modifiedSinceSim() else 0
        elif property == IntProperty.NUM_TESTS:
            return self.getNumTests()
        else:
            return super().getIntProperty(coverindex, property)
    
    def merge(self, source_ucis, create_history: bool = True):
        """
        Merge coverage from another UCIS database
        
        Args:
            source_ucis: Source UCIS database to merge from (can be any UCIS type)
            create_history: Whether to create merge history node
            
        Returns:
            MergeStats object with statistics
        """
        from ucis.sqlite.sqlite_merge import SqliteMerger
        
        # If source is not a SqliteUCIS, convert it first
        if not isinstance(source_ucis, SqliteUCIS):
            source_ucis = _convert_to_sqlite(source_ucis)
            temp_source = source_ucis  # Keep reference to close later
        else:
            temp_source = None
        
        try:
            merger = SqliteMerger(self)
            result = merger.merge(source_ucis, create_history)
            return result
        finally:
            # Clean up temporary SQLite database if we created one
            if temp_source is not None:
                temp_source.close()
