'''
Created on Jan 11, 2020

@author: ballance
'''
from enum import IntFlag

class CoverTypeT(IntFlag):
    """Coverage type identifiers for cover items.
    
    Defines the enumeration of coverage types used to classify cover items (bins)
    in the UCIS data model. The coverage type indicates what kind of coverage
    metric the item represents, such as functional coverage bins, code coverage,
    or assertion results.
    
    Coverage types are implemented as bit flags to support efficient type checking
    and categorization. Each cover item has exactly one coverage type that
    determines its semantics and how coverage tools interpret the data.
    
    Types fall into several categories:
    - **Functional Coverage**: CVGBIN (SystemVerilog covergroups)
    - **Code Coverage**: STMTBIN, BRANCHBIN, EXPRBIN, CONDBIN, TOGGLEBIN, BLOCKBIN
    - **Assertions**: ASSERTBIN, COVERBIN, PASSBIN, FAILBIN, VACUOUSBIN, etc.
    - **FSM Coverage**: FSMBIN
    - **User-defined**: USERBIN, GENERICBIN
    
    Note:
        Coverage types are distinct from scope types. A scope type defines the
        hierarchical container, while a coverage type defines the measurement
        category for individual bins.
        
    See Also:
        CoverItem: Base class for coverage measurements
        ScopeTypeT: Scope type identifiers
        UCIS LRM Section 5.3 "Cover Items"
    """
    
    # Functional coverage types
    CVGBIN = 0x0000000000000001
    """SystemVerilog covergroup bin (functional coverage)."""
    
    # Assertion coverage types
    COVERBIN = 0x0000000000000002
    """Cover directive pass count (cover property succeeded)."""
    
    ASSERTBIN = 0x0000000000000004
    """Assert directive fail count (assertion violated)."""
    
    # Code coverage types
    STMTBIN = 0x0000000000000020
    """Statement coverage bin (line or statement executed)."""
    
    BRANCHBIN = 0x0000000000000040
    """Branch coverage bin (conditional branch taken/not taken)."""
    
    EXPRBIN = 0x0000000000000080
    """Expression coverage bin (sub-expression evaluation)."""
    
    CONDBIN = 0x0000000000000100
    """Condition coverage bin (boolean condition true/false)."""
    
    TOGGLEBIN = 0x0000000000000200
    """Toggle coverage bin (signal transition 0->1 or 1->0)."""
    
    # Additional assertion coverage types
    PASSBIN = 0x0000000000000400
    """Assert directive pass count (assertion succeeded)."""
    
    # FSM coverage type
    FSMBIN = 0x0000000000000800
    """Finite state machine coverage bin (state or transition)."""
    
    # User-defined coverage types
    USERBIN = 0x0000000000001000
    """User-defined coverage metric."""
    
    GENERICBIN = USERBIN
    """Generic user-defined coverage (alias for USERBIN)."""
    
    COUNT = 0x0000000000002000
    """User-defined count metric (not included in coverage percentage)."""
    
    # Additional assertion result types
    FAILBIN = 0x0000000000004000
    """Cover directive fail count (cover property failed)."""
    
    VACUOUSBIN = 0x0000000000008000
    """Assert vacuous pass count (assertion vacuously true)."""
    
    DISABLEDBIN = 0x0000000000010000
    """Assert disabled count (assertion disabled)."""
    
    ATTEMPTBIN = 0x0000000000020000
    """Assert attempt count (assertion evaluation started)."""
    
    ACTIVEBIN = 0x0000000000040000
    """Assert active thread count (concurrent assertion threads)."""
    
    # SystemVerilog covergroup bin types
    IGNOREBIN = 0x0000000000080000
    """SystemVerilog ignore bin (excluded from coverage)."""
    
    ILLEGALBIN = 0x0000000000100000
    """SystemVerilog illegal bin (should not be hit)."""
    
    DEFAULTBIN = 0x0000000000200000
    """SystemVerilog default bin (auto-generated catch-all)."""
    
    PEAKACTIVEBIN = 0x0000000000400000
    """Assert peak active thread count (maximum concurrent threads)."""
    
    # Block coverage type
    BLOCKBIN = 0x0000000001000000
    """Block coverage bin (code block executed)."""
    
    # Reserved bits
    USERBITS = 0x00000000FE000000
    """Reserved bits for user-defined coverage extensions."""
    
    RESERVEDBIN = 0xFF00000000000000
    """Reserved for future use by the UCIS standard."""

    
