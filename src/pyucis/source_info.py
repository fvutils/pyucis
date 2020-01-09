'''
Created on Jan 8, 2020

@author: ballance
'''

class SourceInfo():
    
    def __init__(self, file, line : int, token : int):
        self.file = file
        self.line = line
        self.token = token
        