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
cocotb-coverage format import support for PyUCIS.

This module provides functionality to import functional coverage data
from cocotb-coverage XML and YAML formats into the PyUCIS database.
"""

__all__ = [
    'CocotbXmlReader',
    'CocotbYamlReader',
    'read_cocotb_xml',
    'read_cocotb_yaml',
]

from .cocotb_xml_reader import CocotbXmlReader, read_cocotb_xml
from .cocotb_yaml_reader import CocotbYamlReader, read_cocotb_yaml
