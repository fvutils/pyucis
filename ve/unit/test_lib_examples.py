
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


import os
from unittest.case import TestCase
from pyucis.mem.mem_factory import MemFactory
from pyucis.source_info import SourceInfo
from pyucis.scope import Scope
from pyucis.test_data import TestData
from pyucis import *
from pyucis.lib.LibFactory import LibFactory
import example_create_ucis

class TestUcisExamples(TestCase):

    def setUp(self):
        LibFactory.load_ucis_library("libucis.so")
    
    def test_create_ucis(self):
        db = LibFactory.create()
        example_create_ucis.create_ucis(db)
        db.write("file.ucis", None, True, -1)
        db.close()
