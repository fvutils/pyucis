######################
Coverage Report Object
######################

Many of the tools that format and visualize coverage data make use of the coverage report
object implemented by PyUCIS. The `CoverageReport` object contains information about
the covergroups, covergroup instances, coverpoints and cross coverpoints in a coverage
database. It contains data on the percentage of coverage achieved, as well as detailed
information on the number of hits in each coverpoint and cross bin.


Building a CoverageReport
-------------------------

The best way to obtain a coverage report is to use the `CoverageReportBuilder` class.
The `build` method on this class accepts a UCIS database object and returns a 
`CoverageReport` class.

.. autoclass:: ucis.report.CoverageReportBuilder
   :members: build
  

CoverageReport Object
---------------------

The `CoverageReport` object is a tree of covergroups and coverpoints.

.. autoclass:: ucis.report.CoverageReport
   :members: covergroups, coverage
   
.. autoclass:: ucis.report.CoverageReport.Covergroup
   :members:

.. autoclass:: ucis.report.CoverageReport.CoverItem
   :members:
      
.. autoclass:: ucis.report.CoverageReport.Coverpoint
   :show-inheritance:
   :inherited-members:
   :members:

.. autoclass:: ucis.report.CoverageReport.Cross
   :show-inheritance:
   :inherited-members:
   :members: