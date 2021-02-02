'''
Created on Mar 13, 2020

@author: ballance
'''
from ucis.ucdb.ucdb_obj import UcdbObj
from ucis.cover_index import CoverIndex
from ucis.ucdb import libucdb

class UcdbCoverIndex(UcdbObj, CoverIndex):
    
    def __init__(
            self, 
            db, 
            obj, # The object to which this index is relative 
            index):
        super().__init__(db, obj)
        self.index = index