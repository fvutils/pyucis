"""
Scope hierarchy tests - PRIORITY PHASE 1

Tests scope creation, nesting, and navigation across all backends.
This is the foundational functionality that covergroups build upon.

Priority: Phase 1 (Core - implement first)
"""

import pytest
from ucis import (UCIS_VLOG, UCIS_INSTANCE, UCIS_DU_MODULE, UCIS_SCOPE_UNDER_DU,
                  UCIS_INST_ONCE, UCIS_ENABLED_STMT, UCIS_HISTORYNODE_TEST,
                  UCIS_TESTSTATUS_OK)
from ucis.source_info import SourceInfo
from ucis.test_data import TestData
from ucis.scope_type_t import ScopeTypeT


class TestApiScopeHierarchy:
    """Tests for scope creation and hierarchy navigation"""
    
    def test_create_design_unit(self, backend):
        """Test creating a design unit scope"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        db = create_db()
        
        # Create minimal required structures
        testnode = db.createHistoryNode(None, "test", "test", UCIS_HISTORYNODE_TEST)
        testnode.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                      toolcategory="test", date="20240101000000"))
        
        file_h = db.createFileHandle("module.sv", "/tmp")
        
        # Create design unit
        du = db.createScope(
            "work.my_module",
            SourceInfo(file_h, 1, 0),
            1,  # weight
            UCIS_VLOG,
            UCIS_DU_MODULE,
            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE | UCIS_ENABLED_STMT
        )
        
        assert du is not None
        assert du.getScopeName() == "work.my_module"
        assert du.getScopeType() == UCIS_DU_MODULE
        assert du.getWeight() == 1
        
        # Create an instance (required for XML validity)
        inst = db.createInstance("du_inst", None, 1, UCIS_VLOG, UCIS_INSTANCE, du, UCIS_INST_ONCE)
        
        # Persist and read
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify DU exists
        dus = list(db2.scopes(ScopeTypeT.DU_MODULE))
        assert len(dus) >= 1, f"No design units found for {backend_name}"
        
        found = any(s.getScopeName() == "work.my_module" for s in dus)
        assert found, f"Could not find design unit for {backend_name}"
    
    def test_create_instance_with_du_reference(self, backend):
        """Test creating instance that references a design unit"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        db = create_db()
        
        # Setup
        testnode = db.createHistoryNode(None, "test", "test", UCIS_HISTORYNODE_TEST)
        testnode.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                      toolcategory="test", date="20240101000000"))
        file_h = db.createFileHandle("top.sv", "/tmp")
        
        # Create DU
        du = db.createScope(
            "work.counter",
            SourceInfo(file_h, 1, 0),
            1, UCIS_VLOG, UCIS_DU_MODULE,
            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE
        )
        
        # Create instance referencing DU
        inst = db.createInstance(
            "counter_inst",
            SourceInfo(file_h, 10, 0),
            1, UCIS_VLOG, UCIS_INSTANCE, du, UCIS_INST_ONCE
        )
        
        assert inst is not None
        assert inst.getScopeName() == "counter_inst"
        assert inst.getScopeType() == UCIS_INSTANCE
        
        # Persist and read
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify instance exists
        insts = list(db2.scopes(ScopeTypeT.INSTANCE))
        assert len(insts) >= 1
        found = any(s.getScopeName() == "counter_inst" for s in insts)
        assert found, f"Could not find instance for {backend_name}"
    
    def test_nested_hierarchy(self, backend):
        """Test creating nested scope hierarchy"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        db = create_db()
        
        # Setup
        testnode = db.createHistoryNode(None, "test", "test", UCIS_HISTORYNODE_TEST)
        testnode.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                      toolcategory="test", date="20240101000000"))
        file_h = db.createFileHandle("nested.sv", "/tmp")
        
        # Create DU
        du = db.createScope(
            "work.top_module",
            SourceInfo(file_h, 1, 0),
            1, UCIS_VLOG, UCIS_DU_MODULE,
            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE
        )
        
        # Create top-level instance
        top_inst = db.createInstance(
            "top",
            None, 1, UCIS_VLOG, UCIS_INSTANCE, du, UCIS_INST_ONCE
        )
        
        # Create child DU
        child_du = db.createScope(
            "work.child_module",
            SourceInfo(file_h, 20, 0),
            1, UCIS_VLOG, UCIS_DU_MODULE,
            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE
        )
        
        # Create child instance under top_inst
        child_inst = top_inst.createInstance(
            "child",
            None, 1, UCIS_VLOG, UCIS_INSTANCE, child_du, UCIS_INST_ONCE
        )
        
        assert child_inst is not None
        assert child_inst.getScopeName() == "child"
        
        # Persist and read
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify hierarchy
        top_insts = list(db2.scopes(ScopeTypeT.INSTANCE))
        assert len(top_insts) >= 1
        
        # Find top instance and check it has children
        for inst in top_insts:
            if inst.getScopeName() == "top":
                children = list(inst.scopes(ScopeTypeT.INSTANCE))
                assert len(children) >= 1, f"Top instance has no children for {backend_name}"
                child_names = [c.getScopeName() for c in children]
                assert "child" in child_names, f"Child instance not found for {backend_name}"
                break
        else:
            pytest.fail(f"Top instance not found for {backend_name}")
    
    def test_scope_weights(self, backend):
        """Test that scope weights are preserved"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        # XML format doesn't support instance weights (not in schema)
        if backend_name == "xml":
            pytest.skip("XML format doesn't support instance weights per UCIS LRM schema")
        
        db = create_db()
        
        # Setup
        testnode = db.createHistoryNode(None, "test", "test", UCIS_HISTORYNODE_TEST)
        testnode.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                      toolcategory="test", date="20240101000000"))
        file_h = db.createFileHandle("weight.sv", "/tmp")
        
        # Create instances with different weights
        du = db.createScope(
            "work.weighted",
            SourceInfo(file_h, 1, 0),
            1, UCIS_VLOG, UCIS_DU_MODULE,
            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE
        )
        
        inst1 = db.createInstance("inst1", None, 1, UCIS_VLOG, UCIS_INSTANCE, du, UCIS_INST_ONCE)
        inst2 = db.createInstance("inst2", None, 10, UCIS_VLOG, UCIS_INSTANCE, du, UCIS_INST_ONCE)
        inst3 = db.createInstance("inst3", None, 100, UCIS_VLOG, UCIS_INSTANCE, du, UCIS_INST_ONCE)
        
        assert inst1.getWeight() == 1
        assert inst2.getWeight() == 10
        assert inst3.getWeight() == 100
        
        # Persist and read
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify weights preserved
        insts = list(db2.scopes(ScopeTypeT.INSTANCE))
        inst_weights = {s.getScopeName(): s.getWeight() for s in insts}
        
        assert inst_weights.get("inst1") == 1, f"inst1 weight wrong for {backend_name}"
        assert inst_weights.get("inst2") == 10, f"inst2 weight wrong for {backend_name}"
        assert inst_weights.get("inst3") == 100, f"inst3 weight wrong for {backend_name}"
    
    def test_scope_source_info(self, backend):
        """Test that source information is preserved"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        
        db = create_db()
        
        # Setup
        testnode = db.createHistoryNode(None, "test", "test", UCIS_HISTORYNODE_TEST)
        testnode.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                      toolcategory="test", date="20240101000000"))
        file_h = db.createFileHandle("source.sv", "/project/rtl")
        
        # Create scope with source info
        du = db.createScope(
            "work.sourced",
            SourceInfo(file_h, 42, 5),  # line 42, token 5
            1, UCIS_VLOG, UCIS_DU_MODULE,
            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE
        )
        
        inst = db.createInstance(
            "sourced_inst",
            SourceInfo(file_h, 100, 10),  # line 100, token 10
            1, UCIS_VLOG, UCIS_INSTANCE, du, UCIS_INST_ONCE
        )
        
        # Check source info before persist
        src_info = inst.getSourceInfo()
        if src_info:  # Some backends may not support SourceInfo
            assert src_info.line == 100
        
        # Persist and read
        result = write_db(db, temp_file)
        db2 = read_db(result if result else db)
        
        # Verify source info preserved (if supported by backend)
        insts = list(db2.scopes(ScopeTypeT.INSTANCE))
        for s in insts:
            if s.getScopeName() == "sourced_inst":
                src = s.getSourceInfo()
                if src:  # YAML may not preserve source info
                    assert src.line == 100, f"Source line not preserved for {backend_name}"
                break
