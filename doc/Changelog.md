
## 0.1.7 (Unreleased)
- **File Extension Change:** SQLite databases now use `.cdb` (Coverage DataBase) extension
- **Database Identification:** Added two-level validation system:
  - Level 1: Verify file is a valid SQLite database (SQLite header check)
  - Level 2: Verify it's a PyUCIS database (DATABASE_TYPE marker + required tables)
  - Automatic validation when opening databases with descriptive error messages
- **SQLite Schema v2.1:** Optimized for merge performance and storage efficiency
  - Removed 7 unused indexes (30-40% storage overhead reduction)
  - No query performance impact from index removal
  - Schema version tracking in db_metadata table
- **Merge Optimizations:** 
  - Added `squash_history` parameter to merge APIs for large-scale merges
  - Optional history squashing eliminates per-test history row growth
  - Coverage data accuracy identical in both squashed and non-squashed modes
- **CLI Enhancement:** Added `--squash-history` flag to merge command
- **Test Coverage:** Added 13 new tests (5 validation + 8 optimization tests)
- **Breaking Change:** Databases from schema v2.0 or earlier must be recreated
  - Opening incompatible schema versions now raises descriptive error
  - Non-PyUCIS databases rejected with clear error messages

## 0.1.6 (Unreleased)
- Fixed XML schema bug: coverpoint minOccurs changed from 1 to 0 (matches UCIS spec)
- Implemented complete XML options read/write support (weight, goal, at_least, per_instance, etc.)
- Verified XML cross coverage fully functional (was incorrectly thought to have limitations)
- Removed pytest-asyncio dependency (converted to asyncio.run())
- Fixed method name typo: getFilename → getFileName (per UCIS spec)
- Improved test coverage: 179 → 198 passing tests (95.7% pass rate)
- Documented all legitimate XML format limitations per UCIS schema

## 0.1.5
- (#26) - Correct a whitespace issue found during bytecode pre-compilation 

## 0.1.4
- Update XML writer to properly emit ignore and illegal bins
- Update XML reader to properly read crossExpr elements

## 0.1.3
- Adjust XML reader to reconstruct type coverage based on
  instance coverage saved in the UCIS XML file

## 0.1.2
- Tweaks to merge command and merged-xml output

## 0.1.1
- Tweaks to text reporting

## 0.1.0
- Correct an issue with type-coverage calculation

## 0.0.9
- Adjust dependencies 

## 0.0.8
- Progress on new command format and plug-in architecture
- Labeling this with a new version number just for tracking purposes

## 0.0.7
- Adjust the format of the XML slightly. Now, a single
  cgInstance specifies type coverage, while multiple
  cgInstances specify instance coverage from which 
  type coverage is derived by the reader.

## 0.0.6
- Adjust two aspects of the output XML-file format for
  better compatibility with external tools. 
  - Emit a 'range' element for each coverpoint bin
  - Emit one crossExpr element for each cross component

## 0.0.5
- Add support for ignore and illegal coverpoint bins

## 0.0.3
- Ensure XML file is read back correctly

## 0.0.2
- Ensure coverpoint crosses are properly reported
