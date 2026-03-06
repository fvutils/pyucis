.. _reports:

#############################
Reports and CI/CD Integration
#############################

The :mod:`ucis.ncdb.reports` and :mod:`ucis.ncdb.testplan_export` modules
provide structured reports for testplan closure, regression delta, and
CI/CD export.  Every report function returns a typed dataclass with a
``to_json()`` method; companion ``format_*()`` functions render the
dataclass to human-readable text.

.. contents:: On this page
   :local:
   :depth: 2

-----------

**********************
Closure and gate reports
**********************

.. code-block:: python

    from ucis.ncdb.ncdb_ucis import NcdbUCIS
    from ucis.ncdb.testplan import get_testplan
    from ucis.ncdb.testplan_closure import compute_closure
    from ucis.ncdb.reports import (
        report_testpoint_closure,
        format_testpoint_closure,
        report_stage_gate,
        format_stage_gate,
    )

    db = NcdbUCIS("coverage.cdb")
    plan = get_testplan(db)
    results = compute_closure(plan, db)

    # Print the closure table
    summary = report_testpoint_closure(results)
    print(format_testpoint_closure(summary))

    # Evaluate a stage gate
    gate = report_stage_gate(results, "V2", plan)
    print(format_stage_gate(gate))

    # Machine-readable JSON
    import json
    data = json.loads(summary.to_json())

Stage-rollup output example::

    Testpoint                          Stage  Status     Pass   Fail
    ----------------------------------------------------------------
    uart_reset                         V1     ✓ CLOSED      5      0
    uart_loopback                      V2     ✗ FAILING     0      3
    ----------------------------------------------------------------

    Stage roll-up:
      V1     [████████████████████] 1/1 (100.0%)
      V2     [░░░░░░░░░░░░░░░░░░░░] 0/1 (0.0%)

    Total: 1/2 closed  (0 N/A)

-----------

**********************
Regression delta
**********************

Compare two closure result sets to find testpoints that changed
status between runs::

    from ucis.ncdb.reports import report_regression_delta, format_regression_delta

    # Load two snapshots
    results_baseline = compute_closure(plan, db_baseline)
    results_current  = compute_closure(plan, db_current)

    delta = report_regression_delta(results_current, results_baseline)
    print(format_regression_delta(delta))
    # Regression delta: +1 closed, -0 newly failing, 1 still open

    # Machine-readable
    print(delta.to_json())

-----------

**********************
Reliability report
**********************

Compute per-testpoint flake scores from v2 history data::

    from ucis.ncdb.reports import report_testpoint_reliability, format_testpoint_reliability

    report = report_testpoint_reliability(results, db)
    print(format_testpoint_reliability(report))

Output example::

    Testpoint                          Flake    Pass    Fail
    --------------------------------------------------------
    uart_loopback                      0.800       2       8  ⚠
    uart_reset                         0.000      10       0

-----------

**********************
Unexercised covergroups
**********************

Identify zero-hit or low-coverage covergroups::

    from ucis.ncdb.reports import (
        report_unexercised_covergroups,
        format_unexercised_covergroups,
    )

    report = report_unexercised_covergroups(db, plan, low_threshold=50.0)
    print(format_unexercised_covergroups(report))

-----------

**********************
Coverage contribution
**********************

Show which tests contribute the most unique coverage bins
(requires v2 history with contribution data)::

    from ucis.ncdb.reports import (
        report_coverage_contribution,
        format_coverage_contribution,
    )

    report = report_coverage_contribution(db)
    print(format_coverage_contribution(report))

-----------

**********************
JUnit XML export
**********************

Export closure results as a JUnit XML file for CI dashboards::

    from ucis.ncdb.testplan_export import export_junit_xml

    export_junit_xml(results, "closure_results.xml")

Or via the CLI::

    pyucis testplan export-junit coverage.cdb --out closure_results.xml

The XML maps each testpoint to a ``<testcase>`` element.  FAILING and
PARTIAL testpoints become ``<failure>`` elements; NOT_RUN becomes
``<skipped>``.

-----------

**********************
GitHub Annotations
**********************

Emit GitHub Actions `workflow commands`_ for inline PR annotations::

    from ucis.ncdb.testplan_export import export_github_annotations

    export_github_annotations(results)  # writes to stdout

    # Or capture to a string
    import io
    buf = io.StringIO()
    export_github_annotations(results, output=buf)
    print(buf.getvalue())

In a GitHub Actions workflow::

    - name: Compute closure
      run: |
        python -c "
        from ucis.ncdb.ncdb_ucis import NcdbUCIS
        from ucis.ncdb.testplan import get_testplan
        from ucis.ncdb.testplan_closure import compute_closure
        from ucis.ncdb.testplan_export import export_github_annotations
        db = NcdbUCIS('coverage.cdb')
        plan = get_testplan(db)
        results = compute_closure(plan, db)
        export_github_annotations(results)
        "

.. _workflow commands: https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/workflow-commands-for-github-actions

-----------

**********************
GitHub Step Summary
**********************

Write a markdown table to ``$GITHUB_STEP_SUMMARY``::

    import os
    from ucis.ncdb.testplan_export import export_summary_markdown

    md = export_summary_markdown(results, stage_gate=gate)
    with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
        f.write(md)

The output includes a stage roll-up table, per-testpoint status rows,
and (when *stage_gate* is supplied) a gate verdict with a list of
blocking testpoints.

-----------

**********************
API reference
**********************

.. autofunction:: ucis.ncdb.reports.report_testpoint_closure
.. autofunction:: ucis.ncdb.reports.format_testpoint_closure
.. autoclass:: ucis.ncdb.reports.ClosureSummary

.. autofunction:: ucis.ncdb.reports.report_stage_gate
.. autofunction:: ucis.ncdb.reports.format_stage_gate
.. autoclass:: ucis.ncdb.reports.StageGateReport

.. autofunction:: ucis.ncdb.reports.report_regression_delta
.. autofunction:: ucis.ncdb.reports.format_regression_delta
.. autoclass:: ucis.ncdb.reports.RegressionDelta

.. autofunction:: ucis.ncdb.reports.report_testpoint_reliability
.. autofunction:: ucis.ncdb.reports.format_testpoint_reliability
.. autoclass:: ucis.ncdb.reports.TestpointReliability

.. autofunction:: ucis.ncdb.reports.report_unexercised_covergroups
.. autofunction:: ucis.ncdb.reports.format_unexercised_covergroups
.. autoclass:: ucis.ncdb.reports.UnexercisedCovergroups

.. autofunction:: ucis.ncdb.reports.report_coverage_contribution
.. autofunction:: ucis.ncdb.reports.format_coverage_contribution
.. autoclass:: ucis.ncdb.reports.CoverageContribution

.. autofunction:: ucis.ncdb.testplan_export.export_junit_xml
.. autofunction:: ucis.ncdb.testplan_export.export_github_annotations
.. autofunction:: ucis.ncdb.testplan_export.export_summary_markdown

.. seealso::

   * :ref:`testplan` — Testplan format and closure computation
   * :ref:`test-history` — Binary test history API
