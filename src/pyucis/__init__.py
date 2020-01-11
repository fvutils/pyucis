from enum import IntEnum, auto
from pyucis import ucis
from pyucis.scope import Scope

from pyucis.handle_property import HandleProperty
from pyucis.history_node import HistoryNode
from pyucis.history_node_kind import HistoryNodeKind
from pyucis.int_property import IntProperty
from pyucis.obj import Obj
from pyucis.real_property import RealProperty
from pyucis.source_info import SourceInfo
from pyucis.str_property import StrProperty
from pyucis.test_data import TestData
from pyucis.test_status import TestStatus
from pyucis.source_t import SourceT
from pyucis.scope_t import ScopeT
from pyucis.flags_t import FlagsT


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

UCIS_STR_FILE_NAME = StrProperty.FILE_NAME
UCIS_STR_SCOPE_NAME = StrProperty.SCOPE_NAME
UCIS_STR_SCOPE_HIER_NAME = StrProperty.SCOPE_HIER_NAME
UCIS_STR_INSTANCE_DU_NAME = StrProperty.INSTANCE_DU_NAME
UCIS_STR_UNIQUE_ID = StrProperty.UNIQUE_ID
UCIS_STR_VER_STANDARD = StrProperty.VER_STANDARD
UCIS_STR_VER_STANDARD_VERSION = StrProperty.VER_STANDARD_VERSION
UCIS_STR_VER_VENDOR_ID = StrProperty.VER_VENDOR_ID
UCIS_STR_VER_VENDOR_TOOL = StrProperty.VER_VENDOR_TOOL
UCIS_STR_VER_VENDOR_VERSION = StrProperty.VER_VENDOR_VERSION
UCIS_STR_GENERIC = StrProperty.GENERIC
UCIS_STR_ITH_CROSSED_CVP_NAME = StrProperty.ITH_CROSSED_CVP_NAME
UCIS_STR_HIST_CMDLINE = StrProperty.HIST_CMDLINE
UCIS_STR_HIST_RUNCWD = StrProperty.HIST_RUNCWD
UCIS_STR_COMMENT = StrProperty.COMMENT
UCIS_STR_TEST_TIMEUNIT = StrProperty.TEST_TIMEUNIT
UCIS_STR_TEST_DATE = StrProperty.TEST_DATE
UCIS_STR_TEST_SIMARGS = StrProperty.TEST_SIMARGS
UCIS_STR_TEST_USERNAME = StrProperty.TEST_USERNAME
UCIS_STR_TEST_NAME = StrProperty.TEST_NAME
UCIS_STR_TEST_SEED = StrProperty.TEST_SEED
UCIS_STR_TEST_HOSTNAME = StrProperty.TEST_HOSTNAME
UCIS_STR_TEST_HOSTOS = StrProperty.TEST_HOSTOS
UCIS_STR_EXPR_TERMS = StrProperty.EXPR_TERMS
UCIS_STR_TOGGLE_CANON_NAME = StrProperty.TOGGLE_CANON_NAME
UCIS_STR_UNIQUE_ID_ALIAS = StrProperty.UNIQUE_ID_ALIAS
UCIS_STR_DESIGN_VERSION_ID = StrProperty.DESIGN_VERSION_ID
UCIS_STR_DU_SIGNATURE = StrProperty.DU_SIGNATURE
UCIS_STR_HIST_TOOLCATEGORY = StrProperty.HIST_TOOLCATEGORY
UCIS_STR_HIST_LOG_NAME = StrProperty.HIST_LOG_NAME
UCIS_STR_HIST_PHYS_NAME = StrProperty.HIST_PHYS_NAME    

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

UCIS_VHDL = SourceT.VHDL
UCIS_VLOG = SourceT.VLOG
UCIS_SV = SourceT.SV
UCIS_SYSTEMC = SourceT.SYSTEMC
UCIS_PSL_VHDL = SourceT.PSL_VHDL
UCIS_PSL_VLOG = SourceT.PSL_VLOG
UCIS_PSL_SV = SourceT.PSL_SV
UCIS_PSL_SYSTEMC = SourceT.PSL_SYSTEMC
UCIS_E = SourceT.E
UCIS_VERA = SourceT.VERA
UCIS_NONE = SourceT.NONE
UCIS_OTHER = SourceT.OTHER
UCIS_SOURCE_ERROR = SourceT.SOURCE_ERROR
    
UCIS_TOGGLE = ScopeT.TOGGLE
UCIS_BRANCH = ScopeT.BRANCH
UCIS_EXPR = ScopeT.EXPR
UCIS_COND = ScopeT.COND
UCIS_INSTANCE = ScopeT.INSTANCE
UCIS_PROCESS = ScopeT.PROCESS
UCIS_BLOCK = ScopeT.BLOCK
UCIS_FUNCTION = ScopeT.FUNCTION
UCIS_FORKJOIN = ScopeT.FORKJOIN
UCIS_GENERATE = ScopeT.GENERATE
UCIS_GENERIC = ScopeT.GENERIC
UCIS_CLASS = ScopeT.CLASS
UCIS_COVERGROUP = ScopeT.COVERGROUP
UCIS_COVERINSTANCE = ScopeT.COVERINSTANCE
UCIS_COVERPOINT = ScopeT.COVERPOINT
UCIS_CROSS = ScopeT.CROSS
UCIS_COVER = ScopeT.COVER
UCIS_ASSERT = ScopeT.ASSERT
UCIS_PROGRAM = ScopeT.PROGRAM
UCIS_PACKAGE = ScopeT.PACKAGE
UCIS_TASK = ScopeT.TASK
UCIS_INTERFACE = ScopeT.INTERFACE
UCIS_FSM = ScopeT.FSM
UCIS_DU_MODULE = ScopeT.DU_MODULE
UCIS_DU_ARCH = ScopeT.DU_ARCH
UCIS_DU_PACKAGE = ScopeT.DU_PACKAGE
UCIS_DU_PROGRAM = ScopeT.DU_PROGRAM
UCIS_DU_INTERFACE = ScopeT.DU_INTERFACE
UCIS_FSM_STATES = ScopeT.FSM_STATES
UCIS_FSM_TRANS = ScopeT.FSM_TRANS
UCIS_COVBLOCK = ScopeT.COVBLOCK
UCIS_CVGBINSCOPE = ScopeT.CVGBINSCOPE
UCIS_ILLEGALBINSCOPE = ScopeT.ILLEGALBINSCOPE
UCIS_IGNOREBINSCOPE = ScopeT.IGNOREBINSCOPE
UCIS_RESERVEDSCOPE = ScopeT.RESERVEDSCOPE
UCIS_SCOPE_ERROR = ScopeT.SCOPE_ERROR

UCIS_INST_ONCE = FlagsT.INST_ONCE
UCIS_ENABLED_STMT = FlagsT.ENABLED_STMT
UCIS_ENABLED_BRANCH = FlagsT.ENABLED_BRANCH
UCIS_ENABLED_COND = FlagsT.ENABLED_COND
UCIS_ENABLED_EXPR = FlagsT.ENABLED_EXPR
UCIS_ENABLED_FSM = FlagsT.ENABLED_FSM
UCIS_ENABLED_TOGGLE = FlagsT.ENABLED_TOGGLE
UCIS_SCOPE_UNDER_DU = FlagsT.SCOPE_UNDER_DU
UCIS_SCOPE_EXCLUDED = FlagsT.SCOPE_EXCLUDED
UCIS_SCOPE_PRAGMA_EXCLUDED = FlagsT.SCOPE_PRAGMA_EXCLUDED
UCIS_SCOPE_PRAGMA_CLEARED = FlagsT.SCOPE_PRAGMA_CLEARED
UCIS_SCOPE_SPECIALIZED = FlagsT.SCOPE_SPECIALIZED
UCIS_UOR_SAFE_SCOPE = FlagsT.UOR_SAFE_SCOPE
UCIS_UOR_SAFE_SCOPE_ALLCOVERS = FlagsT.UOR_SAFE_SCOPE_ALLCOVERS
UCIS_IS_TOP_NODE = FlagsT.IS_TOP_NODE
UCIS_IS_IMMEDIATE_ASSERT = FlagsT.IS_IMMEDIATE_ASSERT
UCIS_SCOPE_CVG_AUTO = FlagsT.SCOPE_CVG_AUTO
UCIS_SCOPE_CVG_SCALAR = FlagsT.SCOPE_CVG_SCALAR
UCIS_SCOPE_CVG_VECTOR = FlagsT.SCOPE_CVG_VECTOR
UCIS_SCOPE_CVG_TRANSITION = FlagsT.SCOPE_CVG_TRANSITION
UCIS_SCOPE_IFF_EXISTS = FlagsT.SCOPE_IFF_EXISTS
UCIS_ENABLED_BLOCK = FlagsT.ENABLED_BLOCK
UCIS_SCOPE_BLOCK_ISBRANCH = FlagsT.SCOPE_BLOCK_ISBRANCH
    
    
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
        property : StrProperty
        ) -> str:
    if obj is not None:
        return obj.getStringProperty(coverindex, property)
    else:
        return db.getStringProperty(coverindex, property)
    
def ucis_SetStringProperty(
        db : ucis,
        obj : Obj,
        coverindex : int,
        property : StrProperty,
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
        sourceinfo : SourceInfo,
        weight : int,
        source : SourceT,
        type : ScopeT,
        flags) -> Scope:
    if parent is not None:
        return parent.createScope(name, sourceinfo, weight, source, type, flags)
    else:
        return db.createScope(name, sourceinfo, weight, source, type, flags)

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
    return db.createHistoryNode(parent, logicalname, physicalname, kind)

def ucis_CreateFileHandle (
    db : ucis,
    filename : str,
    fileworkdir : str):
    return db.createFileHandle(filename, fileworkdir)

def ucis_SetTestData(
    db : ucis,
    testhistorynode : HistoryNode,
    testdata : TestData):
    testhistorynode.setTestData(testdata)

