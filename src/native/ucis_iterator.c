/**
 * @file ucis_iterator.c
 * @brief Iterator implementations for scopes and coverage
 */

#include "ucis_impl.h"
#include "ucis.h"
#include <stdlib.h>

/* Helper to get database context */
static ucis_db_context_t* get_db_context(ucisT db) {
    if (!ucis_validate_handle(db, UCIS_HANDLE_DB)) return NULL;
    ucis_handle_entry_t* entry = ucis_get_handle_entry(db);
    return (ucis_db_context_t*)entry->cached_data;
}

int ucis_ScopeIterate(
    ucisT db,
    ucisScopeT parent,
    ucisScopeTypeT type_mask,
    ucisScopeCBT callback,
    void* userdata)
{
    ucis_db_context_t* ctx = get_db_context(db);
    if (!ctx || !callback) return -1;
    
    /* Get parent ID if provided */
    int64_t parent_id = 0;
    int has_parent = 0;
    
    if (parent) {
        if (!ucis_validate_handle(parent, UCIS_HANDLE_SCOPE)) {
            ucis_set_error(ctx, "Invalid parent scope handle");
            return -1;
        }
        ucis_handle_entry_t* parent_entry = ucis_get_handle_entry(parent);
        parent_id = parent_entry->primary_key;
        has_parent = 1;
    }
    
    /* Build query based on parameters */
    const char* sql;
    
    if (has_parent && type_mask != 0) {
        sql = "SELECT scope_id FROM scopes WHERE parent_id = ? AND (scope_type & ?) != 0 ORDER BY scope_id";
    } else if (has_parent) {
        sql = "SELECT scope_id FROM scopes WHERE parent_id = ? ORDER BY scope_id";
    } else if (type_mask != 0) {
        sql = "SELECT scope_id FROM scopes WHERE parent_id IS NULL AND (scope_type & ?) != 0 ORDER BY scope_id";
    } else {
        sql = "SELECT scope_id FROM scopes WHERE parent_id IS NULL ORDER BY scope_id";
    }
    
    sqlite3_stmt* stmt;
    int rc = sqlite3_prepare_v2(ctx->db, sql, -1, &stmt, NULL);
    
    if (rc != SQLITE_OK) {
        ucis_set_error(ctx, "Failed to prepare scope iteration: %s", 
                      sqlite3_errmsg(ctx->db));
        return -1;
    }
    
    /* Bind parameters */
    int param_idx = 1;
    
    if (has_parent) {
        sqlite3_bind_int64(stmt, param_idx++, parent_id);
    }
    
    if (type_mask != 0) {
        sqlite3_bind_int(stmt, param_idx++, (int)type_mask);
    }
    
    /* Iterate and call callback */
    int count = 0;
    
    while ((rc = sqlite3_step(stmt)) == SQLITE_ROW) {
        int64_t scope_id = sqlite3_column_int64(stmt, 0);
        
        /* Create handle for this scope */
        ucisScopeT scope_handle = ucis_alloc_handle(UCIS_HANDLE_SCOPE, ctx->db, scope_id);
        
        /* Call callback */
        int result = callback(userdata, scope_handle);
        
        count++;
        
        /* Check if callback wants to stop */
        if (result != 0) {
            break;
        }
    }
    
    sqlite3_finalize(stmt);
    
    return count;
}

int ucis_CoverIterate(
    ucisT db,
    ucisScopeT parent,
    ucisCoverCBT callback,
    void* userdata)
{
    ucis_db_context_t* ctx = get_db_context(db);
    if (!ctx || !callback) return -1;
    
    if (!ucis_validate_handle(parent, UCIS_HANDLE_SCOPE)) {
        ucis_set_error(ctx, "Invalid parent scope handle");
        return -1;
    }
    
    ucis_handle_entry_t* parent_entry = ucis_get_handle_entry(parent);
    int64_t parent_id = parent_entry->primary_key;
    
    /* Query all coverage items in this scope */
    const char* sql = "SELECT cover_id FROM coveritems WHERE scope_id = ? ORDER BY cover_index";
    
    sqlite3_stmt* stmt;
    int rc = sqlite3_prepare_v2(ctx->db, sql, -1, &stmt, NULL);
    
    if (rc != SQLITE_OK) {
        ucis_set_error(ctx, "Failed to prepare cover iteration: %s", 
                      sqlite3_errmsg(ctx->db));
        return -1;
    }
    
    sqlite3_bind_int64(stmt, 1, parent_id);
    
    /* Iterate and call callback */
    int count = 0;
    
    while ((rc = sqlite3_step(stmt)) == SQLITE_ROW) {
        int64_t cover_id = sqlite3_column_int64(stmt, 0);
        
        /* Create handle for this cover */
        ucisCoverT cover_handle = ucis_alloc_handle(UCIS_HANDLE_COVER, ctx->db, cover_id);
        
        /* Call callback */
        int result = callback(userdata, cover_handle);
        
        count++;
        
        /* Check if callback wants to stop */
        if (result != 0) {
            break;
        }
    }
    
    sqlite3_finalize(stmt);
    
    return count;
}

int ucis_HistoryNodeIterate(
    ucisT db,
    ucisHistoryNodeKindT kind,
    ucisHistoryNodeCBT callback,
    void* userdata)
{
    ucis_db_context_t* ctx = get_db_context(db);
    if (!ctx || !callback) return -1;
    
    /* Build query based on kind filter */
    const char* sql;
    
    if (kind != 0) {
        sql = "SELECT history_id FROM history_nodes WHERE (history_kind & ?) != 0 ORDER BY history_id";
    } else {
        sql = "SELECT history_id FROM history_nodes ORDER BY history_id";
    }
    
    sqlite3_stmt* stmt;
    int rc = sqlite3_prepare_v2(ctx->db, sql, -1, &stmt, NULL);
    
    if (rc != SQLITE_OK) {
        ucis_set_error(ctx, "Failed to prepare history iteration: %s", 
                      sqlite3_errmsg(ctx->db));
        return -1;
    }
    
    if (kind != 0) {
        sqlite3_bind_int(stmt, 1, (int)kind);
    }
    
    /* Iterate and call callback */
    int count = 0;
    
    while ((rc = sqlite3_step(stmt)) == SQLITE_ROW) {
        int64_t history_id = sqlite3_column_int64(stmt, 0);
        
        /* Create handle for this history node */
        ucisHistoryNodeT history_handle = ucis_alloc_handle(UCIS_HANDLE_HISTORY, ctx->db, history_id);
        
        /* Call callback */
        int result = callback(userdata, history_handle);
        
        count++;
        
        /* Check if callback wants to stop */
        if (result != 0) {
            break;
        }
    }
    
    sqlite3_finalize(stmt);
    
    return count;
}
