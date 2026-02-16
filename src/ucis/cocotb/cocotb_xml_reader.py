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

"""
Reader for cocotb-coverage XML format.

This module implements importing functional coverage data from cocotb-coverage
XML files into PyUCIS database format.
"""

from lxml import etree
from typing import Dict, Optional
import logging

from ucis import (
    UCIS_INSTANCE, UCIS_COVERGROUP, UCIS_COVERPOINT, UCIS_CROSS,
    UCIS_CVGBIN, UCIS_IGNOREBIN
)
from ucis.ucis import UCIS
from ucis.sqlite.sqlite_ucis import SqliteUCIS
from ucis.source_info import SourceInfo
from ucis.source_t import SourceT
from ucis.scope_type_t import ScopeTypeT
from ucis.flags_t import FlagsT

logger = logging.getLogger(__name__)


class CocotbXmlReader:
    """Reader for cocotb-coverage XML format."""
    
    def __init__(self):
        self.db: Optional[UCIS] = None
        self.scope_map: Dict[str, any] = {}  # abs_name -> scope mapping
        
    def read(self, filename: str, db: Optional[UCIS] = None) -> UCIS:
        """
        Read cocotb-coverage XML file into UCIS database.
        
        Args:
            filename: Path to cocotb-coverage XML file
            db: Target UCIS database (creates new SQLite in-memory if None)
            
        Returns:
            UCIS database with imported coverage
        """
        if db is None:
            db = SqliteUCIS(":memory:")
        
        self.db = db
        self.scope_map.clear()
        
        # Parse XML file
        try:
            tree = etree.parse(filename)
            root = tree.getroot()
        except Exception as e:
            logger.error(f"Failed to parse XML file {filename}: {e}")
            raise
        
        # Process coverage tree starting from root
        logger.info(f"Importing cocotb-coverage from {filename}")
        self._process_coverage_element(root, None, is_root=True)
        
        logger.info(f"Successfully imported {len(self.scope_map)} coverage items")
        return db
    
    def _process_coverage_element(self, elem, parent_scope, is_root=False):
        """
        Process a coverage element and its children recursively.
        
        Args:
            elem: XML element to process
            parent_scope: Parent UCIS scope (None for root)
            is_root: True if this is the root element
        """
        tag_name = elem.tag
        abs_name = elem.get('abs_name', tag_name)
        
        # Extract coverage metrics
        size = int(elem.get('size', '0'))
        coverage = int(elem.get('coverage', '0'))
        cover_percentage = float(elem.get('cover_percentage', '0.0'))
        
        # Extract coverpoint/cross specific attributes
        weight = int(elem.get('weight', '1'))
        at_least = int(elem.get('at_least', '1'))
        
        logger.debug(f"Processing {tag_name}: {abs_name} (coverage: {cover_percentage}%)")
        
        # Determine scope type and create scope
        current_scope = None
        
        if is_root:
            # Root element - create design unit and instance
            # Create a simple DU scope first
            du_scope = self.db.createScope(
                name=tag_name,
                srcinfo=None,
                weight=1,
                source=SourceT.NONE,
                type=ScopeTypeT.DU_MODULE,
                flags=FlagsT(0)
            )
            # Now create instance under it
            current_scope = self.db.createInstance(
                name="cocotb_coverage",
                fileinfo=None,
                weight=weight,
                source=SourceT.NONE,
                type=ScopeTypeT.INSTANCE,
                du_scope=du_scope,
                flags=FlagsT(0)
            )
            self.scope_map[abs_name] = current_scope
            
        elif self._is_bin_element(elem):
            # This is a bin element - handle separately
            self._create_bin(elem, parent_scope, at_least)
            return  # Don't process children of bins
            
        else:
            # Regular coverage element
            current_scope = self._create_scope_from_element(
                elem, parent_scope, tag_name, abs_name, weight, at_least
            )
        
        # Process child elements recursively
        for child in elem:
            self._process_coverage_element(child, current_scope, is_root=False)
    
    def _is_bin_element(self, elem) -> bool:
        """Check if element is a bin element."""
        # Bin elements have 'bin' attribute and 'hits' attribute
        return elem.get('bin') is not None and elem.get('hits') is not None
    
    def _create_scope_from_element(self, elem, parent_scope, tag_name, abs_name, weight, at_least):
        """
        Create appropriate UCIS scope based on element characteristics.
        
        Returns created scope.
        """
        if parent_scope is None:
            # Shouldn't happen, but handle gracefully
            logger.warning(f"No parent scope for {abs_name}, creating instance")
            scope = parent_scope.createScope(
                name=tag_name,
                srcinfo=None,
                weight=weight,
                source=SourceT.NONE,
                type=ScopeTypeT.INSTANCE,
                flags=FlagsT(0)
            )
            self.scope_map[abs_name] = scope
            return scope
        
        # Determine if this should be a covergroup or coverpoint
        # Heuristic: elements with bin children are coverpoints/crosses
        has_bin_children = any(self._is_bin_element(child) for child in elem)
        
        if has_bin_children:
            # This is a coverpoint or cross
            # Check if parent is a covergroup, if not create one
            if parent_scope. getScopeType() != UCIS_COVERGROUP:
                # Need to ensure parent is a covergroup
                # For simplicity, treat intermediate scopes as covergroups
                parent_scope = self._ensure_covergroup_parent(parent_scope, abs_name)
            
            # Determine if cross or coverpoint based on name or children
            # cocotb uses specific naming, we'll detect crosses by checking bin format
            is_cross = self._looks_like_cross(elem)
            
            if is_cross:
                # For crosses, we need to create it properly
                # cocotb doesn't store cross point references, so we'll create empty list
                scope = parent_scope.createCross(
                    name=tag_name,
                    srcinfo=None,
                    weight=weight,
                    source=SourceT.NONE,
                    points_l=[]  # cocotb doesn't provide this info
                )
            else:
                scope = parent_scope.createCoverpoint(
                    name=tag_name,
                    srcinfo=None,
                    weight=weight,
                    source=SourceT.NONE
                )
        else:
            # Intermediate scope - treat as covergroup
            scope = parent_scope.createCovergroup(
                name=tag_name,
                srcinfo=None,
                weight=weight,
                source=SourceT.NONE
            )
        
        self.scope_map[abs_name] = scope
        return scope
    
    def _looks_like_cross(self, elem) -> bool:
        """
        Determine if element represents cross coverage.
        
        Cross bins typically have tuple-like bin names: "('addr_0', 0)"
        """
        for child in elem:
            if self._is_bin_element(child):
                bin_name = child.get('bin', '')
                # Check for tuple-like structure
                if bin_name.startswith('(') and ',' in bin_name:
                    return True
        return False
    
    def _ensure_covergroup_parent(self, scope, abs_name):
        """
        Ensure scope has a covergroup parent.
        
        If scope is not a covergroup, create a covergroup wrapper.
        """
        if scope. getScopeType() == UCIS_COVERGROUP:
            return scope
        
        # Get or create a covergroup as child of current scope
        # Extract covergroup name from abs_name
        parts = abs_name.split('.')
        if len(parts) > 1:
            cg_name = parts[-2]  # Use parent name
        else:
            cg_name = "covergroup"
        
        # Check if covergroup already exists
        for child in scope.getScopes():
            if child.getName() == cg_name and child. getScopeType() == UCIS_COVERGROUP:
                return child
        
        # Create new covergroup
        covergroup = scope.createScope(
            name=cg_name,
            srcinfo=None,
            weight=1,
            source=SourceT.NONE,
            type=ScopeTypeT.COVERGROUP,
            flags=FlagsT(0)
        )
        return covergroup
    
    def _create_covergroup(self, parent_scope, name, weight):
        """Create a covergroup scope."""
        return parent_scope.createScope(
            name=name,
            srcinfo=None,
            weight=weight,
            source=SourceT.NONE,
            type=ScopeTypeT.COVERGROUP,
            flags=FlagsT(0)
        )
    
    def _create_bin(self, elem, parent_scope, at_least):
        """
        Create a bin in the parent coverpoint/cross.
        
        Args:
            elem: Bin XML element
            parent_scope: Parent coverpoint or cross scope
            at_least: Minimum hits required
        """
        bin_name = elem.get('bin', 'unnamed_bin')
        hits = int(elem.get('hits', '0'))
        
        logger.debug(f"Creating bin '{bin_name}' with {hits} hits (at_least={at_least})")
        
        # Create bin using createBin method
        try:
            bin_scope = parent_scope.createBin(
                name=bin_name,
                srcinfo=None,
                at_least=at_least,
                count=hits,
                rhs=None  # cocotb doesn't use range expressions
            )
            
        except (AttributeError, TypeError) as e:
            logger.warning(f"Failed to create bin '{bin_name}': {e}")
            # Fallback: try generic approach
            try:
                bin_scope = parent_scope.createScope(
                    name=bin_name,
                    srcinfo=None,
                    weight=1,
                    source=SourceT.NONE,
                    type=ScopeTypeT.CVGBIN,
                    flags=FlagsT(0)
                )
            except Exception as e2:
                logger.error(f"Failed to create bin scope '{bin_name}': {e2}")


def read_cocotb_xml(filename: str, db: Optional[UCIS] = None) -> UCIS:
    """
    Convenience function to read cocotb-coverage XML file.
    
    Args:
        filename: Path to XML file
        db: Target database (creates new if None)
        
    Returns:
        UCIS database with imported coverage
    """
    reader = CocotbXmlReader()
    return reader.read(filename, db)
