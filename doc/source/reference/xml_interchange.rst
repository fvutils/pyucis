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

Coverage Options Support
=========================

PyUCIS fully supports reading and writing coverage options per the UCIS 1.0 specification:

Supported Options
-----------------

**Covergroup Options** (``CGINST_OPTIONS``):
  - ``weight`` - Relative weight for coverage calculation
  - ``goal`` - Coverage goal percentage (default: 100)
  - ``at_least`` - Minimum hit count for coverage (default: 1)
  - ``per_instance`` - Track per-instance coverage
  - ``merge_instances`` - Merge instance coverage into type coverage
  - ``get_inst_coverage`` - Enable instance coverage retrieval
  - ``auto_bin_max`` - Maximum auto-generated bins (PyUCIS sets to 64)
  - ``detect_overlap`` - Detect overlapping bins
  - ``strobe`` - Strobe sampling mode

**Coverpoint Options** (``COVERPOINT_OPTIONS``):
  - ``weight`` - Relative weight for coverage calculation
  - ``goal`` - Coverage goal percentage (default: 100)
  - ``at_least`` - Minimum hit count for coverage (default: 1)
  - ``auto_bin_max`` - Maximum auto-generated bins
  - ``detect_overlap`` - Detect overlapping bins

**Cross Options** (``CROSS_OPTIONS``):
  - ``weight`` - Relative weight for coverage calculation
  - ``goal`` - Coverage goal percentage (default: 100)
  - ``at_least`` - Minimum hit count for coverage (default: 1)
  - ``cross_num_print_missing`` - Number of missing cross bins to report

Value Normalization
-------------------

When writing XML, PyUCIS normalizes certain values to comply with XSD schema constraints:

- Negative ``goal`` values → 100 (UCIS default)
- Zero or negative ``at_least`` values → 1 (UCIS default)
- Zero or negative ``auto_bin_max`` values → 64 (UCIS default)

This ensures XML validates against the schema's ``nonNegativeInteger`` requirements.

Schema Compliance
=================

PyUCIS implementation follows UCIS 1.0 XML schema (``ucis.xsd``) with the following notable aspects:

Required Elements
-----------------

- **sourceFiles** (minOccurs="1") - At least one source file entry required
- **historyNodes** (minOccurs="1") - At least one history node required
- **instanceCoverages** (minOccurs="1") - At least one instance coverage required
- **coverpointBin** (minOccurs="1") - Coverpoints must contain at least one bin

Optional Elements
-----------------

- **coverpoint** (minOccurs="0") - Covergroups may be empty (no coverpoints)
- **cross** (minOccurs="0") - Cross coverage is optional
- **crossBin** (minOccurs="0") - Crosses may have no bins

Code Coverage
=============

PyUCIS supports reading and writing all major UCIS code coverage types within
``instanceCoverages`` elements.

Statement Coverage
------------------

Statement coverage is stored as ``blockCoverage`` → flat ``statement`` elements:

.. code::

  <blockCoverage>
    <statement id="1" file="1" line="5" inlineCount="1">
      <contents coverageCount="3"/>
    </statement>
  </blockCoverage>

Each ``statement`` records one source location with its hit count.

Branch Coverage
---------------

Branch coverage is stored as ``branchCoverage`` → ``branch`` elements, one per
branching statement (``if``, ``case``, etc.). Each branch has one or more
``branchBin`` arms:

.. code::

  <branchCoverage>
    <branch id="1" branchType="if" file="1" line="10">
      <branchBin alias="taken">
        <contents coverageCount="2"/>
      </branchBin>
      <branchBin alias="not_taken">
        <contents coverageCount="0"/>
      </branchBin>
    </branch>
  </branchCoverage>

Toggle Coverage
---------------

Toggle coverage is stored as ``toggleCoverage`` → ``toggleObject`` → ``toggleBit``
elements. Each bit records a 0→1 and a 1→0 transition bin:

.. code::

  <toggleCoverage>
    <toggleObject name="sig" canonical="sig">
      <toggleBit name="sig[0]">
        <toggle01Bin>
          <contents coverageCount="1"/>
        </toggle01Bin>
        <toggle10Bin>
          <contents coverageCount="1"/>
        </toggle10Bin>
      </toggleBit>
    </toggleObject>
  </toggleCoverage>

FSM Coverage
------------

FSM coverage is stored as ``fsmCoverage`` → ``fsm`` elements. State coverage uses
``stateBin`` and transition coverage uses ``transitionBin``:

.. code::

  <fsmCoverage>
    <fsm name="state_machine">
      <state stateName="IDLE">
        <stateBin name="IDLE">
          <contents coverageCount="5"/>
        </stateBin>
      </state>
      <stateTransition>
        <state>IDLE</state>
        <state>ACTIVE</state>
        <transitionBin name="IDLE->ACTIVE">
          <contents coverageCount="2"/>
        </transitionBin>
      </stateTransition>
    </fsm>
  </fsmCoverage>

Assertion Coverage
------------------

Assertion coverage is stored as ``assertionCoverage`` → ``assertion`` elements.
The ``assertionKind`` attribute is either ``assert`` or ``cover``:

.. code::

  <assertionCoverage>
    <assertion name="my_property" assertionKind="assert">
      <passBin>
        <contents coverageCount="10"/>
      </passBin>
      <failBin>
        <contents coverageCount="0"/>
      </failBin>
      <attemptBin>
        <contents coverageCount="10"/>
      </attemptBin>
    </assertion>
  </assertionCoverage>

Supported bin kinds for ``assert``: ``failBin``, ``passBin``, ``vacuousBin``,
``disabledBin``, ``attemptBin``, ``activeBin``, ``peakActiveBin``.

Supported bin kinds for ``cover``: ``coverBin``, ``failBin``, ``passBin``,
``vacuousBin``, ``disabledBin``, ``attemptBin``, ``activeBin``, ``peakActiveBin``.

User Attributes
===============

PyUCIS supports round-tripping user attributes (set via ``setAttribute`` /
``getAttribute``) through XML ``userAttr`` child elements. These are written as
the last children of each coverage container element:

.. code::

  <toggleCoverage>
    <!-- ... toggle data ... -->
    <userAttr key="tool_name" type="str">my_simulator</userAttr>
    <userAttr key="version" type="str">2024.1</userAttr>
  </toggleCoverage>

User attributes attached to instance scopes are preserved across XML write/read
round-trips. Tags (set via ``addTag``) are not currently serialized to XML.

History Nodes
=============

History nodes record the provenance of coverage data (test runs, merges). PyUCIS
preserves the parent/child relationships between history nodes using the ``id``
and ``parentId`` attributes:

.. code::

  <historyNodes>
    <historyNode id="1" logicalName="test_run_1" .../>
    <historyNode id="2" logicalName="merge_result" parentId="1" .../>
  </historyNodes>

Known Format Limitations
=========================

The following limitations are inherent to the UCIS XML interchange format specification:

Structural Limitations
----------------------

1. **Design Unit (DU) Scopes Not Serialized**
   
   Only instance coverages are written to XML. Design unit definitions and their source information 
   are not directly preserved. DU information is referenced via the ``moduleName`` attribute in 
   ``instanceCoverages``.

2. **Instance Weight Not Supported**
   
   The ``INSTANCE_COVERAGE`` schema does not include a ``weight`` attribute. Instance-level weighting 
   must be handled through covergroup weights instead.

3. **Mandatory Instance Coverage**
   
   The schema requires at least one ``instanceCoverages`` element. Pure file handle or metadata-only 
   databases cannot be represented in XML format.

4. **Coverpoints Require Bins**
   
   Per the schema, coverpoints must contain at least one bin (``minOccurs="1"`` for ``coverpointBin``). 
   Empty coverpoints cannot be serialized to XML.

Feature Support Matrix
----------------------

.. list-table::
   :header-rows: 1
   :widths: 40 20 40

   * - Feature
     - Supported
     - Notes
   * - Covergroup Options
     - ✅ Yes
     - Full read/write support
   * - Coverpoint Options
     - ✅ Yes
     - Full read/write support
   * - Cross Coverage
     - ✅ Yes
     - Including multi-way crosses
   * - Cross Bins
     - ✅ Yes
     - With index reconstruction
   * - Statement Coverage
     - ✅ Yes
     - Flat statement mode
   * - Branch Coverage
     - ✅ Yes
     - if/case branching statements
   * - Toggle Coverage
     - ✅ Yes
     - Per-bit 0→1 and 1→0 bins
   * - FSM Coverage
     - ✅ Yes
     - State and transition coverage
   * - Assertion Coverage
     - ✅ Yes
     - cover and assert kinds, all bin types
   * - User Attributes
     - ✅ Yes
     - Via ``userAttr`` child elements
   * - History Node Hierarchy
     - ✅ Yes
     - Parent/child via ``parentId``
   * - Condition/Expression Coverage
     - ❌ No
     - Not in Python DM; writer emits ctx.warn
   * - Instance Weights
     - ❌ No
     - Not in XML schema
   * - Empty Coverpoints
     - ❌ No
     - Schema requires bins
   * - DU Source Info
     - ⚠️ Partial
     - Only via instance references
   * - Standalone File Handles
     - ❌ No
     - Requires instanceCoverages
   * - Tags
     - ❌ No
     - No direct XML representation

Workarounds
-----------

**For Empty Coverpoints:**
  Add a placeholder bin when writing to XML. The bin can be marked as ``ignore`` type 
  to indicate it's not a real coverage point.

**For Instance Weights:**
  Use covergroup-level weights instead. Apply instance-specific weights at the covergroup 
  level for each instance.

**For File Handle Preservation:**
  Include at least one instance coverage element in the XML. File handles are preserved 
  within the ``sourceFiles`` section and referenced by ``id`` attributes.

Version Information
===================

This documentation applies to PyUCIS implementation of UCIS 1.0 XML interchange format 
as specified in the Accelera UCIS Standard (June 2012).

Schema file: ``src/ucis/xml/schema/ucis.xsd``

