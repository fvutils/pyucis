'''
Created on Mar 27, 2020

@author: ballance
'''

class CoverageReport(object):
    
    def __init__(self):
        self.covergroups = []
        pass
    
    class CoverItem(object):
        
        def __init__(self, name):
            self.name = name
            self.coverage = 0.0
            
    class Covergroup(CoverItem):
        
        def __init__(self, name):
            super().__init__(name)
           
            self.coverpoints = []
            self.crosses = []
            self.covergroups = []

    class Coverpoint(CoverItem):

        def __init__(self, name):
            super().__init__(name)
            self.bins = []
            
    class CoverBin(object):
        
        def __init__(self, name):
            self.name = name
            self.count = 0
        

        