'''
Created on Jan 11, 2020

@author: ballance
'''
from enum import IntEnum, auto

class SourceT(IntEnum):
    VHDL = 0
    VLOG = auto()  #/* Verilog */
    SV = auto()        #/* SystemVerilog */
    SYSTEMC = auto()
    PSL_VHDL = auto()  #/* assert/cover in PSL VHDL */
    PSL_VLOG = auto()  #/* assert/cover in PSL Verilog */
    PSL_SV = auto()    #/* assert/cover in PSL SystemVerilog */
    PSL_SYSTEMC = auto() #/* assert/cover in PSL SystemC */
    E = auto()
    VERA = auto()
    NONE = auto() #/* if not important */
    OTHER = auto() #/* to refer to user-defined attributes */
    SOURCE_ERROR = auto() #/* for error cases */