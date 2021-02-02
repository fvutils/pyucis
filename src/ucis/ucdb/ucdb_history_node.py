'''
Created on Mar 11, 2020

@author: ballance
'''
from _ctypes import pointer
from ucis import UCIS_INT_TEST_STATUS
from ucis.history_node import HistoryNode
from ucis.ucdb.ucdb_obj import UcdbObj
from ucis.ucdb.ucdb_scope import UcdbScope
from ucis.ucdb.libucdb import get_lib
from ucis.test_data import TestData
from ucis.test_status_t import TestStatusT

from ucis.ucdb.ucdb_test_data import UcdbTestData


class UcdbHistoryNode(UcdbObj, HistoryNode):
    
    def __init__(self, db, hn):
        super().__init__(db, hn)
        
        
    def setTestData(self, testdata:TestData):
        ucdb_td = pointer(UcdbTestData.ctor(testdata))
        
        get_lib().ucis_SetTestData(
            self.db,
            self.obj,
            ucdb_td)
        
    def getTestData(self):
        ucdb_td = pointer(UcdbTestData())
        
        get_lib().ucis_SetTestData(
            self.db,
            self.obj,
            ucdb_td)
        
        return ucdb_td.to_testdata()
    
    def getTestStatus(self) -> TestStatusT:
        return self.getIntProperty(-1, UCIS_INT_TEST_STATUS)
    
    def setTestStatus(self, status : TestStatusT):
        self.setIntProperty(-1, UCIS_INT_TEST_STATUS, status)
    
        
