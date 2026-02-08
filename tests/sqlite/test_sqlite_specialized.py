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
Tests for specialized SQLite scope types (Toggle, FSM, Cross)
"""

import unittest
import tempfile
import os

from ucis.sqlite import SqliteUCIS, SqliteToggleScope, SqliteFSMScope, SqliteCross
from ucis.scope_type_t import ScopeTypeT
from ucis.source_t import SourceT
from ucis.cover_data import CoverData


class TestSqliteToggle(unittest.TestCase):
    """Tests for toggle coverage"""
    
    def test_create_toggle_scope(self):
        """Test creating a toggle scope"""
        ucis = SqliteUCIS()
        
        top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        toggle = top.createScope("clk_toggle", None, 1, SourceT.NONE, ScopeTypeT.TOGGLE, 0)
        
        # Convert to toggle scope
        toggle_scope = SqliteToggleScope(ucis, toggle.scope_id)
        
        self.assertIsNotNone(toggle_scope)
        self.assertEqual(toggle_scope.getScopeType(), ScopeTypeT.TOGGLE)
        
        ucis.close()
    
    def test_toggle_bit_tracking(self):
        """Test per-bit toggle tracking"""
        ucis = SqliteUCIS()
        
        top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        toggle = top.createScope("data_toggle", None, 1, SourceT.NONE, ScopeTypeT.TOGGLE, 0)
        toggle_scope = SqliteToggleScope(ucis, toggle.scope_id)
        
        # Create 8-bit signal
        toggle_scope.setNumBits(8)
        for i in range(8):
            toggle_scope.createBit(i)
        
        self.assertEqual(toggle_scope.getNumBits(), 8)
        
        ucis.close()
    
    def test_toggle_transitions(self):
        """Test toggle transition tracking"""
        ucis = SqliteUCIS()
        
        top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        toggle = top.createScope("sig_toggle", None, 1, SourceT.NONE, ScopeTypeT.TOGGLE, 0)
        toggle_scope = SqliteToggleScope(ucis, toggle.scope_id)
        
        # Create 4-bit signal
        for i in range(4):
            bit = toggle_scope.createBit(i)
            
            # Set toggle counts
            bit.setToggle01(10 + i)
            bit.setToggle10(20 + i)
        
        # Verify
        bit0 = toggle_scope.getBit(0)
        self.assertEqual(bit0.getToggle01(), 10)
        self.assertEqual(bit0.getToggle10(), 20)
        
        bit3 = toggle_scope.getBit(3)
        self.assertEqual(bit3.getToggle01(), 13)
        self.assertEqual(bit3.getToggle10(), 23)
        
        ucis.close()
    
    def test_toggle_increment(self):
        """Test incrementing toggle counts"""
        ucis = SqliteUCIS()
        
        top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        toggle = top.createScope("clk", None, 1, SourceT.NONE, ScopeTypeT.TOGGLE, 0)
        toggle_scope = SqliteToggleScope(ucis, toggle.scope_id)
        
        bit = toggle_scope.createBit(0)
        
        # Increment transitions
        bit.incrementToggle01(5)
        bit.incrementToggle10(3)
        
        self.assertEqual(bit.getToggle01(), 5)
        self.assertEqual(bit.getToggle10(), 3)
        
        # Increment again
        bit.incrementToggle01()
        bit.incrementToggle10(2)
        
        self.assertEqual(bit.getToggle01(), 6)
        self.assertEqual(bit.getToggle10(), 5)
        
        ucis.close()
    
    def test_toggle_coverage_calculation(self):
        """Test toggle coverage percentage calculation"""
        ucis = SqliteUCIS()
        
        top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        toggle = top.createScope("data", None, 1, SourceT.NONE, ScopeTypeT.TOGGLE, 0)
        toggle_scope = SqliteToggleScope(ucis, toggle.scope_id)
        
        # Create 4 bits, toggle 3 of them completely
        for i in range(4):
            bit = toggle_scope.createBit(i)
            if i < 3:  # Toggle first 3 bits
                bit.setToggle01(10)
                bit.setToggle10(10)
        
        # 3 out of 4 bits fully toggled = 75%
        coverage = toggle_scope.getCoveragePercent()
        self.assertEqual(coverage, 75.0)
        
        ucis.close()
    
    def test_toggle_iteration(self):
        """Test iterating toggle bits"""
        ucis = SqliteUCIS()
        
        top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        toggle = top.createScope("bus", None, 1, SourceT.NONE, ScopeTypeT.TOGGLE, 0)
        toggle_scope = SqliteToggleScope(ucis, toggle.scope_id)
        
        # Create bits
        for i in range(3):
            bit = toggle_scope.createBit(i)
            bit.setToggle01(i * 10)
        
        # Iterate
        bits = list(toggle_scope.getBits())
        self.assertEqual(len(bits), 3)
        self.assertEqual(bits[0].getToggle01(), 0)
        self.assertEqual(bits[1].getToggle01(), 10)
        self.assertEqual(bits[2].getToggle01(), 20)
        
        ucis.close()


class TestSqliteFSM(unittest.TestCase):
    """Tests for FSM coverage"""
    
    def test_create_fsm_scope(self):
        """Test creating FSM scope"""
        ucis = SqliteUCIS()
        
        top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        fsm = top.createScope("state_machine", None, 1, SourceT.NONE, ScopeTypeT.FSM, 0)
        fsm_scope = SqliteFSMScope(ucis, fsm.scope_id)
        
        self.assertIsNotNone(fsm_scope)
        self.assertEqual(fsm_scope.getScopeType(), ScopeTypeT.FSM)
        
        ucis.close()
    
    def test_fsm_states(self):
        """Test FSM state creation and tracking"""
        ucis = SqliteUCIS()
        
        top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        fsm = top.createScope("controller", None, 1, SourceT.NONE, ScopeTypeT.FSM, 0)
        fsm_scope = SqliteFSMScope(ucis, fsm.scope_id)
        
        # Create states
        idle = fsm_scope.createState("IDLE", 0)
        active = fsm_scope.createState("ACTIVE", 1)
        error = fsm_scope.createState("ERROR", 2)
        
        self.assertEqual(idle.getName(), "IDLE")
        self.assertEqual(active.getName(), "ACTIVE")
        self.assertEqual(error.getName(), "ERROR")
        
        self.assertEqual(fsm_scope.getNumStates(), 3)
        
        ucis.close()
    
    def test_fsm_transitions(self):
        """Test FSM transition creation"""
        ucis = SqliteUCIS()
        
        top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        fsm = top.createScope("fsm", None, 1, SourceT.NONE, ScopeTypeT.FSM, 0)
        fsm_scope = SqliteFSMScope(ucis, fsm.scope_id)
        
        # Create states
        s0 = fsm_scope.createState("S0", 0)
        s1 = fsm_scope.createState("S1", 1)
        s2 = fsm_scope.createState("S2", 2)
        
        # Create transitions
        trans01 = fsm_scope.createTransition(s0, s1)
        trans12 = fsm_scope.createTransition(s1, s2)
        trans20 = fsm_scope.createTransition(s2, s0)
        
        self.assertEqual(trans01.getName(), "S0->S1")
        self.assertEqual(fsm_scope.getNumTransitions(), 3)
        
        ucis.close()
    
    def test_fsm_transition_counts(self):
        """Test FSM transition counting"""
        ucis = SqliteUCIS()
        
        top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        fsm = top.createScope("fsm", None, 1, SourceT.NONE, ScopeTypeT.FSM, 0)
        fsm_scope = SqliteFSMScope(ucis, fsm.scope_id)
        
        # Create states and transitions
        idle = fsm_scope.createState("IDLE")
        run = fsm_scope.createState("RUN")
        trans = fsm_scope.createTransition(idle, run)
        
        # Initially zero
        self.assertEqual(trans.getCount(), 0)
        
        # Increment
        trans.incrementCount(10)
        self.assertEqual(trans.getCount(), 10)
        
        trans.incrementCount(5)
        self.assertEqual(trans.getCount(), 15)
        
        ucis.close()
    
    def test_fsm_state_iteration(self):
        """Test iterating FSM states"""
        ucis = SqliteUCIS()
        
        top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        fsm = top.createScope("fsm", None, 1, SourceT.NONE, ScopeTypeT.FSM, 0)
        fsm_scope = SqliteFSMScope(ucis, fsm.scope_id)
        
        # Create states
        for name in ["A", "B", "C", "D"]:
            fsm_scope.createState(name)
        
        # Iterate
        states = list(fsm_scope.getStates())
        self.assertEqual(len(states), 4)
        state_names = [s.getName() for s in states]
        self.assertEqual(state_names, ["A", "B", "C", "D"])
        
        ucis.close()
    
    def test_fsm_coverage_percent(self):
        """Test FSM coverage percentage calculation"""
        ucis = SqliteUCIS()
        
        top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        fsm = top.createScope("fsm", None, 1, SourceT.NONE, ScopeTypeT.FSM, 0)
        fsm_scope = SqliteFSMScope(ucis, fsm.scope_id)
        
        # Create states
        s0 = fsm_scope.createState("S0")
        s1 = fsm_scope.createState("S1")
        s2 = fsm_scope.createState("S2")
        
        # Create and hit some transitions
        t01 = fsm_scope.createTransition(s0, s1)
        t12 = fsm_scope.createTransition(s1, s2)
        t20 = fsm_scope.createTransition(s2, s0)
        
        # Hit 2 out of 3 transitions
        t01.incrementCount(5)
        t12.incrementCount(3)
        
        # Should be 66.67% transition coverage
        trans_cov = fsm_scope.getTransitionCoveragePercent()
        self.assertAlmostEqual(trans_cov, 66.67, places=1)
        
        ucis.close()


class TestSqliteCross(unittest.TestCase):
    """Tests for cross coverage"""
    
    def test_create_cross(self):
        """Test creating cross scope"""
        ucis = SqliteUCIS()
        
        cg = ucis.createScope("cg", None, 1, SourceT.NONE, ScopeTypeT.COVERGROUP, 0)
        cross = cg.createScope("addr_x_data", None, 1, SourceT.NONE, ScopeTypeT.CROSS, 0)
        cross_scope = SqliteCross(ucis, cross.scope_id)
        
        self.assertIsNotNone(cross_scope)
        self.assertEqual(cross_scope.getScopeType(), ScopeTypeT.CROSS)
        
        ucis.close()
    
    def test_cross_add_coverpoints(self):
        """Test adding coverpoints to cross"""
        ucis = SqliteUCIS()
        
        cg = ucis.createScope("cg", None, 1, SourceT.NONE, ScopeTypeT.COVERGROUP, 0)
        
        # Create coverpoints
        addr_cp = cg.createScope("addr_cp", None, 1, SourceT.NONE, ScopeTypeT.COVERPOINT, 0)
        data_cp = cg.createScope("data_cp", None, 1, SourceT.NONE, ScopeTypeT.COVERPOINT, 0)
        
        # Create cross
        cross = cg.createScope("cross", None, 1, SourceT.NONE, ScopeTypeT.CROSS, 0)
        cross_scope = SqliteCross(ucis, cross.scope_id)
        
        # Add coverpoints
        cross_scope.addCoverpoint(addr_cp, 0)
        cross_scope.addCoverpoint(data_cp, 1)
        
        self.assertEqual(cross_scope.getNumCoverpoints(), 2)
        
        ucis.close()
    
    def test_cross_cartesian_product(self):
        """Test generating Cartesian product for cross"""
        ucis = SqliteUCIS()
        
        cg = ucis.createScope("cg", None, 1, SourceT.NONE, ScopeTypeT.COVERGROUP, 0)
        
        # Create coverpoints with bins
        addr_cp = cg.createScope("addr", None, 1, SourceT.NONE, ScopeTypeT.COVERPOINT, 0)
        for name in ["low", "high"]:
            cover_data = CoverData(0x01, 0)
            addr_cp.createNextCover(name, cover_data, None)
        
        data_cp = cg.createScope("data", None, 1, SourceT.NONE, ScopeTypeT.COVERPOINT, 0)
        for name in ["zero", "one", "max"]:
            cover_data = CoverData(0x01, 0)
            data_cp.createNextCover(name, cover_data, None)
        
        # Create cross
        cross = cg.createScope("cross", None, 1, SourceT.NONE, ScopeTypeT.CROSS, 0)
        cross_scope = SqliteCross(ucis, cross.scope_id)
        
        cross_scope.addCoverpoint(addr_cp, 0)
        cross_scope.addCoverpoint(data_cp, 1)
        
        # Generate Cartesian product: 2 x 3 = 6 bins
        num_created = cross_scope.generateCartesianProduct()
        self.assertEqual(num_created, 6)
        
        # Verify bins exist
        bins = list(cross_scope.coverItems(-1))
        self.assertEqual(len(bins), 6)
        
        bin_names = [b.getName() for b in bins]
        self.assertIn("<low,zero>", bin_names)
        self.assertIn("<high,max>", bin_names)
        
        ucis.close()
    
    def test_cross_bin_increment(self):
        """Test incrementing specific cross bins"""
        ucis = SqliteUCIS()
        
        cg = ucis.createScope("cg", None, 1, SourceT.NONE, ScopeTypeT.COVERGROUP, 0)
        
        # Create simple 2x2 cross
        cp1 = cg.createScope("cp1", None, 1, SourceT.NONE, ScopeTypeT.COVERPOINT, 0)
        for name in ["a", "b"]:
            cp1.createNextCover(name, CoverData(0x01, 0), None)
        
        cp2 = cg.createScope("cp2", None, 1, SourceT.NONE, ScopeTypeT.COVERPOINT, 0)
        for name in ["x", "y"]:
            cp2.createNextCover(name, CoverData(0x01, 0), None)
        
        cross = cg.createScope("cross", None, 1, SourceT.NONE, ScopeTypeT.CROSS, 0)
        cross_scope = SqliteCross(ucis, cross.scope_id)
        
        cross_scope.addCoverpoint(cp1, 0)
        cross_scope.addCoverpoint(cp2, 1)
        cross_scope.generateCartesianProduct()
        
        # Increment specific combinations
        cross_scope.incrementCrossBin(["a", "x"], 5)
        cross_scope.incrementCrossBin(["b", "y"], 10)
        
        # Verify
        bin_ax = cross_scope.getCrossBinByCombo(["a", "x"])
        self.assertEqual(bin_ax.getCoverData().data, 5)
        
        bin_by = cross_scope.getCrossBinByCombo(["b", "y"])
        self.assertEqual(bin_by.getCoverData().data, 10)
        
        ucis.close()
    
    def test_cross_coverage_percent(self):
        """Test cross coverage percentage"""
        ucis = SqliteUCIS()
        
        cg = ucis.createScope("cg", None, 1, SourceT.NONE, ScopeTypeT.COVERGROUP, 0)
        
        # Create 2x2 cross
        cp1 = cg.createScope("cp1", None, 1, SourceT.NONE, ScopeTypeT.COVERPOINT, 0)
        for name in ["a", "b"]:
            cp1.createNextCover(name, CoverData(0x01, 0), None)
        
        cp2 = cg.createScope("cp2", None, 1, SourceT.NONE, ScopeTypeT.COVERPOINT, 0)
        for name in ["x", "y"]:
            cp2.createNextCover(name, CoverData(0x01, 0), None)
        
        cross = cg.createScope("cross", None, 1, SourceT.NONE, ScopeTypeT.CROSS, 0)
        cross_scope = SqliteCross(ucis, cross.scope_id)
        
        cross_scope.addCoverpoint(cp1, 0)
        cross_scope.addCoverpoint(cp2, 1)
        cross_scope.generateCartesianProduct()
        
        # Hit 3 out of 4 bins
        cross_scope.incrementCrossBin(["a", "x"], 1)
        cross_scope.incrementCrossBin(["a", "y"], 1)
        cross_scope.incrementCrossBin(["b", "x"], 1)
        
        # Should be 75%
        coverage = cross_scope.getCoveragePercent()
        self.assertEqual(coverage, 75.0)
        
        ucis.close()


if __name__ == '__main__':
    unittest.main()
