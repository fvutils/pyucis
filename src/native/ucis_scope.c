/**
 * @file ucis_scope.c
 * @brief Scope creation and management
 */

#include "ucis_impl.h"
#include "ucis.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

/* Helper to get database context from handle */
static ucis_db_context_t* get_db_context(ucisT db) {
    if (!ucis_validate_handle(db, UCIS_HANDLE_DB)) return NULL;
    ucis_handle_entry_t* entry = ucis_get_handle_entry(db);
    return (ucis_db_context_t*)entry->cached_data;
}

ucisScopeT ucis_CreateScope(
    ucisT db,
    ucisScopeT parent,
    const char* name,
    ucisSourceInfoT* source,
    int weight,
    ucisSourceT source_type,
    ucisScopeTypeT type,
    int flags)
{
    ucis_db_context_t* ctx = get_db_context(db);
    if (!ctx || !name) return NULL;
    
    /* Get parent ID if parent provided */
    int64_t parent_id = 0;
    int has_parent = 0;
    
    if (parent) {
        if (!ucis_validate_handle(parent, UCIS_HANDLE_SCOPE)) {
            ucis_set_error(ctx, "Invalid parent scope handle");
            return NULL;
        }
        ucis_handle_entry_t* parent_entry = ucis_get_handle_entry(parent);
        parent_id = parent_entry->primary_key;
        has_parent = 1;
    }
    
    /* Get source file ID if provided */
    int64_t source_file_id = 0;
    int has_source = 0;
    
    if (source && source->filehandle) {
        if (!ucis_validate_handle(source->filehandle, UCIS_HANDLE_FILE)) {
            ucis_set_error(ctx, "Invalid file handle");
            return NULL;
        }
        ucis_handle_entry_t* file_entry = ucis_get_handle_entry(source->filehandle);
        source_file_id = file_entry->primary_key;
        has_source = 1;
    }
    
    /* Prepare INSERT statement */
    const char* sql = 
        "INSERT INTO scopes (parent_id, scope_type, scope_name, scope_flags, "
        "weight, source_file_id, source_line, source_token, language_type) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)";
    
    sqlite3_stmt* stmt;
    int rc = sqlite3_prepare_v2(ctx->db, sql, -1, &stmt, NULL);
    
    if (rc != SQLITE_OK) {
        ucis_set_error(ctx, "Failed to prepare scope insert: %s", 
                      sqlite3_errmsg(ctx->db));
        return NULL;
    }
    
    /* Bind parameters */
    int idx = 1;
    
    if (has_parent) {
        sqlite3_bind_int64(stmt, idx++, parent_id);
    } else {
        sqlite3_bind_null(stmt, idx++);
    }
    
    sqlite3_bind_int(stmt, idx++, (int)type);
    sqlite3_bind_text(stmt, idx++, name, -1, SQLITE_TRANSIENT);
    sqlite3_bind_int(stmt, idx++, flags);
    sqlite3_bind_int(stmt, idx++, weight);
    
    if (has_source) {
        sqlite3_bind_int64(stmt, idx++, source_file_id);
        sqlite3_bind_int(stmt, idx++, source->line);
        sqlite3_bind_int(stmt, idx++, source->token);
    } else {
        sqlite3_bind_null(stmt, idx++);
        sqlite3_bind_null(stmt, idx++);
        sqlite3_bind_null(stmt, idx++);
    }
    
    sqlite3_bind_int(stmt, idx++, (int)source_type);
    
    /* Execute */
    rc = sqlite3_step(stmt);
    
    if (rc != SQLITE_DONE) {
        ucis_set_error(ctx, "Failed to insert scope: %s", 
                      sqlite3_errmsg(ctx->db));
        sqlite3_finalize(stmt);
        return NULL;
    }
    
    /* Get inserted row ID */
    int64_t scope_id = sqlite3_last_insert_rowid(ctx->db);
    sqlite3_finalize(stmt);
    
    /* Create handle */
    ucisScopeT handle = ucis_alloc_handle(UCIS_HANDLE_SCOPE, ctx->db, scope_id);
    
    return handle;
}

ucisScopeT ucis_CreateInstance(
    ucisT db,
    ucisScopeT parent,
    const char* name,
    ucisSourceInfoT* source,
    int weight,
    ucisSourceT source_type)
{
    return ucis_CreateScope(db, parent, name, source, weight, 
                           source_type, UCIS_INSTANCE, 0);
}

const char* ucis_GetScopeName(ucisT db, ucisScopeT scope) {
    ucis_db_context_t* ctx = get_db_context(db);
    if (!ctx) return NULL;
    
    if (!ucis_validate_handle(scope, UCIS_HANDLE_SCOPE)) {
        ucis_set_error(ctx, "Invalid scope handle");
        return NULL;
    }
    
    ucis_handle_entry_t* entry = ucis_get_handle_entry(scope);
    int64_t scope_id = entry->primary_key;
    
    /* Check if name is cached */
    if (entry->cached_data) {
        return (const char*)entry->cached_data;
    }
    
    /* Query database */
    const char* sql = "SELECT scope_name FROM scopes WHERE scope_id = ?";
    sqlite3_stmt* stmt;
    
    int rc = sqlite3_prepare_v2(ctx->db, sql, -1, &stmt, NULL);
    if (rc != SQLITE_OK) return NULL;
    
    sqlite3_bind_int64(stmt, 1, scope_id);
    
    rc = sqlite3_step(stmt);
    if (rc == SQLITE_ROW) {
        const char* name = (const char*)sqlite3_column_text(stmt, 0);
        if (name) {
            /* Cache the name */
            entry->cached_data = ucis_strdup(name);
        }
        sqlite3_finalize(stmt);
        return (const char*)entry->cached_data;
    }
    
    sqlite3_finalize(stmt);
    return NULL;
}

ucisScopeTypeT ucis_GetScopeType(ucisT db, ucisScopeT scope) {
    ucis_db_context_t* ctx = get_db_context(db);
    if (!ctx) return 0;
    
    if (!ucis_validate_handle(scope, UCIS_HANDLE_SCOPE)) {
        ucis_set_error(ctx, "Invalid scope handle");
        return 0;
    }
    
    ucis_handle_entry_t* entry = ucis_get_handle_entry(scope);
    int64_t scope_id = entry->primary_key;
    
    /* Query database */
    const char* sql = "SELECT scope_type FROM scopes WHERE scope_id = ?";
    sqlite3_stmt* stmt;
    
    int rc = sqlite3_prepare_v2(ctx->db, sql, -1, &stmt, NULL);
    if (rc != SQLITE_OK) return 0;
    
    sqlite3_bind_int64(stmt, 1, scope_id);
    
    rc = sqlite3_step(stmt);
    ucisScopeTypeT type = 0;
    
    if (rc == SQLITE_ROW) {
        type = (ucisScopeTypeT)sqlite3_column_int(stmt, 0);
    }
    
    sqlite3_finalize(stmt);
    return type;
}

ucisScopeT ucis_GetParent(ucisT db, ucisScopeT scope) {
    ucis_db_context_t* ctx = get_db_context(db);
    if (!ctx) return NULL;
    
    if (!ucis_validate_handle(scope, UCIS_HANDLE_SCOPE)) {
        ucis_set_error(ctx, "Invalid scope handle");
        return NULL;
    }
    
    ucis_handle_entry_t* entry = ucis_get_handle_entry(scope);
    int64_t scope_id = entry->primary_key;
    
    /* Query database */
    const char* sql = "SELECT parent_id FROM scopes WHERE scope_id = ?";
    sqlite3_stmt* stmt;
    
    int rc = sqlite3_prepare_v2(ctx->db, sql, -1, &stmt, NULL);
    if (rc != SQLITE_OK) return NULL;
    
    sqlite3_bind_int64(stmt, 1, scope_id);
    
    rc = sqlite3_step(stmt);
    ucisScopeT parent = NULL;
    
    if (rc == SQLITE_ROW) {
        if (sqlite3_column_type(stmt, 0) != SQLITE_NULL) {
            int64_t parent_id = sqlite3_column_int64(stmt, 0);
            parent = ucis_alloc_handle(UCIS_HANDLE_SCOPE, ctx->db, parent_id);
        }
    }
    
    sqlite3_finalize(stmt);
    return parent;
}

int ucis_SetScopeWeight(ucisT db, ucisScopeT scope, int weight) {
    ucis_db_context_t* ctx = get_db_context(db);
    if (!ctx) return -1;
    
    if (!ucis_validate_handle(scope, UCIS_HANDLE_SCOPE)) {
        ucis_set_error(ctx, "Invalid scope handle");
        return -1;
    }
    
    ucis_handle_entry_t* entry = ucis_get_handle_entry(scope);
    int64_t scope_id = entry->primary_key;
    
    const char* sql = "UPDATE scopes SET weight = ? WHERE scope_id = ?";
    sqlite3_stmt* stmt;
    
    int rc = sqlite3_prepare_v2(ctx->db, sql, -1, &stmt, NULL);
    if (rc != SQLITE_OK) return -1;
    
    sqlite3_bind_int(stmt, 1, weight);
    sqlite3_bind_int64(stmt, 2, scope_id);
    
    rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    
    return (rc == SQLITE_DONE) ? 0 : -1;
}

int ucis_SetScopeGoal(ucisT db, ucisScopeT scope, int goal) {
    ucis_db_context_t* ctx = get_db_context(db);
    if (!ctx) return -1;
    
    if (!ucis_validate_handle(scope, UCIS_HANDLE_SCOPE)) {
        ucis_set_error(ctx, "Invalid scope handle");
        return -1;
    }
    
    ucis_handle_entry_t* entry = ucis_get_handle_entry(scope);
    int64_t scope_id = entry->primary_key;
    
    const char* sql = "UPDATE scopes SET goal = ? WHERE scope_id = ?";
    sqlite3_stmt* stmt;
    
    int rc = sqlite3_prepare_v2(ctx->db, sql, -1, &stmt, NULL);
    if (rc != SQLITE_OK) return -1;
    
    sqlite3_bind_int(stmt, 1, goal);
    sqlite3_bind_int64(stmt, 2, scope_id);
    
    rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    
    return (rc == SQLITE_DONE) ? 0 : -1;
}

int ucis_SetScopeFlags(ucisT db, ucisScopeT scope, int flags) {
    ucis_db_context_t* ctx = get_db_context(db);
    if (!ctx) return -1;
    
    if (!ucis_validate_handle(scope, UCIS_HANDLE_SCOPE)) {
        ucis_set_error(ctx, "Invalid scope handle");
        return -1;
    }
    
    ucis_handle_entry_t* entry = ucis_get_handle_entry(scope);
    int64_t scope_id = entry->primary_key;
    
    const char* sql = "UPDATE scopes SET scope_flags = ? WHERE scope_id = ?";
    sqlite3_stmt* stmt;
    
    int rc = sqlite3_prepare_v2(ctx->db, sql, -1, &stmt, NULL);
    if (rc != SQLITE_OK) return -1;
    
    sqlite3_bind_int(stmt, 1, flags);
    sqlite3_bind_int64(stmt, 2, scope_id);
    
    rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    
    return (rc == SQLITE_DONE) ? 0 : -1;
}
