##########################
Importing Verilator Coverage
##########################

Verilator writes coverage data in the **SystemC::Coverage-3** text format
(usually ``coverage.dat``). PyUCIS imports both functional coverage
(covergroups, coverpoints, bins) and code coverage (line, branch, toggle).

Basic Import
============

.. code-block:: bash

    ucis convert --input-format vltcov coverage.dat -o coverage.xml

To convert directly to an SQLite database (faster for large files):

.. code-block:: bash

    ucis convert --input-format vltcov --output-format sqlite \
        coverage.dat -o coverage.ucisdb

Merging Multiple Runs
=====================

.. code-block:: bash

    ucis merge --input-format vltcov \
        test1/coverage.dat test2/coverage.dat test3/coverage.dat \
        -o merged.xml

Generating Verilator Coverage
==============================

Enable coverage when compiling and running your simulation:

.. code-block:: bash

    # Compile with coverage instrumentation
    verilator --coverage --coverage-func --coverage-line -cc design.v

    # Run (generates coverage.dat in the working directory)
    make -C obj_dir -f Vdesign.mk
    ./obj_dir/Vdesign

Next Steps
==========

* :doc:`../working-with-coverage/merging` — combine runs into a single database
* :doc:`../working-with-coverage/exploring-tui` — explore coverage interactively
* :doc:`../reporting/html-report` — generate an HTML report
