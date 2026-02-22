##################
Importing Coverage
##################

PyUCIS reads coverage from several simulator and verification framework formats and
converts them all into the same UCIS internal model. Once imported, every tool in
PyUCIS works identically regardless of the original source.

Supported Sources
=================

.. list-table::
   :header-rows: 1
   :widths: 30 25 25 20

   * - Source
     - ``--input-format``
     - File extension
     - Guide
   * - Verilator
     - ``vltcov``
     - ``.dat``
     - :doc:`verilator`
   * - cocotb-coverage (XML)
     - ``cocotb-xml``
     - ``.xml``, ``.cov``
     - :doc:`cocotb`
   * - cocotb-coverage (YAML)
     - ``cocotb-yaml``
     - ``.yml``, ``.yaml``
     - :doc:`cocotb`
   * - AVL (JSON)
     - ``avl-json``
     - ``.json``
     - :doc:`avl`
   * - UCIS XML
     - ``xml`` *(default)*
     - ``.xml``
     - —
   * - UCIS YAML
     - ``yaml``
     - ``.yaml``
     - —

Automatic Format Detection
==========================

When working in Python you can let PyUCIS detect the format automatically:

.. code-block:: python

    from ucis.format_detection import read_coverage_file

    db = read_coverage_file('coverage.xml')   # cocotb XML, UCIS XML, or AVL — auto-detected
    db = read_coverage_file('coverage.yml')   # cocotb YAML or UCIS YAML
    db = read_coverage_file('coverage.json')  # AVL JSON

From the command line always specify ``--input-format`` to be explicit.

.. toctree::
   :maxdepth: 1

   verilator
   cocotb
   avl
