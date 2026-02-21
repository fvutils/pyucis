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
Tests for cover item flag API (CoverFlagsT).

Tests cover:
- getCoverFlags / setCoverFlags on cover items
- CoverFlagsT enum values (HAS_GOAL, HAS_WEIGHT, etc.)
"""

import pytest
from ucis import *
from ucis.source_info import SourceInfo
from ucis.scope_type_t import ScopeTypeT
from ucis.cover_flags_t import CoverFlagsT
from ucis.cover_data import CoverData
from ucis.cover_type_t import CoverTypeT


def _make_coverpoint_with_bin(db):
    fh = db.createFileHandle("design.sv", "/rtl")
    du = db.createScope("work.dut", SourceInfo(fh, 1, 0),
                        1, UCIS_SV, UCIS_DU_MODULE,
                        UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
    inst = db.createInstance("dut", None, 1, UCIS_SV,
                             UCIS_INSTANCE, du, UCIS_INST_ONCE)
    cg = inst.createCovergroup("cg", SourceInfo(fh, 5, 0), 1, UCIS_SV)
    cgi = cg.createCoverInstance("cg", SourceInfo(fh, 5, 0), 1, UCIS_SV)
    cp = cgi.createCoverpoint("cp", SourceInfo(fh, 6, 0), 1, UCIS_SV)
    cd = CoverData(CoverTypeT.CVGBIN, 0)
    cd.data = 3
    bin_item = cp.createNextCover("bin_a", cd, SourceInfo(fh, 7, 0))
    return bin_item


class TestApiCoverFlags:
    """Tests for cover item flags (CoverFlagsT)"""

    def test_default_flags_zero(self, backend):
        """Cover items start with flags == 0"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support cover flags")
        db = create_db()
        item = _make_coverpoint_with_bin(db)
        assert item.getCoverFlags() == 0

    def test_set_get_flags(self, backend):
        """setCoverFlags / getCoverFlags round-trip"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support cover flags")
        db = create_db()
        item = _make_coverpoint_with_bin(db)
        item.setCoverFlags(CoverFlagsT.HAS_GOAL | CoverFlagsT.HAS_WEIGHT)
        flags = item.getCoverFlags()
        assert flags & CoverFlagsT.HAS_GOAL
        assert flags & CoverFlagsT.HAS_WEIGHT

    def test_flags_independent_per_item(self, backend):
        """Flags set on one item do not affect another"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support cover flags")
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
        cd = CoverData(CoverTypeT.CVGBIN, 0)
        b1 = cp.createNextCover("bin_a", cd, SourceInfo(fh, 7, 0))
        b2 = cp.createNextCover("bin_b", CoverData(CoverTypeT.CVGBIN, 0),
                                SourceInfo(fh, 8, 0))
        b1.setCoverFlags(CoverFlagsT.HAS_GOAL)
        assert b1.getCoverFlags() & CoverFlagsT.HAS_GOAL
        assert not (b2.getCoverFlags() & CoverFlagsT.HAS_GOAL)
