'''
Created on Jan 5, 2020

@author: ballance
'''
from pyucis.source_file import SourceFile

class StatementId():
    
    def __init__(self, file : SourceFile, line : int, item : int):
        self.file = file
        self.line = line
        self.item = item
        
    def getFile(self) -> SourceFile:
        return self.file
    
    def getLine(self) -> int:
        return self.line
    
    def getItem(self) -> int:
        return self.item
    
    
    