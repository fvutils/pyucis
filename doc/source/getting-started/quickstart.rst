##########
Quickstart
##########

This page walks through the most common workflow: import a coverage file from your
simulator, explore it interactively, then generate a shareable HTML report.

Step 1 — Import
===============

Convert your simulator's native coverage output to UCIS XML:

.. tab-set::

   .. tab-item:: Verilator

      .. code-block:: bash

          ucis convert --input-format vltcov coverage.dat -o coverage.xml

   .. tab-item:: cocotb-coverage

      .. code-block:: bash

          ucis convert --input-format cocotb-xml coverage.xml -o coverage_ucis.xml
          # or for YAML output from cocotb-coverage:
          ucis convert --input-format cocotb-yaml coverage.yml -o coverage_ucis.xml

   .. tab-item:: AVL

      .. code-block:: bash

          ucis convert --input-format avl-json coverage.json -o coverage.xml

See :doc:`../importing/index` for more detail on each source.

Step 2 — Explore Interactively
===============================

The interactive terminal UI lets you browse coverage without generating a report file:

.. code-block:: bash

    ucis view coverage.xml

Inside the TUI:

* Press **1** for a Dashboard overview
* Press **3** to see uncovered items (Gaps)
* Press **4** for prioritized recommendations (Hotspots)
* Press **q** to quit

See :doc:`../working-with-coverage/exploring-tui` for the full TUI guide.

Step 3 — Generate a Shareable Report
=====================================

.. code-block:: bash

    ucis report coverage.xml -of html -o report.html

Open ``report.html`` in any browser — it is a single self-contained file that can
be emailed, archived, or hosted on a web server without any extra dependencies.

Step 4 — Merge Multiple Runs (optional)
========================================

If you have coverage from several test runs, merge them before reporting:

.. code-block:: bash

    ucis merge -o merged.xml test1.xml test2.xml test3.xml
    ucis report merged.xml -of html -o merged_report.html

Next Steps
==========

* :doc:`../importing/index` — more on importing from different sources
* :doc:`../working-with-coverage/analyzing` — analyze gaps and hotspots from the CLI
* :doc:`../reporting/exporting` — export to LCOV, Cobertura, or JaCoCo for CI/CD tools
* :doc:`../cicd/index` — ready-to-use CI/CD pipeline examples
