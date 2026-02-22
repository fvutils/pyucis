################################
Exporting to CI/CD Formats
################################

``ucis show code-coverage`` exports code coverage data in industry-standard
formats that are consumed by CI/CD platforms and code-quality tools.

Format Overview
===============

.. list-table::
   :header-rows: 1
   :widths: 20 45 35

   * - Format
     - Consumed by
     - Command flag
   * - **LCOV**
     - genhtml, Codecov, Coveralls, GitLab CI
     - ``--output-format lcov``
   * - **Cobertura**
     - Jenkins, GitLab CI, SonarQube, Azure DevOps
     - ``--output-format cobertura``
   * - **JaCoCo**
     - Maven, Gradle, SonarQube, Bamboo
     - ``--output-format jacoco``
   * - **Clover**
     - Bamboo, Jenkins (Clover plugin), IntelliJ
     - ``--output-format clover``

Usage
=====

.. code-block:: bash

    # LCOV
    ucis show code-coverage coverage.xml --output-format lcov > coverage.info

    # Cobertura
    ucis show code-coverage coverage.xml --output-format cobertura > coverage.xml

    # JaCoCo
    ucis show code-coverage coverage.xml --output-format jacoco > jacoco.xml

    # Clover
    ucis show code-coverage coverage.xml --output-format clover > clover.xml

The command reads any UCIS database format (XML, SQLite, YAML) via
``--input-format``.

Choosing a Format
=================

* If you use **Codecov or Coveralls**, use LCOV.
* If you use **Jenkins** with the Cobertura plugin, use Cobertura.
* If you use **SonarQube**, Cobertura and JaCoCo are both supported; check your
  scanner configuration.
* If you use **Bamboo**, use Clover.
* If you are unsure, Cobertura has the broadest tool support.

For complete per-platform pipeline examples see :doc:`../cicd/index`.

See :doc:`../reference/cli` for the full ``show code-coverage`` option reference.
