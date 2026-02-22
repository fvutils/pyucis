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
Tests for HDL structural scope types: PROCESS, BLOCK, FUNCTION, GENERATE,
FORKJOIN, BRANCH, EXPR, COND.

These scope types model code-coverage constructs inside design units and
instances (procedures, blocks, generate loops, expressions, etc.).

Also covers createInstanceByName() — creating instances by DU name string.
"""

import pytest
from ucis import *
from ucis.source_info import SourceInfo
from ucis.scope_type_t import ScopeTypeT


def _base_hierarchy(db):
    fh = db.createFileHandle("design.sv", "/rtl")
    du = db.createScope("work.top", SourceInfo(fh, 1, 0),
                        1, UCIS_SV, UCIS_DU_MODULE,
                        UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
    inst = db.createInstance("top", None, 1, UCIS_SV,
                             UCIS_INSTANCE, du, UCIS_INST_ONCE)
    return fh, du, inst


class TestApiHdlScopes:
    """Test HDL structural scope types"""

    def test_create_process_scope(self, backend):
        """PROCESS scope can be created under an INSTANCE"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support HDL scopes")
        db = create_db()
        fh, du, inst = _base_hierarchy(db)
        proc = inst.createScope("always_ff_0", SourceInfo(fh, 10, 0),
                                1, UCIS_SV, ScopeTypeT.PROCESS, 0)
        assert proc is not None
        assert proc.getScopeType() == ScopeTypeT.PROCESS
        assert proc.getScopeName() == "always_ff_0"

    def test_create_block_scope(self, backend):
        """BLOCK scope can be created inside a PROCESS"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support HDL scopes")
        db = create_db()
        fh, du, inst = _base_hierarchy(db)
        proc = inst.createScope("p1", SourceInfo(fh, 10, 0),
                                1, UCIS_SV, ScopeTypeT.PROCESS, 0)
        blk = proc.createScope("begin_end", SourceInfo(fh, 11, 0),
                               1, UCIS_SV, ScopeTypeT.BLOCK, 0)
        assert blk.getScopeType() == ScopeTypeT.BLOCK

    def test_create_generate_scope(self, backend):
        """GENERATE scope can be created under an INSTANCE"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support HDL scopes")
        db = create_db()
        fh, du, inst = _base_hierarchy(db)
        gen = inst.createScope("genblk1", SourceInfo(fh, 20, 0),
                               1, UCIS_SV, ScopeTypeT.GENERATE, 0)
        assert gen.getScopeType() == ScopeTypeT.GENERATE

    def test_create_forkjoin_scope(self, backend):
        """FORKJOIN scope can be created inside a PROCESS"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support HDL scopes")
        db = create_db()
        fh, du, inst = _base_hierarchy(db)
        proc = inst.createScope("p1", SourceInfo(fh, 10, 0),
                                1, UCIS_SV, ScopeTypeT.PROCESS, 0)
        fj = proc.createScope("fork_join", SourceInfo(fh, 12, 0),
                              1, UCIS_SV, ScopeTypeT.FORKJOIN, 0)
        assert fj.getScopeType() == ScopeTypeT.FORKJOIN

    def test_create_branch_scope(self, backend):
        """BRANCH scope can be created inside a PROCESS"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support HDL scopes")
        db = create_db()
        fh, du, inst = _base_hierarchy(db)
        proc = inst.createScope("p1", SourceInfo(fh, 10, 0),
                                1, UCIS_SV, ScopeTypeT.PROCESS, 0)
        branch = proc.createScope("if_stmt", SourceInfo(fh, 15, 0),
                                  1, UCIS_SV, ScopeTypeT.BRANCH, 0)
        assert branch.getScopeType() == ScopeTypeT.BRANCH

    def test_create_expr_scope(self, backend):
        """EXPR scope can be created inside a PROCESS"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support HDL scopes")
        db = create_db()
        fh, du, inst = _base_hierarchy(db)
        proc = inst.createScope("p1", SourceInfo(fh, 10, 0),
                                1, UCIS_SV, ScopeTypeT.PROCESS, 0)
        expr = proc.createScope("expr0", SourceInfo(fh, 16, 0),
                                1, UCIS_SV, ScopeTypeT.EXPR, 0)
        assert expr.getScopeType() == ScopeTypeT.EXPR

    def test_scope_iteration_by_type(self, backend):
        """scopes() iterator correctly filters by HDL scope type"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support HDL scopes")
        db = create_db()
        fh, du, inst = _base_hierarchy(db)
        inst.createScope("p1", SourceInfo(fh, 10, 0), 1, UCIS_SV, ScopeTypeT.PROCESS, 0)
        inst.createScope("gen1", SourceInfo(fh, 20, 0), 1, UCIS_SV, ScopeTypeT.GENERATE, 0)
        inst.createScope("p2", SourceInfo(fh, 30, 0), 1, UCIS_SV, ScopeTypeT.PROCESS, 0)

        processes = list(inst.scopes(ScopeTypeT.PROCESS))
        generates = list(inst.scopes(ScopeTypeT.GENERATE))
        assert len(processes) == 2
        assert len(generates) == 1


class TestApiCreateInstanceByName:
    """Test createInstanceByName"""

    def test_create_instance_by_qualified_du_name(self, backend):
        """createInstanceByName with 'lib.module' resolves the DU"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support createInstanceByName")
        db = create_db()
        fh = db.createFileHandle("d.sv", "/rtl")
        du = db.createScope("work.counter", SourceInfo(fh, 1, 0),
                            1, UCIS_SV, UCIS_DU_MODULE,
                            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst = db.createInstanceByName("cnt0", "work.counter",
                                       None, 1, UCIS_SV, UCIS_INST_ONCE)
        assert inst is not None
        assert inst.getScopeName() == "cnt0"

    def test_create_instance_by_unqualified_du_name(self, backend):
        """createInstanceByName with 'module' uses default 'work' library"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support createInstanceByName")
        db = create_db()
        fh = db.createFileHandle("d.sv", "/rtl")
        db.createScope("work.alu", SourceInfo(fh, 1, 0),
                       1, UCIS_SV, UCIS_DU_MODULE,
                       UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst = db.createInstanceByName("alu0", "alu",
                                       None, 1, UCIS_SV, UCIS_INST_ONCE)
        assert inst.getScopeName() == "alu0"

    def test_create_instance_by_name_unknown_raises(self, backend):
        """createInstanceByName raises KeyError for unknown DU name"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support createInstanceByName")
        db = create_db()
        with pytest.raises(KeyError):
            db.createInstanceByName("x", "work.nonexistent",
                                    None, 1, UCIS_SV, UCIS_INST_ONCE)
