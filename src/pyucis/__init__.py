from pyucis import ucis
from pyucis.scope import Scope
from pyucis.source_info import SourceInfo
from pyucis.obj import Obj
from enum import IntEnum, auto

#********************************************************************
#* Property Functions
#********************************************************************

class IntProperty(IntEnum):
    IS_MODIFIED = auto() # Modified since opening stored UCISDB (In-memory and read only)
    MODIFIED_SINCE_SIM = auto() # Modified since end of simulation run (In-memory and read only)
    NUM_TESTS = auto() # Number of test history nodes (UCIS_HISTORYNODE_TEST) in UCISDB 
    SCOPE_WEIGHT = auto() # Scope weight 
    SCOPE_GOAL = auto() # Scope goal 
    SCOPE_SOURCE_TYPE = auto() # Scope source type (ucisSourceT) 
    NUM_CROSSED_CVPS = auto() # Number of coverpoints in a cross (read only) 
    SCOPE_IS_UNDER_DU = auto() # Scope is underneath design unit scope (read only) 
    SCOPE_IS_UNDER_COVERINSTANCE = auto() # Scope is underneath covergroup instance (read only) 
    SCOPE_NUM_COVERITEMS = auto() # Number of coveritems underneath scope (read only) 
    SCOPE_NUM_EXPR_TERMS = auto() # Number of input ordered expr term strings delimited by '#' 
    TOGGLE_TYPE = auto() # Toggle type (ucisToggleTypeT) 
    TOGGLE_DIR = auto() # Toggle direction (ucisToggleDirT) 
    TOGGLE_COVERED = auto() # Toggle object is covered 
    BRANCH_HAS_ELSE = auto() # Branch has an 'else' coveritem 
    BRANCH_ISCASE = auto() # Branch represents 'case' statement 
    COVER_GOAL = auto() # Coveritem goal 
    COVER_LIMIT = auto() # Coverage count limit for coveritem 
    COVER_WEIGHT = auto() # Coveritem weight 
    TEST_STATUS = auto() # Test run status (ucisTestStatusT) 
    TEST_COMPULSORY = auto() # Test run is compulsory 
    STMT_INDEX = auto() # Index or number of statement on a line 
    BRANCH_COUNT = auto() # Total branch execution count 
    FSM_STATEVAL = auto() # FSM state value 
    CVG_ATLEAST = auto() # Covergroup at_least option 
    CVG_AUTOBINMAX = auto() # Covergroup auto_bin_max option 
    CVG_DETECTOVERLAP = auto() # Covergroup detect_overlap option 
    CVG_NUMPRINTMISSING = auto() # Covergroup cross_num_print_missing option 
    CVG_STROBE = auto() # Covergroup strobe option 
    CVG_PERINSTANCE = auto() # Covergroup per_instance option 
    CVG_GETINSTCOV = auto() # Covergroup get_inst_coverage option 
    CVG_MERGEINSTANCES = auto() # Covergroup merge_instances option     

# Global declarations    
UCIS_INT_IS_MODIFIED = IntProperty.IS_MODIFIED
UCIS_INT_MODIFIED_SINCE_SIM = IntProperty.MODIFIED_SINCE_SIM
UCIS_INT_NUM_TESTS = IntProperty.NUM_TESTS
UCIS_INT_SCOPE_WEIGHT = IntProperty.SCOPE_WEIGHT
UCIS_INT_SCOPE_GOAL = IntProperty.SCOPE_GOAL
UCIS_INT_SCOPE_SOURCE_TYPE = IntProperty.SCOPE_SOURCE_TYPE
UCIS_INT_NUM_CROSSED_CVPS = IntProperty.NUM_CROSSED_CVPS
UCIS_INT_SCOPE_IS_UNDER_DU = IntProperty.SCOPE_IS_UNDER_DU
UCIS_INT_SCOPE_IS_UNDER_COVERINSTANCE = IntProperty.SCOPE_IS_UNDER_COVERINSTANCE
UCIS_INT_SCOPE_NUM_COVERITEMS = IntProperty.SCOPE_NUM_COVERITEMS
UCIS_INT_SCOPE_NUM_EXPR_TERMS = IntProperty.SCOPE_NUM_EXPR_TERMS
UCIS_INT_TOGGLE_TYPE = IntProperty.TOGGLE_TYPE
UCIS_INT_TOGGLE_DIR = IntProperty.TOGGLE_DIR
UCIS_INT_TOGGLE_COVERED = IntProperty.TOGGLE_COVERED
UCIS_INT_BRANCH_HAS_ELSE = IntProperty.BRANCH_HAS_ELSE
UCIS_INT_BRANCH_ISCASE = IntProperty.BRANCH_ISCASE
UCIS_INT_COVER_GOAL = IntProperty.COVER_GOAL
UCIS_INT_COVER_LIMIT = IntProperty.COVER_LIMIT
UCIS_INT_COVER_WEIGHT = IntProperty.COVER_WEIGHT
UCIS_INT_TEST_STATUS = IntProperty.TEST_STATUS
UCIS_INT_TEST_COMPULSORY = IntProperty.TEST_COMPULSORY
UCIS_INT_STMT_INDEX = IntProperty.STMT_INDEX
UCIS_INT_BRANCH_COUNT = IntProperty.BRANCH_COUNT
UCIS_INT_FSM_STATEVAL = IntProperty.FSM_STATEVAL
UCIS_INT_CVG_ATLEAST = IntProperty.CVG_ATLEAST
UCIS_INT_CVG_AUTOBINMAX = IntProperty.CVG_AUTOBINMAX
UCIS_INT_CVG_DETECTOVERLAP = IntProperty.CVG_DETECTOVERLAP
UCIS_INT_CVG_NUMPRINTMISSING = IntProperty.CVG_NUMPRINTMISSING
UCIS_INT_CVG_STROBE = IntProperty.CVG_STROBE
UCIS_INT_CVG_PERINSTANCE = IntProperty.CVG_PERINSTANCE
UCIS_INT_CVG_GETINSTCOV = IntProperty.CVG_GETINSTCOV
UCIS_INT_CVG_MERGEINSTANCES = IntProperty.CVG_MERGEINSTANCES
    
class RealProperty(IntEnum):
    b = 0
    
class StringProperty(IntEnum):
    c = 0
    
class HandleProperty(IntEnum):
    d = 0
    
def ucis_GetIntProperty(
        db : ucis,
        obj : Obj,
        coverindex : int,
        property : IntProperty
        ) -> int:
    if obj is not None:
        return obj.getIntProperty(coverindex, property)
    else:
        return db.getIntProperty(coverindex, property)
    
def ucis_SetIntProperty(
        db : ucis,
        obj : Obj,
        coverindex : int,
        property : IntProperty,
        value : int
        ):
    if obj is not None:
        obj.setIntProperty(coverindex, property, value)
    else:
        db.setIntProperty(coverindex, property, value)
        
def ucis_GetRealProperty(
        db : ucis,
        obj : Obj,
        coverindex : int,
        property : RealProperty
        ) -> float:
    if obj is not None:
        return obj.getRealProperty(coverindex, property)
    else:
        return db.getRealProperty(coverindex, property)
    
def ucis_SetRealProperty(
        db : ucis,
        obj : Obj,
        coverindex : int,
        property : RealProperty,
        value : float
        ):
    if obj is not None:
        obj.setRealProperty(coverindex, property, value)
    else:
        db.setRealProperty(coverindex, property, value)

def ucis_GetStringProperty(
        db : ucis,
        obj : Obj,
        coverindex : int,
        property : StringProperty
        ) -> str:
    if obj is not None:
        return obj.getStringProperty(coverindex, property)
    else:
        return db.getStringProperty(coverindex, property)
    
def ucis_SetStringProperty(
        db : ucis,
        obj : Obj,
        coverindex : int,
        property : StringProperty,
        value : str
        ):
    if obj is not None:
        obj.setStringProperty(coverindex, property, value)
    else:
        db.setStringProperty(coverindex, property, value)
        
def ucis_GetHandleProperty(
        db : ucis,
        obj : Obj,
        coverindex : int,
        property : HandleProperty
        ) -> Scope:
    if obj is not None:
        return obj.getHandleProperty(coverindex, property)
    else:
        return db.getHandleProperty(coverindex, property)
    
def ucis_SetHandleProperty(
        db : ucis,
        obj : Obj,
        coverindex : int,
        property : HandleProperty,
        value : Scope
        ):
    if obj is not None:
        obj.setHandleProperty(coverindex, property, value)
    else:
        db.setHandleProperty(coverindex, property, value)        
        
def ucis_CreateScope(
        db : ucis,
        parent : Scope,
        name : str,
        weight : int,
        source : SourceInfo,
        type,
        flags) -> Scope:
    if parent is not None:
        return parent.createScope(name, weight, source, type, flags)
    else:
        return db.createScope(name, weight, source, type, flags)

def ucis_RemoveScope(
        db : ucis,
        scope : Scope) -> int:
    return db.removeScope(scope)

