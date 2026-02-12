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
SQLite-backed Covergroup implementation
"""

from typing import List
from ucis.covergroup import Covergroup
from ucis.source_info import SourceInfo
from ucis.source_t import SourceT
from ucis.scope_type_t import ScopeTypeT
from ucis.sqlite.sqlite_scope import SqliteScope


class SqliteCovergroup(SqliteScope, Covergroup):
    """SQLite-backed covergroup with specialized methods"""
    
    def __init__(self, ucis_db, scope_id: int):
        """Initialize SqliteCovergroup"""
        # Must set ucis_db FIRST for getattr check in setGoal
        self.ucis_db = ucis_db
        self._initializing = True
        
        # Covergroup-specific attributes (lazy loaded)
        # Must initialize BEFORE parent __init__ since it calls setGoal() -> _ensure_loaded()
        self._per_instance = None
        self._merge_instances = None
        self._get_inst_coverage = None
        self._at_least = None
        self._auto_bin_max = None
        self._detect_overlap = None
        self._strobe = None
        self._comment = None
        
        # Initialize parent classes
        SqliteScope.__init__(self, ucis_db, scope_id)
        
        # Reset initialization flag before calling Covergroup.__init__
        # because Covergroup.__init__ calls setters with defaults
        self._initializing = True
        Covergroup.__init__(self)
        
        # Clear initialization flag NOW, after all parent __init__ calls
        self._initializing = False
    
    def _ensure_loaded(self):
        """Lazy load scope data including covergroup-specific columns"""
        super()._ensure_loaded()
        
        # Don't use caching - always reload from database
        # Multiple Python objects may exist for same scope_id
        
        # Load covergroup-specific columns
        cursor = self.ucis_db.conn.execute(
            """SELECT per_instance, merge_instances, get_inst_coverage,
                      at_least, auto_bin_max, detect_overlap, strobe
               FROM scopes WHERE scope_id = ?""",
            (self.scope_id,)
        )
        
        row = cursor.fetchone()
        if row:
            self._per_instance = bool(row[0]) if row[0] is not None else False
            self._merge_instances = bool(row[1]) if row[1] is not None else True
            self._get_inst_coverage = bool(row[2]) if row[2] is not None else False
            self._at_least = row[3] if row[3] is not None else 1
            self._auto_bin_max = row[4] if row[4] is not None else 64
            self._detect_overlap = bool(row[5]) if row[5] is not None else False
            self._strobe = bool(row[6]) if row[6] is not None else False
        else:
            # Set defaults if columns don't exist yet
            self._per_instance = False
            self._merge_instances = True
            self._get_inst_coverage = False
            self._at_least = 1
            self._auto_bin_max = 64
            self._detect_overlap = False
            self._strobe = False
        
        self._comment = ""
    
    # Covergroup-specific methods
    def getPerInstance(self) -> bool:
        self._ensure_loaded()
        return self._per_instance
    
    def setPerInstance(self, value: bool):
        if getattr(self, '_initializing', False):
            return
        self._ensure_loaded()
        self._per_instance = value
        self.ucis_db.conn.execute(
            "UPDATE scopes SET per_instance = ? WHERE scope_id = ?",
            (1 if value else 0, self.scope_id)
        )
    
    def getMergeInstances(self) -> bool:
        self._ensure_loaded()
        return self._merge_instances
    
    def setMergeInstances(self, value: bool):
        if getattr(self, '_initializing', False):
            return
        self._ensure_loaded()
        self._merge_instances = value
        self.ucis_db.conn.execute(
            "UPDATE scopes SET merge_instances = ? WHERE scope_id = ?",
            (1 if value else 0, self.scope_id)
        )
    
    def getGetInstCoverage(self) -> bool:
        self._ensure_loaded()
        return self._get_inst_coverage
    
    def setGetInstCoverage(self, value: bool):
        if getattr(self, '_initializing', False):
            return
        self._ensure_loaded()
        self._get_inst_coverage = value
        self.ucis_db.conn.execute(
            "UPDATE scopes SET get_inst_coverage = ? WHERE scope_id = ?",
            (1 if value else 0, self.scope_id)
        )
    
    # CvgScope methods (inherited from Covergroup via CvgScope)
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
        self._ensure_loaded()
        return self._comment
    
    def setComment(self, value: str):
        self._ensure_loaded()
        self._comment = value
        # Note: comment might be stored in properties table or separate column
    
    # Creation methods
    def createCoverpoint(self, name: str, srcinfo: SourceInfo, weight: int,
                        source: SourceT):
        """Create a coverpoint as a child scope"""
        from ucis.sqlite.sqlite_coverpoint import SqliteCoverpoint
        
        # Create scope in database
        scope = self.createScope(name, srcinfo, weight, source,
                                ScopeTypeT.COVERPOINT, 0)
        
        # Return as SqliteCoverpoint
        return SqliteCoverpoint(self.ucis_db, scope.scope_id)
    
    def createCross(self, name: str, srcinfo: SourceInfo, weight: int,
                   source: SourceT, points_l: List['Coverpoint']):
        """Create a cross coverage scope"""
        from ucis.sqlite.sqlite_cross import SqliteCross
        
        # Create scope in database
        scope = self.createScope(name, srcinfo, weight, source,
                                ScopeTypeT.CROSS, 0)
        
        # Create SqliteCross object
        cross = SqliteCross(self.ucis_db, scope.scope_id)
        
        # Store cross point references
        for index, coverpoint in enumerate(points_l):
            cross.addCoverpoint(coverpoint, index)
        
        return cross
    
    def createCoverInstance(self, name: str, srcinfo: SourceInfo, weight: int,
                          source: SourceT) -> 'Covergroup':
        """Create a covergroup instance under this covergroup type.
        
        Creates a new COVERINSTANCE scope representing a specific instantiation
        of this covergroup type. Used when per-instance coverage is enabled to
        track coverage separately for each instance.
        
        Args:
            name: Instance name identifying this instantiation.
            srcinfo: Source location of the instance.
            weight: Relative weight for this instance.
            source: Source language (e.g., SourceT.SV for SystemVerilog).
            
        Returns:
            Newly created SqliteCovergroup object representing the instance.
        """
        # Create scope with COVERINSTANCE type
        scope = self.createScope(name, srcinfo, weight, source,
                                ScopeTypeT.COVERINSTANCE, 0)
        
        # Return as SqliteCovergroup to support covergroup operations
        return SqliteCovergroup(self.ucis_db, scope.scope_id)
