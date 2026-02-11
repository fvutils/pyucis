"""
Pytest configuration and fixtures for UCIS API backend tests.

Provides parametrized fixtures for testing across multiple backends:
- backend: Full-featured backends (Memory, XML, SQLite)
- yaml_backend: Simplified YAML backend (limited feature set)
"""

import pytest
import tempfile
import os
from pathlib import Path

from ucis.mem.mem_factory import MemFactory
from ucis.xml.xml_factory import XmlFactory
from ucis.sqlite.sqlite_ucis import SqliteUCIS
from ucis.scope_type_t import ScopeTypeT

# Backend configuration
FULL_BACKENDS = [
    ("memory", "mem"),
    ("xml", "xml"),
    ("sqlite", "sqlite"),
]

YAML_SIMPLE_BACKEND = [
    ("yaml", "yaml"),
]


@pytest.fixture(params=FULL_BACKENDS, ids=[b[0] for b in FULL_BACKENDS])
def backend(request, tmp_path):
    """
    Parametrized fixture for full-featured backends (Memory, XML, SQLite).
    
    Returns:
        tuple: (backend_name, create_func, write_func, read_func, temp_file)
    """
    backend_name, backend_type = request.param
    
    # Create temp file path (used by file-based backends)
    if backend_type == "xml":
        temp_file = tmp_path / "test.xml"
    elif backend_type == "sqlite":
        temp_file = tmp_path / "test.db"
    else:
        temp_file = None
    
    # Define backend operations
    if backend_type == "mem":
        def create_db():
            return MemFactory.create()
        
        def write_db(db, path):
            # Memory backend doesn't need explicit write
            return db
        
        def read_db(db_or_path):
            # Return same DB instance
            return db_or_path
    
    elif backend_type == "xml":
        def create_db():
            return MemFactory.create()
        
        def write_db(db, path):
            XmlFactory.write(db, str(path))
            return path
        
        def read_db(path):
            return XmlFactory.read(str(path))
    
    elif backend_type == "sqlite":
        def create_db():
            return SqliteUCIS(str(temp_file))
        
        def write_db(db, path):
            db.close()  # Commit changes
            return path
        
        def read_db(path):
            return SqliteUCIS(str(path))
    
    yield (backend_name, create_db, write_db, read_db, temp_file)


@pytest.fixture(params=YAML_SIMPLE_BACKEND, ids=[b[0] for b in YAML_SIMPLE_BACKEND])
def yaml_backend(request, tmp_path):
    """
    Separate fixture for YAML backend with limited functionality.
    Only use this for basic scope/covergroup/coverpoint tests.
    
    YAML backend supports:
    - Basic scopes (INSTANCE, MODULE)
    - Covergroups
    - Coverpoints
    - Bins with counts
    
    YAML backend does NOT support:
    - Complex metadata (history nodes, properties)
    - User-defined attributes
    - Toggle/FSM/assertion coverage
    - Code coverage details
    
    Returns:
        tuple: (backend_name, create_func, write_func, read_func, temp_file)
    """
    backend_name, backend_type = request.param
    temp_file = tmp_path / "test.yaml"
    
    def create_db():
        return MemFactory.create()
    
    def write_db(db, path):
        # Use YamlWriter if available
        try:
            from ucis.yaml.yaml_writer import YamlWriter
            writer = YamlWriter()
            with open(str(path), 'w') as f:
                writer.write(f, db)
            return path
        except (ImportError, AttributeError) as e:
            pytest.skip(f"YAML writer not available: {e}")
    
    def read_db(path):
        from ucis.yaml.yaml_reader import YamlReader
        reader = YamlReader()
        with open(str(path), 'r') as f:
            return reader.read(f)
    
    yield (backend_name, create_db, write_db, read_db, temp_file)


# Helper assertions
def assert_coverage_equal(expected, actual, tolerance=0.01):
    """Compare coverage percentages with tolerance"""
    assert abs(expected - actual) < tolerance, f"Expected {expected}, got {actual}"


def assert_scope_tree_equal(scope1, scope2):
    """Recursively compare scope hierarchies"""
    assert scope1.getScopeName() == scope2.getScopeName(), \
        f"Scope names differ: {scope1.getScopeName()} != {scope2.getScopeName()}"
    assert scope1.getScopeType() == scope2.getScopeType(), \
        f"Scope types differ: {scope1.getScopeType()} != {scope2.getScopeType()}"
