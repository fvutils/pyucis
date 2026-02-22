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
SQLite-backed FSM Coverage implementation with state and transition tracking
"""

from ucis.sqlite.sqlite_scope import SqliteScope
from ucis.cover_data import CoverData


class FSMState:
    """Represents an FSM state"""
    
    def __init__(self, fsm_scope, state_id: int, state_name: str, state_index: int,
                 cover_scope_id: int = None):
        self.fsm_scope = fsm_scope
        self.state_id = state_id
        self.state_name = state_name
        self.state_index = state_index
        # scope_id where the FSMBIN coveritem lives (FSM_STATES sub-scope per LRM)
        self._cover_scope_id = cover_scope_id if cover_scope_id is not None else fsm_scope.scope_id
    
    def getName(self) -> str:
        """Get state name"""
        return self.state_name
    
    def getIndex(self) -> int:
        """Get state index"""
        return self.state_index
    
    def getVisitCount(self) -> int:
        """Get number of times this state was visited"""
        cursor = self.fsm_scope.ucis_db.conn.execute(
            """SELECT cover_data FROM coveritems 
               WHERE scope_id = ? AND cover_name = ? AND cover_type & 0x800 != 0""",
            (self._cover_scope_id, self.state_name)
        )
        row = cursor.fetchone()
        return row[0] if row else 0

    def getCount(self) -> int:
        """Alias for getVisitCount."""
        return self.getVisitCount()

    def incrementCount(self, amt: int = 1):
        """Increment visit count by amt."""
        current = self.getVisitCount()
        self.fsm_scope.ucis_db.conn.execute(
            """UPDATE coveritems SET cover_data = ?
               WHERE scope_id = ? AND cover_name = ? AND cover_type & 0x800 != 0""",
            (current + amt, self._cover_scope_id, self.state_name)
        )

    def incrementVisitCount(self, amt: int = 1):
        """Alias for incrementCount."""
        self.incrementCount(amt)


class FSMTransition:
    """Represents an FSM state transition"""
    
    def __init__(self, fsm_scope, cover_id: int, from_state: FSMState, to_state: FSMState):
        self.fsm_scope = fsm_scope
        self.cover_id = cover_id
        self.from_state = from_state
        self.to_state = to_state
    
    def getFromState(self) -> FSMState:
        """Get source state"""
        return self.from_state
    
    def getToState(self) -> FSMState:
        """Get destination state"""
        return self.to_state
    
    def getName(self) -> str:
        """Get transition name"""
        return f"{self.from_state.getName()}->{self.to_state.getName()}"
    
    def getCount(self) -> int:
        """Get transition count"""
        cursor = self.fsm_scope.ucis_db.conn.execute(
            "SELECT cover_data FROM coveritems WHERE cover_id = ?",
            (self.cover_id,)
        )
        row = cursor.fetchone()
        return row[0] if row else 0
    
    def incrementCount(self, amt: int = 1):
        """Increment transition count"""
        current = self.getCount()
        self.fsm_scope.ucis_db.conn.execute(
            "UPDATE coveritems SET cover_data = ? WHERE cover_id = ?",
            (current + amt, self.cover_id)
        )


class SqliteFSMScope(SqliteScope):
    """FSM coverage scope with state and transition tracking.

    Per UCIS LRM section 6.5.6: a UCIS_FSM scope shall have exactly one
    UCIS_FSM_STATES child scope and one UCIS_FSM_TRANS child scope.
    FSMBIN coveritems are routed to those sub-scopes, not the FSM scope itself.
    """
    
    def __init__(self, ucis_db, scope_id: int):
        super().__init__(ucis_db, scope_id)
        self._states_cache = {}
        self._transitions_cache = {}
        self._states_scope_cache = None
        self._trans_scope_cache = None

    def _get_or_create_sub_scope(self, scope_type, scope_name):
        """Find existing or create the mandatory FSM sub-scope in the DB."""
        cursor = self.ucis_db.conn.execute(
            "SELECT scope_id FROM scopes WHERE parent_id = ? AND scope_type = ?",
            (self.scope_id, scope_type)
        )
        row = cursor.fetchone()
        if row:
            return SqliteScope(self.ucis_db, row[0])
        cursor = self.ucis_db.conn.execute(
            """INSERT INTO scopes (parent_id, scope_type, scope_name, scope_flags,
                                   weight, goal, source_file_id, source_line, source_token)
               VALUES (?, ?, ?, 0, 1, 100, NULL, -1, -1)""",
            (self.scope_id, scope_type, scope_name)
        )
        return SqliteScope(self.ucis_db, cursor.lastrowid)

    def _get_states_scope(self):
        """Return (and lazy-create) the FSM_STATES child scope."""
        from ucis.scope_type_t import ScopeTypeT
        if self._states_scope_cache is None:
            self._states_scope_cache = self._get_or_create_sub_scope(
                ScopeTypeT.FSM_STATES, "UCIS:STATE")
        return self._states_scope_cache

    def _get_trans_scope(self):
        """Return (and lazy-create) the FSM_TRANS child scope."""
        from ucis.scope_type_t import ScopeTypeT
        if self._trans_scope_cache is None:
            self._trans_scope_cache = self._get_or_create_sub_scope(
                ScopeTypeT.FSM_TRANS, "UCIS:TRANSITION")
        return self._trans_scope_cache

    def createNextCover(self, name, data, sourceinfo):
        """Route FSMBIN coveritems to the correct mandatory sub-scope."""
        if "->" in name:
            return self._get_trans_scope().createNextCover(name, data, sourceinfo)
        else:
            return self._get_states_scope().createNextCover(name, data, sourceinfo)
    
    def createState(self, state_name: str, state_index: int = None) -> FSMState:
        """Create a new FSM state"""
        # Auto-assign index if not provided
        if state_index is None:
            cursor = self.ucis_db.conn.execute(
                "SELECT MAX(state_index) FROM fsm_states WHERE scope_id = ?",
                (self.scope_id,)
            )
            row = cursor.fetchone()
            state_index = (row[0] + 1) if (row[0] is not None) else 0
        
        # Insert state
        cursor = self.ucis_db.conn.execute(
            """INSERT INTO fsm_states (scope_id, state_name, state_index)
               VALUES (?, ?, ?)""",
            (self.scope_id, state_name, state_index)
        )
        state_id = cursor.lastrowid
        
        # Create a coveritem for state visits (routes to FSM_STATES sub-scope)
        cover_data = CoverData(0x800, 0)  # FSMBIN type
        cover_data.data = 0
        state_cover = self.createNextCover(state_name, cover_data, None)
        
        # Create state object; coveritem lives in FSM_STATES sub-scope
        state = FSMState(self, state_id, state_name, state_index,
                         cover_scope_id=self._get_states_scope().scope_id)
        self._states_cache[state_name] = state
        
        return state
    
    def getState(self, state_name: str) -> FSMState:
        """Get state by name"""
        if state_name in self._states_cache:
            return self._states_cache[state_name]
        
        cursor = self.ucis_db.conn.execute(
            """SELECT state_id, state_index FROM fsm_states 
               WHERE scope_id = ? AND state_name = ?""",
            (self.scope_id, state_name)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
        
        state = FSMState(self, row[0], state_name, row[1],
                         cover_scope_id=self._get_states_scope().scope_id)
        self._states_cache[state_name] = state
        return state
    
    def getStates(self):
        """Iterate all states"""
        cursor = self.ucis_db.conn.execute(
            """SELECT state_id, state_name, state_index FROM fsm_states 
               WHERE scope_id = ?
               ORDER BY state_index""",
            (self.scope_id,)
        )
        
        for row in cursor:
            state_name = row[1]
            if state_name not in self._states_cache:
                self._states_cache[state_name] = FSMState(
                    self, row[0], state_name, row[2],
                    cover_scope_id=self._get_states_scope().scope_id)
            yield self._states_cache[state_name]
    
    def getNumStates(self) -> int:
        """Get number of states"""
        cursor = self.ucis_db.conn.execute(
            "SELECT COUNT(*) FROM fsm_states WHERE scope_id = ?",
            (self.scope_id,)
        )
        row = cursor.fetchone()
        return row[0] if row else 0
    
    def createTransition(self, from_state: FSMState, to_state: FSMState) -> FSMTransition:
        """Create a state transition"""
        trans_name = f"{from_state.getName()}->{to_state.getName()}"
        
        # Create coveritem for this transition
        cover_data = CoverData(0x800, 0)  # FSMBIN type
        cover_data.data = 0
        trans_cover = self.createNextCover(trans_name, cover_data, None)
        
        # Link to fsm_transitions table
        self.ucis_db.conn.execute(
            """INSERT INTO fsm_transitions (cover_id, from_state_id, to_state_id)
               VALUES (?, ?, ?)""",
            (trans_cover.cover_id, from_state.state_id, to_state.state_id)
        )
        
        # Create transition object
        transition = FSMTransition(self, trans_cover.cover_id, from_state, to_state)
        cache_key = (from_state.state_name, to_state.state_name)
        self._transitions_cache[cache_key] = transition
        
        return transition
    
    def getTransition(self, from_state: FSMState, to_state: FSMState) -> FSMTransition:
        """Get transition between two states"""
        cache_key = (from_state.state_name, to_state.state_name)
        if cache_key in self._transitions_cache:
            return self._transitions_cache[cache_key]
        
        # Query from database
        cursor = self.ucis_db.conn.execute(
            """SELECT ft.cover_id FROM fsm_transitions ft
               WHERE ft.from_state_id = ? AND ft.to_state_id = ?""",
            (from_state.state_id, to_state.state_id)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
        
        transition = FSMTransition(self, row[0], from_state, to_state)
        self._transitions_cache[cache_key] = transition
        return transition
    
    def getTransitions(self):
        """Iterate all transitions"""
        cursor = self.ucis_db.conn.execute(
            """SELECT ft.cover_id, ft.from_state_id, ft.to_state_id,
                      fs1.state_name, fs1.state_index,
                      fs2.state_name, fs2.state_index
               FROM fsm_transitions ft
               JOIN fsm_states fs1 ON ft.from_state_id = fs1.state_id
               JOIN fsm_states fs2 ON ft.to_state_id = fs2.state_id
               WHERE fs1.scope_id = ?""",
            (self.scope_id,)
        )
        
        for row in cursor:
            from_state = FSMState(self, row[1], row[3], row[4])
            to_state = FSMState(self, row[2], row[5], row[6])
            
            cache_key = (from_state.state_name, to_state.state_name)
            if cache_key not in self._transitions_cache:
                self._transitions_cache[cache_key] = FSMTransition(
                    self, row[0], from_state, to_state
                )
            
            yield self._transitions_cache[cache_key]
    
    def getNumTransitions(self) -> int:
        """Get number of transitions"""
        cursor = self.ucis_db.conn.execute(
            """SELECT COUNT(*) FROM fsm_transitions ft
               JOIN fsm_states fs ON ft.from_state_id = fs.state_id
               WHERE fs.scope_id = ?""",
            (self.scope_id,)
        )
        row = cursor.fetchone()
        return row[0] if row else 0
    
    def getStateCoveragePercent(self) -> float:
        """Get state coverage percentage (visited states / total states)"""
        total = self.getNumStates()
        if total == 0:
            return 0.0
        
        # Coveritems live in FSM_STATES sub-scope per LRM
        states_scope_id = self._get_states_scope().scope_id
        cursor = self.ucis_db.conn.execute(
            """SELECT COUNT(*) FROM fsm_states fs
               JOIN coveritems c ON c.scope_id = ? AND c.cover_name = fs.state_name
               WHERE fs.scope_id = ? AND c.cover_data > 0""",
            (states_scope_id, self.scope_id)
        )
        row = cursor.fetchone()
        visited = row[0] if row else 0
        
        return (100.0 * visited / total) if total > 0 else 0.0
    
    def getTransitionCoveragePercent(self) -> float:
        """Get transition coverage percentage"""
        total = self.getNumTransitions()
        if total == 0:
            return 0.0
        
        # Count transitions with count > 0
        cursor = self.ucis_db.conn.execute(
            """SELECT COUNT(*) FROM fsm_transitions ft
               JOIN fsm_states fs ON ft.from_state_id = fs.state_id
               JOIN coveritems c ON ft.cover_id = c.cover_id
               WHERE fs.scope_id = ? AND c.cover_data > 0""",
            (self.scope_id,)
        )
        row = cursor.fetchone()
        covered = row[0] if row else 0
        
        return (100.0 * covered / total) if total > 0 else 0.0

    def createNextTransition(self, from_state_name: str, to_state_name: str,
                             data=None, srcinfo=None):
        """Create an FSM transition cover item, creating states if needed."""
        from_state = self.getState(from_state_name)
        if from_state is None:
            from_state = self.createState(from_state_name)
        to_state = self.getState(to_state_name)
        if to_state is None:
            to_state = self.createState(to_state_name)
        return self.createTransition(from_state, to_state)
