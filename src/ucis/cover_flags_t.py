'''
Created on Jan 11, 2020

@author: ballance
'''
from enum import IntFlag

class CoverFlagsT(IntFlag):
    """Coverage data flags for cover items.
    
    Defines bit flags that control the interpretation and format of coverage
    data in CoverData objects. Flags indicate which fields are valid, data
    precision, and coverage item behaviors.
    
    Flags are used to:
    - Specify data precision (32-bit vs 64-bit vs vector)
    - Indicate which optional fields are present (goal, weight, limit)
    - Control exclusion and enablement
    - Mark coverage status
    - Store type-specific behaviors (assertion actions, FSM transitions, etc.)
    
    Flags are combined using bitwise OR when creating CoverData objects.
    
    See Also:
        CoverData: Coverage data container using these flags
        UCIS LRM Section 8.11 "Coveritem Creation and Manipulation"
    """
    
    # Data format flags
    IS_32BIT = 0x00000001
    """Coverage data is 32-bit integer."""
    
    IS_64BIT = 0x00000002
    """Coverage data is 64-bit integer."""
    
    IS_VECTOR = 0x00000004
    """Coverage data is bit vector (use bitlen field)."""
    
    # Optional field flags
    HAS_GOAL = 0x00000008
    """Goal field is included and meaningful."""
    
    HAS_WEIGHT = 0x00000010
    """Weight field is included and meaningful."""
    
    # Note: The following flags are defined in comments in the original file
    # but not implemented as Python enum values. They are included here for
    # documentation purposes and may be added in future versions:
    #
    # HAS_LIMIT = 0x00000400        # Count saturation limit included
    # HAS_COUNT = 0x00000800        # Has count value
    # IS_COVERED = 0x00001000       # Item is covered (goal met)
    # EXCLUDE_PRAGMA = 0x00000020   # Excluded by pragma directive
    # EXCLUDE_FILE = 0x00000040     # Excluded by file (not in total)
    # EXCLUDE_INST = 0x00000080     # Instance-specific exclusion
    # EXCLUDE_AUTO = 0x00000100     # Automatic exclusion
    # ENABLED = 0x00000200          # Item is enabled for coverage
    # UOR_SAFE_COVERITEM = 0x00002000  # Universal Object Recognition compliant
    # CLEAR_PRAGMA = 0x00004000     # Pragma exclusion cleared
    #
    # Type-qualified flags (0x07FF0000 - flag locations may be reused):
    # HAS_ACTION = 0x00010000       # ASSERTBIN: has action
    # IS_TLW_ENABLED = 0x00020000   # ASSERTBIN: TLW enabled
    # LOG_ON = 0x00040000           # COVERBIN/ASSERTBIN: logging on
    # IS_EOS_NOTE = 0x00080000      # COVERBIN/ASSERTBIN: end-of-sim note
    # IS_FSM_RESET = 0x00010000     # FSMBIN: reset state
    # IS_FSM_TRAN = 0x00020000      # FSMBIN: transition
    # IS_BR_ELSE = 0x00010000       # BRANCHBIN: else branch
    # BIN_IFF_EXISTS = 0x00010000   # CVGBIN: iff condition exists
    # BIN_SAMPLE_TRUE = 0x00020000  # CVGBIN: sample condition true
    # IS_CROSSAUTO = 0x00040000     # CROSS: auto-generated cross
    # COVERFLAG_MARK = 0x08000000   # Temporary mark flag
    # USERFLAGS = 0xF0000000        # Reserved for user flags

