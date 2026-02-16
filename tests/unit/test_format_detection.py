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
Tests for format detection.
"""

import pytest
from pathlib import Path

from ucis.format_detection import (
    FormatDetector, 
    CoverageFormat, 
    detect_format,
    get_reader,
    read_coverage_file
)


# Path to test fixtures
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "cocotb_avl"


class TestFormatDetection:
    """Test suite for format detection."""
    
    def test_detector_instantiation(self):
        """Test that detector can be instantiated."""
        detector = FormatDetector()
        assert detector is not None
        assert len(detector.detectors) > 0
    
    def test_detect_cocotb_xml(self):
        """Test detection of cocotb XML format."""
        xml_file = FIXTURES_DIR / "sample_cocotb_coverage.xml"
        if not xml_file.exists():
            pytest.skip(f"Sample file not found: {xml_file}")
        
        fmt = detect_format(str(xml_file))
        assert fmt == CoverageFormat.COCOTB_XML
    
    def test_detect_cocotb_yaml(self):
        """Test detection of cocotb YAML format."""
        yaml_file = FIXTURES_DIR / "sample_cocotb_coverage.yml"
        if not yaml_file.exists():
            pytest.skip(f"Sample file not found: {yaml_file}")
        
        fmt = detect_format(str(yaml_file))
        assert fmt == CoverageFormat.COCOTB_YAML
    
    def test_detect_avl_json(self):
        """Test detection of AVL JSON format."""
        json_file = FIXTURES_DIR / "sample_avl_coverage.json"
        if not json_file.exists():
            pytest.skip(f"Sample file not found: {json_file}")
        
        fmt = detect_format(str(json_file))
        assert fmt == CoverageFormat.AVL_JSON
    
    def test_detect_unknown_format(self):
        """Test handling of unknown format."""
        # Use a Python file which shouldn't be detected
        py_file = Path(__file__)
        
        fmt = detect_format(str(py_file))
        assert fmt == CoverageFormat.UNKNOWN
    
    def test_get_reader_cocotb_xml(self):
        """Test getting reader for cocotb XML."""
        xml_file = FIXTURES_DIR / "sample_cocotb_coverage.xml"
        if not xml_file.exists():
            pytest.skip(f"Sample file not found: {xml_file}")
        
        reader = get_reader(str(xml_file))
        assert reader is not None
        assert callable(reader)
    
    def test_get_reader_cocotb_yaml(self):
        """Test getting reader for cocotb YAML."""
        yaml_file = FIXTURES_DIR / "sample_cocotb_coverage.yml"
        if not yaml_file.exists():
            pytest.skip(f"Sample file not found: {yaml_file}")
        
        reader = get_reader(str(yaml_file))
        assert reader is not None
        assert callable(reader)
    
    def test_get_reader_avl_json(self):
        """Test getting reader for AVL JSON."""
        json_file = FIXTURES_DIR / "sample_avl_coverage.json"
        if not json_file.exists():
            pytest.skip(f"Sample file not found: {json_file}")
        
        reader = get_reader(str(json_file))
        assert reader is not None
        assert callable(reader)
    
    def test_get_reader_unknown(self):
        """Test getting reader for unknown format."""
        py_file = Path(__file__)
        
        reader = get_reader(str(py_file))
        assert reader is None
    
    def test_read_coverage_file_cocotb_xml(self):
        """Test auto-read of cocotb XML file."""
        xml_file = FIXTURES_DIR / "sample_cocotb_coverage.xml"
        if not xml_file.exists():
            pytest.skip(f"Sample file not found: {xml_file}")
        
        db = read_coverage_file(str(xml_file))
        assert db is not None
    
    def test_read_coverage_file_cocotb_yaml(self):
        """Test auto-read of cocotb YAML file."""
        yaml_file = FIXTURES_DIR / "sample_cocotb_coverage.yml"
        if not yaml_file.exists():
            pytest.skip(f"Sample file not found: {yaml_file}")
        
        db = read_coverage_file(str(yaml_file))
        assert db is not None
    
    def test_read_coverage_file_avl_json(self):
        """Test auto-read of AVL JSON file."""
        json_file = FIXTURES_DIR / "sample_avl_coverage.json"
        if not json_file.exists():
            pytest.skip(f"Sample file not found: {json_file}")
        
        db = read_coverage_file(str(json_file))
        assert db is not None
    
    def test_read_coverage_file_unknown(self):
        """Test error handling for unknown format."""
        py_file = Path(__file__)
        
        with pytest.raises(ValueError):
            read_coverage_file(str(py_file))
