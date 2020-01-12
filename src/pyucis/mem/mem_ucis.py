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
'''
Created on Jan 5, 2020

@author: ballance
'''

from datetime import datetime
import getpass
from pyucis.ucis import UCIS
from pyucis.unimpl_error import UnimplError

from pyucis.flags_t import FlagsT
from pyucis.history_node import HistoryNode
from pyucis.instance_coverage import InstanceCoverage
from pyucis.mem.mem_du_scope import MemDUScope
from pyucis.mem.mem_history_node import MemHistoryNode
from pyucis.mem.mem_instance_coverage import MemInstanceCoverage
from pyucis.mem.mem_instance_scope import MemInstanceScope
from pyucis.mem.mem_scope import MemScope
from pyucis.mem.mem_source_file import MemSourceFile
from pyucis.scope_type_t import ScopeTypeT
from pyucis.source_file import SourceFile
from pyucis.source_info import SourceInfo
from pyucis.source_t import SourceT
from pyucis.statement_id import StatementId


class MemUCIS(UCIS):
    
    def __init__(self):
        super().__init__()
        self.ucis_version = "1.0"
        self.writtenBy = getpass.getuser()
        self.writtenTime = int(datetime.timestamp(datetime.now()))
        self.m_history_node_l = []
        self.m_source_file_l = []
        self.m_instance_coverage_l = []
        
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
        ret = MemSourceFile(len(self.m_source_file_l), filename)
        self.m_source_file_l.append(ret)
        return ret
    
    def createScope(self,
                name : str,
                srcinfo : SourceInfo,
                weight : int,
                source,
                type : ScopeTypeT,
                flags):
        # Creates a type scope and associates source information with it
        if ScopeTypeT.DU_ANY(type):
            ret = MemDUScope(None, name, srcinfo, weight,
                              source, type, flags)
            self.m_du_scope_l.append(ret)
        else:
            raise UnimplError()
        
        return ret
    
    def createInstance(self,
                    name : str,
                    fileinfo : SourceInfo,
                    weight : int,
                    source : SourceT,
                    type : ScopeTypeT,
                    du_scope : 'Scope',
                    flags : FlagsT) ->'Scope':
        # Create an instance of a type scope
        return MemInstanceScope(None, name, fileinfo, weight, source, type, du_scope, flags)
    
    def createHistoryNode(self, parent, logicalname, physicalname=None, kind=None):
        ret = MemHistoryNode(parent, logicalname, physicalname, kind)
        self.m_history_node_l.append(ret)
        return ret

    def createCoverInstance(self, name, stmt_id : StatementId):
        ret = MemInstanceCoverage(name, str(len(self.m_instance_coverage_l)), stmt_id)
        self.m_instance_coverage_l.append(ret)
        return ret
        
    def getHistoryNodes(self) -> [HistoryNode]:
        return self.m_history_node_l
    
    def getSourceFiles(self)->[SourceFile]:
        return self.m_source_file_l
    
    def getCoverInstances(self)->[InstanceCoverage]:
        return self.m_instance_coverage_l

    
    