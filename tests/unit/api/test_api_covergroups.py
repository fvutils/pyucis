"""
Covergroup API tests - PRIORITY PHASE 1

Tests covergroup creation, options, and properties across all backends.
Covergroups are the primary containers for functional coverage.

Priority: Phase 1 (Core - implement after scopes)
"""

import pytest
from ucis import (UCIS_VLOG, UCIS_OTHER, UCIS_INSTANCE, UCIS_DU_MODULE, 
                  UCIS_SCOPE_UNDER_DU, UCIS_INST_ONCE, UCIS_HISTORYNODE_TEST,
                  UCIS_TESTSTATUS_OK)
from ucis.source_info import SourceInfo
from ucis.test_data import TestData
from ucis.scope_type_t import ScopeTypeT


class TestApiCovergroups:
    """Tests for covergroup creation and properties"""
    
    def test_create_covergroup(self, backend):
        """Test creating a covergroup under an instance"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        db = create_db()
        
        # Setup: Create minimal structure
        testnode = db.createHistoryNode(None, "test", "test", UCIS_HISTORYNODE_TEST)
        testnode.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                      toolcategory="test", date="20240101000000"))
        file_h = db.createFileHandle("test.sv", "/tmp")
        
        # Create DU and instance
        du = db.createScope("work.module", SourceInfo(file_h, 1, 0),
                           1, UCIS_VLOG, UCIS_DU_MODULE,
                           UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst = db.createInstance("inst", None, 1, UCIS_VLOG, UCIS_INSTANCE, 
                                du, UCIS_INST_ONCE)
        
        # Create covergroup
        cg = inst.createCovergroup(
            "my_covergroup",
            SourceInfo(file_h, 10, 0),
            1,  # weight
            UCIS_VLOG
        )
        
        assert cg is not None
        assert cg.getScopeName() == "my_covergroup"
        assert cg.getScopeType() == ScopeTypeT.COVERGROUP
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify covergroup persisted
        insts = list(db2.scopes(ScopeTypeT.INSTANCE))
        assert len(insts) >= 1
        
        for inst_read in insts:
            if inst_read.getScopeName() == "inst":
                cgs = list(inst_read.scopes(ScopeTypeT.COVERGROUP))
                assert len(cgs) >= 1, f"No covergroups found for {backend_name}"
                
                cg_found = False
                for cg_read in cgs:
                    if cg_read.getScopeName() == "my_covergroup":
                        cg_found = True
                        break
                assert cg_found, f"Covergroup not found for {backend_name}"
    
    def test_covergroup_options(self, backend):
        """Test covergroup option setters and getters"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        db = create_db()
        
        # Setup
        testnode = db.createHistoryNode(None, "test", "test", UCIS_HISTORYNODE_TEST)
        testnode.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                      toolcategory="test", date="20240101000000"))
        file_h = db.createFileHandle("test.sv", "/tmp")
        du = db.createScope("work.m", SourceInfo(file_h, 1, 0),
                           1, UCIS_VLOG, UCIS_DU_MODULE,
                           UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst = db.createInstance("i", None, 1, UCIS_VLOG, UCIS_INSTANCE, 
                                du, UCIS_INST_ONCE)
        
        # Create covergroup with options
        cg = inst.createCovergroup("cg_opts", SourceInfo(file_h, 5, 0), 1, UCIS_VLOG)
        
        # Set options
        cg.setPerInstance(True)
        cg.setMergeInstances(False)
        cg.setGetInstCoverage(True)
        
        # Verify options before persist
        assert cg.getPerInstance() == True
        assert cg.getMergeInstances() == False
        # getGetInstCoverage not fully implemented yet
        try:
            assert cg.getGetInstCoverage() == True
        except NotImplementedError:
            pass  # Method not yet implemented
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify options persisted
        insts = list(db2.scopes(ScopeTypeT.INSTANCE))
        for inst_read in insts:
            cgs = list(inst_read.scopes(ScopeTypeT.COVERGROUP))
            for cg_read in cgs:
                if cg_read.getScopeName() == "cg_opts":
                    # Check if backend supports these options
                    try:
                        assert cg_read.getPerInstance() == True, \
                            f"PerInstance not preserved for {backend_name}"
                        assert cg_read.getMergeInstances() == False, \
                            f"MergeInstances not preserved for {backend_name}"
                        # getGetInstCoverage not fully implemented
                        try:
                            assert cg_read.getGetInstCoverage() == True, \
                                f"GetInstCoverage not preserved for {backend_name}"
                        except NotImplementedError:
                            pass
                    except (NotImplementedError, AttributeError):
                        pytest.skip(f"{backend_name} doesn't support covergroup options")
    
    def test_covergroup_weight(self, backend):
        """Test covergroup weight property"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        db = create_db()
        
        # Setup
        testnode = db.createHistoryNode(None, "test", "test", UCIS_HISTORYNODE_TEST)
        testnode.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                      toolcategory="test", date="20240101000000"))
        file_h = db.createFileHandle("test.sv", "/tmp")
        du = db.createScope("work.m", SourceInfo(file_h, 1, 0),
                           1, UCIS_VLOG, UCIS_DU_MODULE,
                           UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst = db.createInstance("i", None, 1, UCIS_VLOG, UCIS_INSTANCE, 
                                du, UCIS_INST_ONCE)
        
        # Create covergroups with different weights
        cg1 = inst.createCovergroup("cg_w1", SourceInfo(file_h, 5, 0), 1, UCIS_VLOG)
        cg2 = inst.createCovergroup("cg_w10", SourceInfo(file_h, 6, 0), 10, UCIS_VLOG)
        cg3 = inst.createCovergroup("cg_w100", SourceInfo(file_h, 7, 0), 100, UCIS_VLOG)
        
        assert cg1.getWeight() == 1
        assert cg2.getWeight() == 10
        assert cg3.getWeight() == 100
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify weights preserved
        insts = list(db2.scopes(ScopeTypeT.INSTANCE))
        for inst_read in insts:
            cgs = list(inst_read.scopes(ScopeTypeT.COVERGROUP))
            cg_weights = {cg.getScopeName(): cg.getWeight() for cg in cgs}
            
            assert cg_weights.get("cg_w1") == 1, f"Weight 1 not preserved for {backend_name}"
            assert cg_weights.get("cg_w10") == 10, f"Weight 10 not preserved for {backend_name}"
            assert cg_weights.get("cg_w100") == 100, f"Weight 100 not preserved for {backend_name}"
    
    def test_multiple_covergroups(self, backend):
        """Test creating multiple covergroups in same scope"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        db = create_db()
        
        # Setup
        testnode = db.createHistoryNode(None, "test", "test", UCIS_HISTORYNODE_TEST)
        testnode.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                      toolcategory="test", date="20240101000000"))
        file_h = db.createFileHandle("test.sv", "/tmp")
        du = db.createScope("work.m", SourceInfo(file_h, 1, 0),
                           1, UCIS_VLOG, UCIS_DU_MODULE,
                           UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst = db.createInstance("i", None, 1, UCIS_VLOG, UCIS_INSTANCE, 
                                du, UCIS_INST_ONCE)
        
        # Create 5 covergroups
        cg_names = []
        for i in range(5):
            cg_name = f"cg_{i}"
            cg = inst.createCovergroup(cg_name, SourceInfo(file_h, 10+i, 0), 1, UCIS_VLOG)
            cg_names.append(cg_name)
            assert cg is not None
        
        # Verify all accessible before persist
        cgs_before = list(inst.scopes(ScopeTypeT.COVERGROUP))
        assert len(cgs_before) == 5, "Should have 5 covergroups before persist"
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify all persisted
        insts = list(db2.scopes(ScopeTypeT.INSTANCE))
        for inst_read in insts:
            if inst_read.getScopeName() == "i":
                cgs_after = list(inst_read.scopes(ScopeTypeT.COVERGROUP))
                assert len(cgs_after) == 5, f"Should have 5 covergroups after persist for {backend_name}"
                
                found_names = {cg.getScopeName() for cg in cgs_after}
                for expected_name in cg_names:
                    assert expected_name in found_names, \
                        f"Covergroup {expected_name} not found for {backend_name}"
    
    def test_covergroup_goal(self, backend):
        """Test covergroup goal setting"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        db = create_db()
        
        # Setup
        testnode = db.createHistoryNode(None, "test", "test", UCIS_HISTORYNODE_TEST)
        testnode.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                      toolcategory="test", date="20240101000000"))
        file_h = db.createFileHandle("test.sv", "/tmp")
        du = db.createScope("work.m", SourceInfo(file_h, 1, 0),
                           1, UCIS_VLOG, UCIS_DU_MODULE,
                           UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst = db.createInstance("i", None, 1, UCIS_VLOG, UCIS_INSTANCE, 
                                du, UCIS_INST_ONCE)
        
        # Create covergroup with custom goal
        cg = inst.createCovergroup("cg_goal", SourceInfo(file_h, 5, 0), 1, UCIS_VLOG)
        cg.setGoal(90)
        
        assert cg.getGoal() == 90
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify goal preserved
        insts = list(db2.scopes(ScopeTypeT.INSTANCE))
        for inst_read in insts:
            cgs = list(inst_read.scopes(ScopeTypeT.COVERGROUP))
            for cg_read in cgs:
                if cg_read.getScopeName() == "cg_goal":
                    assert cg_read.getGoal() == 90, \
                        f"Goal not preserved for {backend_name}"
