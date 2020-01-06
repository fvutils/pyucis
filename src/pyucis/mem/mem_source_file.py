'''
Created on Jan 5, 2020

@author: ballance
'''

class MemSourceFile():
    
    def __init__(self, fileid, filename):
        self.fileid = fileid
        self.m_filename = filename
        
    def getFilename(self) -> str:
        return self.m_filename
        
        
        