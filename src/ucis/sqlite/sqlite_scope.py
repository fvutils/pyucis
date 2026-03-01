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
        
        # Flag to prevent database updates during initialization
        self._initializing = True
        
        # Now call Scope.__init__ which calls setGoal(100)
        # This will set _goal in memory but won't update database
        Scope.__init__(self)
        
        # Clear initialization flag
        self._initializing = False
        
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
            file_path = srcinfo.file.getFileName()
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
        return SqliteScope.create_specialized_scope(self.ucis_db, new_scope_id)
    
    def createInstance(self, name: str, fileinfo: SourceInfo, weight: int,
                      source: SourceT, type: ScopeTypeT, du_scope: 'Scope',
                      flags: FlagsT) -> 'Scope':
        """Create an instance scope with design-unit linkage.

        Persists the instance-to-DU association in the design_units table
        so that getInstanceDu() can retrieve it later.
        """
        scope = self.createScope(name, fileinfo, weight, source, type, flags)
        if du_scope is not None:
            du_id = getattr(du_scope, 'scope_id', None)
            if du_id is not None:
                du_name = du_scope.getScopeName()
                du_type = (du_scope._scope_type
                           if getattr(du_scope, '_scope_type', None) is not None
                           else 0)
                self.ucis_db.conn.execute(
                    "INSERT OR REPLACE INTO design_units "
                    "(du_scope_id, du_name, du_type) VALUES (?, ?, ?)",
                    (scope.scope_id, du_name, du_type))
        return scope
    
    def createToggle(self, name: str, canonical_name: str, flags: FlagsT,
                    toggle_metric, toggle_type, toggle_dir) -> 'Scope':
        """Create a toggle scope"""
        scope = self.createScope(name, None, 1, SourceT.NONE, ScopeTypeT.TOGGLE, flags)
        # Store toggle metadata if specialized scope was returned
        from ucis.sqlite.sqlite_toggle_scope import SqliteToggleScope
        if isinstance(scope, SqliteToggleScope):
            scope.setCanonicalName(canonical_name if canonical_name else name)
            if toggle_metric is not None:
                scope.setToggleMetric(toggle_metric)
            if toggle_type is not None:
                scope.setToggleType(toggle_type)
            if toggle_dir is not None:
                scope.setToggleDir(toggle_dir)
        return scope
    
    def createCovergroup(self, name: str, srcinfo: SourceInfo, weight: int,
                        source: SourceT) -> 'Scope':
        """Create a covergroup scope"""
        scope = self.createScope(name, srcinfo, weight, source, ScopeTypeT.COVERGROUP, 0)
        # Return as specialized SqliteCovergroup
        from ucis.sqlite.sqlite_covergroup import SqliteCovergroup
        return SqliteCovergroup(self.ucis_db, scope.scope_id)
    
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
            file_path = sourceinfo.file.getFileName()
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
        at_least = data.goal if data else 1
        
        cursor = self.ucis_db.conn.execute(
            """INSERT INTO coveritems (scope_id, cover_index, cover_type, cover_name, 
                                       cover_data, at_least, source_file_id, source_line, source_token)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (self.scope_id, next_index, cover_type, name, cover_count, at_least,
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
        # Skip during initialization to preserve database value
        if getattr(self, '_initializing', False):
            return
            
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
        # During initialization, Scope.__init__() calls setGoal(100)
        # We want to skip this so the database value is preserved
        if getattr(self, '_initializing', False):
            return
        
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
    
    def getInstanceDu(self) -> 'SqliteScope':
        """Get the design-unit scope associated with this instance.

        First checks the design_units table for an explicit link recorded by
        createInstance().  Falls back to a sibling-scope heuristic for
        databases created before the fix.
        """
        # Explicit lookup via design_units table
        row = self.ucis_db.conn.execute(
            "SELECT du_name FROM design_units WHERE du_scope_id = ?",
            (self.scope_id,)).fetchone()
        if row is not None:
            du_name = row[0]
            du_row = self.ucis_db.conn.execute(
                "SELECT scope_id FROM scopes WHERE scope_name = ? AND scope_type = ?",
                (du_name, ScopeTypeT.DU_MODULE)).fetchone()
            if du_row is not None:
                return SqliteScope(self.ucis_db, du_row[0])

        # Fallback: search sibling scopes for a DU scope
        self._ensure_loaded()
        du_mask = (ScopeTypeT.DU_MODULE | ScopeTypeT.DU_ARCH |
                   ScopeTypeT.DU_PACKAGE | ScopeTypeT.DU_PROGRAM |
                   ScopeTypeT.DU_INTERFACE)
        parent_id = self._parent_id
        if parent_id is None:
            cursor = self.ucis_db.conn.execute(
                "SELECT scope_id FROM scopes WHERE parent_id IS NULL AND (scope_type & ?) != 0",
                (int(du_mask),))
        else:
            cursor = self.ucis_db.conn.execute(
                "SELECT scope_id FROM scopes WHERE parent_id = ? AND (scope_type & ?) != 0",
                (parent_id, int(du_mask)))
        row = cursor.fetchone()
        if row:
            return SqliteScope(self.ucis_db, row[0])
        return None

    def getScopeName(self) -> str:
        """Get scope name"""
        self._ensure_loaded()
        return self._scope_name

    def getStringProperty(self, coverindex: int, property) -> str:
        """Get string property, handling SCOPE_NAME specially."""
        from ucis.str_property import StrProperty
        if property == StrProperty.SCOPE_NAME:
            self._ensure_loaded()
            return self._scope_name
        return super().getStringProperty(coverindex, property)
    
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
            yield SqliteScope.create_specialized_scope(self.ucis_db, row[0])
    
    def coverItems(self, mask: CoverTypeT) -> Iterator['CoverIndex']:
        """Iterate coverage items matching type mask"""
        from ucis.sqlite.sqlite_cover_index import SqliteCoverIndex
        from ucis.cover_type_t import CoverTypeT as CType

        # Handle "all" masks (-1 or very large ALL value)
        if mask == -1 or mask == CType.ALL:
            cursor = self.ucis_db.conn.execute(
                "SELECT cover_id FROM coveritems WHERE scope_id = ? ORDER BY cover_index",
                (self.scope_id,)
            )
        else:
            # Filter by type mask (SQLite INTEGER max is 2^63-1, signed)
            mask_int = int(mask) & 0x7FFFFFFFFFFFFFFF
            cursor = self.ucis_db.conn.execute(
                "SELECT cover_id FROM coveritems WHERE scope_id = ? AND (cover_type & ?) != 0 ORDER BY cover_index",
                (self.scope_id, mask_int)
            )
        
        for row in cursor:
            yield SqliteCoverIndex(self.ucis_db, row[0])
    
    def removeCover(self, coverindex: int) -> None:
        """Remove cover item at the given index from this scope."""
        cursor = self.ucis_db.conn.execute(
            "SELECT cover_id FROM coveritems WHERE scope_id = ? ORDER BY cover_index",
            (self.scope_id,)
        )
        rows = cursor.fetchall()
        if 0 <= coverindex < len(rows):
            cover_id = rows[coverindex][0]
            self.ucis_db.conn.execute(
                "DELETE FROM coveritems WHERE cover_id = ?", (cover_id,)
            )

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
    
    @staticmethod
    def create_specialized_scope(ucis_db, scope_id: int) -> 'SqliteScope':
        """Factory method to create appropriate scope subclass based on type"""
        # Query scope type
        cursor = ucis_db.conn.execute(
            "SELECT scope_type FROM scopes WHERE scope_id = ?",
            (scope_id,)
        )
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Scope {scope_id} not found")
        
        scope_type = row[0]
        
        # Return specialized subclass based on type
        if scope_type & ScopeTypeT.COVERGROUP:
            from ucis.sqlite.sqlite_covergroup import SqliteCovergroup
            return SqliteCovergroup(ucis_db, scope_id)
        elif scope_type & ScopeTypeT.CROSS:
            from ucis.sqlite.sqlite_cross import SqliteCross
            return SqliteCross(ucis_db, scope_id)
        elif scope_type & ScopeTypeT.COVERPOINT:
            from ucis.sqlite.sqlite_coverpoint import SqliteCoverpoint
            return SqliteCoverpoint(ucis_db, scope_id)
        elif scope_type & ScopeTypeT.TOGGLE:
            from ucis.sqlite.sqlite_toggle_scope import SqliteToggleScope
            return SqliteToggleScope(ucis_db, scope_id)
        elif scope_type & ScopeTypeT.FSM:
            from ucis.sqlite.sqlite_fsm_scope import SqliteFSMScope
            return SqliteFSMScope(ucis_db, scope_id)
        else:
            # Generic scope
            return SqliteScope(ucis_db, scope_id)
