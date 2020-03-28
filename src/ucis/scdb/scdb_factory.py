'''
Created on Mar 24, 2020

@author: ballance
'''
from ucis.scdb.scdb_ucis import ScdbUCIS

class ScdbFactory(object):
    
    def create(self, file=None):
        return ScdbUCIS()
    
        