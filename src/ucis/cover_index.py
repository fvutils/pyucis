'''
Created on Mar 13, 2020

@author: ballance
'''
from ucis.cover_data import CoverData
from ucis.source_info import SourceInfo

class CoverIndex(object):
    """Reference to a coverage item within a scope.
    
    CoverIndex provides indexed access to coverage items (bins) within their
    parent scope. Each cover item is identified by an integer index within
    its scope, starting from 0.
    
    Coverage items are the leaf nodes in the UCIS hierarchy, representing
    individual bins, branches, toggle states, or other coverage points.
    Unlike scopes which form the tree structure, cover items do not have
    children.
    
    A CoverIndex allows querying and modifying the coverage data (hit count)
    and metadata (name, source location) for a specific coverage item.
    
    Note:
        CoverIndex objects are typically obtained by iterating over a scope's
        cover items or by the index returned from createNextCover(). The index
        value is only valid within the context of its parent scope.
        
    Example:
        >>> # Iterate cover items in a coverpoint
        >>> for idx in coverpoint.coverItems():
        ...     name = idx.getName()
        ...     data = idx.getCoverData()
        ...     print(f"{name}: {data.data}/{data.goal} hits")
        ...
        >>> # Increment a specific item's count
        >>> idx.incrementCover(5)
        
    See Also:
        Scope.coverItems(): Iterate cover items in a scope
        Scope.createNextCover(): Create new cover item (returns index)
        CoverData: Coverage measurement data
        UCIS LRM Section 8.11.3 "ucis_GetCoverData"
        UCIS LRM Section 8.11.5 "ucis_IncrementCover"
    """
    
    def __init__(self):
        super().__init__()
        
    def getName(self)->str:
        """Get the name of this coverage item.
        
        Returns the name assigned when the cover item was created. Names
        are optional and may be None/empty for some coverage types.
        
        Returns:
            Name string, or None if no name was assigned.
            
        Example:
            >>> idx = coverpoint.coverItems().__next__()
            >>> name = idx.getName()
            >>> print(f"Bin name: {name}")
            
        See Also:
            Scope.createNextCover(): Set name when creating items
            UCIS LRM Section 8.11.3 "ucis_GetCoverData"
        """
        raise NotImplementedError()
    
    def getCoverData(self)->CoverData:
        """Get the coverage measurement data for this item.
        
        Retrieves the CoverData object containing hit count, goal, weight,
        and other coverage metrics for this item. The returned data reflects
        the current state and may be modified if the data structure is mutable.
        
        Returns:
            CoverData object with current coverage metrics.
            
        Example:
            >>> idx = coverpoint.coverItems().__next__()
            >>> data = idx.getCoverData()
            >>> print(f"Hits: {data.data}, Goal: {data.goal}")
            >>> covered = (data.data >= data.goal)
            
        Note:
            The returned data should be treated as a snapshot. To modify
            coverage data, use incrementCover() or scope-level methods.
            
        See Also:
            CoverData: Coverage data container
            incrementCover(): Modify hit count
            UCIS LRM Section 8.11.3 "ucis_GetCoverData"
        """
        raise NotImplementedError()
    
    def getSourceInfo(self)->SourceInfo:
        """Get source location information for this coverage item.
        
        Returns the source file location where this coverage item was defined
        or instantiated in the design. This links coverage results back to
        source code.
        
        Returns:
            SourceInfo object with file, line, and token information.
            May be None if source location was not recorded.
            
        Example:
            >>> idx = coverpoint.coverItems().__next__()
            >>> src = idx.getSourceInfo()
            >>> if src:
            ...     print(f"Defined at {src.filename}:{src.line}")
            
        See Also:
            SourceInfo: Source location data
            FileHandle: File reference system
            UCIS LRM Section 8.11.3 "ucis_GetCoverData"
        """
        raise NotImplementedError()
    
    def incrementCover(self, amt=1):
        """Increment this coverage item's hit count.
        
        Adds the specified amount to the current hit count (data field)
        of this coverage item. This is the primary method for recording
        coverage events during simulation or when merging coverage databases.
        
        Args:
            amt: Amount to add to hit count. Default is 1. Can be negative
                to decrement (though unusual). Must fit in int64_t range.
                
        Example:
            >>> # Record single hit
            >>> idx.incrementCover()
            >>>
            >>> # Record multiple hits at once
            >>> idx.incrementCover(10)
            >>>
            >>> # Verify increment
            >>> before = idx.getCoverData().data
            >>> idx.incrementCover(5)
            >>> after = idx.getCoverData().data
            >>> assert after == before + 5
            
        Note:
            Some coverage items may have a limit (HAS_LIMIT flag), causing
            counts to saturate at the limit value rather than overflow.
            
        See Also:
            getCoverData(): Query current hit count
            CoverData: Coverage data fields
            UCIS LRM Section 8.11.5 "ucis_IncrementCover"
        """
        raise NotImplementedError()
        
        
    