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
SQLite-backed Coverpoint implementation
"""

from ucis.coverpoint import Coverpoint
from ucis.cover_index import CoverIndex
from ucis.cover_data import CoverData
from ucis.cover_type_t import CoverTypeT
from ucis.cover_flags_t import CoverFlagsT
from ucis.source_info import SourceInfo
from ucis.sqlite.sqlite_scope import SqliteScope


class SqliteCoverpoint(SqliteScope, Coverpoint):
    """SQLite-backed coverpoint with bin management"""
    
    def __init__(self, ucis_db, scope_id: int):
        """Initialize SqliteCoverpoint"""
        # Must set ucis_db FIRST for getattr check in setGoal
        self.ucis_db = ucis_db
        self._initializing = True
        
        # Coverpoint-specific attributes (lazy loaded)
        # Must initialize BEFORE parent __init__ since it calls setGoal() -> _ensure_loaded()
        self._at_least = None
        self._auto_bin_max = None
        self._detect_overlap = None
        self._strobe = None
        self._comment = None
        
        # Initialize parent classes
        SqliteScope.__init__(self, ucis_db, scope_id)
        
        # Reset initialization flag before calling Coverpoint.__init__
        # because CvgScope.__init__ (parent of Coverpoint) calls setters with defaults
        self._initializing = True
        Coverpoint.__init__(self)
        
        # Clear initialization flag NOW, after all parent __init__ calls
        self._initializing = False
    
    def _ensure_loaded(self):
        """Lazy load scope data including coverpoint-specific columns"""
        super()._ensure_loaded()
        
        # Don't use caching - always reload from database
        # Multiple Python objects may exist for same scope_id
        
        # Load coverpoint-specific columns
        cursor = self.ucis_db.conn.execute(
            """SELECT at_least, auto_bin_max, detect_overlap, strobe
               FROM scopes WHERE scope_id = ?""",
            (self.scope_id,)
        )
        
        row = cursor.fetchone()
        if row:
            self._at_least = row[0] if row[0] is not None else 1
            self._auto_bin_max = row[1] if row[1] is not None else 64
            self._detect_overlap = bool(row[2]) if row[2] is not None else False
            self._strobe = bool(row[3]) if row[3] is not None else False
        else:
            # Set defaults if columns don't exist yet
            self._at_least = 1
            self._auto_bin_max = 64
            self._detect_overlap = False
            self._strobe = False
        
        self._comment = ""
    
    # CvgScope methods
    def getAtLeast(self) -> int:
        self._ensure_loaded()
        return self._at_least
    
    def setAtLeast(self, value: int):
        if getattr(self, '_initializing', False):
            return
        self._ensure_loaded()
        self._at_least = value
        self.ucis_db.conn.execute(
            "UPDATE scopes SET at_least = ? WHERE scope_id = ?",
            (value, self.scope_id)
        )
    
    def getAutoBinMax(self) -> int:
        self._ensure_loaded()
        return self._auto_bin_max
    
    def setAutoBinMax(self, value: int):
        if getattr(self, '_initializing', False):
            return
        self._ensure_loaded()
        self._auto_bin_max = value
        self.ucis_db.conn.execute(
            "UPDATE scopes SET auto_bin_max = ? WHERE scope_id = ?",
            (value, self.scope_id)
        )
    
    def getDetectOverlap(self) -> bool:
        self._ensure_loaded()
        return self._detect_overlap
    
    def setDetectOverlap(self, value: bool):
        if getattr(self, '_initializing', False):
            return
        self._ensure_loaded()
        self._detect_overlap = value
        self.ucis_db.conn.execute(
            "UPDATE scopes SET detect_overlap = ? WHERE scope_id = ?",
            (1 if value else 0, self.scope_id)
        )
    
    def getStrobe(self) -> bool:
        self._ensure_loaded()
        return self._strobe
    
    def setStrobe(self, value: bool):
        if getattr(self, '_initializing', False):
            return
        self._ensure_loaded()
        self._strobe = value
        self.ucis_db.conn.execute(
            "UPDATE scopes SET strobe = ? WHERE scope_id = ?",
            (1 if value else 0, self.scope_id)
        )
    
    def getComment(self) -> str:
        from ucis.str_property import StrProperty
        val = self.getStringProperty(-1, StrProperty.COMMENT)
        return val if val is not None else ''
    
    def setComment(self, value: str):
        from ucis.str_property import StrProperty
        self.setStringProperty(-1, StrProperty.COMMENT, value)
    def getScopeGoal(self) -> int:
        """Get coverpoint-specific goal"""
        return self.getGoal()
    
    def setScopeGoal(self, goal: int):
        """Set coverpoint-specific goal"""
        self.setGoal(goal)
    
    # Bin creation method
    def createBin(self, name: str, srcinfo: SourceInfo, at_least: int,
                 count: int, rhs: str, kind: CoverTypeT = CoverTypeT.CVGBIN) -> CoverIndex:
        """Create a bin (coverage item) for this coverpoint"""
        # Create CoverData with appropriate flags
        coverdata = CoverData(
            kind,
            (CoverFlagsT.IS_32BIT | CoverFlagsT.HAS_GOAL | CoverFlagsT.HAS_WEIGHT)
        )
        coverdata.data = count
        coverdata.at_least = at_least
        coverdata.goal = 1
        coverdata.weight = 1
        
        # Use inherited createNextCover from SqliteScope
        index = self.createNextCover(name, coverdata, srcinfo)
        
        return index
