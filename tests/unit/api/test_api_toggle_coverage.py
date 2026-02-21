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
Test toggle coverage across all backends.

Tests cover:
- Creating toggle coverage scopes
- Setting toggle metric, type, direction
- Creating 0->1 and 1->0 toggle bins
- Querying coverage data
"""

import pytest
from ucis import *
from ucis.test_data import TestData
from ucis.source_info import SourceInfo
from ucis.cover_data import CoverData
from ucis.scope_type_t import ScopeTypeT
from ucis.cover_type_t import CoverTypeT
from ucis.toggle_metric_t import ToggleMetricT
from ucis.toggle_type_t import ToggleTypeT
from ucis.toggle_dir_t import ToggleDirT


class TestApiToggleCoverage:
    """Test toggle coverage operations"""

    def test_create_toggle_scope(self, backend):
        """Test creating a toggle scope via createToggle()"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        file_h = db.createFileHandle("design.v", "/rtl")
        du = db.createScope("work.module1", SourceInfo(file_h, 1, 0),
                            1, UCIS_VLOG, UCIS_DU_MODULE,
                            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst = db.createInstance("i_module1", None, 1, UCIS_VLOG,
                                 UCIS_INSTANCE, du, UCIS_INST_ONCE)

        toggle = inst.createToggle(
            "data_sig",
            "top.i_module1.data_sig",
            UCIS_INST_ONCE,
            ToggleMetricT._2STOGGLE,
            ToggleTypeT.NET,
            ToggleDirT.INTERNAL
        )

        assert toggle is not None
        assert toggle.getScopeName() == "data_sig"
        assert toggle.getScopeType() == ScopeTypeT.TOGGLE

    def test_toggle_canonical_name(self, backend):
        """Test canonical name on toggle scope"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        file_h = db.createFileHandle("design.v", "/rtl")
        du = db.createScope("work.module1", SourceInfo(file_h, 1, 0),
                            1, UCIS_VLOG, UCIS_DU_MODULE,
                            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst = db.createInstance("i_module1", None, 1, UCIS_VLOG,
                                 UCIS_INSTANCE, du, UCIS_INST_ONCE)

        toggle = inst.createToggle(
            "data_sig",
            "top.i_module1.data_sig",
            UCIS_INST_ONCE,
            ToggleMetricT._2STOGGLE,
            ToggleTypeT.NET,
            ToggleDirT.INTERNAL
        )

        assert toggle.getCanonicalName() == "top.i_module1.data_sig"

    def test_toggle_metric_type_dir(self, backend):
        """Test toggle metric, type, and direction properties"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        file_h = db.createFileHandle("design.v", "/rtl")
        du = db.createScope("work.module1", SourceInfo(file_h, 1, 0),
                            1, UCIS_VLOG, UCIS_DU_MODULE,
                            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst = db.createInstance("i_module1", None, 1, UCIS_VLOG,
                                 UCIS_INSTANCE, du, UCIS_INST_ONCE)

        toggle = inst.createToggle(
            "out_port",
            "top.i_module1.out_port",
            UCIS_INST_ONCE,
            ToggleMetricT._2STOGGLE,
            ToggleTypeT.REG,
            ToggleDirT.OUT
        )

        assert toggle.getToggleMetric() == ToggleMetricT._2STOGGLE
        assert toggle.getToggleType() == ToggleTypeT.REG
        assert toggle.getToggleDir() == ToggleDirT.OUT

    def test_toggle_bins(self, backend):
        """Test creating 0->1 and 1->0 bins on a toggle scope"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        file_h = db.createFileHandle("design.v", "/rtl")
        du = db.createScope("work.module1", SourceInfo(file_h, 1, 0),
                            1, UCIS_VLOG, UCIS_DU_MODULE,
                            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst = db.createInstance("i_module1", None, 1, UCIS_VLOG,
                                 UCIS_INSTANCE, du, UCIS_INST_ONCE)

        toggle = inst.createToggle(
            "clk",
            "top.i_module1.clk",
            UCIS_INST_ONCE,
            ToggleMetricT._2STOGGLE,
            ToggleTypeT.NET,
            ToggleDirT.IN
        )

        # Create the 0->1 and 1->0 toggle bins
        cd01 = CoverData(CoverTypeT.TOGGLEBIN, 10)
        cd10 = CoverData(CoverTypeT.TOGGLEBIN, 10)
        toggle.createNextCover("0->1", cd01, None)
        toggle.createNextCover("1->0", cd10, None)

        # Verify bins exist via iteration
        bins = list(toggle.coverItems(CoverTypeT.TOGGLEBIN))
        assert len(bins) == 2

    def test_toggle_write_read_roundtrip(self, backend):
        """Test writing and reading back toggle coverage"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        if backend_name == "xml":
            pytest.skip("XML backend does not support toggle scope roundtrip")

        db = create_db()
        file_h = db.createFileHandle("design.v", "/rtl")
        du = db.createScope("work.module1", SourceInfo(file_h, 1, 0),
                            1, UCIS_VLOG, UCIS_DU_MODULE,
                            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst = db.createInstance("i_module1", None, 1, UCIS_VLOG,
                                 UCIS_INSTANCE, du, UCIS_INST_ONCE)

        toggle = inst.createToggle(
            "bus_sig",
            "top.i_module1.bus_sig",
            UCIS_INST_ONCE,
            ToggleMetricT._2STOGGLE,
            ToggleTypeT.NET,
            ToggleDirT.INTERNAL
        )
        cd01 = CoverData(CoverTypeT.TOGGLEBIN, 7)
        cd10 = CoverData(CoverTypeT.TOGGLEBIN, 7)
        toggle.createNextCover("0->1", cd01, None)
        toggle.createNextCover("1->0", cd10, None)

        # Write and read back
        written = write_db(db, temp_file)
        db2 = read_db(written if written is not None else db)

        # Walk back to the instance scope
        inst2 = None
        for s in db2.scopes(ScopeTypeT.INSTANCE):
            inst2 = s
            break

        assert inst2 is not None

        # Find the toggle scope
        toggle2 = None
        for s in inst2.scopes(ScopeTypeT.TOGGLE):
            toggle2 = s
            break

        assert toggle2 is not None
        assert toggle2.getScopeName() == "bus_sig"

    def test_multiple_toggles(self, backend):
        """Test creating multiple toggle scopes on an instance"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        file_h = db.createFileHandle("design.v", "/rtl")
        du = db.createScope("work.module1", SourceInfo(file_h, 1, 0),
                            1, UCIS_VLOG, UCIS_DU_MODULE,
                            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst = db.createInstance("i_module1", None, 1, UCIS_VLOG,
                                 UCIS_INSTANCE, du, UCIS_INST_ONCE)

        for sig in ["sig_a", "sig_b", "sig_c"]:
            t = inst.createToggle(sig, f"top.{sig}", UCIS_INST_ONCE,
                                  ToggleMetricT._2STOGGLE, ToggleTypeT.NET,
                                  ToggleDirT.INTERNAL)
            t.createNextCover("0->1", CoverData(CoverTypeT.TOGGLEBIN, 1), None)
            t.createNextCover("1->0", CoverData(CoverTypeT.TOGGLEBIN, 1), None)

        toggles = list(inst.scopes(ScopeTypeT.TOGGLE))
        assert len(toggles) == 3
        names = {t.getScopeName() for t in toggles}
        assert names == {"sig_a", "sig_b", "sig_c"}
