'''
Created on Mar 22, 2020

@author: ballance
'''
from pyucis.file_handle import FileHandle

class MemFileHandle(FileHandle):
    
    def __init__(self, filename):
        self.filename = filename
        
    def getFileName(self)->str:
        return self.filename
    
