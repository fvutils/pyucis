'''
Created on Jan 8, 2020

@author: ballance
'''

class TestData():
    
    def __init__(self,
                 teststatus,
                 toolcategory : str,
                 date : str,
                 simtime : float = 0.0,
                 timeunit : str = "ns",
                 runcwd : str = ".",
                 cputime : float = 0.0,
                 seed : str = "0",
                 cmd : str = "",
                 args : str = "",
                 compulsory : int = 0,
                 user : str = "user",
                 cost : float = 0.0
                 ):
        self.teststatus = teststatus
        self.simtime = simtime
        self.timeunit = timeunit
        self.runcwd = runcwd
        self.cputime = cputime
        self.seed = seed
        self.cmd = cmd 
        self.args = args 
        self.compulsory = compulsory
        self.date = date
        self.user = user
        self.cost = cost
        self.toolcategory = toolcategory
        