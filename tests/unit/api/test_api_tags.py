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
Dedicated tests for the tag API on UCIS scope objects.

Tags are string labels attached to scopes for filtering and categorization.
These tests verify addTag, hasTag, removeTag, and getTags behaviour in isolation.
"""

import pytest
from ucis import *
from ucis.source_info import SourceInfo
from ucis.scope_type_t import ScopeTypeT


def _make_inst(db):
    fh = db.createFileHandle("design.v", "/rtl")
    du = db.createScope("work.module1", SourceInfo(fh, 1, 0),
                        1, UCIS_VLOG, UCIS_DU_MODULE,
                        UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
    return db.createInstance("i_module1", None, 1, UCIS_VLOG,
                             UCIS_INSTANCE, du, UCIS_INST_ONCE)


class TestApiTags:
    """Tests for tag API on scope objects"""

    def test_add_and_has_tag(self, backend):
        """addTag / hasTag basic round-trip"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support tags")
        db = create_db()
        inst = _make_inst(db)
        assert not inst.hasTag("smoke")
        inst.addTag("smoke")
        assert inst.hasTag("smoke")

    def test_has_tag_absent(self, backend):
        """hasTag returns False for a tag that was never added"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support tags")
        db = create_db()
        inst = _make_inst(db)
        assert not inst.hasTag("nonexistent")

    def test_remove_tag(self, backend):
        """removeTag makes hasTag return False"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support tags")
        db = create_db()
        inst = _make_inst(db)
        inst.addTag("regression")
        assert inst.hasTag("regression")
        inst.removeTag("regression")
        assert not inst.hasTag("regression")

    def test_get_tags_returns_all(self, backend):
        """getTags returns all added tags"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support tags")
        db = create_db()
        inst = _make_inst(db)
        inst.addTag("alpha")
        inst.addTag("beta")
        inst.addTag("gamma")
        tags = inst.getTags()
        assert "alpha" in tags
        assert "beta" in tags
        assert "gamma" in tags

    def test_tags_independent_per_scope(self, backend):
        """Tags on one scope do not appear on a sibling scope"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support tags")
        db = create_db()
        fh = db.createFileHandle("d.v", "/rtl")
        du = db.createScope("work.m", SourceInfo(fh, 1, 0),
                            1, UCIS_VLOG, UCIS_DU_MODULE,
                            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst_a = db.createInstance("ia", None, 1, UCIS_VLOG,
                                   UCIS_INSTANCE, du, UCIS_INST_ONCE)
        inst_b = db.createInstance("ib", None, 1, UCIS_VLOG,
                                   UCIS_INSTANCE, du, UCIS_INST_ONCE)
        inst_a.addTag("only_on_a")
        assert not inst_b.hasTag("only_on_a")

    def test_duplicate_add_tag(self, backend):
        """Adding the same tag twice does not cause an error"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support tags")
        db = create_db()
        inst = _make_inst(db)
        inst.addTag("dup")
        inst.addTag("dup")
        assert inst.hasTag("dup")
