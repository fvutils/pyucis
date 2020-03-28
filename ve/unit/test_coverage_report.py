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
from unittest.case import TestCase
from ucis.report.coverage_report_builder import CoverageReportBuilder


class TestCoverageReport(TestCase):
    
    def test_simple_typecov(self):
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
        
        cp.createBin(
            "auto[a]",
            SourceInfo(file, 4, 0),
            1,
            4,
            "a")
        
        cov_report = CoverageReportBuilder.build(db)
        
        print("covergroups: " + str(len(cov_report.covergroups)))

