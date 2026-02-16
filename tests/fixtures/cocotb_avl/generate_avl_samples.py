#!/usr/bin/env python3
"""
Generate AVL-style coverage sample files for testing import functionality.

Note: This creates a mock AVL coverage structure since full AVL requires
actual CocoTB simulation. The JSON structure matches AVL's DataFrame export.
"""

import json
import pandas as pd
from datetime import datetime

# Create sample coverage data in AVL format
# AVL exports coverage as pandas DataFrame serialized to JSON

coverage_data = {
    "metadata": {
        "generator": "AVL",
        "version": "0.5.0",
        "timestamp": datetime.now().isoformat(),
        "test_name": "sample_avl_test"
    },
    "functional_coverage": {
        "covergroups": {
            "address_coverage": {
                "type": "covergroup",
                "coverpoints": {
                    "addr_range": {
                        "bins": {
                            "low": {"range": [0, 31], "hits": 45},
                            "mid": {"range": [32, 63], "hits": 38},
                            "high": {"range": [64, 127], "hits": 22},
                            "very_high": {"range": [128, 255], "hits": 0}
                        },
                        "total_bins": 4,
                        "covered_bins": 3,
                        "coverage_pct": 75.0
                    },
                    "addr_parity": {
                        "bins": {
                            "even": {"hits": 56},
                            "odd": {"hits": 49}
                        },
                        "total_bins": 2,
                        "covered_bins": 2,
                        "coverage_pct": 100.0
                    }
                }
            },
            "transaction_coverage": {
                "type": "covergroup",
                "coverpoints": {
                    "trans_type": {
                        "bins": {
                            "read": {"hits": 67},
                            "write": {"hits": 54},
                            "read_modify_write": {"hits": 12},
                            "atomic": {"hits": 0}
                        },
                        "total_bins": 4,
                        "covered_bins": 3,
                        "coverage_pct": 75.0
                    },
                    "burst_length": {
                        "bins": {
                            "single": {"hits": 80},
                            "burst_2": {"hits": 25},
                            "burst_4": {"hits": 15},
                            "burst_8": {"hits": 8},
                            "burst_16": {"hits": 5}
                        },
                        "total_bins": 5,
                        "covered_bins": 5,
                        "coverage_pct": 100.0
                    }
                },
                "crosses": {
                    "type_x_length": {
                        "bins": {
                            "(read, single)": {"hits": 45},
                            "(read, burst_2)": {"hits": 12},
                            "(read, burst_4)": {"hits": 8},
                            "(write, single)": {"hits": 35},
                            "(write, burst_2)": {"hits": 13},
                            "(write, burst_4)": {"hits": 6}
                        },
                        "total_bins": 20,
                        "covered_bins": 6,
                        "coverage_pct": 30.0
                    }
                }
            }
        },
        "summary": {
            "total_bins": 53,
            "covered_bins": 39,
            "coverage_pct": 73.58
        }
    }
}

# Also create a DataFrame-based format (more typical for AVL)
df_data = {
    "coverpoint_name": [
        "addr_range.low",
        "addr_range.mid", 
        "addr_range.high",
        "addr_range.very_high",
        "addr_parity.even",
        "addr_parity.odd",
        "trans_type.read",
        "trans_type.write",
        "trans_type.read_modify_write",
        "trans_type.atomic"
    ],
    "bin_name": [
        "low", "mid", "high", "very_high",
        "even", "odd",
        "read", "write", "read_modify_write", "atomic"
    ],
    "hits": [45, 38, 22, 0, 56, 49, 67, 54, 12, 0],
    "goal": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    "covered": [True, True, True, False, True, True, True, True, True, False]
}

df = pd.DataFrame(df_data)

# Export hierarchical JSON
json_file = "sample_avl_coverage.json"
print(f"Generating AVL coverage sample data...")
print(f"Writing hierarchical format to {json_file}...")

with open(json_file, 'w') as f:
    json.dump(coverage_data, f, indent=2)

# Export DataFrame format
df_json_file = "sample_avl_coverage_df.json"
print(f"Writing DataFrame format to {df_json_file}...")

df.to_json(df_json_file, orient='records', indent=2)

# Also export as table format (index-oriented)
df_table_file = "sample_avl_coverage_table.json"
print(f"Writing table format to {df_table_file}...")

df.to_json(df_table_file, orient='index', indent=2)

print("\n" + "="*70)
print("AVL COVERAGE SUMMARY")
print("="*70)
print(f"Total Bins: {coverage_data['functional_coverage']['summary']['total_bins']}")
print(f"Covered Bins: {coverage_data['functional_coverage']['summary']['covered_bins']}")
print(f"Coverage: {coverage_data['functional_coverage']['summary']['coverage_pct']:.2f}%")

print("\nDataFrame Summary:")
print(df.to_string(index=False))

print("\n✓ Sample files generated successfully!")
print(f"  - {json_file} (hierarchical format)")
print(f"  - {df_json_file} (DataFrame records format)")
print(f"  - {df_table_file} (DataFrame table format)")
