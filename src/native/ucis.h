/**
 * @file ucis.h
 * @brief UCIS 1.0 C API - Public Interface
 * 
 * Complete implementation of the Unified Coverage Interoperability Standard
 * Version 1.0 C API using SQLite3 as the backend storage.
 */

#ifndef UCIS_H
#define UCIS_H

#include "ucis_types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* ========================================================================
 * Database Lifecycle Functions
 * ======================================================================== */

/**
 * Open or create a UCIS database
 * @param name File path or NULL for in-memory database
 * @return Database handle or NULL on error
 */
ucisT ucis_Open(const char* name);

/**
 * Close a UCIS database
 * @param db Database handle
 */
void ucis_Close(ucisT db);

/**
 * Write database to file
 * @param db Database handle
 * @param name File path to write to
 * @return 0 on success, non-zero on error
 */
int ucis_Write(ucisT db, const char* name);

/**
 * Get UCIS API version
 * @return Version string (e.g., "1.0")
 */
const char* ucis_GetAPIVersion(void);

/* ========================================================================
 * Scope Operations
 * ======================================================================== */

/**
 * Create a new scope
 */
ucisScopeT ucis_CreateScope(
    ucisT db,
    ucisScopeT parent,
    const char* name,
    ucisSourceInfoT* source,
    int weight,
    ucisSourceT source_type,
    ucisScopeTypeT type,
    int flags);

/**
 * Create an instance scope (convenience wrapper)
 */
ucisScopeT ucis_CreateInstance(
    ucisT db,
    ucisScopeT parent,
    const char* name,
    ucisSourceInfoT* source,
    int weight,
    ucisSourceT source_type);

/**
 * Get scope name
 */
const char* ucis_GetScopeName(ucisT db, ucisScopeT scope);

/**
 * Get scope type
 */
ucisScopeTypeT ucis_GetScopeType(ucisT db, ucisScopeT scope);

/**
 * Get parent scope
 */
ucisScopeT ucis_GetParent(ucisT db, ucisScopeT scope);

/**
 * Set scope weight
 */
int ucis_SetScopeWeight(ucisT db, ucisScopeT scope, int weight);

/**
 * Set scope goal
 */
int ucis_SetScopeGoal(ucisT db, ucisScopeT scope, int goal);

/**
 * Set scope flags
 */
int ucis_SetScopeFlags(ucisT db, ucisScopeT scope, int flags);

/**
 * Iterate over child scopes
 */
int ucis_ScopeIterate(
    ucisT db,
    ucisScopeT parent,
    ucisScopeTypeT type_mask,
    ucisScopeCBT callback,
    void* userdata);

/* ========================================================================
 * Coverage Operations
 * ======================================================================== */

/**
 * Create next coverage item in scope
 */
ucisCoverT ucis_CreateNextCover(
    ucisT db,
    ucisScopeT parent,
    const char* name,
    ucisCoverDataT* data,
    ucisSourceInfoT* source);

/**
 * Get coverage data
 */
int ucis_GetCoverData(
    ucisT db,
    ucisCoverT cover,
    ucisCoverDataT* data);

/**
 * Set coverage data
 */
int ucis_SetCoverData(
    ucisT db,
    ucisCoverT cover,
    ucisCoverDataT* data);

/**
 * Increment coverage count
 */
int ucis_IncrementCoverData(
    ucisT db,
    ucisCoverT cover,
    int64_t increment);

/**
 * Iterate over coverage items in scope
 */
int ucis_CoverIterate(
    ucisT db,
    ucisScopeT parent,
    ucisCoverCBT callback,
    void* userdata);

/* ========================================================================
 * History Node Operations
 * ======================================================================== */

/**
 * Create a history node (test record)
 */
ucisHistoryNodeT ucis_CreateHistoryNode(
    ucisT db,
    ucisHistoryNodeT parent,
    const char* logicalname,
    const char* physicalname,
    ucisHistoryNodeKindT kind);

/**
 * Set test data for history node
 */
int ucis_SetTestData(
    ucisT db,
    ucisHistoryNodeT node,
    ucisTestDataT* data);

/**
 * Get test data from history node
 */
int ucis_GetTestData(
    ucisT db,
    ucisHistoryNodeT node,
    ucisTestDataT* data);

/**
 * Iterate over history nodes
 */
int ucis_HistoryNodeIterate(
    ucisT db,
    ucisHistoryNodeKindT kind,
    ucisHistoryNodeCBT callback,
    void* userdata);

/* ========================================================================
 * Property Operations
 * ======================================================================== */

/**
 * Set integer property
 */
int ucis_SetIntProperty(
    ucisT db,
    void* obj,
    ucisObjKindT obj_kind,
    int key,
    int64_t value);

/**
 * Get integer property
 */
int ucis_GetIntProperty(
    ucisT db,
    void* obj,
    ucisObjKindT obj_kind,
    int key,
    int64_t* value);

/**
 * Set string attribute
 */
int ucis_SetStringAttribute(
    ucisT db,
    void* obj,
    ucisObjKindT obj_kind,
    const char* key,
    const char* value);

/**
 * Get string attribute
 */
const char* ucis_GetStringAttribute(
    ucisT db,
    void* obj,
    ucisObjKindT obj_kind,
    const char* key);

/* ========================================================================
 * File Handle Operations
 * ======================================================================== */

/**
 * Create a file handle
 */
ucisFileHandleT ucis_CreateFileHandle(
    ucisT db,
    const char* filename,
    int table_id);

/* ========================================================================
 * Error Handling
 * ======================================================================== */

/**
 * Get last error message
 */
const char* ucis_GetLastError(ucisT db);

#ifdef __cplusplus
}
#endif

#endif /* UCIS_H */
