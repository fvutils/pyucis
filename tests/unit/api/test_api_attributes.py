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
Test user-defined attributes and tags on scopes.

Tests cover:
- Setting and getting string attributes on scopes
- Deleting attributes
- Adding, checking, and removing tags
"""

import pytest
from ucis import *
from ucis.source_info import SourceInfo
from ucis.scope_type_t import ScopeTypeT


class TestApiAttributes:
    """Test user-defined attributes and tags on scopes"""

    def _make_inst(self, db):
        fh = db.createFileHandle("design.v", "/rtl")
        du = db.createScope("work.module1", SourceInfo(fh, 1, 0),
                            1, UCIS_VLOG, UCIS_DU_MODULE,
                            UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
        inst = db.createInstance("i_module1", None, 1, UCIS_VLOG,
                                 UCIS_INSTANCE, du, UCIS_INST_ONCE)
        return inst

    def test_set_get_attribute(self, backend):
        """Test setting and getting a string attribute"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        inst = self._make_inst(db)

        inst.setAttribute("tool", "vcs")
        assert inst.getAttribute("tool") == "vcs"

    def test_get_nonexistent_attribute(self, backend):
        """Test getting a non-existent attribute returns None"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        inst = self._make_inst(db)

        result = inst.getAttribute("nonexistent")
        assert result is None

    def test_multiple_attributes(self, backend):
        """Test setting multiple attributes"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        inst = self._make_inst(db)

        inst.setAttribute("tool", "vcs")
        inst.setAttribute("version", "2024.1")
        inst.setAttribute("seed", "42")

        assert inst.getAttribute("tool") == "vcs"
        assert inst.getAttribute("version") == "2024.1"
        assert inst.getAttribute("seed") == "42"

    def test_get_all_attributes(self, backend):
        """Test getting all attributes as a dict"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        inst = self._make_inst(db)

        inst.setAttribute("key1", "val1")
        inst.setAttribute("key2", "val2")

        attrs = inst.getAttributes()
        assert attrs.get("key1") == "val1"
        assert attrs.get("key2") == "val2"

    def test_delete_attribute(self, backend):
        """Test deleting an attribute"""
        backend_name, create_db, write_db, read_db, temp_file = backend

        db = create_db()
        inst = self._make_inst(db)

        inst.setAttribute("temp", "to_delete")
        assert inst.getAttribute("temp") == "to_delete"

        inst.deleteAttribute("temp")
        assert inst.getAttribute("temp") is None

    def test_add_check_tag(self, backend):
        """Test adding and checking a tag"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support user tags")

        db = create_db()
        inst = self._make_inst(db)

        inst.addTag("important")
        assert inst.hasTag("important")
        assert not inst.hasTag("other")

    def test_multiple_tags(self, backend):
        """Test multiple tags on a scope"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support user tags")

        db = create_db()
        inst = self._make_inst(db)

        inst.addTag("high_priority")
        inst.addTag("regression")
        inst.addTag("synthesis")

        assert inst.hasTag("high_priority")
        assert inst.hasTag("regression")
        assert inst.hasTag("synthesis")
        assert not inst.hasTag("other")

    def test_remove_tag(self, backend):
        """Test removing a tag"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support user tags")

        db = create_db()
        inst = self._make_inst(db)

        inst.addTag("temp_tag")
        assert inst.hasTag("temp_tag")

        inst.removeTag("temp_tag")
        assert not inst.hasTag("temp_tag")

    def test_get_all_tags(self, backend):
        """Test getting all tags on a scope"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend does not support user tags")

        db = create_db()
        inst = self._make_inst(db)

        inst.addTag("alpha")
        inst.addTag("beta")
        inst.addTag("gamma")

        tags = inst.getTags()
        assert "alpha" in tags
        assert "beta" in tags
        assert "gamma" in tags
        assert len(tags) == 3
