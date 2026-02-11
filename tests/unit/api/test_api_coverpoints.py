"""
Coverpoint and Bin API tests - PRIORITY PHASE 1

Tests coverpoint creation, bins, and coverage data across all backends.
Coverpoints are the core of functional coverage measurement.

Priority: Phase 1 (Core - implement after covergroups)
"""

import pytest
from ucis import (UCIS_VLOG, UCIS_OTHER, UCIS_INSTANCE, UCIS_DU_MODULE, 
                  UCIS_SCOPE_UNDER_DU, UCIS_INST_ONCE, UCIS_HISTORYNODE_TEST,
                  UCIS_TESTSTATUS_OK, UCIS_CVGBIN, UCIS_IGNOREBIN, UCIS_ILLEGALBIN)
from ucis.source_info import SourceInfo
from ucis.test_data import TestData
from ucis.scope_type_t import ScopeTypeT
from ucis.cover_type_t import CoverTypeT


class TestApiCoverpoints:
    """Tests for coverpoint and bin operations"""
    
    def test_create_coverpoint(self, backend):
        """Test creating a coverpoint under a covergroup"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        # XML requires coverpoints to have bins
        if backend_name == "xml":
            pytest.skip("XML schema requires coverpoints to have bins")
        
        db = create_db()
        
        # Setup
        testnode = db.createHistoryNode(None, "test", "test", UCIS_HISTORYNODE_TEST)
        testnode.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                      toolcategory="test", date="20240101000000"))
        file_h = db.createFileHandle("test.sv", "/tmp")
        
        # Create structure: DU -> instance -> covergroup -> coverpoint
        du = db.createScope("work.m", SourceInfo(file_h, 1, 0),
                           1, UCIS_VLOG, UCIS_DU_MODULE,
                           UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst = db.createInstance("i", None, 1, UCIS_VLOG, UCIS_INSTANCE, 
                                du, UCIS_INST_ONCE)
        cg = inst.createCovergroup("cg", SourceInfo(file_h, 5, 0), 1, UCIS_VLOG)
        
        # Create coverpoint
        cp = cg.createCoverpoint(
            "my_coverpoint",
            SourceInfo(file_h, 10, 0),
            1,  # weight
            UCIS_VLOG
        )
        
        assert cp is not None
        assert cp.getScopeName() == "my_coverpoint"
        assert cp.getScopeType() == ScopeTypeT.COVERPOINT
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify coverpoint persisted
        insts = list(db2.scopes(ScopeTypeT.INSTANCE))
        for inst_read in insts:
            cgs = list(inst_read.scopes(ScopeTypeT.COVERGROUP))
            for cg_read in cgs:
                if cg_read.getScopeName() == "cg":
                    cps = list(cg_read.scopes(ScopeTypeT.COVERPOINT))
                    assert len(cps) >= 1, f"No coverpoints found for {backend_name}"
                    
                    cp_found = False
                    for cp_read in cps:
                        if cp_read.getScopeName() == "my_coverpoint":
                            cp_found = True
                            break
                    assert cp_found, f"Coverpoint not found for {backend_name}"
    
    def test_create_bins(self, backend):
        """Test creating bins with different types"""
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
        cg = inst.createCovergroup("cg", SourceInfo(file_h, 5, 0), 1, UCIS_VLOG)
        cp = cg.createCoverpoint("cp", SourceInfo(file_h, 10, 0), 1, UCIS_VLOG)
        
        # Create different bin types
        bin1 = cp.createBin(
            "normal_bin",
            SourceInfo(file_h, 11, 0),
            1,   # at_least
            10,  # count
            "0",
            UCIS_CVGBIN
        )
        
        bin2 = cp.createBin(
            "ignore_bin",
            SourceInfo(file_h, 12, 0),
            1,
            0,
            "1",
            UCIS_IGNOREBIN
        )
        
        bin3 = cp.createBin(
            "illegal_bin",
            SourceInfo(file_h, 13, 0),
            1,
            0,
            "2",
            UCIS_ILLEGALBIN
        )
        
        # Verify bins before persist
        bins = list(cp.coverItems(CoverTypeT.CVGBIN | CoverTypeT.IGNOREBIN | CoverTypeT.ILLEGALBIN))
        assert len(bins) == 3, "Should have 3 bins before persist"
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify bins persisted with correct types
        insts = list(db2.scopes(ScopeTypeT.INSTANCE))
        for inst_read in insts:
            cgs = list(inst_read.scopes(ScopeTypeT.COVERGROUP))
            for cg_read in cgs:
                cps = list(cg_read.scopes(ScopeTypeT.COVERPOINT))
                for cp_read in cps:
                    if cp_read.getScopeName() == "cp":
                        bins_read = list(cp_read.coverItems(
                            CoverTypeT.CVGBIN | CoverTypeT.IGNOREBIN | CoverTypeT.ILLEGALBIN))
                        assert len(bins_read) == 3, f"Should have 3 bins after persist for {backend_name}"
                        
                        # Check bin types
                        bin_types = {}
                        for b in bins_read:
                            bin_types[b.getName()] = b.getCoverData().type
                        
                        assert bin_types.get("normal_bin") == CoverTypeT.CVGBIN, \
                            f"Normal bin type wrong for {backend_name}"
                        assert bin_types.get("ignore_bin") == CoverTypeT.IGNOREBIN, \
                            f"Ignore bin type wrong for {backend_name}"
                        assert bin_types.get("illegal_bin") == CoverTypeT.ILLEGALBIN, \
                            f"Illegal bin type wrong for {backend_name}"
    
    def test_bin_counts(self, backend):
        """Test that bin hit counts are preserved"""
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
        cg = inst.createCovergroup("cg", SourceInfo(file_h, 5, 0), 1, UCIS_VLOG)
        cp = cg.createCoverpoint("cp", SourceInfo(file_h, 10, 0), 1, UCIS_VLOG)
        
        # Create bins with different counts
        test_counts = {
            "bin_0": 0,
            "bin_1": 1,
            "bin_100": 100,
            "bin_1000": 1000,
        }
        
        for bin_name, count in test_counts.items():
            cp.createBin(bin_name, SourceInfo(file_h, 11, 0), 1, count, "x", UCIS_CVGBIN)
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify counts preserved
        insts = list(db2.scopes(ScopeTypeT.INSTANCE))
        for inst_read in insts:
            cgs = list(inst_read.scopes(ScopeTypeT.COVERGROUP))
            for cg_read in cgs:
                cps = list(cg_read.scopes(ScopeTypeT.COVERPOINT))
                for cp_read in cps:
                    if cp_read.getScopeName() == "cp":
                        bins = list(cp_read.coverItems(CoverTypeT.CVGBIN))
                        bin_counts = {b.getName(): b.getCoverData().data for b in bins}
                        
                        for bin_name, expected_count in test_counts.items():
                            actual_count = bin_counts.get(bin_name)
                            assert actual_count == expected_count, \
                                f"Count mismatch for {bin_name}: expected {expected_count}, got {actual_count} for {backend_name}"
    
    def test_coverpoint_atleast(self, backend):
        """Test coverpoint at_least threshold"""
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
        cg = inst.createCovergroup("cg", SourceInfo(file_h, 5, 0), 1, UCIS_VLOG)
        cp = cg.createCoverpoint("cp", SourceInfo(file_h, 10, 0), 1, UCIS_VLOG)
        
        # Set at_least threshold
        cp.setAtLeast(10)
        assert cp.getAtLeast() == 10
        
        # Create bins with counts below and above threshold
        cp.createBin("below", SourceInfo(file_h, 11, 0), 10, 5, "0", UCIS_CVGBIN)
        cp.createBin("at", SourceInfo(file_h, 12, 0), 10, 10, "1", UCIS_CVGBIN)
        cp.createBin("above", SourceInfo(file_h, 13, 0), 10, 20, "2", UCIS_CVGBIN)
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify at_least preserved
        insts = list(db2.scopes(ScopeTypeT.INSTANCE))
        for inst_read in insts:
            cgs = list(inst_read.scopes(ScopeTypeT.COVERGROUP))
            for cg_read in cgs:
                cps = list(cg_read.scopes(ScopeTypeT.COVERPOINT))
                for cp_read in cps:
                    if cp_read.getScopeName() == "cp":
                        # Check if backend supports at_least
                        try:
                            assert cp_read.getAtLeast() == 10, \
                                f"AtLeast not preserved for {backend_name}"
                        except (NotImplementedError, AttributeError):
                            pytest.skip(f"{backend_name} doesn't support getAtLeast")
    
    def test_bin_names(self, backend):
        """Test that bin names are preserved"""
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
        cg = inst.createCovergroup("cg", SourceInfo(file_h, 5, 0), 1, UCIS_VLOG)
        cp = cg.createCoverpoint("cp", SourceInfo(file_h, 10, 0), 1, UCIS_VLOG)
        
        # Create bins with special names
        special_names = [
            "auto[0]",
            "auto[1]",
            "illegal_values",
            "default_bin",
        ]
        
        for name in special_names:
            cp.createBin(name, SourceInfo(file_h, 11, 0), 1, 5, "x", UCIS_CVGBIN)
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify names preserved
        insts = list(db2.scopes(ScopeTypeT.INSTANCE))
        for inst_read in insts:
            cgs = list(inst_read.scopes(ScopeTypeT.COVERGROUP))
            for cg_read in cgs:
                cps = list(cg_read.scopes(ScopeTypeT.COVERPOINT))
                for cp_read in cps:
                    if cp_read.getScopeName() == "cp":
                        bins = list(cp_read.coverItems(CoverTypeT.CVGBIN))
                        found_names = {b.getName() for b in bins}
                        
                        for expected_name in special_names:
                            assert expected_name in found_names, \
                                f"Bin name '{expected_name}' not found for {backend_name}"
    
    def test_multiple_coverpoints(self, backend):
        """Test creating multiple coverpoints in same covergroup"""
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
        cg = inst.createCovergroup("cg", SourceInfo(file_h, 5, 0), 1, UCIS_VLOG)
        
        # Create multiple coverpoints
        cp_names = []
        for i in range(3):
            cp_name = f"cp_{i}"
            cp = cg.createCoverpoint(cp_name, SourceInfo(file_h, 10+i, 0), 1, UCIS_VLOG)
            # Add at least one bin to each coverpoint
            cp.createBin(f"bin_{i}", SourceInfo(file_h, 20+i, 0), 1, 5, "x", UCIS_CVGBIN)
            cp_names.append(cp_name)
        
        # Verify all accessible before persist
        cps_before = list(cg.scopes(ScopeTypeT.COVERPOINT))
        assert len(cps_before) == 3, "Should have 3 coverpoints before persist"
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify all persisted
        insts = list(db2.scopes(ScopeTypeT.INSTANCE))
        for inst_read in insts:
            cgs = list(inst_read.scopes(ScopeTypeT.COVERGROUP))
            for cg_read in cgs:
                if cg_read.getScopeName() == "cg":
                    cps_after = list(cg_read.scopes(ScopeTypeT.COVERPOINT))
                    assert len(cps_after) == 3, f"Should have 3 coverpoints after persist for {backend_name}"
                    
                    found_names = {cp.getScopeName() for cp in cps_after}
                    for expected_name in cp_names:
                        assert expected_name in found_names, \
                            f"Coverpoint {expected_name} not found for {backend_name}"
    
    def test_coverpoint_weight(self, backend):
        """Test coverpoint weight property"""
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
        cg = inst.createCovergroup("cg", SourceInfo(file_h, 5, 0), 1, UCIS_VLOG)
        
        # Create coverpoints with different weights
        cp1 = cg.createCoverpoint("cp_w1", SourceInfo(file_h, 10, 0), 1, UCIS_VLOG)
        cp1.createBin("b1", SourceInfo(file_h, 11, 0), 1, 5, "x", UCIS_CVGBIN)
        
        cp2 = cg.createCoverpoint("cp_w10", SourceInfo(file_h, 12, 0), 10, UCIS_VLOG)
        cp2.createBin("b2", SourceInfo(file_h, 13, 0), 1, 5, "x", UCIS_CVGBIN)
        
        cp3 = cg.createCoverpoint("cp_w100", SourceInfo(file_h, 14, 0), 100, UCIS_VLOG)
        cp3.createBin("b3", SourceInfo(file_h, 15, 0), 1, 5, "x", UCIS_CVGBIN)
        
        assert cp1.getWeight() == 1
        assert cp2.getWeight() == 10
        assert cp3.getWeight() == 100
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify weights preserved
        insts = list(db2.scopes(ScopeTypeT.INSTANCE))
        for inst_read in insts:
            cgs = list(inst_read.scopes(ScopeTypeT.COVERGROUP))
            for cg_read in cgs:
                cps = list(cg_read.scopes(ScopeTypeT.COVERPOINT))
                cp_weights = {cp.getScopeName(): cp.getWeight() for cp in cps}
                
                assert cp_weights.get("cp_w1") == 1, f"Weight 1 not preserved for {backend_name}"
                assert cp_weights.get("cp_w10") == 10, f"Weight 10 not preserved for {backend_name}"
                assert cp_weights.get("cp_w100") == 100, f"Weight 100 not preserved for {backend_name}"
