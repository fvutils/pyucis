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
SQLite-backed HistoryNode implementation
"""

from ucis.history_node import HistoryNode
from ucis.history_node_kind import HistoryNodeKind
from ucis.test_status_t import TestStatusT
from ucis.sqlite.sqlite_obj import SqliteObj


class SqliteHistoryNode(SqliteObj, HistoryNode):
    """SQLite-backed history node (test record)"""
    
    def __init__(self, ucis_db, history_id: int):
        SqliteObj.__init__(self, ucis_db)
        HistoryNode.__init__(self)
        self.history_id = history_id
        self._loaded = False
        self._logical_name = None
        self._physical_name = None
        self._history_kind = None
        self._test_status = None
        self._parent_id = None
        
    def _ensure_loaded(self):
        """Lazy load history data from database"""
        if self._loaded:
            return
        
        cursor = self.ucis_db.conn.execute(
            """SELECT logical_name, physical_name, history_kind, test_status, parent_id
               FROM history_nodes WHERE history_id = ?""",
            (self.history_id,)
        )
        
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"History node {self.history_id} not found in database")
        
        self._logical_name = row[0]
        self._physical_name = row[1]
        self._history_kind = row[2]
        self._test_status = row[3]
        self._parent_id = row[4]
        
        self._loaded = True
    
    def _get_property_table(self):
        return 'history_properties'
    
    def _get_obj_id(self):
        return self.history_id
    
    def getParent(self):
        """Get parent history node"""
        self._ensure_loaded()
        if self._parent_id is not None:
            return SqliteHistoryNode(self.ucis_db, self._parent_id)
        return None
    
    def getLogicalName(self) -> str:
        """Get logical test name"""
        self._ensure_loaded()
        return self._logical_name
    
    def setLogicalName(self, name: str):
        """Set logical test name"""
        self._ensure_loaded()
        self._logical_name = name
        self.ucis_db.conn.execute(
            "UPDATE history_nodes SET logical_name = ? WHERE history_id = ?",
            (name, self.history_id)
        )
    
    def getPhysicalName(self) -> str:
        """Get physical test name"""
        self._ensure_loaded()
        return self._physical_name
    
    def setPhysicalName(self, name: str):
        """Set physical test name"""
        self._ensure_loaded()
        self._physical_name = name
        self.ucis_db.conn.execute(
            "UPDATE history_nodes SET physical_name = ? WHERE history_id = ?",
            (name, self.history_id)
        )
    
    def getKind(self) -> HistoryNodeKind:
        """Get history node kind"""
        self._ensure_loaded()
        return self._history_kind
    
    def getTestStatus(self) -> TestStatusT:
        """Get test status"""
        self._ensure_loaded()
        return self._test_status
    
    def setTestStatus(self, status: TestStatusT):
        """Set test status"""
        self._ensure_loaded()
        self._test_status = status
        self.ucis_db.conn.execute(
            "UPDATE history_nodes SET test_status = ? WHERE history_id = ?",
            (status, self.history_id)
        )
    
    def getSimTime(self) -> float:
        """Get simulation time"""
        cursor = self.ucis_db.conn.execute(
            "SELECT sim_time_low, sim_time_high FROM history_nodes WHERE history_id = ?",
            (self.history_id,)
        )
        row = cursor.fetchone()
        if row and row[0] is not None:
            # Reconstruct 64-bit value from two 32-bit values
            return float(row[0])  # Simplified for now
        return 0.0
    
    def setSimTime(self, time: float):
        """Set simulation time"""
        # Store as integer for now (simplified)
        self.ucis_db.conn.execute(
            "UPDATE history_nodes SET sim_time_low = ? WHERE history_id = ?",
            (int(time), self.history_id)
        )
    
    def getTimeUnit(self) -> str:
        """Get time unit"""
        cursor = self.ucis_db.conn.execute(
            "SELECT time_unit FROM history_nodes WHERE history_id = ?",
            (self.history_id,)
        )
        row = cursor.fetchone()
        return str(row[0]) if row and row[0] is not None else ""
    
    def setTimeUnit(self, unit: str):
        """Set time unit"""
        self.ucis_db.conn.execute(
            "UPDATE history_nodes SET time_unit = ? WHERE history_id = ?",
            (unit, self.history_id)
        )
    
    def getCpuTime(self) -> float:
        """Get CPU time"""
        cursor = self.ucis_db.conn.execute(
            "SELECT cpu_time FROM history_nodes WHERE history_id = ?",
            (self.history_id,)
        )
        row = cursor.fetchone()
        return row[0] if row and row[0] is not None else 0.0
    
    def setCpuTime(self, time: float):
        """Set CPU time"""
        self.ucis_db.conn.execute(
            "UPDATE history_nodes SET cpu_time = ? WHERE history_id = ?",
            (time, self.history_id)
        )
    
    def getSeed(self) -> str:
        """Get random seed"""
        cursor = self.ucis_db.conn.execute(
            "SELECT seed FROM history_nodes WHERE history_id = ?",
            (self.history_id,)
        )
        row = cursor.fetchone()
        return row[0] if row and row[0] is not None else ""
    
    def setSeed(self, seed: str):
        """Set random seed"""
        self.ucis_db.conn.execute(
            "UPDATE history_nodes SET seed = ? WHERE history_id = ?",
            (seed, self.history_id)
        )
    
    def getCmd(self) -> str:
        """Get command line"""
        cursor = self.ucis_db.conn.execute(
            "SELECT cmd_line FROM history_nodes WHERE history_id = ?",
            (self.history_id,)
        )
        row = cursor.fetchone()
        return row[0] if row and row[0] is not None else ""
    
    def setCmd(self, cmd: str):
        """Set command line"""
        self.ucis_db.conn.execute(
            "UPDATE history_nodes SET cmd_line = ? WHERE history_id = ?",
            (cmd, self.history_id)
        )
    
    def getDate(self) -> int:
        """Get test date"""
        cursor = self.ucis_db.conn.execute(
            "SELECT date FROM history_nodes WHERE history_id = ?",
            (self.history_id,)
        )
        row = cursor.fetchone()
        if row and row[0] is not None:
            # Try to parse as int first, otherwise return 0
            try:
                return int(row[0])
            except (ValueError, TypeError):
                return 0
        return 0
    
    def setDate(self, date: int):
        """Set test date"""
        self.ucis_db.conn.execute(
            "UPDATE history_nodes SET date = ? WHERE history_id = ?",
            (str(date), self.history_id)
        )
    
    def getUserName(self) -> str:
        """Get user name"""
        cursor = self.ucis_db.conn.execute(
            "SELECT user_name FROM history_nodes WHERE history_id = ?",
            (self.history_id,)
        )
        row = cursor.fetchone()
        return row[0] if row and row[0] is not None else ""
    
    def setUserName(self, user: str):
        """Set user name"""
        self.ucis_db.conn.execute(
            "UPDATE history_nodes SET user_name = ? WHERE history_id = ?",
            (user, self.history_id)
        )
    
    def getCost(self) -> int:
        """Get test cost"""
        cursor = self.ucis_db.conn.execute(
            "SELECT cost FROM history_nodes WHERE history_id = ?",
            (self.history_id,)
        )
        row = cursor.fetchone()
        return int(row[0]) if row and row[0] is not None else 0
    
    def setCost(self, cost: int):
        """Set test cost"""
        self.ucis_db.conn.execute(
            "UPDATE history_nodes SET cost = ? WHERE history_id = ?",
            (cost, self.history_id)
        )
    
    # Stub implementations for less common methods
    def getRunCwd(self) -> str:
        return ""
    
    def setRunCwd(self, cwd: str):
        pass
    
    def getArgs(self):
        return []
    
    def setArgs(self, args):
        pass
    
    def getCompulsory(self):
        return []
    
    def setCompulsory(self, compulsory):
        pass
    
    def getToolCategory(self) -> str:
        return ""
    
    def setToolCategory(self, category: str):
        pass
    
    def getUCISVersion(self) -> str:
        return "1.0"
    
    def getVendorId(self) -> str:
        return ""
    
    def setVendorId(self, tool: str):
        pass
    
    def getVendorTool(self) -> str:
        return ""
    
    def setVendorTool(self, tool: str):
        pass
    
    def getVendorToolVersion(self) -> str:
        return ""
    
    def setVendorToolVersion(self, version: str):
        pass
    
    def getSameTests(self) -> int:
        return 0
    
    def setSameTests(self, test_l: int):
        pass
    
    def getUserAttr(self):
        return None
    
    def getComment(self):
        return ""
    
    def setComment(self, comment):
        pass

    def getRealProperty(self, property):
        """Get a real-valued property by RealProperty enum."""
        from ucis.real_property import RealProperty
        if property == RealProperty.SIMTIME:
            return self.getSimTime()
        elif property == RealProperty.CPUTIME:
            return self.getCpuTime()
        elif property == RealProperty.COST:
            return 0.0
        return None

    def setRealProperty(self, property, value: float):
        """Set a real-valued property by RealProperty enum."""
        from ucis.real_property import RealProperty
        if property == RealProperty.SIMTIME:
            self.setSimTime(value)
        elif property == RealProperty.CPUTIME:
            self.setCpuTime(value)
