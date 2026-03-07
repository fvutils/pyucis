.. _testplan:

####################
Testplan Integration
####################

PyUCIS can embed a structured *testplan* inside each NCDB ``.cdb`` file.
A testplan describes the verification tasks (testpoints) and functional
coverage groups expected for a design.  Together with the binary test
history (see :ref:`test-history`) it enables:

* **Closure reporting** — did every testpoint's tests actually pass?
* **Stage gate evaluation** — are all V1/V2/V3 testpoints closed?
* **Merge propagation** — the testplan travels with the database so
  reports always use the correct plan.

.. contents:: On this page
   :local:
   :depth: 2

-----------

**********************
Quick-start
**********************

Import an OpenTitan-style Hjson testplan and embed it in a ``.cdb``::

    from ucis.ncdb.testplan_hjson import import_hjson
    from ucis.ncdb.ncdb_ucis import NcdbUCIS
    from ucis.ncdb.ncdb_writer import NcdbWriter

    plan = import_hjson("uart_testplan.hjson",
                        substitutions={"baud": ["9600", "115200"]})

    db = NcdbUCIS("coverage.cdb")
    db.setTestplan(plan)
    NcdbWriter().write(db, "coverage.cdb")

Compute closure against the embedded testplan::

    from ucis.ncdb.testplan_closure import compute_closure, stage_gate_status
    from ucis.ncdb.testplan import get_testplan

    db = NcdbUCIS("coverage.cdb")
    plan = db.getTestplan()
    results = compute_closure(plan, db)

    for r in results:
        print(f"{r.testpoint.name:30s} {r.status.value}")

    gate = stage_gate_status(results, "V2", plan)
    print(gate["message"])

-----------

**********************
Testplan format
**********************

A testplan is stored as ``testplan.json`` inside the NCDB ZIP and is also
exportable as a standalone JSON file.  The schema is::

    {
      "format_version": 1,
      "source_file": "path/to/uart.hjson",
      "import_timestamp": "2025-01-01T00:00:00+00:00",
      "testpoints": [
        {
          "name": "uart_reset",
          "stage": "V1",
          "desc": "Verify reset behaviour",
          "tests": ["uart_smoke", "uart_init_*"],
          "tags": ["smoke"],
          "na": false,
          "source_template": ""
        }
      ],
      "covergroups": [
        {"name": "cg_uart_reset", "desc": "Reset coverage"}
      ]
    }

Stages follow the OpenTitan V1 → V2 → V2S → V3 hierarchy; custom strings
are also accepted and sort after V3 in gate evaluation.

-----------

**********************
Importing Hjson
**********************

Use :func:`~ucis.ncdb.testplan_hjson.import_hjson` to parse an OpenTitan
``.hjson`` testplan (or a standard ``.json`` file)::

    plan = import_hjson(
        "uart_testplan.hjson",
        substitutions={
            "uart":  ["uart0", "uart1"],
            "mode":  ["loopback", "normal"],
        },
    )

The ``substitutions`` dict provides values for ``{key}`` placeholders in
test name templates.  A list value generates the cartesian product of all
combinations::

    # Template: "{uart}_{mode}_test"
    # Substitutions: uart=["uart0","uart1"], mode=["loopback","normal"]
    # Expands to: uart0_loopback_test, uart0_normal_test,
    #             uart1_loopback_test, uart1_normal_test

Tests listed as ``["N/A"]`` are treated as intentionally unmapped
(``testpoint.na = True``).

-----------

**********************
Closure computation
**********************

:func:`~ucis.ncdb.testplan_closure.compute_closure` evaluates each
testpoint against the test history stored in the database:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Status
     - Meaning
   * - ``CLOSED``
     - All mapped tests have at least one passing run
   * - ``PARTIAL``
     - Some passing, some failing
   * - ``FAILING``
     - All mapped tests failed
   * - ``NOT_RUN``
     - None of the mapped tests appear in the database
   * - ``N/A``
     - Testpoint has ``na = True``
   * - ``UNIMPLEMENTED``
     - Testpoint has an empty ``tests`` list

Test name matching uses three strategies in order:

1. **Exact** — the test name appears literally in ``testpoint.tests``.
2. **Seed-suffix strip** — trailing ``_\d+`` is removed and the result
   matched exactly (e.g. ``uart_smoke_42`` → ``uart_smoke``).
3. **Wildcard** — any ``testpoint.tests`` entry ending in ``_*`` is used
   as a prefix match.

-----------

**********************
Stage gate evaluation
**********************

:func:`~ucis.ncdb.testplan_closure.stage_gate_status` determines whether
a regression is ready to advance to the next stage::

    gate = stage_gate_status(results, "V2", plan)
    if gate["passed"]:
        print("Ready to tape-out!")
    else:
        for r in gate["blocking"]:
            print(f"  BLOCKING: {r.testpoint.name}")

The gate passes when all testpoints at the target stage **and all stages
below it** (V1 < V2 < V2S < V3) are CLOSED or N/A.

-----------

**********************
Waivers
**********************

Coverage and test failures can be suppressed with a
:class:`~ucis.ncdb.waivers.WaiverSet`::

    from ucis.ncdb.waivers import Waiver, WaiverSet

    ws = WaiverSet([
        Waiver(
            id="W-001",
            scope_pattern="top/uart/**",
            bin_pattern="reset_*",
            rationale="Reset coverage deferred to V2",
            approver="eng",
            approved_at="2025-01-01T00:00:00",
            expires_at="2026-01-01T00:00:00",
        )
    ])

    db.setWaivers(ws)
    NcdbWriter().write(db, "coverage.cdb")

Scope patterns use glob syntax: ``*`` matches a single path segment,
``**`` matches any number of segments.  Expiry enforcement is the
caller's responsibility — use :meth:`~ucis.ncdb.waivers.WaiverSet.active_at`
to filter out expired waivers before passing to closure::

    import time
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    active_waivers = ws.active_at(now)

-----------

**********************
Modes A and B
**********************

**Mode A (embedded)** — testplan stored inside the ``.cdb``::

    db.setTestplan(plan)
    NcdbWriter().write(db, "coverage.cdb")

    # Read back — travels with the database
    db2 = NcdbUCIS("coverage.cdb")
    plan2 = db2.getTestplan()

**Mode B (standalone)** — testplan kept as a separate file::

    plan.save("uart_testplan_snapshot.json")

    # Load later and pass to analysis functions
    plan = Testplan.load("uart_testplan_snapshot.json")
    results = compute_closure(plan, db)

Both modes produce the same :class:`~ucis.ncdb.testplan.Testplan` object.
The helper :func:`~ucis.ncdb.testplan.get_testplan` works with both::

    from ucis.ncdb.testplan import get_testplan
    plan = get_testplan(db)   # works for NcdbUCIS or MemUCIS

-----------

**********************
API reference
**********************

.. autofunction:: ucis.ncdb.testplan_hjson.import_hjson
.. autoclass:: ucis.ncdb.testplan.Testplan
   :members: getTestpoint, testpointForTest, testpointsForStage, stages,
             add_testpoint, serialize, from_bytes, load, save, stamp_import_time
.. autoclass:: ucis.ncdb.testplan.Testpoint
.. autoclass:: ucis.ncdb.testplan.CovergroupEntry
.. autoclass:: ucis.ncdb.testplan.RequirementLink
.. autofunction:: ucis.ncdb.testplan_closure.compute_closure
.. autofunction:: ucis.ncdb.testplan_closure.stage_gate_status
.. autoclass:: ucis.ncdb.testplan_closure.TPStatus
.. autoclass:: ucis.ncdb.testplan_closure.TestpointResult
.. autoclass:: ucis.ncdb.waivers.WaiverSet
   :members: add, matches_scope, active_at, get, serialize, from_bytes, load, save
.. autoclass:: ucis.ncdb.waivers.Waiver

.. seealso::

   * :ref:`test-history` — Binary test history API
   * :ref:`ncdb-format` — NCDB binary format specification
