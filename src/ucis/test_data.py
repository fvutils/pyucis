
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
Created on Jan 8, 2020

@author: ballance
'''

class TestData(object):
    """Test run metadata container.
    
    TestData encapsulates all metadata associated with a test run, including
    execution status, timing information, command line, environment details,
    and resource usage.
    
    This data is typically stored in history nodes of type TEST and provides
    complete traceability of test execution for regression analysis and
    coverage debugging.
    
    Attributes:
        teststatus (TestStatusT): Test execution status (OK, ERROR, etc.)
        toolcategory (str): Tool category identifier
        date (str): Test execution date/timestamp
        simtime (float): Simulation time in time units
        timeunit (str): Simulation time unit (e.g., "ns", "ps")
        runcwd (str): Working directory where test was run
        cputime (float): CPU time consumed by test
        seed (str): Random seed value used
        cmd (str): Command used to run test
        args (str): Command line arguments
        compulsory (int): Compulsory flag (0 or 1)
        user (str): Username who ran the test
        cost (float): Cost metric for test execution
        
    Example:
        >>> from ucis.test_status_t import TestStatusT
        >>> # Create test data for successful run
        >>> test_data = TestData(
        ...     teststatus=TestStatusT.OK,
        ...     toolcategory="simulator",
        ...     date="2024-01-15T10:30:00",
        ...     simtime=1000000.0,
        ...     timeunit="ns",
        ...     runcwd="/workspace/tests",
        ...     cputime=45.2,
        ...     seed="12345",
        ...     cmd="vsim",
        ...     args="-c -do run.do",
        ...     compulsory=1,
        ...     user="engineer",
        ...     cost=1.0)
        >>>
        >>> # Apply to history node
        >>> hist_node.setTestData(test_data)
        
    See Also:
        HistoryNode.setTestData(): Apply test data to history node
        TestStatusT: Test status enumeration
        HistoryNodeKind.TEST: Test history node type
        UCIS LRM Section 4.13 "History Nodes"
    """
    
    def __init__(self,
                 teststatus,
                 toolcategory : str,
                 date : str,
                 simtime : float = 0.0,
                 timeunit : str = "ns",
                 runcwd : str = ".",
                 cputime : float = 0.0,
                 seed : str = "0",
                 cmd : str = "",
                 args : str = "",
                 compulsory : int = 0,
                 user : str = "user",
                 cost : float = 0.0
                 ):
        """Create test metadata container.
        
        Args:
            teststatus: Test execution status (TestStatusT).
            toolcategory: Tool category string.
            date: Execution date/timestamp string.
            simtime: Simulation time value. Default 0.0.
            timeunit: Time unit string ("ns", "ps", etc.). Default "ns".
            runcwd: Working directory path. Default ".".
            cputime: CPU seconds consumed. Default 0.0.
            seed: Random seed string. Default "0".
            cmd: Command string. Default "".
            args: Arguments string. Default "".
            compulsory: Compulsory flag (0/1). Default 0.
            user: Username string. Default "user".
            cost: Cost metric. Default 0.0.
        """
        self.teststatus = teststatus
        self.simtime = simtime
        self.timeunit = timeunit
        self.runcwd = runcwd
        self.cputime = cputime
        self.seed = seed
        self.cmd = cmd 
        self.args = args 
        self.compulsory = compulsory
        self.date = date
        self.user = user
        self.cost = cost
        self.toolcategory = toolcategory
        