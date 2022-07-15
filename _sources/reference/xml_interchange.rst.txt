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
schema-compliant XML description, and the data it produces. Many of the
details are shaped by how existing tools interpret the XML interchange 
format. Because our goal is to maximize interoperability, PyUCIS 
deliberately shapes its data output (especially) to maximize interoperability

Functional Coverage
===================

Functional coverage data is stored in `cgInstance` sections within a 
`covergroupCoverage` scope. 


Covergroup instance/type linkage
--------------------------------
The cgId section inside the cgInstance specifies the associated covergroup type.

.. code:: 

  <cgInstance name="top.cg_i1" key="0">
    <options/>
    <cgId cgName="my_covergroup" moduleName="top">
      <cginstSourceId file="1" line="1" inlineCount="1"/>
      <cgSourceId file="1" line="1" inlineCount="1"/>
    </cgId>
  </cgInstance>

This covergroup instance name is `top.cg_i1`, and is associated with a 
covergroup type `top::my_covergroup`.

Covergroup instance and type data
---------------------------------
The UCIS data model represents covergroup type coverage (the merge of all
covergroup instances of a given type) as a scope that contains a series
of sub-scopes that hold per-instance coverage data. The XML interchange
format does not provide such a hierarchy.

When instance coverage is being recorded, all cgInstance sections 
associated with a given covergroup type contain instance data. The 
reader of XML data is responsible for reconstructing type coverage.

When instance coverage is not being recorded, only a single cgInstance
section is written. This section contains type data.
This intepretation is backed up bythe spec: a `covergroupCoverage` scope 
with a single `cgInstance` entry represents coverage for the covergroup as a whole. 
For example, a covergroup with `per_instance` set to false.

Coverage Instance Options
-------------------------
When reading XML, PyUCIS considers the following coverage options significant:

- _per_instance_ - Indicates whether per-instance data is recorded
- _merge_instances_ - Specifies whether to produce type coverage from the merge of instance data

Both of these options are boolean options. PyUCIS accepts `true`, `false`, `0`, and `1`.

When writing XML, PyUCIS emits `auto_bin_max=0`. This is because PyUCIS represents all coverpoint
bins explicitly. Some consumers of XML interchange format attempt to create auto-bins if this 
option is not explicitly set to 0.

Coverpoint Bins
---------------

.. code::

    <coverpoint name="cp1" key="0">
        <options/>
        <coverpointBin name="a[0]", type="bins" key="0">
            <range from "-1" to "-1">
                contents coverageCount="1"/>
            </range>
        </coverpointBin>
    </coverpoint>

     
Coverpoint data is stored within a `coverpoint` subsection inside `cgInstance`. PyUCIS
writes the bin type as one of `bins`, `ignore`, `illegal`.

PyUCIS only interprets and records the following options:
- `weight`
- `at_least`

PyUCIS does not interpret the value-range data, and records both bounds of the
range as `-1`. This is because UCIS doesn't provide relevant data to record.


Cross Bins
----------
The most common case with cross bins is to record auto-bins resulting from
the cross of the relevant coverpoints. 

.. code::

    <cross name="cp1Xcp2" key="0">
        <options/>
        <crossExpr>cp1</crossExpr>
        <crossExpr>cp2</crossExpr>
        <crossBin name="&lt;a[0],a[0]&gt;" key="0">
            <index>0</index>
            <index>0</index>
            <contents coverageCount="1"/>
        </crossBin>
    </cross>


Note that the bin-index information is not something that is present in 
the UCIS data model. Cross bins, like all other bins, are simply named
counts. PyUCIS attempts to reconstruct the indices by looking for bin 
names within the bin name. In the example above, the bin names a[0],
a[0] are both the first bin within their respective coverpoints. 
Consequently, bin indices 0,0 are specified.

In the case of `ignore` or `illegal` bins, all indices are specified
as -1.

PyUCIS records the bin type only if it is `ignore` or `illegal`. This
improves interoperability with some tools.

