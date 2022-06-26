######################
XML Interchange Format
######################

The Accelera UCIS Standard document specifies an XML interchange format. While the 
XML document structure has some similarities with the data model accessed via the
UCIS C API, there are also significant differences.

The UCIS standards document also has relatively few examples of the XML interchange
format, leaving some things a bit ambiguous. None of the ambiguities are with respect
to the document schema. Rather, they are with respect to how a schema-compliant
XML document is interpreted.

This section of the PyUCIS documentation describes how PyUCIS interprets a 
schema-compliant XML description, and the data it produces.

Functional Coverage
===================

Functional coverage data is stored in `cgInstance` sections within a 
`covergroupCoverage` scope. PyUCIS assumes that all `cgInstance` children
of a `covergroupCoverage` scope record data for the same covergroup type.

The UCIS data model represents covergroup type coverage (the merge of all
covergroup instances of a given type) as a scope that contains a series
of sub-scopes that hold per-instance coverage data. The XML interchange
format does not provide such a hierarchy.

According to the spec, a `covergroupCoverage` scope with a single 
`cgInstance` entry represents coverage for the covergroup as a whole. 
For example, a covergroup with `per_instance` set to false.

If a `covergroupCoverage` contains a single `cgInstance` entry, PyUCIS
interprets that entry as containing type coverage. If a 
`covergroupCoverage` contains more than one `cgInstance` entry, PyUCIS
interprets that content as being instance coverage. Type coverage is
created as the merge of the instance coverage.



