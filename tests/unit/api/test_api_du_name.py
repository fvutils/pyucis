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
Tests for parseDUName and composeDUName utility functions.
"""

import pytest
from ucis.du_name import parseDUName, composeDUName


class TestApiDuName:
    """Tests for DU name parsing and composition"""

    def test_parse_qualified_name(self):
        """parseDUName splits library and module on first dot"""
        lib, mod = parseDUName("work.counter")
        assert lib == "work"
        assert mod == "counter"

    def test_parse_unqualified_name_uses_default_library(self):
        """parseDUName with no dot uses default library 'work'"""
        lib, mod = parseDUName("counter")
        assert lib == "work"
        assert mod == "counter"

    def test_parse_custom_default_library(self):
        """parseDUName respects custom default_library argument"""
        lib, mod = parseDUName("alu", default_library="mylib")
        assert lib == "mylib"
        assert mod == "alu"

    def test_parse_only_splits_on_first_dot(self):
        """parseDUName only splits on the first dot"""
        lib, mod = parseDUName("work.my.module")
        assert lib == "work"
        assert mod == "my.module"

    def test_compose_basic(self):
        """composeDUName joins library and module with a dot"""
        assert composeDUName("work", "counter") == "work.counter"

    def test_compose_custom_library(self):
        """composeDUName works with non-default library names"""
        assert composeDUName("mylib", "alu") == "mylib.alu"

    def test_parse_empty_raises(self):
        """parseDUName raises ValueError on empty string"""
        with pytest.raises(ValueError):
            parseDUName("")

    def test_compose_empty_module_raises(self):
        """composeDUName raises ValueError when module is empty"""
        with pytest.raises(ValueError):
            composeDUName("work", "")

    def test_compose_empty_library_raises(self):
        """composeDUName raises ValueError when library is empty"""
        with pytest.raises(ValueError):
            composeDUName("", "counter")

    def test_round_trip(self):
        """parseDUName(composeDUName(lib, mod)) round-trips"""
        lib, mod = parseDUName(composeDUName("mylib", "adder"))
        assert lib == "mylib"
        assert mod == "adder"
