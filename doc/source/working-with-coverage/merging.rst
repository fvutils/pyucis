###############
Merging Coverage
###############

Coverage from multiple test runs must be merged into a single database before
you can report on the full regression. Use ``ucis merge``:

.. code-block:: bash

    ucis merge -o merged.xml test1.xml test2.xml test3.xml

Common Options
==============

``--input-format`` / ``-if``
    Source format. Specify once and it applies to all inputs.
    Defaults to ``xml``. Use ``vltcov``, ``cocotb-xml``, etc. to merge
    directly from simulator output without a prior convert step.

    .. code-block:: bash

        ucis merge --input-format vltcov -o merged.xml \
            test1/coverage.dat test2/coverage.dat

``--output-format`` / ``-of``
    Output format. Defaults to ``xml``. Use ``sqlite`` for large
    regressions — it is faster to query and supports the ``--fast`` path.

    .. code-block:: bash

        ucis merge --output-format sqlite -o merged.ucisdb \
            test1.xml test2.xml test3.xml

``--fast``
    **SQLite-to-SQLite only.** Bypasses the in-memory model and merges
    directly at the database level. Significantly faster for large regressions.
    Requires both inputs and output to be SQLite format.

    .. code-block:: bash

        ucis merge --input-format sqlite --output-format sqlite --fast \
            -j 8 -o merged.ucisdb tests/*.ucisdb

``-j`` / ``--workers``
    Number of parallel reader threads for ``--fast`` merge (default: 4).

``--squash-history``
    Collapse per-test history nodes into a single summary. Useful when
    you do not need per-test attribution in the merged result.

NCDB — Fast, Compact Merging
==============================

For large regressions the **NCDB** format offers the best merge performance
and the smallest disk footprint (typically 100–200× smaller than SQLite).
Use ``ncdb`` as the output format to accumulate per-test ``.cdb`` files:

.. code-block:: bash

    # Per-test run (simulator writes NCDB directly, or convert after)
    ucis convert -if sqlite -of ncdb -o test_42.cdb test_42.ucisdb

    # Merge all per-test NCDB files into one
    ucis merge --input-format ncdb --output-format ncdb \
        -o regression.cdb tests/test_*.cdb

When all input files share the same scope-tree structure (same design, same
elaboration), NCDB uses a *same-schema fast-merge* path that reduces the
merge to element-wise integer addition over a flat array — no SQL overhead,
no scope-tree parsing.  See :doc:`../reference/formats/ncdb-format` for the
technical details.

**When to choose NCDB vs SQLite:**

* **NCDB** — continuous integration, large seed sweeps, any scenario where
  disk space and merge speed matter.
* **SQLite** — when you need to query coverage via SQL, or when third-party
  tools require a SQLite ``.cdb``.

Typical Regression Workflow
============================

.. code-block:: bash

    # 1. Run tests (each produces a coverage file)
    make run_all_tests   # produces test_*.xml

    # 2. Merge
    ucis merge -o regression.xml test_*.xml

    # 3. Explore or report
    ucis view regression.xml
    ucis report regression.xml -of html -o regression_report.html

Next Steps
==========

* :doc:`exploring-tui` — interactively explore the merged database
* :doc:`analyzing` — summarize, find gaps, identify hotspots
* :doc:`../reporting/html-report` — generate a shareable HTML report
