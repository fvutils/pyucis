
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

'''
Created on Jan 8, 2020

@author: ballance
'''
from ucis.unimpl_error import UnimplError
from ucis.int_property import IntProperty
from ucis.real_property import RealProperty
from ucis.str_property import StrProperty
from ucis.handle_property import HandleProperty

class Obj():
    """Base class for all UCIS objects.
    
    The Obj class provides the foundation for all objects in the UCIS data model,
    including scopes, cover items, and history nodes. It implements a property-based
    interface for accessing and modifying object attributes through type-specific
    getter and setter methods.
    
    Properties in UCIS are accessed by enumerated property identifiers (IntProperty,
    RealProperty, StrProperty, HandleProperty) and may be associated with either the
    object itself (when coverindex < 0) or with a specific cover item within a scope
    (when coverindex >= 0).
    
    This class serves as an abstract base class and is typically extended by concrete
    implementations such as Scope, CoverItem, and HistoryNode.
    
    Note:
        The property interface provides a uniform way to access diverse object attributes
        without requiring separate methods for each property. Properties are defined by
        the UCIS standard and enable tool-independent data access.
        
    See Also:
        UCIS LRM Section 8.3 "Database Property Functions"
        UCIS LRM Section 8.4 "User-defined Attribute Functions"
    """
    
    def __init__(self):
        pass
    
    def getIntProperty(
            self, 
            coverindex : int,
            property : IntProperty
            )->int:
        """Get an integer property value from this object.
        
        Retrieves integer-valued properties such as weights, goals, counts, flags,
        and other numeric attributes. Properties can apply to the object as a whole
        (scope-level) or to a specific cover item within the object.
        
        Args:
            coverindex: Index of cover item within parent scope. Use -1 to apply
                the property to the scope itself rather than a specific cover item.
            property: Integer property identifier from the IntProperty enumeration,
                such as SCOPE_WEIGHT, SCOPE_GOAL, COVER_GOAL, NUM_TESTS, etc.
                
        Returns:
            The integer value of the requested property.
            
        Raises:
            UnimplError: If the property is not implemented for this object type.
            ValueError: If the property is not applicable to this object type.
            
        Example:
            >>> # Get the weight of a scope
            >>> weight = scope.getIntProperty(-1, IntProperty.SCOPE_WEIGHT)
            >>> # Get the goal of a specific cover item
            >>> goal = scope.getIntProperty(0, IntProperty.COVER_GOAL)
            
        Note:
            If the return value would naturally be -1, this method returns -1 without
            raising an error. Error handlers are only invoked for true error conditions.
            
        See Also:
            setIntProperty(): Set integer property values
            UCIS LRM Section 8.3.5 "ucis_GetIntProperty"
        """
        raise UnimplError()
    
    def setIntProperty(
            self,
            coverindex : int,
            property : IntProperty,
            value : int):
        """Set an integer property value on this object.
        
        Modifies integer-valued properties such as weights, goals, and flags.
        Properties can be set on the object as a whole or on a specific cover item.
        
        Args:
            coverindex: Index of cover item within parent scope. Use -1 to apply
                the property to the scope itself rather than a specific cover item.
            property: Integer property identifier from the IntProperty enumeration,
                such as SCOPE_WEIGHT, SCOPE_GOAL, COVER_GOAL, etc.
            value: New integer value for the property.
                
        Raises:
            UnimplError: If the property is not implemented for this object type.
            ValueError: If the property is not applicable or read-only.
            
        Example:
            >>> # Set the weight of a scope
            >>> scope.setIntProperty(-1, IntProperty.SCOPE_WEIGHT, 10)
            >>> # Set the goal of a specific cover item  
            >>> scope.setIntProperty(0, IntProperty.COVER_GOAL, 100)
            
        Note:
            Some properties are read-only (e.g., NUM_TESTS, SCOPE_NUM_COVERITEMS)
            and cannot be set. Attempting to set a read-only property will raise
            an error.
            
        See Also:
            getIntProperty(): Get integer property values
            UCIS LRM Section 8.3.6 "ucis_SetIntProperty"
        """
        raise UnimplError()

    def getRealProperty(
            self,
            coverindex : int,
            property : RealProperty) -> float:
        """Get a floating-point property value from this object.
        
        Retrieves real-valued (floating-point) properties such as coverage percentages,
        thresholds, and other numeric attributes that require fractional precision.
        
        Args:
            coverindex: Index of cover item within parent scope. Use -1 to apply
                the property to the scope itself rather than a specific cover item.
            property: Real property identifier from the RealProperty enumeration.
                
        Returns:
            The floating-point value of the requested property.
            
        Raises:
            UnimplError: If the property is not implemented for this object type.
            ValueError: If the property is not applicable to this object type.
            
        Example:
            >>> # Get coverage percentage
            >>> pct = scope.getRealProperty(-1, RealProperty.COVERAGE_PCT)
            
        See Also:
            setRealProperty(): Set real property values
            UCIS LRM Section 8.3.7 "ucis_GetRealProperty"
        """
        raise UnimplError()
        
    def setRealProperty(
            self,
            coverindex : int,
            property : RealProperty,
            value : float):
        """Set a floating-point property value on this object.
        
        Modifies real-valued (floating-point) properties such as coverage percentages
        and thresholds.
        
        Args:
            coverindex: Index of cover item within parent scope. Use -1 to apply
                the property to the scope itself rather than a specific cover item.
            property: Real property identifier from the RealProperty enumeration.
            value: New floating-point value for the property.
                
        Raises:
            UnimplError: If the property is not implemented for this object type.
            ValueError: If the property is not applicable or read-only.
            
        Example:
            >>> # Set a threshold value
            >>> scope.setRealProperty(-1, RealProperty.THRESHOLD, 95.0)
            
        See Also:
            getRealProperty(): Get real property values
            UCIS LRM Section 8.3.8 "ucis_SetRealProperty"
        """
        raise UnimplError()

    def getStringProperty(
            self,
            coverindex : int,
            property : StrProperty) -> str:
        """Get a string property value from this object.
        
        Retrieves string-valued properties such as names, comments, file paths,
        and other textual attributes.
        
        Args:
            coverindex: Index of cover item within parent scope. Use -1 to apply
                the property to the scope itself rather than a specific cover item.
            property: String property identifier from the StrProperty enumeration,
                such as NAME, COMMENT, FILE_NAME, etc.
                
        Returns:
            The string value of the requested property.
            
        Raises:
            UnimplError: If the property is not implemented for this object type.
            ValueError: If the property is not applicable to this object type.
            
        Example:
            >>> # Get the name of a scope
            >>> name = scope.getStringProperty(-1, StrProperty.NAME)
            >>> # Get a comment on a cover item
            >>> comment = scope.getStringProperty(0, StrProperty.COMMENT)
            
        See Also:
            setStringProperty(): Set string property values
            UCIS LRM Section 8.3.9 "ucis_GetStringProperty"
        """
        raise UnimplError()
    
    def setStringProperty(
            self,
            coverindex : int,
            property : StrProperty,
            value : str):
        """Set a string property value on this object.
        
        Modifies string-valued properties such as names, comments, and other
        textual attributes.
        
        Args:
            coverindex: Index of cover item within parent scope. Use -1 to apply
                the property to the scope itself rather than a specific cover item.
            property: String property identifier from the StrProperty enumeration,
                such as NAME, COMMENT, etc.
            value: New string value for the property.
                
        Raises:
            UnimplError: If the property is not implemented for this object type.
            ValueError: If the property is not applicable or read-only.
            
        Example:
            >>> # Set a comment on a scope
            >>> scope.setStringProperty(-1, StrProperty.COMMENT, "Main test scope")
            >>> # Set a comment on a specific cover item
            >>> scope.setStringProperty(0, StrProperty.COMMENT, "Edge case")
            
        Note:
            Some string properties like NAME may be read-only after object creation
            to maintain data model consistency.
            
        See Also:
            getStringProperty(): Get string property values
            UCIS LRM Section 8.3.10 "ucis_SetStringProperty"
        """
        raise UnimplError()
        
    def getHandleProperty(
            self,
            coverindex : int,
            property : HandleProperty) -> 'Scope':
        """Get an object reference (handle) property from this object.
        
        Retrieves properties that reference other UCIS objects, such as parent
        scopes, design unit references, or related objects in the coverage hierarchy.
        
        Args:
            coverindex: Index of cover item within parent scope. Use -1 to apply
                the property to the scope itself rather than a specific cover item.
            property: Handle property identifier from the HandleProperty enumeration,
                such as PARENT, DU_SCOPE, etc.
                
        Returns:
            Reference to the related UCIS object (typically a Scope subclass).
            
        Raises:
            UnimplError: If the property is not implemented for this object type.
            ValueError: If the property is not applicable to this object type.
            
        Example:
            >>> # Get the parent scope
            >>> parent = scope.getHandleProperty(-1, HandleProperty.PARENT)
            >>> # Get the design unit scope for an instance
            >>> du = instance.getHandleProperty(-1, HandleProperty.DU_SCOPE)
            
        See Also:
            setHandleProperty(): Set object reference properties
            UCIS LRM Section 8.3.11 "ucis_GetHandleProperty"
        """
        raise UnimplError()
    
    def setHandleProperty(
            self,
            coverindex : int,
            property : HandleProperty,
            value : 'Scope'):
        """Set an object reference (handle) property on this object.
        
        Modifies properties that reference other UCIS objects in the coverage
        hierarchy, establishing relationships between objects.
        
        Args:
            coverindex: Index of cover item within parent scope. Use -1 to apply
                the property to the scope itself rather than a specific cover item.
            property: Handle property identifier from the HandleProperty enumeration.
            value: Reference to the UCIS object to associate with this property.
                
        Raises:
            UnimplError: If the property is not implemented for this object type.
            ValueError: If the property is not applicable or read-only.
            TypeError: If the value is not a compatible object type.
            
        Example:
            >>> # Associate a design unit with an instance
            >>> instance.setHandleProperty(-1, HandleProperty.DU_SCOPE, du)
            
        Note:
            Most handle properties are set during object creation and may be
            read-only afterward to maintain hierarchy consistency.
            
        See Also:
            getHandleProperty(): Get object reference properties
            UCIS LRM Section 8.3.12 "ucis_SetHandleProperty"
        """
        raise UnimplError()
    
    def accept(self, v):
        """Accept a visitor for traversing the UCIS object hierarchy.
        
        Implements the Visitor design pattern, allowing external traversal and
        processing of the UCIS object tree without modifying the object classes.
        Visitors can implement operations like reporting, merging, filtering, or
        custom analysis.
        
        Args:
            v: Visitor object implementing the appropriate visit methods for
                each object type (visitScope, visitCoverItem, etc.).
                
        Raises:
            UnimplError: If the visitor pattern is not implemented.
            
        Example:
            >>> class MyVisitor:
            ...     def visitScope(self, scope):
            ...         print(f"Visiting scope: {scope.getName()}")
            ...
            >>> visitor = MyVisitor()
            >>> scope.accept(visitor)
            
        Note:
            The visitor pattern enables separation of algorithms from the object
            structure they operate on, facilitating extensibility without modifying
            core classes.
            
        See Also:
            Visitor design pattern documentation
        """
        raise UnimplError()
        
