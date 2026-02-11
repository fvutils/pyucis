'''
Created on Jan 12, 2020

@author: ballance
'''
from ucis.obj import Obj
from ucis.unimpl_error import UnimplError

class CoverItem(Obj):
    """Base class for coverage items (bins).
    
    CoverItem is the base class for all coverage leaf nodes in the UCIS
    hierarchy. Coverage items (also called "bins") represent individual
    coverage points such as:
    - Covergroup bins (CVGBIN)
    - Branch outcomes (BRANCHBIN)
    - Toggle states (TOGGLEBIN)
    - Assertion outcomes (ASSERTBIN)
    - FSM transitions (FSMBIN)
    
    Unlike scopes which form the hierarchical tree structure, coverage items
    are leaf nodes that contain measurement data (hit counts) but no children.
    
    Coverage items are typically accessed via CoverIndex objects obtained by
    iterating over a scope's cover items, rather than by direct instantiation
    of CoverItem subclasses.
    
    Note:
        This class extends Obj, inheriting the property interface for
        accessing integer, real, string, and handle properties. Properties
        on cover items are accessed with coverindex ≥ 0, unlike scope-level
        properties which use coverindex = -1.
        
    Example:
        >>> # Access cover items in a scope
        >>> for cover_idx in coverpoint.coverItems():
        ...     # Each cover_idx provides access to a CoverItem
        ...     name = cover_idx.getName()
        ...     data = cover_idx.getCoverData()
        ...
        >>> # Get property from a cover item
        >>> count = coverpoint.getIntProperty(
        ...     IntProperty.COUNT, coverindex=0)
        
    See Also:
        CoverIndex: Reference to coverage items
        Scope.coverItems(): Iterate cover items
        Scope.createNextCover(): Create new cover items
        CoverData: Coverage measurement data
        UCIS LRM Section 8.11 "Coveritem Creation and Manipulation"
    """
    
    def __init__(self):
        super().__init__()
        
    def getStmtIndex(self)->int:
        """Get the statement index for code coverage items.
        
        For code coverage types (statement, branch, condition, expression),
        returns the index identifying which statement in the scope this
        coverage item represents. This links coverage data to specific
        statements in the source code.
        
        Returns:
            Statement index (non-negative integer), or implementation-specific
            value if not applicable for this coverage type.
            
        Raises:
            UnimplError: Not implemented in base class or specific backend.
            
        Note:
            This method is primarily relevant for code coverage scopes
            (STMTBIN, BRANCHBIN, CONDBIN, EXPRBIN). For other coverage types
            like covergroups or toggles, the return value may not be meaningful.
            
        See Also:
            setStmtIndex(): Set statement index
            CoverTypeT: Coverage type enumeration
        """
        raise UnimplError()
    
    def setStmtIndex(self, i):
        """Set the statement index for code coverage items.
        
        Sets the statement index that links this coverage item to a specific
        statement in the source code. Used primarily for code coverage types.
        
        Args:
            i: Statement index (non-negative integer).
            
        Raises:
            UnimplError: Not implemented in base class or specific backend.
            
        See Also:
            getStmtIndex(): Query statement index
        """
        raise UnimplError()

        