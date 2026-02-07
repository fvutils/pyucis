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
Base object class for SQLite UCIS implementation.
Provides property storage and management.
"""

from ucis.obj import Obj
from ucis.int_property import IntProperty
from ucis.real_property import RealProperty
from ucis.str_property import StrProperty
from ucis.handle_property import HandleProperty

# Property type enum
class PropertyType:
    INT = 1
    REAL = 2
    STRING = 3
    HANDLE = 4


class SqliteObj(Obj):
    """Base class for all SQLite-backed UCIS objects"""
    
    def __init__(self, ucis_db):
        super().__init__()
        self.ucis_db = ucis_db
        self._property_cache = {}
        
    def _get_property_table(self):
        """Get the name of the property table for this object type"""
        raise NotImplementedError("Subclasses must implement _get_property_table")
    
    def _get_obj_id(self):
        """Get the object ID for this object"""
        raise NotImplementedError("Subclasses must implement _get_obj_id")
    
    def getIntProperty(self, coverindex: int, property: IntProperty) -> int:
        """Get integer property value"""
        cache_key = (coverindex, property, PropertyType.INT)
        
        if cache_key in self._property_cache:
            return self._property_cache[cache_key]
        
        table = self._get_property_table()
        obj_id = self._get_obj_id()
        
        # Map coverindex to appropriate ID column
        if table == 'scope_properties':
            id_col = 'scope_id'
        elif table == 'coveritem_properties':
            id_col = 'cover_id'
        elif table == 'history_properties':
            id_col = 'history_id'
        else:
            raise ValueError(f"Unknown property table: {table}")
        
        cursor = self.ucis_db.conn.execute(
            f"SELECT int_value FROM {table} WHERE {id_col} = ? AND property_key = ? AND property_type = ?",
            (obj_id, property, PropertyType.INT)
        )
        
        row = cursor.fetchone()
        value = row[0] if row else None
        
        self._property_cache[cache_key] = value
        return value
    
    def setIntProperty(self, coverindex: int, property: IntProperty, value: int):
        """Set integer property value"""
        cache_key = (coverindex, property, PropertyType.INT)
        
        table = self._get_property_table()
        obj_id = self._get_obj_id()
        
        if table == 'scope_properties':
            id_col = 'scope_id'
        elif table == 'coveritem_properties':
            id_col = 'cover_id'
        elif table == 'history_properties':
            id_col = 'history_id'
        else:
            raise ValueError(f"Unknown property table: {table}")
        
        self.ucis_db.conn.execute(
            f"INSERT OR REPLACE INTO {table} ({id_col}, property_key, property_type, int_value) VALUES (?, ?, ?, ?)",
            (obj_id, property, PropertyType.INT, value)
        )
        
        self._property_cache[cache_key] = value
    
    def getRealProperty(self, coverindex: int, property: RealProperty) -> float:
        """Get real (float) property value"""
        cache_key = (coverindex, property, PropertyType.REAL)
        
        if cache_key in self._property_cache:
            return self._property_cache[cache_key]
        
        table = self._get_property_table()
        obj_id = self._get_obj_id()
        
        if table == 'scope_properties':
            id_col = 'scope_id'
        elif table == 'coveritem_properties':
            id_col = 'cover_id'
        elif table == 'history_properties':
            id_col = 'history_id'
        else:
            raise ValueError(f"Unknown property table: {table}")
        
        cursor = self.ucis_db.conn.execute(
            f"SELECT real_value FROM {table} WHERE {id_col} = ? AND property_key = ? AND property_type = ?",
            (obj_id, property, PropertyType.REAL)
        )
        
        row = cursor.fetchone()
        value = row[0] if row else None
        
        self._property_cache[cache_key] = value
        return value
    
    def setRealProperty(self, coverindex: int, property: RealProperty, value: float):
        """Set real (float) property value"""
        cache_key = (coverindex, property, PropertyType.REAL)
        
        table = self._get_property_table()
        obj_id = self._get_obj_id()
        
        if table == 'scope_properties':
            id_col = 'scope_id'
        elif table == 'coveritem_properties':
            id_col = 'cover_id'
        elif table == 'history_properties':
            id_col = 'history_id'
        else:
            raise ValueError(f"Unknown property table: {table}")
        
        self.ucis_db.conn.execute(
            f"INSERT OR REPLACE INTO {table} ({id_col}, property_key, property_type, real_value) VALUES (?, ?, ?, ?)",
            (obj_id, property, PropertyType.REAL, value)
        )
        
        self._property_cache[cache_key] = value
    
    def getStringProperty(self, coverindex: int, property: StrProperty) -> str:
        """Get string property value"""
        cache_key = (coverindex, property, PropertyType.STRING)
        
        if cache_key in self._property_cache:
            return self._property_cache[cache_key]
        
        table = self._get_property_table()
        obj_id = self._get_obj_id()
        
        if table == 'scope_properties':
            id_col = 'scope_id'
        elif table == 'coveritem_properties':
            id_col = 'cover_id'
        elif table == 'history_properties':
            id_col = 'history_id'
        else:
            raise ValueError(f"Unknown property table: {table}")
        
        cursor = self.ucis_db.conn.execute(
            f"SELECT string_value FROM {table} WHERE {id_col} = ? AND property_key = ? AND property_type = ?",
            (obj_id, property, PropertyType.STRING)
        )
        
        row = cursor.fetchone()
        value = row[0] if row else None
        
        self._property_cache[cache_key] = value
        return value
    
    def setStringProperty(self, coverindex: int, property: StrProperty, value: str):
        """Set string property value"""
        cache_key = (coverindex, property, PropertyType.STRING)
        
        table = self._get_property_table()
        obj_id = self._get_obj_id()
        
        if table == 'scope_properties':
            id_col = 'scope_id'
        elif table == 'coveritem_properties':
            id_col = 'cover_id'
        elif table == 'history_properties':
            id_col = 'history_id'
        else:
            raise ValueError(f"Unknown property table: {table}")
        
        self.ucis_db.conn.execute(
            f"INSERT OR REPLACE INTO {table} ({id_col}, property_key, property_type, string_value) VALUES (?, ?, ?, ?)",
            (obj_id, property, PropertyType.STRING, value)
        )
        
        self._property_cache[cache_key] = value
    
    def getHandleProperty(self, coverindex: int, property: HandleProperty):
        """Get handle property value"""
        cache_key = (coverindex, property, PropertyType.HANDLE)
        
        if cache_key in self._property_cache:
            return self._property_cache[cache_key]
        
        table = self._get_property_table()
        obj_id = self._get_obj_id()
        
        if table == 'scope_properties':
            id_col = 'scope_id'
        elif table == 'coveritem_properties':
            id_col = 'cover_id'
        elif table == 'history_properties':
            id_col = 'history_id'
        else:
            raise ValueError(f"Unknown property table: {table}")
        
        cursor = self.ucis_db.conn.execute(
            f"SELECT handle_value FROM {table} WHERE {id_col} = ? AND property_key = ? AND property_type = ?",
            (obj_id, property, PropertyType.HANDLE)
        )
        
        row = cursor.fetchone()
        
        if row and row[0] is not None:
            # Return the scope object referenced by the handle
            from ucis.sqlite.sqlite_scope import SqliteScope
            value = SqliteScope(self.ucis_db, row[0])
        else:
            value = None
        
        self._property_cache[cache_key] = value
        return value
    
    def setHandleProperty(self, coverindex: int, property: HandleProperty, value):
        """Set handle property value"""
        cache_key = (coverindex, property, PropertyType.HANDLE)
        
        table = self._get_property_table()
        obj_id = self._get_obj_id()
        
        if table == 'scope_properties':
            id_col = 'scope_id'
        elif table == 'coveritem_properties':
            id_col = 'cover_id'
        elif table == 'history_properties':
            id_col = 'history_id'
        else:
            raise ValueError(f"Unknown property table: {table}")
        
        # Extract scope_id from the handle value
        handle_id = value._get_obj_id() if value else None
        
        self.ucis_db.conn.execute(
            f"INSERT OR REPLACE INTO {table} ({id_col}, property_key, property_type, handle_value) VALUES (?, ?, ?, ?)",
            (obj_id, property, PropertyType.HANDLE, handle_id)
        )
        
        self._property_cache[cache_key] = value
