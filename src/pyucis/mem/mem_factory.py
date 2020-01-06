'''
Created on Jan 5, 2020

@author: ballance
'''
from pyucis import ucis
from pyucis.mem.mem_ucis import MemUCIS

class MemFactory():
    
    
    @staticmethod
    def create() -> ucis:
        """
        Creates a new in-memory database. 
        """
        return MemUCIS()
    
    
    @staticmethod
    def clone(db : ucis):
        """Clones an existing database and creates a new in-memory database"""
        pass

        
    
        
        