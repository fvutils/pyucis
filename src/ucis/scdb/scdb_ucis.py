'''
Created on Mar 24, 2020

@author: ballance
'''
from ucis.mem.mem_ucis import MemUCIS

class ScdbUCIS(MemUCIS):
    
    def write(self, file, scope=None, recurse=True, covertype=-1):
        MemUCIS.write(self, file, scope=scope, recurse=recurse, covertype=covertype)