'''
Created on Jan 12, 2020

@author: ballance
'''
from enum import IntEnum, auto

class ToggleMetricT(IntEnum):
    """Toggle coverage metric types.
    
    Defines the type of toggle metric being measured. Different metrics track
    different aspects of signal transitions and state changes.
    
    Metric types:
    - **NOBINS**: Scope has no local bins (hierarchical container)
    - **ENUM**: Enumerated state tracking (UCIS:ENUM)
    - **TRANSITION**: State transition tracking (UCIS:TRANSITION)
    - **_2STOGGLE**: 2-state toggle (0→1, 1→0) (UCIS:2STOGGLE)
    - **ZTOGGLE**: High-impedance toggle tracking (UCIS:ZTOGGLE)
    - **XTOGGLE**: Unknown value toggle tracking (UCIS:XTOGGLE)
    
    Example:
        >>> # Standard 2-state toggle
        >>> toggle = instance.createToggle(
        ...     name="data_bus",
        ...     srcinfo=src_info,
        ...     canonicalName="top.data",
        ...     metric=ToggleMetricT._2STOGGLE)
        >>>
        >>> # Tri-state signal with Z tracking
        >>> toggle = instance.createToggle(
        ...     name="tristate_bus",
        ...     srcinfo=src_info,
        ...     canonicalName="top.ts_data",
        ...     metric=ToggleMetricT.ZTOGGLE)
        
    See Also:
        ToggleTypeT: Toggle type (NET vs REG)
        ToggleDirT: Signal direction
        UCIS LRM Section 6.6 "Toggle Coverage"
    """
    
    NOBINS     = 1
    """Toggle scope has no local bins (hierarchical container only)."""
    
    ENUM       = auto()
    """Enumerated state tracking (UCIS:ENUM)."""
    
    TRANSITION = auto()
    """State transition tracking (UCIS:TRANSITION)."""
    
    _2STOGGLE  = auto()
    """2-state toggle: 0→1 and 1→0 transitions (UCIS:2STOGGLE)."""
    
    ZTOGGLE    = auto()
    """High-impedance toggle tracking (UCIS:ZTOGGLE)."""
    
    XTOGGLE    = auto()
    """Unknown value toggle tracking (UCIS:XTOGGLE)."""
