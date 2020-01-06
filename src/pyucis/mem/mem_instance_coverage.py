'''
Created on Jan 5, 2020

@author: ballance
'''
from pyucis.statement_id import StatementId
from pyucis.instance_coverage import InstanceCoverage

class MemInstanceCoverage(InstanceCoverage):
    
    def __init__(self, 
                 name : str,
                 key : str,
                 stmt_id : StatementId):
        self.name = name
        self.key = key
        self.stmt_id = stmt_id
        self.instanceId = None # optional
        self.alias = None # optional
        self.moduleName = None # optional
        self.parentInstanceId = -1 # optional
        self.design_parameter_l = []
        self.toggle_coverage_l = []
        self.block_coverage_l = []
        self.condition_coverage_l = []
        self.branch_coverage_l = []
        self.fsm_coverage_l = []
        self.assertion_coverage_l = []
        self.covergroup_coverage_l = []
        self.user_attr_l = []
        pass

    def getId(self)->StatementId:
        return self.stmt_id
    
    def getName(self)->str:
        return self.name
    
    def getKey(self)->str:
        return self.key