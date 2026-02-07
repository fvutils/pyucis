######################
Show Commands Reference
######################

The ``ucis show`` commands provide comprehensive coverage analysis and reporting
capabilities with support for industry-standard format export.

***************
Overview
***************

The show commands extract and present coverage data from UCIS databases in various
formats, enabling:

* **Coverage Analysis**: Detailed examination of functional, code, assertion, and toggle coverage
* **Gap Identification**: Finding uncovered items requiring attention
* **Database Comparison**: Regression detection between coverage runs
* **Format Export**: Generating reports in LCOV, Cobertura, JaCoCo, and Clover formats
* **CI/CD Integration**: Seamless integration with Jenkins, GitLab CI, GitHub Actions, and more

All show commands support both JSON (for automation) and text (for human readability) output formats.

***************
Available Commands
***************

Core Analysis Commands
======================

show summary
------------

Display overall coverage statistics across all coverage types.

.. code-block:: bash

    ucis show summary database.ucis --output-format json
    ucis show summary database.ucis --output-format text

**Output includes:**

* Overall coverage percentage
* Breakdown by coverage type (functional, code, assertion, toggle)
* Test statistics (pass/fail counts)
* Database metadata

show gaps
---------

Identify uncovered or low-coverage items requiring attention.

.. code-block:: bash

    ucis show gaps database.ucis --threshold 80
    ucis show gaps database.ucis --threshold 90 --limit 20

**Parameters:**

* ``--threshold``: Show items below this coverage percentage (default: 100)
* ``--limit``: Maximum number of items to show (default: unlimited)

**Output includes:**

* Uncovered covergroups and bins
* Coverage percentages for each item
* Priority ranking based on weights

show covergroups
----------------

Display detailed covergroup information.

.. code-block:: bash

    ucis show covergroups database.ucis
    ucis show covergroups database.ucis --pattern "alu_*"

**Parameters:**

* ``--pattern``: Filter covergroups by name pattern

**Output includes:**

* Covergroup names and coverage percentages
* Coverpoint details
* Bin counts and status

show bins
---------

Display bin-level coverage details with filtering.

.. code-block:: bash

    ucis show bins database.ucis --covergroup cg_example
    ucis show bins database.ucis --status hit

**Parameters:**

* ``--covergroup``: Filter by covergroup name
* ``--coverpoint``: Filter by coverpoint name
* ``--status``: Filter by hit status (hit/missed)

**Output includes:**

* Bin names and hit counts
* Value ranges
* Hit/missed status

Design Structure Commands
==========================

show hierarchy
--------------

Display the design hierarchy and scope structure.

.. code-block:: bash

    ucis show hierarchy database.ucis
    ucis show hierarchy database.ucis --depth 3

**Parameters:**

* ``--depth``: Maximum depth to traverse (default: unlimited)

**Output includes:**

* Design unit hierarchy
* Instance paths
* Scope types and coverage

show tests
----------

Display test execution information.

.. code-block:: bash

    ucis show tests database.ucis

**Output includes:**

* Test names and execution dates
* Pass/fail status
* Test-specific coverage

Advanced Analysis Commands
===========================

show metrics
------------

Display advanced coverage metrics and analysis.

.. code-block:: bash

    ucis show metrics database.ucis

**Output includes:**

* Coverage efficiency metrics
* Bin distribution analysis
* Weighted coverage calculations
* Actionable recommendations

show compare
------------

Compare two coverage databases to detect regressions.

.. code-block:: bash

    ucis show compare baseline.ucis current.ucis
    ucis show compare old.ucis new.ucis --output-format json

**Parameters:**

* Two database paths (baseline and current)

**Output includes:**

* Coverage deltas (increased/decreased)
* New and removed items
* Bin-level changes
* Regression detection

show hotspots
-------------

Identify coverage hotspots requiring attention.

.. code-block:: bash

    ucis show hotspots database.ucis --target 90
    ucis show hotspots database.ucis --limit 10

**Parameters:**

* ``--target``: Target coverage percentage (default: 80)
* ``--limit``: Maximum items per category (default: 10)

**Output includes:**

* Low-coverage items prioritized by impact
* Actionable recommendations
* Estimated effort to reach target

Coverage Type Commands
======================

show code-coverage
------------------

Display code coverage with multi-format export support.

.. code-block:: bash

    ucis show code-coverage database.ucis --output-format json
    ucis show code-coverage database.ucis --output-format lcov > coverage.info
    ucis show code-coverage database.ucis --output-format cobertura > coverage.xml
    ucis show code-coverage database.ucis --output-format jacoco > jacoco.xml
    ucis show code-coverage database.ucis --output-format clover > clover.xml

**Supported Formats:**

* **json**: Machine-readable JSON (default)
* **text**: Human-readable text
* **lcov**: LCOV .info format (Codecov, Coveralls, genhtml)
* **cobertura**: Cobertura XML (Jenkins, GitLab CI, SonarQube)
* **jacoco**: JaCoCo XML (Maven, Gradle, SonarQube)
* **clover**: Clover XML (Bamboo, Jenkins)

show assertions
---------------

Display assertion coverage information.

.. code-block:: bash

    ucis show assertions database.ucis

**Output includes:**

* Assertion names and status
* Pass/fail counts
* Coverage percentage

**Note:** Requires assertion coverage data in the database.

show toggle
-----------

Display toggle coverage for signals.

.. code-block:: bash

    ucis show toggle database.ucis

**Output includes:**

* Signal names
* 0→1 and 1→0 toggle status
* Fully/partially toggled counts
* Coverage percentage

**Note:** Requires toggle coverage data in the database.

***************************
CI/CD Integration Examples
***************************

The show commands integrate seamlessly with CI/CD pipelines:

Jenkins
=======

Generate Cobertura XML for Jenkins Cobertura plugin:

.. code-block:: bash

    ucis show code-coverage results.ucis --output-format cobertura > coverage.xml

JaCoCo XML for Jenkins JaCoCo plugin:

.. code-block:: bash

    ucis show code-coverage results.ucis --output-format jacoco > jacoco.xml

GitLab CI
=========

Generate LCOV for GitLab test coverage visualization:

.. code-block:: yaml

    test:
      script:
        - ucis show code-coverage coverage.ucis --output-format lcov > coverage.info
      artifacts:
        reports:
          coverage_report:
            coverage_format: cobertura
            path: coverage.xml

GitHub Actions
==============

Upload coverage to Codecov:

.. code-block:: yaml

    - name: Generate LCOV
      run: ucis show code-coverage coverage.ucis --output-format lcov > coverage.info
    
    - name: Upload to Codecov
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.info

SonarQube
=========

Generate coverage for SonarQube analysis:

.. code-block:: bash

    ucis show code-coverage results.ucis --output-format cobertura > coverage.xml
    sonar-scanner -Dsonar.coverageReportPaths=coverage.xml

***************
Output Formats
***************

All show commands support multiple output formats:

JSON Format
===========

Machine-readable structured data with complete coverage information:

.. code-block:: bash

    ucis show summary database.ucis --output-format json

Use ``jq`` for filtering:

.. code-block:: bash

    ucis show summary db.ucis -of json | jq '.coverage_by_type.functional'

Text Format
===========

Human-readable formatted output:

.. code-block:: bash

    ucis show summary database.ucis --output-format text

Standard Coverage Formats
==========================

**LCOV Format** (``.info`` files):

* Supported by: genhtml, Codecov, Coveralls, GitLab CI
* Line, branch, and function coverage
* Text-based format

**Cobertura XML**:

* Supported by: Jenkins, GitLab CI, SonarQube, Azure DevOps
* Package/class structure
* Line and branch coverage

**JaCoCo XML**:

* Supported by: Maven, Gradle, SonarQube, IntelliJ IDEA
* Instruction, branch, line, method, class counters
* Session information

**Clover XML**:

* Supported by: Bamboo, Jenkins (Clover plugin)
* Statement, conditional, method metrics
* Project/package/file hierarchy

***************
Common Options
***************

All show commands support these options:

``--out, -o <path>``
  Write output to specified file instead of stdout

``--input-format, -if <format>``
  Input database format (xml, yaml, libucis). Default: xml

``--output-format, -of <format>``
  Output format. Available formats depend on the command:
  
  * All commands: json, text (or txt)
  * code-coverage: json, text, lcov, cobertura, jacoco, clover

***************
Best Practices
***************

Coverage Analysis Workflow
===========================

1. **Get Overview**: Start with ``show summary`` to understand overall coverage
2. **Identify Gaps**: Use ``show gaps`` to find items needing attention
3. **Analyze Hotspots**: Use ``show hotspots`` for prioritized recommendations
4. **Detailed Investigation**: Use specific commands (covergroups, bins) to drill down
5. **Track Progress**: Use ``show compare`` to measure improvements

CI/CD Integration
=================

1. **Generate Format**: Export to appropriate format for your platform
2. **Validate Output**: Ensure format is correct before upload
3. **Set Thresholds**: Use coverage gates to enforce quality
4. **Track Trends**: Compare runs to detect regressions

Automation
==========

1. **Use JSON Output**: For scripting and automation
2. **Pipe to Tools**: Combine with jq, grep, awk for filtering
3. **Set Exit Codes**: Check coverage thresholds in scripts
4. **Generate Reports**: Create custom dashboards from JSON data

Example Automation Script:

.. code-block:: bash

    #!/bin/bash
    # Check if coverage meets threshold
    
    COVERAGE=$(ucis show summary coverage.ucis -of json | jq -r '.overall_coverage')
    THRESHOLD=80
    
    if (( $(echo "$COVERAGE < $THRESHOLD" | bc -l) )); then
        echo "Coverage $COVERAGE% below threshold $THRESHOLD%"
        exit 1
    fi
    
    echo "Coverage $COVERAGE% meets threshold"
    exit 0
