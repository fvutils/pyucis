'''
Created on Mar 23, 2020

@author: ballance
'''
from typing import List
from ucis.mem.mem_cover_index import MemCoverIndex
from ucis.cover_type_t import CoverTypeT

class MemCoverIndexIterator(object):
    
    def __init__(self, coveritems : List[MemCoverIndex], mask : CoverTypeT):
        self.coveritems = coveritems
        self.mask = int(mask)
        self.idx = 0

    def __iter__(self):
        return self

    def __next__(self):
        mask = self.mask
        while self.idx < len(self.coveritems):
            n = self.coveritems[self.idx]
            self.idx += 1
            if (int(n.data.type) & mask) != 0:
                return n
        raise StopIteration
