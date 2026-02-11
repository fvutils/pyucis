'''
Created on Jan 12, 2020

@author: ballance
'''
from ucis.scope import Scope
from ucis.unimpl_error import UnimplError
from ucis.str_property import StrProperty


class DUScope(Scope):
    """Design unit (DU) definition scope.
    
    DUScope represents a design unit definition in the UCIS hierarchy. Design
    units are the "types" or templates that instances instantiate. They contain
    structural information about the design unit but no instance-specific data.
    
    Design unit types include:
    - **DU_MODULE**: Verilog/SystemVerilog module definition
    - **DU_ARCH**: VHDL architecture definition
    - **DU_PACKAGE**: HDL package definition
    - **DU_PROGRAM**: SystemVerilog program definition
    - **DU_INTERFACE**: SystemVerilog interface definition
    
    A DU scope stores:
    - Structural hierarchy of the design unit
    - Statement/branch/condition definitions
    - Signature for unique identification
    
    The signature uniquely identifies the DU definition, allowing tools to
    match instances to their design units across different test runs or
    compilations.
    
    Example:
        >>> # Design units are typically created automatically by tools
        >>> # Access DU from an instance
        >>> du = instance.getInstanceDu()
        >>> print(f"Design unit: {du.getName()}")
        >>>
        >>> # Get/set DU signature
        >>> sig = du.getSignature()
        >>> du.setSignature("module:core:v1.0:checksum_abc123")
        >>>
        >>> # Query design unit type
        >>> du_type = du.getType()  # Returns ScopeTypeT.DU_MODULE, etc.
        
    Note:
        Design units are typically created by EDA tools during elaboration or
        compilation. User code usually accesses them via instance references
        rather than creating them directly.
        
    See Also:
        InstanceScope: Instance referencing this DU
        ScopeTypeT.DU_MODULE: Module design unit type
        ScopeTypeT.DU_ARCH: Architecture design unit type
        StrProperty.DU_SIGNATURE: Signature property
        UCIS LRM Section 6.3.4 "Design Unit Scopes"
    """
    
    def __init__(self):
        super().__init__()
        
    def getSignature(self):
        """Get the signature identifying this design unit.
        
        Returns a signature string that uniquely identifies this design unit
        definition. Signatures enable tools to match instances to design units
        across different simulations and database merges.
        
        The signature format is tool-specific but typically includes the
        design unit name, version, and/or checksum of the source code.
        
        Returns:
            Signature string, or None if not set.
            
        Raises:
            UnimplError: Not implemented in base class or specific backend.
            
        Example:
            >>> sig = du.getSignature()
            >>> print(f"DU signature: {sig}")
            >>>
            >>> # Signatures help match instances across runs
            >>> if du.getSignature() == expected_sig:
            ...     print("Design unit matches expected version")
            
        See Also:
            setSignature(): Set the signature
            StrProperty.DU_SIGNATURE: Underlying property
        """
        raise UnimplError()
    
    def setSignature(self, sig):
        """Set the signature identifying this design unit.
        
        Sets a signature string that uniquely identifies this design unit.
        Tools use signatures to ensure instances refer to the correct DU
        version when merging databases or reloading data.
        
        Args:
            sig: Signature string. Format is tool-specific but should uniquely
                identify the DU definition.
                
        Raises:
            UnimplError: Not implemented in base class or specific backend.
            
        Example:
            >>> # Set signature with module name and checksum
            >>> du.setSignature("module:my_core:v2.1:md5_abc123def456")
            >>>
            >>> # Or use file path and timestamp
            >>> du.setSignature("file:rtl/core.sv:2024-01-15T10:30:00")
            
        See Also:
            getSignature(): Query the signature
        """
        raise UnimplError()
    
    def getStringProperty(
            self,
            coverindex : int,
            property : StrProperty) -> str:
        if property == StrProperty.DU_SIGNATURE:
            return self.getSignature()
        else:
            return super().getStringProperty(coverindex, property)
    
    def setStringProperty(
            self,
            coverindex : int,
            property : StrProperty,
            value : str):
        if property == StrProperty.DU_SIGNATURE:
            self.setSignature(value)
        else:
            self.setStringProperty(coverindex, property, value)
        
    def accept(self, v):
        v.visit_du_scope(self)
        