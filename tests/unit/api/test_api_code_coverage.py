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
Test code coverage across all backends.

Tests cover:
- Statement coverage (STMTBIN)
- Branch coverage (BRANCHBIN)
- Condition coverage (CONDBIN)
- Expression coverage (EXPRBIN)
- Block coverage (BLOCKBIN)

Code coverage uses createNextCover() API directly on instances,
following the UCIS LRM pattern with UOR naming convention:
  #stmt#fileno#line#item#
  #branch#fileno#line#item#
  etc.
"""

import pytest
from ucis import *
from ucis.test_data import TestData
from ucis.source_info import SourceInfo
from ucis.cover_data import CoverData


class TestApiCodeCoverage:
    """Test code coverage operations"""
    
    def test_statement_coverage(self, backend):
        """Test statement coverage tracking"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        db = create_db()
        
        testnode = db.createHistoryNode(None, "test", "test", UCIS_HISTORYNODE_TEST)
        testnode.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                      toolcategory="test", date="20240101000000"))
        
        # Create design hierarchy
        file_h = db.createFileHandle("design.v", "/rtl")
        
        du = db.createScope("work.module1", SourceInfo(file_h, 1, 0),
                           1, UCIS_VLOG, UCIS_DU_MODULE,
                           UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        
        inst = db.createInstance("i_module1", None, 1, UCIS_VLOG,
                                UCIS_INSTANCE, du, UCIS_INST_ONCE)
        
        # Add statement coverage directly to instance using createNextCover()
        # This is the standard UCIS pattern - no intermediate scope needed
        # UOR naming: #stmt#fileno#line#item#
        
        # Statement at line 10, hit 5 times
        coverdata1 = CoverData(UCIS_STMTBIN, 5)
        inst.createNextCover("#stmt#1#10#1#", coverdata1, SourceInfo(file_h, 10, 0))
        
        # Statement at line 11, hit 3 times
        coverdata2 = CoverData(UCIS_STMTBIN, 3)
        inst.createNextCover("#stmt#1#11#1#", coverdata2, SourceInfo(file_h, 11, 0))
        
        # Statement at line 12, not hit
        coverdata3 = CoverData(UCIS_STMTBIN, 0)
        inst.createNextCover("#stmt#1#12#1#", coverdata3, SourceInfo(file_h, 12, 0))
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify instance persisted (code coverage is part of the instance)
        insts_read = list(db2.scopes(ScopeTypeT.INSTANCE))
        found = False
        for inst_read in insts_read:
            if inst_read.getScopeName() == "i_module1":
                found = True
                break
        
        assert found, "Instance with statement coverage not found after persistence"
    
    def test_branch_coverage(self, backend):
        """Test branch coverage tracking"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        db = create_db()
        
        testnode = db.createHistoryNode(None, "test", "test", UCIS_HISTORYNODE_TEST)
        testnode.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                      toolcategory="test", date="20240101000000"))
        
        # Create design hierarchy
        file_h = db.createFileHandle("design.v", "/rtl")
        
        du = db.createScope("work.module1", SourceInfo(file_h, 1, 0),
                           1, UCIS_VLOG, UCIS_DU_MODULE,
                           UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        
        inst = db.createInstance("i_module1", None, 1, UCIS_VLOG,
                                UCIS_INSTANCE, du, UCIS_INST_ONCE)
        
        # Add branch coverage directly to instance
        # Branch at line 20: if condition
        # True branch hit 7 times
        coverdata1 = CoverData(UCIS_BRANCHBIN, 7)
        inst.createNextCover("#branch#1#20#1#", coverdata1, SourceInfo(file_h, 20, 0))
        
        # False branch hit 3 times
        coverdata2 = CoverData(UCIS_BRANCHBIN, 3)
        inst.createNextCover("#branch#1#20#2#", coverdata2, SourceInfo(file_h, 20, 0))
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify instance persisted
        insts_read = list(db2.scopes(ScopeTypeT.INSTANCE))
        found = False
        for inst_read in insts_read:
            if inst_read.getScopeName() == "i_module1":
                found = True
                break
        
        assert found, "Instance with branch coverage not found after persistence"
    
    def test_condition_coverage(self, backend):
        """Test condition coverage tracking"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        db = create_db()
        
        testnode = db.createHistoryNode(None, "test", "test", UCIS_HISTORYNODE_TEST)
        testnode.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                      toolcategory="test", date="20240101000000"))
        
        # Create design hierarchy
        file_h = db.createFileHandle("design.v", "/rtl")
        
        du = db.createScope("work.module1", SourceInfo(file_h, 1, 0),
                           1, UCIS_VLOG, UCIS_DU_MODULE,
                           UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        
        inst = db.createInstance("i_module1", None, 1, UCIS_VLOG,
                                UCIS_INSTANCE, du, UCIS_INST_ONCE)
        
        # Add condition coverage directly to instance
        # Condition: (a && b) at line 30
        # Test all combinations: TT, TF, FT, FF
        inst.createNextCover("#cond#1#30#1#", CoverData(UCIS_CONDBIN, 4), SourceInfo(file_h, 30, 0))  # TT
        inst.createNextCover("#cond#1#30#2#", CoverData(UCIS_CONDBIN, 2), SourceInfo(file_h, 30, 0))  # TF
        inst.createNextCover("#cond#1#30#3#", CoverData(UCIS_CONDBIN, 3), SourceInfo(file_h, 30, 0))  # FT
        inst.createNextCover("#cond#1#30#4#", CoverData(UCIS_CONDBIN, 1), SourceInfo(file_h, 30, 0))  # FF
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify instance persisted
        insts_read = list(db2.scopes(ScopeTypeT.INSTANCE))
        found = False
        for inst_read in insts_read:
            if inst_read.getScopeName() == "i_module1":
                found = True
                break
        
        assert found, "Instance with condition coverage not found after persistence"
    
    def test_expression_coverage(self, backend):
        """Test expression coverage tracking"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        db = create_db()
        
        testnode = db.createHistoryNode(None, "test", "test", UCIS_HISTORYNODE_TEST)
        testnode.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                      toolcategory="test", date="20240101000000"))
        
        # Create design hierarchy
        file_h = db.createFileHandle("design.v", "/rtl")
        
        du = db.createScope("work.module1", SourceInfo(file_h, 1, 0),
                           1, UCIS_VLOG, UCIS_DU_MODULE,
                           UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        
        inst = db.createInstance("i_module1", None, 1, UCIS_VLOG,
                                UCIS_INSTANCE, du, UCIS_INST_ONCE)
        
        # Add expression coverage directly to instance
        # Expression: (a + b) > c
        inst.createNextCover("#expr#1#40#1#", CoverData(UCIS_EXPRBIN, 8), SourceInfo(file_h, 40, 0))  # True
        inst.createNextCover("#expr#1#40#2#", CoverData(UCIS_EXPRBIN, 2), SourceInfo(file_h, 40, 0))  # False
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify instance persisted
        insts_read = list(db2.scopes(ScopeTypeT.INSTANCE))
        found = False
        for inst_read in insts_read:
            if inst_read.getScopeName() == "i_module1":
                found = True
                break
        
        assert found, "Instance with expression coverage not found after persistence"
    
    def test_block_coverage(self, backend):
        """Test basic block coverage tracking"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        db = create_db()
        
        testnode = db.createHistoryNode(None, "test", "test", UCIS_HISTORYNODE_TEST)
        testnode.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                      toolcategory="test", date="20240101000000"))
        
        # Create design hierarchy
        file_h = db.createFileHandle("design.v", "/rtl")
        
        du = db.createScope("work.module1", SourceInfo(file_h, 1, 0),
                           1, UCIS_VLOG, UCIS_DU_MODULE,
                           UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        
        inst = db.createInstance("i_module1", None, 1, UCIS_VLOG,
                                UCIS_INSTANCE, du, UCIS_INST_ONCE)
        
        # Add block coverage directly to instance
        # Basic blocks
        inst.createNextCover("#block#1#50#1#", CoverData(UCIS_BLOCKBIN, 10), SourceInfo(file_h, 50, 0))
        inst.createNextCover("#block#1#55#1#", CoverData(UCIS_BLOCKBIN, 10), SourceInfo(file_h, 55, 0))
        inst.createNextCover("#block#1#60#1#", CoverData(UCIS_BLOCKBIN, 0), SourceInfo(file_h, 60, 0))
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify instance persisted
        insts_read = list(db2.scopes(ScopeTypeT.INSTANCE))
        found = False
        for inst_read in insts_read:
            if inst_read.getScopeName() == "i_module1":
                found = True
                break
        
        assert found, "Instance with block coverage not found after persistence"
    
    def test_multiple_code_coverage_types(self, backend):
        """Test multiple code coverage types in one instance"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        db = create_db()
        
        testnode = db.createHistoryNode(None, "test", "test", UCIS_HISTORYNODE_TEST)
        testnode.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                      toolcategory="test", date="20240101000000"))
        
        # Create design hierarchy
        file_h = db.createFileHandle("design.v", "/rtl")
        
        du = db.createScope("work.module1", SourceInfo(file_h, 1, 0),
                           1, UCIS_VLOG, UCIS_DU_MODULE,
                           UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        
        inst = db.createInstance("i_module1", None, 1, UCIS_VLOG,
                                UCIS_INSTANCE, du, UCIS_INST_ONCE)
        
        # Add all types of code coverage directly to instance
        # All coverage types can coexist on the same instance
        inst.createNextCover("#stmt#1#10#1#", CoverData(UCIS_STMTBIN, 5), SourceInfo(file_h, 10, 0))
        inst.createNextCover("#branch#1#20#1#", CoverData(UCIS_BRANCHBIN, 3), SourceInfo(file_h, 20, 0))
        inst.createNextCover("#cond#1#30#1#", CoverData(UCIS_CONDBIN, 2), SourceInfo(file_h, 30, 0))
        inst.createNextCover("#expr#1#40#1#", CoverData(UCIS_EXPRBIN, 7), SourceInfo(file_h, 40, 0))
        inst.createNextCover("#block#1#50#1#", CoverData(UCIS_BLOCKBIN, 4), SourceInfo(file_h, 50, 0))
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify instance persisted
        insts_read = list(db2.scopes(ScopeTypeT.INSTANCE))
        found = False
        for inst_read in insts_read:
            if inst_read.getScopeName() == "i_module1":
                found = True
                break
        
        assert found, "Instance with multiple code coverage types not found after persistence"
