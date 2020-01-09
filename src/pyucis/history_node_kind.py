'''
Created on Jan 9, 2020

@author: ballance
'''
from enum import IntEnum

class HistoryNodeKind(IntEnum):
    
    NONE  = -1
    ALL   =  0  #/* valid only in iterate-all request */
                #/* (no real object gets this value)  */
    TEST  =  1  #/* test leaf node (primary database) */
    MERGE =  2  #/* merge node */
    