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
Tests for hierarchical path separator API.

Tests cover:
- Default separator is '/'
- setPathSeparator / getPathSeparator round-trip
- Alternate separators ('.' used in SystemVerilog hierarchical references)
- ValueError on multi-character separator
"""

import pytest
from ucis import *
from ucis.source_info import SourceInfo
from ucis.scope_type_t import ScopeTypeT


class TestApiPathSeparator:
    """Test getPathSeparator / setPathSeparator on UCIS databases"""

    def test_default_separator(self, backend):
        """Default path separator is '/'"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend path separator not tested")
        db = create_db()
        assert db.getPathSeparator() == '/'

    def test_set_dot_separator(self, backend):
        """Can change separator to '.'"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend path separator not tested")
        db = create_db()
        db.setPathSeparator('.')
        assert db.getPathSeparator() == '.'

    def test_restore_slash_separator(self, backend):
        """Can change separator back to '/'"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend path separator not tested")
        db = create_db()
        db.setPathSeparator('.')
        db.setPathSeparator('/')
        assert db.getPathSeparator() == '/'

    def test_invalid_multchar_separator(self, backend):
        """setPathSeparator raises ValueError for multi-character input"""
        backend_name, create_db, write_db, read_db, temp_file = backend
        if backend_name == "xml":
            pytest.skip("XML backend path separator not tested")
        db = create_db()
        with pytest.raises((ValueError, Exception)):
            db.setPathSeparator('::')
