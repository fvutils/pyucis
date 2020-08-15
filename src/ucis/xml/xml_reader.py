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

from datetime import datetime
from logging import _srcfile
import sys
from typing import Dict

from lxml import etree
from ucis import UCIS_ENABLED_STMT, UCIS_ENABLED_BRANCH, UCIS_ENABLED_COND, \
    UCIS_ENABLED_EXPR, UCIS_ENABLED_FSM, UCIS_ENABLED_TOGGLE, UCIS_INST_ONCE, \
    UCIS_SCOPE_UNDER_DU, UCIS_DU_MODULE, UCIS_OTHER, du_scope, UCIS_INSTANCE
from ucis.mem.mem_file_handle import MemFileHandle
from ucis.mem.mem_scope import MemScope
from ucis.mem.mem_ucis import MemUCIS
from ucis.statement_id import StatementId
from ucis.ucis import UCIS
from ucis.xml import validate_ucis_xml


class XmlReader():
    
    def __init__(self):
        self.file_m : Dict[int,MemFileHandle] = {}
        self.module_scope_m : Dict[str, MemScope] = {}
        self.inst_scope_m : Dict[str, MemScope] = {}
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
       
#        self.db.setWrittenBy(root.get("writtenBy"))
#        self.db.setWrittenTime(self.getAttrDateTime(root, "writtenTime"))
        
        for srcFileN in tree.iter("sourceFiles"):
            self.readSourceFile(srcFileN)
            
        for histN in tree.iter("historyNodes"):
            self.readHistoryNode(histN)

        for instN in tree.iter("instanceCoverages"):
            self.readInstanceCoverage(instN)
            
        from ..report.text_coverage_report_formatter import TextCoverageReportFormatter
        from ..report.coverage_report_builder import CoverageReportBuilder
        report = CoverageReportBuilder.build(self.db)
        formatter = TextCoverageReportFormatter(report, sys.stdout)
        formatter.details = True
        formatter.report()

        return self.db
    
    @staticmethod
    def validate(file_or_filename):
        validate_ucis_xml(file_or_filename)
        
    
    def readSourceFile(self, srcFileN):
        filename = srcFileN.get("fileName")
        id = int(srcFileN.get("id"))
        file_h = self.db.createFileHandle(filename, None)
        self.file_m[id] = file_h
        
        return file_h
    
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
        self.setFloatIfEx(histN, ret.setCost, "cost")
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
            
        srcinfo = None
            
        # TODO: Creating a coverage instance depends on
        # having a du_type
        module_scope_name = self.getAttr(instN, "moduleName", "default")
        
        type_scope = self.getScope(
            module_scope_name, 
            None, 
            UCIS_OTHER) # TODO: how do we determine source type?
        
        inst_scope = self.getInstScope(
            name,
            srcinfo,
            UCIS_OTHER,
            type_scope)
        
        for cg in instN.iter("covergroupCoverage"):
            self.readCovergroup(cg, inst_scope)

#        self.setIntIfEx(instN, ret.setAli, name)

    def readCovergroup(self, cg, inst_scope):
        # This entry is for a given covergroup type
        
        cg_typescope = None
        covergroup_scope = None
        
        for cgN in cg.iter("cgInstance"):
            srcinfo = None
            if cg_typescope is None:
                cg_typescope = inst_scope.createCovergroup(
                    self.getAttr(cgN, "name", "default"),
                    srcinfo,
                    1,
                    UCIS_OTHER)
                covergroup_scope = cg_typescope
            else:
                covergroup_scope = cg_typescope.createCoverInstance(
                    self.getAttr(cgN, "name", "default"),
                    srcinfo,
                    1,
                    UCIS_OTHER)
                
            cp_m = {}
                
            for cpN in cgN.iter("coverpoint"):
                cp = self.readCoverpoint(cpN, covergroup_scope)
                cp_m[self.getAttr(cpN, "name", "default")] = cp
                
            for crN in cgN.iter("cross"):
                self.readCross(crN, cp_m, covergroup_scope)
                
    def readCoverpoint(self, cpN, covergroup_scope):
        srcinfo = None
        
        cp = covergroup_scope.createCoverpoint(
            self.getAttr(cpN, "name", "default"),
            srcinfo,
            1, # weight
            UCIS_OTHER)
        
        for cpBin in cpN.iter("coverpointBin"):
            self.readCoverpointBin(cpBin, cp)
            
        return cp
            
    def readCoverpointBin(self, cpBin, cp):
        srcinfo = None
        seq = next(cpBin.iter("sequence"))
        contents = next(seq.iter("contents"))
        
        cp.createBin(
            self.getAttr(cpBin, "name", "default"),
            srcinfo,
            1,
            self.getAttrInt(contents, "coverageCount"),
            self.getAttr(cpBin, "name", "default"))
        
    def readCross(self, crN, cp_m, covergroup_scope):
        crossExpr = next(crN.iter("crossExpr"))
        name = self.getAttr(crN, "name", "default")
        
        cp_l = []
        for cp_n in crossExpr.text.split(','):
            print("cp_n=\"" + cp_n + "\"")
            if cp_n in cp_m.keys():
                cp_l.append(cp_m[cp_n])
            else:
                raise Exception("Cross " + name + " references missing coverpoint " + cp_n)

        srcinfo = None
        
        cr = covergroup_scope.createCross(
            name,
            srcinfo,
            1, # weight
            UCIS_OTHER,
            cp_l)
        
        for crB in crN.iter("crossBin"):
            self.readCrossBin(crB, cr)
        
        return cr
    
    def readCrossBin(self, crB, cr):
        name = self.getAttr(crB, "name", "default")
        srcinfo = None
        contentsN = next(crB.iter("contents"))
        
        cr.createBin(
            name,
            srcinfo,
            1, # weight
            self.getAttrInt(contentsN, "coverageCount"),
            "") # TODO:
        

    def readStatementId(self, stmt_idN):
        file_id = int(stmt_idN.attrib["file"])
        line = int(stmt_idN.attrib["line"])
        item = int(stmt_idN.attrib["inlineCount"])
        file = self.file_m[file_id]
        return StatementId(file, line, item)

    def getScope(self,
                 name,
                 srcinfo,
                 source):
        
        if name not in self.module_scope_m.keys():
            scope = self.db.createScope(
                name, 
                srcinfo, 
                1, 
                source, 
                UCIS_DU_MODULE,
                UCIS_ENABLED_STMT | UCIS_ENABLED_BRANCH
                | UCIS_ENABLED_COND | UCIS_ENABLED_EXPR
                | UCIS_ENABLED_FSM | UCIS_ENABLED_TOGGLE
                | UCIS_INST_ONCE | UCIS_SCOPE_UNDER_DU)
            self.module_scope_m[name] = scope
        else:
            scope = self.module_scope_m[name]
            
        return scope
    
    def getInstScope(self,
                     name,
                     srcinfo,
                     source,
                     du_scope):
        if name not in self.inst_scope_m.keys():
            scope = self.db.createInstance(
                name,
                srcinfo,
                1,
                source,
                UCIS_INSTANCE,
                du_scope,
                UCIS_INST_ONCE)
            self.inst_scope_m[name] = scope
        else:
            scope = self.inst_scope_m[name]
            
        return scope
    
    def getAttrDateTime(self, e, name):
        """Converts ISO time used by XML to the YYYYMMDDHHMMSS format used by the library"""
        val = e.get(name)
        dateVal = datetime.strptime(val,"%Y-%m-%dT%H:%M:%S")
        return dateVal.strftime("%Y%m%d%H%M%S")
    
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
        
    def getAttrInt(self, e, name):
        return int(e.attrib[name])
        
    def setIfEx(self, n, f, name):
        if name in n.attrib:
            f(n.attrib[name])
            
    def setIntIfEx(self, n, f, name):
        if name in n.attrib:
            f(int(n.attrib[name]))

    def setFloatIfEx(self, n, f, name):
        if name in n.attrib:
            f(float(n.attrib[name]))
