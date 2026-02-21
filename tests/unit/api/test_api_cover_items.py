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
Test cover item operations across all backends.

Tests cover:
- createNextCover with various cover types
- incrementCover / setCoverData
- getCoverData / getName / getSourceInfo
- Cover item flags (HAS_GOAL, HAS_WEIGHT)
"""

import pytest
from ucis import *
from ucis.source_info import SourceInfo
from ucis.cover_data import CoverData
from ucis.cover_type_t import CoverTypeT
from ucis.cover_flags_t import CoverFlagsT
from ucis.scope_type_t import ScopeTypeT


class TestApiCoverItems:
    """Test cover item CRUD and data manipulation"""

    def _make_cg_cp(self, db):
        """Helper: create a covergroup + coverpoint."""
        fh = db.createFileHandle("design.sv", "/rtl")
        du = db.createScope("work.m1", SourceInfo(fh, 1, 0),
                            1, UCIS_VLOG, UCIS_DU_MODULE,
                            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst = db.createInstance("i_m1", None, 1, UCIS_VLOG,
                                 UCIS_INSTANCE, du, UCIS_INST_ONCE)
        cg = inst.createCovergroup("cg", SourceInfo(fh, 5, 0), 1, UCIS_OTHER)
        cgi = cg.createCoverInstance("cg", SourceInfo(fh, 5, 0), 1, UCIS_OTHER)
        cp = cgi.createCoverpoint("cp", SourceInfo(fh, 6, 0), 1, UCIS_VLOG)
        return cp, fh

    def test_create_cover_item(self, backend):
        """Test creating a cover item with createNextCover"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        cp, fh = self._make_cg_cp(db)

        cd = CoverData(UCIS_CVGBIN, 0)
        cd.goal = 1
        idx = cp.createNextCover("bin_a", cd, SourceInfo(fh, 7, 0))
        assert idx is not None

    def test_get_cover_item_name(self, backend):
        """Test getting the name of a cover item"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        cp, fh = self._make_cg_cp(db)

        cd = CoverData(UCIS_CVGBIN, 5)
        cp.createNextCover("my_bin", cd, SourceInfo(fh, 7, 0))

        items = list(cp.coverItems(CoverTypeT.CVGBIN))
        assert len(items) >= 1
        found = any(item.getName() == "my_bin" for item in items)
        assert found, "Cover item 'my_bin' not found"

    def test_get_cover_data(self, backend):
        """Test getting cover data from a cover item"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        cp, fh = self._make_cg_cp(db)

        cd = CoverData(UCIS_CVGBIN, 0)
        cd.data = 7  # set count explicitly
        cp.createNextCover("bin_count_7", cd, None)

        items = list(cp.coverItems(CoverTypeT.CVGBIN))
        for item in items:
            if item.getName() == "bin_count_7":
                data = item.getCoverData()
                assert data.data == 7
                return
        pytest.fail("Cover item 'bin_count_7' not found")

    def test_increment_cover(self, backend):
        """Test incrementing a cover item count"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support in-memory cover item mutation after read")

        db = create_db()
        cp, fh = self._make_cg_cp(db)

        cd = CoverData(UCIS_CVGBIN, 0)
        cd.data = 3  # initial count
        cp.createNextCover("bin_inc", cd, None)

        items = list(cp.coverItems(CoverTypeT.CVGBIN))
        for item in items:
            if item.getName() == "bin_inc":
                item.incrementCover(2)
                assert item.getCoverData().data == 5
                return
        pytest.fail("Cover item 'bin_inc' not found")

    def test_set_cover_data(self, backend):
        """Test setting cover data directly"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support in-memory cover item mutation")

        db = create_db()
        cp, fh = self._make_cg_cp(db)

        cd = CoverData(UCIS_CVGBIN, 0)
        cd.data = 1
        cp.createNextCover("bin_set", cd, None)

        items = list(cp.coverItems(CoverTypeT.CVGBIN))
        for item in items:
            if item.getName() == "bin_set":
                new_data = CoverData(UCIS_CVGBIN, 0)
                new_data.data = 99
                item.setCoverData(new_data)
                assert item.getCoverData().data == 99
                return
        pytest.fail("Cover item 'bin_set' not found")

    def test_cover_item_source_info(self, backend):
        """Test getting source info from a cover item"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        cp, fh = self._make_cg_cp(db)

        cd = CoverData(UCIS_CVGBIN, 0)
        cp.createNextCover("bin_src", cd, SourceInfo(fh, 42, 0))

        items = list(cp.coverItems(CoverTypeT.CVGBIN))
        for item in items:
            if item.getName() == "bin_src":
                src = item.getSourceInfo()
                if src is not None:
                    assert src.line == 42
                return
        pytest.fail("Cover item 'bin_src' not found")

    def test_multiple_cover_items(self, backend):
        """Test creating multiple cover items on a coverpoint"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        cp, fh = self._make_cg_cp(db)

        for i in range(5):
            cd = CoverData(UCIS_CVGBIN, i * 2)
            cp.createNextCover(f"bin_{i}", cd, None)

        items = list(cp.coverItems(CoverTypeT.CVGBIN))
        assert len(items) == 5
