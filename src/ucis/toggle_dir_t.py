'''
Created on Jan 12, 2020

@author: ballance
'''
from enum import IntEnum, auto

class ToggleDirT(IntEnum):
    """Toggle signal direction enumeration.
    
    Defines the direction or port type of signals being measured for toggle
    coverage. Direction affects how toggle coverage is analyzed and reported.
    
    Signal directions include:
    - **INTERNAL**: Internal wires or variables (non-port)
    - **IN**: Input ports
    - **OUT**: Output ports  
    - **INOUT**: Bidirectional ports
    
    Example:
        >>> # Create toggle for output port
        >>> toggle_scope = instance.createToggle(
        ...     name="data_out",
        ...     srcinfo=src_info,
        ...     canonicalName="top.data_out",
        ...     direction=ToggleDirT.OUT)
        >>>
        >>> # Internal signal
        >>> toggle_scope = instance.createToggle(
        ...     name="state_reg",
        ...     srcinfo=src_info,
        ...     canonicalName="top.u_core.state",
        ...     direction=ToggleDirT.INTERNAL)
        
    See Also:
        ToggleTypeT: Toggle type (NET vs REG)
        ScopeTypeT.TOGGLE: Toggle scope type
        UCIS LRM Section 6.6 "Toggle Coverage"
    """
    
    INTERNAL = 1
    """Non-port signal: internal wire or variable within a module."""
    
    IN = auto()
    """Input port signal."""
    
    OUT = auto()
    """Output port signal."""
    
    INOUT = auto()
    """Bidirectional (inout) port signal."""
