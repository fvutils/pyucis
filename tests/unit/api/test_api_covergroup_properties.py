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
Test covergroup properties: weight, goal, at_least, comment, etc.

Tests cover:
- setWeight/getWeight on scopes
- setGoal/getGoal on covergroups and coverpoints
- setAtLeast/getAtLeast on coverpoints
- setComment/getComment
- IntProperty API (SCOPE_WEIGHT, COVER_GOAL)
"""

import pytest
from ucis import *
from ucis.source_info import SourceInfo
from ucis.cover_data import CoverData
from ucis.scope_type_t import ScopeTypeT
from ucis.int_property import IntProperty


class TestApiCovergroupProperties:
    """Test weight, goal, at_least, and comment properties on scopes"""

    def _make_cg_cp(self, db):
        fh = db.createFileHandle("design.sv", "/rtl")
        du = db.createScope("work.m1", SourceInfo(fh, 1, 0),
                            1, UCIS_VLOG, UCIS_DU_MODULE,
                            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst = db.createInstance("i_m1", None, 1, UCIS_VLOG,
                                 UCIS_INSTANCE, du, UCIS_INST_ONCE)
        cg = inst.createCovergroup("cg", SourceInfo(fh, 5, 0), 1, UCIS_OTHER)
        cgi = cg.createCoverInstance("cg", SourceInfo(fh, 5, 0), 1, UCIS_OTHER)
        cp = cgi.createCoverpoint("cp", SourceInfo(fh, 6, 0), 1, UCIS_VLOG)
        return cg, cgi, cp

    def test_scope_weight(self, backend):
        """Test setWeight/getWeight on a scope"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        cg, cgi, cp = self._make_cg_cp(db)

        cp.setWeight(5)
        assert cp.getWeight() == 5

    def test_scope_goal(self, backend):
        """Test setGoal/getGoal on a scope"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        cg, cgi, cp = self._make_cg_cp(db)

        cp.setGoal(100)
        assert cp.getGoal() == 100

    def test_scope_weight_via_int_property(self, backend):
        """Test SCOPE_WEIGHT via IntProperty API"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        cg, cgi, cp = self._make_cg_cp(db)

        cp.setIntProperty(-1, IntProperty.SCOPE_WEIGHT, 7)
        val = cp.getIntProperty(-1, IntProperty.SCOPE_WEIGHT)
        assert val == 7

    def test_coverpoint_at_least(self, backend):
        """Test setAtLeast/getAtLeast on coverpoint"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend doesn't persist at_least")

        db = create_db()
        cg, cgi, cp = self._make_cg_cp(db)

        cp.setAtLeast(10)
        assert cp.getAtLeast() == 10

    def test_covergroup_comment(self, backend):
        """Test setComment/getComment on covergroup"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support covergroup comment persistence")

        db = create_db()
        cg, cgi, cp = self._make_cg_cp(db)

        cp.setComment("my coverage comment")
        assert cp.getComment() == "my coverage comment"

    def test_covergroup_weight_and_goal(self, backend):
        """Test covergroup weight and goal properties"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        cg, cgi, cp = self._make_cg_cp(db)

        cg.setWeight(3)
        cg.setGoal(90)

        assert cg.getWeight() == 3
        assert cg.getGoal() == 90

    def test_multiple_coverpoints_with_weights(self, backend):
        """Test multiple coverpoints with different weights"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        fh = db.createFileHandle("design.sv", "/rtl")
        du = db.createScope("work.m1", SourceInfo(fh, 1, 0),
                            1, UCIS_VLOG, UCIS_DU_MODULE,
                            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst = db.createInstance("i_m1", None, 1, UCIS_VLOG,
                                 UCIS_INSTANCE, du, UCIS_INST_ONCE)
        cg = inst.createCovergroup("cg", SourceInfo(fh, 5, 0), 1, UCIS_OTHER)
        cgi = cg.createCoverInstance("cg", SourceInfo(fh, 5, 0), 1, UCIS_OTHER)

        cp1 = cgi.createCoverpoint("cp1", SourceInfo(fh, 6, 0), 2, UCIS_VLOG)
        cp2 = cgi.createCoverpoint("cp2", SourceInfo(fh, 7, 0), 3, UCIS_VLOG)

        assert cp1.getWeight() == 2
        assert cp2.getWeight() == 3
