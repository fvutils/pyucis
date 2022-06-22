'''
Created on Jun 11, 2022

@author: mballance
'''
from ucis.db_format_if import DbFormatIf
from ucis.ucis import UCIS
from ucis.xml.xml_factory import XmlFactory


class DbFormatIfXml(DbFormatIf):
    
    def init(self, options):
        raise Exception("Options %s not accepted by the XML format" % str(options))
    
    def create(self):
        raise Exception("The XML format can only be read and written, not created")
    
    def read(self, file_or_filename) -> UCIS:
        return XmlFactory.read(file_or_filename)
    
    def write(self, db : UCIS, file_or_filename):
        XmlFactory.write(db, file_or_filename)
        