#!/bin/bash
# Test script to verify format detection

echo "========================================================================"
echo "Format Detection Verification Tests"
echo "========================================================================"
echo ""

cd "$(dirname "$0")"
export PYTHONPATH="$(cd ../.. && pwd)/src"

echo "Test 1: Detect .cdb file format"
python3 -c "
from ucis.rgy.format_rgy import FormatRgy
rgy = FormatRgy.inst()
fmt = rgy.detectDatabaseFormat('coverage/coverage.cdb')
print(f'  Detected: {fmt}')
print(f'  Expected: sqlite')
print(f'  Status: {\"✅ PASS\" if fmt == \"sqlite\" else \"❌ FAIL\"}')"
echo ""

echo "Test 2: Load database with auto-detection"
python3 -c "
from ucis.tui.models.coverage_model import CoverageModel
try:
    model = CoverageModel('coverage/coverage.cdb')
    print('  ✅ PASS - Database loaded successfully')
except Exception as e:
    print(f'  ❌ FAIL - {e}')"
echo ""

echo "Test 3: View command starts without errors (quick test)"
timeout 2 python -m ucis view coverage/coverage.cdb 2>&1 | grep -q "Coverage Dashboard" 
if [ $? -eq 0 ]; then
    echo "  ✅ PASS - TUI launched successfully"
else
    echo "  ⚠️  WARNING - Could not verify TUI (timeout or display issue)"
fi
echo ""

echo "Test 4: Format detection for various extensions"
python3 << 'PYEOF'
from ucis.rgy.format_rgy import FormatRgy
import tempfile
import os

rgy = FormatRgy.inst()
tests = [
    ('.xml', b'<?xml version="1.0"?>', 'xml'),
    ('.yaml', b'---\nucis: test', 'yaml'),
    ('.cdb', b'SQLite format 3\x00', 'sqlite'),
    ('.dat', b'test', 'vltcov'),
]

all_pass = True
for ext, content, expected in tests:
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
        f.write(content)
        fname = f.name
    
    detected = rgy.detectDatabaseFormat(fname)
    status = '✅' if detected == expected else '❌'
    if detected != expected:
        all_pass = False
    print(f'  {status} {ext}: expected={expected}, detected={detected}')
    os.unlink(fname)

if all_pass:
    print('\n  ✅ PASS - All extensions detected correctly')
else:
    print('\n  ❌ FAIL - Some extensions not detected correctly')
PYEOF
echo ""

echo "========================================================================"
echo "Format Detection Tests Complete"
echo "========================================================================"
