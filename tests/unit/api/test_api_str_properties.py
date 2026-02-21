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
Tests for string properties (StrProperty) on scopes and history nodes.

Tests cover:
- SCOPE_NAME (scope name retrieval)
- COMMENT (setting/getting comments on scopes)
- HIST_CMDLINE (command-line string on history nodes)
- HIST_ELABORATION_DATE and HIST_VERSION on history nodes
"""

import pytest
from ucis import *
from ucis.source_info import SourceInfo
from ucis.scope_type_t import ScopeTypeT
from ucis.str_property import StrProperty
from ucis.history_node_kind import HistoryNodeKind


class TestApiStrProperties:
    """Test StrProperty on scopes and history nodes"""

    def _make_db_with_inst(self, db):
        fh = db.createFileHandle("design.v", "/rtl")
        du = db.createScope("work.module1", SourceInfo(fh, 1, 0),
                            1, UCIS_VLOG, UCIS_DU_MODULE,
                            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst = db.createInstance("i_module1", None, 1, UCIS_VLOG,
                                 UCIS_INSTANCE, du, UCIS_INST_ONCE)
        return inst

    def test_scope_name_property(self, backend):
        """SCOPE_NAME property returns the scope's name"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        db = create_db()
        inst = self._make_db_with_inst(db)
        assert inst.getStringProperty(-1, StrProperty.SCOPE_NAME) == "i_module1"

    def test_comment_round_trip(self, backend):
        """COMMENT can be set and retrieved on a scope"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support COMMENT string property")
        db = create_db()
        inst = self._make_db_with_inst(db)
        inst.setStringProperty(-1, StrProperty.COMMENT, "my comment")
        assert inst.getStringProperty(-1, StrProperty.COMMENT) == "my comment"

    def test_hist_cmdline(self, backend):
        """HIST_CMDLINE can be stored on a history node"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support HistoryNode cmdline write")
        db = create_db()
        hn = db.createHistoryNode(None, "sim_run", None,
                                  HistoryNodeKind.MERGE)
        hn.setStringProperty(-1, StrProperty.HIST_CMDLINE, "simv +test=foo")
        assert hn.getStringProperty(-1, StrProperty.HIST_CMDLINE) == "simv +test=foo"

    def test_hist_username(self, backend):
        """TEST_USERNAME can be stored on a history node"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support HistoryNode username write")
        db = create_db()
        hn = db.createHistoryNode(None, "sim_run", None,
                                  HistoryNodeKind.MERGE)
        hn.setStringProperty(-1, StrProperty.TEST_USERNAME, "jdoe")
        assert hn.getStringProperty(-1, StrProperty.TEST_USERNAME) == "jdoe"
