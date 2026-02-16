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

"""AVL (Apheleia Verification Library) format interface for PyUCIS format registry."""

from typing import Union, BinaryIO
from ucis.rgy.format_if_db import FormatIfDb, FormatDescDb, FormatDbFlags
from ucis.mem.mem_ucis import MemUCIS
from ucis import UCIS

from .avl_json_reader import AvlJsonReader


class DbFormatIfAvlJson(FormatIfDb):
    """AVL JSON format interface.
    
    Supports reading AVL (Apheleia Verification Library) JSON export format.
    Handles hierarchical, DataFrame records, and DataFrame table variations.
    """
    
    def read(self, file_or_filename: Union[str, BinaryIO]) -> UCIS:
        """Read AVL JSON file and return UCIS database.
        
        Args:
            file_or_filename: Path to JSON file or file object
            
        Returns:
            UCIS database populated with coverage data
        """
        # Handle file objects vs filenames
        if isinstance(file_or_filename, str):
            filename = file_or_filename
        else:
            # File object - get name if available
            filename = getattr(file_or_filename, 'name', 'coverage.json')
            file_or_filename.close()  # We'll reopen by name
        
        # Create UCIS database
        db = MemUCIS()
        
        # Import coverage
        reader = AvlJsonReader()
        reader.read(filename, db)
        
        return db
    
    def write(self, db: UCIS, file_or_filename: Union[str, BinaryIO]):
        """Write UCIS database to AVL JSON format.
        
        Not yet implemented.
        
        Args:
            db: UCIS database to write
            file_or_filename: Target file
            
        Raises:
            NotImplementedError: Writing not yet supported
        """
        raise NotImplementedError("Writing AVL JSON format not yet supported")
    
    @staticmethod
    def register(rgy):
        """Register AVL JSON format with PyUCIS format registry.
        
        Args:
            rgy: Format registry instance
        """
        rgy.addDatabaseFormat(FormatDescDb(
            DbFormatIfAvlJson,
            "avl-json",
            FormatDbFlags.Read,  # Read-only
            "AVL (Apheleia Verification Library) JSON export format"
        ))
