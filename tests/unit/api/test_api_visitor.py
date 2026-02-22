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
Test the UCISVisitor and traverse utility.

Tests cover:
- Basic traversal of a database
- Visiting instances, covergroups, coverpoints
- Visiting cover items
- Custom visitor accumulates correct scope counts
"""

import pytest
from ucis import *
from ucis.source_info import SourceInfo
from ucis.cover_data import CoverData
from ucis.cover_type_t import CoverTypeT
from ucis.scope_type_t import ScopeTypeT
from ucis.visitors.UCISVisitor import UCISVisitor
from ucis.visitors.traverse import traverse


class CountingVisitor(UCISVisitor):
    """A visitor that counts visits to each scope type."""

    def __init__(self):
        super().__init__()
        self.instances = []
        self.covergroups = []
        self.coverpoints = []
        self.cover_items = []
        self.dbs = []

    def visit_db(self, db):
        self.dbs.append(db)

    def visit_instance(self, inst):
        self.instances.append(inst.getScopeName())

    def visit_covergroup(self, cg):
        self.covergroups.append(cg.getScopeName())

    def visit_coverpoint(self, cp):
        self.coverpoints.append(cp.getScopeName())

    def visit_cover_item(self, idx):
        self.cover_items.append(idx.getName())


class TestApiVisitor:
    """Test the UCISVisitor and traverse utility"""

    def test_traverse_empty_db(self, backend):
        """Test traversing an empty database"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        v = CountingVisitor()
        traverse(db, v)

        assert len(v.dbs) == 1
        assert len(v.instances) == 0

    def test_traverse_single_instance(self, backend):
        """Test traversal visits an instance scope"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        fh = db.createFileHandle("design.v", "/rtl")
        du = db.createScope("work.top", SourceInfo(fh, 1, 0),
                            1, UCIS_VLOG, UCIS_DU_MODULE,
                            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        db.createInstance("top_inst", None, 1, UCIS_VLOG,
                          UCIS_INSTANCE, du, UCIS_INST_ONCE)

        v = CountingVisitor()
        traverse(db, v)

        assert "top_inst" in v.instances

    def test_traverse_coverpoint_bins(self, backend):
        """Test traversal visits coverpoints and their bins"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        fh = db.createFileHandle("design.sv", "/rtl")
        du = db.createScope("work.m", SourceInfo(fh, 1, 0),
                            1, UCIS_VLOG, UCIS_DU_MODULE,
                            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst = db.createInstance("i_m", None, 1, UCIS_VLOG,
                                 UCIS_INSTANCE, du, UCIS_INST_ONCE)
        cg = inst.createCovergroup("cg", SourceInfo(fh, 5, 0), 1, UCIS_OTHER)
        cgi = cg.createCoverInstance("cg", SourceInfo(fh, 5, 0), 1, UCIS_OTHER)
        cp = cgi.createCoverpoint("cp", SourceInfo(fh, 6, 0), 1, UCIS_VLOG)

        cd = CoverData(UCIS_CVGBIN, 0)
        cp.createNextCover("bin_a", cd, None)
        cd2 = CoverData(UCIS_CVGBIN, 0)
        cp.createNextCover("bin_b", cd2, None)

        v = CountingVisitor()
        traverse(db, v)

        assert "cp" in v.coverpoints
        assert "bin_a" in v.cover_items
        assert "bin_b" in v.cover_items

    def test_traverse_covergroup(self, backend):
        """Test that covergroup scopes are visited"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        fh = db.createFileHandle("design.sv", "/rtl")
        du = db.createScope("work.m", SourceInfo(fh, 1, 0),
                            1, UCIS_VLOG, UCIS_DU_MODULE,
                            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst = db.createInstance("i_m", None, 1, UCIS_VLOG,
                                 UCIS_INSTANCE, du, UCIS_INST_ONCE)
        inst.createCovergroup("my_cg", SourceInfo(fh, 5, 0), 1, UCIS_OTHER)

        v = CountingVisitor()
        traverse(db, v)

        assert "my_cg" in v.covergroups

    def test_custom_visitor(self, backend):
        """Test writing a simple coverage reporter visitor"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        fh = db.createFileHandle("design.sv", "/rtl")
        du = db.createScope("work.m", SourceInfo(fh, 1, 0),
                            1, UCIS_VLOG, UCIS_DU_MODULE,
                            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        for i in range(3):
            db.createInstance(f"inst_{i}", None, 1, UCIS_VLOG,
                              UCIS_INSTANCE, du, UCIS_INST_ONCE)

        class InstanceCounter(UCISVisitor):
            def __init__(self):
                super().__init__()
                self.count = 0

            def visit_instance(self, inst):
                self.count += 1

        v = InstanceCounter()
        traverse(db, v)
        assert v.count == 3

    def test_clone_database(self, backend):
        """Test cloning a database"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("clone() not applicable for XML backend")

        from ucis.mem.mem_factory import MemFactory

        db = create_db()
        fh = db.createFileHandle("d.v", "/r")
        du = db.createScope("work.m", SourceInfo(fh, 1, 0),
                            1, UCIS_VLOG, UCIS_DU_MODULE,
                            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        db.createInstance("top", None, 1, UCIS_VLOG, UCIS_INSTANCE, du, UCIS_INST_ONCE)

        cloned = MemFactory.clone(db)

        v_orig = CountingVisitor()
        v_clone = CountingVisitor()
        traverse(db, v_orig)
        traverse(cloned, v_clone)

        assert v_orig.instances == v_clone.instances
