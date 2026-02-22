##########
GitLab CI
##########

The example below shows a complete coverage workflow for GitLab CI: merge
coverage, export Cobertura for the GitLab coverage visualization, and publish
an HTML report as a job artifact.

Full Workflow Example
=====================

.. code-block:: yaml

    stages:
      - test
      - coverage

    run_tests:
      stage: test
      script:
        - make run_all_tests   # produces test_*.xml
      artifacts:
        paths:
          - test_*.xml

    coverage:
      stage: coverage
      script:
        - pip install pyucis

        # Merge
        - ucis merge -o merged.xml test_*.xml

        # Coverage gate
        - |
          COV=$(ucis show summary merged.xml -of json | jq -r '.overall_coverage')
          echo "Coverage: ${COV}%"
          python3 -c "import sys; sys.exit(0 if float('$COV') >= 80 else 1)" \
            || (echo "Coverage below 80%" && exit 1)

        # Export Cobertura for GitLab coverage widget
        - ucis show code-coverage merged.xml --output-format cobertura > coverage.xml

        # Generate shareable HTML report
        - ucis report merged.xml -of html -o coverage_report.html

      coverage: '/Coverage:\s+(\d+\.\d+)%/'

      artifacts:
        reports:
          coverage_report:
            coverage_format: cobertura
            path: coverage.xml
        paths:
          - coverage_report.html
        expire_in: 1 week

Verilator Projects
==================

.. code-block:: yaml

    - ucis merge --input-format vltcov -o merged.xml tests/*/coverage.dat
