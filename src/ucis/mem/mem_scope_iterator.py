'''
Created on Mar 22, 2020

@author: ballance
'''
from typing import List


class MemScopeIterator(object):
    
    def __init__(self, nodes : List['MemScope'], mask):
        self.nodes = nodes
        self.idx = 0
        self.mask = int(mask)

    def __iter__(self):
        return self

    def __next__(self):
        next = None
        mask = self.mask

        while self.idx < len(self.nodes):
            n = self.nodes[self.idx]
            self.idx += 1
            if (int(n.getScopeType()) & mask) != 0:
                return n

        raise StopIteration
