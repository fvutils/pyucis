'''
Created on Mar 11, 2020

@author: ballance
'''
import os
from pyucis import ucis_Write, ucis_Close, UCIS_HISTORYNODE_TEST, \
    UCIS_TESTSTATUS_OK, UCIS_VLOG, UCIS_DU_MODULE, UCIS_ENABLED_BRANCH, \
    UCIS_ENABLED_EXPR, UCIS_ENABLED_FSM, UCIS_ENABLED_TOGGLE, UCIS_INST_ONCE, \
    UCIS_SCOPE_UNDER_DU, UCIS_ENABLED_STMT, UCIS_ENABLED_COND, UCIS_INSTANCE, \
    UCIS_OTHER
from pyucis.lib.LibFactory import LibFactory
from pyucis.source_info import SourceInfo
from pyucis.test_data import TestData
import unittest
from unittest.case import TestCase

from example_create_ucis import create_testdata, create_covergroup, \
    create_coverpoint_bin, create_coverpoint, create_filehandle, create_instance, \
    create_design_unit


class TestSimpleCreate(TestCase):
    
    def test_simplest_create(self):
        print("-- test_simplest_create")
        
        ucisdb = "file.ucis"
        LibFactory.load_ucis_library("libucis.so")
        db = LibFactory.create()
        
        testnode = db.createHistoryNode(
            None, 
            "logicalName",
            ucisdb,
            UCIS_HISTORYNODE_TEST)
        td = TestData(
            teststatus=UCIS_TESTSTATUS_OK,
            toolcategory="UCIS:simulator",
            date="20200202020"
            )
        testnode.setTestData(td)
        
        file = db.createFileHandle("dummy", os.getcwd())

        srcinfo = SourceInfo(file, 0, 0)
        du = db.createScope(
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
        
        instance = db.createInstance(
            "dummy",
            None, # sourceinfo
            1, # weight
            UCIS_OTHER,
            UCIS_INSTANCE,
            du,
            UCIS_INST_ONCE)
        
        cg = instance.createCovergroup(
            "cg",
            SourceInfo(file, 3, 0),
            1, # weight
            UCIS_OTHER)
        
        cp = cg.createCoverpoint(
            "t",
            SourceInfo(file, 4, 0),
            1, # weight
            UCIS_VLOG
            )
        cp.setComment("Hello There")
        
        print("--> createBin")
        cp.createBin(
            "auto[a]",
            SourceInfo(file, 4, 0),
            1,
            4,
            "a")
        print("<-- createBin")

        db.write(ucisdb, None, True, -1)
        db.close()
        
#         LibFactory.load_ucis_library("libucis.so")
#         db = LibFactory.create()
#         
#         ucisdb = "file.ucis"
#         
#         create_testdata(db, ucisdb)
#         filehandle = create_filehandle(db,"dummy")
# 
#         # Need a unique typename for the design unit
#         du = create_design_unit(db, "foo.bar", filehandle, 0)        
#         
#         # Need a different instancename 
#         instance = create_instance(db, "dummy", None, du)
#         
#         cvg = create_covergroup(db, instance, "cg", filehandle, 3)
#         cvp = create_coverpoint(db, cvg, "t", filehandle, 4)
#         create_coverpoint_bin(db, cvp, "auto[a]", filehandle, 4, 1, 0, "a")
#         
#         ucis_Write(db, ucisdb, None, 1, -1)
#         ucis_Close(db)


if __name__ == "__main__":
    unittest.main()

