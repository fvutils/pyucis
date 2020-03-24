'''
Created on Mar 11, 2020

@author: ballance
'''
import os
from ucis import ucis_Write, ucis_Close, UCIS_HISTORYNODE_TEST, \
    UCIS_TESTSTATUS_OK, UCIS_VLOG, UCIS_DU_MODULE, UCIS_ENABLED_BRANCH, \
    UCIS_ENABLED_EXPR, UCIS_ENABLED_FSM, UCIS_ENABLED_TOGGLE, UCIS_INST_ONCE, \
    UCIS_SCOPE_UNDER_DU, UCIS_ENABLED_STMT, UCIS_ENABLED_COND, UCIS_INSTANCE, \
    UCIS_OTHER
from ucis.lib.LibFactory import LibFactory
from ucis.source_info import SourceInfo
from ucis.test_data import TestData
import unittest
from unittest.case import TestCase

from example_create_ucis import create_testdata, create_covergroup, \
    create_coverpoint_bin, create_coverpoint, create_filehandle, create_instance, \
    create_design_unit
from ucis.mem.mem_factory import MemFactory
from ucis.xml.xml_reader import XmlReader
from ucis.xml.xml_writer import XmlWriter
from _io import StringIO


class TestSimpleCreate(TestCase):
    
    def test_simplest_create(self):
        print("-- test_simplest_create")
        
        ucisdb = "file.ucis"
        db = MemFactory.create()
        
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

#        db.write(ucisdb, None, True, -1)
        db.close()

        xmlout = StringIO()        
        writer = XmlWriter()
        writer.write(xmlout, db)
        xmlin = StringIO(xmlout.getvalue())
        XmlReader.validate(xmlin)

    def test_simplest_create_2inst(self):
        
        ucisdb = "file_2inst.ucis"
        db = MemFactory.create()
        
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
        du1 = db.createScope(
            "foo.bar1",
            srcinfo,
            1, # weight
            UCIS_OTHER,
            UCIS_DU_MODULE,
            UCIS_ENABLED_STMT | UCIS_ENABLED_BRANCH
            | UCIS_ENABLED_COND | UCIS_ENABLED_EXPR
            | UCIS_ENABLED_FSM | UCIS_ENABLED_TOGGLE
            | UCIS_INST_ONCE | UCIS_SCOPE_UNDER_DU
            )
        
        du2 = db.createScope(
            "foo.bar2",
            srcinfo,
            1, # weight
            UCIS_OTHER,
            UCIS_DU_MODULE,
            UCIS_ENABLED_STMT | UCIS_ENABLED_BRANCH
            | UCIS_ENABLED_COND | UCIS_ENABLED_EXPR
            | UCIS_ENABLED_FSM | UCIS_ENABLED_TOGGLE
            | UCIS_INST_ONCE | UCIS_SCOPE_UNDER_DU
            )
        
        instance1 = db.createInstance(
            "dummy",
            None, # sourceinfo
            1, # weight
            UCIS_OTHER,
            UCIS_INSTANCE,
            du1,
            UCIS_INST_ONCE)
        
        cg1 = instance1.createCovergroup(
            "cg",
            SourceInfo(file, 3, 0),
            1, # weight
            UCIS_OTHER)
        
        cp1 = cg1.createCoverpoint(
            "t",
            SourceInfo(file, 4, 0),
            1, # weight
            UCIS_VLOG
            )
        
        cp1.createBin(
            "auto[a]",
            SourceInfo(file, 4, 0),
            1,
            4,
            "a")

        du2 = db.createScope(
            "foo.bar2",
            srcinfo,
            1, # weight
            UCIS_OTHER,
            UCIS_DU_MODULE,
            UCIS_ENABLED_STMT | UCIS_ENABLED_BRANCH
            | UCIS_ENABLED_COND | UCIS_ENABLED_EXPR
            | UCIS_ENABLED_FSM | UCIS_ENABLED_TOGGLE
            | UCIS_INST_ONCE | UCIS_SCOPE_UNDER_DU
            )
        
        instance2 = db.createInstance(
            "dummy",
            None, # sourceinfo
            1, # weight
            UCIS_OTHER,
            UCIS_INSTANCE,
            du2,
            UCIS_INST_ONCE)
        
        cg2 = instance2.createCovergroup(
            "cg",
            SourceInfo(file, 3, 0),
            1, # weight
            UCIS_OTHER)
        
        cp2 = cg2.createCoverpoint(
            "t",
            SourceInfo(file, 4, 0),
            1, # weight
            UCIS_VLOG
            )
        
        cp2.createBin(
            "auto[a]",
            SourceInfo(file, 4, 0),
            1,
            4,
            "a")

        db.close()        
        
        xmlout = StringIO()        
        writer = XmlWriter()
        writer.write(xmlout, db)
        xmlin = StringIO(xmlout.getvalue())
        XmlReader.validate(xmlin)        
        
    def test_create_type_inst_cg(self):
        ucisdb = "file_type_inst.ucis"
        db = MemFactory.create()
        
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
        
        cg_t = instance.createCovergroup(
            "cg",
            SourceInfo(file, 3, 0),
            1, # weight
            UCIS_OTHER)
        
        cp = cg_t.createCoverpoint(
            "t",
            SourceInfo(file, 4, 0),
            1, # weight
            UCIS_VLOG
            )
        
        cp.createBin(
            "auto[a]",
            SourceInfo(file, 4, 0),
            1,
            4,
            "a")
        
        cg_i1 = cg_t.createCoverInstance(
            "cg_i1",
            SourceInfo(file, 3, 0),
            1, # weight
            UCIS_OTHER)

        cp = cg_i1.createCoverpoint(
            "t",
            SourceInfo(file, 4, 0),
            1, # weight
            UCIS_VLOG
            )
        
        cp.createBin(
            "auto[a]",
            SourceInfo(file, 4, 0),
            1,
            0,
            "a")
        
        db.close()
        
        xmlout = StringIO()        
        writer = XmlWriter()
        writer.write(xmlout, db)
        xmlin = StringIO(xmlout.getvalue())
        XmlReader.validate(xmlin)
        
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

