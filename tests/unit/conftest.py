"""
Pytest configuration for unit tests
"""
import pytest
import os


@pytest.fixture
def test_data_dir(tmpdir):
    """Fixture to provide a temporary directory for test data"""
    return tmpdir
