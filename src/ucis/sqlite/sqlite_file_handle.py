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
SQLite-backed FileHandle implementation
"""

from ucis.file_handle import FileHandle


class SqliteFileHandle(FileHandle):
    """SQLite-backed file handle"""
    
    def __init__(self, ucis_db, file_id: int, filename: str):
        super().__init__()
        self.ucis_db = ucis_db
        self.file_id = file_id
        self.filename = filename
    
    def getFileName(self) -> str:
        """Get file name"""
        return self.filename
    
    def setFileName(self, name: str):
        """Set file name"""
        self.filename = name
        self.ucis_db.conn.execute(
            "UPDATE files SET file_path = ? WHERE file_id = ?",
            (name, self.file_id)
        )
