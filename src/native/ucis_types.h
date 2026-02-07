/**
 * @file ucis_types.h
 * @brief UCIS type definitions and enumerations
 * 
 * Defines all UCIS data types, enumerations, and structures
 * according to the UCIS 1.0 specification.
 */

#ifndef UCIS_TYPES_H
#define UCIS_TYPES_H

#include <stdint.h>

/* Opaque handle types */
typedef void* ucisT;           /* Database handle */
typedef void* ucisScopeT;      /* Scope handle */
typedef void* ucisCoverT;      /* Coverage item handle */
typedef void* ucisHistoryNodeT; /* History node handle */
typedef void* ucisFileHandleT; /* File handle */

/* Scope type enumeration (one-hot encoded) */
typedef enum {
    UCIS_TOGGLE         = 0x01,
    UCIS_BRANCH         = 0x02,
    UCIS_EXPR           = 0x04,
    UCIS_COND           = 0x08,
    UCIS_INSTANCE       = 0x10,
    UCIS_DU_MODULE      = 0x20,
    UCIS_DU_ARCH        = 0x40,
    UCIS_PACKAGE        = 0x80,
    UCIS_PROGRAM        = 0x100,
    UCIS_CLASS          = 0x200,
    UCIS_FUNCTION       = 0x400,
    UCIS_COVERGROUP     = 0x1000,
    UCIS_COVERINSTANCE  = 0x2000,
    UCIS_COVERPOINT     = 0x4000,
    UCIS_CROSS          = 0x8000,
    UCIS_ASSERT         = 0x800000,
    UCIS_FSM            = 0x400000,
    UCIS_BLOCK          = 0x10000
} ucisScopeTypeT;

/* Coverage type enumeration (one-hot encoded) */
typedef enum {
    UCIS_CVGBIN         = 0x01,
    UCIS_STMTBIN        = 0x02,
    UCIS_BRANCHBIN      = 0x04,
    UCIS_EXPRBIN        = 0x08,
    UCIS_CONDBIN        = 0x10,
    UCIS_TOGGLEBIN      = 0x200,
    UCIS_ASSERTBIN      = 0x400,
    UCIS_FSMBIN         = 0x800,
    UCIS_IGNOREBIN      = 0x80000,
    UCIS_ILLEGALBIN     = 0x100000,
    UCIS_DEFAULTBIN     = 0x200000
} ucisCoverTypeT;

/* History node kind */
typedef enum {
    UCIS_HISTORYNODE_TEST     = 0x01,
    UCIS_HISTORYNODE_MERGE    = 0x02,
    UCIS_HISTORYNODE_TESTPLAN = 0x04
} ucisHistoryNodeKindT;

/* Test status */
typedef enum {
    UCIS_TESTSTATUS_OK      = 0,
    UCIS_TESTSTATUS_WARNING = 1,
    UCIS_TESTSTATUS_FATAL   = 2
} ucisTestStatusT;

/* Source type */
typedef enum {
    UCIS_VHDL        = 0,
    UCIS_VERILOG     = 1,
    UCIS_SV          = 2,
    UCIS_PSL         = 3,
    UCIS_E           = 4,
    UCIS_OTHER_LANG  = 5
} ucisSourceT;

/* Scope flags */
#define UCIS_ENABLED_STMT                0x01
#define UCIS_ENABLED_BRANCH              0x02
#define UCIS_ENABLED_COND                0x04
#define UCIS_ENABLED_EXPR                0x08
#define UCIS_ENABLED_FSM                 0x10
#define UCIS_ENABLED_TOGGLE              0x20
#define UCIS_UOR_SAFE_SCOPE              0x40
#define UCIS_UOR_SAFE_SCOPE_ALLCOVERS    0x80
#define UCIS_INST_ONCE                   0x100

/* Cover flags */
#define UCIS_IS_COVERED                  0x01
#define UCIS_CVG_EXCLUDE                 0x02
#define UCIS_UOR_SAFE_COVERITEM          0x04

/* Source information structure */
typedef struct {
    ucisFileHandleT filehandle;
    int line;
    int token;
} ucisSourceInfoT;

/* Coverage data structure */
typedef struct {
    int type;           /* ucisCoverTypeT */
    int64_t data;       /* Primary count */
    int64_t data_fec;   /* Functional equivalence count */
    int at_least;       /* Coverage threshold */
    int weight;
    int goal;
    int flags;
} ucisCoverDataT;

/* Test data structure */
typedef struct {
    const char* logicalname;
    const char* physicalname;
    int teststatus;
    int64_t simtime;
    int timeunit;
    double cputime;
    const char* seed;
    const char* cmd;
    int compulsory;
    const char* date;
    const char* username;
    double cost;
    const char* toolcategory;
    const char* toolversion;
    const char* toolvendor;
    const char* comment;
} ucisTestDataT;

/* Property keys */
typedef enum {
    UCIS_STR_UNIQUE_ID              = 0x100,
    UCIS_STR_NAME                   = 0x101,
    UCIS_STR_COMMENT                = 0x102,
    UCIS_INT_SCOPE_NUM_COVERS       = 0x200,
    UCIS_INT_COVERAGE_COUNT         = 0x201,
    UCIS_REAL_CVG_INST_AVERAGE      = 0x300
} ucisPropertyKeyT;

/* Property types */
typedef enum {
    UCIS_PROPERTY_INT    = 1,
    UCIS_PROPERTY_REAL   = 2,
    UCIS_PROPERTY_STRING = 3,
    UCIS_PROPERTY_HANDLE = 4
} ucisPropertyTypeT;

/* Object kind for attributes */
typedef enum {
    UCIS_OBJ_SCOPE   = 1,
    UCIS_OBJ_COVER   = 2,
    UCIS_OBJ_HISTORY = 3
} ucisObjKindT;

/* Callback types */
typedef int (*ucisScopeCBT)(void* userdata, ucisScopeT scope);
typedef int (*ucisCoverCBT)(void* userdata, ucisCoverT cover);
typedef int (*ucisHistoryNodeCBT)(void* userdata, ucisHistoryNodeT node);

#endif /* UCIS_TYPES_H */
