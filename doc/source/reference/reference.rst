################
PyUCIS Reference
################

This section provides information on APIs and file formats
used by PyUCIS.

.. toctree::
   :maxdepth: 2

   coverage_report_api
   coverage_report_json
   html_coverage_report
   xml_interchange
   yaml_coverage
   recording_coverage_best_practices
   ucis_oo_api
   ucis_c_api
   sqlite_api
   sqlite_schema_reference
   native_api
   


Back-End APIs
=============

PyUCIS supports multiple backend storage implementations, each with different trade-offs:

In-Memory
---------

The in-memory backend stores all coverage data in RAM for fast access. Best for:

* Small to medium databases that fit in memory
* Temporary coverage processing
* Fast iteration and analysis

See :doc:`ucis_oo_api` for the Python object-oriented API.

SQLite
------

The SQLite backend provides persistent, queryable storage using SQLite3 databases. Best for:

* Large coverage databases
* Persistent storage requirements
* SQL-based queries and analysis
* Integration with database tools

See :doc:`sqlite_api` for the Python SQLite API and :doc:`sqlite_schema_reference` for detailed schema documentation.

Native C Library
----------------

The native C library provides a UCIS 1.0 compliant C API with SQLite3 backend. Best for:

* C/C++ applications
* Performance-critical operations
* Integration with native tools
* Python ctypes integration

See :doc:`native_api` for the C API documentation.

UCIS C API
----------

The UCIS C API wrapper provides access to external UCIS libraries. See :doc:`ucis_c_api` for details.

XML
---

The XML backend reads and writes UCIS data in XML format for interchange. See :doc:`xml_interchange` for details.

YAML
----

The YAML backend provides a human-readable text format. See :doc:`yaml_coverage` for details.





