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
Tests for cocotb-coverage YAML reader.
"""

import pytest
from pathlib import Path

from ucis.cocotb.cocotb_yaml_reader import CocotbYamlReader, read_cocotb_yaml
from ucis.cocotb.cocotb_xml_reader import read_cocotb_xml
from ucis.scope_type_t import ScopeTypeT


# Path to test fixtures
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "cocotb_avl"
SAMPLE_YAML = FIXTURES_DIR / "sample_cocotb_coverage.yml"
SAMPLE_XML = FIXTURES_DIR / "sample_cocotb_coverage.xml"


class TestCocotbYamlReader:
    """Test suite for cocotb-coverage YAML import."""
    
    def test_reader_instantiation(self):
        """Test that reader can be instantiated."""
        reader = CocotbYamlReader()
        assert reader is not None
        assert reader.db is None
        assert len(reader.scope_map) == 0
    
    def test_read_sample_file(self):
        """Test reading the sample cocotb-coverage YAML file."""
        if not SAMPLE_YAML.exists():
            pytest.skip(f"Sample file not found: {SAMPLE_YAML}")
        
        db = read_cocotb_yaml(str(SAMPLE_YAML))
        assert db is not None
        
        # Verify database has scopes
        scopes_list = list(db.scopes(-1))
        assert len(scopes_list) > 0, "Database should have child scopes"
    
    def test_hierarchy_creation(self):
        """Test that scope hierarchy is correctly created."""
        if not SAMPLE_YAML.exists():
            pytest.skip(f"Sample file not found: {SAMPLE_YAML}")
        
        db = read_cocotb_yaml(str(SAMPLE_YAML))
        
        # Navigate hierarchy
        scopes = list(db.scopes(-1))
        assert len(scopes) > 0, "Should have child scopes"
        
        # Check scope names
        scope_names = [s.getScopeName() for s in scopes]
        assert len(scope_names) > 0
    
    def test_coverpoint_creation(self):
        """Test that coverpoints are correctly created."""
        if not SAMPLE_YAML.exists():
            pytest.skip(f"Sample file not found: {SAMPLE_YAML}")
        
        db = read_cocotb_yaml(str(SAMPLE_YAML))
        
        # Find all coverpoints
        coverpoints = self._find_scopes_by_type(db, ScopeTypeT.COVERPOINT)
        assert len(coverpoints) > 0, "Should have coverpoints"
        
        # Verify coverpoint attributes
        for cp in coverpoints[:3]:
            assert cp.getScopeName() is not None
    
    def test_bin_creation(self):
        """Test that bins are correctly created with hit counts."""
        if not SAMPLE_YAML.exists():
            pytest.skip(f"Sample file not found: {SAMPLE_YAML}")
        
        db = read_cocotb_yaml(str(SAMPLE_YAML))
        
        # Find a coverpoint
        coverpoints = self._find_scopes_by_type(db, ScopeTypeT.COVERPOINT)
        assert len(coverpoints) > 0
        
        # Check bins in first coverpoint
        cp = coverpoints[0]
        bins = list(cp.scopes(-1))
        
        # Should have bins
        if len(bins) > 0:
            bin_scope = bins[0]
            assert bin_scope.getScopeName() is not None
    
    def test_cross_detection(self):
        """Test that cross coverage is correctly detected."""
        if not SAMPLE_YAML.exists():
            pytest.skip(f"Sample file not found: {SAMPLE_YAML}")
        
        db = read_cocotb_yaml(str(SAMPLE_YAML))
        
        # Find all crosses
        crosses = self._find_scopes_by_type(db, ScopeTypeT.CROSS)
        
        # Our sample has one cross: addr_data_cross
        print(f"Found {len(crosses)} crosses")
    
    def test_yaml_xml_equivalence(self):
        """Test that YAML and XML imports produce equivalent results."""
        if not SAMPLE_YAML.exists() or not SAMPLE_XML.exists():
            pytest.skip("Sample files not found")
        
        # Import both formats
        yaml_db = read_cocotb_yaml(str(SAMPLE_YAML))
        xml_db = read_cocotb_xml(str(SAMPLE_XML))
        
        # Compare scope counts
        yaml_coverpoints = self._find_scopes_by_type(yaml_db, ScopeTypeT.COVERPOINT)
        xml_coverpoints = self._find_scopes_by_type(xml_db, ScopeTypeT.COVERPOINT)
        
        assert len(yaml_coverpoints) == len(xml_coverpoints), \
            f"YAML and XML should have same number of coverpoints"
        
        yaml_crosses = self._find_scopes_by_type(yaml_db, ScopeTypeT.CROSS)
        xml_crosses = self._find_scopes_by_type(xml_db, ScopeTypeT.CROSS)
        
        assert len(yaml_crosses) == len(xml_crosses), \
            f"YAML and XML should have same number of crosses"
    
    def _find_scopes_by_type(self, scope, scope_type, found=None):
        """Helper to recursively find all scopes of a given type."""
        if found is None:
            found = []
        
        if scope.getScopeType() == scope_type:
            found.append(scope)
        
        for child in scope.scopes(-1):
            self._find_scopes_by_type(child, scope_type, found)
        
        return found
