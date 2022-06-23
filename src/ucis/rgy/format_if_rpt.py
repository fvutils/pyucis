'''
Created on Jun 22, 2022

@author: mballance
'''
from ucis.ucis import UCIS

class FormatDescRpt(object):
    
    def __init__(self, 
                 fmt_if : 'FormatIfDb',
                 name : str,
                 description : str):
        self._fmt_if = fmt_if
        self._name = name
        self._description = description
        
    @property
    def fmt_if(self):
        return self._fmt_if

    @property
    def name(self):
        return self._name
    
    @property
    def description(self):
        return self._description

class FormatIfRpt(object):
    
    def report(self, 
               db : UCIS,
               out,
               args):
        raise NotImplementedError("FormatIfRpt.report not implemented by %s" % str(type(self)))
    