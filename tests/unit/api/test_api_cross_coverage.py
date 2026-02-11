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
Test cross coverage functionality across all backends.

Tests cover:
- Creating cross coverage items
- Cross coverage with multiple coverpoints
- Cross bins and counts
- Cross coverage persistence
"""

import pytest
from ucis import *
from ucis.source_info import SourceInfo
from ucis.test_data import TestData
from ucis.cover_data import CoverData


class TestApiCrossCoverage:
    """Test cross coverage operations"""
    
    def test_create_cross(self, backend):
        """Test basic cross coverage creation"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        db = create_db()
        
        # Setup: Create test structure
        testnode = db.createHistoryNode(None, "test", "test", UCIS_HISTORYNODE_TEST)
        testnode.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                      toolcategory="test", date="20240101000000"))
        file_h = db.createFileHandle("test.sv", "/tmp")
        du = db.createScope("work.m", SourceInfo(file_h, 1, 0),
                           1, UCIS_VLOG, UCIS_DU_MODULE,
                           UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst = db.createInstance("inst", None, 1, UCIS_VLOG, UCIS_INSTANCE, 
                                du, UCIS_INST_ONCE)
        
        # Create covergroup with coverpoints
        cg = inst.createCovergroup("cg_cross", SourceInfo(file_h, 5, 0), 1, UCIS_VLOG)
        
        # Create two coverpoints that will be crossed
        cp1 = cg.createCoverpoint("cp1", SourceInfo(file_h, 6, 0), 1, UCIS_VLOG)
        # XML requires bins in coverpoints
        if backend_name == "xml":
            cp1.createBin("cp1_bin", SourceInfo(file_h, 6, 0), 1, 0, "val1", UCIS_CVGBIN)
        
        cp2 = cg.createCoverpoint("cp2", SourceInfo(file_h, 7, 0), 1, UCIS_VLOG)
        # XML requires bins in coverpoints
        if backend_name == "xml":
            cp2.createBin("cp2_bin", SourceInfo(file_h, 7, 0), 1, 0, "val2", UCIS_CVGBIN)
        
        # Create cross coverage
        cross = cg.createCross("cross_cp1_cp2", SourceInfo(file_h, 8, 0), 
                              1, UCIS_VLOG, [cp1, cp2])
        
        # Verify cross was created
        assert cross is not None
        assert cross.getScopeName() == "cross_cp1_cp2"
        assert cross.getScopeType() == ScopeTypeT.CROSS  # Cross is its own scope type
        
        # Verify cross references the coverpoints
        num_crossed = cross.getNumCrossedCoverpoints()
        assert num_crossed == 2
        
        crossed_cp1 = cross.getIthCrossedCoverpoint(0)
        crossed_cp2 = cross.getIthCrossedCoverpoint(1)
        assert crossed_cp1.getScopeName() == "cp1"
        assert crossed_cp2.getScopeName() == "cp2"
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify cross persisted
        insts = list(db2.scopes(ScopeTypeT.INSTANCE))
        assert len(insts) >= 1
        
        for inst_read in insts:
            if inst_read.getScopeName() == "inst":
                cgs = list(inst_read.scopes(ScopeTypeT.COVERGROUP))
                assert len(cgs) >= 1
                
                for cg_read in cgs:
                    if cg_read.getScopeName() == "cg_cross":
                        # Find the cross using CROSS scope type
                        crosses = list(cg_read.scopes(ScopeTypeT.CROSS))
                        assert len(crosses) == 1, f"Cross not found for {backend_name}"
                        
                        cross_read = crosses[0]
                        assert cross_read.getScopeName() == "cross_cp1_cp2"
                        num_crossed = cross_read.getNumCrossedCoverpoints()
                        assert num_crossed == 2, \
                            f"Cross should reference 2 coverpoints for {backend_name}"
    
    def test_cross_with_bins(self, backend):
        """Test cross coverage with bins"""
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
        
        # Create covergroup with coverpoints and bins
        cg = inst.createCovergroup("cg", SourceInfo(file_h, 5, 0), 1, UCIS_VLOG)
        
        cp1 = cg.createCoverpoint("cp1", SourceInfo(file_h, 6, 0), 1, UCIS_VLOG)
        bin1_1 = cp1.createBin("low", SourceInfo(file_h, 7, 0), 1, 0, "low", CoverTypeT.CVGBIN)
        bin1_2 = cp1.createBin("high", SourceInfo(file_h, 8, 0), 1, 0, "high", CoverTypeT.CVGBIN)
        
        cp2 = cg.createCoverpoint("cp2", SourceInfo(file_h, 9, 0), 1, UCIS_VLOG)
        bin2_1 = cp2.createBin("x", SourceInfo(file_h, 10, 0), 1, 0, "x", CoverTypeT.CVGBIN)
        bin2_2 = cp2.createBin("y", SourceInfo(file_h, 11, 0), 1, 0, "y", CoverTypeT.CVGBIN)
        
        # Create cross
        cross = cg.createCross("cross_ab", SourceInfo(file_h, 12, 0), 
                              1, UCIS_VLOG, [cp1, cp2])
        
        # Create cross bins (combinations of cp1 and cp2 bins)
        # Cross bin represents: low x x, low x y, high x x, high x y
        cross_bin1 = cross.createBin("low_x", SourceInfo(file_h, 13, 0), 1, 5, "low_x", CoverTypeT.CVGBIN)
        cross_bin2 = cross.createBin("low_y", SourceInfo(file_h, 14, 0), 1, 3, "low_y", CoverTypeT.CVGBIN)
        cross_bin3 = cross.createBin("high_x", SourceInfo(file_h, 15, 0), 1, 7, "high_x", CoverTypeT.CVGBIN)
        cross_bin4 = cross.createBin("high_y", SourceInfo(file_h, 16, 0), 1, 2, "high_y", CoverTypeT.CVGBIN)
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify cross bins persisted
        insts = list(db2.scopes(ScopeTypeT.INSTANCE))
        for inst_read in insts:
            cgs = list(inst_read.scopes(ScopeTypeT.COVERGROUP))
            for cg_read in cgs:
                crosses = list(cg_read.scopes(ScopeTypeT.CROSS))
                for cross_read in crosses:
                    if cross_read.getScopeName() == "cross_ab":
                        # Check cross bins - need to pass mask to coverItems
                        cross_bins = list(cross_read.coverItems(CoverTypeT.CVGBIN))
                        assert len(cross_bins) == 4, \
                            f"Cross should have 4 bins for {backend_name}"
                        
                        # Verify bin counts
                        bin_counts = {b.getName(): b.getCoverData().data 
                                     for b in cross_bins}
                        assert bin_counts.get("low_x") == 5
                        assert bin_counts.get("low_y") == 3
                        assert bin_counts.get("high_x") == 7
                        assert bin_counts.get("high_y") == 2
    
    def test_cross_three_coverpoints(self, backend):
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        """Test cross coverage with three coverpoints"""
        
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
        
        # Create covergroup with three coverpoints
        cg = inst.createCovergroup("cg_3way", SourceInfo(file_h, 5, 0), 1, UCIS_VLOG)
        
        cp1 = cg.createCoverpoint("addr", SourceInfo(file_h, 6, 0), 1, UCIS_VLOG)
        # XML requires bins in coverpoints
        if backend_name == "xml":
            cp1.createBin("addr_bin", SourceInfo(file_h, 6, 0), 1, 0, "val1", UCIS_CVGBIN)
        
        cp2 = cg.createCoverpoint("data", SourceInfo(file_h, 7, 0), 1, UCIS_VLOG)
        if backend_name == "xml":
            cp2.createBin("data_bin", SourceInfo(file_h, 7, 0), 1, 0, "val2", UCIS_CVGBIN)
        
        cp3 = cg.createCoverpoint("ctrl", SourceInfo(file_h, 8, 0), 1, UCIS_VLOG)
        if backend_name == "xml":
            cp3.createBin("ctrl_bin", SourceInfo(file_h, 8, 0), 1, 0, "val3", UCIS_CVGBIN)
        
        # Create 3-way cross
        cross = cg.createCross("addr_data_ctrl", SourceInfo(file_h, 9, 0), 
                              1, UCIS_VLOG, [cp1, cp2, cp3])
        
        assert cross is not None
        assert cross.getNumCrossedCoverpoints() == 3
        
        # Verify all three coverpoints are referenced
        crossed_names = []
        for i in range(3):
            cp = cross.getIthCrossedCoverpoint(i)
            crossed_names.append(cp.getScopeName())
        
        assert "addr" in crossed_names
        assert "data" in crossed_names
        assert "ctrl" in crossed_names
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify 3-way cross persisted
        insts = list(db2.scopes(ScopeTypeT.INSTANCE))
        for inst_read in insts:
            cgs = list(inst_read.scopes(ScopeTypeT.COVERGROUP))
            for cg_read in cgs:
                if cg_read.getScopeName() == "cg_3way":
                    crosses = list(cg_read.scopes(ScopeTypeT.CROSS))
                    assert len(crosses) == 1
                    
                    cross_read = crosses[0]
                    assert cross_read.getScopeName() == "addr_data_ctrl"
                    assert cross_read.getNumCrossedCoverpoints() == 3, \
                        f"3-way cross should reference 3 coverpoints for {backend_name}"
    
    def test_multiple_crosses(self, backend):
        """Test multiple cross coverage items in same covergroup"""
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
        
        # Create covergroup with multiple coverpoints
        cg = inst.createCovergroup("cg_multi", SourceInfo(file_h, 5, 0), 1, UCIS_VLOG)
        
        cp_a = cg.createCoverpoint("a", SourceInfo(file_h, 6, 0), 1, UCIS_VLOG)
        # XML requires bins in coverpoints
        if backend_name != "xml":
            # For non-XML backends, we can have coverpoints without bins
            pass
        else:
            # For XML, add minimal bins to satisfy schema
            cp_a.createBin("a_bin", SourceInfo(file_h, 6, 0), 1, 0, "a_val", CoverTypeT.CVGBIN)
        
        cp_b = cg.createCoverpoint("b", SourceInfo(file_h, 7, 0), 1, UCIS_VLOG)
        if backend_name == "xml":
            cp_b.createBin("b_bin", SourceInfo(file_h, 7, 0), 1, 0, "b_val", CoverTypeT.CVGBIN)
        
        cp_c = cg.createCoverpoint("c", SourceInfo(file_h, 8, 0), 1, UCIS_VLOG)
        if backend_name == "xml":
            cp_c.createBin("c_bin", SourceInfo(file_h, 8, 0), 1, 0, "c_val", CoverTypeT.CVGBIN)
        
        # Create multiple different crosses
        cross_ab = cg.createCross("cross_ab", SourceInfo(file_h, 9, 0), 
                                 1, UCIS_VLOG, [cp_a, cp_b])
        cross_bc = cg.createCross("cross_bc", SourceInfo(file_h, 10, 0), 
                                 1, UCIS_VLOG, [cp_b, cp_c])
        cross_ac = cg.createCross("cross_ac", SourceInfo(file_h, 11, 0), 
                                 1, UCIS_VLOG, [cp_a, cp_c])
        
        # Verify all crosses created
        assert cross_ab is not None
        assert cross_bc is not None
        assert cross_ac is not None
        
        # Persist and read back
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify all crosses persisted
        insts = list(db2.scopes(ScopeTypeT.INSTANCE))
        for inst_read in insts:
            cgs = list(inst_read.scopes(ScopeTypeT.COVERGROUP))
            for cg_read in cgs:
                if cg_read.getScopeName() == "cg_multi":
                    # Get regular coverpoints and crosses separately
                    coverpoints = list(cg_read.scopes(ScopeTypeT.COVERPOINT))
                    crosses = list(cg_read.scopes(ScopeTypeT.CROSS))
                    
                    # Should have 3 regular coverpoints
                    assert len(coverpoints) == 3, \
                        f"Should have 3 coverpoints for {backend_name}"
                    
                    # Should have 3 crosses
                    assert len(crosses) == 3, \
                        f"Should have 3 crosses for {backend_name}"
                    
                    # Verify cross names
                    cross_names = {c.getScopeName() for c in crosses}
                    assert "cross_ab" in cross_names
                    assert "cross_bc" in cross_names
                    assert "cross_ac" in cross_names
