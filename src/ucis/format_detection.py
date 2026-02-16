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
Format detection for coverage import.

This module provides automatic detection of coverage file formats
including cocotb-coverage (XML/YAML) and AVL (JSON).
"""

import json
import logging
from pathlib import Path
from typing import Optional, Callable
from enum import Enum

try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    HAS_LXML = False

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

logger = logging.getLogger(__name__)


class CoverageFormat(Enum):
    """Supported coverage file formats."""
    COCOTB_XML = "cocotb_xml"
    COCOTB_YAML = "cocotb_yaml"
    AVL_JSON = "avl_json"
    UNKNOWN = "unknown"


class FormatDetector:
    """Automatic coverage format detection."""
    
    def __init__(self):
        self.detectors = [
            self._detect_cocotb_xml,
            self._detect_cocotb_yaml,
            self._detect_avl_json,
        ]
    
    def detect(self, filename: str) -> CoverageFormat:
        """
        Detect the format of a coverage file.
        
        Args:
            filename: Path to coverage file
            
        Returns:
            Detected format or UNKNOWN
        """
        path = Path(filename)
        
        if not path.exists():
            logger.error(f"File not found: {filename}")
            return CoverageFormat.UNKNOWN
        
        # Try each detector
        for detector in self.detectors:
            try:
                fmt = detector(path)
                if fmt != CoverageFormat.UNKNOWN:
                    logger.info(f"Detected format: {fmt.value}")
                    return fmt
            except Exception as e:
                logger.debug(f"Detector {detector.__name__} failed: {e}")
                continue
        
        logger.warning(f"Could not detect format for: {filename}")
        return CoverageFormat.UNKNOWN
    
    def _detect_cocotb_xml(self, path: Path) -> CoverageFormat:
        """Detect cocotb-coverage XML format."""
        if not HAS_LXML:
            return CoverageFormat.UNKNOWN
        
        # Check file extension
        if path.suffix.lower() not in ['.xml', '.cov']:
            return CoverageFormat.UNKNOWN
        
        # Try to parse as XML
        try:
            tree = etree.parse(str(path))
            root = tree.getroot()
            
            # Check for cocotb-coverage XML structure
            # cocotb uses abs_name and cover_percentage attributes
            if root.get('abs_name') is not None and root.get('cover_percentage') is not None:
                return CoverageFormat.COCOTB_XML
            
            # Also check child elements
            for elem in root.iter():
                if elem.get('abs_name') is not None and elem.get('cover_percentage') is not None:
                    return CoverageFormat.COCOTB_XML
        except Exception as e:
            logger.debug(f"XML parsing failed: {e}")
        
        return CoverageFormat.UNKNOWN
    
    def _detect_cocotb_yaml(self, path: Path) -> CoverageFormat:
        """Detect cocotb-coverage YAML format."""
        if not HAS_YAML:
            return CoverageFormat.UNKNOWN
        
        # Check file extension
        if path.suffix.lower() not in ['.yml', '.yaml']:
            return CoverageFormat.UNKNOWN
        
        # Try to parse as YAML
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
            
            if not isinstance(data, dict):
                return CoverageFormat.UNKNOWN
            
            # Check for cocotb-coverage YAML structure
            # Look for dot-separated keys and bins:_hits pattern
            for key, value in data.items():
                if isinstance(value, dict):
                    # Check for cocotb-specific keys
                    if 'bins:_hits' in value:
                        return CoverageFormat.COCOTB_YAML
                    if 'cover_percentage' in value and 'at_least' in value:
                        return CoverageFormat.COCOTB_YAML
        except Exception as e:
            logger.debug(f"YAML parsing failed: {e}")
        
        return CoverageFormat.UNKNOWN
    
    def _detect_avl_json(self, path: Path) -> CoverageFormat:
        """Detect AVL JSON format."""
        # Check file extension
        if path.suffix.lower() != '.json':
            return CoverageFormat.UNKNOWN
        
        # Try to parse as JSON
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            # Check for AVL JSON structure
            if isinstance(data, dict):
                # Check for AVL metadata (highest priority)
                if 'metadata' in data:
                    metadata = data['metadata']
                    if isinstance(metadata, dict) and metadata.get('generator') == 'AVL':
                        return CoverageFormat.AVL_JSON
                
                # Check for hierarchical coverage structure
                if 'functional_coverage' in data:
                    cov = data['functional_coverage']
                    if isinstance(cov, dict) and 'covergroups' in cov:
                        return CoverageFormat.AVL_JSON
                
                # Check for DataFrame table format (dict with numeric keys)
                if data:
                    first_val = next(iter(data.values()))
                    if isinstance(first_val, dict):
                        # If it has coverage-related fields, it's AVL DataFrame format
                        if 'coverpoint_name' in first_val or 'bin_name' in first_val:
                            return CoverageFormat.AVL_JSON
            
            # Check for DataFrame format (list of records)
            elif isinstance(data, list) and len(data) > 0:
                # Check if records have coverage-related fields
                first = data[0]
                if isinstance(first, dict):
                    if 'coverpoint_name' in first or 'bin_name' in first:
                        return CoverageFormat.AVL_JSON
        except Exception as e:
            logger.debug(f"JSON parsing failed: {e}")
        
        return CoverageFormat.UNKNOWN


def detect_format(filename: str) -> CoverageFormat:
    """
    Convenience function to detect coverage file format.
    
    Args:
        filename: Path to coverage file
        
    Returns:
        Detected format
    """
    detector = FormatDetector()
    return detector.detect(filename)


def get_reader(filename: str) -> Optional[Callable]:
    """
    Get appropriate reader function for a coverage file.
    
    Args:
        filename: Path to coverage file
        
    Returns:
        Reader function or None if format unknown
    """
    fmt = detect_format(filename)
    
    if fmt == CoverageFormat.COCOTB_XML:
        from ucis.cocotb.cocotb_xml_reader import read_cocotb_xml
        return read_cocotb_xml
    elif fmt == CoverageFormat.COCOTB_YAML:
        from ucis.cocotb.cocotb_yaml_reader import read_cocotb_yaml
        return read_cocotb_yaml
    elif fmt == CoverageFormat.AVL_JSON:
        from ucis.avl.avl_json_reader import read_avl_json
        return read_avl_json
    else:
        logger.error(f"Unknown format for: {filename}")
        return None


def read_coverage_file(filename: str, db=None):
    """
    Auto-detect and read a coverage file.
    
    Args:
        filename: Path to coverage file
        db: Target UCIS database (creates new if None)
        
    Returns:
        UCIS database with imported coverage
        
    Raises:
        ValueError: If format cannot be detected
    """
    reader = get_reader(filename)
    if reader is None:
        raise ValueError(f"Could not detect format for: {filename}")
    
    return reader(filename, db)
