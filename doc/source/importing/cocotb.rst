################################
Importing cocotb-coverage Data
################################

`cocotb-coverage <https://github.com/mciepluc/cocotb-coverage>`_ can export
functional coverage in XML or YAML format. PyUCIS imports both, producing an
identical UCIS database from either.

Basic Import
============

.. tab-set::

   .. tab-item:: XML

      .. code-block:: bash

          ucis convert --input-format cocotb-xml coverage.xml -o coverage_ucis.xml

   .. tab-item:: YAML

      .. code-block:: bash

          ucis convert --input-format cocotb-yaml coverage.yml -o coverage_ucis.xml

Merging Multiple Runs
=====================

.. code-block:: bash

    ucis merge --input-format cocotb-xml \
        run1.xml run2.xml run3.xml -o merged.xml

Exporting Coverage from cocotb-coverage
========================================

In your cocotb testbench, after sampling:

.. code-block:: python

    from cocotb_coverage.coverage import coverage_db

    # Export at end of test
    coverage_db.export_to_xml("coverage.xml")
    # or
    coverage_db.export_to_yaml("coverage.yml")

Coverage Types Supported
========================

* Covergroups and coverpoints
* Cross coverage
* Bins with hit counts and ``at_least`` thresholds

Next Steps
==========

* :doc:`../working-with-coverage/merging` — combine runs
* :doc:`../working-with-coverage/analyzing` — analyze from the CLI
* :doc:`../reporting/html-report` — HTML report
