.. _ncdb-format:

############################
NCDB Coverage File Format
############################

NCDB (*Native Coverage DataBase*) is a compact, ZIP-based binary format for
storing and merging UCIS coverage data.  A single ``.cdb`` file is a standard
ZIP archive whose members encode the scope hierarchy, hit counts, test history,
and source file references.

The format is designed to be:

* **Space-efficient** — typically 100–200× smaller than the equivalent SQLite
  ``.cdb`` (see :ref:`ncdb-benchmarks`).
* **Merge-fast** — same-schema merges reduce to element-wise integer addition
  over a flat array, with no SQL overhead.
* **Self-describing** — a ``manifest.json`` at the root of the archive carries
  all metadata needed to read or merge the file without any external schema.
* **Readable without PyUCIS** — every binary encoding is documented here in
  sufficient detail to write an independent parser.

.. contents:: On this page
   :local:
   :depth: 2

-----------

**********************
1. File identification
**********************

Both NCDB and the legacy SQLite backend use the ``.cdb`` extension.
Format discrimination is done by inspecting the first 16 bytes of the file.

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Format
     - Header (hex)
     - Description
   * - SQLite
     - ``53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00``
     - Literal ASCII ``SQLite format 3\x00``
   * - NCDB (non-empty)
     - ``50 4B 03 04 …``
     - ZIP local-file header signature ``PK\x03\x04``
   * - NCDB (empty archive)
     - ``50 4B 05 06 …``
     - ZIP end-of-central-directory signature ``PK\x05\x06``

**Detection algorithm:**

1. Read the first 16 bytes of the file.
2. If ``bytes[0:16]`` equals the SQLite magic string → format is ``sqlite``.
3. If ``bytes[0:4]`` is ``PK\x03\x04`` or ``PK\x05\x06``:

   a. Open as ZIP.
   b. Read ``manifest.json``.
   c. If ``manifest["format"] == "NCDB"`` → format is ``ncdb``.

4. Otherwise → format is ``unknown``.

-----------

***********************
2. Archive structure
***********************

An NCDB file is a **standard ZIP archive** (DEFLATE compression) whose members
are named as follows.  Members marked *required* must be present in every valid
NCDB file; others are only written when the corresponding data is non-empty or
non-default.

.. list-table::
   :header-rows: 1
   :widths: 25 12 63

   * - Member name
     - Required
     - Contents
   * - ``manifest.json``
     - ✓
     - Format identity, version, statistics, and the schema hash.
   * - ``strings.bin``
     - ✓
     - Deduplicated string table referenced by index throughout other members.
   * - ``scope_tree.bin``
     - ✓
     - DFS-serialized scope hierarchy (V2 encoding).  Counts are *not* stored here.
   * - ``counts.bin``
     - ✓
     - Flat array of hit counts in the same DFS order as ``scope_tree.bin``.
   * - ``history.json``
     - ✓
     - Array of test-run and merge history records.
   * - ``sources.json``
     - ✓
     - Ordered list of source file paths; indices match file IDs in ``scope_tree.bin``.
   * - ``attrs.bin``
     - —
     - User-defined attribute assignments.
   * - ``tags.json``
     - —
     - Tag assignments for scopes and coveritems.
   * - ``toggle.bin``
     - —
     - Per-signal toggle metadata (canonical name, type, direction).
   * - ``fsm.bin``
     - —
     - FSM state and transition metadata.
   * - ``cross.bin``
     - —
     - Cross-coverpoint link records.
   * - ``properties.json``
     - —
     - Typed property values (int, real, string, handle).
   * - ``design_units.json``
     - —
     - Design-unit records (module, package, interface, program).
   * - ``formal.bin``
     - —
     - Formal-verification assertion data.
   * - ``contrib/NNNNN.bin``
     - —
     - Per-test coveritem contribution arrays (delta-encoded, sparse).

-----------

***********************
3. Primitive encodings
***********************

.. _ncdb-varint:

3.1 Unsigned LEB128 varint
==========================

All variable-length integers in NCDB are encoded as **unsigned LEB128**
(also called unsigned varint or ULEB128).  This is the same encoding used
by DWARF, WebAssembly, and Protocol Buffers (field type ``uint64``).

**Encoding:**

1. Take the 7 least-significant bits of the value; set bit 7 to ``1`` if more
   bytes follow, ``0`` if this is the last byte.
2. Shift the value right by 7.  Repeat until the value is zero.

.. code-block:: text

   value     bytes (hex)
   ────────────────────
   0         00
   1         01
   127       7F
   128       80 01
   255       FF 01
   16383     FF 7F
   16384     80 80 01
   2³²−1     FF FF FF FF 0F
   2⁶⁴−1     FF FF FF FF FF FF FF FF FF 01

**Decoding:**

Read bytes one at a time.  For each byte, take the low 7 bits and OR them into
the accumulator at the current bit position (starting at 0).  Advance the bit
position by 7.  If bit 7 of the byte is set, continue reading; otherwise stop.

.. code-block:: python

   def decode_varint(buf: bytes, offset: int = 0):
       result, shift = 0, 0
       while True:
           byte = buf[offset]; offset += 1
           result |= (byte & 0x7F) << shift
           shift += 7
           if not (byte & 0x80):
               return result, offset

3.2 UTF-8 strings
=================

All text is UTF-8.  Strings stored inline (e.g. in JSON members) are standard
JSON strings.  Strings stored in binary members (``scope_tree.bin``,
``strings.bin``) are referenced by their **string-table index** (a varint).

-----------

********************
4. manifest.json
********************

A JSON object with the following fields (all present; unknown fields must be
ignored by readers for forward compatibility):

.. code-block:: json

   {
     "format":          "NCDB",
     "version":         "1.0",
     "ucis_version":    "1.0",
     "created":         "2026-02-25T21:00:00Z",
     "path_separator":  "/",
     "scope_count":     42,
     "coveritem_count": 8800,
     "test_count":      64,
     "total_hits":      155432,
     "covered_bins":    7312,
     "schema_hash":     "sha256:a3f1...",
     "generator":       "pyucis-ncdb"
   }

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Field
     - Description
   * - ``format``
     - Always the string ``"NCDB"``.  Readers must reject files where this
       is not ``"NCDB"``.
   * - ``version``
     - Format version string.  Currently ``"1.0"``.  Readers should check
       the major component; a mismatch should produce a clear error.
   * - ``ucis_version``
     - UCIS standard version the data conforms to.  Currently ``"1.0"``.
   * - ``created``
     - ISO 8601 UTC timestamp when the file was written.
   * - ``path_separator``
     - Hierarchical path separator used in scope names.  Typically ``"/"``.
   * - ``scope_count``
     - Total number of scopes in ``scope_tree.bin`` (informational).
   * - ``coveritem_count``
     - Total number of coveritems.  Must equal the length of the array in
       ``counts.bin``.
   * - ``test_count``
     - Number of TEST-kind entries in ``history.json``.
   * - ``total_hits``
     - Sum of all values in ``counts.bin``.
   * - ``covered_bins``
     - Number of non-zero values in ``counts.bin``.
   * - ``schema_hash``
     - ``"sha256:"`` followed by the lowercase hex SHA-256 digest of the
       **uncompressed** ``scope_tree.bin`` content.  Used by the fast-merge
       path to verify schema identity without parsing the scope tree.
       (See :ref:`ncdb-merge`.)
   * - ``generator``
     - Free-form tool identification string.

-----------

********************
5. strings.bin
********************

A deduplicated string table.  Every string used anywhere in ``scope_tree.bin``
(scope names, coveritem names) is stored exactly once here and referenced by a
zero-based integer index.

**Binary layout:**

.. code-block:: text

   [count   : varint]          — number of strings
   [len_0   : varint]          — byte length of string 0 (UTF-8 encoded)
   [bytes_0 : len_0 bytes]     — UTF-8 bytes of string 0
   [len_1   : varint]
   [bytes_1 : len_1 bytes]
   ...

* **Index 0** is always the empty string ``""``.
* String indices are stable: the same string always maps to the same index
  within a single file (indices are assigned in first-encounter DFS order).

-----------

************************
6. scope_tree.bin
************************

The complete scope hierarchy encoded as a depth-first traversal.  The file
contains a flat sequence of scope records with no explicit end marker; the
count of child scopes embedded in each record defines the nesting.

Counts (hit values) are **not** stored in this member.  Instead, each
coveritem encountered during DFS appends its hit count to ``counts.bin`` in
the same traversal order.  A reader reconstructs the association by walking
``scope_tree.bin`` and consuming counts from ``counts.bin`` in lockstep.

6.1 Scope record types
=======================

Every scope record begins with a one-byte **marker**:

.. list-table::
   :header-rows: 1
   :widths: 15 20 65

   * - Marker byte
     - Name
     - Description
   * - ``0x00``
     - ``REGULAR``
     - Full scope record with type, name, presence bitfield, and children.
   * - ``0x01``
     - ``TOGGLE_PAIR``
     - Compact 2-field record for BRANCH scopes that carry exactly two
       TOGGLEBIN coveritems with the implicit names ``"0 -> 1"`` and
       ``"1 -> 0"``.  Saves ~10 bytes per signal.

6.2 REGULAR scope record
=========================

.. code-block:: text

   [marker    : 1 byte  ]  always 0x00
   [scope_type: varint  ]  ScopeTypeT integer value
   [name_ref  : varint  ]  index into strings.bin
   [presence  : varint  ]  bitfield of optional fields present (see below)

   — optional fields, each present only if the corresponding bit is set —
   [flags     : varint  ]  only if PRESENCE_FLAGS  (bit 0) set
   [file_id   : varint  ]  only if PRESENCE_SOURCE (bit 1) set
   [line      : varint  ]     "
   [token     : varint  ]     "
   [weight    : varint  ]  only if PRESENCE_WEIGHT  (bit 2) set
   [at_least  : varint  ]  only if PRESENCE_AT_LEAST (bit 3) set

   — always present —
   [num_children : varint]  number of child scope records that follow
   [num_covers   : varint]  number of coveritem records that follow

   — present only when num_covers > 0 —
   [cover_type   : varint]  CoverTypeT of all coveritems in this scope

   — num_covers coveritem records —
   [name_ref_ci  : varint]  × num_covers   (one per coveritem)

   — num_children child scope records (recursive) —

**Presence bitfield values:**

.. list-table::
   :header-rows: 1
   :widths: 10 20 70

   * - Bit
     - Name
     - Meaning
   * - 0
     - ``PRESENCE_FLAGS``
     - Non-default scope flags are stored.
   * - 1
     - ``PRESENCE_SOURCE``
     - Source location (``file_id``, ``line``, ``token``) is stored.
   * - 2
     - ``PRESENCE_WEIGHT``
     - Non-default scope weight (≠ 1) is stored.
   * - 3
     - ``PRESENCE_AT_LEAST``
     - An ``at_least`` threshold that overrides the cover-type default is
       stored at the scope level (applies to all coveritems in the scope).

**Cover-type defaults** (used when ``PRESENCE_AT_LEAST`` is absent):

.. list-table::
   :header-rows: 1
   :widths: 30 15 15 15

   * - CoverTypeT
     - flags default
     - at_least default
     - weight default
   * - ``CVGBIN``
     - 0
     - **1**
     - 1
   * - All others (TOGGLEBIN, STMTBIN, BRANCHBIN, …)
     - 0
     - 0
     - 1

6.3 TOGGLE_PAIR record
=======================

.. code-block:: text

   [marker   : 1 byte ]  always 0x01
   [name_ref : varint ]  scope name index in strings.bin

A TOGGLE_PAIR record implicitly encodes:

* Scope type: ``BRANCH``
* Two TOGGLEBIN coveritems with names ``"0 -> 1"`` and ``"1 -> 0"`` (in that
  order).
* Two consecutive entries are consumed from ``counts.bin``: first the
  ``"0 -> 1"`` count, then the ``"1 -> 0"`` count.

No child scope records follow a TOGGLE_PAIR.

6.4 Scope-type integer values
==============================

The ``scope_type`` varint uses the integer values of ``ScopeTypeT``.
The most common values are:

.. list-table::
   :header-rows: 1
   :widths: 15 45 40

   * - Value
     - ScopeTypeT name
     - Typical context
   * - 2
     - ``DU_MODULE``
     - Design-unit scope for a Verilog module
   * - 16
     - ``INSTANCE``
     - Instantiation of a design unit
   * - 22
     - ``COVERGROUP``
     - SystemVerilog covergroup type or instance
   * - 23
     - ``COVERPOINT``
     - SystemVerilog coverpoint
   * - 28
     - ``CROSS``
     - SystemVerilog cross
   * - 30
     - ``BRANCH``
     - Code-coverage branch (toggle pair or regular)
   * - 32
     - ``TOGGLE``
     - Toggle scope (parent of BRANCH scopes)
   * - 33
     - ``FSM``
     - Finite state machine
   * - 36
     - ``BLOCK``
     - Statement block

The full set of values is defined in ``ucis/scope_type_t.py``.

-----------

********************
7. counts.bin
********************

A flat array of non-negative integers, one per coveritem, in the **same DFS
order** as the coveritems encountered while reading ``scope_tree.bin``.  TOGGLE_PAIR
scopes contribute two consecutive counts (``"0 -> 1"`` then ``"1 -> 0"``).

The array length is given by ``coveritem_count`` in ``manifest.json``.

7.1 Binary layout
==================

.. code-block:: text

   [mode  : 1 byte ]  0 = UINT32, 1 = VARINT
   [count : varint ]  number of integers that follow
   [data  : …      ]  mode-dependent encoding (see below)

**Mode 0 — UINT32:**
Each integer is a 4-byte little-endian unsigned 32-bit value.  Used when
most counts are large (i.e. varint encoding would not save space).

.. code-block:: text

   [v_0 : 4 bytes LE] [v_1 : 4 bytes LE] … [v_{n-1} : 4 bytes LE]

**Mode 1 — VARINT:**
Each integer is encoded as an unsigned LEB128 varint
(see :ref:`ncdb-varint`).  Used when most counts are small (0–127), which is
the common case for per-test databases.

.. code-block:: text

   [varint_0] [varint_1] … [varint_{n-1}]

**Mode selection:** The writer computes both encodings and selects VARINT when
``len(varint_encoding) < count × 4`` (i.e. when it is strictly smaller),
falling back to UINT32 otherwise.  A reader must support both modes.

7.2 Efficient single-byte fast path
=====================================

When mode is VARINT and all values fit in a single byte (0–127), each byte in
the data section is equal to the corresponding count value (the high bit is
never set).  A parser can exploit this: scan the data section for any byte
≥ 0x80; if none are found, each byte *is* its value, and the entire section
can be decoded with a single ``bytes → list`` conversion.

-----------

********************
8. history.json
********************

A JSON array of history node records.  Each element represents either a test
run (``kind: "TEST"``) or a merge operation (``kind: "MERGE"``).

**Record schema:**

.. code-block:: json

   [
     {
       "name":          "regression_seed_42",
       "parent":        null,
       "kind":          "TEST",
       "teststatus":    0,
       "toolcategory":  "sim",
       "date":          "2026-02-25",
       "simtime":       1500.0,
       "timeunit":      "ns",
       "runcwd":        "/home/user/sim",
       "cputime":       12.3,
       "seed":          "42",
       "cmd":           "vsim -seed 42 top",
       "args":          "",
       "user":          "jsmith",
       "cost":          0.0
     }
   ]

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Field
     - Type
     - Description
   * - ``name``
     - string
     - Unique name for this history node (test name or merge label).
   * - ``parent``
     - string | null
     - Name of the parent history node, or ``null`` for a root node.
   * - ``kind``
     - ``"TEST"`` | ``"MERGE"``
     - History node kind.
   * - ``teststatus``
     - integer
     - Test status code: 0 = OK, 1 = WARNING, 2 = ERROR, 3 = FATAL,
       4 = NOTRUN.
   * - ``toolcategory``
     - string
     - Free-form tool category (e.g. ``"sim"``, ``"formal"``).
   * - ``date``
     - string
     - Date string (ISO 8601 recommended).
   * - ``simtime``
     - number
     - Simulation end time in ``timeunit`` units.
   * - ``timeunit``
     - string
     - Simulation time unit (e.g. ``"ns"``, ``"ps"``).
   * - ``runcwd``
     - string
     - Working directory of the simulation run.
   * - ``cputime``
     - number
     - CPU seconds consumed.
   * - ``seed``
     - string
     - Random seed used.
   * - ``cmd``
     - string
     - Simulator command line.
   * - ``args``
     - string
     - Additional arguments.
   * - ``user``
     - string
     - Username that ran the simulation.
   * - ``cost``
     - number
     - Simulation cost (tool-defined).

-----------

********************
9. sources.json
********************

A JSON array of strings, where each element is an absolute or relative file
path.  The position of each path in the array is its **file ID**, which is the
integer used as ``file_id`` in ``scope_tree.bin`` source references.

.. code-block:: json

   [
     "/home/user/design/top.sv",
     "/home/user/design/alu.sv",
     "/home/user/tb/coverage_pkg.sv"
   ]

File ID 0 corresponds to the first element.  An empty ``sources.json`` (``[]``)
is valid when no source information was recorded.

-----------

.. _ncdb-merge:

**************************
10. Merging NCDB files
**************************

The key performance advantage of NCDB over SQLite is the **same-schema fast
merge path**, which reduces a multi-file merge to element-wise integer addition.

10.1 Same-schema fast merge
============================

Two NCDB files are *schema-compatible* if and only if their ``schema_hash``
values are equal.  The ``schema_hash`` is ``"sha256:"`` followed by the
SHA-256 digest of the uncompressed ``scope_tree.bin`` bytes; equal hashes
guarantee an identical scope hierarchy and coveritem ordering.

**Algorithm for merging N same-schema files into one output file:**

1. Read ``manifest.json`` from all N sources.  Verify ``schema_hash`` is
   identical for all; if not, fall back to the cross-schema path.
2. Read ``counts.bin`` from all N sources → N lists of integers.
3. Compute the merged count array: element-wise sum of all N lists.
   (In Python: ``list(map(sum, zip(*all_counts)))``)
4. Concatenate all ``history.json`` arrays from all sources.  Append a new
   MERGE history node that references all source names.
5. Copy ``strings.bin``, ``scope_tree.bin``, and ``sources.json`` verbatim
   from the first source (they are identical for same-schema files).
6. Write the output ZIP with the merged manifest, the copied schema members,
   the merged ``counts.bin``, and the combined ``history.json``.

The scope tree and string table never need to be decoded for a same-schema
merge.

10.2 Cross-schema merge
========================

When the schema hashes differ, the merger must parse both scope trees, match
scopes by ``(path, type, name)`` key, and add counts for matched coveritems.
Unmatched coveritems from either source are appended with their original
counts.  This path is slower but correct for merging databases from designs
that have evolved between runs.

10.3 Merge history node
========================

A merge operation appends a ``"MERGE"``-kind history node to ``history.json``:

.. code-block:: json

   {
     "name":   "merge:output.cdb",
     "parent": null,
     "kind":   "MERGE",
     "teststatus": 0,
     "toolcategory": "merge",
     "date":   "2026-02-25T21:00:00Z"
   }

-----------

*******************************
11. Optional binary members
*******************************

These members are omitted from the archive when the corresponding data is
absent or all-default.  Readers must silently skip any optional member they
do not support, and must not fail if an expected optional member is absent.

11.1 attrs.bin
==============

User-defined attribute assignments for scopes and coveritems.

11.2 tags.json
==============

Tag assignments.  A JSON object mapping tag names to arrays of scope paths.

11.3 toggle.bin
================

Per-signal toggle metadata for ``TOGGLE``-type scopes.  Records the
canonical signal name, toggle type (NET, REG, …), and direction (IN, OUT, …).

11.4 fsm.bin
=============

FSM metadata for ``FSM``-type scopes.  Records state names and transition
labels that correspond to coveritems in ``counts.bin``.

11.5 contrib/NNNNN.bin
=======================

Per-test contribution arrays.  One file per test (zero-padded 5-digit
sequence number matches the TEST history node order).  Each file encodes a
sparse, delta-encoded array of per-test hit counts, allowing reconstruction
of which tests hit which bins.

-----------

***********************
12. Version history
***********************

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - Version
     - Changes
   * - ``1.0``
     - Initial release.  Scope-tree V2 encoding with presence bitfield and
       TOGGLE_PAIR optimization.  Varint + UINT32 dual-mode counts encoding.
       Same-schema fast-merge path via ``schema_hash``.

-----------

.. _ncdb-benchmarks:

*************************************
13. Size and performance reference
*************************************

Measurements using synthetic BM1–BM6 benchmark databases (pure Python,
no C accelerator, median of 3 merge runs):

.. list-table::
   :header-rows: 1
   :widths: 20 10 16 12 16 12 14

   * - Workload
     - Bins
     - SQLite/test
     - NCDB/test
     - Size ratio
     - SQLite merge
     - NCDB merge
   * - BM1 Counter
     - 5
     - 276 KB
     - 1.3 KB
     - **209×**
     - 22 ms
     - 1.2 ms
   * - BM2 ALU
     - 104
     - 276 KB
     - 1.4 KB
     - **196×**
     - 24 ms
     - 1.7 ms
   * - BM3 Protocol
     - 180
     - 276 KB
     - 1.4 KB
     - **195×**
     - 29 ms
     - 3.5 ms
   * - BM4 Hierarchy
     - 117
     - 276 KB
     - 1.4 KB
     - **195×**
     - 28 ms
     - 4.0 ms
   * - BM5 Bins (8K)
     - 8 800
     - 276 KB
     - 2.3 KB
     - **122×**
     - 40 ms
     - 17 ms
   * - BM6 SoC
     - 256
     - 276 KB
     - 1.4 KB
     - **192×**
     - 72 ms
     - 12 ms

*Merge seed counts: BM1=4, BM2=16, BM3=32, BM4=32, BM5=64, BM6=128.*

The SQLite per-test size is dominated by the fixed B-tree page overhead
(minimum 276 KB regardless of design size).  NCDB scales with actual data:
a design with 5 bins uses only 1.3 KB.

With a C accelerator for varint encode/decode, BM5 merge time is projected
to drop to ~5 ms (~7.5× faster than SQLite).

-----------

*****************************
14. Implementing a reader
*****************************

To read an NCDB file without PyUCIS:

.. code-block:: python

   import zipfile, json, struct, hashlib

   def read_varint(data, offset):
       result, shift = 0, 0
       while True:
           b = data[offset]; offset += 1
           result |= (b & 0x7F) << shift
           shift += 7
           if not (b & 0x80):
               return result, offset

   def read_ncdb(path):
       with zipfile.ZipFile(path) as zf:
           manifest = json.loads(zf.read("manifest.json"))
           assert manifest["format"] == "NCDB"

           strings_raw = zf.read("strings.bin")
           counts_raw  = zf.read("counts.bin")
           history     = json.loads(zf.read("history.json"))
           sources     = json.loads(zf.read("sources.json"))

       # Decode string table
       offset = 0
       n_strings, offset = read_varint(strings_raw, offset)
       strings = []
       for _ in range(n_strings):
           length, offset = read_varint(strings_raw, offset)
           strings.append(strings_raw[offset:offset+length].decode("utf-8"))
           offset += length

       # Decode counts
       mode = counts_raw[0]; offset = 1
       n_counts, offset = read_varint(counts_raw, offset)
       counts = []
       if mode == 1:  # VARINT
           # Fast path: all single-byte values
           payload = counts_raw[offset:offset + n_counts]
           if len(payload) == n_counts and all(b < 0x80 for b in payload):
               counts = list(payload)
           else:
               for _ in range(n_counts):
                   v, offset = read_varint(counts_raw, offset)
                   counts.append(v)
       else:  # UINT32
           counts = list(struct.unpack_from(f"<{n_counts}I", counts_raw, offset))

       return {
           "manifest": manifest,
           "strings":  strings,
           "counts":   counts,
           "history":  history,
           "sources":  sources,
       }

.. seealso::

   * :doc:`sqlite-schema` — SQLite backend schema reference
   * :doc:`xml-interchange` — XML interchange format
   * :ref:`working-with-coverage-merging` — How to merge databases using the CLI
