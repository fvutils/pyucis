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
SQLite-backed CoverIndex implementation
"""

from ucis.cover_index import CoverIndex
from ucis.cover_data import CoverData
from ucis.source_info import SourceInfo


class SqliteCoverIndex(CoverIndex):
    """SQLite-backed coverage item"""
    
    def __init__(self, ucis_db, cover_id: int):
        super().__init__()
        self.ucis_db = ucis_db
        self.cover_id = cover_id
        self._loaded = False
        self._cover_name = None
        self._cover_data = None
        self._source_info = None
        
    def _ensure_loaded(self):
        """Lazy load coverage data from database"""
        if self._loaded:
            return
        
        cursor = self.ucis_db.conn.execute(
            """SELECT cover_name, cover_type, cover_data, at_least,
                      source_file_id, source_line, source_token
               FROM coveritems WHERE cover_id = ?""",
            (self.cover_id,)
        )
        
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Cover item {self.cover_id} not found in database")
        
        self._cover_name = row[0]
        cover_type = row[1]
        cover_count = row[2]
        at_least = row[3]
        
        self._cover_data = CoverData(cover_type, 0)
        self._cover_data.data = cover_count
        self._cover_data.goal = at_least
        
        # Load source info
        if row[4] is not None:
            file_cursor = self.ucis_db.conn.execute(
                "SELECT file_path FROM files WHERE file_id = ?",
                (row[4],)
            )
            file_row = file_cursor.fetchone()
            file_path = file_row[0] if file_row else None
            
            from ucis.file_handle import FileHandle
            file_handle = self.ucis_db.createFileHandle(file_path, None) if file_path else None
            self._source_info = SourceInfo(file_handle, row[5], row[6])
        else:
            self._source_info = SourceInfo(None, -1, -1)
        
        self._loaded = True
    
    def getName(self) -> str:
        """Get coverage item name"""
        self._ensure_loaded()
        return self._cover_name
    
    def getCoverData(self) -> CoverData:
        """Get coverage data"""
        self._ensure_loaded()
        return self._cover_data
    
    def getCount(self) -> int:
        """Get coverage count"""
        return self.getCoverData().data
    
    def setCount(self, count: int):
        """Set coverage count"""
        self._ensure_loaded()
        self._cover_data.data = count
        # Update database
        self.ucis_db.conn.execute(
            "UPDATE coveritems SET cover_data = ? WHERE cover_id = ?",
            (count, self.cover_id)
        )
    
    def getSourceInfo(self) -> SourceInfo:
        """Get source information"""
        self._ensure_loaded()
        return self._source_info
    
    def incrementCover(self, amt: int = 1):
        """Increment coverage count"""
        self._ensure_loaded()
        
        new_count = self._cover_data.data + amt
        self.setCount(new_count)
