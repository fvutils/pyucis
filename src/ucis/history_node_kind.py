
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
from enum import IntEnum

class HistoryNodeKind(IntEnum):
    """History node type identifiers.
    
    Defines the types of history nodes in the UCIS database. History nodes
    track the provenance of coverage data, recording test runs and database
    merge operations.
    
    The history node tree represents the lineage of the coverage data:
    - **TEST nodes** are leaves representing individual test runs (primary data)
    - **MERGE nodes** are internal nodes representing database merge operations
    
    Each coverage database has a history tree showing which tests contributed
    to the final coverage and how databases were merged together. This enables
    traceability and regression analysis.
    
    History Node Types:
    
    - **NONE**: Uninitialized or invalid history node
    - **ALL**: Special value for iteration (matches all node types)
    - **TEST**: Leaf node representing a single test run
    - **MERGE**: Internal node representing a merge operation
    
    Example:
        >>> # Create test history node
        >>> test_node = db.createHistoryNode(
        ...     parent=None,
        ...     logicalName="regression_test_42",
        ...     physicalName="/results/test42.ucis",
        ...     kind=HistoryNodeKind.TEST)
        >>>
        >>> # Create merge node combining two tests
        >>> merge_node = db.createHistoryNode(
        ...     parent=None,
        ...     logicalName="merged_coverage",
        ...     physicalName="/results/merged.ucis",
        ...     kind=HistoryNodeKind.MERGE)
        >>>
        >>> # Iterate all history nodes
        >>> for node in db.historyNodes(HistoryNodeKind.ALL):
        ...     kind = node.getKind()
        ...     if kind == HistoryNodeKind.TEST:
        ...         print(f"Test: {node.getLogicalName()}")
        ...     elif kind == HistoryNodeKind.MERGE:
        ...         print(f"Merge: {node.getLogicalName()}")
        
    See Also:
        UCIS.createHistoryNode(): Create history nodes
        UCIS.historyNodes(): Iterate history nodes
        HistoryNode: History node class (if exists)
        UCIS LRM Section 4.13 "History Nodes"
        UCIS LRM Section 8.13 "History Node Management"
    """
    
    NONE  = -1
    """Uninitialized or invalid history node type."""
    
    ALL   =  0
    """
    Special value for iteration to match all history node types.
    
    Note:
        This is used as a filter parameter for iteration; no actual
        history node object has this type.
    """
    
    TEST  =  1
    """
    Test leaf node representing a single test run (primary database).
    
    Test nodes are the leaves of the history tree and represent the
    original coverage data collected from individual test runs. They
    contain test metadata such as command line, date, seed, username, etc.
    """
    
    MERGE =  2
    """
    Merge node representing a database merge operation.
    
    Merge nodes are internal nodes in the history tree that represent
    the combination of multiple coverage databases. They track which
    databases were merged and enable analysis of coverage contributions.
    """
    