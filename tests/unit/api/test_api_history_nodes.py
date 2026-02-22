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
Test history node (test data) properties across all backends.

Tests cover:
- Creating history nodes with test data
- Setting/getting simtime, CPU time, and other properties
- RealProperty API (SIMTIME, CPUTIME)
- IntProperty API on history nodes
"""

import pytest
from ucis import *
from ucis.test_data import TestData
from ucis.real_property import RealProperty


class TestApiHistoryNodes:
    """Test history node and test data properties"""

    def test_create_test_node(self, backend):
        """Test creating a test history node"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        node = db.createHistoryNode(None, "mytest", "mytest.db",
                                    UCIS_HISTORYNODE_TEST)
        assert node is not None

    def test_test_node_with_test_data(self, backend):
        """Test setting test data on a history node"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        node = db.createHistoryNode(None, "run1", "run1.db",
                                    UCIS_HISTORYNODE_TEST)
        node.setTestData(TestData(
            teststatus=UCIS_TESTSTATUS_OK,
            toolcategory="vcs",
            date="20240101120000"
        ))

        assert node.getTestStatus() == UCIS_TESTSTATUS_OK

    def test_sim_time_property(self, backend):
        """Test setting/getting sim time via RealProperty"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        node = db.createHistoryNode(None, "run1", "run1.db",
                                    UCIS_HISTORYNODE_TEST)
        node.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                  toolcategory="vcs", date="20240101000000"))
        node.setSimTime(1234.0)

        assert node.getSimTime() == pytest.approx(1234.0)

    def test_real_property_simtime(self, backend):
        """Test RealProperty.SIMTIME get/set"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend doesn't support RealProperty API")

        db = create_db()
        node = db.createHistoryNode(None, "run1", "run1.db",
                                    UCIS_HISTORYNODE_TEST)
        node.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                  toolcategory="vcs", date="20240101000000"))

        node.setRealProperty(RealProperty.SIMTIME, 9999.0)
        val = node.getRealProperty(RealProperty.SIMTIME)
        assert val == pytest.approx(9999.0)

    def test_real_property_cputime(self, backend):
        """Test RealProperty.CPUTIME get/set"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend doesn't support RealProperty API")

        db = create_db()
        node = db.createHistoryNode(None, "run1", "run1.db",
                                    UCIS_HISTORYNODE_TEST)
        node.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                  toolcategory="vcs", date="20240101000000"))

        node.setRealProperty(RealProperty.CPUTIME, 42.5)
        val = node.getRealProperty(RealProperty.CPUTIME)
        assert val == pytest.approx(42.5)

    def test_multiple_history_nodes(self, backend):
        """Test creating multiple history nodes"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        for i in range(3):
            node = db.createHistoryNode(None, f"test{i}", f"test{i}.db",
                                        UCIS_HISTORYNODE_TEST)
            node.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                      toolcategory="vcs",
                                      date="20240101000000"))

        nodes = list(db.historyNodes(UCIS_HISTORYNODE_TEST))
        assert len(nodes) == 3

    def test_history_node_write_read(self, backend):
        """Test history node persists through write/read"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend requires coverage scopes for valid document")

        db = create_db()
        node = db.createHistoryNode(None, "persist_test", "persist.db",
                                    UCIS_HISTORYNODE_TEST)
        node.setTestData(TestData(teststatus=UCIS_TESTSTATUS_OK,
                                  toolcategory="vcs", date="20240101000000"))

        written = write_db(db, temp_file)
        db2 = read_db(written if written is not None else db)

        nodes = list(db2.historyNodes(UCIS_HISTORYNODE_TEST))
        assert len(nodes) >= 1
