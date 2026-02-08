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
SQLite-backed Toggle Coverage implementation with per-bit tracking
"""

from ucis.sqlite.sqlite_scope import SqliteScope
from ucis.scope_type_t import ScopeTypeT
from ucis.toggle_dir_t import ToggleDirT
from ucis.toggle_metric_t import ToggleMetricT
from ucis.toggle_type_t import ToggleTypeT


class ToggleBit:
    """Represents a single bit in toggle coverage"""
    
    def __init__(self, toggle_scope, bit_index: int, bit_type: int = 0):
        self.toggle_scope = toggle_scope
        self.bit_index = bit_index
        self.bit_type = bit_type
        self._toggle_01 = 0
        self._toggle_10 = 0
        self._loaded = False
        
    def _ensure_loaded(self):
        """Load toggle bit data from database"""
        if self._loaded:
            return
        
        cursor = self.toggle_scope.ucis_db.conn.execute(
            """SELECT toggle_01, toggle_10 
               FROM toggle_bits 
               WHERE cover_id = ? AND bit_index = ?""",
            (self.toggle_scope.toggle_cover_id, self.bit_index)
        )
        
        row = cursor.fetchone()
        if row:
            self._toggle_01 = row[0]
            self._toggle_10 = row[1]
        
        self._loaded = True
    
    def getToggle01(self) -> int:
        """Get 0->1 transition count"""
        self._ensure_loaded()
        return self._toggle_01
    
    def setToggle01(self, count: int):
        """Set 0->1 transition count"""
        self._ensure_loaded()
        self._toggle_01 = count
        
        # Update or insert
        self.toggle_scope.ucis_db.conn.execute(
            """INSERT OR REPLACE INTO toggle_bits 
               (cover_id, bit_index, bit_type, toggle_01, toggle_10)
               VALUES (?, ?, ?, ?, ?)""",
            (self.toggle_scope.toggle_cover_id, self.bit_index, 
             self.bit_type, self._toggle_01, self._toggle_10)
        )
    
    def getToggle10(self) -> int:
        """Get 1->0 transition count"""
        self._ensure_loaded()
        return self._toggle_10
    
    def setToggle10(self, count: int):
        """Set 1->0 transition count"""
        self._ensure_loaded()
        self._toggle_10 = count
        
        # Update or insert
        self.toggle_scope.ucis_db.conn.execute(
            """INSERT OR REPLACE INTO toggle_bits 
               (cover_id, bit_index, bit_type, toggle_01, toggle_10)
               VALUES (?, ?, ?, ?, ?)""",
            (self.toggle_scope.toggle_cover_id, self.bit_index, 
             self.bit_type, self._toggle_01, self._toggle_10)
        )
    
    def incrementToggle01(self, amt: int = 1):
        """Increment 0->1 transition count"""
        self._ensure_loaded()
        self.setToggle01(self._toggle_01 + amt)
    
    def incrementToggle10(self, amt: int = 1):
        """Increment 1->0 transition count"""
        self._ensure_loaded()
        self.setToggle10(self._toggle_10 + amt)


class SqliteToggleScope(SqliteScope):
    """Toggle coverage scope with per-bit tracking"""
    
    def __init__(self, ucis_db, scope_id: int):
        super().__init__(ucis_db, scope_id)
        self.toggle_cover_id = None
        self._canonical_name = None
        self._toggle_metric = None
        self._toggle_type = None
        self._toggle_dir = None
        self._num_bits = 0
        self._bits_cache = {}
    
    def _ensure_toggle_data(self):
        """Ensure toggle-specific data is loaded"""
        if self.toggle_cover_id is not None:
            return
        
        # Find the toggle coveritem for this scope
        cursor = self.ucis_db.conn.execute(
            """SELECT cover_id FROM coveritems 
               WHERE scope_id = ? AND cover_type & 0x200 != 0
               LIMIT 1""",
            (self.scope_id,)
        )
        
        row = cursor.fetchone()
        if row:
            self.toggle_cover_id = row[0]
        else:
            # Create a default toggle coveritem if it doesn't exist
            from ucis.cover_data import CoverData
            cover = self.createNextCover("toggle_data", CoverData(0x200, 0), None)
            self.toggle_cover_id = cover.cover_id
    
    def setCanonicalName(self, name: str):
        """Set canonical signal name"""
        self._canonical_name = name
        # Could store this in a property if needed
    
    def getCanonicalName(self) -> str:
        """Get canonical signal name"""
        return self._canonical_name
    
    def setToggleMetric(self, metric: ToggleMetricT):
        """Set toggle metric type"""
        self._toggle_metric = metric
    
    def getToggleMetric(self) -> ToggleMetricT:
        """Get toggle metric type"""
        return self._toggle_metric
    
    def setToggleType(self, ttype: ToggleTypeT):
        """Set toggle type"""
        self._toggle_type = ttype
    
    def getToggleType(self) -> ToggleTypeT:
        """Get toggle type"""
        return self._toggle_type
    
    def setToggleDir(self, dir: ToggleDirT):
        """Set toggle direction"""
        self._toggle_dir = dir
    
    def getToggleDir(self) -> ToggleDirT:
        """Get toggle direction"""
        return self._toggle_dir
    
    def setNumBits(self, num_bits: int):
        """Set number of bits in signal"""
        self._num_bits = num_bits
    
    def getNumBits(self) -> int:
        """Get number of bits in signal"""
        if self._num_bits == 0:
            # Count from database
            self._ensure_toggle_data()
            cursor = self.ucis_db.conn.execute(
                "SELECT COUNT(*) FROM toggle_bits WHERE cover_id = ?",
                (self.toggle_cover_id,)
            )
            row = cursor.fetchone()
            self._num_bits = row[0] if row else 0
        return self._num_bits
    
    def getBit(self, bit_index: int) -> ToggleBit:
        """Get toggle bit at index"""
        if bit_index in self._bits_cache:
            return self._bits_cache[bit_index]
        
        self._ensure_toggle_data()
        bit = ToggleBit(self, bit_index)
        self._bits_cache[bit_index] = bit
        return bit
    
    def createBit(self, bit_index: int, bit_type: int = 0) -> ToggleBit:
        """Create a new toggle bit"""
        self._ensure_toggle_data()
        
        bit = ToggleBit(self, bit_index, bit_type)
        self._bits_cache[bit_index] = bit
        
        # Insert into database
        self.ucis_db.conn.execute(
            """INSERT OR IGNORE INTO toggle_bits 
               (cover_id, bit_index, bit_type, toggle_01, toggle_10)
               VALUES (?, ?, ?, 0, 0)""",
            (self.toggle_cover_id, bit_index, bit_type)
        )
        
        return bit
    
    def getBits(self):
        """Iterate all toggle bits"""
        self._ensure_toggle_data()
        
        cursor = self.ucis_db.conn.execute(
            """SELECT bit_index FROM toggle_bits 
               WHERE cover_id = ?
               ORDER BY bit_index""",
            (self.toggle_cover_id,)
        )
        
        for row in cursor:
            yield self.getBit(row[0])
    
    def getTotalToggle01(self) -> int:
        """Get total 0->1 transitions across all bits"""
        self._ensure_toggle_data()
        
        cursor = self.ucis_db.conn.execute(
            "SELECT SUM(toggle_01) FROM toggle_bits WHERE cover_id = ?",
            (self.toggle_cover_id,)
        )
        row = cursor.fetchone()
        return row[0] if row and row[0] else 0
    
    def getTotalToggle10(self) -> int:
        """Get total 1->0 transitions across all bits"""
        self._ensure_toggle_data()
        
        cursor = self.ucis_db.conn.execute(
            "SELECT SUM(toggle_10) FROM toggle_bits WHERE cover_id = ?",
            (self.toggle_cover_id,)
        )
        row = cursor.fetchone()
        return row[0] if row and row[0] else 0
    
    def getCoveragePercent(self) -> float:
        """Calculate toggle coverage percentage"""
        num_bits = self.getNumBits()
        if num_bits == 0:
            return 0.0
        
        # Count bits with both transitions
        self._ensure_toggle_data()
        cursor = self.ucis_db.conn.execute(
            """SELECT COUNT(*) FROM toggle_bits 
               WHERE cover_id = ? AND toggle_01 > 0 AND toggle_10 > 0""",
            (self.toggle_cover_id,)
        )
        row = cursor.fetchone()
        covered = row[0] if row else 0
        
        return (100.0 * covered / num_bits) if num_bits > 0 else 0.0
