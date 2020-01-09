'''
Created on Jan 9, 2020

@author: ballance
'''
from enum import IntEnum, auto

class TestStatus(IntEnum):
    OK = auto()
    WARNING = auto()     #/* test warning ($warning called) */
    ERROR = auto()       #/* test error ($error called) */
    FATAL = auto()       #/* fatal test error ($fatal called) */
    MISSING = auto()     #/* test not run yet */
    MERGE_ERROR = auto() #/* testdata record was merged with inconsistent data values */
