
# Tables

DatabaseInfo
  - schemaVersion
  - createdDate
  - 

HistoryNodes
  - nodeId (primary for this table)
  - parentId (references nodeId in HistoryNodes)
  - logicalName
  - physicalName
  - kind (TEST | MERGE)
  - ucisTestStatusT teststatus;
  - double simtime;
  - const char* timeunit;
  - const char* runcwd;
  - double cputime;
  - const char* seed;
  - const char* cmd;
  - const char* args;
  - int compulsory;

HistoryBlobAttr
  - parentId
  - key
  - value

HistoryIntAttr
  - parentId
  - key
  - value

HistoryStrAttr
  - parentId
  - key
  - value

HistoryRealAttr
  - parentId
  - key
  - value

<!-- 

The set of attributes is fixed. Let's just leave it at that...

HistoryNodeIntProperties
  - parentId (references nodeId in HistoryNodes)
  - kind
  - value

HistoryNodeRealProperties
  - parentId (references nodeId in HistoryNodes)
  - kind
  - value

HistoryNodeStrProperties
  - parentId (references nodeId in HistoryNodes)
  - kind
  - value 
-->

Scopes
  - scopeId (primary for this table)
  - name
  - scopeType (64-bit bitmask)
  - parentId (references scopeId in Scopes)
  - fileId or NULL (references fileId in Files)
  - lineNo or NULL

Files
  - fileId (primary for this table)
  - path

ScopeIntProperties
  - parentId (references scopeId in Scopes)
  - coverIndex
  - kind
  - value

ScopeStrProperties
  - parentId (references scopeId in Scopes)
  - coverIndex
  - kind
  - value

ScopeRealProperties
  - parentId (references scopeId in Scopes)
  - coverIndex
  - kind
  - value

ScopeBlobAttr
  - parentId
  - coverIndex
  - key
  - value

ScopeIntAttr
  - parentId
  - coverIndex
  - key
  - value

ScopeStrAttr
  - parentId
  - coverIndex
  - key
  - value

ScopeRealAttr
  - parentId
  - coverIndex
  - key
  - value

CoverData
  - coverId (primary for this table)
  - parentId (references scopeId in Scopes)
  - type
  - flags
  - coverIndex 
  - count (int64 count)

CoverDataGoal # Only store if requested
  - coverId
  - goal (at-least)

CoverDataWeight # Only store if requested
  - coverId
  - weight 

CoverDataLimit # Only store if requested
  - coverId
  - limit


CoverBins
  - fileId
  - parentId (references scopeId in Scopes)
  - coverIndex 
  - name
  - at_least
  - count
  - kind
  - weight


- files (?)
- testhistory
- scopes
- coverInstances
- covergroups
- coveritems

