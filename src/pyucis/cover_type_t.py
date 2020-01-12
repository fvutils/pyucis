'''
Created on Jan 11, 2020

@author: ballance
'''
from enum import IntFlag

class CoverTypeT(IntFlag):
    # For SV Covergroups:
    CVGBIN = 0x0000000000000001
    # For cover directives- pass:
    COVERBIN = 0x0000000000000002
    # For assert directives- fail: 
    ASSERTBIN = 0x0000000000000004
    # For Code coverage(Statement):
    STMTBIN = 0x0000000000000020
# #define UCIS_BRANCHBIN      /* For Code coverage(Branch): */ \
#                              INT64_LITERAL(0x0000000000000040)
# #define UCIS_EXPRBIN         /* For Code coverage(Expression): */ \
#                              INT64_LITERAL(0x0000000000000080)
# #define UCIS_CONDBIN         /* For Code coverage(Condition): */ \
#                              INT64_LITERAL(0x0000000000000100)
# #define UCIS_TOGGLEBIN       /* For Code coverage(Toggle): */ \
#                              INT64_LITERAL(0x0000000000000200)
# #define UCIS_PASSBIN         /* For assert directives- pass count: */ \
#                              INT64_LITERAL(0x0000000000000400)
# #define UCIS_FSMBIN          /* For FSM coverage: */ \
#                              INT64_LITERAL(0x0000000000000800)
# #define UCIS_USERBIN         /* User-defined coverage: */ \
#                              INT64_LITERAL(0x0000000000001000)
# #define UCIS_GENERICBIN      UCIS_USERBIN
# #define UCIS_COUNT           /* user-defined count, not in coverage: */ \
#                              INT64_LITERAL(0x0000000000002000)
# #define UCIS_FAILBIN         /* For cover directives- fail count: */ \
#                              INT64_LITERAL(0x0000000000004000)
# #define UCIS_VACUOUSBIN      /* For assert- vacuous pass count: */ \
#                              INT64_LITERAL(0x0000000000008000)
# #define UCIS_DISABLEDBIN     /* For assert- disabled count: */ \
#                              INT64_LITERAL(0x0000000000010000)
# #define UCIS_ATTEMPTBIN      /* For assert- attempt count: */ \
#                              INT64_LITERAL(0x0000000000020000)
# #define UCIS_ACTIVEBIN       /* For assert- active thread count: */ \
#                              INT64_LITERAL(0x0000000000040000)
# #define UCIS_IGNOREBIN       /* For SV Covergroups: */ \
#                              INT64_LITERAL(0x0000000000080000)
# #define UCIS_ILLEGALBIN      /* For SV Covergroups: */ \
#                              INT64_LITERAL(0x0000000000100000)
# #define UCIS_DEFAULTBIN      /* For SV Covergroups: */ \
#                              INT64_LITERAL(0x0000000000200000)
# #define UCIS_PEAKACTIVEBIN   /* For assert- peak active thread count: */ \
#                              INT64_LITERAL(0x0000000000400000)
# #define UCIS_BLOCKBIN        /* For Code coverage(Block): */ \
#                              INT64_LITERAL(0x0000000001000000)
# #define UCIS_USERBITS        /* For user-defined coverage: */ \
#                              INT64_LITERAL(0x00000000FE000000)
# #define UCIS_RESERVEDBIN     INT64_LITERAL(0xFF00000000000000)
    
