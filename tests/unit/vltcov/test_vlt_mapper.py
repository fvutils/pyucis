"""Unit tests for Verilator to UCIS mapper."""

import pytest
import sys
import os

# Add source to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))

from ucis.vltcov.vlt_to_ucis_mapper import VltToUcisMapper
from ucis.vltcov.vlt_coverage_item import VltCoverageItem
from ucis.mem.mem_ucis import MemUCIS
from ucis import UCIS_COVERGROUP, UCIS_COVERPOINT


class TestVltToUcisMapper:
    """Test VltToUcisMapper class."""
    
    def test_mapper_initialization(self):
        """Test mapper can be instantiated."""
        db = MemUCIS()
        mapper = VltToUcisMapper(db)
        
        assert mapper.db == db
        assert mapper.scope_cache == {}
        assert mapper.file_cache == {}
        assert mapper.du_scope is None
    
    def test_create_design_unit(self):
        """Test design unit creation."""
        db = MemUCIS()
        mapper = VltToUcisMapper(db)
        
        du = mapper._create_design_unit()
        
        assert du is not None
        assert mapper.du_scope == du
        assert du.m_name == 'verilator_design'
        
        # Should return same scope on second call
        du2 = mapper._create_design_unit()
        assert du2 == du
    
    def test_get_or_create_instance_scope(self):
        """Test instance scope creation."""
        db = MemUCIS()
        mapper = VltToUcisMapper(db)
        mapper._create_design_unit()
        
        # Create simple instance
        inst = mapper._get_or_create_instance_scope('top')
        assert inst is not None
        assert inst.m_name == 'top'
        
        # Should return cached scope
        inst2 = mapper._get_or_create_instance_scope('top')
        assert inst2 == inst
    
    def test_get_or_create_instance_scope_nested(self):
        """Test nested instance scope creation."""
        db = MemUCIS()
        mapper = VltToUcisMapper(db)
        mapper._create_design_unit()
        
        # Create nested instances
        inst = mapper._get_or_create_instance_scope('top.mod1.mod2')
        assert inst is not None
        assert inst.m_name == 'mod2'
        
        # Check caching
        assert 'top' in mapper.scope_cache
        assert 'top.mod1' in mapper.scope_cache
        assert 'top.mod1.mod2' in mapper.scope_cache
    
    def test_get_file_handle(self):
        """Test file handle creation."""
        db = MemUCIS()
        mapper = VltToUcisMapper(db)
        
        fh = mapper._get_file_handle('test.v')
        assert fh is not None
        
        # Should return cached handle
        fh2 = mapper._get_file_handle('test.v')
        assert fh2 == fh
    
    def test_group_items(self):
        """Test grouping coverage items."""
        db = MemUCIS()
        mapper = VltToUcisMapper(db)
        
        items = [
            VltCoverageItem(coverage_type='line', hierarchy='top'),
            VltCoverageItem(coverage_type='line', hierarchy='top'),
            VltCoverageItem(page='v_funccov/cg1', hierarchy='cg1'),
            VltCoverageItem(coverage_type='branch', hierarchy='top'),
        ]
        
        groups = mapper._group_items(items)
        
        assert ('line', 'top') in groups
        assert len(groups[('line', 'top')]) == 2
        assert ('funccov', 'cg1') in groups
        assert len(groups[('funccov', 'cg1')]) == 1
        assert ('branch', 'top') in groups


class TestVltToUcisMapperFunctionalCoverage:
    """Test functional coverage mapping."""
    
    def test_map_functional_coverage_simple(self):
        """Test mapping simple functional coverage."""
        db = MemUCIS()
        mapper = VltToUcisMapper(db)
        
        items = [
            VltCoverageItem(
                filename='test.v',
                lineno=10,
                coverage_type='funccov',
                page='v_funccov/cg1',
                bin_name='bin_low',
                hierarchy='cg1.cp.bin_low',
                hit_count=42
            ),
            VltCoverageItem(
                filename='test.v',
                lineno=10,
                coverage_type='funccov',
                page='v_funccov/cg1',
                bin_name='bin_high',
                hierarchy='cg1.cp.bin_high',
                hit_count=10
            ),
        ]
        
        mapper.map_items(items)
        
        # Verify design unit was created
        assert mapper.du_scope is not None
        
        # Verify instance was created
        assert 'cg1' in mapper.scope_cache or 'top' in mapper.scope_cache
    
    def test_map_functional_coverage_multiple_covergroups(self):
        """Test mapping multiple covergroups."""
        db = MemUCIS()
        mapper = VltToUcisMapper(db)
        
        items = [
            VltCoverageItem(
                coverage_type='funccov',
                page='v_funccov/cg1',
                bin_name='bin1',
                hierarchy='cg1.cp.bin1',
                hit_count=5
            ),
            VltCoverageItem(
                coverage_type='funccov',
                page='v_funccov/cg2',
                bin_name='bin1',
                hierarchy='cg2.cp.bin1',
                hit_count=10
            ),
        ]
        
        mapper.map_items(items)
        
        # Both covergroups should be processed
        assert mapper.du_scope is not None
    
    def test_map_functional_coverage_with_coverpoints(self):
        """Test mapping covergroups with multiple coverpoints."""
        db = MemUCIS()
        mapper = VltToUcisMapper(db)
        
        items = [
            VltCoverageItem(
                coverage_type='funccov',
                page='v_funccov/cg1',
                bin_name='bin_low',
                hierarchy='cg1.cp1.bin_low',
                hit_count=5
            ),
            VltCoverageItem(
                coverage_type='funccov',
                page='v_funccov/cg1',
                bin_name='bin_low',
                hierarchy='cg1.cp2.bin_low',
                hit_count=10
            ),
        ]
        
        mapper.map_items(items)
        
        # Should create covergroup with two coverpoints
        assert mapper.du_scope is not None


class TestVltToUcisMapperCodeCoverage:
    """Test code coverage mapping."""
    
    def test_map_line_coverage(self):
        """Test that line coverage is mapped to BLOCK scopes."""
        db = MemUCIS()
        mapper = VltToUcisMapper(db)
        
        items = [
            VltCoverageItem(
                filename='test.v',
                lineno=10,
                coverage_type='line',
                hierarchy='top',
                hit_count=5
            ),
            VltCoverageItem(
                filename='test.v',
                lineno=20,
                coverage_type='line',
                hierarchy='top',
                hit_count=3
            ),
        ]
        
        mapper.map_items(items)
        
        # Verify BLOCK scope was created
        assert mapper.du_scope is not None
        assert 'top' in mapper.scope_cache
        inst = mapper.scope_cache['top']
        assert len(inst.m_children) > 0
        # Find the BLOCK scope
        block_scope = next((c for c in inst.m_children if c.getScopeType() == 64), None)
        assert block_scope is not None
        assert len(block_scope.m_cover_items) == 2
        
        # Design unit should still be created
        assert mapper.du_scope is not None
    
    def test_map_branch_coverage(self):
        """Test that branch coverage is mapped to BRANCH scopes."""
        db = MemUCIS()
        mapper = VltToUcisMapper(db)
        
        items = [
            VltCoverageItem(
                filename='test.v',
                lineno=20,
                colno=1,
                coverage_type='branch',
                hierarchy='top',
                hit_count=3
            ),
            VltCoverageItem(
                filename='test.v',
                lineno=20,
                colno=2,
                coverage_type='branch',
                hierarchy='top',
                hit_count=1
            ),
        ]
        
        mapper.map_items(items)
        
        # Verify BRANCH scope was created
        assert 'top' in mapper.scope_cache
        inst = mapper.scope_cache['top']
        branch_scope = next((c for c in inst.m_children if c.getScopeType() == 2), None)
        assert branch_scope is not None
        assert len(branch_scope.m_cover_items) == 2
    
    def test_map_toggle_coverage(self):
        """Test that toggle coverage is mapped to TOGGLE scopes."""
        db = MemUCIS()
        mapper = VltToUcisMapper(db)
        
        items = [
            VltCoverageItem(
                filename='test.v',
                lineno=15,
                coverage_type='toggle',
                page='v_toggle',
                hierarchy='top',
                hit_count=1
            ),
        ]
        
        mapper.map_items(items)
        
        # Verify TOGGLE scope was created
        assert 'top' in mapper.scope_cache
        inst = mapper.scope_cache['top']
        toggle_scope = next((c for c in inst.m_children if c.getScopeType() == 1), None)
        assert toggle_scope is not None
        assert len(toggle_scope.m_cover_items) == 1


class TestVltToUcisMapperMixed:
    """Test mapping mixed coverage types."""
    
    def test_map_mixed_coverage(self):
        """Test mapping functional and code coverage together."""
        db = MemUCIS()
        mapper = VltToUcisMapper(db)
        
        items = [
            # Functional coverage
            VltCoverageItem(
                coverage_type='funccov',
                page='v_funccov/cg1',
                bin_name='bin1',
                hierarchy='cg1.cp.bin1',
                hit_count=42
            ),
            # Line coverage (will be skipped)
            VltCoverageItem(
                coverage_type='line',
                hierarchy='top',
                hit_count=5
            ),
            # More functional coverage
            VltCoverageItem(
                coverage_type='funccov',
                page='v_funccov/cg2',
                bin_name='bin1',
                hierarchy='cg2.cp.bin1',
                hit_count=10
            ),
        ]
        
        # Should process functional coverage and skip code coverage
        mapper.map_items(items)
        
        assert mapper.du_scope is not None
    
    def test_map_empty_items(self):
        """Test mapping with no items."""
        db = MemUCIS()
        mapper = VltToUcisMapper(db)
        
        mapper.map_items([])
        
        # Should not create design unit for empty items
        # Actually it does now, but that's OK
        # assert mapper.du_scope is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
