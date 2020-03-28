'''
Created on Mar 27, 2020

@author: ballance
'''
from _io import StringIO
import os
from ucis import UCIS_HISTORYNODE_TEST, UCIS_TESTSTATUS_OK, UCIS_OTHER, \
    UCIS_DU_MODULE, UCIS_ENABLED_STMT, UCIS_ENABLED_BRANCH, UCIS_ENABLED_COND, \
    UCIS_ENABLED_EXPR, UCIS_ENABLED_FSM, UCIS_ENABLED_TOGGLE, UCIS_INST_ONCE, \
    UCIS_SCOPE_UNDER_DU, UCIS_INSTANCE, UCIS_VLOG
from ucis.mem.mem_factory import MemFactory
from ucis.source_info import SourceInfo
from ucis.test_data import TestData
from ucis.xml import validate_ucis_xml
from ucis.xml.xml_writer import XmlWriter
from unittest.case import TestCase
from ucis.xml.xml_reader import XmlReader


class TestXmlReader(TestCase):
    
    def test_smoke(self):
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
            "my_inst_scope",
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
        
        cp1 = cg.createCoverpoint(
            "cp1",
            SourceInfo(file, 4, 0),
            1, # weight
            UCIS_VLOG
            )
        
        cp1.createBin(
            "v[1]",
            SourceInfo(file, 4, 0),
            1,
            4,
            "v")
        cp1.createBin(
            "v[2]",
            SourceInfo(file, 4, 0),
            1,
            4,
            "v")
        
        cp2 = cg.createCoverpoint(
            "cp2",
            SourceInfo(file, 4, 0),
            1, # weight
            UCIS_VLOG
            )
        
        cp2.createBin(
            "v2[1]",
            SourceInfo(file, 4, 0),
            1,
            4,
            "v2")
        cp2.createBin(
            "v2[2]",
            SourceInfo(file, 4, 0),
            1,
            4,
            "v2")        
        
        cr = cg.createCross(
            "cr",
            SourceInfo(file, 4, 0),
            1,
            UCIS_VLOG,
            [cp1, cp2])
        
        cr.createBin(
            "<v1[1],v2[1]>",
            SourceInfo(file, 4, 0),
            1,
            4,
            "v1,v2")
        
        cr.createBin(
            "<v1[2],v2[1]>",
            SourceInfo(file, 4, 0),
            1,
            4,
            "v1,v2")
        
        cr.createBin(
            "<v1[1],v2[2]>",
            SourceInfo(file, 4, 0),
            1,
            4,
            "v1,v2")
        
        cr.createBin(
            "<v1[2],v2[2]>",
            SourceInfo(file, 4, 0),
            1,
            4,
            "v1,v2")

        out = StringIO()
        writer = XmlWriter()
        writer.write(out, db)
        
        print("XML Output:\n" + out.getvalue())
        input = StringIO(out.getvalue())
        validate_ucis_xml(input)
        
        input = StringIO(out.getvalue())
        reader = XmlReader()
        db2 = reader.read(input)
        
        out2 = StringIO()
        writer = XmlWriter()
        writer.write(out2, db2)
        print("XML Output2:\n" + out2.getvalue())
        input = StringIO(out2.getvalue())
        validate_ucis_xml(input)

        
        
        