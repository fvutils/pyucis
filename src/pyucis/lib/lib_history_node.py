'''
Created on Mar 11, 2020

@author: ballance
'''
from pyucis.history_node import HistoryNode
from pyucis.lib.lib_scope import LibScope
from pyucis.lib.lib_obj import LibObj
from pyucis.test_data import TestData
from pyucis.lib.libucis import get_lib
from pyucis.lib.lib_test_data import LibTestData
from _ctypes import pointer

class LibHistoryNode(LibObj, HistoryNode):
    
    def __init__(self, db, hn):
        super().__init__(db, hn)
        
        
    def setTestData(self, testdata:TestData):
        lib_td = pointer(LibTestData.ctor(testdata))
        
        get_lib().ucis_SetTestData(
            self.db,
            self.obj,
            lib_td)
        
    def getTestData(self):
        lib_td = pointer(LibTestData())
        
        get_lib().ucis_SetTestData(
            self.db,
            self.obj,
            lib_td)
        
        return lib_td.to_testdata()
    
        
