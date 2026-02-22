######################
Analyzing Coverage
######################

The ``ucis show`` sub-commands extract coverage data from any UCIS database
and print it in text or JSON format. Use them for quick checks, scripting,
and CI/CD gates.

Recommended Workflow
====================

Work through these commands in order for an efficient analysis session:

1. Get an overall health check
2. Find what is not covered
3. Prioritize where to work next
4. Drill down into specific items

Step 1 — Summary
================

.. code-block:: bash

    ucis show summary coverage.xml

Prints overall coverage percentage and a breakdown by type (functional, code,
assertion, toggle). Add ``--output-format json`` for machine-readable output:

.. code-block:: bash

    ucis show summary coverage.xml --output-format json | jq '.overall_coverage'

Step 2 — Gaps
=============

.. code-block:: bash

    ucis show gaps coverage.xml

Lists every item below 100% coverage. Use ``--threshold`` to show only items
below a specific percentage, and ``--limit`` to cap the output:

.. code-block:: bash

    ucis show gaps coverage.xml --threshold 80 --limit 20

Step 3 — Hotspots
=================

.. code-block:: bash

    ucis show hotspots coverage.xml

Provides prioritized recommendations (P0/P1/P2) based on coverage percentage
and potential impact. The ``--target`` option sets the goal:

.. code-block:: bash

    ucis show hotspots coverage.xml --target 90

Step 4 — Drill Down
===================

.. rubric:: Covergroups

.. code-block:: bash

    ucis show covergroups coverage.xml
    ucis show covergroups coverage.xml --pattern "alu_*"

.. rubric:: Bins

.. code-block:: bash

    ucis show bins coverage.xml --covergroup addr_cg
    ucis show bins coverage.xml --status missed   # only uncovered bins

.. rubric:: Tests

.. code-block:: bash

    ucis show tests coverage.xml

Shows per-test pass/fail status and test-specific coverage contribution.

.. rubric:: Hierarchy

.. code-block:: bash

    ucis show hierarchy coverage.xml --depth 3

.. rubric:: Assertions and Toggle

.. code-block:: bash

    ucis show assertions coverage.xml
    ucis show toggle coverage.xml

Other Options
=============

All ``show`` commands accept:

* ``--output-format`` / ``-of`` — ``json``, ``text`` (default varies by command)
* ``--out`` / ``-o`` — write output to a file instead of stdout
* ``--input-format`` / ``-if`` — source format (default: ``xml``)

Coverage Gate Script
====================

Check whether coverage meets a threshold in CI/CD:

.. code-block:: bash

    #!/bin/bash
    COVERAGE=$(ucis show summary coverage.xml -of json | jq -r '.overall_coverage')
    THRESHOLD=80
    if (( $(echo "$COVERAGE < $THRESHOLD" | bc -l) )); then
        echo "Coverage ${COVERAGE}% is below ${THRESHOLD}%"
        exit 1
    fi

See the full parameter reference in :doc:`../reference/cli`.

Next Steps
==========

* :doc:`comparing` — compare two databases to detect regressions
* :doc:`../reporting/exporting` — export to LCOV, Cobertura, JaCoCo, or Clover
* :doc:`../cicd/index` — ready-to-use CI/CD pipeline examples
