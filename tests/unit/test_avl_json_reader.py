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
Tests for AVL JSON reader.
"""

import pytest
from pathlib import Path

from ucis.avl.avl_json_reader import AvlJsonReader, read_avl_json
from ucis.scope_type_t import ScopeTypeT


# Path to test fixtures
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "cocotb_avl"
SAMPLE_HIERARCHICAL = FIXTURES_DIR / "sample_avl_coverage.json"
SAMPLE_DF_RECORDS = FIXTURES_DIR / "sample_avl_coverage_df.json"
SAMPLE_DF_TABLE = FIXTURES_DIR / "sample_avl_coverage_table.json"


class TestAvlJsonReader:
    """Test suite for AVL JSON import."""
    
    def test_reader_instantiation(self):
        """Test that reader can be instantiated."""
        reader = AvlJsonReader()
        assert reader is not None
        assert reader.db is None
        assert len(reader.scope_map) == 0
    
    def test_read_hierarchical_format(self):
        """Test reading hierarchical AVL JSON format."""
        if not SAMPLE_HIERARCHICAL.exists():
            pytest.skip(f"Sample file not found: {SAMPLE_HIERARCHICAL}")
        
        db = read_avl_json(str(SAMPLE_HIERARCHICAL))
        assert db is not None
        
        # Verify database has scopes
        scopes_list = list(db.scopes(-1))
        assert len(scopes_list) > 0, "Database should have child scopes"
    
    def test_covergroup_creation(self):
        """Test that covergroups are correctly created."""
        if not SAMPLE_HIERARCHICAL.exists():
            pytest.skip(f"Sample file not found: {SAMPLE_HIERARCHICAL}")
        
        db = read_avl_json(str(SAMPLE_HIERARCHICAL))
        
        # Find all covergroups
        covergroups = self._find_scopes_by_type(db, ScopeTypeT.COVERGROUP)
        assert len(covergroups) > 0, "Should have covergroups"
        
        # Check names
        cg_names = [cg.getScopeName() for cg in covergroups]
        # Our sample has: address_coverage, transaction_coverage
        assert any('address' in name or 'transaction' in name for name in cg_names)
    
    def test_coverpoint_creation(self):
        """Test that coverpoints are correctly created."""
        if not SAMPLE_HIERARCHICAL.exists():
            pytest.skip(f"Sample file not found: {SAMPLE_HIERARCHICAL}")
        
        db = read_avl_json(str(SAMPLE_HIERARCHICAL))
        
        # Find all coverpoints
        coverpoints = self._find_scopes_by_type(db, ScopeTypeT.COVERPOINT)
        assert len(coverpoints) > 0, "Should have coverpoints"
        
        # Our sample should have: addr_range, addr_parity, trans_type, burst_length
        assert len(coverpoints) >= 2
    
    def test_bin_creation(self):
        """Test that bins are correctly created with hit counts."""
        if not SAMPLE_HIERARCHICAL.exists():
            pytest.skip(f"Sample file not found: {SAMPLE_HIERARCHICAL}")
        
        db = read_avl_json(str(SAMPLE_HIERARCHICAL))
        
        # Find a coverpoint
        coverpoints = self._find_scopes_by_type(db, ScopeTypeT.COVERPOINT)
        assert len(coverpoints) > 0
        
        # Check bins in first coverpoint
        cp = coverpoints[0]
        bins = list(cp.coverItems(-1))  # Use coverItems() instead of scopes()
        
        # Should have bins
        assert len(bins) > 0, "Coverpoint should have bins"
        
        # Verify bin has hit count
        first_bin = bins[0]
        assert first_bin.getName() is not None
        assert first_bin.getCoverData().data >= 0  # Count can be 0 or more
    
    def test_cross_creation(self):
        """Test that cross coverage is correctly created."""
        if not SAMPLE_HIERARCHICAL.exists():
            pytest.skip(f"Sample file not found: {SAMPLE_HIERARCHICAL}")
        
        db = read_avl_json(str(SAMPLE_HIERARCHICAL))
        
        # Find all crosses
        crosses = self._find_scopes_by_type(db, ScopeTypeT.CROSS)
        
        # Our sample has type_x_length cross
        print(f"Found {len(crosses)} crosses")
        # At least one cross should be found
        assert len(crosses) >= 1, "Should have at least one cross"
    
    def test_dataframe_records_format(self):
        """Test reading DataFrame records format."""
        if not SAMPLE_DF_RECORDS.exists():
            pytest.skip(f"Sample file not found: {SAMPLE_DF_RECORDS}")
        
        db = read_avl_json(str(SAMPLE_DF_RECORDS))
        assert db is not None
        
        # Should have created coverpoints
        coverpoints = self._find_scopes_by_type(db, ScopeTypeT.COVERPOINT)
        assert len(coverpoints) > 0, "Should have coverpoints from DataFrame"
    
    def test_dataframe_table_format(self):
        """Test reading DataFrame table format."""
        if not SAMPLE_DF_TABLE.exists():
            pytest.skip(f"Sample file not found: {SAMPLE_DF_TABLE}")
        
        db = read_avl_json(str(SAMPLE_DF_TABLE))
        assert db is not None
        
        # Should have created coverpoints
        coverpoints = self._find_scopes_by_type(db, ScopeTypeT.COVERPOINT)
        assert len(coverpoints) > 0, "Should have coverpoints from DataFrame"
    
    def _find_scopes_by_type(self, scope, scope_type, found=None):
        """Helper to recursively find all scopes of a given type."""
        if found is None:
            found = []
        
        if scope.getScopeType() == scope_type:
            found.append(scope)
        
        for child in scope.scopes(-1):
            self._find_scopes_by_type(child, scope_type, found)
        
        return found
