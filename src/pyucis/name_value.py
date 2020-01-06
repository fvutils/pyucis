'''
Created on Jan 5, 2020

@author: ballance
'''

class NameValue():
    
    def __init__(self, name, value):
        self.name = name
        self.value = value
        
    def getName(self) -> str:
        return self.name
    
    def getValue(self) -> str:
        return self.value