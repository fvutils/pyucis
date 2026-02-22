##################################
Importing AVL Coverage Data
##################################

`AVL (Apheleia Verification Library) <https://github.com/projectapheleia/avl>`_
exports functional coverage as JSON. PyUCIS automatically detects which of the
three AVL JSON variants is present (hierarchical, DataFrame records, DataFrame table).

Basic Import
============

.. code-block:: bash

    ucis convert --input-format avl-json coverage.json -o coverage.xml

Merging Multiple Runs
=====================

.. code-block:: bash

    ucis merge --input-format avl-json \
        run1.json run2.json run3.json -o merged.xml

Exporting Coverage from AVL
============================

In your AVL testbench:

.. code-block:: python

    # Hierarchical format (recommended)
    cg.export_json("coverage.json")

    # DataFrame format (also supported)
    cg.export_dataframe("coverage_df.json")

Coverage Types Supported
========================

* Covergroups and coverpoints
* Bins with hit counts
* Cross coverage

Next Steps
==========

* :doc:`../working-with-coverage/merging` — combine runs
* :doc:`../working-with-coverage/analyzing` — analyze from the CLI
* :doc:`../reporting/html-report` — HTML report
