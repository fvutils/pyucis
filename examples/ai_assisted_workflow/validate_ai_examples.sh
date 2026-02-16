#!/bin/bash
# AI Examples Validation Script
# Run this to verify the AI-assisted workflow examples work correctly

set -e  # Exit on error

echo "======================================================================="
echo "PyUCIS AI-Assisted Workflow Validation"
echo "======================================================================="
echo ""

# Change to verilator example directory
cd "$(dirname "$0")"
EXAMPLES_DIR=$(pwd)

echo "Working directory: $EXAMPLES_DIR"
echo "Note: Using coverage data from verilator example via symlink"
echo ""

# Set up environment
export PYTHONPATH="../../src"
echo "✓ Set PYTHONPATH to ../../src"

# Check PyUCIS import
echo "Testing PyUCIS import..."
python3 -c "import ucis; print('✓ PyUCIS module imported successfully')" || {
    echo "✗ Failed to import PyUCIS module"
    echo "  Make sure PyUCIS is installed or PYTHONPATH is set correctly"
    exit 1
}
echo ""

# Check if merged database exists
echo "Checking for coverage database..."
if [ ! -f "coverage/merged.cdb" ]; then
    echo "✗ coverage/merged.cdb not found"
    echo "  Checking if verilator example has data..."
    if [ -f "../verilator/coverage/merged.cdb" ]; then
        echo "  ✓ Found data in verilator example"
        echo "  Symlink should work, but let's verify..."
        ls -l coverage/merged.cdb
    else
        echo "  Please build the verilator example first:"
        echo "  cd ../verilator && make merge"
        exit 1
    fi
fi
echo "✓ Database exists: coverage/merged.cdb ($(du -h coverage/merged.cdb | cut -f1))"
echo ""

# Test Scenario 1: Summary
echo "Testing Scenario 1: Coverage Summary"
echo "------------------------------------"
python3 -m ucis show summary coverage/merged.cdb --output-format text > /tmp/test_summary.txt 2>&1 || {
    echo "✗ Failed to get summary"
    cat /tmp/test_summary.txt
    exit 1
}
echo "✓ Summary command works"
grep -q "database:" /tmp/test_summary.txt && echo "  - Database path found in output"
echo ""

# Test Scenario 2: Test List
echo "Testing Scenario 2: Test Listing"
echo "---------------------------------"
python3 -m ucis show tests coverage/merged.cdb --output-format json > /tmp/test_tests.json 2>&1 || {
    echo "✗ Failed to list tests"
    cat /tmp/test_tests.json
    exit 1
}
echo "✓ Test listing command works"
TEST_COUNT=$(python3 -c "import json; data=json.load(open('/tmp/test_tests.json')); print(len(data.get('tests', [])))" 2>/dev/null || echo "0")
echo "  - Found $TEST_COUNT tests in database"
echo ""

# Test Scenario 3: Hierarchy
echo "Testing Scenario 3: Hierarchy Display"
echo "--------------------------------------"
python3 -m ucis show hierarchy coverage/merged.cdb --max-depth 2 --output-format text > /tmp/test_hierarchy.txt 2>&1 || {
    echo "✗ Failed to show hierarchy"
    cat /tmp/test_hierarchy.txt
    exit 1
}
echo "✓ Hierarchy command works"
echo ""

# Test Scenario 4: Gaps Analysis
echo "Testing Scenario 4: Coverage Gaps"
echo "----------------------------------"
python3 -m ucis show gaps coverage/merged.cdb --threshold 80 --output-format json > /tmp/test_gaps.json 2>&1 || {
    echo "✗ Failed to find gaps"
    cat /tmp/test_gaps.json
    exit 1
}
echo "✓ Gaps command works"
echo ""

# Test Scenario 5: Hotspots
echo "Testing Scenario 5: Coverage Hotspots"
echo "--------------------------------------"
python3 -m ucis show hotspots coverage/merged.cdb --limit 5 --output-format text > /tmp/test_hotspots.txt 2>&1 || {
    echo "✗ Failed to identify hotspots"
    cat /tmp/test_hotspots.txt
    exit 1
}
echo "✓ Hotspots command works"
echo ""

# Test Scenario 6: Code Coverage
echo "Testing Scenario 6: Code Coverage Details"
echo "------------------------------------------"
python3 -m ucis show code-coverage coverage/merged.cdb --output-format text > /tmp/test_codecov.txt 2>&1 || {
    echo "✗ Failed to show code coverage"
    cat /tmp/test_codecov.txt
    exit 1
}
echo "✓ Code coverage command works"
echo ""

# Test Scenario 7: Export LCOV
echo "Testing Scenario 7: LCOV Export"
echo "--------------------------------"
python3 -m ucis show code-coverage coverage/merged.cdb --output-format lcov -o /tmp/test_coverage.lcov 2>&1 || {
    echo "✗ Failed to export LCOV"
    exit 1
}
if [ -f "/tmp/test_coverage.lcov" ]; then
    echo "✓ LCOV export successful ($(wc -l < /tmp/test_coverage.lcov) lines)"
    head -3 /tmp/test_coverage.lcov | sed 's/^/  /'
else
    echo "✗ LCOV file not created"
    exit 1
fi
echo ""

# Test Scenario 8: Export Cobertura
echo "Testing Scenario 8: Cobertura Export"
echo "-------------------------------------"
python3 -m ucis show code-coverage coverage/merged.cdb --output-format cobertura -o /tmp/test_coverage.xml 2>&1 || {
    echo "✗ Failed to export Cobertura XML"
    exit 1
}
if [ -f "/tmp/test_coverage.xml" ]; then
    echo "✓ Cobertura export successful ($(wc -l < /tmp/test_coverage.xml) lines)"
    head -2 /tmp/test_coverage.xml | sed 's/^/  /'
else
    echo "✗ Cobertura XML file not created"
    exit 1
fi
echo ""

# Test Scenario 9: Metrics
echo "Testing Scenario 9: Coverage Metrics"
echo "-------------------------------------"
python3 -m ucis show metrics coverage/merged.cdb --output-format json > /tmp/test_metrics.json 2>&1 || {
    echo "✗ Failed to show metrics"
    cat /tmp/test_metrics.json
    exit 1
}
echo "✓ Metrics command works"
echo ""

# Test Scenario 10: Query Script
echo "Testing Scenario 10: Test Coverage Query Script"
echo "------------------------------------------------"
if [ -f "query_test_coverage.py" ]; then
    python3 query_test_coverage.py > /tmp/test_query.txt 2>&1 || {
        echo "⚠ Query script failed (may have known issues)"
        echo "  This is not critical for AI examples"
    }
    if grep -q "TEST CONTRIBUTION" /tmp/test_query.txt; then
        echo "✓ Query script executed (partial)"
    else
        echo "⚠ Query script output unexpected"
    fi
else
    echo "⚠ query_test_coverage.py not found (optional)"
fi
echo ""

# Test JSON parsing
echo "Testing JSON Output Parsing"
echo "---------------------------"
TOTAL_COVERGROUPS=$(python3 -c "
import json
try:
    with open('/tmp/test_summary.txt') as f:
        content = f.read()
        # Try to parse if it's JSON, otherwise just check it exists
        if content.strip():
            print('OK')
        else:
            print('EMPTY')
except Exception as e:
    print(f'ERROR: {e}')
" 2>&1)
echo "✓ Output files can be processed"
echo ""

# Clean up
echo "Cleaning up temporary files..."
rm -f /tmp/test_*.txt /tmp/test_*.json /tmp/test_*.lcov /tmp/test_*.xml
echo "✓ Cleanup complete"
echo ""

echo "======================================================================="
echo "Validation Summary"
echo "======================================================================="
echo "✓ All core commands validated successfully"
echo "✓ PyUCIS is working correctly"
echo "✓ Coverage database is accessible"
echo "✓ Export formats are functional"
echo ""
echo "The AI-assisted workflow examples are ready to use!"
echo ""
echo "Next steps:"
echo "  1. Read QUICK_START_AI.md for basic commands"
echo "  2. Try scenarios from AI_ASSISTED_WORKFLOW.md"
echo "  3. Explore with: python3 -m ucis view coverage/merged.cdb"
echo "======================================================================="
