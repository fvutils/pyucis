from pyucis import ucis
from pyucis.scope import Scope
from pyucis.source_info import SourceInfo
from pyucis.obj import Obj
from enum import IntEnum, auto
from pyucis.int_property import IntProperty
from pyucis.real_property import RealProperty
from pyucis.string_property import StringProperty
from pyucis.handle_property import HandleProperty
from pyucis.test_status import TestStatus
from pyucis.history_node_kind import HistoryNodeKind
from pyucis.history_node import HistoryNode
from pyucis.test_data import TestData

#********************************************************************
#* Property Functions
#********************************************************************

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

UCIS_TESTSTATUS_OK = TestStatus.OK
UCIS_TESTSTATUS_WARNING = TestStatus.WARNING    #/* test warning ($warning called) */
UCIS_TESTSTATUS_ERROR = TestStatus.ERROR      #/* test error ($error called) */
UCIS_TESTSTATUS_FATAL = TestStatus.FATAL      #/* fatal test error ($fatal called) */
UCIS_TESTSTATUS_MISSING = TestStatus.MISSING         #/* test not run yet */
UCIS_TESTSTATUS_MERGE_ERROR = TestStatus.MERGE_ERROR #/* testdata record was merged with inconsistent data values */

UCIS_HISTORYNODE_NONE   = HistoryNodeKind.NONE
UCIS_HISTORYNODE_ALL    = HistoryNodeKind.ALL
UCIS_HISTORYNODE_TEST   = HistoryNodeKind.TEST
UCIS_HISTORYNODE_MERGE  = HistoryNodeKind.MERGE
    
    
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

def ucis_CreateHistoryNode(
    db : ucis,
    parent : HistoryNode,
    logicalname,   #/* primary key, never NULL */
    physicalname,
    kind : HistoryNodeKind):
    # TODO: what if parent is non-null?
    return db.createHistoryNode(logicalname, physicalname, kind)

def ucis_SetTestData(
    db : ucis,
    testhistorynode : HistoryNode,
    testdata : TestData):
    testhistorynode.setTestData(testdata)

