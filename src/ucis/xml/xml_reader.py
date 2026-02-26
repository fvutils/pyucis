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
import logging
from io import StringIO
from logging import _srcfile
import sys
from typing import Dict
from xml.dom.minidom import Element

from lxml import etree
from ucis import UCIS_ENABLED_STMT, UCIS_ENABLED_BRANCH, UCIS_ENABLED_COND, \
    UCIS_ENABLED_EXPR, UCIS_ENABLED_FSM, UCIS_ENABLED_TOGGLE, UCIS_INST_ONCE, \
    UCIS_SCOPE_UNDER_DU, UCIS_DU_MODULE, UCIS_OTHER, du_scope, UCIS_INSTANCE,\
    UCIS_CVGBIN, UCIS_IGNOREBIN, UCIS_ILLEGALBIN, UCIS_VLOG
from ucis.cover_data import CoverData
from ucis.cover_type_t import CoverTypeT
from ucis.scope_type_t import ScopeTypeT
from ucis.mem.mem_file_handle import MemFileHandle
from ucis.mem.mem_scope import MemScope
from ucis.mem.mem_ucis import MemUCIS
from ucis.source_info import SourceInfo
from ucis.statement_id import StatementId
from ucis.ucis import UCIS
from ucis.xml import validate_ucis_xml


class XmlReader():
    
    def __init__(self):
        self.file_m : Dict[int,MemFileHandle] = {}
        self.module_scope_m : Dict[str, MemScope] = {}
        self.inst_scope_m : Dict[str, MemScope] = {}
        self.inst_id_m : Dict[int, MemScope] = {}  # Map instanceId to scope

    @staticmethod
    def read_user_attrs(elem, scope):
        """Read <userAttr> children from elem and set them on scope."""
        for child in elem:
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if tag == "userAttr":
                key = child.get("key")
                if key and hasattr(scope, 'setAttribute'):
                    scope.setAttribute(key, child.text or "")

    def loads(self, s) -> UCIS:
        fp = StringIO(s)
        return self.read(fp)


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
            
        hist_id_m = {}  # maps historyNodeId → node object
        for histN in tree.iter("historyNodes"):
            node_id = int(histN.get("historyNodeId", 0))
            node = self.readHistoryNode(histN)
            hist_id_m[node_id] = node

        # Wire parent relationships now that all nodes are created
        for histN in tree.iter("historyNodes"):
            parent_id_str = histN.get("parentId")
            if parent_id_str is not None:
                node_id = int(histN.get("historyNodeId", 0))
                parent_node = hist_id_m.get(int(parent_id_str))
                if parent_node is not None:
                    hist_id_m[node_id].m_parent = parent_node

        for instN in tree.iter("instanceCoverages"):
            self.readInstanceCoverage(instN)
            
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
        kind_str = self.getAttr(histN, "kind", None)
        # Convert string kind to HistoryNodeKind enum
        from ucis.history_node_kind import HistoryNodeKind
        if kind_str is not None:
            try:
                kind = HistoryNodeKind(int(kind_str))
            except (ValueError, KeyError):
                kind = HistoryNodeKind.TEST
        else:
            kind = HistoryNodeKind.TEST
        
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
        instance_id = self.getAttr(instN, "instanceId", None)
        parent_instance_id = self.getAttr(instN, "parentInstanceId", None)
        
        # Read source info from <id> element
        srcinfo = None
        for stmt_idN in instN.iter("id"):
            stmt_id = self.readStatementId(stmt_idN)
            # Convert StatementId to SourceInfo (item -> token)
            srcinfo = SourceInfo(stmt_id.file, stmt_id.line, stmt_id.item)
            break  # Only first one
            
        # Get module/DU scope
        module_scope_name = self.getAttr(instN, "moduleName", "default")
        type_scope = self.getScope(
            module_scope_name, 
            None, 
            UCIS_OTHER) # TODO: how do we determine source type?
        
        # Determine parent scope
        parent_scope = None
        if parent_instance_id is not None:
            parent_id = int(parent_instance_id)
            parent_scope = self.inst_id_m.get(parent_id, None)
        
        # Create instance under parent (or at top level if no parent)
        if parent_scope is None:
            inst_scope = self.db.createInstance(
                name,
                srcinfo,
                1,  # Weight not in XML schema
                UCIS_OTHER,
                UCIS_INSTANCE,
                type_scope,
                UCIS_INST_ONCE)
        else:
            inst_scope = parent_scope.createInstance(
                name,
                srcinfo,
                1,  # Weight not in XML schema
                UCIS_OTHER,
                UCIS_INSTANCE,
                type_scope,
                UCIS_INST_ONCE)
        
        # Store in lookup maps
        self.inst_scope_m[name] = inst_scope
        if instance_id is not None:
            self.inst_id_m[int(instance_id)] = inst_scope
        
        # Read coverage content
        for cg in instN.iter("covergroupCoverage"):
            self.readCovergroups(cg, inst_scope, module_scope_name)
        for tc in instN.iter("toggleCoverage"):
            self.readToggleCoverage(tc, inst_scope)
        for bc in instN.iter("blockCoverage"):
            self.readBlockCoverage(bc, inst_scope)
        for br in instN.iter("branchCoverage"):
            self.readBranchCoverage(br, inst_scope)
        for fc in instN.iter("fsmCoverage"):
            self.readFsmCoverage(fc, inst_scope)
        for ac in instN.iter("assertionCoverage"):
            self.readAssertionCoverage(ac, inst_scope)
        self.read_user_attrs(instN, inst_scope)

    def readToggleCoverage(self, tc_elem, inst_scope):
        for to_elem in tc_elem:
            local_tag = to_elem.tag.split("}")[-1] if "}" in to_elem.tag else to_elem.tag
            if local_tag != "toggleObject":
                continue
            name = to_elem.get("name", "toggle")
            srcinfo = None
            for id_elem in to_elem:
                id_local = id_elem.tag.split("}")[-1] if "}" in id_elem.tag else id_elem.tag
                if id_local == "id":
                    file_id = int(id_elem.get("file", "1"))
                    line = int(id_elem.get("line", "1"))
                    token = int(id_elem.get("inlineCount", "1"))
                    srcinfo = SourceInfo(self.file_m.get(file_id), line, token)
                    break
            toggle_scope = inst_scope.createScope(
                name, srcinfo, 1, UCIS_VLOG, ScopeTypeT.TOGGLE, UCIS_ENABLED_TOGGLE)
            for tb_elem in to_elem:
                tb_local = tb_elem.tag.split("}")[-1] if "}" in tb_elem.tag else tb_elem.tag
                if tb_local != "toggleBit":
                    continue
                for toggle_elem in tb_elem:
                    tg_local = toggle_elem.tag.split("}")[-1] if "}" in toggle_elem.tag else toggle_elem.tag
                    if tg_local != "toggle":
                        continue
                    from_val = toggle_elem.get("from", "0")
                    to_val = toggle_elem.get("to", "1")
                    bin_name = from_val + "to" + to_val
                    count = 0
                    for bin_elem in toggle_elem:
                        b_local = bin_elem.tag.split("}")[-1] if "}" in bin_elem.tag else bin_elem.tag
                        if b_local == "bin":
                            for c_elem in bin_elem:
                                c_local = c_elem.tag.split("}")[-1] if "}" in c_elem.tag else c_elem.tag
                                if c_local == "contents":
                                    count = int(c_elem.get("coverageCount", "0"))
                    cd = CoverData(CoverTypeT.TOGGLEBIN, 0)
                    cd.data = count
                    toggle_scope.createNextCover(bin_name, cd, srcinfo)
        self.read_user_attrs(tc_elem, inst_scope)

    def readBlockCoverage(self, bc_elem, inst_scope):
        block_scope = inst_scope.createScope(
            "block", None, 1, UCIS_VLOG, ScopeTypeT.BLOCK, UCIS_ENABLED_STMT)
        for stmt_elem in bc_elem:
            local_tag = stmt_elem.tag.split("}")[-1] if "}" in stmt_elem.tag else stmt_elem.tag
            if local_tag != "statement":
                continue
            stmt_name = stmt_elem.get("alias", "stmt")
            srcinfo = None
            count = 0
            for child in stmt_elem:
                child_local = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                if child_local == "id":
                    file_id = int(child.get("file", "1"))
                    line = int(child.get("line", "1"))
                    token = int(child.get("inlineCount", "1"))
                    srcinfo = SourceInfo(self.file_m.get(file_id), line, token)
                elif child_local == "bin":
                    for c_elem in child:
                        c_local = c_elem.tag.split("}")[-1] if "}" in c_elem.tag else c_elem.tag
                        if c_local == "contents":
                            count = int(c_elem.get("coverageCount", "0"))
            cd = CoverData(CoverTypeT.STMTBIN, 0)
            cd.data = count
            block_scope.createNextCover(stmt_name, cd, srcinfo)
        self.read_user_attrs(bc_elem, inst_scope)

    def readBranchCoverage(self, bc_elem, inst_scope):
        for stmt_elem in bc_elem:
            local_tag = stmt_elem.tag.split("}")[-1] if "}" in stmt_elem.tag else stmt_elem.tag
            if local_tag != "statement":
                continue
            srcinfo = None
            for id_elem in stmt_elem:
                id_local = id_elem.tag.split("}")[-1] if "}" in id_elem.tag else id_elem.tag
                if id_local == "id":
                    file_id = int(id_elem.get("file", "1"))
                    line = int(id_elem.get("line", "1"))
                    token = int(id_elem.get("inlineCount", "1"))
                    srcinfo = SourceInfo(self.file_m.get(file_id), line, token)
                    break
            branch_name = stmt_elem.get("branchExpr", "branch")
            branch_scope = inst_scope.createScope(
                branch_name, srcinfo, 1, UCIS_VLOG, ScopeTypeT.BRANCH, UCIS_ENABLED_BRANCH)
            for branch_elem in stmt_elem:
                b_local = branch_elem.tag.split("}")[-1] if "}" in branch_elem.tag else branch_elem.tag
                if b_local != "branch":
                    continue
                arm_srcinfo = None
                count = 0
                arm_name = "arm"
                for child in branch_elem:
                    c_local = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                    if c_local == "id":
                        file_id = int(child.get("file", "1"))
                        line = int(child.get("line", "1"))
                        token = int(child.get("inlineCount", "1"))
                        arm_srcinfo = SourceInfo(self.file_m.get(file_id), line, token)
                    elif c_local == "branchBin":
                        arm_name = child.get("alias", "arm")
                        for cc in child:
                            cc_local = cc.tag.split("}")[-1] if "}" in cc.tag else cc.tag
                            if cc_local == "contents":
                                count = int(cc.get("coverageCount", "0"))
                cd = CoverData(CoverTypeT.BRANCHBIN, 0)
                cd.data = count
                branch_scope.createNextCover(arm_name, cd, arm_srcinfo or srcinfo)
        self.read_user_attrs(bc_elem, inst_scope)

    def readFsmCoverage(self, fc_elem, inst_scope):
        for fsm_elem in fc_elem:
            local = fsm_elem.tag.split("}")[-1] if "}" in fsm_elem.tag else fsm_elem.tag
            if local != "fsm":
                continue
            name = fsm_elem.get("name", "fsm")
            fsm_scope = inst_scope.createScope(
                name, None, 1, UCIS_VLOG, ScopeTypeT.FSM, UCIS_ENABLED_FSM)
            for child in fsm_elem:
                child_local = (child.tag.split("}")[-1]
                               if "}" in child.tag else child.tag)
                if child_local == "state":
                    state_name = child.get("stateName", "state")
                    count = 0
                    for sb in child:
                        sb_l = sb.tag.split("}")[-1] if "}" in sb.tag else sb.tag
                        if sb_l == "stateBin":
                            for c in sb:
                                c_l = c.tag.split("}")[-1] if "}" in c.tag else c.tag
                                if c_l == "contents":
                                    count = int(c.get("coverageCount", "0"))
                    cd = CoverData(CoverTypeT.FSMBIN, 0)
                    cd.data = count
                    fsm_scope.createNextCover(state_name, cd, None)
                elif child_local == "stateTransition":
                    states, count = [], 0
                    for t in child:
                        t_l = t.tag.split("}")[-1] if "}" in t.tag else t.tag
                        if t_l == "state":
                            states.append(t.text.strip() if t.text else "")
                        elif t_l == "transitionBin":
                            for c in t:
                                c_l = c.tag.split("}")[-1] if "}" in c.tag else c.tag
                                if c_l == "contents":
                                    count = int(c.get("coverageCount", "0"))
                    if len(states) >= 2:
                        cd = CoverData(CoverTypeT.FSMBIN, 0)
                        cd.data = count
                        fsm_scope.createNextCover("->".join(states), cd, None)
        self.read_user_attrs(fc_elem, inst_scope)

    def readAssertionCoverage(self, ac_elem, inst_scope):
        _XML_TO_BIN = {
            "assert": {
                "failBin":      CoverTypeT.ASSERTBIN,
                "passBin":      CoverTypeT.PASSBIN,
                "vacuousBin":   CoverTypeT.VACUOUSBIN,
                "disabledBin":  CoverTypeT.DISABLEDBIN,
                "attemptBin":   CoverTypeT.ATTEMPTBIN,
                "activeBin":    CoverTypeT.ACTIVEBIN,
                "peakActiveBin": CoverTypeT.PEAKACTIVEBIN,
            },
            "cover": {
                "coverBin":     CoverTypeT.COVERBIN,
                "failBin":      CoverTypeT.FAILBIN,
                "passBin":      CoverTypeT.PASSBIN,
                "vacuousBin":   CoverTypeT.VACUOUSBIN,
                "disabledBin":  CoverTypeT.DISABLEDBIN,
                "attemptBin":   CoverTypeT.ATTEMPTBIN,
                "activeBin":    CoverTypeT.ACTIVEBIN,
                "peakActiveBin": CoverTypeT.PEAKACTIVEBIN,
            },
        }
        for asrt_elem in ac_elem:
            local = (asrt_elem.tag.split("}")[-1]
                     if "}" in asrt_elem.tag else asrt_elem.tag)
            if local != "assertion":
                continue
            name = asrt_elem.get("name", "assertion")
            kind = asrt_elem.get("assertionKind", "assert")
            scope_type = (ScopeTypeT.ASSERT if kind == "assert"
                          else ScopeTypeT.COVER)
            assert_scope = inst_scope.createScope(
                name, None, 1, UCIS_VLOG, scope_type, 0)
            bin_map = _XML_TO_BIN.get(kind, _XML_TO_BIN["assert"])
            for bin_elem in asrt_elem:
                bin_local = (bin_elem.tag.split("}")[-1]
                             if "}" in bin_elem.tag else bin_elem.tag)
                cover_type = bin_map.get(bin_local)
                if cover_type is None:
                    continue
                count = 0
                for c in bin_elem:
                    c_l = c.tag.split("}")[-1] if "}" in c.tag else c.tag
                    if c_l == "contents":
                        count = int(c.get("coverageCount", "0"))
                cd = CoverData(cover_type, 0)
                cd.data = count
                assert_scope.createNextCover(bin_local, cd, None)
        self.read_user_attrs(ac_elem, inst_scope)

    def readCovergroups(self, cg, inst_scope, module_scope_name):
        # This entry is for a given covergroup type
        
        cg_typescope = None
        covergroup_scope = None

        # The name attribute associated with each cgInstance is the
        # covergroup instance name. The type name is stored in the 
        # cgId entity / cgName attribute

        cg_type_m = {}

        instances = [i for i in cg.iter("cgInstance")]

        for i in cg.iter("cgInstance"):
            try:
                cgId_l = next(i.iter("cgId"))
                typename = self.getAttr(cgId_l, "cgName", "xxx")
            except:
                typename = "default"

            if typename in cg_type_m.keys():
                cg_type_m[typename].append(i)
            else:
                cg_type_m[typename] = [i]

        # UCIS XML coverage data only has instance information.
        # The reader is responsible for reconstructing the 
        # type coverage information
        for cg_typename in cg_type_m.keys():
            cg_typescope = inst_scope.createCovergroup(
                cg_typename,
                None,
                1,
                UCIS_OTHER)
            
            # Read options from first instance (type-level options)
            if len(cg_type_m[cg_typename]) > 0:
                self.readOptions(cg_type_m[cg_typename][0], cg_typescope)

            # Process all instances of a given covergroup type
            self.readCovergroup(cg_typescope, cg_type_m[cg_typename])

    def readCovergroup(self, cg_t, cg_l):

        cr_m = {}
        cp_m = {}

        # Create a merged understanding of all covergroup instances
        cg_inst_l = []
        for cg_e in cg_l:
            srcinfo = None

            cg_i_name = self.getAttr(cg_e, "name", "<unknown>")
            cg_i = cg_t.createCoverInstance(
                cg_i_name, 
                srcinfo,
                1,
                UCIS_OTHER)
            
            # Read covergroup instance options
            self.readOptions(cg_e, cg_i)

            # Build up a map of coverpoint name/inst-handle refs
            cg_inst_cp_m = {}

            for cp_e in cg_e.iter("coverpoint"):
                cp_name = self.getAttr(cp_e, "name", "<unknown>")

                if cp_name not in cp_m.keys():
                    # New coverpoint. Create type and instance
                    # representations
                    cp_t = cg_t.createCoverpoint(
                        cp_name,
                        srcinfo,
                        1,
                        UCIS_OTHER)
                    
                    # Read coverpoint options
                    self.readOptions(cp_e, cp_t)

                    # Tuple of coverpoint type and map between
                    # bin name and count
                    cp_i = (cp_t, {})
                    cp_m[cp_name] = cp_i
                else:
                    # Already-known coverpoint. Only create
                    # new instance representation
                    cp_i = cp_m[cp_name]

                cp_inst = self.readCoverpointInst(cg_i, cp_e, cp_i)
                
                # Also read options for instance
                self.readOptions(cp_e, cp_inst)
                
                cg_inst_cp_m[cp_name] = cp_inst

            for cr_e in cg_e.iter("cross"):
                cp_name = self.getAttr(cr_e, "name", "<unknown>")

                if cp_name not in cr_m.keys():
                    cp_l = []
                    for crossExpr in cr_e.iter("crossExpr"):
                        cp_n = crossExpr.text.strip()
                        logging.debug("cp_n=\"" + cp_n + "\"")
                        if cp_n in cp_m.keys():
                            cp_l.append(cp_m[cp_n][0])
                        else:
                            raise Exception("Cross %s references missing coverpoint %s" % (
                                cp_name, cp_n))

                    # New crosspoint
                    cr_t = cg_t.createCross(
                        cp_name,
                        srcinfo,
                        1,
                        UCIS_OTHER,
                        cp_l)

                    cr_i = (cr_t, {})
                    cr_m[cp_name] = cr_i
                else:
                    # Already-known crosspoint. Only create
                    # new instance representation
                    cr_i = cr_m[cp_name]
                
                self.readCrossInst(cg_i, cr_e, cr_i, cg_inst_cp_m)

        # Now, create the type info
        for cp_name in cp_m.keys():
            self.populateCoverpointType(cp_m[cp_name][0], cp_m[cp_name][1])

        # Now, create the cross type info
        for cr_name in cr_m.keys():
            self.populateCrossType(
                cr_m[cr_name][0],
                cr_m[cr_name][1])

        pass
                
    def readCoverpointInst(self, cg_i, cp_e, cp_type_i):
        srcinfo = None
        
        cp = cg_i.createCoverpoint(
            self.getAttr(cp_e, "name", "<unknown>"),
            srcinfo,
            1, # weight
            UCIS_OTHER)
        
        for cpBin in cp_e.iter("coverpointBin"):
            self.readCoverpointBin(cpBin, cp, cp_type_i)
            
        return cp
            
    def readCoverpointBin(self, cpBin : Element, cp, cp_type_i):
        srcinfo = None

        seq = next(cpBin.iter("sequence"),None)
        rng = next(cpBin.iter("range"),None)

        if seq is not None:
            contents = next(seq.iter("contents"))
        elif rng is not None:
            contents = next(rng.iter("contents"))
        else:
            raise Exception("Format error: neither 'sequence' nor 'range' present")

        kind_a = self.getAttr(cpBin, "type", "default")
        kind = UCIS_CVGBIN
        
        if kind_a == "bins" or kind_a == "default":
            kind = UCIS_CVGBIN
        elif kind_a == "ignore":
            kind = UCIS_IGNOREBIN
        elif kind_a == "illegal":
            kind = UCIS_ILLEGALBIN
        else:
            raise Exception("Unknown bin type %s" % str(kind_a))
        
        cp_bin_name = self.getAttr(cpBin, "name", "<unknown>")
        cp_bin_count = self.getAttrInt(contents, "coverageCount")

        if cp_bin_name not in cp_type_i[1].keys():
            cp_type_i[1][cp_bin_name] = (kind, cp_bin_count)
        else:
            entry = cp_type_i[1][cp_bin_name]
            cp_type_i[1][cp_bin_name] = (entry[0], entry[1] + cp_bin_count)
        
        cp.createBin(
            cp_bin_name,
            srcinfo,
            1,
            cp_bin_count,
            self.getAttr(cpBin, "name", "default"),
            kind)
        
    def populateCoverpointType(self, cp_t, cp_bin_m):
        srcinfo = None

        for bin_name,(kind,count) in cp_bin_m.items():
            cp_t.createBin(
                bin_name,
                srcinfo,
                1,
                count,
                bin_name,
                kind)

    def readCrossInst(self, cg_i, cr_e, cr_type_i, cp_m):
        name = self.getAttr(cr_e, "name", "<unknown>")
        
        cp_l = []
        for crossExpr in cr_e.iter("crossExpr"):
            cp_n = crossExpr.text.strip()
            logging.debug("cp_n=\"" + cp_n + "\"")
            if cp_n in cp_m.keys():
                cp_l.append(cp_m[cp_n])
            else:
                raise Exception("Cross " + cp_n + " references missing coverpoint " + cp_n)

        srcinfo = None
        
        cr = cg_i.createCross(
            name,
            srcinfo,
            1, # weight
            UCIS_OTHER,
            cp_l)
        
        for crb_e in cr_e.iter("crossBin"):
            self.readCrossBin(crb_e, cr, cr_type_i)
        
        return cr

    def populateCrossType(self, cr_t, cr_bin_m):
        srcinfo = None

        for bin_name,count in cr_bin_m.items():
            cr_t.createBin
            cr_t.createBin(
                bin_name,
                srcinfo,
                1, # weight
                count,
                "") # TODO:
        pass
    
    def readCrossBin(self, crb_e, cr, cr_type_i):
        name = self.getAttr(crb_e, "name", "default")
        srcinfo = None
        contentsN = next(crb_e.iter("contents"))

        count = self.getAttrInt(contentsN, "coverageCount")

        if name in cr_type_i[1].keys():
            cr_type_i[1][name] += count
        else:
            cr_type_i[1][name] = count

        cr.createBin(
            name,
            srcinfo,
            1, # weight
            count,
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
        # Try with and without fractional seconds
        for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
            try:
                dateVal = datetime.strptime(val, fmt)
                return dateVal.strftime("%Y%m%d%H%M%S")
            except ValueError:
                continue
        raise ValueError(f"Cannot parse datetime: {val!r}")
    
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
            
    def setBoolIfEx(self, n, f, name):
        if name in n.attrib:
            f(n.attrib[name] == "true")
    
    def readOptions(self, parent_elem, target_obj):
        """Read options element and apply to target object"""
        options = parent_elem.find("options")
        if options is not None:
            # Read common options
            self.setIntIfEx(options, target_obj.setWeight, "weight")
            self.setIntIfEx(options, target_obj.setGoal, "goal")
            self.setIntIfEx(options, target_obj.setAtLeast, "at_least")
            
            # Read covergroup-specific options
            if hasattr(target_obj, 'setPerInstance'):
                self.setBoolIfEx(options, target_obj.setPerInstance, "per_instance")
            if hasattr(target_obj, 'setMergeInstances'):
                self.setBoolIfEx(options, target_obj.setMergeInstances, "merge_instances")
            if hasattr(target_obj, 'setGetInstCoverage'):
                self.setBoolIfEx(options, target_obj.setGetInstCoverage, "get_inst_coverage")
                
            # Read CvgScope options
            if hasattr(target_obj, 'setAutoBinMax'):
                self.setIntIfEx(options, target_obj.setAutoBinMax, "auto_bin_max")
            if hasattr(target_obj, 'setDetectOverlap'):
                self.setBoolIfEx(options, target_obj.setDetectOverlap, "detect_overlap")
            if hasattr(target_obj, 'setStrobe'):
                self.setBoolIfEx(options, target_obj.setStrobe, "strobe")

    def setFloatIfEx(self, n, f, name):
        if name in n.attrib:
            f(float(n.attrib[name]))
