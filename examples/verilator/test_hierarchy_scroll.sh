#!/bin/bash
# Quick test script to verify hierarchy scrolling
echo "🚀 Launching TUI..."
echo "   Press '2' to go to Hierarchy view"
echo "   Press 'E' to expand all nodes"
echo "   Use arrow keys to navigate down"
echo "   Verify content scrolls when cursor reaches bottom"
echo "   Press 'q' to quit"
echo ""
PYTHONPATH=/home/mballance/projects/fvutils/pyucis-main/src python3 -m ucis view coverage/coverage.cdb
