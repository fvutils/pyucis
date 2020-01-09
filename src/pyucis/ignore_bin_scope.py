'''
Created on Jan 8, 2020

@author: ballance
'''
from pyucis.cvg_scope import CvgScope

class IgnoreBinScope(CvgScope):
    
    def __init__(self):
        super().__init__()
        