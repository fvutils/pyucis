"""
Basic database creation and lifecycle tests.

Tests fundamental database operations across all backends.
Priority: Phase 1 (Foundation)
"""

import pytest
from ucis import (UCIS_VLOG, UCIS_INSTANCE, UCIS_DU_MODULE, UCIS_SCOPE_UNDER_DU,
                  UCIS_INST_ONCE, UCIS_ENABLED_STMT, UCIS_HISTORYNODE_TEST,
                  UCIS_TESTSTATUS_OK, UCIS_OTHER)
from ucis.source_info import SourceInfo
from ucis.test_data import TestData
from ucis.scope_type_t import ScopeTypeT


class TestApiBasic:
    """Basic database creation and metadata tests"""
    
    def test_create_empty_database(self, backend):
        """Test creating a minimal valid database"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        # Create database
        db = create_db()
        assert db is not None, f"Failed to create database for {backend_name}"
        
        # Add minimal required content
        # 1. History node (test metadata)
        testnode = db.createHistoryNode(
            None,
            "test_logical",
            "test_physical",
            UCIS_HISTORYNODE_TEST
        )
        td = TestData(
            teststatus=UCIS_TESTSTATUS_OK,
            toolcategory="UCIS:test",
            date="20240101000000"
        )
        testnode.setTestData(td)
        
        # 2. File handle
        file_h = db.createFileHandle("test.sv", "/tmp")
        
        # 3. Design unit
        du = db.createScope(
            "work.minimal",
            SourceInfo(file_h, 1, 0),
            1,
            UCIS_VLOG,
            UCIS_DU_MODULE,
            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE
        )
        
        # 4. Instance (this creates an instanceCoverages element in XML)
        inst = db.createInstance(
            "minimal_inst",
            None,
            1,
            UCIS_VLOG,
            UCIS_INSTANCE,
            du,
            UCIS_INST_ONCE
        )
        
        # Persist (for file-based backends)
        result = write_db(db, temp_file)
        
        # Read back
        db2 = read_db(result if result else db)
        assert db2 is not None, f"Failed to read database for {backend_name}"
        
        # Verify we can find the instance
        insts = list(db2.scopes(ScopeTypeT.INSTANCE))
        assert len(insts) >= 1, f"No instances found for {backend_name}"
    
    def test_database_with_design_unit_and_instance(self, backend):
        """Test database with design unit and instance"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        # Create database
        db = create_db()
        
        # Add history node (required for XML)
        testnode = db.createHistoryNode(
            None,
            "test_logical",
            "test_physical",
            UCIS_HISTORYNODE_TEST
        )
        td = TestData(
            teststatus=UCIS_TESTSTATUS_OK,
            toolcategory="UCIS:test",
            date="20240101000000"
        )
        testnode.setTestData(td)
        
        # Create a file handle
        file_h = db.createFileHandle("test.sv", "/tmp")
        
        # Create a design unit
        du = db.createScope(
            "work.test_module",
            SourceInfo(file_h, 1, 0),
            1,  # weight
            UCIS_VLOG,
            UCIS_DU_MODULE,
            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE | UCIS_ENABLED_STMT
        )
        assert du is not None
        
        # Create an instance
        inst = db.createInstance(
            "top",
            None,  # source info
            1,  # weight
            UCIS_VLOG,
            UCIS_INSTANCE,
            du,  # reference to DU
            UCIS_INST_ONCE
        )
        
        assert inst is not None, f"Failed to create instance for {backend_name}"
        assert inst.getScopeName() == "top"
        
        # Persist
        result = write_db(db, temp_file)
        
        # Read back
        db2 = read_db(result if result else db)
        
        # Verify instance exists
        # All backends require a mask parameter for scopes()
        scopes = list(db2.scopes(ScopeTypeT.INSTANCE))
        
        assert len(scopes) >= 1, f"No scopes found after read for {backend_name}"
        
        # Find our instance
        found = False
        for s in scopes:
            if s.getScopeName() == "top":
                found = True
                assert s.getScopeType() == UCIS_INSTANCE
                break
        
        assert found, f"Could not find 'top' instance after read for {backend_name}"
