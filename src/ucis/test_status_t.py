
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
Created on Jan 9, 2020

@author: ballance
'''
from enum import IntEnum, auto

class TestStatusT(IntEnum):
    """Test execution status enumeration.
    
    Defines the execution status of a test run recorded in a history node.
    The status indicates whether the test completed successfully or encountered
    errors, warnings, or other exceptional conditions.
    
    Test status helps identify:
    - Successfully completed tests (OK)
    - Tests with warnings or errors
    - Fatal test failures
    - Missing or incomplete test data
    - Data inconsistencies from merging
    
    Status values typically correspond to SystemVerilog severity system tasks
    ($warning, $error, $fatal) and test infrastructure states.
    
    Example:
        >>> # Check test status from history node
        >>> status = test_node.getTestStatus()
        >>> if status == TestStatusT.OK:
        ...     print("Test passed successfully")
        >>> elif status == TestStatusT.WARNING:
        ...     print("Test completed with warnings")
        >>> elif status == TestStatusT.ERROR:
        ...     print("Test had errors")
        >>> elif status == TestStatusT.FATAL:
        ...     print("Test failed fatally")
        >>>
        >>> # Set test status
        >>> test_node.setTestStatus(TestStatusT.OK)
        >>>
        >>> # Filter for passing tests
        >>> passing_tests = [node for node in db.historyNodes()
        ...                  if node.getTestStatus() == TestStatusT.OK]
        
    See Also:
        HistoryNode: History node with test status (if class exists)
        HistoryNodeKind.TEST: Test history node type
        UCIS.createHistoryNode(): Create history nodes with status
        UCIS LRM Section 4.13 "History Nodes"
    """
    
    OK = auto()
    """
    Test completed successfully without errors or warnings.
    
    Indicates normal test completion with no issues detected.
    """
    
    WARNING = auto()
    """
    Test completed with warnings.
    
    Corresponds to SystemVerilog $warning system task calls. The test
    ran to completion but encountered non-fatal issues that should be
    reviewed.
    """
    
    ERROR = auto()
    """
    Test encountered errors.
    
    Corresponds to SystemVerilog $error system task calls. The test
    detected errors but may have continued execution. Results may be
    suspect.
    """
    
    FATAL = auto()
    """
    Test failed with fatal error.
    
    Corresponds to SystemVerilog $fatal system task calls. The test
    terminated abnormally due to a critical failure. Coverage data
    may be incomplete or invalid.
    """
    
    MISSING = auto()
    """
    Test has not been run yet or data is missing.
    
    Indicates that the test is planned or expected but coverage data
    has not been collected yet. Used in regression tracking.
    """
    
    MERGE_ERROR = auto()
    """
    Test data record was merged with inconsistent data values.
    
    Indicates that during database merging, conflicting or inconsistent
    data was encountered for this test. The merged results may not be
    reliable and should be investigated.
    """
