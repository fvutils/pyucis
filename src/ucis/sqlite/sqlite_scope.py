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
SQLite-backed Scope implementation
"""

from typing import Iterator
from ucis.scope import Scope
from ucis.source_info import SourceInfo
from ucis.source_t import SourceT
from ucis.scope_type_t import ScopeTypeT
from ucis.flags_t import FlagsT
from ucis.cover_data import CoverData
from ucis.cover_index import CoverIndex
from ucis.cover_type_t import CoverTypeT
from ucis.sqlite.sqlite_obj import SqliteObj
from ucis.sqlite.sqlite_attributes import AttributeTagMixin, ObjectKind
from ucis.int_property import IntProperty


class SqliteScope(AttributeTagMixin, SqliteObj, Scope):
    """SQLite-backed scope implementation"""
    
    def __init__(self, ucis_db, scope_id: int):
        # Set ucis_db FIRST (required by SqliteObj)
        self.ucis_db = ucis_db
        self._property_cache = {}
        
        # Initialize scope attributes BEFORE calling parent __init__
        self.scope_id = scope_id
        self._loaded = False
        self._scope_name = None
        self._scope_type = None
        self._scope_flags = None
        self._weight = None
        self._goal = None
        self._parent_id = None
        self._source_info = None
        
        # Now call Scope.__init__ which might call setGoal
        Scope.__init__(self)
        
    def _ensure_loaded(self):
        """Lazy load scope data from database"""
        if self._loaded:
            return
            
        cursor = self.ucis_db.conn.execute(
            """SELECT scope_name, scope_type, scope_flags, weight, goal, parent_id,
                      source_file_id, source_line, source_token
               FROM scopes WHERE scope_id = ?""",
            (self.scope_id,)
        )
        
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Scope {self.scope_id} not found in database")
        
        self._scope_name = row[0]
        self._scope_type = row[1]
        self._scope_flags = row[2]
        self._weight = row[3]
        self._goal = row[4] if row[4] is not None else 100
        self._parent_id = row[5]
        
        # Load source info
        if row[6] is not None:
            # Get file path
            file_cursor = self.ucis_db.conn.execute(
                "SELECT file_path FROM files WHERE file_id = ?",
                (row[6],)
            )
            file_row = file_cursor.fetchone()
            file_path = file_row[0] if file_row else None
            
            file_handle = self.ucis_db.createFileHandle(file_path, None) if file_path else None
            self._source_info = SourceInfo(file_handle, row[7], row[8])
        else:
            self._source_info = SourceInfo(None, -1, -1)
        
        self._loaded = True
    
    def _get_property_table(self):
        return 'scope_properties'
    
    def _get_obj_id(self):
        return self.scope_id
    
    def createScope(self, name: str, srcinfo: SourceInfo, weight: int,
                   source: SourceT, type: ScopeTypeT, flags: FlagsT) -> 'Scope':
        """Create a child scope"""
        # Handle source file
        source_file_id = None
        source_line = -1
        source_token = -1
        
        if srcinfo and srcinfo.file:
            file_path = srcinfo.file.getFilename()
            # Get or create file
            cursor = self.ucis_db.conn.execute(
                "SELECT file_id FROM files WHERE file_path = ?",
                (file_path,)
            )
            row = cursor.fetchone()
            if row:
                source_file_id = row[0]
            else:
                cursor = self.ucis_db.conn.execute(
                    "INSERT INTO files (file_path) VALUES (?)",
                    (file_path,)
                )
                source_file_id = cursor.lastrowid
            
            source_line = srcinfo.line
            source_token = srcinfo.token
        
        # Insert scope
        cursor = self.ucis_db.conn.execute(
            """INSERT INTO scopes (parent_id, scope_type, scope_name, scope_flags, weight, goal,
                                   source_file_id, source_line, source_token)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (self.scope_id, type, name, flags, weight, 100, 
             source_file_id, source_line, source_token)
        )
        
        new_scope_id = cursor.lastrowid
        return SqliteScope(self.ucis_db, new_scope_id)
    
    def createInstance(self, name: str, fileinfo: SourceInfo, weight: int,
                      source: SourceT, type: ScopeTypeT, du_scope: 'Scope',
                      flags: FlagsT) -> 'Scope':
        """Create an instance scope"""
        return self.createScope(name, fileinfo, weight, source, type, flags)
    
    def createToggle(self, name: str, canonical_name: str, flags: FlagsT,
                    toggle_metric, toggle_type, toggle_dir) -> 'Scope':
        """Create a toggle scope"""
        return self.createScope(name, None, 1, SourceT.NONE, ScopeTypeT.TOGGLE, flags)
    
    def createCovergroup(self, name: str, srcinfo: SourceInfo, weight: int,
                        source: SourceT) -> 'Scope':
        """Create a covergroup scope"""
        return self.createScope(name, srcinfo, weight, source, ScopeTypeT.COVERGROUP, 0)
    
    def createNextCover(self, name: str, data: CoverData, 
                       sourceinfo: SourceInfo) -> CoverIndex:
        """Create a coverage item"""
        # Find next available index
        cursor = self.ucis_db.conn.execute(
            "SELECT MAX(cover_index) FROM coveritems WHERE scope_id = ?",
            (self.scope_id,)
        )
        row = cursor.fetchone()
        next_index = (row[0] + 1) if (row[0] is not None) else 0
        
        # Handle source file
        source_file_id = None
        source_line = -1
        source_token = -1
        
        if sourceinfo and sourceinfo.file:
            file_path = sourceinfo.file.getFilename()
            cursor = self.ucis_db.conn.execute(
                "SELECT file_id FROM files WHERE file_path = ?",
                (file_path,)
            )
            row = cursor.fetchone()
            if row:
                source_file_id = row[0]
            else:
                cursor = self.ucis_db.conn.execute(
                    "INSERT INTO files (file_path) VALUES (?)",
                    (file_path,)
                )
                source_file_id = cursor.lastrowid
            
            source_line = sourceinfo.line
            source_token = sourceinfo.token
        
        # Insert coveritem
        cover_type = data.type if data else 0x01  # Default to CVGBIN
        cover_count = data.data if data else 0
        
        cursor = self.ucis_db.conn.execute(
            """INSERT INTO coveritems (scope_id, cover_index, cover_type, cover_name, 
                                       cover_data, source_file_id, source_line, source_token)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (self.scope_id, next_index, cover_type, name, cover_count,
             source_file_id, source_line, source_token)
        )
        
        cover_id = cursor.lastrowid
        
        from ucis.sqlite.sqlite_cover_index import SqliteCoverIndex
        return SqliteCoverIndex(self.ucis_db, cover_id)
    
    def getWeight(self) -> int:
        """Get scope weight"""
        self._ensure_loaded()
        return self._weight
    
    def setWeight(self, w: int):
        """Set scope weight"""
        self._ensure_loaded()
        self._weight = w
        self.ucis_db.conn.execute(
            "UPDATE scopes SET weight = ? WHERE scope_id = ?",
            (w, self.scope_id)
        )
    
    def getGoal(self) -> int:
        """Get coverage goal"""
        self._ensure_loaded()
        return self._goal
    
    def setGoal(self, goal: int):
        """Set coverage goal"""
        self._ensure_loaded()
        self._goal = goal
        self.ucis_db.conn.execute(
            "UPDATE scopes SET goal = ? WHERE scope_id = ?",
            (goal, self.scope_id)
        )
    
    def getFlags(self) -> FlagsT:
        """Get scope flags"""
        self._ensure_loaded()
        return self._scope_flags
    
    def getScopeType(self) -> ScopeTypeT:
        """Get scope type"""
        self._ensure_loaded()
        return self._scope_type
    
    def getScopeName(self) -> str:
        """Get scope name"""
        self._ensure_loaded()
        return self._scope_name
    
    def getSourceInfo(self) -> SourceInfo:
        """Get source information"""
        self._ensure_loaded()
        return self._source_info
    
    def scopes(self, mask: ScopeTypeT) -> Iterator['Scope']:
        """Iterate child scopes matching type mask"""
        if mask == -1:
            # All scopes
            cursor = self.ucis_db.conn.execute(
                "SELECT scope_id FROM scopes WHERE parent_id = ?",
                (self.scope_id,)
            )
        else:
            # Filter by type mask
            cursor = self.ucis_db.conn.execute(
                "SELECT scope_id FROM scopes WHERE parent_id = ? AND (scope_type & ?) != 0",
                (self.scope_id, mask)
            )
        
        for row in cursor:
            yield SqliteScope(self.ucis_db, row[0])
    
    def coverItems(self, mask: CoverTypeT) -> Iterator['CoverIndex']:
        """Iterate coverage items matching type mask"""
        from ucis.sqlite.sqlite_cover_index import SqliteCoverIndex
        
        if mask == -1:
            # All coverage items
            cursor = self.ucis_db.conn.execute(
                "SELECT cover_id FROM coveritems WHERE scope_id = ? ORDER BY cover_index",
                (self.scope_id,)
            )
        else:
            # Filter by type mask
            cursor = self.ucis_db.conn.execute(
                "SELECT cover_id FROM coveritems WHERE scope_id = ? AND (cover_type & ?) != 0 ORDER BY cover_index",
                (self.scope_id, mask)
            )
        
        for row in cursor:
            yield SqliteCoverIndex(self.ucis_db, row[0])
    
    def getIntProperty(self, coverindex: int, property: IntProperty) -> int:
        """Get integer property with scope-specific handling"""
        if property == IntProperty.SCOPE_WEIGHT:
            return self.getWeight()
        elif property == IntProperty.SCOPE_GOAL:
            return self.getGoal()
        else:
            return super().getIntProperty(coverindex, property)
    
    def setIntProperty(self, coverindex: int, property: IntProperty, value: int):
        """Set integer property with scope-specific handling"""
        if property == IntProperty.SCOPE_WEIGHT:
            self.setWeight(value)
        elif property == IntProperty.SCOPE_GOAL:
            self.setGoal(value)
        else:
            super().setIntProperty(coverindex, property, value)
    
    def _get_obj_kind(self):
        """Get object kind for attributes/tags"""
        from ucis.sqlite.sqlite_attributes import ObjectKind
        return ObjectKind.SCOPE
