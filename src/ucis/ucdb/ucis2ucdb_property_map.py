'''
Created on Feb 2, 2021

@author: mballance
'''
from ucis.int_property import IntProperty


class Ucis2UcdbPropertyMap(object):
    
    @staticmethod
    def int2attr(p : IntProperty):
        return {
            IntProperty.IS_MODIFIED : None,
            IntProperty.MODIFIED_SINCE_SIM : None,
            IntProperty.NUM_TESTS : None,
            IntProperty.SCOPE_WEIGHT : None,
            IntProperty.SCOPE_GOAL : "#GOAL#",
            IntProperty.SCOPE_SOURCE_TYPE : None,
            IntProperty.NUM_CROSSED_CVPS : None,
            IntProperty.SCOPE_IS_UNDER_DU : None,
            IntProperty.SCOPE_IS_UNDER_COVERINSTANCE : None,
            IntProperty.SCOPE_NUM_COVERITEMS : None,
            IntProperty.SCOPE_NUM_EXPR_TERMS : None,
            IntProperty.TOGGLE_TYPE : None,
            IntProperty.TOGGLE_DIR : None,
            IntProperty.TOGGLE_COVERED : None,
            IntProperty.BRANCH_HAS_ELSE : "#BHASELSE#",
            IntProperty.BRANCH_ISCASE : "#BTYPE#",
            IntProperty.COVER_GOAL : "#GOAL#",
            IntProperty.COVER_LIMIT : None,
            IntProperty.COVER_WEIGHT : None,
            IntProperty.TEST_STATUS : None,
            IntProperty.TEST_COMPULSORY : None,
            IntProperty.STMT_INDEX : "#SINDEX#",
            IntProperty.BRANCH_COUNT : "#BCOUNT#",
            IntProperty.FSM_STATEVAL : "#FSTATEVAL#",
            IntProperty.CVG_ATLEAST : "ATLEAST",
            IntProperty.CVG_AUTOBINMAX : "AUTOBINMAX",
            IntProperty.CVG_DETECTOVERLAP : "DETECTOVERLAP",
            IntProperty.CVG_NUMPRINTMISSING : "PRINTMISSING",
            IntProperty.CVG_STROBE : "STROBE",
            IntProperty.CVG_PERINSTANCE : "PERINSTANCE",
            IntProperty.CVG_GETINSTCOV : "GETINSTCOV",
            IntProperty.CVG_MERGEINSTANCES : "MERGEINSTANCES"
            }[p]