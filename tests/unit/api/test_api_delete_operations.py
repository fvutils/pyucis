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
Tests for removeScope() and removeCover() delete operations.
"""

import pytest
from ucis import *
from ucis.source_info import SourceInfo
from ucis.scope_type_t import ScopeTypeT
from ucis.cover_data import CoverData
from ucis.cover_type_t import CoverTypeT


def _make_hierarchy(db):
    """Create a small hierarchy: db -> du, inst"""
    fh = db.createFileHandle("design.v", "/rtl")
    du = db.createScope("work.module1", SourceInfo(fh, 1, 0),
                        1, UCIS_VLOG, UCIS_DU_MODULE,
                        UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
    inst = db.createInstance("i_module1", None, 1, UCIS_VLOG,
                             UCIS_INSTANCE, du, UCIS_INST_ONCE)
    return du, inst, fh


class TestApiDeleteOperations:
    """Tests for removeScope and removeCover"""

    def test_remove_scope_reduces_scope_count(self, backend):
        """removeScope removes a scope so it no longer appears in iteration"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support removeScope")
        db = create_db()
        fh = db.createFileHandle("d.v", "/rtl")
        du = db.createScope("work.m", SourceInfo(fh, 1, 0),
                            1, UCIS_VLOG, UCIS_DU_MODULE,
                            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst_a = db.createInstance("ia", None, 1, UCIS_VLOG,
                                   UCIS_INSTANCE, du, UCIS_INST_ONCE)
        inst_b = db.createInstance("ib", None, 1, UCIS_VLOG,
                                   UCIS_INSTANCE, du, UCIS_INST_ONCE)
        # Both instances visible before removal
        names_before = {s.getScopeName() for s in db.scopes(ScopeTypeT.ALL)}
        assert "ia" in names_before
        assert "ib" in names_before

        db.removeScope(inst_a)

        names_after = {s.getScopeName() for s in db.scopes(ScopeTypeT.ALL)}
        assert "ia" not in names_after
        assert "ib" in names_after

    def test_remove_cover_reduces_cover_count(self, backend):
        """removeCover removes a bin so it no longer appears in coverItems"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support removeCover")
        db = create_db()
        fh = db.createFileHandle("d.sv", "/rtl")
        du = db.createScope("work.dut", SourceInfo(fh, 1, 0),
                            1, UCIS_SV, UCIS_DU_MODULE,
                            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst = db.createInstance("dut", None, 1, UCIS_SV,
                                 UCIS_INSTANCE, du, UCIS_INST_ONCE)
        cg = inst.createCovergroup("cg", SourceInfo(fh, 5, 0), 1, UCIS_SV)
        cgi = cg.createCoverInstance("cg", SourceInfo(fh, 5, 0), 1, UCIS_SV)
        cp = cgi.createCoverpoint("cp", SourceInfo(fh, 6, 0), 1, UCIS_SV)
        cd0 = CoverData(CoverTypeT.CVGBIN, 0)
        cd1 = CoverData(CoverTypeT.CVGBIN, 0)
        cp.createNextCover("bin_a", cd0, SourceInfo(fh, 7, 0))
        cp.createNextCover("bin_b", cd1, SourceInfo(fh, 8, 0))

        items_before = list(cp.coverItems(CoverTypeT.CVGBIN))
        assert len(items_before) == 2

        cp.removeCover(0)

        items_after = list(cp.coverItems(CoverTypeT.CVGBIN))
        assert len(items_after) == 1
        assert items_after[0].getName() == "bin_b"
