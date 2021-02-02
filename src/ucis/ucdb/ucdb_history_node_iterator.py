'''
Created on Mar 22, 2020

@author: ballance
'''
from ucis.ucdb.libucdb import get_lib
from ucis.ucdb.ucdb_history_node import UcdbHistoryNode


class UcdbHistoryNodeIterator(object):
    
    def __init__(self, db, hist_obj, kind):
        self.db = db
        self.next = get_lib().ucdb_NextHistoryNode(self.db, None, kind)
        
    def __iter__(self):
        return self
    
    def __next__(self):
        self.next = get_lib().ucis_HistoryScan(self.db, self.next)
        
        if next is None:
            raise StopIteration
        
        return UcdbHistoryNode(self.db, self.next)
        
        
        
        