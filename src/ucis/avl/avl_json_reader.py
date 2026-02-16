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
Reader for AVL (Apheleia Verification Library) JSON format.

This module implements importing functional coverage data from AVL
JSON files into PyUCIS database format.

AVL exports coverage as JSON in various formats:
1. Hierarchical format (nested dicts):
   {
     "functional_coverage": {
       "covergroups": {
         "group_name": {
           "coverpoints": {
             "point_name": {
               "bins": {"bin_name": {"hits": N}}
             }
           }
         }
       }
     }
   }

2. DataFrame format (pandas serialization)
3. Table format (index-oriented)
"""

import json
from typing import Dict, Optional, Any
import logging

from ucis.ucis import UCIS
from ucis.sqlite.sqlite_ucis import SqliteUCIS
from ucis.source_t import SourceT
from ucis.scope_type_t import ScopeTypeT
from ucis.flags_t import FlagsT

logger = logging.getLogger(__name__)


class AvlJsonReader:
    """Reader for AVL JSON coverage format."""
    
    def __init__(self):
        self.db: Optional[UCIS] = None
        self.scope_map: Dict[str, any] = {}
        
    def read(self, filename: str, db: Optional[UCIS] = None) -> UCIS:
        """
        Read AVL JSON file into UCIS database.
        
        Args:
            filename: Path to AVL JSON file
            db: Target UCIS database (creates new SQLite in-memory if None)
            
        Returns:
            UCIS database with imported coverage
        """
        if db is None:
            db = SqliteUCIS(":memory:")
        
        self.db = db
        self.scope_map.clear()
        
        # Parse JSON file
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to parse JSON file {filename}: {e}")
            raise
        
        logger.info(f"Importing AVL coverage from {filename}")
        
        # Create root instance
        du_scope = self.db.createScope(
            name="avl",
            srcinfo=None,
            weight=1,
            source=SourceT.NONE,
            type=ScopeTypeT.DU_MODULE,
            flags=FlagsT(0)
        )
        root_instance = self.db.createInstance(
            name="avl_coverage",
            fileinfo=None,
            weight=1,
            source=SourceT.NONE,
            type=ScopeTypeT.INSTANCE,
            du_scope=du_scope,
            flags=FlagsT(0)
        )
        self.scope_map['_root'] = root_instance
        
        # Detect format and process
        if self._is_hierarchical_format(data):
            self._process_hierarchical_format(data)
        elif self._is_dataframe_format(data):
            self._process_dataframe_format(data)
        else:
            logger.warning(f"Unknown AVL JSON format, attempting hierarchical parse")
            self._process_hierarchical_format(data)
        
        logger.info(f"Successfully imported {len(self.scope_map)} coverage items")
        return db
    
    def _is_hierarchical_format(self, data) -> bool:
        """Detect hierarchical format (nested covergroups/coverpoints)."""
        if not isinstance(data, dict):
            return False
        return ('functional_coverage' in data or 
                'covergroups' in data or
                any('coverpoints' in str(v) for v in data.values() if isinstance(v, dict)))
    
    def _is_dataframe_format(self, data) -> bool:
        """Detect pandas DataFrame serialization format."""
        # DataFrame formats typically have numeric keys or specific column names
        if isinstance(data, list):
            return True  # records format
        if isinstance(data, dict) and data and isinstance(next(iter(data.values()), None), dict):
            # Check if looks like DataFrame index format
            first_val = next(iter(data.values()))
            return isinstance(first_val, dict) and 'coverpoint_name' in first_val
        return False
    
    def _process_hierarchical_format(self, data: dict):
        """Process hierarchical AVL format."""
        # Navigate to coverage data
        if 'functional_coverage' in data:
            cov_data = data['functional_coverage']
        else:
            cov_data = data
        
        # Process covergroups
        covergroups = cov_data.get('covergroups', {})
        for cg_name, cg_data in covergroups.items():
            self._process_covergroup(cg_name, cg_data)
    
    def _process_covergroup(self, name: str, data: dict):
        """Process a covergroup."""
        # Create covergroup under root
        root = self.scope_map['_root']
        
        covergroup = root.createCovergroup(
            name=name,
            srcinfo=None,
            weight=1,
            source=SourceT.NONE
        )
        self.scope_map[name] = covergroup
        logger.debug(f"Created covergroup: {name}")
        
        # Process coverpoints
        coverpoints = data.get('coverpoints', {})
        for cp_name, cp_data in coverpoints.items():
            self._process_coverpoint(covergroup, cp_name, cp_data)
        
        # Process crosses if any
        crosses = data.get('crosses', {})
        for cross_name, cross_data in crosses.items():
            self._process_cross(covergroup, cross_name, cross_data)
    
    def _process_coverpoint(self, parent, name: str, data: dict):
        """Process a coverpoint."""
        # Create coverpoint
        coverpoint = parent.createCoverpoint(
            name=name,
            srcinfo=None,
            weight=1,
            source=SourceT.NONE
        )
        logger.debug(f"Created coverpoint: {name}")
        
        # Process bins
        bins = data.get('bins', {})
        for bin_name, bin_data in bins.items():
            hits = bin_data.get('hits', 0) if isinstance(bin_data, dict) else bin_data
            self._create_bin(coverpoint, bin_name, hits)
    
    def _process_cross(self, parent, name: str, data: dict):
        """Process a cross coverage item."""
        # Create cross
        cross = parent.createCross(
            name=name,
            srcinfo=None,
            weight=1,
            source=SourceT.NONE,
            points_l=[]  # AVL doesn't provide cross point references in this format
        )
        logger.debug(f"Created cross: {name}")
        
        # Process cross bins
        bins = data.get('bins', {})
        for bin_name, bin_data in bins.items():
            hits = bin_data.get('hits', 0) if isinstance(bin_data, dict) else bin_data
            self._create_bin(cross, bin_name, hits)
    
    def _create_bin(self, parent_scope, bin_name: str, hits: int, at_least: int = 1):
        """Create a bin in the coverpoint/cross."""
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
    
    def _process_dataframe_format(self, data):
        """Process pandas DataFrame serialization format."""
        logger.info("Processing DataFrame format")
        
        # Create a default covergroup
        root = self.scope_map['_root']
        covergroup = root.createCovergroup(
            name="dataframe_coverage",
            srcinfo=None,
            weight=1,
            source=SourceT.NONE
        )
        
        # Handle records format (list of dicts)
        if isinstance(data, list):
            self._process_dataframe_records(covergroup, data)
        # Handle index/table format (dict of dicts)
        elif isinstance(data, dict):
            self._process_dataframe_table(covergroup, data)
    
    def _process_dataframe_records(self, parent, records: list):
        """Process DataFrame records format."""
        # Group by coverpoint name
        coverpoints = {}
        for record in records:
            cp_name = record.get('coverpoint_name', 'unknown')
            if cp_name not in coverpoints:
                coverpoints[cp_name] = []
            coverpoints[cp_name].append(record)
        
        # Create coverpoints and bins
        for cp_name, bins in coverpoints.items():
            # Extract base coverpoint name (before '.')
            base_name = cp_name.split('.')[0] if '.' in cp_name else cp_name
            
            if base_name not in self.scope_map:
                coverpoint = parent.createCoverpoint(
                    name=base_name,
                    srcinfo=None,
                    weight=1,
                    source=SourceT.NONE
                )
                self.scope_map[base_name] = coverpoint
            else:
                coverpoint = self.scope_map[base_name]
            
            # Create bins
            for bin_record in bins:
                bin_name = bin_record.get('bin_name', 'unknown')
                hits = bin_record.get('hits', 0)
                self._create_bin(coverpoint, bin_name, hits)
    
    def _process_dataframe_table(self, parent, table: dict):
        """Process DataFrame table/index format."""
        # Similar logic to records but with different structure
        for idx, record in table.items():
            cp_name = record.get('coverpoint_name', f'coverpoint_{idx}')
            base_name = cp_name.split('.')[0] if '.' in cp_name else cp_name
            
            if base_name not in self.scope_map:
                coverpoint = parent.createCoverpoint(
                    name=base_name,
                    srcinfo=None,
                    weight=1,
                    source=SourceT.NONE
                )
                self.scope_map[base_name] = coverpoint
            else:
                coverpoint = self.scope_map[base_name]
            
            bin_name = record.get('bin_name', f'bin_{idx}')
            hits = record.get('hits', 0)
            self._create_bin(coverpoint, bin_name, hits)


def read_avl_json(filename: str, db: Optional[UCIS] = None) -> UCIS:
    """
    Convenience function to read AVL JSON file.
    
    Args:
        filename: Path to JSON file
        db: Target database (creates new if None)
        
    Returns:
        UCIS database with imported coverage
    """
    reader = AvlJsonReader()
    return reader.read(filename, db)
