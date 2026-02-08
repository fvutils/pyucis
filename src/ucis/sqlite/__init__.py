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
SQLite backend for UCIS Python API
"""

from ucis.sqlite.sqlite_ucis import SqliteUCIS
from ucis.sqlite.sqlite_scope import SqliteScope
from ucis.sqlite.sqlite_cover_index import SqliteCoverIndex
from ucis.sqlite.sqlite_history_node import SqliteHistoryNode
from ucis.sqlite.sqlite_file_handle import SqliteFileHandle
from ucis.sqlite.sqlite_toggle_scope import SqliteToggleScope, ToggleBit
from ucis.sqlite.sqlite_fsm_scope import SqliteFSMScope, FSMState, FSMTransition
from ucis.sqlite.sqlite_cross import SqliteCross
from ucis.sqlite.sqlite_merge import SqliteMerger, MergeStats, merge_databases
from ucis.sqlite.sqlite_attributes import AttributeManager, TagManager, ObjectKind

__all__ = [
    'SqliteUCIS',
    'SqliteScope',
    'SqliteCoverIndex',
    'SqliteHistoryNode',
    'SqliteFileHandle',
    'SqliteToggleScope',
    'ToggleBit',
    'SqliteFSMScope',
    'FSMState',
    'FSMTransition',
    'SqliteCross',
    'SqliteMerger',
    'MergeStats',
    'merge_databases',
    'AttributeManager',
    'TagManager',
    'ObjectKind',
]
