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
Reader for cocotb-coverage YAML format.

This module implements importing functional coverage data from cocotb-coverage
YAML files into PyUCIS database format.

cocotb-coverage YAML format is a flat dictionary with dot-separated keys:
  test.covergroup.coverpoint:
    at_least: 1
    bins:_hits:
      bin1: 10
      bin2: 5
    weight: 1
    type: <class 'cocotb_coverage.coverage.CoverPoint'>
"""

import yaml
from typing import Dict, Optional, Set
import logging

from ucis import UCIS_INSTANCE, UCIS_COVERGROUP, UCIS_COVERPOINT, UCIS_CROSS
from ucis.ucis import UCIS
from ucis.sqlite.sqlite_ucis import SqliteUCIS
from ucis.source_t import SourceT
from ucis.scope_type_t import ScopeTypeT
from ucis.flags_t import FlagsT

logger = logging.getLogger(__name__)


class CocotbYamlReader:
    """Reader for cocotb-coverage YAML format."""
    
    def __init__(self):
        self.db: Optional[UCIS] = None
        self.scope_map: Dict[str, any] = {}  # path -> scope mapping
        
    def read(self, filename: str, db: Optional[UCIS] = None) -> UCIS:
        """
        Read cocotb-coverage YAML file into UCIS database.
        
        Args:
            filename: Path to cocotb-coverage YAML file
            db: Target UCIS database (creates new SQLite in-memory if None)
            
        Returns:
            UCIS database with imported coverage
        """
        if db is None:
            db = SqliteUCIS(":memory:")
        
        self.db = db
        self.scope_map.clear()
        
        # Parse YAML file
        try:
            with open(filename, 'r') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to parse YAML file {filename}: {e}")
            raise
        
        logger.info(f"Importing cocotb-coverage from {filename}")
        
        # Process the flat dictionary
        # Strategy:
        # 1. Build hierarchy from paths
        # 2. Create coverpoints/crosses when we see 'bins:_hits'
        # 3. Create intermediate covergroups as needed
        
        # First pass: identify all paths and sort by depth
        paths = sorted(data.keys(), key=lambda x: x.count('.'))
        
        # Create root instance
        du_scope = self.db.createScope(
            name="cocotb_yaml",
            srcinfo=None,
            weight=1,
            source=SourceT.NONE,
            type=ScopeTypeT.DU_MODULE,
            flags=FlagsT(0)
        )
        root_instance = self.db.createInstance(
            name="cocotb_coverage",
            fileinfo=None,
            weight=1,
            source=SourceT.NONE,
            type=ScopeTypeT.INSTANCE,
            du_scope=du_scope,
            flags=FlagsT(0)
        )
        self.scope_map[''] = root_instance
        
        # Process paths to build hierarchy
        for path in paths:
            self._process_yaml_entry(path, data[path])
        
        logger.info(f"Successfully imported {len(self.scope_map)} coverage items")
        return db
    
    def _process_yaml_entry(self, path: str, entry: dict):
        """
        Process a single YAML entry.
        
        Args:
            path: Dot-separated path (e.g., "test.covergroup.coverpoint")
            entry: Dictionary with coverage data
        """
        # Check if this entry has bins (i.e., is a coverpoint/cross)
        has_bins = 'bins:_hits' in entry or 'bins_hits' in entry
        
        if has_bins:
            # This is a coverpoint or cross
            self._create_coverpoint_from_yaml(path, entry)
        else:
            # This is an intermediate scope (covergroup)
            self._ensure_covergroup_from_path(path, entry)
    
    def _ensure_covergroup_from_path(self, path: str, entry: dict):
        """
        Ensure covergroup exists for the given path.
        
        Args:
            path: Dot-separated path
            entry: Entry data with coverage metrics
        """
        if path in self.scope_map:
            return self.scope_map[path]
        
        # Get or create parent
        parts = path.split('.')
        parent_path = '.'.join(parts[:-1]) if len(parts) > 1 else ''
        parent_scope = self._ensure_parent_scope(parent_path)
        
        # Extract attributes
        weight = entry.get('weight', 1)
        name = parts[-1]
        
        # Create covergroup
        covergroup = parent_scope.createCovergroup(
            name=name,
            srcinfo=None,
            weight=weight,
            source=SourceT.NONE
        )
        
        self.scope_map[path] = covergroup
        logger.debug(f"Created covergroup: {path}")
        return covergroup
    
    def _create_coverpoint_from_yaml(self, path: str, entry: dict):
        """
        Create coverpoint or cross from YAML entry.
        
        Args:
            path: Dot-separated path
            entry: Entry data with bins and attributes
        """
        if path in self.scope_map:
            return  # Already created
        
        # Get parent (ensure it's a covergroup)
        parts = path.split('.')
        parent_path = '.'.join(parts[:-1]) if len(parts) > 1 else ''
        parent_scope = self._ensure_parent_scope(parent_path)
        
        # Ensure parent is covergroup
        if parent_scope.getScopeType() != ScopeTypeT.COVERGROUP:
            # Create intermediate covergroup
            parent_scope = self._ensure_covergroup_from_path(parent_path, {})
        
        # Extract attributes
        name = parts[-1]
        weight = entry.get('weight', 1)
        at_least = entry.get('at_least', 1)
        
        # Get bins
        bins_hits = entry.get('bins:_hits') or entry.get('bins_hits', {})
        
        # Determine if this is a cross (tuple-like bin names)
        is_cross = self._is_cross_from_bins(bins_hits)
        
        # Create coverpoint or cross
        if is_cross:
            coverpoint = parent_scope.createCross(
                name=name,
                srcinfo=None,
                weight=weight,
                source=SourceT.NONE,
                points_l=[]  # cocotb doesn't provide cross point references
            )
            logger.debug(f"Created cross: {path}")
        else:
            coverpoint = parent_scope.createCoverpoint(
                name=name,
                srcinfo=None,
                weight=weight,
                source=SourceT.NONE
            )
            logger.debug(f"Created coverpoint: {path}")
        
        # Create bins
        for bin_name, hits in bins_hits.items():
            self._create_bin_from_yaml(coverpoint, str(bin_name), hits, at_least)
        
        self.scope_map[path] = coverpoint
    
    def _is_cross_from_bins(self, bins_hits: dict) -> bool:
        """Determine if bins represent cross coverage (tuple-like names)."""
        if not bins_hits:
            return False
        
        # Check first few bin names
        for bin_name in list(bins_hits.keys())[:3]:
            bin_str = str(bin_name)
            if bin_str.startswith('(') and ',' in bin_str:
                return True
        return False
    
    def _create_bin_from_yaml(self, parent_scope, bin_name: str, hits: int, at_least: int):
        """
        Create a bin in the coverpoint/cross.
        
        Args:
            parent_scope: Parent coverpoint or cross
            bin_name: Bin name
            hits: Hit count
            at_least: Minimum hits required
        """
        try:
            parent_scope.createBin(
                name=bin_name,
                srcinfo=None,
                at_least=at_least,
                count=hits,
                rhs=None
            )
            logger.debug(f"Created bin '{bin_name}' with {hits} hits")
        except (AttributeError, TypeError) as e:
            logger.warning(f"Failed to create bin '{bin_name}': {e}")
    
    def _ensure_parent_scope(self, path: str):
        """
        Ensure parent scope exists, creating intermediate scopes as needed.
        
        Args:
            path: Parent path (may be empty for root)
            
        Returns:
            Parent scope
        """
        if not path:
            return self.scope_map['']  # Root instance
        
        if path in self.scope_map:
            return self.scope_map[path]
        
        # Need to create parent path
        # Recursively ensure grandparent exists
        parts = path.split('.')
        if len(parts) > 1:
            grandparent_path = '.'.join(parts[:-1])
            grandparent = self._ensure_parent_scope(grandparent_path)
        else:
            grandparent = self.scope_map['']
        
        # Create this level as covergroup
        name = parts[-1]
        scope = grandparent.createCovergroup(
            name=name,
            srcinfo=None,
            weight=1,
            source=SourceT.NONE
        )
        self.scope_map[path] = scope
        logger.debug(f"Created intermediate covergroup: {path}")
        return scope


def read_cocotb_yaml(filename: str, db: Optional[UCIS] = None) -> UCIS:
    """
    Convenience function to read cocotb-coverage YAML file.
    
    Args:
        filename: Path to YAML file
        db: Target database (creates new if None)
        
    Returns:
        UCIS database with imported coverage
    """
    reader = CocotbYamlReader()
    return reader.read(filename, db)
