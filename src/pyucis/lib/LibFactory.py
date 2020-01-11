'''
Created on Jan 10, 2020

@author: ballance
'''
from ctypes import *
from pyucis.lib import libucis
from pyucis.lib.libucis import _lib, get_ucis_library
from pyucis.lib.lib_ucis import LibUCIS

class LibFactory():

    @staticmethod
    def create(file=None):
        if get_ucis_library() is None:
            raise Exception("libucis not loaded")
        
        return LibUCIS(file)
        

    # Load the specified UCIS library
    @staticmethod
    def load_ucis_library(lib):
        libucis.load_ucis_library(lib)
    