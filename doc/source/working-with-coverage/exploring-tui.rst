############################
Exploring Coverage with TUI
############################

The ``ucis view`` command launches an interactive Terminal UI (TUI) for browsing
coverage data without generating a report file. It works over SSH, requires no
browser, and starts instantly.

.. code-block:: bash

    ucis view coverage.xml
    ucis view coverage.ucisdb   # SQLite loads faster for large databases

Quick Assessment (2–3 minutes)
================================

1. Launch the TUI and check the **Dashboard** (press **1**) — overall percentage
   and per-type breakdown.
2. Press **3** (Gaps) to see every item below 100% coverage, sorted by priority.
3. Press **4** (Hotspots) for algorithmic recommendations on where to focus next.
4. Press **q** to quit.

The Five Views
==============

Press the number key at any time to switch views.

**1 — Dashboard**
    Overall coverage percentage, counts by type (covergroups, coverpoints, bins,
    assertions, toggles, branches, statements), and color-coded status indicators.

**2 — Hierarchy**
    Expandable tree of the design hierarchy. Use arrow keys to navigate.
    Each node shows its coverage percentage and color.

    * ``→`` / ``Enter`` — expand node
    * ``←`` — collapse node
    * ``↑`` / ``↓`` (or ``k`` / ``j``) — move up/down

**3 — Gaps**
    Filtered list of all items below 100% coverage, lowest first.
    Shows item name, type, percentage, and full path.

**4 — Hotspots**
    Priority-ordered recommendations:

    * **P0** (red) — modules below 50%, needs immediate attention
    * **P1** (yellow) — completely untested coverpoints (0%) or near-complete
      items (≥90%, easy wins)
    * **P2** (blue) — other partially covered items

**5 — Metrics**
    Statistical analysis: hit-count distribution histogram, mean/median/stddev,
    coverage tier breakdown (complete / high / medium / low), bin utilization rate.

Global Keys
===========

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Key
     - Action
   * - ``1`` – ``5``
     - Switch view
   * - ``?``
     - Help overlay
   * - ``q`` / ``Ctrl+C``
     - Quit

TUI vs. HTML Reports
====================

Use the TUI for quick interactive checks during active verification.
Use :doc:`../reporting/html-report` when you need a shareable artifact.

Remote Use
==========

The TUI works well over SSH. Enable compression for better responsiveness:

.. code-block:: bash

    ssh -C user@build-server
    ucis view /path/to/regression.ucisdb

Tips
====

* **Use SQLite** — convert XML to SQLite first for large databases:
  ``ucis convert --input-format xml --output-format sqlite coverage.xml -o coverage.ucisdb``
* Press ``?`` inside the TUI for a full keyboard reference overlay.
