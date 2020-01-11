'''
Created on Jan 11, 2020

@author: ballance
'''
from pyucis.file_handle import FileHandle

class LibFileHandle(FileHandle):
    
    def __init__(self, fh):
        super().__init__()
        self.fh = fh