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
from typing import Iterator
from ucis.mem.mem_history_node_iterator import MemHistoryNodeIterator
from ucis.mem.mem_file_handle import MemFileHandle
'''
Created on Jan 5, 2020

@author: ballance
'''

from datetime import datetime
import getpass
from ucis.flags_t import FlagsT
from ..history_node import HistoryNode
from ..history_node_kind import HistoryNodeKind
from ..instance_coverage import InstanceCoverage
from ..mem.mem_du_scope import MemDUScope
from ..mem.mem_history_node import MemHistoryNode
from ..mem.mem_instance_coverage import MemInstanceCoverage
from ..mem.mem_instance_scope import MemInstanceScope
from ..mem.mem_scope import MemScope
from ..mem.mem_source_file import MemSourceFile
from ..scope_type_t import ScopeTypeT
from ..source_file import SourceFile
from ucis.source_info import SourceInfo
from ucis.source_t import SourceT
from ucis.statement_id import StatementId
from ucis.ucis import UCIS
from ucis.unimpl_error import UnimplError


class MemUCIS(MemScope,UCIS):
    
    def __init__(self):
        MemScope.__init__(
            self,
            None,
            "",
            None,
            1,
            SourceT.NONE,
            ScopeTypeT.RESERVEDSCOPE,
            0)
        UCIS.__init__(self)
        self.ucis_version = "1.0"
        self.writtenBy = getpass.getuser()
        self.writtenTime = int(datetime.timestamp(datetime.now()))
        self.file_handle_m : Dict[str,MemFileHandle] = {}
        self.m_history_node_l = []
        self.m_instance_coverage_l = []
        self._path_separator = '/'
        
        self.m_du_scope_l = []
        self.m_inst_scope_l = []
    
    def getAPIVersion(self)->str:
        return "1.0"
    
    def getWrittenBy(self)->str:
        return self.writtenBy
    
    def setWrittenBy(self, by):
        self.writtenBy = by
    
    def getWrittenTime(self)->int:
        return self.writtenTime
    
    def setWrittenTime(self, time : int):
        self.writtenTime = time
    
    def createFileHandle(self, filename, workdir):
        if filename not in self.file_handle_m.keys():
            self.file_handle_m[filename] = MemFileHandle(filename)
        return self.file_handle_m[filename]

    def getPathSeparator(self) -> str:
        """Get the hierarchical path separator (default '/')."""
        return self._path_separator

    def setPathSeparator(self, separator: str):
        """Set the hierarchical path separator."""
        if len(separator) != 1:
            raise ValueError("Path separator must be a single character")
        self._path_separator = separator

    def removeScope(self, scope) -> None:
        """Remove a scope (and its subtree) from the database."""
        def _remove_from(parent, target):
            if target in parent.m_children:
                parent.m_children.remove(target)
                return True
            for child in parent.m_children:
                if hasattr(child, 'm_children') and _remove_from(child, target):
                    return True
            return False
        _remove_from(self, scope)

    def matchScopeByUniqueId(self, uid: str):
        """Find a scope by its UNIQUE_ID string property (depth-first walk)."""
        from ucis.str_property import StrProperty
        def _walk(scope):
            if hasattr(scope, '_str_properties'):
                if scope._str_properties.get(StrProperty.UNIQUE_ID) == uid:
                    return scope
            for child in getattr(scope, 'm_children', []):
                result = _walk(child)
                if result is not None:
                    return result
            return None
        return _walk(self)

    def matchCoverByUniqueId(self, uid: str):
        """Find (scope, coverindex) by UNIQUE_ID on a cover item."""
        def _walk(scope):
            for i, item in enumerate(getattr(scope, 'm_cover_items', [])):
                if hasattr(item, '_str_properties'):
                    from ucis.str_property import StrProperty
                    if item._str_properties.get(StrProperty.UNIQUE_ID) == uid:
                        return (scope, i)
            for child in getattr(scope, 'm_children', []):
                result = _walk(child)
                if result is not None:
                    return result
            return (None, -1)
        return _walk(self)
    

    
    def createHistoryNode(self, parent, logicalname, physicalname=None, kind=None):
        ret = MemHistoryNode(parent, logicalname, physicalname, kind)
        self.m_history_node_l.append(ret)
        return ret

    def createCoverInstance(self, name, stmt_id : StatementId):
        ret = MemInstanceCoverage(name, str(len(self.m_instance_coverage_l)), stmt_id)
        self.m_instance_coverage_l.append(ret)
        return ret
        
    def historyNodes(self, kind:HistoryNodeKind)->Iterator[HistoryNode]:
        return MemHistoryNodeIterator(self.m_history_node_l, kind)
    
    def getCoverInstances(self)->[InstanceCoverage]:
        """Get top-level coverage instances (includes both InstanceCoverage and INSTANCE scopes)."""
        # Include instances added via createCoverInstance() as well as direct INSTANCE children
        from ucis.scope_type_t import ScopeTypeT
        result = list(self.m_instance_coverage_l)
        for child in self.m_children:
            if child.getScopeType() == ScopeTypeT.INSTANCE:
                result.append(child)
        return result

    def getSourceFiles(self):
        """Get list of all registered source file handles"""
        return list(self.file_handle_m.values())
    
    def close(self):
        # NOP
        pass

    
    