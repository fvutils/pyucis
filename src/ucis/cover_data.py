'''
Created on Jan 11, 2020

@author: ballance
'''
from ucis.cover_type_t import CoverTypeT

class CoverData():
    """Container for coverage measurement data.
    
    CoverData encapsulates all measurement values associated with a coverage
    item (bin), including the hit count, goal, weight, and limit. It serves as
    a data transfer object when creating or querying cover items.
    
    Coverage data consists of:
    - **data**: The actual hit count (how many times the item was covered)
    - **goal**: Target count for considering the item "covered"
    - **weight**: Relative importance in coverage calculations
    - **limit**: Maximum count before saturation (coverage stops incrementing)
    - **type**: Coverage type (CVGBIN, BRANCHBIN, TOGGLEBIN, etc.)
    - **flags**: Behavioral flags (data format, has_goal, has_weight, etc.)
    
    The flags determine which fields are valid and how data is interpreted.
    For example, HAS_GOAL flag indicates the goal field is meaningful.
    
    Attributes:
        type (CoverTypeT): Coverage type identifying the metric category.
        flags (CoverFlagsT): Bitwise flags controlling data interpretation.
        data (int): Hit count - number of times this coverage item was hit.
        goal (int): Target count for coverage completion (if HAS_GOAL flag set).
        weight (int): Relative weight for coverage computation (if HAS_WEIGHT flag set).
        limit (int): Count saturation limit (if HAS_LIMIT flag set).
        bitlen (int): Bit length for vector data (if IS_VECTOR flag set).
        
    Example:
        >>> from ucis.cover_flags_t import CoverFlagsT
        >>> # Simple bin with goal and weight
        >>> data = CoverData(
        ...     type=CoverTypeT.CVGBIN,
        ...     flags=CoverFlagsT.HAS_GOAL | CoverFlagsT.HAS_WEIGHT)
        >>> data.goal = 1
        >>> data.weight = 1
        >>> data.data = 0  # Not yet hit
        >>> 
        >>> # Use when creating cover item
        >>> idx = coverpoint.createNextCover("bin_low", data, src_info)
        
    Note:
        Default values (0) are set for all fields. Set flags appropriately to
        indicate which fields contain valid data. Tools may ignore fields whose
        corresponding flags are not set.
        
    See Also:
        Scope.createNextCover(): Create cover items with this data
        CoverTypeT: Coverage type enumeration
        CoverFlagsT: Coverage data flags
        UCIS LRM Section 8.11.3 "ucis_GetCoverData"
        UCIS LRM Section 8.11.4 "ucis_SetCoverData"
    """
    
    def __init__(self,
                 type : CoverTypeT,
                 flags):
        """Create coverage data container.
        
        Args:
            type: Coverage type (CoverTypeT enum) indicating metric category.
            flags: Bitwise OR of CoverFlagsT flags controlling data interpretation.
                Common flags: HAS_GOAL, HAS_WEIGHT, HAS_LIMIT, IS_32BIT, IS_64BIT.
                
        Example:
            >>> # Covergroup bin with goal and weight
            >>> data = CoverData(CoverTypeT.CVGBIN, 
            ...                  CoverFlagsT.HAS_GOAL | CoverFlagsT.HAS_WEIGHT)
            >>> # Branch coverage with just count
            >>> data = CoverData(CoverTypeT.BRANCHBIN, 0)
        """
        self.type = type
        self.flags = flags
        # TODO: determine default data based on flags
        self.data = 0
        self.goal = 0 # if UCIS_HAS_GOAL
        self.weight = 0 # if UCIS_HAS_WEIGHT
        self.limit = 0 # if UCIS_HAS_LIMIT
        self.bitlen = 0 # if bytevector
                 
            