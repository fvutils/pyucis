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
Test assertion coverage across all backends.

Tests cover:
- Creating ASSERT and COVER scopes
- Creating pass/fail/vacuous bins
- Querying assertion coverage data
"""

import pytest
from ucis import *
from ucis.source_info import SourceInfo
from ucis.cover_data import CoverData
from ucis.scope_type_t import ScopeTypeT
from ucis.cover_type_t import CoverTypeT


class TestApiAssertionCoverage:
    """Test assertion and cover property coverage"""

    def _make_inst(self, db):
        file_h = db.createFileHandle("design.sv", "/rtl")
        du = db.createScope("work.module1", SourceInfo(file_h, 1, 0),
                            1, UCIS_VLOG, UCIS_DU_MODULE,
                            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst = db.createInstance("i_module1", None, 1, UCIS_VLOG,
                                 UCIS_INSTANCE, du, UCIS_INST_ONCE)
        return inst, file_h

    def test_create_assert_scope(self, backend):
        """Test creating an ASSERT scope"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        inst, fh = self._make_inst(db)

        assert_scope = inst.createScope("my_assert", SourceInfo(fh, 10, 0),
                                        1, UCIS_VLOG, ScopeTypeT.ASSERT,
                                        UCIS_INST_ONCE)
        assert assert_scope is not None
        assert assert_scope.getScopeName() == "my_assert"
        assert assert_scope.getScopeType() == ScopeTypeT.ASSERT

    def test_create_cover_scope(self, backend):
        """Test creating a COVER (cover property) scope"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        inst, fh = self._make_inst(db)

        cover_scope = inst.createScope("my_cover_prop", SourceInfo(fh, 20, 0),
                                       1, UCIS_VLOG, ScopeTypeT.COVER,
                                       UCIS_INST_ONCE)
        assert cover_scope is not None
        assert cover_scope.getScopeName() == "my_cover_prop"
        assert cover_scope.getScopeType() == ScopeTypeT.COVER

    def test_assert_pass_fail_bins(self, backend):
        """Test creating pass and fail bins on an assertion scope"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        inst, fh = self._make_inst(db)

        assert_scope = inst.createScope("chk_valid", SourceInfo(fh, 15, 0),
                                        1, UCIS_VLOG, ScopeTypeT.ASSERT,
                                        UCIS_INST_ONCE)

        pass_data = CoverData(CoverTypeT.PASSBIN, 100)
        fail_data = CoverData(CoverTypeT.FAILBIN, 0)
        assert_scope.createNextCover("pass", pass_data, SourceInfo(fh, 15, 0))
        assert_scope.createNextCover("fail", fail_data, SourceInfo(fh, 15, 0))

        pass_bins = list(assert_scope.coverItems(CoverTypeT.PASSBIN))
        fail_bins = list(assert_scope.coverItems(CoverTypeT.FAILBIN))
        assert len(pass_bins) == 1
        assert len(fail_bins) == 1

    def test_assert_scope_in_hierarchy(self, backend):
        """Test assertion scopes appear in hierarchy iteration"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        inst, fh = self._make_inst(db)

        for name in ["assert1", "assert2"]:
            inst.createScope(name, SourceInfo(fh, 10, 0), 1, UCIS_VLOG,
                             ScopeTypeT.ASSERT, UCIS_INST_ONCE)

        assert_scopes = list(inst.scopes(ScopeTypeT.ASSERT))
        assert len(assert_scopes) == 2
        names = {s.getScopeName() for s in assert_scopes}
        assert names == {"assert1", "assert2"}

    def test_vacuous_bin(self, backend):
        """Test vacuous pass bin on assertion scope"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        inst, fh = self._make_inst(db)

        assert_scope = inst.createScope("seq_check", SourceInfo(fh, 30, 0),
                                        1, UCIS_VLOG, ScopeTypeT.ASSERT,
                                        UCIS_INST_ONCE)

        vacuous_data = CoverData(CoverTypeT.VACUOUSBIN, 5)
        assert_scope.createNextCover("vacuous", vacuous_data, None)

        vac_bins = list(assert_scope.coverItems(CoverTypeT.VACUOUSBIN))
        assert len(vac_bins) == 1
