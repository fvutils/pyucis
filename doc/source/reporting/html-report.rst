#####################
Interactive HTML Report
#####################

``ucis report -of html`` generates a **single self-contained HTML file** with
interactive charts, expandable hierarchy, and bin-level details. It can be
opened in any modern browser and shared via email or file hosting — no web
server required.

Generating
==========

.. code-block:: bash

    ucis report coverage.xml -of html -o report.html

Open ``report.html`` directly in a browser.

Report Features
===============

* **Coverage summary** — overall percentage with a pie/bar chart breakdown by type
* **Expandable hierarchy** — tree view of design units and instances; click to expand
* **Coverpoint bin details** — hit counts, goal, and hit/miss status per bin
* **Search and filter** — filter the hierarchy by name or coverage level
* **Self-contained** — all JavaScript and styles are embedded in the single file

Sharing
=======

Because the report is a single file it is easy to:

* Attach to a pull request or email
* Publish as a CI/CD artifact (e.g. GitHub Actions ``upload-artifact``)
* Archive alongside the test results

.. code-block:: yaml

    # GitHub Actions example — publish the report as an artifact
    - name: Generate HTML report
      run: ucis report merged.xml -of html -o coverage_report.html

    - uses: actions/upload-artifact@v4
      with:
        name: coverage-report
        path: coverage_report.html

Generating from SQLite
======================

SQLite databases load faster for large regressions:

.. code-block:: bash

    ucis report coverage.ucisdb -of html -o report.html

See :doc:`../reference/report-formats/html-report-format` for the full technical
specification of the HTML report format.

Next Steps
==========

* :doc:`exporting` — export to CI/CD tool formats
* :doc:`../cicd/github-actions` — publish reports in GitHub Actions
