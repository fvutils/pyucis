'''
Created on Mar 24, 2020

@author: ballance
'''
from ucis.ucis import UCIS
import os
import sqlite3

class ScdbWriter(object):
    
    def __init__(self, db, conn):
        self.db = db
        self.conn = conn
        pass
    
    @staticmethod
    def write(db : UCIS, filename):
        
        if os.path.isfile(filename):
            # No incremental option for now
            os.unlink(filename)
            
        conn = sqlite3.connect(filename)
            
        writer = ScdbWriter(db, conn)
        writer._write()
        
        conn.close()
        
    def _write(self):
        
        for scope in self.db.scopes():
            print("scope=" + str(scope))
        
        # First write scopes
        