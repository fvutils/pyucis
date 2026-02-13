###########################
Interactive Terminal UI
###########################

Overview
========

PyUCIS includes an interactive Terminal User Interface (TUI) for exploring and analyzing 
coverage databases directly from the command line. The TUI provides a fast, keyboard-driven 
alternative to HTML reports, ideal for real-time coverage assessment during verification.

**Key Benefits:**

* **Fast Navigation** - Keyboard shortcuts for efficient browsing
* **Real-Time Analysis** - No need to generate static reports
* **Remote-Friendly** - Works over SSH and in terminal-only environments  
* **Priority-Driven** - Built-in hotspot analysis for test planning
* **Rich Visualizations** - Color-coded indicators and formatted tables
* **Low Overhead** - Lightweight compared to browser-based reports

Launch the TUI
==============

Use the ``ucis view`` command to open any coverage database:

.. code-block:: bash

    # View a coverage database
    ucis view coverage.xml
    
    # View SQLite database
    ucis view coverage.ucisdb
    
    # View YAML format
    ucis view coverage.yaml

The TUI will load the database and display the Dashboard view by default.

TUI Views
=========

The TUI provides five specialized views for coverage analysis:

Dashboard View
--------------

**Keyboard:** Press ``1`` or launch the TUI

The Dashboard provides a high-level overview of coverage statistics:

* **Total Coverage Percentage** - Overall coverage across all items
* **Coverage Breakdown** - Detailed counts by coverage type:
  
  - Covergroups, Coverpoints, Bins
  - Assertions, Toggles, Branches  
  - Statements, Expressions, FSM states/transitions

* **Color-Coded Status** - Visual indicators for coverage levels:
  
  - 🟢 Green (≥80%) - Good coverage
  - 🟡 Yellow (50-80%) - Needs attention
  - 🔴 Red (<50%) - Critical gaps

**Use Cases:**

* Quick health check of verification progress
* High-level status for stakeholder updates
* Starting point before drilling into details

Hierarchy View  
--------------

**Keyboard:** Press ``2``

Navigate the design/verification hierarchy with an interactive tree structure:

**Features:**

* **Expandable Tree** - Show/hide child scopes with arrow keys
* **Coverage Indicators** - Percentage and color coding for each node
* **Breadth-First Display** - See all scopes at each level
* **Scope Details** - Type, weight, and source information

**Navigation:**

* ``↑/↓`` - Move between tree items
* ``→`` - Expand selected node to show children
* ``←`` - Collapse selected node
* ``Enter`` - Toggle expansion
* ``Home/End`` - Jump to first/last item
* ``PgUp/PgDn`` - Scroll by page

**Use Cases:**

* Understanding design structure and organization
* Finding specific modules or covergroups
* Identifying hierarchy branches with low coverage
* Navigating from top-level to detailed coverage items

Gaps View
---------

**Keyboard:** Press ``3``

Focus on incomplete coverage items that need attention:

**Features:**

* **Filtered List** - Only shows items below 100% coverage
* **Sorted by Priority** - Lowest coverage items first
* **Coverage Percentage** - Current status for each gap
* **Full Path** - Hierarchical location of each item
* **Gap Count** - Total number of incomplete items

**Information Displayed:**

* Item name and type (covergroup, coverpoint, assertion, etc.)
* Current coverage percentage
* Full hierarchical path
* Scope type and details

**Use Cases:**

* Test planning - identify what needs coverage
* Prioritizing verification efforts
* Tracking progress toward coverage goals
* Finding zero-hit items quickly

Hotspots View
-------------

**Keyboard:** Press ``4``

Intelligent priority-based recommendations for coverage improvement:

**Priority Levels:**

* **P0 - Critical:** Low coverage modules (<50%) requiring immediate attention
* **P1 - High Priority:**
  
  - Completely untested coverpoints (0% coverage)
  - Near-complete items (90%+) - "low hanging fruit"

* **P2 - Medium Priority:** Other partially covered items needing work

**Features:**

* **Smart Prioritization** - Algorithmic ranking based on multiple factors
* **Impact Analysis** - Focus on items that will improve coverage most
* **Actionable Targets** - Clear next steps for verification team
* **Effort Optimization** - Balance between coverage gain and test complexity

**Information Displayed:**

* Priority level (P0/P1/P2) with color coding
* Item name and hierarchical path
* Current coverage percentage  
* Recommended action (test, complete, investigate)

**Use Cases:**

* Sprint planning and task assignment
* Identifying quick wins vs. long-term efforts
* Resource allocation for verification
* Coverage closure strategy

Metrics View
------------

**Keyboard:** Press ``5``

Statistical analysis and quality indicators for coverage data:

**Coverage Distribution:**

* **By Hit Count** - Histogram of bins in ranges:
  
  - 0 hits (uncovered)
  - 1-10 hits (lightly tested)
  - 11-100 hits (moderately tested)  
  - 100+ hits (heavily tested)

* **Visualization** - Bar chart showing distribution

**Statistical Measures:**

* **Mean Hit Count** - Average hits per bin
* **Median Hit Count** - Middle value (50th percentile)
* **Min/Max Hits** - Range of coverage activity
* **Standard Deviation** - Variance in testing intensity

**Quality Indicators:**

* **Complete Tier** - Items at 100% coverage
* **High Tier** - Items at 80-99% coverage
* **Medium Tier** - Items at 50-79% coverage  
* **Low Tier** - Items below 50% coverage

**Utilization Metrics:**

* **Bin Utilization Rate** - Percentage of bins with any hits
* **Zero-Hit Ratio** - Percentage of completely untested bins
* **Average Bins per Coverpoint** - Coverage granularity indicator

**Use Cases:**

* Quality assessment beyond just percentages
* Identifying under-tested vs. over-tested areas
* Detecting potential test redundancy (over-testing)
* Understanding verification intensity patterns
* Coverage model validation

Keyboard Shortcuts
==================

Global Navigation
-----------------

These shortcuts work in all views:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Key
     - Action
   * - ``1``
     - Switch to Dashboard view
   * - ``2``
     - Switch to Hierarchy view
   * - ``3``
     - Switch to Gaps view
   * - ``4``
     - Switch to Hotspots view
   * - ``5``
     - Switch to Metrics view
   * - ``?``
     - Show help overlay with all shortcuts
   * - ``q`` or ``Ctrl+C``
     - Quit the TUI

List/Tree Navigation
--------------------

For views with lists or trees (Hierarchy, Gaps, Hotspots):

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Key
     - Action
   * - ``↑`` or ``k``
     - Move up one item
   * - ``↓`` or ``j``
     - Move down one item  
   * - ``→`` or ``l``
     - Expand tree node (Hierarchy view)
   * - ``←`` or ``h``
     - Collapse tree node (Hierarchy view)
   * - ``Enter`` or ``Space``
     - Toggle expansion (Hierarchy view)
   * - ``Home``
     - Jump to first item
   * - ``End``
     - Jump to last item
   * - ``PgUp``
     - Scroll up one page
   * - ``PgDn``
     - Scroll down one page

Tips & Tricks
=============

Efficient Workflows
-------------------

**Quick Assessment (2-3 minutes):**

1. Launch with ``ucis view coverage.xml``
2. Check Dashboard (view 1) for overall status
3. Jump to Gaps (view 3) to see what's missing
4. Review Hotspots (view 4) for prioritized actions

**Deep Analysis (10-15 minutes):**

1. Start with Metrics (view 5) to understand quality
2. Navigate Hierarchy (view 2) to explore structure
3. Identify problem areas with Gaps (view 3)
4. Plan next tests with Hotspots (view 4)

**Daily Verification Loop:**

1. Run tests and update coverage database
2. ``ucis view coverage.ucisdb`` to check progress
3. Check Gaps (view 3) - is the list shrinking?
4. Focus on P0/P1 Hotspots (view 4) for next tests

Performance Tips
----------------

* **Use SQLite** - Faster loading than XML for large databases
* **Local Files** - Avoid network-mounted databases when possible
* **Reasonable Size** - TUI works best with databases up to ~100MB
* **SSH Optimization** - Use compression: ``ssh -C user@host``

Remote Workflows
----------------

The TUI is ideal for remote development:

.. code-block:: bash

    # SSH into build server
    ssh -C user@build-server
    
    # Navigate to verification directory
    cd /path/to/verification
    
    # Check latest coverage
    ucis view regression_coverage.ucisdb
    
    # Or view specific test
    ucis view test_results/test_name.ucis

Color Scheme
============

The TUI uses color coding throughout for quick visual assessment:

**Coverage Levels:**

* 🟢 **Green** - Good coverage (≥80%)
* 🟡 **Yellow** - Needs attention (50-79%)  
* 🔴 **Red** - Critical gap (<50%)
* ⚪ **White/Gray** - Uncovered (0%)

**Priority Levels:**

* 🔴 **Red** - P0 Critical
* 🟡 **Yellow** - P1 High Priority
* 🔵 **Blue** - P2 Medium Priority

**UI Elements:**

* **Bold** - Selected/highlighted item
* **Dim** - Secondary information
* **Underline** - Active view/tab

Comparison: TUI vs. HTML Reports
=================================

Choose the right tool for your workflow:

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Feature
     - TUI (``ucis view``)
     - HTML Reports
   * - **Speed**
     - ✅ Instant startup
     - ⚠️ Generation + browser load
   * - **Navigation**
     - ✅ Keyboard-driven
     - 🖱️ Mouse-driven
   * - **Environment**
     - ✅ Terminal only
     - 🌐 Browser required
   * - **Remote Access**
     - ✅ SSH-friendly
     - ⚠️ Needs port forwarding
   * - **Visualizations**
     - ⚠️ Text-based
     - ✅ Charts and graphs
   * - **Sharing**
     - ⚠️ Live access only
     - ✅ Self-contained file
   * - **Filtering**
     - 🔍 Built-in views
     - 🔍 Interactive filters
   * - **Large Data**
     - ✅ Handles well
     - ⚠️ Can be slow
   * - **Offline Use**
     - ✅ Always works
     - ✅ Works after first load

**When to Use TUI:**

* During active verification (quick checks)
* Remote terminal sessions
* CI/CD pipeline integration
* Performance-critical environments
* Keyboard-centric workflows

**When to Use HTML:**

* Stakeholder presentations
* Detailed visual analysis
* Team sharing and collaboration
* Archival documentation
* Graphical trend analysis

CI/CD Integration
=================

The TUI can be used in automated workflows:

**GitLab CI Example:**

.. code-block:: yaml

    coverage_check:
      script:
        - run_tests.sh
        - ucis merge -o coverage.ucisdb test_*.ucis
        # Check if coverage meets threshold
        - |
          coverage=$(ucis show summary coverage.ucisdb --output-format json | jq '.total_coverage')
          if (( $(echo "$coverage < 80" | bc -l) )); then
            echo "❌ Coverage below 80% ($coverage%)"
            ucis view coverage.ucisdb  # Show TUI output in logs
            exit 1
          fi

**GitHub Actions Example:**

.. code-block:: yaml

    - name: Check Coverage
      run: |
        ucis merge -o coverage.ucisdb test_*.ucis
        # Display TUI output in GitHub Actions logs
        ucis view coverage.ucisdb
        # Then check threshold
        ucis show summary coverage.ucisdb

**Jenkins Integration:**

.. code-block:: groovy

    stage('Coverage Analysis') {
        steps {
            sh 'ucis merge -o coverage.ucisdb **/*.ucis'
            // Display TUI in console output
            sh 'ucis view coverage.ucisdb'
            // Generate reports
            sh 'ucis report coverage.ucisdb -of html -o coverage.html'
        }
    }

Troubleshooting
===============

Common Issues
-------------

**TUI doesn't display correctly**

* Ensure terminal supports colors: ``echo $TERM``
* Use modern terminal emulator (iTerm2, Windows Terminal, GNOME Terminal)
* Check terminal size: ``tput cols`` and ``tput lines`` (minimum 80x24)

**Slow performance**

* Convert XML to SQLite: ``ucis convert -if xml -of sqlite input.xml -o output.ucisdb``
* Reduce database size by filtering or sampling
* Use local storage instead of network mounts

**Database won't load**

* Verify file format is supported: ``.xml``, ``.ucis``, ``.ucisdb``, ``.yaml``
* Check file permissions: ``ls -l coverage.xml``
* Validate database integrity: ``ucis show summary coverage.xml``

**SSH rendering issues**

* Enable compression: ``ssh -C user@host``
* Use screen/tmux for session persistence
* Check SSH client terminal settings

Getting Help
------------

**In the TUI:**

* Press ``?`` for help overlay with all keyboard shortcuts
* Press ``q`` to quit and return to shell

**Command Line:**

.. code-block:: bash

    # View command help
    ucis view --help
    
    # Check database info without TUI
    ucis show summary coverage.xml

**Documentation:**

* :doc:`show_commands` - Command-line analysis tools
* :doc:`reference/html_coverage_report` - Alternative HTML reports
* :doc:`commands` - All PyUCIS commands

Examples
========

Example 1: Daily Verification Workflow
---------------------------------------

.. code-block:: bash

    # Run regression tests
    make regression
    
    # Merge all test results
    ucis merge -o daily_coverage.ucisdb test_results/*.ucis
    
    # Quick TUI check
    ucis view daily_coverage.ucisdb
    # Press 3 to see gaps
    # Press 4 to see priorities
    # Press q to exit
    
    # If coverage looks good, generate HTML for team
    ucis report daily_coverage.ucisdb -of html -o daily_report.html

Example 2: Coverage Debugging
------------------------------

.. code-block:: bash

    # Test failed but coverage seems wrong
    ucis view test_output.ucis
    
    # In TUI:
    # - Press 2 to navigate hierarchy
    # - Find the module in question
    # - Check if covergroups are present
    # - Verify bins have expected structure
    
    # Export details for investigation
    ucis show covergroups test_output.ucis > debug.txt

Example 3: Remote Verification
-------------------------------

.. code-block:: bash

    # SSH to build server
    ssh -C verification@server
    
    # Check current status
    cd /project/verification
    ucis view latest_regression.ucisdb
    
    # Review gaps and priorities
    # Exit TUI (q)
    
    # Start targeted tests for P0 items
    make test TEST=high_priority_tests

Example 4: Coverage Comparison
-------------------------------

.. code-block:: bash

    # Check yesterday's coverage
    ucis view regression_2026-02-12.ucisdb
    # Note gaps from view 3
    
    # Check today's coverage
    ucis view regression_2026-02-13.ucisdb
    # Compare - did gaps shrink?
    
    # Formal comparison
    ucis show compare regression_2026-02-12.ucisdb regression_2026-02-13.ucisdb

See Also
========

* :doc:`show_commands` - Command-line coverage analysis tools
* :doc:`reference/html_coverage_report` - Interactive HTML reports
* :doc:`commands` - Complete command reference
* :doc:`mcp_server` - AI agent integration for automated analysis
