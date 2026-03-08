# Test directory for file list feature

This directory contains tests for the `--file-list` feature of the merge command.

## Tests

- `test_file_list_feature.py` - Comprehensive tests including:
  - Basic file list functionality
  - Comments and blank lines handling
  - Combined file list + direct arguments
  - Large scale test with 1000 databases
  - Error handling

## Running Tests

```bash
# Run all file list tests
python -m unittest ve.unit.test_file_list.test_file_list_feature -v

# Run specific test
python -m unittest ve.unit.test_file_list.test_file_list_feature.TestFileList.test_file_list_large_scale -v
```
