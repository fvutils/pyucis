'''
Created on Jun 11, 2022

@author: mballance
'''
from ucis.rgy.format_if_db import FormatIfDb, FormatDescDb, FormatDbFlags, FormatCapabilities
from ucis.mem import MemUCIS

class DbFormatIfXml(FormatIfDb):
    
    def init(self, options):
        raise Exception("Options %s not accepted by the XML format" % str(options))
    
    def create(self, filename=None):
        return MemUCIS()
    
    def read(self, file_or_filename) -> 'UCIS':
        from ucis.xml.xml_factory import XmlFactory
        return XmlFactory.read(file_or_filename)

    def write(self, db, file_or_filename, ctx=None) -> None:
        from ucis.xml.xml_writer import XmlWriter
        writer = XmlWriter()
        with open(file_or_filename, "w") as fp:
            writer.write(fp, db, ctx)
    
    @staticmethod        
    def register(rgy):
        rgy.addDatabaseFormat(FormatDescDb(
            DbFormatIfXml,
            name="xml",
            description="Supports reading and writing UCIS XML interchange",
            flags=FormatDbFlags.Read|FormatDbFlags.Write,
            capabilities=FormatCapabilities(
                can_read=True, can_write=True,
                functional_coverage=True, cross_coverage=True,
                ignore_illegal_bins=True, code_coverage=True,
                toggle_coverage=True, fsm_coverage=True,
                assertions=True, history_nodes=True,
                design_hierarchy=True, lossless=True,
            )))

        
        