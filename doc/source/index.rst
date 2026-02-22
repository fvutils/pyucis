PyUCIS
======

PyUCIS is a Python toolkit for **importing, merging, analyzing, and reporting
functional verification coverage data** in the
`Unified Coverage Interoperability Standard (UCIS) <https://www.accellera.org/activities/committees/ucis>`_
format. It works with coverage from Verilator, cocotb-coverage, AVL, and UCIS XML files,
and provides a command-line interface, an interactive terminal UI, HTML reports, and
CI/CD format export.

.. rubric:: Where do you want to start?

.. list-table::
   :widths: 40 60

   * - :doc:`getting-started/quickstart`
     - I have a coverage file and want to view or report it in 5 minutes
   * - :doc:`importing/index`
     - I need to import coverage from Verilator, cocotb, or AVL
   * - :doc:`cicd/index`
     - I want to integrate coverage into a CI/CD pipeline
   * - :doc:`reference/index`
     - I'm writing Python code against the PyUCIS API

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Getting Started

   getting-started/index

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Importing Coverage

   importing/index

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Working with Coverage

   working-with-coverage/index

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Reporting

   reporting/index

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: CI/CD Integration

   cicd/index

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: AI Integration

   ai-integration/mcp-server

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Reference

   reference/index
