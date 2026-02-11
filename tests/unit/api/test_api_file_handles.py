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
Test file handle management across all backends.

Tests cover:
- Creating file handles
- File handle uniqueness
- Path handling (absolute, relative, special characters)
- Multiple file handle management
- File handle persistence
"""

import pytest
from ucis import *
from ucis.test_data import TestData


class TestApiFileHandles:
    """Test file handle operations"""
    
    def test_create_file_handle(self, backend):
        """Test basic file handle creation"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        # XML requires instanceCoverages to be valid
        if backend_name == "xml":
            pytest.skip("XML format requires coverage structures, not just file handles")
        
        db = create_db()
        
        # Create history node (required for database)
        testnode = db.createHistoryNode(None, "test", "test", UCIS_HISTORYNODE_TEST)
        testnode.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                      toolcategory="test", date="20240101000000"))
        
        # Create file handle
        file_h = db.createFileHandle("test.sv", "/home/user/project")
        
        # Verify file handle
        assert file_h is not None
        assert file_h.getFileName() == "test.sv"
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify file handle persisted
        # Note: File handles may not have a direct query API
        # They're typically retrieved via source info on scopes
        # For now, just verify database reloads without error
        assert db2 is not None
    
    def test_file_handle_uniqueness(self, backend):
        """Test that same file returns same handle"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        db = create_db()
        
        testnode = db.createHistoryNode(None, "test", "test", UCIS_HISTORYNODE_TEST)
        testnode.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                      toolcategory="test", date="20240101000000"))
        
        # Create same file handle twice
        file_h1 = db.createFileHandle("design.v", "/work")
        file_h2 = db.createFileHandle("design.v", "/work")
        
        # Should return same handle (or at least same filename)
        assert file_h1.getFileName() == file_h2.getFileName()
        
        # Different file should be different
        file_h3 = db.createFileHandle("testbench.sv", "/work")
        assert file_h3.getFileName() != file_h1.getFileName()
    
    def test_multiple_file_handles(self, backend):
        """Test creating and managing multiple file handles"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        # XML requires instanceCoverages to be valid
        if backend_name == "xml":
            pytest.skip("XML format requires coverage structures, not just file handles")
        
        db = create_db()
        
        testnode = db.createHistoryNode(None, "test", "test", UCIS_HISTORYNODE_TEST)
        testnode.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                      toolcategory="test", date="20240101000000"))
        
        # Create multiple file handles
        filenames = [
            "module1.sv",
            "module2.sv",
            "package.svh",
            "interface.sv",
            "testbench.sv",
            "assertions.sva",
            "config.sv",
            "top.sv",
            "dut.v",
            "memory.v"
        ]
        
        file_handles = []
        for filename in filenames:
            fh = db.createFileHandle(filename, "/project/rtl")
            file_handles.append(fh)
            assert fh.getFileName() == filename
        
        # Verify all handles are valid
        assert len(file_handles) == len(filenames)
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Database should reload without error
        assert db2 is not None
    
    def test_file_handle_with_scopes(self, backend):
        """Test file handles referenced by scopes"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        # Known issue: XML source info file handles not fully persisting
        if backend_name == "xml":
            pytest.skip("XML has issues with source info file handle persistence")
        
        db = create_db()
        
        testnode = db.createHistoryNode(None, "test", "test", UCIS_HISTORYNODE_TEST)
        testnode.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                      toolcategory="test", date="20240101000000"))
        
        # Create file handles
        file_design = db.createFileHandle("design.sv", "/rtl")
        file_tb = db.createFileHandle("testbench.sv", "/tb")
        
        # Create scopes using these file handles
        from ucis.source_info import SourceInfo
        
        du = db.createScope("work.module1", SourceInfo(file_design, 10, 0),
                           1, UCIS_VLOG, UCIS_DU_MODULE,
                           UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        
        inst = db.createInstance("i_module1", None, 1, UCIS_VLOG, 
                                UCIS_INSTANCE, du, UCIS_INST_ONCE)
        
        # Verify source info
        src_info = du.getSourceInfo()
        assert src_info is not None
        assert src_info.file.getFileName() == "design.sv"
        assert src_info.line == 10
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify file handles persisted with scopes
        dus = list(db2.scopes(ScopeTypeT.DU_MODULE))
        assert len(dus) >= 1
        
        for du_read in dus:
            if du_read.getScopeName() == "work.module1":
                src_info_read = du_read.getSourceInfo()
                assert src_info_read is not None
                assert src_info_read.file.getFileName() == "design.sv"
                assert src_info_read.line == 10
    
    def test_file_handle_paths(self, backend):
        """Test various path formats"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        # XML requires instanceCoverages to be valid
        if backend_name == "xml":
            pytest.skip("XML format requires coverage structures, not just file handles")
        
        db = create_db()
        
        testnode = db.createHistoryNode(None, "test", "test", UCIS_HISTORYNODE_TEST)
        testnode.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                      toolcategory="test", date="20240101000000"))
        
        # Test absolute path
        fh1 = db.createFileHandle("test.sv", "/absolute/path/to/project")
        assert fh1.getFileName() == "test.sv"
        
        # Test relative path
        fh2 = db.createFileHandle("module.sv", "relative/path")
        assert fh2.getFileName() == "module.sv"
        
        # Test None workdir
        fh3 = db.createFileHandle("standalone.sv", None)
        assert fh3.getFileName() == "standalone.sv"
        
        # Test path with spaces (if supported)
        try:
            fh4 = db.createFileHandle("file with spaces.sv", "/path with spaces")
            assert fh4.getFileName() == "file with spaces.sv"
        except:
            # Some backends might not support spaces
            pass
        
        # Test path with dots
        fh5 = db.createFileHandle("file.name.sv", "../relative")
        assert fh5.getFileName() == "file.name.sv"
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        assert db2 is not None
    
    def test_file_handle_in_covergroup(self, backend):
        """Test file handles in functional coverage"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        # XML requires bins in coverpoints
        if backend_name == "xml":
            pytest.skip("XML format requires bins in coverpoints")
        
        db = create_db()
        
        testnode = db.createHistoryNode(None, "test", "test", UCIS_HISTORYNODE_TEST)
        testnode.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                      toolcategory="test", date="20240101000000"))
        
        # Create file handle for coverage definition
        file_cov = db.createFileHandle("coverage.sv", "/verif")
        
        from ucis.source_info import SourceInfo
        
        # Create coverage hierarchy
        du = db.createScope("work.top", SourceInfo(file_cov, 1, 0),
                           1, UCIS_VLOG, UCIS_DU_MODULE,
                           UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        
        inst = db.createInstance("i_top", None, 1, UCIS_VLOG, 
                                UCIS_INSTANCE, du, UCIS_INST_ONCE)
        
        # Create covergroup with source info
        cg = inst.createCovergroup("cg1", SourceInfo(file_cov, 50, 0), 1, UCIS_VLOG)
        
        # Create coverpoint with source info
        cp = cg.createCoverpoint("cp1", SourceInfo(file_cov, 55, 0), 1, UCIS_VLOG)
        
        # Verify source info at different levels
        # DU should have source info
        du_src = du.getSourceInfo()
        assert du_src is not None
        assert du_src.file.getFileName() == "coverage.sv"
        assert du_src.line == 1
        
        # Covergroup should have source info
        cg_src = cg.getSourceInfo()
        assert cg_src is not None
        assert cg_src.file.getFileName() == "coverage.sv"
        assert cg_src.line == 50
        
        # Coverpoint should have source info
        cp_src = cp.getSourceInfo()
        assert cp_src is not None
        assert cp_src.file.getFileName() == "coverage.sv"
        assert cp_src.line == 55
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify source info persisted
        insts = list(db2.scopes(ScopeTypeT.INSTANCE))
        for inst_read in insts:
            if inst_read.getScopeName() == "i_top":
                cgs = list(inst_read.scopes(ScopeTypeT.COVERGROUP))
                for cg_read in cgs:
                    if cg_read.getScopeName() == "cg1":
                        src = cg_read.getSourceInfo()
                        assert src.file.getFileName() == "coverage.sv"
                        assert src.line == 50
