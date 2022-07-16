#########################
YAML Coverage Data Format
#########################

The YAML coverage-data format is used to represent functional coverage 
data in a manner that is accurate and relatively easy for humans and
tools to create and process.


Format Reference
================

.. jsonschema:: ../../../src/ucis/schema/coverage.json

Every coverage-data document has a `coverage` element as its root. Currently,
the only sub-elements is a list of covergroup types.

.. jsonschema:: ../../../src/ucis/schema/coverage.json#/defs/covergroupType

A type covergroup provides data about a covergroup type. All instances
of a covergroup type have the same coverpoints and crosses. All 
coverpoints in instances of a covergroup type have the same bins.
Merged type coverage (the union of coverage achieved by all instances)
is derived by PyUCIS from the instance coverage, and is not specified
in the coverage file.

.. jsonschema:: ../../../src/ucis/schema/coverage.json#/defs/covergroupInstType

An instance covergroup provides data about a covergroup instance. 


.. jsonschema:: ../../../src/ucis/schema/coverage.json#/defs/coverpointType

A coverpoint lists a set of bins that it is monitoring. Each
coverpoint can specify an `atleast` count to specify that a
bin must contain `atleast` hits in order to count as being covered.
By default, `atleast` is 1.

.. jsonschema:: ../../../src/ucis/schema/coverage.json#/defs/crossType

A cross lists the set of coverpoints from which it is composed,
and lists its cross bins.  Each cross can specify an `atleast` 
count to specify that a bin must contain `atleast` hits in 
order to count as being covered. By default, `atleast` is 1.

.. jsonschema:: ../../../src/ucis/schema/coverage.json#/defs/coverBinType

A coverbin associates a bin name with the number of hits 
in that bin.
