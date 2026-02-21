'''
Created on Jun 11, 2022

@author: mballance
'''
from ucis.rgy.format_if_db import FormatIfDb, FormatDescDb, FormatDbFlags, FormatCapabilities
from ucis.yaml.yaml_ucis import YamlUCIS
from .yaml_reader import YamlReader
from .yaml_writer import YamlWriter

class DbFormatIfYaml(FormatIfDb):
    
    def init(self, options):
        raise NotImplementedError("DbFormatIf.init not implemented by %s" % str(type(self)))
    
    def create(self, filename=None) -> 'UCIS':
        return YamlUCIS()
    
    def read(self, filename) -> 'UCIS':
        reader = YamlReader()

        with open(filename, "r") as fp:
            db = reader.load(fp)

        return db

    def write(self, db, filename, ctx=None):
        YamlWriter().write(db, filename, ctx)
    
    @staticmethod
    def register(rgy):
        rgy.addDatabaseFormat(FormatDescDb(
            DbFormatIfYaml,
            name="yaml",
            flags=FormatDbFlags.Read|FormatDbFlags.Write,
            description="Reads/writes coverage data in PyUCIS YAML format",
            capabilities=FormatCapabilities(
                can_read=True, can_write=True,
                functional_coverage=True, cross_coverage=True,
                ignore_illegal_bins=True, code_coverage=False,
                toggle_coverage=False, fsm_coverage=False,
                assertions=False, history_nodes=False,
                design_hierarchy=False, lossless=False,
            )))
        