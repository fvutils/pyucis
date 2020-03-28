'''
Created on Mar 24, 2020

@author: ballance
'''
from unittest.case import TestCase

class TestSQLite(TestCase):
    
    def disabled_test_smoke(self):
        import sqlite3
        
        conn = sqlite3.connect("my_db.scdb")
        
        print("conn=" + str(conn))
        
        
        with conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS scopes (
                    id integer PRIMARY KEY,
                    parent integer,
                    name text NOT NULL,
                    type integer,
                    flags integer
                );        
            """)
        
            c.execute("""
                INSERT INTO scopes(parent,name,type,flags)
                VALUES(?,?,?,?)
                """, (-1, "foo", 1, 0))
            
            c.execute("""
                INSERT INTO scopes(parent,name,type,flags)
                VALUES(-1,"bar",1, 0)
                """)
            
            c.execute("""
                INSERT INTO scopes(parent,name,type,flags)
                VALUES(?,?,?,?)""", (1, "baz", 1, 0))

            # Retrieve all top-level scopes            
            c.execute("""SELECT * from scopes where parent=-1""")
            print("rows=" + str(c.fetchall()))
            
        