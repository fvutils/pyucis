########################
UCIS Object-Oriented API
########################

The UCIS object-oriented API provides access to coverage databases through a
hierarchy of Python classes. This page documents every class in the public API,
organized from the top of the type hierarchy down to leaf types.

.. contents::
   :local:
   :depth: 2

Class Hierarchy
===============

.. code-block:: text

    Obj
    ├── UCIS (Scope)          ← database root; use MemFactory or SqliteUCIS
    ├── Scope (Obj)
    │   ├── CovScope
    │   │   └── FuncCovScope
    │   │       └── CvgScope
    │   │           ├── Covergroup
    │   │           │   └── (instances returned by createCovergroup)
    │   │           ├── Coverpoint
    │   │           │   └── Cross
    │   │           ├── CvgBinScope
    │   │           ├── IgnoreBinScope
    │   │           └── IllegalBinScope
    │   ├── DUScope           ← design unit definition
    │   └── InstanceScope     ← design hierarchy instance
    ├── HistoryNode           ← test run / merge record
    └── CoverItem             ← bin (leaf coverage measurement)

    CoverData                 ← data container for a bin's hit count and goal
    SourceInfo                ← (file, line, token) tuple
    TestData                  ← test run metadata passed to createHistoryNode

Creating a Database
===================

All interaction with coverage data starts by obtaining a :class:`~ucis.ucis.UCIS`
object from one of the backend factories.

In-Memory Backend
-----------------

.. autoclass:: ucis.mem.mem_factory.MemFactory
   :members:
   :member-order: bysource
   :undoc-members:

SQLite Backend
--------------

.. autoclass:: ucis.sqlite.sqlite_ucis.SqliteUCIS
   :members:
   :member-order: bysource
   :undoc-members:

------------

Core Classes
============

UCIS
----

The database root. Returned by ``MemFactory.create()`` and ``SqliteUCIS(path)``.

.. autoclass:: ucis.ucis.UCIS
   :members:
   :member-order: bysource
   :undoc-members:

Scope
-----

Base class for all hierarchical containers. Every node in the design hierarchy and
the coverage model is a ``Scope``. The key operations — creating child scopes,
iterating child scopes, and accessing cover items — are defined here.

.. autoclass:: ucis.scope.Scope
   :members:
   :member-order: bysource
   :undoc-members:

HistoryNode
-----------

Records one test run or merge operation in the database's provenance tree.
Create via :meth:`~ucis.ucis.UCIS.createHistoryNode`; iterate via
:meth:`~ucis.ucis.UCIS.historyNodes`.

.. autoclass:: ucis.history_node.HistoryNode
   :members:
   :member-order: bysource
   :undoc-members:

------------

Coverage Scope Hierarchy
=========================

CovScope
--------

Base class for generic coverage scopes (code coverage types such as branch and
toggle). Extends :class:`~ucis.scope.Scope`.

.. autoclass:: ucis.cov_scope.CovScope
   :members:
   :member-order: bysource
   :undoc-members:

FuncCovScope
------------

Base class for functional coverage scopes. Extends :class:`~ucis.cov_scope.CovScope`.

.. autoclass:: ucis.func_cov_scope.FuncCovScope
   :members:
   :member-order: bysource
   :undoc-members:

CvgScope
--------

Base class for covergroup-level scopes (groups, coverpoints, crosses).
Provides shared attributes such as ``at_least``, ``auto_bin_max``, and
``comment``. Extends :class:`~ucis.func_cov_scope.FuncCovScope`.

.. autoclass:: ucis.cvg_scope.CvgScope
   :members:
   :member-order: bysource
   :undoc-members:

Covergroup
----------

A SystemVerilog or SystemC covergroup type definition. Contains
:class:`~ucis.coverpoint.Coverpoint`, :class:`~ucis.cross.Cross`, and
per-instance coverage children.

Create via :meth:`~ucis.scope.Scope.createCovergroup`.

.. autoclass:: ucis.covergroup.Covergroup
   :members:
   :member-order: bysource
   :undoc-members:

Coverpoint
----------

A coverpoint measuring coverage of a single variable or expression.
Contains bins created via :meth:`~ucis.coverpoint.Coverpoint.createBin`.

Create via :meth:`~ucis.covergroup.Covergroup.createCoverpoint`.

.. autoclass:: ucis.coverpoint.Coverpoint
   :members:
   :member-order: bysource
   :undoc-members:

Cross
-----

Cross-product coverage of two or more coverpoints. Extends
:class:`~ucis.coverpoint.Coverpoint`.

Create via :meth:`~ucis.covergroup.Covergroup.createCross`.

.. autoclass:: ucis.cross.Cross
   :members:
   :member-order: bysource
   :undoc-members:

CvgBinScope
-----------

Normal bin scope for SystemVerilog covergroups.

.. autoclass:: ucis.cvg_bin_scope.CvgBinScope
   :members:
   :member-order: bysource
   :undoc-members:

IgnoreBinScope
--------------

Scope representing a SystemVerilog ``ignore_bins`` declaration.

.. autoclass:: ucis.ignore_bin_scope.IgnoreBinScope
   :members:
   :member-order: bysource
   :undoc-members:

IllegalBinScope
---------------

Scope representing a SystemVerilog ``illegal_bins`` declaration.

.. autoclass:: ucis.illegal_bin_scope.IllegalBinScope
   :members:
   :member-order: bysource
   :undoc-members:

------------

Design Hierarchy Scopes
=======================

DUScope
-------

Design unit (module/entity/package) definition. DU scopes act as templates
for instances. Create via :meth:`~ucis.scope.Scope.createScope` with
:attr:`~ucis.scope_type_t.ScopeTypeT.DU_MODULE` (or other ``DU_*`` type).

.. autoclass:: ucis.du_scope.DUScope
   :members:
   :member-order: bysource
   :undoc-members:

InstanceScope
-------------

A design hierarchy instance. Points back to its design unit via
:meth:`~ucis.instance_scope.InstanceScope.getInstanceDu`. Create via
:meth:`~ucis.scope.Scope.createInstance`.

.. autoclass:: ucis.instance_scope.InstanceScope
   :members:
   :member-order: bysource
   :undoc-members:

------------

Cover Items
===========

CoverItem
---------

Base class for bins — the leaf-level coverage measurements within
coverpoints, crosses, and code coverage scopes.

.. autoclass:: ucis.cover_item.CoverItem
   :members:
   :member-order: bysource
   :undoc-members:

CoverData
---------

Holds the hit count, goal, and status flags for one cover item.
Passed to :meth:`~ucis.coverpoint.Coverpoint.createBin` and
returned by :meth:`~ucis.obj.Obj.getCoverData`.

.. autoclass:: ucis.cover_data.CoverData
   :members:
   :member-order: bysource
   :undoc-members:

------------

Value Objects
=============

SourceInfo
----------

Bundles a :class:`~ucis.file_handle.FileHandle` with a line number and token
offset to identify where a scope or bin was declared in source.

.. autoclass:: ucis.source_info.SourceInfo
   :members:
   :member-order: bysource
   :undoc-members:

TestData
--------

Carries test metadata (status, tool, date, seed, …) and is passed to
:meth:`~ucis.history_node.HistoryNode.setTestData`.

.. autoclass:: ucis.test_data.TestData
   :members:
   :member-order: bysource
   :undoc-members:

------------

Enumerations
============

ScopeTypeT
----------

Identifies the type of every scope in the hierarchy. Used as a filter mask
in :meth:`~ucis.scope.Scope.scopes` and as a required argument to scope
creation methods.

.. autoclass:: ucis.scope_type_t.ScopeTypeT
   :members:
   :member-order: bysource
   :undoc-members:

CoverTypeT
----------

Identifies the coverage type of every cover item (bin). Used as a filter
mask in :meth:`~ucis.scope.Scope.coverItems`.

.. autoclass:: ucis.cover_type_t.CoverTypeT
   :members:
   :member-order: bysource
   :undoc-members:

CoverFlagsT
-----------

Bit flags stored in a :class:`~ucis.cover_data.CoverData` that control
data precision and indicate which optional fields are valid.

.. autoclass:: ucis.cover_flags_t.CoverFlagsT
   :members:
   :member-order: bysource
   :undoc-members:

HistoryNodeKind
---------------

Discriminates test-run nodes (``TEST``) from merge nodes (``MERGE``) in the
database history tree.

.. autoclass:: ucis.history_node_kind.HistoryNodeKind
   :members:
   :member-order: bysource
   :undoc-members:

TestStatusT
-----------

Pass/fail status recorded on a test history node.

.. autoclass:: ucis.test_status_t.TestStatusT
   :members:
   :member-order: bysource
   :undoc-members:

SourceT
-------

HDL source language of a scope (``VLOG``, ``SV``, ``VHDL``, etc.).

.. autoclass:: ucis.source_t.SourceT
   :members:
   :member-order: bysource
   :undoc-members:

FlagsT
------

Scope-level flags controlling coverage enablement, exclusion, and other
scope behaviours. Passed as the ``flags`` argument to scope creation methods.

.. autoclass:: ucis.flags_t.FlagsT
   :members:
   :member-order: bysource
   :undoc-members:
