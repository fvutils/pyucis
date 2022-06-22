'''
Created on Jun 11, 2022

@author: mballance
'''
from ucis.db_format_if import DbFormatIf, DbFormatFlags
from ucis.ucis import UCIS

class DbFormatIfYaml(DbFormatIf):
    
    def flags(self) -> DbFormatFlags:
        return DbFormatFlags.Read|DbFormatFlags.Write
    
    def init(self, options):
        raise NotImplementedError("DbFormatIf.init not implemented by %s" % str(type(self)))
    
    def create(self) -> UCIS:
        raise NotImplementedError("DbFormatIf.create not implemented by %s" % str(type(self)))
    
    def read(self, file_or_filename) -> UCIS:
        raise NotImplementedError("DbFormatIf.read not implemented by %s" % str(type(self)))
    
    def write(self, db : UCIS, file_or_filename):
        raise NotImplementedError("DbFormatIf.write not implemented by %s" % str(type(self)))
        