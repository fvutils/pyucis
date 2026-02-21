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

"""In-memory FSM coverage scope."""

from typing import Iterator
from ucis.mem.mem_scope import MemScope
from ucis.scope_type_t import ScopeTypeT
from ucis.int_property import IntProperty


class MemFSMState:
    """An FSM state with a name, optional numeric value, and visit count."""

    def __init__(self, name: str, index: int = None):
        self.name = name
        self.index = index if index is not None else 0
        self.visit_count = 0

    def getName(self) -> str:
        return self.name

    def getIndex(self) -> int:
        return self.index

    def getVisitCount(self) -> int:
        return self.visit_count

    def incrementVisitCount(self, amt: int = 1):
        self.visit_count += amt

    def incrementCount(self, amt: int = 1):
        """Alias for incrementVisitCount for API compatibility."""
        self.visit_count += amt

    def getCount(self) -> int:
        """Alias for getVisitCount for API compatibility."""
        return self.visit_count


class MemFSMTransition:
    """An FSM transition from one state to another with a traversal count."""

    def __init__(self, from_state: MemFSMState, to_state: MemFSMState):
        self.from_state = from_state
        self.to_state = to_state
        self.count = 0

    def getFromState(self) -> MemFSMState:
        return self.from_state

    def getToState(self) -> MemFSMState:
        return self.to_state

    def getName(self) -> str:
        return f"{self.from_state.name}->{self.to_state.name}"

    def getCount(self) -> int:
        return self.count

    def incrementCount(self, amt: int = 1):
        self.count += amt


class MemFSMScope(MemScope):
    """In-memory FSM coverage scope.

    Stores FSM states and transitions in memory. States and transitions
    are also reflected as FSMBIN cover items for compatibility with
    generic coverage iteration.
    """

    def __init__(self, parent, name, srcinfo, weight, source, flags=0):
        super().__init__(parent, name, srcinfo, weight, source,
                         ScopeTypeT.FSM, flags)
        self._states = {}         # name -> MemFSMState
        self._transitions = {}    # (from_name, to_name) -> MemFSMTransition

    # --- State API ---

    def createState(self, state_name: str,
                    state_index: int = None) -> MemFSMState:
        """Create an FSM state and a corresponding FSMBIN cover item."""
        if state_name in self._states:
            return self._states[state_name]

        idx = state_index if state_index is not None else len(self._states)
        state = MemFSMState(state_name, idx)
        self._states[state_name] = state

        # Create a FSMBIN cover item so generic iteration works
        from ucis.cover_data import CoverData
        from ucis.cover_type_t import CoverTypeT
        cd = CoverData(CoverTypeT.FSMBIN, 0)
        self.createNextCover(state_name, cd, None)

        return state

    def getState(self, state_name: str) -> MemFSMState:
        return self._states.get(state_name)

    def getStates(self) -> Iterator[MemFSMState]:
        return iter(self._states.values())

    def getNumStates(self) -> int:
        return len(self._states)

    # --- Transition API ---

    def createTransition(self, from_state: MemFSMState,
                         to_state: MemFSMState) -> MemFSMTransition:
        """Create an FSM transition and a corresponding FSMBIN cover item."""
        key = (from_state.name, to_state.name)
        if key in self._transitions:
            return self._transitions[key]

        trans = MemFSMTransition(from_state, to_state)
        self._transitions[key] = trans

        from ucis.cover_data import CoverData
        from ucis.cover_type_t import CoverTypeT
        cd = CoverData(CoverTypeT.FSMBIN, 0)
        self.createNextCover(trans.getName(), cd, None)

        return trans

    def getTransition(self, from_state: MemFSMState,
                      to_state: MemFSMState) -> MemFSMTransition:
        key = (from_state.name, to_state.name)
        return self._transitions.get(key)

    def getTransitions(self) -> Iterator[MemFSMTransition]:
        return iter(self._transitions.values())

    def getNumTransitions(self) -> int:
        return len(self._transitions)

    # --- Coverage metrics ---

    def getStateCoveragePercent(self) -> float:
        """Return percentage of states visited at least once."""
        if not self._states:
            return 0.0
        visited = sum(1 for s in self._states.values() if s.visit_count > 0)
        return 100.0 * visited / len(self._states)

    def getTransitionCoveragePercent(self) -> float:
        """Return percentage of transitions traversed at least once."""
        if not self._transitions:
            return 0.0
        traversed = sum(1 for t in self._transitions.values() if t.count > 0)
        return 100.0 * traversed / len(self._transitions)

    # --- createNextTransition helper ---

    def createNextTransition(self, from_state_name: str, to_state_name: str,
                             data=None, srcinfo=None):
        """Convenience: create states if needed, then create the transition."""
        from_state = self._states.get(from_state_name) or self.createState(from_state_name)
        to_state = self._states.get(to_state_name) or self.createState(to_state_name)
        return self.createTransition(from_state, to_state)

    # --- IntProperty ---

    def getIntProperty(self, coverindex, property):
        if property == IntProperty.FSM_STATEVAL:
            # Return index of state at coverindex if it is a state bin
            items = list(self.m_cover_items)
            if 0 <= coverindex < len(items):
                name = items[coverindex].m_name
                state = self._states.get(name)
                if state:
                    return state.index
        return super().getIntProperty(coverindex, property)
