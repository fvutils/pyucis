'''
Created on Mar 27, 2020

@author: ballance
'''
from ucis.covergroup import Covergroup
from ucis.cover_item import CoverItem

class CoverageReport(object):
    
    def __init__(self):
        self.covergroups = []
        self.coverage = 0.0
        pass
    
    def add_covergroup(self,cg)->Covergroup:
        self.covergroups.append(cg)
        return cg
    
    class CoverItem(object):
        
        def __init__(self, name):
            self.name = name
            self.coverage = 0.0
            self.weight = 1
            
    class Covergroup(CoverItem):
        
        def __init__(self, name, instname):
            super().__init__(name)
            self.instname = instname
           
            self.coverpoints = []
            self.crosses = []
            self.covergroups = []
            
        def add_coverpoint(self, cp)->'Coverpoint':
            self.coverpoints.append(cp)
            return cp
            

    class Coverpoint(CoverItem):

        def __init__(self, name):
            super().__init__(name)
            self.bins = []
            
    class Cross(CoverItem):
        def __init__(self, name):
            super().__init__(name)
            self.bins = []
            
    class CoverBin(object):
        
        def __init__(self, name, goal, count):
            self.name = name
            self.goal = goal
            self.count = count

        @property            
        def hit(self):
            return self.count >= self.goal
        

