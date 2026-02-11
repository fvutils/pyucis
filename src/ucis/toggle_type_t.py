'''
Created on Jan 12, 2020

@author: ballance
'''
from enum import IntEnum

class ToggleTypeT(IntEnum):
    """Toggle coverage type enumeration.
    
    Defines the type of signal being measured for toggle coverage. Toggle
    coverage tracks transitions (0→1 and 1→0) on digital signals to ensure
    all bits in a design are exercised.
    
    Toggle types distinguish between:
    - **NET**: Continuous assignment signals (wires, nets)
    - **REG**: Registered signals (registers, flip-flops)
    
    This distinction is important because nets and registers have different
    behavioral characteristics and may require different coverage strategies.
    
    Example:
        >>> # Create toggle coverage for a register
        >>> toggle_scope = instance.createToggle(
        ...     name="data_reg",
        ...     srcinfo=src_info,
        ...     canonicalName="top.u_core.data_reg",
        ...     toggleType=ToggleTypeT.REG)
        >>>
        >>> # Create toggle coverage for a wire
        >>> toggle_scope = instance.createToggle(
        ...     name="ready_wire",
        ...     srcinfo=src_info,
        ...     canonicalName="top.u_core.ready",
        ...     toggleType=ToggleTypeT.NET)
        >>>
        >>> # Query toggle type
        >>> ttype = toggle_scope.getToggleType()
        >>> if ttype == ToggleTypeT.REG:
        ...     print("Measuring registered signal")
        
    See Also:
        Scope.createToggle(): Create toggle coverage scopes
        ScopeTypeT.TOGGLE: Toggle scope type
        CoverTypeT.TOGGLEBIN: Toggle bin coverage type
        UCIS LRM Section 6.6 "Toggle Coverage"
    """
    
    NET = 1
    """
    Net/wire signal (continuous assignment).
    
    Toggle coverage for combinational signals, wires, and continuous
    assignments. These signals change value through continuous assignments
    rather than being clocked into registers.
    """
    
    REG = 2
    """
    Registered signal (flip-flop, latch).
    
    Toggle coverage for sequential signals that are stored in flip-flops
    or latches. These signals are typically clocked and hold state.
    """
