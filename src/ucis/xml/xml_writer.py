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
    
    def write(self, file, db : UCIS, ctx=None):
        self.db = db
        self.ctx = ctx

        # Map each of the source files to a unique identifier
        self.file_id_m = {
            "__null__file__" : 1}
        self.find_all_files(db.scopes(ScopeTypeT.ALL)) # TODO: need to handle mask
        
        self.root = et.Element(QName(XmlWriter.UCIS, "UCIS"), nsmap={
#        self.root = et.Element("UCIS", nsmap={
            "ucis" : XmlWriter.UCIS
            })
        # TODO: these aren't really UCIS properties
        wb = db.getWrittenBy()
        self.setAttr(self.root, "writtenBy", wb if wb else getpass.getuser())
        wt = db.getWrittenTime()
        if wt:
            self.setAttrDateTime(self.root, "writtenTime", wt)
        else:
            self.setAttrDateTime(self.root, "writtenTime",
                                 date.today().strftime("%Y%m%d%H%M%S"))
        
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
        node_id_m = {}  # maps history node object → assigned id
        for i,h in enumerate(self.db.getHistoryNodes(HistoryNodeKind.ALL)):
            node_id_m[id(h)] = i
            histN = self.mkElem(self.root, "historyNodes")
            histN.set("historyNodeId", str(i))
            have_hist_nodes = True

            parent = h.getParent()
            if parent is not None and id(parent) in node_id_m:
                histN.set("parentId", str(node_id_m[id(parent)]))

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
            
    def write_user_attrs(self, elem, scope):
        """Emit <userAttr> children for any attributes on the scope."""
        if not hasattr(scope, 'getAttributes'):
            return
        for key, val in scope.getAttributes().items():
            attrN = self.mkElem(elem, "userAttr")
            attrN.set("key", key)
            attrN.set("type", "str")
            attrN.text = str(val)

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
        self.write_toggle_coverage(inst, s)
        self.write_block_coverage(inst, s)
        self.write_branch_coverage(inst, s)
        self.write_fsm_coverage(inst, s)
        self.write_assertion_coverage(inst, s)
        self.write_condition_coverage(inst, s)
        self.write_user_attrs(inst, s)
        
        # Recursively write child instances
        for child in s.scopes(ScopeTypeT.INSTANCE):
            self.write_instance_coverages(child, instance_id)
        
        
    def write_toggle_coverage(self, inst_elem, scope):
        toggle_scopes = list(scope.scopes(ScopeTypeT.TOGGLE))
        if not toggle_scopes:
            return
        tc_elem = self.mkElem(inst_elem, "toggleCoverage")
        for i, toggle_scope in enumerate(toggle_scopes):
            to_elem = self.mkElem(tc_elem, "toggleObject")
            to_elem.set("name", toggle_scope.getScopeName())
            to_elem.set("key", str(i))
            self.addId(to_elem, toggle_scope.getSourceInfo())
            bins = list(toggle_scope.coverItems(CoverTypeT.TOGGLEBIN))
            if bins:
                tb_elem = self.mkElem(to_elem, "toggleBit")
                tb_elem.set("name", "bit0")
                tb_elem.set("key", "0")
                for bin_item in bins:
                    name = bin_item.getName()
                    if "->" in name:
                        parts = name.split("->", 1)
                        from_val, to_val = parts[0].strip(), parts[1].strip()
                    elif "to" in name.lower():
                        parts = name.lower().split("to", 1)
                        from_val, to_val = parts[0], parts[1]
                    else:
                        from_val, to_val = "0", "1"
                    toggle_elem = self.mkElem(tb_elem, "toggle")
                    toggle_elem.set("from", from_val)
                    toggle_elem.set("to", to_val)
                    bin_elem = self.mkElem(toggle_elem, "bin")
                    contents_elem = self.mkElem(bin_elem, "contents")
                    contents_elem.set("coverageCount", str(bin_item.getCoverData().data))
        self.write_user_attrs(tc_elem, scope)

    def write_block_coverage(self, inst_elem, scope):
        block_scopes = list(scope.scopes(ScopeTypeT.BLOCK))
        if not block_scopes:
            return
        bc_elem = self.mkElem(inst_elem, "blockCoverage")
        for block_scope in block_scopes:
            stmts = list(block_scope.coverItems(CoverTypeT.STMTBIN))
            for stmt in stmts:
                stmt_elem = self.mkElem(bc_elem, "statement")
                stmt_elem.set("alias", stmt.getName())  # use alias to preserve name
                self.addId(stmt_elem, stmt.getSourceInfo())
                bin_elem = self.mkElem(stmt_elem, "bin")
                contents_elem = self.mkElem(bin_elem, "contents")
                contents_elem.set("coverageCount", str(stmt.getCoverData().data))
        self.write_user_attrs(bc_elem, scope)

    def write_branch_coverage(self, inst_elem, scope):
        branch_scopes = list(scope.scopes(ScopeTypeT.BRANCH))
        if not branch_scopes:
            return
        bc_elem = self.mkElem(inst_elem, "branchCoverage")
        for i, branch_scope in enumerate(branch_scopes):
            stmt_elem = self.mkElem(bc_elem, "statement")
            stmt_elem.set("statementType", "if")
            stmt_elem.set("branchExpr", branch_scope.getScopeName())
            self.addId(stmt_elem, branch_scope.getSourceInfo())
            arms = list(branch_scope.coverItems(CoverTypeT.BRANCHBIN))
            for j, arm in enumerate(arms):
                branch_elem = self.mkElem(stmt_elem, "branch")
                self.addId(branch_elem, arm.getSourceInfo())
                bb_elem = self.mkElem(branch_elem, "branchBin")
                bb_elem.set("alias", arm.getName())  # use alias to preserve name
                contents_elem = self.mkElem(bb_elem, "contents")
                contents_elem.set("coverageCount", str(arm.getCoverData().data))
        self.write_user_attrs(bc_elem, scope)

    def write_fsm_coverage(self, inst_elem, scope):
        fsm_scopes = list(scope.scopes(ScopeTypeT.FSM))
        if not fsm_scopes:
            return
        fc_elem = self.mkElem(inst_elem, "fsmCoverage")
        for fsm_scope in fsm_scopes:
            fsm_elem = self.mkElem(fc_elem, "fsm")
            fsm_elem.set("name", fsm_scope.getScopeName())
            fsm_elem.set("type", "reg")
            fsm_elem.set("width", "1")
            # FSMBIN items live in FSM_STATES and FSM_TRANS child scopes (LRM 6.5.6)
            state_bins = []
            for ss in fsm_scope.scopes(ScopeTypeT.FSM_STATES):
                state_bins.extend(ss.coverItems(CoverTypeT.FSMBIN))
            trans_bins = []
            for ts in fsm_scope.scopes(ScopeTypeT.FSM_TRANS):
                trans_bins.extend(ts.coverItems(CoverTypeT.FSMBIN))
            # States must come before transitions in XML (schema order)
            for i, bin_item in enumerate(state_bins):
                state_elem = self.mkElem(fsm_elem, "state")
                state_elem.set("stateName", bin_item.getName())
                state_elem.set("stateValue", str(i))
                sb_elem = self.mkElem(state_elem, "stateBin")
                contents = self.mkElem(sb_elem, "contents")
                contents.set("coverageCount", str(bin_item.getCoverData().data))
            for bin_item in trans_bins:
                parts = bin_item.getName().split("->", 1)
                trans_elem = self.mkElem(fsm_elem, "stateTransition")
                from_elem = self.mkElem(trans_elem, "state")
                from_elem.text = parts[0].strip() if len(parts) > 1 else bin_item.getName()
                to_elem = self.mkElem(trans_elem, "state")
                to_elem.text = parts[1].strip() if len(parts) > 1 else ""
                tb_elem = self.mkElem(trans_elem, "transitionBin")
                contents = self.mkElem(tb_elem, "contents")
                contents.set("coverageCount", str(bin_item.getCoverData().data))
        self.write_user_attrs(fc_elem, scope)

    def write_assertion_coverage(self, inst_elem, scope):
        assert_scopes = (list(scope.scopes(ScopeTypeT.ASSERT))
                         + list(scope.scopes(ScopeTypeT.COVER)))
        if not assert_scopes:
            return
        ac_elem = self.mkElem(inst_elem, "assertionCoverage")
        # XML schema requires bins in this fixed order
        _ASSERT_BIN_ORDER = [
            (CoverTypeT.COVERBIN,      "coverBin"),
            (CoverTypeT.PASSBIN,       "passBin"),
            (CoverTypeT.ASSERTBIN,     "failBin"),   # assert fail → failBin
            (CoverTypeT.FAILBIN,       "failBin"),   # cover fail → failBin
            (CoverTypeT.VACUOUSBIN,    "vacuousBin"),
            (CoverTypeT.DISABLEDBIN,   "disabledBin"),
            (CoverTypeT.ATTEMPTBIN,    "attemptBin"),
            (CoverTypeT.ACTIVEBIN,     "activeBin"),
            (CoverTypeT.PEAKACTIVEBIN, "peakActiveBin"),
        ]
        for assert_scope in assert_scopes:
            kind = ("assert" if assert_scope.getScopeType() & ScopeTypeT.ASSERT
                    else "cover")
            asrt_elem = self.mkElem(ac_elem, "assertion")
            asrt_elem.set("name", assert_scope.getScopeName())
            asrt_elem.set("assertionKind", kind)
            emitted = set()
            for cover_type, xml_name in _ASSERT_BIN_ORDER:
                if xml_name in emitted:
                    continue  # don't emit failBin twice
                bins = list(assert_scope.coverItems(cover_type))
                if bins:
                    emitted.add(xml_name)
                    bin_elem = self.mkElem(asrt_elem, xml_name)
                    contents = self.mkElem(bin_elem, "contents")
                    contents.set("coverageCount",
                                 str(sum(b.getCoverData().data for b in bins)))
        self.write_user_attrs(ac_elem, scope)

    def write_condition_coverage(self, inst_elem, scope):
        cond_scopes = list(scope.scopes(ScopeTypeT.COND))
        if not cond_scopes:
            return
        cc_elem = self.mkElem(inst_elem, "conditionCoverage")
        cc_elem.set("metricMode", "UCIS:STD")
        for key, cond_scope in enumerate(cond_scopes):
            src = cond_scope.getSourceInfo()
            if src and src.file:
                file_id = self.file_id_m.get(src.file.getFileName(), 1)
                line = src.line if src.line >= 1 else 1
            else:
                file_id = 1
                line = 1
            uid = f"#cond#{file_id}#{line}#{key}#"
            expr_elem = self.mkElem(cc_elem, "expr")
            expr_elem.set("name", uid)
            expr_elem.set("key", str(key))
            expr_elem.set("exprString", cond_scope.getScopeName())
            expr_elem.set("index", "0")
            expr_elem.set("width", "1")
            self.addId(expr_elem, src)
            bins = list(cond_scope.coverItems(CoverTypeT.CONDBIN))
            # Infer input count from max length of binary-vector bin names
            binary_names = [b.getName() for b in bins
                            if all(c in '01-' for c in b.getName())]
            n_inputs = max((len(n) for n in binary_names), default=1) if binary_names else 1
            # Emit placeholder subExpr names (signal names not available in DM)
            for i in range(n_inputs):
                sub_elem = self.mkElem(expr_elem, "subExpr")
                sub_elem.text = f"_input_{i}"
            for bin_item in bins:
                bin_elem = self.mkElem(expr_elem, "bin")
                bin_elem.set("alias", bin_item.getName())
                contents_elem = self.mkElem(bin_elem, "contents")
                contents_elem.set("coverageCount", str(bin_item.getCoverData().data))
        self.write_user_attrs(cc_elem, scope)

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

            bin_type = cp_bin.getCoverData().type
            if bin_type == CoverTypeT.CVGBIN:
                self.setAttr(cpBinElem, "type", "bins")
            elif bin_type == CoverTypeT.IGNOREBIN:
                self.setAttr(cpBinElem, "type", "ignore")
            elif bin_type == CoverTypeT.ILLEGALBIN:
                self.setAttr(cpBinElem, "type", "illegal")
            else:
                raise Exception("Unknown bin type %s" % str(bin_type))
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
        if val is None:
            return
        # If val is an integer, treat it as a Unix timestamp directly
        if isinstance(val, int):
            self.setAttr(e, name, datetime.fromtimestamp(val).isoformat())
            return
        # Try the standard UCIS format first, then common ISO variants
        for fmt in ("%Y%m%d%H%M%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
            try:
                val_i = time.mktime(datetime.strptime(val, fmt).timetuple())
                self.setAttr(e, name, datetime.fromtimestamp(val_i).isoformat())
                return
            except ValueError:
                pass
        # If no format matched, store the raw value to avoid data loss
        self.setAttr(e, name, val)
            
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
            
