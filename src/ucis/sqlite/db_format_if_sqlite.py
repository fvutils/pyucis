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
SQLite format interface for UCIS database format registry
"""

from ucis.rgy.format_if_db import FormatIfDb, FormatDescDb, FormatDbFlags
from ucis.ucis import UCIS
from ucis.sqlite.sqlite_ucis import SqliteUCIS


class DbFormatIfSqlite(FormatIfDb):
    """SQLite database format interface"""
    
    def __init__(self):
        self.options = {}
    
    def init(self, options):
        """
        Initialize with options
        
        Supported options:
            in_memory: bool - Create in-memory database (default: False)
        """
        self.options = options or {}
    
    def create(self, filename=None) -> UCIS:
        """
        Create a new SQLite UCIS database
        
        Args:
            filename: Path to database file, or None for in-memory
            
        Returns:
            SqliteUCIS database object
        """
        if filename:
            return SqliteUCIS(filename)
        else:
            return SqliteUCIS()  # In-memory
    
    def read(self, file_or_filename) -> UCIS:
        """
        Read/open an existing SQLite UCIS database
        
        Args:
            file_or_filename: Path to .ucisdb file or file object
            
        Returns:
            SqliteUCIS database object
        """
        if isinstance(file_or_filename, str):
            return SqliteUCIS(file_or_filename)
        else:
            # If file object, get the name
            if hasattr(file_or_filename, 'name'):
                return SqliteUCIS(file_or_filename.name)
            else:
                raise ValueError("SQLite format requires file path, not file object")
    
    @classmethod
    def register(cls, rgy):
        """Register SQLite format with format registry"""
        rgy.addDatabaseFormat(FormatDescDb(
            fmt_if=cls,
            name='sqlite',
            flags=FormatDbFlags.Create | FormatDbFlags.Read | FormatDbFlags.Write,
            description='SQLite database format - persistent, queryable storage'
        ))
