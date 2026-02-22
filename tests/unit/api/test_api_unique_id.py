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
Tests for matchScopeByUniqueId and matchCoverByUniqueId.
"""

import pytest
from ucis import *
from ucis.source_info import SourceInfo
from ucis.scope_type_t import ScopeTypeT
from ucis.str_property import StrProperty


def _make_db_with_tagged_scope(db):
    """Create a small DB, tag one scope with UNIQUE_ID, return (db, inst)."""
    fh = db.createFileHandle("design.v", "/rtl")
    du = db.createScope("work.module1", SourceInfo(fh, 1, 0),
                        1, UCIS_VLOG, UCIS_DU_MODULE,
                        UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
    inst = db.createInstance("i_module1", None, 1, UCIS_VLOG,
                             UCIS_INSTANCE, du, UCIS_INST_ONCE)
    inst.setStringProperty(-1, StrProperty.UNIQUE_ID, "uid-inst-001")
    return inst


class TestApiUniqueId:
    """Tests for matchScopeByUniqueId / matchCoverByUniqueId"""

    def test_match_scope_by_unique_id(self, backend):
        """matchScopeByUniqueId finds a scope tagged with UNIQUE_ID"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support matchScopeByUniqueId")
        db = create_db()
        inst = _make_db_with_tagged_scope(db)

        found = db.matchScopeByUniqueId("uid-inst-001")
        assert found is not None
        assert found.getScopeName() == "i_module1"

    def test_match_scope_not_found_returns_none(self, backend):
        """matchScopeByUniqueId returns None for an unknown UID"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support matchScopeByUniqueId")
        db = create_db()
        _make_db_with_tagged_scope(db)

        found = db.matchScopeByUniqueId("no-such-uid")
        assert found is None

    def test_match_scope_after_multiple_scopes(self, backend):
        """matchScopeByUniqueId finds the right scope among several"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support matchScopeByUniqueId")
        db = create_db()
        fh = db.createFileHandle("d.v", "/rtl")
        du = db.createScope("work.m", SourceInfo(fh, 1, 0),
                            1, UCIS_VLOG, UCIS_DU_MODULE,
                            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst_a = db.createInstance("ia", None, 1, UCIS_VLOG,
                                   UCIS_INSTANCE, du, UCIS_INST_ONCE)
        inst_b = db.createInstance("ib", None, 1, UCIS_VLOG,
                                   UCIS_INSTANCE, du, UCIS_INST_ONCE)
        inst_a.setStringProperty(-1, StrProperty.UNIQUE_ID, "uid-a")
        inst_b.setStringProperty(-1, StrProperty.UNIQUE_ID, "uid-b")

        assert db.matchScopeByUniqueId("uid-a").getScopeName() == "ia"
        assert db.matchScopeByUniqueId("uid-b").getScopeName() == "ib"
