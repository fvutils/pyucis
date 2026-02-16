#!/usr/bin/env python3
"""
Generate cocotb-coverage sample files for testing import functionality.

This script creates various coverage scenarios and exports them to both
XML and YAML formats for testing the PyUCIS import implementation.
"""

from cocotb_coverage.coverage import coverage_db, CoverPoint, CoverCross, CoverCheck

# Clear any existing coverage
coverage_db.clear()

# Example 1: Simple coverpoint with bins
@CoverPoint(
    name="test.simple_coverage.address_cp",
    vname="addr",
    bins=[0, 1, 2, 3, 4, 5, 6, 7],
    bins_labels=["addr_0", "addr_1", "addr_2", "addr_3", "addr_4", "addr_5", "addr_6", "addr_7"],
    weight=1,
    at_least=1
)
def sample_address(addr):
    pass

# Example 2: Coverpoint with ranges
@CoverPoint(
    name="test.simple_coverage.data_cp",
    vname="data",
    xf=lambda d: d // 16,  # Divide into ranges
    rel=lambda val, bin: val == bin,
    bins=list(range(16)),  # 16 bins for data ranges
    weight=2,
    at_least=2
)
def sample_data(data):
    pass

# Example 3: Tuple coverpoint
@CoverPoint(
    name="test.advanced_coverage.transaction_cp",
    bins=[(0, 0), (0, 1), (1, 0), (1, 1)],
    bins_labels=["read_idle", "read_active", "write_idle", "write_active"],
    weight=1
)
def sample_transaction(read_write, active):
    pass

# Example 4: Cross coverage
@CoverCross(
    name="test.advanced_coverage.addr_data_cross",
    items=["test.simple_coverage.address_cp", "test.simple_coverage.data_cp"],
    weight=3,
    at_least=1
)
def sample_cross(addr, data):
    pass

# Example 5: Cover check (pass/fail)
@CoverCheck(
    name="test.checks.valid_protocol",
    f_fail=lambda valid, ready: not valid or ready,
    weight=1
)
def check_protocol(valid, ready):
    pass

# Generate some sample coverage data
print("Generating cocotb-coverage sample data...")

# Sample addresses
for i in range(100):
    sample_address(i % 8)
    
# Sample data values
for i in range(150):
    sample_data(i % 256)

# Sample transactions
transactions = [
    (0, 0), (0, 1), (1, 0), (1, 1),
    (0, 0), (0, 1), (1, 0),  # Some bins hit multiple times
    (1, 1), (1, 1)
]
for read_write, active in transactions:
    sample_transaction(read_write, active)

# Sample cross coverage (reuse address and data samples)
for i in range(50):
    addr = i % 8
    data = i % 256
    sample_cross(addr, data)

# Sample protocol checks
protocol_samples = [
    (True, True),   # Valid
    (False, False), # Valid
    (False, True),  # Valid
    (True, True),   # Valid
    (True, False),  # Invalid - should fail
]
for valid, ready in protocol_samples:
    check_protocol(valid, ready)

# Report coverage to console
print("\n" + "="*70)
print("COVERAGE REPORT")
print("="*70)
coverage_db.report_coverage(print, bins=True)

# Export to XML
xml_file = "sample_cocotb_coverage.xml"
print(f"\nExporting to {xml_file}...")
coverage_db.export_to_xml(xml_file)

# Export to YAML
yaml_file = "sample_cocotb_coverage.yml"
print(f"Exporting to {yaml_file}...")
coverage_db.export_to_yaml(yaml_file)

print("\n✓ Sample files generated successfully!")
print(f"  - {xml_file}")
print(f"  - {yaml_file}")
