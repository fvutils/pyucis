'''
Created on Dec 22, 2019

@author: ballance
'''

class UnimplError(Exception):
    
    def __init__(self, msg=""):
        super().__init__(msg)