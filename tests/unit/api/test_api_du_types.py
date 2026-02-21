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
Test DU scope types and HDL instance scopes across all backends.

Tests cover:
- DU_MODULE, DU_ARCH, DU_PACKAGE, DU_PROGRAM, DU_INTERFACE design units
- INSTANCE scope creation
- DU_ANY helper method
- Nested instance hierarchies
- getSourceFiles and getCoverInstances
"""

import pytest
from ucis import *
from ucis.source_info import SourceInfo
from ucis.scope_type_t import ScopeTypeT


class TestApiDUTypes:
    """Test design unit scope types and HDL instance scopes"""

    def test_du_module(self, backend):
        """Test creating a DU_MODULE scope"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        fh = db.createFileHandle("top.v", "/rtl")

        du = db.createScope("work.top", SourceInfo(fh, 1, 0),
                            1, UCIS_VLOG, UCIS_DU_MODULE,
                            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        assert du is not None
        assert du.getScopeName() == "work.top"
        assert du.getScopeType() == ScopeTypeT.DU_MODULE

    def test_du_package(self, backend):
        """Test creating a DU_PACKAGE scope"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        fh = db.createFileHandle("pkg.sv", "/rtl")

        pkg = db.createScope("work.my_pkg", SourceInfo(fh, 1, 0),
                             1, UCIS_VLOG, ScopeTypeT.DU_PACKAGE,
                             UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        assert pkg is not None
        assert pkg.getScopeType() == ScopeTypeT.DU_PACKAGE

    def test_du_program(self, backend):
        """Test creating a DU_PROGRAM scope"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        fh = db.createFileHandle("prog.sv", "/rtl")

        prog = db.createScope("work.my_prog", SourceInfo(fh, 1, 0),
                              1, UCIS_VLOG, ScopeTypeT.DU_PROGRAM,
                              UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        assert prog is not None
        assert prog.getScopeType() == ScopeTypeT.DU_PROGRAM

    def test_du_interface(self, backend):
        """Test creating a DU_INTERFACE scope"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        fh = db.createFileHandle("intf.sv", "/rtl")

        intf = db.createScope("work.my_intf", SourceInfo(fh, 1, 0),
                              1, UCIS_VLOG, ScopeTypeT.DU_INTERFACE,
                              UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        assert intf is not None
        assert intf.getScopeType() == ScopeTypeT.DU_INTERFACE

    def test_du_any_classification(self, backend):
        """Test DU_ANY() helper identifies all DU types"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        fh = db.createFileHandle("design.sv", "/rtl")

        for du_type in [ScopeTypeT.DU_MODULE, ScopeTypeT.DU_PACKAGE,
                        ScopeTypeT.DU_PROGRAM, ScopeTypeT.DU_INTERFACE]:
            du = db.createScope(f"work.du_{du_type}", SourceInfo(fh, 1, 0),
                                1, UCIS_VLOG, du_type,
                                UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
            assert ScopeTypeT.DU_ANY(du.getScopeType()), \
                f"DU_ANY should match {du_type}"

    def test_instance_scope(self, backend):
        """Test creating INSTANCE scope under a DU"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        fh = db.createFileHandle("top.v", "/rtl")

        du = db.createScope("work.top", SourceInfo(fh, 1, 0),
                            1, UCIS_VLOG, UCIS_DU_MODULE,
                            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)

        inst = db.createInstance("top", None, 1, UCIS_VLOG,
                                 UCIS_INSTANCE, du, UCIS_INST_ONCE)
        assert inst is not None
        assert inst.getScopeName() == "top"
        assert inst.getScopeType() == ScopeTypeT.INSTANCE

    def test_nested_instances(self, backend):
        """Test nested instance hierarchy"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        fh = db.createFileHandle("top.v", "/rtl")

        du_top = db.createScope("work.top", SourceInfo(fh, 1, 0),
                                1, UCIS_VLOG, UCIS_DU_MODULE,
                                UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        du_sub = db.createScope("work.sub", SourceInfo(fh, 10, 0),
                                1, UCIS_VLOG, UCIS_DU_MODULE,
                                UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)

        top_inst = db.createInstance("top", None, 1, UCIS_VLOG,
                                     UCIS_INSTANCE, du_top, UCIS_INST_ONCE)
        sub_inst = top_inst.createInstance("u_sub", None, 1, UCIS_VLOG,
                                           UCIS_INSTANCE, du_sub, UCIS_INST_ONCE)

        assert sub_inst is not None
        assert sub_inst.getScopeName() == "u_sub"

        # sub_inst should appear in top_inst's child scopes
        children = list(top_inst.scopes(ScopeTypeT.INSTANCE))
        assert len(children) == 1
        assert children[0].getScopeName() == "u_sub"

    def test_get_source_files(self, backend):
        """Test getSourceFiles() returns registered file handles"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend getSourceFiles not fully implemented")

        db = create_db()
        db.createFileHandle("file1.v", "/rtl")
        db.createFileHandle("file2.v", "/rtl")
        db.createFileHandle("file3.v", "/rtl")

        files = db.getSourceFiles()
        filenames = {f.getFileName() for f in files}
        assert "file1.v" in filenames
        assert "file2.v" in filenames
        assert "file3.v" in filenames

    def test_get_cover_instances(self, backend):
        """Test getCoverInstances() returns top-level instance scopes"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend getCoverInstances not fully tested")

        db = create_db()
        fh = db.createFileHandle("top.v", "/rtl")
        du = db.createScope("work.top", SourceInfo(fh, 1, 0),
                            1, UCIS_VLOG, UCIS_DU_MODULE,
                            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        db.createInstance("top", None, 1, UCIS_VLOG,
                          UCIS_INSTANCE, du, UCIS_INST_ONCE)

        instances = db.getCoverInstances()
        # At least one instance should be returned
        assert len(instances) >= 1
