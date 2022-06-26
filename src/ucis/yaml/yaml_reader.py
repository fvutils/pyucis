'''
Created on Nov 9, 2021

@author: mballance
'''
import yaml

from ucis import UCIS_HISTORYNODE_TEST, UCIS_OTHER, UCIS_CVGBIN, UCIS_IGNOREBIN, \
    UCIS_ILLEGALBIN, UCIS_DU_MODULE, UCIS_ENABLED_STMT, UCIS_ENABLED_BRANCH, \
    UCIS_ENABLED_COND, UCIS_ENABLED_EXPR, UCIS_ENABLED_FSM, UCIS_ENABLED_TOGGLE, \
    UCIS_INST_ONCE, UCIS_SCOPE_UNDER_DU, UCIS_INSTANCE
from ucis.mem.mem_ucis import MemUCIS
from ucis.scope import Scope
from ucis.ucis import UCIS

import os
import json
import python_jsonschema_objects as pjs
import yaml
from yaml.loader import Loader
import jsonschema


class YamlReader(object):
    
    def __init__(self):
        self.active_scope_s = []
        self.cg_default_du_name = "du"
        self.cg_default_inst_name = "cg_inst"
        pass
    
    _coverage_ns = None
    _coverage_schema = None
    
    @classmethod
    def getCoverageNS(cls):
        if cls._coverage_ns is None:
            schema = cls.getCoverageSchema()
            builder = pjs.ObjectBuilder(schema)
            cls._coverage_ns = builder.build_classes()
        return cls._coverage_ns
    
    @classmethod
    def getCoverageSchema(cls):
        if cls._coverage_schema is None:
            yaml_dir = os.path.dirname(os.path.abspath(__file__))
            schema_dir = os.path.join(os.path.dirname(yaml_dir), "schema")

            with open(os.path.join(schema_dir, "coverage.json"), "r") as fp:
                cls._coverage_schema = json.load(fp)
        return cls._coverage_schema
            
    
    def loads(self, s) -> UCIS:

        ns = YamlReader.getCoverageNS()
        schema = YamlReader.getCoverageSchema()

        for c in dir(ns):
            print("C: %s" % str(c))

        cov_yml = yaml.load(s, Loader=yaml.FullLoader)
        
        jsonschema.validate(instance=cov_yml, schema=schema)
            
        coverage = ns.CoverageData()
        print("cov: %s" % str(coverage))
        coverage = coverage.from_json(json.dumps(cov_yml))
        print("cov: %s" % str(coverage))
        
        self.db = MemUCIS()
#        doc_i = yaml.load(s, Loader=yaml.Loader)
#        if doc_i is None or "coverage" not in doc_i.keys():
#            raise Exception("Invalid input")

        coverage = coverage.coverage
        
        if coverage.covergroups is not None:
            for cg in coverage.covergroups:
                self.process_covergroup(cg, 0)
                
        return self.db
                
                
    def process_covergroup(self, cg_s, depth):
        print("process_covergroup")
        parent = self.get_cg_inst()

        type_name = None
        if "type-name" in cg_s.keys():
            type_name = cg_s["type-name"]
            
        inst_name = None
        if "inst-name" in cg_s.keys():
            inst_name = cg_s["inst-name"]
            
        weight = 1
        if cg_s.weight is not None:
            weight = int(cg_s.weight)

        cg_location = None
        if depth == 0:
            self.active_scope_s.append(parent.createCovergroup(
                type_name,
                cg_location,
                weight,
                UCIS_OTHER))
        else:
            self.active_scope_s.append(parent.createCoverInstance(
                inst_name,
                cg_location,
                weight,
                UCIS_OTHER))

        if cg_s.coverpoints is not None:            
            for cp in cg_s.coverpoints:
                self.process_coverpoint(cp)

        if depth == 0:
            if cg_s.instances is not None:
                print("--> covergroups")
                for cg in cg_s.instances:
                    self.process_covergroup(cg, depth+1)
                print("<-- covergroups")

        self.active_scope_s.pop()
        
    def process_coverpoint(self, cp_s):
        parent = self.active_scope_s[-1]
        
        cp_location = None
        
        weight = 1
        if "weight" in cp_s.keys():
            weight = int(cp_s["weight"])
            
        at_least = 1
        if "at-least" in cp_s.keys():
            at_least = cp_s["at-least"]
            
        cp_scope = parent.createCoverpoint(
            cp_s["name"],
            cp_location,
            weight,
            UCIS_OTHER)
        
        if "bins" in cp_s.keys():
            for b in cp_s["bins"]:
                cp_scope.createBin(
                    b["name"],
                    cp_location,
                    at_least,
                    b["count"],
                    b["name"],
                    UCIS_CVGBIN)
                
        if "ignore-bins" in cp_s.keys():
            for b in cp_s["ignore-bins"]:
                cp_scope.createBin(
                    b["name"],
                    cp_location,
                    at_least,
                    b["count"],
                    b["name"],
                    UCIS_IGNOREBIN)
                
        if "illegal-bins" in cp_s.keys():
            for b in cp_s["illegal-bins"]:
                cp_scope.createBin(
                    b["name"],
                    cp_location,
                    at_least,
                    b["count"],
                    b["name"],
                    UCIS_ILLEGALBIN)

    def get_cg_inst(self) -> Scope:
        if len(self.active_scope_s) > 0:
            return self.active_scope_s[-1]
        else:
            # Need to create a default scope
#            from ucis.source_info import SourceInfo
#            file = self.db.createFileHandle("dummy", os.getcwd())
#            du_src_info = SourceInfo(file, 0, 0)
            du_src_info = None
            
            cg_default_du = self.db.createScope(
                self.cg_default_du_name,
                du_src_info,
                1, # weight
                UCIS_OTHER, # source language
                UCIS_DU_MODULE,
                UCIS_ENABLED_STMT | UCIS_ENABLED_BRANCH
                | UCIS_ENABLED_COND | UCIS_ENABLED_EXPR
                | UCIS_ENABLED_FSM | UCIS_ENABLED_TOGGLE
                | UCIS_INST_ONCE | UCIS_SCOPE_UNDER_DU)
            
            cg_default_inst = self.db.createInstance(
                self.cg_default_inst_name,
                None, # sourceinfo
                1, # weight
                UCIS_OTHER, # source language
                UCIS_INSTANCE,
                cg_default_du,
                UCIS_INST_ONCE)

            self.active_scope_s.append(cg_default_inst)
            
            return cg_default_inst

        
        
