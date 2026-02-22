##########################
Comparing Coverage Databases
##########################

``ucis show compare`` compares two coverage databases and reports what changed.
Use it in nightly regressions to detect coverage regressions before they
accumulate.

Basic Usage
===========

.. code-block:: bash

    ucis show compare baseline.xml current.xml

Output (text format) shows:

* Items whose coverage **increased**
* Items whose coverage **decreased** (regressions)
* New items present in ``current`` but absent from ``baseline``
* Removed items present in ``baseline`` but absent from ``current``
* Bin-level changes for any changed coverpoint

JSON Output
===========

.. code-block:: bash

    ucis show compare baseline.xml current.xml --output-format json \
        | jq '.regressions'

Typical Regression Integration
===============================

Save the previous run's database as the baseline, then compare after each run:

.. code-block:: bash

    # After tests pass
    cp regression.xml regression_baseline.xml
    make run_all_tests
    ucis merge -o regression.xml test_*.xml

    # Check for regressions
    ucis show compare regression_baseline.xml regression.xml

For a full CI/CD example see :doc:`../cicd/github-actions`.

Next Steps
==========

* :doc:`../reporting/html-report` — generate a detailed visual report
* :doc:`../cicd/index` — automate comparison in your pipeline
