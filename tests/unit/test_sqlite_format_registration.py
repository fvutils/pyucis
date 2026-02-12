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
Test SQLite format registration and instantiation.

This test verifies that the SQLite format is properly registered with the
format registry and can be instantiated correctly. This addresses the issue
where DbFormatIfSqlite.register() was passing an instance instead of a class,
causing TypeError when downstream code tried to call desc.fmt_if().
"""

import pytest
import os
import tempfile
from ucis.rgy.format_rgy import FormatRgy
from ucis.sqlite.db_format_if_sqlite import DbFormatIfSqlite


class TestSqliteFormatRegistration:
    """Test SQLite format registration and instantiation"""

    def test_sqlite_format_registered(self):
        """Verify SQLite format is registered in format registry"""
        rgy = FormatRgy.inst()
        assert rgy.hasDatabaseFormat("sqlite"), "SQLite format should be registered"

    def test_sqlite_format_callable(self):
        """Verify fmt_if is callable (a class, not an instance)"""
        rgy = FormatRgy.inst()
        desc = rgy.getDatabaseDesc("sqlite")
        
        # The fmt_if should be a class (callable), not an instance
        assert callable(desc.fmt_if), "fmt_if should be callable (a class)"
        
        # Calling it should return an instance of DbFormatIfSqlite
        fmt_if_instance = desc.fmt_if()
        assert isinstance(fmt_if_instance, DbFormatIfSqlite), \
            f"Expected DbFormatIfSqlite instance, got {type(fmt_if_instance)}"

    def test_sqlite_format_create(self):
        """Verify we can create a SQLite database through the format interface"""
        rgy = FormatRgy.inst()
        desc = rgy.getDatabaseDesc("sqlite")
        
        # Get an instance of the format interface
        fmt_if = desc.fmt_if()
        
        # Create an in-memory database
        db = fmt_if.create()
        assert db is not None, "Should be able to create an in-memory database"
        
        # Verify it's a SqliteUCIS instance
        from ucis.sqlite.sqlite_ucis import SqliteUCIS
        assert isinstance(db, SqliteUCIS), \
            f"Expected SqliteUCIS instance, got {type(db)}"

    def test_sqlite_format_read_write(self):
        """Verify we can read/write SQLite databases through the format interface"""
        rgy = FormatRgy.inst()
        desc = rgy.getDatabaseDesc("sqlite")
        
        # Get an instance of the format interface
        fmt_if = desc.fmt_if()
        
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(suffix='.ucisdb', delete=False) as f:
            test_db_path = f.name
        
        try:
            # Create a database with some content
            from ucis.scope_type_t import ScopeTypeT
            from ucis.source_t import SourceT
            from ucis.flags_t import FlagsT
            
            db = fmt_if.create(test_db_path)
            db.createScope("test_scope", None, 1, SourceT.NONE, 
                          ScopeTypeT.INSTANCE, FlagsT(0))
            db.close()
            
            # Verify file was created
            assert os.path.exists(test_db_path), "Database file should be created"
            assert os.path.getsize(test_db_path) > 0, "Database file should not be empty"
            
            # Read it back
            db2 = fmt_if.read(test_db_path)
            assert db2 is not None, "Should be able to read database"
            
            # Verify we can access the scope
            scopes = list(db2.scopes(ScopeTypeT.INSTANCE))
            assert len(scopes) > 0, "Should have at least one scope"
            assert scopes[0].getScopeName() == "test_scope", \
                "Scope name should match what we created"
            
            db2.close()
            
        finally:
            # Clean up
            if os.path.exists(test_db_path):
                os.unlink(test_db_path)

    def test_sqlite_cli_integration(self):
        """
        Verify convert command can use SQLite format without errors.
        This simulates what cmd_convert.py does: desc.fmt_if() to get interface.
        """
        from ucis.mem.mem_ucis import MemUCIS
        from ucis.source_info import SourceInfo
        from ucis.source_t import SourceT
        from ucis.scope_type_t import ScopeTypeT
        from ucis.cover_data import CoverData
        from ucis.cover_type_t import CoverTypeT
        from ucis.flags_t import FlagsT
        from ucis.xml.xml_factory import XmlFactory
        
        rgy = FormatRgy.inst()
        
        # Create a simple test database in memory
        db = MemUCIS()
        fh = db.createFileHandle("test.sv", os.getcwd())
        si = SourceInfo(fh, 1, 0)
        du = db.createScope("tb", si, 1, SourceT.NONE, ScopeTypeT.DU_MODULE, FlagsT(0))
        inst = db.createInstance("tb", si, 1, SourceT.NONE, ScopeTypeT.INSTANCE, du, FlagsT(0))
        cg = inst.createCovergroup("cg", si, 1, SourceT.NONE)
        cp = cg.createScope("cp", si, 1, SourceT.NONE, ScopeTypeT.COVERPOINT, FlagsT(0))
        cd = CoverData(CoverTypeT.CVGBIN, 0)
        cd.data = 5
        cp.createNextCover("bin0", cd, si)
        
        # Write to XML first
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            xml_path = f.name
        
        try:
            XmlFactory.write(db, xml_path)
            
            # Now simulate what cmd_convert does
            input_desc = rgy.getDatabaseDesc("xml")
            output_desc = rgy.getDatabaseDesc("sqlite")
            
            # This is the critical line that was failing
            input_if = input_desc.fmt_if()
            output_if = output_desc.fmt_if()
            
            # Read input
            in_db = input_if.read(xml_path)
            
            # Create output in memory
            out_db = output_if.create()
            
            # Simple verification that we can work with both databases
            from ucis.scope_type_t import ScopeTypeT
            for scope in in_db.scopes(ScopeTypeT.INSTANCE):
                # Just verify we can iterate
                assert scope is not None
            
            in_db.close()
            out_db.close()
            
        finally:
            if os.path.exists(xml_path):
                os.unlink(xml_path)
