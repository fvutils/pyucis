###########################
HTML Coverage Report Format
###########################

The HTML coverage report format generates a single-file, interactive HTML report that provides comprehensive visualization and analysis of UCIS coverage data. The report can be opened directly in any modern web browser without requiring a web server or external dependencies.

**Key Features:**

* **Single-File Portability** - All data, code, and styles embedded in one HTML file
* **Interactive Navigation** - Expandable hierarchical tree with filtering and search
* **D3.js Visualizations** - Pie charts, bar charts, and treemaps for coverage analysis
* **Coverpoint Bin Details** - View individual bins with hit counts, goals, and status
* **Zero Dependencies** - JavaScript libraries loaded from CDN (works offline if cached)
* **Responsive Design** - Professional UI that works on desktop and tablet
* **Export Friendly** - Easy to share via email, archive, or web hosting

Generating HTML Reports
=======================

Command Line
------------

The ``pyucis report`` command can generate HTML reports using the ``-of html`` option:

.. code-block:: bash

    # Basic HTML report
    pyucis report coverage.xml -of html -o report.html
    
    # From SQLite database
    pyucis report coverage.ucis -of html -o report.html
    
    # From YAML
    pyucis report coverage.yaml -of html -o report.html

The generated HTML file can be opened directly in any browser:

.. code-block:: bash

    firefox report.html
    # or
    chrome report.html
    # or
    open report.html  # macOS

Python API
----------

You can generate HTML reports programmatically using the ``HtmlFormatter`` class:

.. code-block:: python

    from ucis import UCIS
    from ucis.formatters.format_html import HtmlFormatter
    
    # Load database
    db = UCIS.load("coverage.xml")
    
    # Create formatter
    formatter = HtmlFormatter(
        include_source=True,  # Include source file info
        compress=False,       # Don't compress data (better for debugging)
        theme='light'         # Use light theme
    )
    
    # Generate report
    with open("report.html", "w") as f:
        formatter.format(db, f)

Report Features
===============

Summary Dashboard
-----------------

The summary view provides high-level coverage metrics:

* **Total Coverage Percentage** - Overall coverage across all items
* **Total Items** - Count of all coverage items (bins, statements, etc.)
* **Covered Items** - Count of items that have been hit
* **Uncovered Items** - Count of items that have not been hit
* **Coverage by Type** - Breakdown by coverage type (functional, line, branch, etc.)
* **Progress Bar** - Visual representation of overall coverage

Hierarchical Navigation
-----------------------

The hierarchy view displays the complete design/verification structure:

**Tree Features:**

* **Expandable/Collapsible Nodes** - Click arrows (▶/▼) to show/hide children
* **Expand All / Collapse All** - Buttons to quickly navigate deep hierarchies
* **Type-Specific Icons** - Visual distinction between modules (📦), covergroups (📋), coverpoints (🎯), etc.
* **Scope Type Labels** - Shows type in parentheses, e.g., "my_covergroup (COVERGROUP)"
* **Coverage Indicators** - Color-coded percentages (green ≥80%, orange 50-80%, red <50%)
* **4-Level Deep Support** - Handles nested hierarchies up to 4 levels

**Filtering:**

* **Search** - Real-time text search across scope names
* **Status Filter** - Filter by all/covered/uncovered/partial coverage
* **Coverage Threshold** - Show only scopes meeting minimum coverage percentage
* **Reset** - Clear all filters with one click

Coverpoint Bin Details
-----------------------

When you click on a coverpoint in the hierarchy, a detailed table displays all bins:

**Bin Table Columns:**

1. **Bin Name** - Identifier for the bin (monospace font)
2. **Type** - Badge showing bin type:
   
   * ``bin`` (blue) - Regular coverage bin
   * ``ignore_bin`` (orange) - Excluded from coverage calculations
   * ``illegal_bin`` (red) - Should never be hit

3. **Hits** - Number of times the bin was hit (formatted with thousands separators)
4. **Goal** - Target hit count (at_least threshold)
5. **Status** - Badge showing bin status:
   
   * ``covered`` (green) - Hit count ≥ goal
   * ``uncovered`` (red) - Hit count < goal
   * ``ignored`` (gray) - Excluded bin
   * ``illegal`` (red) - Illegal bin was hit (error!)
   * ``ok`` (green) - Illegal bin not hit

6. **Coverage** - Mini progress bar + percentage showing hits/goal ratio

**Visual Features:**

* **Row Highlighting** - Green background for covered bins, red for illegal bins that were hit
* **Hover Effects** - Subtle highlighting when hovering over rows
* **Sortable** - (Future: Click headers to sort)
* **Color-Coded Progress Bars** - Green (covered), orange (partial), red (uncovered)

Interactive Visualizations
---------------------------

The Charts tab provides three D3.js-powered visualizations:

Pie Chart: Coverage by Type
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Displays coverage percentage breakdown by type (functional, line, branch, toggle, etc.):

* **Color-Coded Segments** - Each type has a distinct color
* **Interactive Tooltips** - Hover to see exact percentages
* **Smart Labels** - Only show labels for segments >5% to avoid clutter
* **Hover Effects** - Segments highlight on mouseover

Bar Chart: Top Coverage Gaps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Shows the 10 scopes with the lowest coverage:

* **Horizontal Bars** - Length represents coverage percentage
* **Color-Coded** - Red (<50%), orange (50-80%), green (≥80%)
* **Labeled Axes** - Clear percentage scale and scope names
* **Interactive Tooltips** - Hover for scope name and exact percentage
* **Priority Identification** - Focus on items that need the most work

Treemap: Hierarchical Coverage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Visualizes the entire design hierarchy as nested rectangles:

* **Rectangle Size** - Proportional to scope weight (importance)
* **Rectangle Color** - Based on coverage percentage:
  
  * Red (0-50%) - Low coverage, needs attention
  * Orange (50-80%) - Moderate coverage
  * Green (80-100%) - Good coverage

* **Labels** - Scope name and coverage % shown for larger cells
* **Interactive Tooltips** - Hover for detailed information
* **Hover Highlighting** - Border thickness increases on mouseover
* **Quick Overview** - See entire project status at a glance

Coverage Gaps View
------------------

Shows all scopes with less than 100% coverage:

* **Filtered List** - Only incomplete coverage items
* **Quick Identification** - Find areas that need more verification
* **Coverage Percentages** - See how close each item is to completion

By Type View
------------

Lists coverage statistics grouped by coverage type:

* **Functional Coverage** - Covergroups and coverpoints
* **Code Coverage** - Line, branch, toggle, block, etc.
* **Organized Display** - Easy to see strengths and weaknesses

Technical Details
=================

File Structure
--------------

The HTML report is completely self-contained:

.. code-block:: html

    <!DOCTYPE html>
    <html>
    <head>
        <title>UCIS Coverage Report</title>
        <style>
            /* Embedded CSS (~15 KB) */
        </style>
    </head>
    <body>
        <!-- Application HTML structure -->
        
        <!-- Embedded JSON data -->
        <script id="coverage-data" type="application/json">
        {
            "metadata": {...},
            "summary": {...},
            "scopes": [...]
        }
        </script>
        
        <!-- Embedded JavaScript (~20 KB) -->
        <script>
            // Alpine.js reactive framework
            // D3.js visualization code
            // Application logic
        </script>
        
        <!-- Load libraries from CDN -->
        <script src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
    </body>
    </html>

Data Format
-----------

Coverage data is embedded as JSON within a ``<script>`` tag:

.. code-block:: json

    {
        "metadata": {
            "generator": "pyucis v1.0.0",
            "timestamp": "2024-02-12 02:00:00",
            "database": "coverage.ucis"
        },
        "summary": {
            "total_coverage": 73.5,
            "total_items": 1250,
            "covered_items": 919,
            "uncovered_items": 331,
            "coverage_by_type": {
                "functional": 68.0,
                "line": 82.5,
                "branch": 71.2
            }
        },
        "scopes": [
            {
                "id": "scope_1",
                "name": "top",
                "type": "DU_MODULE",
                "coverage": 73.5,
                "weight": 1,
                "children": [...],
                "bins": [...]
            }
        ]
    }

Technologies Used
-----------------

The HTML report uses modern web technologies:

* **Alpine.js v3** - Lightweight reactive framework (~15 KB)
* **D3.js v7** - Data visualization library (~40 KB)
* **Tailwind-inspired CSS** - Modern, responsive styling
* **ES6+ JavaScript** - Modern JavaScript features

**Browser Requirements:**

* Chrome 90+
* Firefox 88+
* Safari 14+
* Edge 90+
* Any modern browser with JavaScript enabled

Libraries are loaded from CDN for convenience but are cached by the browser after the first load.

File Size
---------

Typical file sizes:

* **Template + Code**: ~50-60 KB (HTML, CSS, JavaScript)
* **Data**: Variable based on coverage size
* **Total**: Usually 100-500 KB for typical projects
* **Libraries**: Loaded from CDN (not counted in file size)

For very large databases, data can optionally be compressed using gzip and base64 encoding (5-10x reduction).

Performance
-----------

* **Load Time**: < 3 seconds for typical projects
* **Chart Rendering**: < 500ms per chart
* **Tree Expansion**: Instant (reactive UI)
* **Search/Filter**: Real-time (< 100ms)
* **Memory Usage**: Efficient DOM rendering
* **Scalability**: Tested with 1000+ scopes

Use Cases
=========

Gap Analysis
------------

Identify areas needing more verification:

1. Open "Coverage Gaps" tab to see all incomplete items
2. Or use hierarchy view with filters:
   
   * Set "Status" to "Partial" or "Uncovered"
   * Set "Min Coverage" to filter by threshold
   * Use search to find specific modules

3. Click "📊 Charts" tab and check bar chart for top gaps
4. Focus verification effort on red/orange items

Bin Coverage Analysis
---------------------

Analyze functional coverage bins:

1. Navigate hierarchy to find covergroup
2. Expand covergroup to see coverpoints
3. Click on a coverpoint
4. Review bin table:
   
   * Green rows = covered bins (good!)
   * Red "uncovered" badges = need more hits
   * Red "illegal" badges = bins that shouldn't be hit but were!
   * Gray "ignored" = excluded as expected

5. Check hit counts vs. goals to prioritize test development

Subsystem Comparison
--------------------

Compare coverage across design subsystems:

1. Open "Hierarchy" tab
2. Expand top-level module to see instances
3. Compare coverage percentages at a glance
4. Or switch to "📊 Charts" tab
5. View treemap to see:
   
   * Large boxes = more important (higher weight)
   * Red boxes = need attention (low coverage)
   * Green boxes = well covered

Management Reporting
--------------------

Share coverage status with stakeholders:

1. Generate HTML report once
2. Share via email (single file attachment)
3. Or host on internal web server
4. Or save to SharePoint/shared drive
5. Stakeholders can:
   
   * View interactive charts (no tools required)
   * Drill down into details
   * See coverage trends over time (by comparing reports)
   * No UCIS tools or databases needed

Advantages
==========

Over Text Reports
-----------------

* **Visual** - Charts and colors instead of plain text
* **Interactive** - Navigate, filter, and drill down
* **Comprehensive** - All data in one place
* **Shareable** - Easy to email or host

Over Database Tools
-------------------

* **Portable** - Single file, works anywhere
* **No Installation** - Just open in browser
* **Offline Capable** - Works without internet (after first CDN load)
* **Universal** - Any platform with a web browser

Over Commercial Tools
---------------------

* **Free and Open Source** - No licensing costs
* **Customizable** - Source code available for modifications
* **Standard Format** - Uses UCIS standard
* **Integration Friendly** - Easy to incorporate into CI/CD

Limitations
===========

The HTML format has some limitations:

* **Read-Only** - Cannot modify coverage data (use UCIS tools for that)
* **No Real-Time Updates** - Static snapshot at generation time
* **CDN Dependency** - Requires internet for first load (libraries can be inlined if needed)
* **Browser Required** - Cannot view from command line (use text format instead)
* **Large Data** - Very large databases (100MB+) may load slowly in browser

For these cases, consider:

* **JSON format** - For programmatic processing
* **SQLite format** - For querying with SQL
* **Text format** - For command-line viewing
* **XML format** - For tool interchange

Advanced Options
================

Compression
-----------

For large databases, enable compression:

.. code-block:: python

    formatter = HtmlFormatter(compress=True)

Data is compressed using gzip and encoded as base64, typically reducing size by 5-10x. Note: Decompression in browser is not yet implemented, so compressed reports will show a warning message.

Theming
-------

Choose light or dark theme:

.. code-block:: python

    formatter = HtmlFormatter(theme='light')  # or 'dark'

Currently only light theme is fully implemented.

Customization
-------------

The HTML formatter is designed to be extensible:

* **Custom CSS** - Modify ``_get_css()`` method to change styles
* **Additional Views** - Add new tabs/views in ``_render_template()``
* **Custom Charts** - Add D3.js visualizations in ``_get_javascript()``
* **Data Preprocessing** - Modify ``_build_coverage_data()`` to include additional fields

See ``src/ucis/formatters/format_html.py`` for implementation details.

Examples
========

Basic Usage
-----------

.. code-block:: bash

    # Generate report from XML
    pyucis report coverage.xml -of html -o report.html
    
    # Open in default browser
    xdg-open report.html  # Linux
    open report.html      # macOS
    start report.html     # Windows

CI/CD Integration
-----------------

.. code-block:: bash

    #!/bin/bash
    # Generate coverage report in CI pipeline
    
    # Run tests and collect coverage
    run_tests.sh
    
    # Generate HTML report
    pyucis report coverage.ucis -of html -o coverage_report.html
    
    # Archive as build artifact
    cp coverage_report.html $ARTIFACTS_DIR/
    
    # Or publish to web server
    scp coverage_report.html user@server:/var/www/coverage/

Python Script
-------------

.. code-block:: python

    #!/usr/bin/env python3
    """Generate HTML coverage report with custom filtering."""
    
    from ucis import UCIS
    from ucis.formatters.format_html import HtmlFormatter
    
    # Load database
    db = UCIS.load("coverage.ucis")
    
    # Generate report
    formatter = HtmlFormatter(
        include_source=True,
        compress=False,
        theme='light'
    )
    
    with open("coverage_report.html", "w") as f:
        formatter.format(db, f)
    
    print("✓ HTML report generated: coverage_report.html")
    print("  Open in browser to view interactive report")

API Reference
=============

.. autoclass:: ucis.formatters.format_html.HtmlFormatter
   :members: __init__, format
   :member-order: bysource

Constructor Parameters
----------------------

.. py:method:: __init__(include_source=True, compress=False, theme='light')

   Initialize HTML formatter.
   
   :param bool include_source: Include source file information in report (default: True)
   :param bool compress: Compress JSON data with gzip (default: False, not fully implemented)
   :param str theme: UI theme - 'light' or 'dark' (default: 'light', dark theme not fully implemented)

Format Method
-------------

.. py:method:: format(db, output)

   Generate HTML report from UCIS database.
   
   :param db: UCIS database object (any backend)
   :param output: Output file handle or stream (must be writable)
   :raises Exception: If database cannot be read or output cannot be written
   
   Example::
   
       from ucis import UCIS
       from ucis.formatters.format_html import HtmlFormatter
       
       db = UCIS.load("coverage.xml")
       formatter = HtmlFormatter()
       
       with open("report.html", "w") as f:
           formatter.format(db, f)

See Also
========

* :doc:`json-report-format` - Coverage report data structure and JSON format specification
* :doc:`../formats/xml-interchange` - XML format for interchange
* :doc:`../formats/yaml-format` - YAML human-readable format
