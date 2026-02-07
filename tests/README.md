# Tests

This directory contains all tests for the pyucis-sqlite project.

## Directory Structure

- `unit/` - Unit tests (converted from unittest to pytest)
- `sqlite/` - SQLite-specific tests

## Running Tests

### Run all unit tests
```bash
export PYTHONPATH=/path/to/pyucis-sqlite/src
python3 -m pytest tests/unit/
```

### Run specific test file
```bash
export PYTHONPATH=/path/to/pyucis-sqlite/src
python3 -m pytest tests/unit/test_merge.py
```

### Run specific test
```bash
export PYTHONPATH=/path/to/pyucis-sqlite/src
python3 -m pytest tests/unit/test_merge.py::TestMerge::test_2db_1t_1i
```

### Run tests with verbose output
```bash
export PYTHONPATH=/path/to/pyucis-sqlite/src
python3 -m pytest tests/unit/ -v
```

### Run tests from project root
```bash
export PYTHONPATH=./src
python3 -m pytest
```

The `pytest.ini` configuration file in the project root specifies that tests are located in `tests/unit/`.

## Test Fixtures

The `conftest.py` file in the unit tests directory provides common pytest fixtures:

- `test_data_dir(tmpdir)` - Provides a temporary directory for test data

Tests can use this fixture by including it as a parameter:

```python
def test_my_function(test_data_dir):
    # test_data_dir is a temporary directory
    test_file = test_data_dir.join("test.txt")
    test_file.write("content")
    # ...
```

## Migration from unittest

These tests were migrated from unittest to pytest. Key changes:

1. Test classes no longer inherit from `unittest.TestCase`
2. `self.assertEqual(a, b)` → `assert a == b`
3. `self.assertNotEqual(a, b)` → `assert a != b`
4. `setUp()` and `tearDown()` methods can be replaced with pytest fixtures
5. tmpdir fixture available for temporary file operations
