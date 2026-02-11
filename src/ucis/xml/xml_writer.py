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

import time
import datetime
from datetime import datetime
from datetime import date
from typing import Dict, Iterator
from ucis.cover_index import CoverIndex
from ucis.cover_type_t import CoverTypeT
from ucis.covergroup import Covergroup
from ucis.coverpoint import Coverpoint
from ucis.history_node_kind import HistoryNodeKind
from ucis.scope import Scope
from ucis.scope_type_t import ScopeTypeT
from ucis.statement_id import StatementId

from lxml import etree as et
from lxml.etree import QName, tounicode, SubElement

import getpass


class XmlWriter():
    
    UCIS = "http://www.w3.org/2001/XMLSchema-instance"
    
    def __init__(self):
        self.db = None
        self.root = None
        self.file_id_m : Dict[str,int] = {}
        self.instance_id_m : Dict[Scope,int] = {}
        self.next_instance_id = 0
        pass
    
    def write(self, file, db : UCIS):
        self.db = db

        # Map each of the source files to a unique identifier
        self.file_id_m = {
            "__null__file__" : 1}
        self.find_all_files(db.scopes(ScopeTypeT.ALL)) # TODO: need to handle mask
        
        self.root = et.Element(QName(XmlWriter.UCIS, "UCIS"), nsmap={
#        self.root = et.Element("UCIS", nsmap={
            "ucis" : XmlWriter.UCIS
            })
        # TODO: these aren't really UCIS properties
        self.setAttr(self.root, "writtenBy", getpass.getuser())
        self.setAttrDateTime(self.root, "writtenTime", date.today().strftime("%Y%m%d%H%M%S"))
        
#        self.setAttr(self.root, "writtenBy", db.getWrittenBy())
#        self.setAttrDateTime(self.root, "writtenTime", db.getWrittenTime())
        
        self.setAttr(self.root, "ucisVersion", db.getAPIVersion())
        
        # TODO: collect source files
        self.write_source_files()
        self.write_history_nodes()
        for s in self.db.scopes(ScopeTypeT.INSTANCE):
            self.write_instance_coverages(s)

        for elem in self.root.getiterator():
            if not hasattr(elem.tag, 'find'): continue  # (1)
            i = elem.tag.find('}')
            if i >= 0:
                elem.tag = elem.tag[i+1:]

#        file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
#        file.write("<?xml version=\"1.0\"?>\n")
        file.write(tounicode(self.root, pretty_print=True))
        
    def write_source_files(self):

        for filename,id in self.file_id_m.items():
            fileN = self.mkElem(self.root, "sourceFiles")
            self.setAttr(fileN, "fileName", filename)
            self.setAttr(fileN, "id", str(id))
        
    def write_history_nodes(self):
        
#        histNodes = self.root.SubElement(self.root, "historyNodes")

        have_hist_nodes = False
        for i,h in enumerate(self.db.getHistoryNodes(HistoryNodeKind.ALL)):
            histN = self.mkElem(self.root, "historyNodes")
            histN.set("historyNodeId", str(i))
            have_hist_nodes = True
            
            # TODO: parent
            histN.set("logicalName", h.getLogicalName())
            self.setIfNonNull(histN, "physicalName", h.getPhysicalName())
            self.setIfNonNull(histN, "kind", h.getKind())
            self.setAttrBool(histN, "testStatus", h.getTestStatus())
            self.setIfNonNeg(histN, "simtime", h.getSimTime())
            self.setIfNonNull(histN, "timeunit", h.getTimeUnit())
            self.setIfNonNull(histN, "runCwd", h.getRunCwd())
            self.setIfNonNeg(histN, "cpuTime", h.getCpuTime())
            self.setIfNonNull(histN, "seed", h.getSeed())
            self.setIfNonNull(histN, "cmd", h.getCmd())
            self.setIfNonNull(histN, "args", h.getArgs())
            self.setIfNonNull(histN, "compulsory", h.getCompulsory())
            self.setAttrDateTime(histN, "date", h.getDate())
            self.setIfNonNull(histN, "userName", h.getUserName())
            self.setIfNonNeg(histN, "cost", h.getCost())
            self.setAttr(histN, "toolCategory", h.getToolCategory())
            self.setAttr(histN, "ucisVersion", h.getUCISVersion())
            self.setAttr(histN, "vendorId", h.getVendorId())
            self.setAttr(histN, "vendorTool", h.getVendorTool())
            self.setAttr(histN, "vendorToolVersion", h.getVendorToolVersion())
            self.setIfNonNeg(histN, "sameTests", h.getSameTests())
            self.setIfNonNull(histN, "comment", h.getComment())

        if not have_hist_nodes:
            # XML requires history nodes, so add a dummy history node
            histN = self.mkElem(self.root, "historyNodes")
            histN.set("historyNodeId", str(0))

            histN.set("logicalName", "dummy")
            self.setIfNonNull(histN, "physicalName", "dummy")
            self.setIfNonNull(histN, "kind", "dummy")
            self.setAttrBool(histN, "testStatus", True)
            self.setIfNonNeg(histN, "simtime", 0)
            self.setIfNonNull(histN, "timeunit", 0)
            self.setIfNonNull(histN, "runCwd", "")
            self.setIfNonNeg(histN, "cpuTime", 0)
            self.setIfNonNull(histN, "seed", 0)
            self.setIfNonNull(histN, "cmd", "")
            self.setIfNonNull(histN, "args", "")
#            self.setIfNonNull(histN, "compulsory", h.getCompulsory())
            self.setAttrDateTime(histN, "date", datetime.now().strftime("%Y%m%d%H%M%S"))
            self.setIfNonNull(histN, "userName", "dummy")
#            self.setIfNonNeg(histN, "cost", h.getCost())
            self.setAttr(histN, "toolCategory", "unknown")
            self.setAttr(histN, "ucisVersion", "1.0")
            self.setAttr(histN, "vendorId", "unknown")
            self.setAttr(histN, "vendorTool", "PyUCIS")
            self.setAttr(histN, "vendorToolVersion", "unknown")
#            self.setIfNonNeg(histN, "sameTests", h.getSameTests())
#            self.setIfNonNull(histN, "comment", h.getComment())

            
            # TODO: userAttr
            
    def write_instance_coverages(self, s, parent_instance_id=None):
        # Assign instance ID
        instance_id = self.next_instance_id
        self.instance_id_m[s] = instance_id
        self.next_instance_id += 1
        
        inst = self.mkElem(self.root, "instanceCoverages")
        inst.set("name", s.getScopeName())
        inst.set("key", "0") # TODO:
        inst.set("instanceId", str(instance_id))
        
        # Set moduleName from the DU scope if available
        du_scope = s.getInstanceDu()
        if du_scope is not None:
            inst.set("moduleName", du_scope.getScopeName())
        
        # Set parentInstanceId if this is a child instance
        if parent_instance_id is not None:
            inst.set("parentInstanceId", str(parent_instance_id))
        
        self.addId(inst, s.getSourceInfo())
        
        self.write_covergroups(inst, s)
        
        # Recursively write child instances
        for child in s.scopes(ScopeTypeT.INSTANCE):
            self.write_instance_coverages(child, instance_id)
        
        
    def write_covergroups(self, inst, scope):
        for cg in scope.scopes(ScopeTypeT.COVERGROUP):
            cgElem = self.mkElem(inst, "covergroupCoverage")
#            self.setAttr(cgElem, "weight", str(scope.getWeight()))

            inst_it = cg.scopes(ScopeTypeT.COVERINSTANCE)
            
            cg_inst = next(inst_it, None)
            
            # If there is only type coverage (no instances), write only that
            if cg_inst is None:
                self.write_coverinstance(cgElem, cg.getScopeName(), cg)
            else:
                # If there is instance coverage, write only that
                while cg_inst is not None:
                    self.write_coverinstance(cgElem, cg.getScopeName(), cg_inst)
                    cg_inst = next(inst_it, None)
    
    def write_coverinstance(self, cgElem, cgName, cg : Covergroup):
        cgInstElem = self.mkElem(cgElem, "cgInstance")
        self.setAttr(cgInstElem, "name", cg.getScopeName())
        self.setAttr(cgInstElem, "key", "0")
        
        self.write_options(cgInstElem, cg)
        
        cgIdElem = self.mkElem(cgInstElem, "cgId")
        self.setAttr(cgIdElem, "cgName", cgName)
        self.setAttr(cgIdElem, "moduleName", cgName)
        
        # Instance source information
        cgSourceIdElem = self.mkElem(cgIdElem, "cginstSourceId")
        self.setAttr(cgSourceIdElem, "file", "1")
        self.setAttr(cgSourceIdElem, "line", "1")
        self.setAttr(cgSourceIdElem, "inlineCount", "1")
        
        # Declaration source information
        cgSourceIdElem = self.mkElem(cgIdElem, "cgSourceId")
        self.setAttr(cgSourceIdElem, "file", "1")
        self.setAttr(cgSourceIdElem, "line", "1")
        self.setAttr(cgSourceIdElem, "inlineCount", "1")
        
        for cp in cg.scopes(ScopeTypeT.COVERPOINT):
            self.write_coverpoint(cgInstElem, cp)
            
        for cr in cg.scopes(ScopeTypeT.CROSS):
            self.write_cross(cgInstElem, cr)
            
    def write_coverpoint(self, cgInstElem, cp : Coverpoint):
        cpElem = self.mkElem(cgInstElem, "coverpoint")
        self.setAttr(cpElem, "name", cp.getScopeName())
        self.setAttr(cpElem, "key", "0")
        
        self.write_options(cpElem, cp, is_coverpoint=True)
        
        self.write_coverpoint_bins(cpElem, cp.coverItems(
            CoverTypeT.CVGBIN|CoverTypeT.IGNOREBIN|CoverTypeT.ILLEGALBIN))

    def write_coverpoint_bins(self, cpElem, coveritems : Iterator[CoverIndex]):
        # TODO: should probably organize bins into a structure that fits more nicely into the interchage format
        
        for cp_bin in coveritems:
            cov_data = cp_bin.getCoverData()
            cpBinElem = self.mkElem(cpElem, "coverpointBin")
            self.setAttr(cpBinElem, "name", cp_bin.getName())

            if cp_bin.data.type == CoverTypeT.CVGBIN:
                self.setAttr(cpBinElem, "type", "bins")
            elif cp_bin.data.type == CoverTypeT.IGNOREBIN:
                self.setAttr(cpBinElem, "type", "ignore")
            elif cp_bin.data.type == CoverTypeT.ILLEGALBIN:
                self.setAttr(cpBinElem, "type", "illegal")
            else:
                raise Exception("Unknown bin type %s" % str(cp_bin.type))
            self.setAttr(cpBinElem, "key", "0")
            
            # Now, add the coverage data
            rng = self.mkElem(cpBinElem, "range")

            # The from..to attributes do not contain useful information
            self.setAttr(rng, "from", "-1")
            self.setAttr(rng, "to", "-1")

#            seq = self.mkElem(cpBinElem, "sequence")
            contents = self.mkElem(rng, "contents")
            self.setAttr(contents, "coverageCount", str(cov_data.data))
#            seqValue = self.mkElem(seq, "seqValue")
#            seqValue.text = "-1" # Note: this is a meaningless value
            
    def write_cross(self, cgInstElem, cr):
        crossElem = self.mkElem(cgInstElem, "cross")
        self.setAttr(crossElem, "name", cr.getScopeName())
        self.setAttr(crossElem, "key", "0")
        self.write_options(crossElem, cr, is_cross=True)  # Cross has its own minimal schema

        # Each cross expression lists one element of the cross        

        for i in range(cr.getNumCrossedCoverpoints()):
            crossExpr = self.mkElem(crossElem, "crossExpr")
            crossExpr.text = cr.getIthCrossedCoverpoint(i).getScopeName() 
        
        self.write_cross_bins(crossElem, cr.coverItems(
            CoverTypeT.CVGBIN|CoverTypeT.IGNOREBIN|CoverTypeT.ILLEGALBIN))
        
    def write_cross_bins(self, crossElem, coveritems : Iterator[CoverIndex]):
        
        for cr_bin in coveritems:
            cov_data = cr_bin.getCoverData()
            crBinElem = self.mkElem(crossElem, "crossBin")
            self.setAttr(crBinElem, "name", cr_bin.getName())
            self.setAttr(crBinElem, "key", "0")
            self.setAttr(crBinElem, "type", "default") # TOOD: illegal, ignore
            
            index = self.mkElem(crBinElem, "index")
            index.text = "-1" # Note: this is a meaningless value
            
            contents = self.mkElem(crBinElem, "contents")
            self.setAttr(contents, "coverageCount", str(cov_data.data))
            
    
    def write_options(self, parent, opts_item, is_coverpoint=False, is_cross=False):
        optionsElem = self.mkElem(parent, "options")
        
        # Write covergroup/coverpoint/cross options according to UCIS spec
        try:
            # Common options for all types
            self.setAttr(optionsElem, "weight", str(opts_item.getWeight()))
            
            # Goal: use 100 as default if negative (UCIS default)
            goal = opts_item.getGoal()
            if goal < 0:
                goal = 100
            self.setAttr(optionsElem, "goal", str(goal))
            
            # AtLeast: use 1 as default if <= 0 (UCIS default)
            at_least = opts_item.getAtLeast()
            if at_least <= 0:
                at_least = 1
            self.setAttr(optionsElem, "at_least", str(at_least))
            
            # Covergroup-specific options (not for coverpoints or cross)
            if not is_coverpoint and not is_cross:
                if hasattr(opts_item, 'getPerInstance'):
                    self.setAttrBool(optionsElem, "per_instance", opts_item.getPerInstance())
                if hasattr(opts_item, 'getMergeInstances'):
                    self.setAttrBool(optionsElem, "merge_instances", opts_item.getMergeInstances())
                if hasattr(opts_item, 'getGetInstCoverage'):
                    self.setAttrBool(optionsElem, "get_inst_coverage", opts_item.getGetInstCoverage())
                if hasattr(opts_item, 'getStrobe'):
                    self.setAttrBool(optionsElem, "strobe", opts_item.getStrobe())
                
            # Coverpoint-specific options (not for cross)
            if is_coverpoint and not is_cross:
                if hasattr(opts_item, 'getAutoBinMax'):
                    auto_bin_max = opts_item.getAutoBinMax()
                    if auto_bin_max <= 0:
                        auto_bin_max = 64  # UCIS default
                    self.setAttr(optionsElem, "auto_bin_max", str(auto_bin_max))
                if hasattr(opts_item, 'getDetectOverlap'):
                    self.setAttrBool(optionsElem, "detect_overlap", opts_item.getDetectOverlap())
        except (AttributeError, NotImplementedError):
            # If methods don't exist, just skip them
            pass
        

    def write_statement_id(self, stmt_id : StatementId, p, name="id"):
        stmtN = self.mkElem(p, name)
        # TODO: 
        file_id = self.file_id_m[stmt_id.getFile()]+1
        self.setAttr(stmtN, "file", str(file_id))
        self.setAttr(stmtN, "line", str(stmt_id.getLine()))
        self.setAttr(stmtN, "inlineCount", str(stmt_id.getItem()))
        
            
    def mkElem(self, p, name):
        # Creates a UCIS-qualified node
        return SubElement(p, QName(XmlWriter.UCIS, name))
        
    def setAttr(self, e, name, val):
#        e.set(QName(XmlWriter.UCIS, name), val)
        e.set(name, val)
        
    def setAttrBool(self, e, name, val):
        if val:
            e.set(name, "true")
        else:
            e.set(name, "false")

    def setAttrDateTime(self, e, name, val):
        val_i = time.mktime(datetime.strptime(val, "%Y%m%d%H%M%S").timetuple())
        self.setAttr(e, name, datetime.fromtimestamp(val_i).isoformat())
            
    def setIfNonNull(self, n, attr, val):
        if val is not None:
            self.setAttr(n, attr, str(val))
            
    def setIfNonNeg(self, n, attr, val):
        if val >= 0:
            self.setAttr(n, attr, str(val))
            
    def addId(self, ctxt, srcinfo):
        idElem = self.mkElem(ctxt, "id")
        if srcinfo is None or srcinfo.file is None:
            fileid = 1
        else:
            fileid = self.file_id_m[srcinfo.file.getFileName()]
        self.setAttr(idElem, "file", str(fileid))
            
        # XML schema requires positiveInteger (>= 1) for line and inlineCount
        line = 1
        if srcinfo is not None and srcinfo.line >= 1:
            line = srcinfo.line
        self.setAttr(idElem, "line", str(line))
        
        inlineCount = 1
        if srcinfo is not None and srcinfo.token >= 1:
            inlineCount = srcinfo.token
        self.setAttr(idElem, "inlineCount", str(inlineCount))
        

    def find_all_files(self, scope_i : Iterator[Scope]):
        for s in scope_i:
            srcinfo = s.getSourceInfo()
            
            if srcinfo.file is not None:
                filename = srcinfo.file.getFileName()
                if filename not in self.file_id_m.keys():
                    id = len(self.file_id_m)+1
                    self.file_id_m[filename] = id
                    
            self.find_all_files(s.scopes(ScopeTypeT.ALL))
            
