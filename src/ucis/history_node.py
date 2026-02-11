from ucis.test_status_t import TestStatusT
from ucis.history_node_kind import HistoryNodeKind

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

'''
Created on Jan 5, 2020

@author: ballance
'''
from ucis.unimpl_error import UnimplError
from ucis.test_data import TestData
from ucis.obj import Obj
from ucis.int_property import IntProperty

class HistoryNode(Obj):
    """History node tracking test runs and merge operations.
    
    HistoryNode represents a node in the coverage database history tree. History
    nodes track the provenance of coverage data, recording:
    - Individual test runs (TEST nodes) with complete execution metadata
    - Database merge operations (MERGE nodes) combining multiple sources
    
    The history tree enables:
    - Traceability of which tests contributed to coverage
    - Regression analysis and test filtering
    - Coverage attribution and debugging
    - Merge tracking for database composition
    
    Each TEST history node contains comprehensive test metadata including
    execution status, timing, command line, seed, user, and resource usage.
    
    History nodes extend Obj, so they support the property interface for
    additional metadata storage.
    
    Example:
        >>> from ucis.test_status_t import TestStatusT
        >>> from ucis.test_data import TestData
        >>> 
        >>> # Create test history node
        >>> test = db.createHistoryNode(
        ...     parent=None,
        ...     logicalName="test_basic",
        ...     physicalName="/results/test_basic.ucis",
        ...     kind=HistoryNodeKind.TEST)
        >>>
        >>> # Set test metadata
        >>> test_data = TestData(
        ...     teststatus=TestStatusT.OK,
        ...     toolcategory="simulator",
        ...     date="2024-01-15",
        ...     seed="12345")
        >>> test.setTestData(test_data)
        >>>
        >>> # Query test info
        >>> status = test.getTestStatus()
        >>> seed = test.getSeed()
        >>> cmd = test.getCmd()
        
    See Also:
        UCIS.createHistoryNode(): Create history nodes
        HistoryNodeKind: Node type enumeration
        TestStatusT: Test status values
        TestData: Test metadata container
        UCIS LRM Section 4.13 "History Nodes"
        UCIS LRM Section 8.13 "History Node Management"
    """
    
    def __init__(self):
        super().__init__()
    
    def setTestData(self, testdata : TestData):
        """Set test metadata from TestData object.
        
        Convenience method to set all test-related fields from a TestData
        object in one call. Calls individual setters for each field.
        
        Args:
            testdata: TestData object containing test metadata.
            
        Example:
            >>> test_data = TestData(
            ...     teststatus=TestStatusT.OK,
            ...     toolcategory="simulator",
            ...     date="2024-01-15",
            ...     seed="12345")
            >>> hist_node.setTestData(test_data)
            
        See Also:
            TestData: Test metadata container
        """
        self.setTestStatus(testdata.teststatus)
        self.setToolCategory(testdata.toolcategory)
        self.setDate(testdata.date)
        self.setSimTime(testdata.simtime)
        self.setTimeUnit(testdata.timeunit)
        self.setRunCwd(testdata.runcwd)
        self.setCpuTime(testdata.cputime)
        self.setSeed(testdata.seed)
        self.setCmd(testdata.cmd)
        self.setArgs(testdata.args)
        self.setCompulsory(testdata.compulsory)
        self.setUserName(testdata.user)
        self.setCost(testdata.cost)
   
    # Note: This class has 30+ getter/setter methods for history node metadata.
    # Key methods include:
    # - getLogicalName/setLogicalName: Node identifier
    # - getPhysicalName/setPhysicalName: Database file path
    # - getKind: Node type (TEST or MERGE)
    # - getTestStatus/setTestStatus: Test execution status
    # - getSimTime/setSimTime, getTimeUnit/setTimeUnit: Simulation timing
    # - getRunCwd/setRunCwd: Working directory
    # - getCpuTime/setCpuTime: CPU time consumed
    # - getSeed/setSeed: Random seed
    # - getCmd/setCmd, getArgs/setArgs: Command and arguments
    # - getDate/setDate: Execution date
    # - getUserName/setUserName: User who ran test
    # - getVendorId/setVendorId, getVendorTool/setVendorTool: Tool info
    # - getComment/setComment: Descriptive comment
    #
    # All getters raise UnimplError if not implemented by backend.
    # See implementation for full method signatures.
   
    def getUserAttr(self):
        raise UnimplError()
    
    def getParent(self):
        raise UnimplError()
    
    def getLogicalName(self) -> str:
        raise UnimplError()
    
    def setLogicalName(self, name : str):
        raise UnimplError()
    
    def getPhysicalName(self) -> str:
        raise UnimplError()
    
    def setPhysicalName(self, name : str):
        raise UnimplError()
    
    def getKind(self) -> HistoryNodeKind:
        raise UnimplError()
    
    def getTestStatus(self) -> TestStatusT:
        raise UnimplError()
    
    def setTestStatus(self, status : TestStatusT):
        raise UnimplError()
    
    def getSimTime(self) -> float:
        raise UnimplError()
    
    def setSimTime(self, time : float):
        raise UnimplError()
    
    def getTimeUnit(self) -> str:
        raise UnimplError()
    
    def setTimeUnit(self, unit : str):
        raise UnimplError()
    
    def getRunCwd(self) -> str:
        raise UnimplError()
    
    def setRunCwd(self, cwd : str):
        raise UnimplError()
    
    def getCpuTime(self) -> float:
        raise UnimplError()
    
    def setCpuTime(self, time : float):
        raise UnimplError()
    
    def getSeed(self) -> str:
        raise UnimplError()
    
    def setSeed(self, seed : str):
        raise UnimplError()
    
    def getCmd(self) -> str:
        raise UnimplError()
    
    def setCmd(self, cmd : str):
        raise UnimplError()
    
    def getArgs(self) -> [str]:
        raise UnimplError()
    
    def setArgs(self, args : [str]):
        raise UnimplError()
    
    def getCompulsory(self) -> [str]:
        raise UnimplError()
    
    def setCompulsory(self, compulsory : [str]):
        raise UnimplError()
    
    def getDate(self)->int:
        raise UnimplError()
    
    def setDate(self, date : int):
        raise UnimplError()
    
    def getUserName(self) -> str:
        raise UnimplError()
    
    def setUserName(self, user : str):
        raise UnimplError()
    
    def getCost(self) -> int:
        raise UnimplError()
    
    def setCost(self, cost : int):
        raise UnimplError()
    
    def getToolCategory(self) -> str:
        raise UnimplError()
    
    def setToolCategory(self, category : str):
        raise UnimplError()
    
    def getUCISVersion(self) -> str:
        raise UnimplError()
    
    def getVendorId(self) -> str:
        raise UnimplError()
    
    def setVendorId(self, tool : str):
        raise UnimplError()
    
    def getVendorTool(self) -> str:
        raise UnimplError()
    
    def setVendorTool(self, tool : str):
        raise UnimplError()
    
    def getVendorToolVersion(self) -> str:
        raise UnimplError()
    
    def setVendorToolVersion(self, version : str):
        raise UnimplError()
    
    def getSameTests(self) -> int:
        raise UnimplError()
    
    def setSameTests(self, test_l : int):
        raise UnimplError()
    
    def getComment(self):
        raise UnimplError()
    
    def setComment(self, comment):
        raise UnimplError()
        
        
        
    
