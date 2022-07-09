'''
Created on Jun 11, 2022

@author: mballance
'''
from ucis.rgy.format_if_db import FormatIfDb, FormatDescDb, FormatDbFlags
from ucis.yaml.yaml_ucis import YamlUCIS
from .yaml_reader import YamlReader

class DbFormatIfYaml(FormatIfDb):
    

    
    def init(self, options):
        raise NotImplementedError("DbFormatIf.init not implemented by %s" % str(type(self)))
    
    def create(self) -> 'UCIS':
        return YamlUCIS()
    
    def read(self, filename) -> 'UCIS':
        reader = YamlReader()

        with open(filename, "r") as fp:
            db = reader.load(fp)

        return db
    
    def write(self, db : 'UCIS', file_or_filename):
        raise NotImplementedError("DbFormatIf.write not implemented by %s" % str(type(self)))
    
    @staticmethod
    def register(rgy):
        rgy.addDatabaseFormat(FormatDescDb(
            DbFormatIfYaml,
            name="yaml",
            flags=FormatDbFlags.Read|FormatDbFlags.Write,
            description="Reads coverage data from a YAML file"))
        