'''
Created on Jan 12, 2020

@author: ballance
'''
from ucis.scope import Scope
from ucis.unimpl_error import UnimplError

from ucis.cover_instance import CoverInstance
from ucis.cover_item import CoverItem
from ucis.int_property import IntProperty


class InstanceScope(Scope):
    """Design hierarchy instance scope.
    
    InstanceScope represents a design instance in the UCIS hierarchy, typically
    corresponding to a module instance, architecture instance, program instance,
    or other instantiated design unit in the HDL source.
    
    Instances form the structural backbone of the UCIS database, mirroring the
    design hierarchy. Each instance references its design unit (DU) definition
    and contains coverage data specific to that instance.
    
    Key characteristics:
    - Scope type: INSTANCE (or specialized types like PROGRAM, PACKAGE, INTERFACE)
    - Contains code coverage items (statements, branches, conditions, etc.)
    - References a design unit (DU) scope for structural information
    - May contain child instances and coverage scopes
    
    The instance hierarchy typically follows the design's module instantiation
    tree, with the root instance representing the top-level testbench or DUT.
    
    Example:
        >>> # Create instance hierarchy
        >>> top = db.createInstance("top", None, src_info, weight=1,
        ...                         source=SourceT.SV, duName="top_module")
        >>> 
        >>> # Create child instance
        >>> child = top.createInstance("u_core", src_info, weight=1,
        ...                            source=SourceT.SV, duName="core")
        >>>
        >>> # Get design unit reference
        >>> du = child.getInstanceDu()
        >>> print(f"Design unit: {du.getName()}")
        >>>
        >>> # Access code coverage items
        >>> for i in range(child.getNumCovers()):
        ...     item = child.getIthCoverItem(i)
        ...     stmt_idx = item.getStmtIndex()
        
    See Also:
        Scope: Base scope class
        DUScope: Design unit definition
        CoverItem: Coverage items within instance
        ScopeTypeT.INSTANCE: Instance scope type
        UCIS LRM Section 6.3.1 "Instance Hierarchy"
    """
    
    def __init__(self):
        super().__init__()
        
    def getIthCoverItem(self, i)->CoverItem:
        """Get the i-th coverage item in this instance.
        
        Returns a specific coverage item (statement, branch, condition, etc.)
        by index within this instance scope.
        
        Args:
            i: Zero-based index of the coverage item (0 to numCovers-1).
            
        Returns:
            CoverItem object at the specified index.
            
        Raises:
            UnimplError: Not implemented in base class or specific backend.
            
        Example:
            >>> # Iterate all coverage items in instance
            >>> num_items = instance.getNumCovers()
            >>> for i in range(num_items):
            ...     item = instance.getIthCoverItem(i)
            ...     stmt_idx = item.getStmtIndex()
            ...     data = instance.getCoverData(i)
            ...     print(f"Statement {stmt_idx}: {data.data} hits")
            
        See Also:
            Scope.getNumCovers(): Get total number of coverage items
            CoverItem: Coverage item class
        """
        raise UnimplError()
    
    def getInstanceDu(self) -> Scope:
        """Get the design unit (DU) scope for this instance.
        
        Returns the design unit scope that defines the structural template
        for this instance. The DU scope contains the "type" information
        (module definition, architecture, etc.) while the instance contains
        the "instance-specific" coverage data.
        
        Returns:
            DUScope object representing the design unit, or None if no DU
            is associated.
            
        Raises:
            UnimplError: Not implemented in base class or specific backend.
            
        Example:
            >>> # Get design unit for an instance
            >>> du = instance.getInstanceDu()
            >>> if du:
            ...     print(f"Instance type: {du.getName()}")
            ...     sig = du.getSignature()  # Get DU signature
            
        Note:
            In VHDL designs, the DU represents the entity/architecture pair.
            In Verilog/SystemVerilog, it represents the module definition.
            
        See Also:
            DUScope: Design unit scope class
            Scope.createInstance(): Create instances with DU references
            UCIS LRM Section 6.3.4 "Design Unit Scopes"
        """
        raise UnimplError()
    
    def setIntProperty(
        self, 
        coverindex:int, 
        property:IntProperty, 
        value:int):
        if property == IntProperty.STMT_INDEX:
            ci = self.getIthCoverItem(coverindex)
            ci.setStmtIndex(value)
        else:
            super().setIntProperty(coverindex, property, value)
        
    def getIntProperty(
        self, 
        coverindex:int, 
        property:IntProperty)-> int:
        if property == IntProperty.STMT_INDEX:
            ci = self.getIthCoverItem(coverindex)
            return ci.getStmtIndex()
        else:
            return super().getIntProperty(coverindex, property)
        