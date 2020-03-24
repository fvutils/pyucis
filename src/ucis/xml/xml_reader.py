from ucis.xml import validate_ucis_xml

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
Created on Jan 6, 2020

@author: ballance
'''
from ucis.ucis import UCIS
from lxml import etree
from ucis.mem.mem_ucis import MemUCIS
from ucis.statement_id import StatementId

class XmlReader():
    
    def __init__(self):
        pass
    
    def read(self, file) -> UCIS:
        tree = etree.parse(file)
        root = tree.getroot()
        self.db = MemUCIS()
        
        for elem in root.getiterator():
            if not hasattr(elem.tag, 'find'): continue  # (1)
            i = elem.tag.find('}')
            if i >= 0:
                elem.tag = elem.tag[i+1:]
       
        self.db.setWrittenBy(root.get("writtenBy"))
        self.db.setWrittenTime(self.getAttrDateTime(root, "writtenTime"))
        
        for srcFileN in tree.iter("sourceFiles"):
            self.readSourceFile(srcFileN)
            
        for histN in tree.iter("historyNodes"):
            self.readHistoryNode(histN)

        for instN in tree.iter("instanceCoverages"):
            self.readInstanceCoverage(instN)

        return self.db
    
    @staticmethod
    def validate(file_or_filename):
        validate_ucis_xml(file_or_filename)
        
    
    def readSourceFile(self, srcFileN):
        filename = srcFileN.get("fileName")
        return self.db.createFileHandle(filename, None)
    
    def readHistoryNode(self, histN):
        parent = None
        logicalname = histN.get("logicalName")
        physicalname = self.getAttr(histN, "physicalName", None)
        kind = self.getAttr(histN, "kind", None)
        
        ret = self.db.createHistoryNode(parent, logicalname, physicalname, kind)
        ret.setTestStatus(self.getAttrBool(histN, "testStatus"))
        self.setFloatIfEx(histN, ret.setSimTime, "simtime")
        self.setIfEx(histN, ret.setTimeUnit, "timeunit")
        self.setIfEx(histN, ret.setRunCwd, "runCwd")
        self.setFloatIfEx(histN, ret.setCpuTime, "cpuTime")
        self.setIfEx(histN, ret.setSeed, "seed")
        self.setIfEx(histN, ret.setCmd, "cmd")
        self.setIfEx(histN, ret.setArgs, "args")
        self.setIfEx(histN, ret.setCompulsory, "compulsory")
        ret.setDate(self.getAttrDateTime(histN, "date"))
        self.setIfEx(histN, ret.setUserName, "userName")
        self.setIntIfEx(histN, ret.setCost, "cost")
        ret.setToolCategory(histN.attrib["toolCategory"])
        ret.setVendorId(histN.attrib["vendorId"])
        ret.setVendorTool(histN.attrib["vendorTool"])
        ret.setVendorToolVersion(histN.attrib["vendorToolVersion"])
        self.setIntIfEx(histN, ret.setSameTests, "sameTests")
        self.setIfEx(histN, ret.setComment, "comment")
        
        return ret
    
    def readInstanceCoverage(self, instN):
        name = instN.attrib["name"]
        stmt_id = None
        for stmt_idN in instN.iter("id"):
            stmt_id = self.readStatementId(stmt_idN)

        print("stmt_id")
        ret = self.db.createCoverInstance(name, stmt_id)
##        ret.setKey

#        self.setIntIfEx(instN, ret.setAli, name)
        
        return ret

    def readStatementId(self, stmt_idN):
        file_id = int(stmt_idN.attrib["file"])
        line = int(stmt_idN.attrib["line"])
        item = int(stmt_idN.attrib["inlineCount"])
        file = self.db.getSourceFiles()[file_id-1]
        return StatementId(file, line, item)
        
    
    def getAttrDateTime(self, e, name):
        val = e.get(name)
        return 0;
    
    def getAttr(self, node, name, default):
        if name in node.attrib:
            return node.attrib[name]
        else:
            return default
        
    def getAttrBool(self, e, name):
        if e.attrib[name] == "true":
            return True
        else:
            return False
        
    def setIfEx(self, n, f, name):
        if name in n.attrib:
            f(n.attrib[name])
            
    def setIntIfEx(self, n, f, name):
        if name in n.attrib:
            f(int(n.attrib[name]))

    def setFloatIfEx(self, n, f, name):
        if name in n.attrib:
            f(float(n.attrib[name]))
