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
Test FSM coverage across all backends.

Tests cover:
- Creating FSM scopes
- Creating states and transitions
- Querying state/transition counts and coverage
"""

import pytest
from ucis import *
from ucis.source_info import SourceInfo
from ucis.cover_data import CoverData
from ucis.scope_type_t import ScopeTypeT
from ucis.cover_type_t import CoverTypeT


class TestApiFSMCoverage:
    """Test FSM coverage operations"""

    def _make_inst(self, db):
        """Helper: build standard DU + instance hierarchy."""
        file_h = db.createFileHandle("design.v", "/rtl")
        du = db.createScope("work.module1", SourceInfo(file_h, 1, 0),
                            1, UCIS_VLOG, UCIS_DU_MODULE,
                            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst = db.createInstance("i_module1", None, 1, UCIS_VLOG,
                                 UCIS_INSTANCE, du, UCIS_INST_ONCE)
        return inst

    def test_create_fsm_scope(self, backend):
        """Test creating an FSM scope via createScope(FSM)"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        inst = self._make_inst(db)

        fsm = inst.createScope("state_machine", None, 1, UCIS_VLOG,
                               ScopeTypeT.FSM, UCIS_INST_ONCE)
        assert fsm is not None
        assert fsm.getScopeName() == "state_machine"
        assert fsm.getScopeType() == ScopeTypeT.FSM

    def test_fsm_create_states(self, backend):
        """Test creating FSM states"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support FSM scopes")

        db = create_db()
        inst = self._make_inst(db)
        fsm = inst.createScope("fsm1", None, 1, UCIS_VLOG,
                               ScopeTypeT.FSM, UCIS_INST_ONCE)

        fsm.createState("IDLE")
        fsm.createState("ACTIVE")
        fsm.createState("DONE")

        assert fsm.getNumStates() == 3

    def test_fsm_create_transitions(self, backend):
        """Test creating FSM transitions"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support FSM scopes")

        db = create_db()
        inst = self._make_inst(db)
        fsm = inst.createScope("fsm1", None, 1, UCIS_VLOG,
                               ScopeTypeT.FSM, UCIS_INST_ONCE)

        s_idle = fsm.createState("IDLE")
        s_active = fsm.createState("ACTIVE")
        s_done = fsm.createState("DONE")

        fsm.createTransition(s_idle, s_active)
        fsm.createTransition(s_active, s_done)
        fsm.createTransition(s_done, s_idle)

        assert fsm.getNumTransitions() == 3

    def test_fsm_create_next_transition(self, backend):
        """Test createNextTransition() auto-creating states"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support FSM scopes")

        db = create_db()
        inst = self._make_inst(db)
        fsm = inst.createScope("fsm1", None, 1, UCIS_VLOG,
                               ScopeTypeT.FSM, UCIS_INST_ONCE)

        # createNextTransition should create states implicitly
        fsm.createNextTransition("IDLE", "ACTIVE")
        fsm.createNextTransition("ACTIVE", "DONE")

        assert fsm.getNumStates() == 3  # IDLE, ACTIVE, DONE
        assert fsm.getNumTransitions() == 2

    def test_fsm_get_state_by_name(self, backend):
        """Test looking up a state by name"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support FSM scopes")

        db = create_db()
        inst = self._make_inst(db)
        fsm = inst.createScope("fsm1", None, 1, UCIS_VLOG,
                               ScopeTypeT.FSM, UCIS_INST_ONCE)

        fsm.createState("IDLE")
        fsm.createState("ACTIVE")

        s = fsm.getState("IDLE")
        assert s is not None
        assert s.getName() == "IDLE"

        s_missing = fsm.getState("NONEXISTENT")
        assert s_missing is None

    def test_fsm_iterate_states(self, backend):
        """Test iterating all FSM states"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support FSM scopes")

        db = create_db()
        inst = self._make_inst(db)
        fsm = inst.createScope("fsm1", None, 1, UCIS_VLOG,
                               ScopeTypeT.FSM, UCIS_INST_ONCE)

        for name in ["S0", "S1", "S2", "S3"]:
            fsm.createState(name)

        states = list(fsm.getStates())
        assert len(states) == 4
        names = {s.getName() for s in states}
        assert names == {"S0", "S1", "S2", "S3"}

    def test_fsm_iterate_transitions(self, backend):
        """Test iterating all FSM transitions"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support FSM scopes")

        db = create_db()
        inst = self._make_inst(db)
        fsm = inst.createScope("fsm1", None, 1, UCIS_VLOG,
                               ScopeTypeT.FSM, UCIS_INST_ONCE)

        s0 = fsm.createState("S0")
        s1 = fsm.createState("S1")
        s2 = fsm.createState("S2")
        fsm.createTransition(s0, s1)
        fsm.createTransition(s1, s2)
        fsm.createTransition(s2, s0)

        transitions = list(fsm.getTransitions())
        assert len(transitions) == 3

    def test_fsm_coverage_percent(self, backend):
        """Test FSM state/transition coverage percentage"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support FSM scopes")

        db = create_db()
        inst = self._make_inst(db)
        fsm = inst.createScope("fsm1", None, 1, UCIS_VLOG,
                               ScopeTypeT.FSM, UCIS_INST_ONCE)

        s0 = fsm.createState("S0")
        s1 = fsm.createState("S1")
        s2 = fsm.createState("S2")

        # Mark one state as visited
        s0.incrementCount(5)

        state_pct = fsm.getStateCoveragePercent()
        # 1 of 3 states covered = 33.3%
        assert 30.0 < state_pct < 40.0

    def test_fsm_scope_in_hierarchy(self, backend):
        """Test FSM scope appears in scope iteration"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support FSM scopes")

        db = create_db()
        inst = self._make_inst(db)
        inst.createScope("fsm_ctrl", None, 1, UCIS_VLOG,
                         ScopeTypeT.FSM, UCIS_INST_ONCE)
        inst.createScope("fsm_data", None, 1, UCIS_VLOG,
                         ScopeTypeT.FSM, UCIS_INST_ONCE)

        fsm_scopes = list(inst.scopes(ScopeTypeT.FSM))
        assert len(fsm_scopes) == 2
        names = {s.getScopeName() for s in fsm_scopes}
        assert names == {"fsm_ctrl", "fsm_data"}
