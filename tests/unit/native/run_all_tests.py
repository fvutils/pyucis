#!/usr/bin/env python3
"""
Run all UCIS C API tests
"""

import sys
import subprocess
import os

def run_test(test_file):
    """Run a single test file and return True if passed"""
    print(f"\n{'='*70}")
    print(f"Running: {test_file}")
    print('='*70)
    
    result = subprocess.run(
        [sys.executable, test_file],
        cwd=os.path.dirname(test_file)
    )
    
    return result.returncode == 0

def main():
    # Get test directory
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # List of test files in order
    tests = [
        os.path.join(test_dir, "test_basic.py"),
        os.path.join(test_dir, "test_scopes.py"),
        os.path.join(test_dir, "test_coverage.py"),
    ]
    
    print("="*70)
    print("UCIS C API - Complete Test Suite")
    print("="*70)
    
    results = {}
    
    for test in tests:
        test_name = os.path.basename(test)
        if os.path.exists(test):
            results[test_name] = run_test(test)
        else:
            print(f"\n⚠️  Test not found: {test_name}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        print(f"  {status:8} - {test_name}")
    
    print("-"*70)
    print(f"  Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 ALL TESTS PASSED! 🎉")
        print("="*70)
        return 0
    else:
        print("\n  ❌ SOME TESTS FAILED")
        print("="*70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
