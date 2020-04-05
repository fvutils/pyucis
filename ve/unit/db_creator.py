'''
Created on Apr 5, 2020

@author: ballance
'''
import os

from ucis import UCIS_HISTORYNODE_TEST, UCIS_TESTSTATUS_OK, db, UCIS_OTHER, \
    UCIS_DU_MODULE, UCIS_ENABLED_STMT, UCIS_ENABLED_BRANCH, UCIS_ENABLED_COND, \
    UCIS_ENABLED_EXPR, UCIS_ENABLED_FSM, UCIS_ENABLED_TOGGLE, UCIS_INST_ONCE, \
    UCIS_SCOPE_UNDER_DU, UCIS_INSTANCE
from ucis.covergroup import Covergroup
from ucis.mem.mem_factory import MemFactory
from ucis.scope import Scope
from ucis.source_info import SourceInfo
from ucis.test_data import TestData
from ucis.ucis import UCIS


class DbCreator():
    
    def __init__(self, db : UCIS = None):
        if db is None:
            self.db = MemFactory.create()
        else:
            self.db = db

        self.source = UCIS_OTHER            
        self.ucisdb = "file.ucis"

    def dummy_test_data(self):
        testnode = self.db.createHistoryNode(
            None, 
            "logicalName",
            self.ucisdb,
        UCIS_HISTORYNODE_TEST)
        td = TestData(
            teststatus=UCIS_TESTSTATUS_OK,
            toolcategory="UCIS:simulator",
            date="20200202020"
        )
        testnode.setTestData(td)
        
    def dummy_instance(self):
        file = self.db.createFileHandle("dummy", os.getcwd())
    
        srcinfo = SourceInfo(file, 0, 0)
        du = self.db.createScope(
            "foo.bar",
            srcinfo,
            1, # weight
            UCIS_OTHER,
            UCIS_DU_MODULE,
            UCIS_ENABLED_STMT | UCIS_ENABLED_BRANCH
            | UCIS_ENABLED_COND | UCIS_ENABLED_EXPR
            | UCIS_ENABLED_FSM | UCIS_ENABLED_TOGGLE
            | UCIS_INST_ONCE | UCIS_SCOPE_UNDER_DU
            )
        
        instance = self.db.createInstance(
            "dummy",
            None, # sourceinfo
            1, # weight
            UCIS_OTHER,
            UCIS_INSTANCE,
            du,
            UCIS_INST_ONCE)        
    
        return instance
        
    def create_covergroup(
            self,
            parent : Scope, # Instance or CovergroupType
            name : str,
            spec):
        
        options = None if not "options" in spec.keys() else spec["options"]
        
        if options is None or not "weight" in options.keys():
            weight = 1
        else:
            weight = int(options["weight"])
        

        cg_n = parent.createCovergroup(
            name,
            None,
            weight,
            self.source
            )
        
        coverpoints = None if not "coverpoints" in spec.keys() else spec["coverpoints"]
        crosses = None if not "crosses" in spec.keys() else spec["crosses"]
        
        if crosses is not None and coverpoints is None:
            raise Exception("Cannot create a cross without coverpoints")

        if coverpoints is not None:
                

            for cp_n,cp_s in coverpoints.items():
                options = None if not "options" in cp_s.keys() else cp_s["options"]
            
                if options is None or not "weight" in options.keys():
                    weight = 1
                else:
                    weight = int(options["weight"])
                    
                if options is None or not "at_least" in options.keys():
                    at_least = 1
                else:
                    at_least = int(options["at_least"])
                    
                if not "bins" in cp_s.keys():
                    raise Exception("No bins specified for coverpoint " + cp_n)
                
                cp = cg_n.createCoverpoint(
                    cp_n,
                    None,
                    weight, # weight
                    self.source
                )
                
                for bn_n,bn_hits in cp_s["bins"]:
                    cp.createBin(
                        bn_n,
                        None,
                        at_least,
                        bn_hits,
                        "a")            
                    
                
            