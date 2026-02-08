/**
 * @file ucis_cover.c
 * @brief Coverage item operations
 */

#include "ucis_impl.h"
#include "ucis.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

/* Helper to get database context */
static ucis_db_context_t* get_db_context(ucisT db) {
    if (!ucis_validate_handle(db, UCIS_HANDLE_DB)) return NULL;
    ucis_handle_entry_t* entry = ucis_get_handle_entry(db);
    return (ucis_db_context_t*)entry->cached_data;
}

ucisCoverT ucis_CreateNextCover(
    ucisT db,
    ucisScopeT parent,
    const char* name,
    ucisCoverDataT* data,
    ucisSourceInfoT* source)
{
    ucis_db_context_t* ctx = get_db_context(db);
    if (!ctx || !parent || !name || !data) return NULL;
    
    /* Validate parent scope */
    if (!ucis_validate_handle(parent, UCIS_HANDLE_SCOPE)) {
        ucis_set_error(ctx, "Invalid parent scope handle");
        return NULL;
    }
    
    ucis_handle_entry_t* parent_entry = ucis_get_handle_entry(parent);
    int64_t scope_id = parent_entry->primary_key;
    
    /* Get next cover_index for this scope */
    const char* sql_max = "SELECT COALESCE(MAX(cover_index), -1) FROM coveritems WHERE scope_id = ?";
    sqlite3_stmt* stmt;
    
    int rc = sqlite3_prepare_v2(ctx->db, sql_max, -1, &stmt, NULL);
    if (rc != SQLITE_OK) {
        ucis_set_error(ctx, "Failed to query max cover_index: %s", 
                      sqlite3_errmsg(ctx->db));
        return NULL;
    }
    
    sqlite3_bind_int64(stmt, 1, scope_id);
    
    int cover_index = 0;
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        cover_index = sqlite3_column_int(stmt, 0) + 1;
    }
    sqlite3_finalize(stmt);
    
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
    
    /* Insert coveritem */
    const char* sql_insert = 
        "INSERT INTO coveritems (scope_id, cover_index, cover_type, cover_name, "
        "cover_flags, cover_data, cover_data_fec, at_least, weight, goal, "
        "source_file_id, source_line, source_token) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
    
    rc = sqlite3_prepare_v2(ctx->db, sql_insert, -1, &stmt, NULL);
    if (rc != SQLITE_OK) {
        ucis_set_error(ctx, "Failed to prepare cover insert: %s", 
                      sqlite3_errmsg(ctx->db));
        return NULL;
    }
    
    /* Bind parameters */
    int idx = 1;
    sqlite3_bind_int64(stmt, idx++, scope_id);
    sqlite3_bind_int(stmt, idx++, cover_index);
    sqlite3_bind_int(stmt, idx++, data->type);
    sqlite3_bind_text(stmt, idx++, name, -1, SQLITE_TRANSIENT);
    sqlite3_bind_int(stmt, idx++, data->flags);
    sqlite3_bind_int64(stmt, idx++, data->data);
    sqlite3_bind_int64(stmt, idx++, data->data_fec);
    sqlite3_bind_int(stmt, idx++, data->at_least);
    sqlite3_bind_int(stmt, idx++, data->weight);
    
    if (data->goal > 0) {
        sqlite3_bind_int(stmt, idx++, data->goal);
    } else {
        sqlite3_bind_null(stmt, idx++);
    }
    
    if (has_source) {
        sqlite3_bind_int64(stmt, idx++, source_file_id);
        sqlite3_bind_int(stmt, idx++, source->line);
        sqlite3_bind_int(stmt, idx++, source->token);
    } else {
        sqlite3_bind_null(stmt, idx++);
        sqlite3_bind_null(stmt, idx++);
        sqlite3_bind_null(stmt, idx++);
    }
    
    /* Execute */
    rc = sqlite3_step(stmt);
    
    if (rc != SQLITE_DONE) {
        ucis_set_error(ctx, "Failed to insert coveritem: %s", 
                      sqlite3_errmsg(ctx->db));
        sqlite3_finalize(stmt);
        return NULL;
    }
    
    /* Get inserted row ID */
    int64_t cover_id = sqlite3_last_insert_rowid(ctx->db);
    sqlite3_finalize(stmt);
    
    /* Create handle */
    ucisCoverT handle = ucis_alloc_handle(UCIS_HANDLE_COVER, ctx->db, cover_id);
    
    return handle;
}

int ucis_GetCoverData(
    ucisT db,
    ucisCoverT cover,
    ucisCoverDataT* data)
{
    ucis_db_context_t* ctx = get_db_context(db);
    if (!ctx || !data) return -1;
    
    if (!ucis_validate_handle(cover, UCIS_HANDLE_COVER)) {
        ucis_set_error(ctx, "Invalid cover handle");
        return -1;
    }
    
    ucis_handle_entry_t* entry = ucis_get_handle_entry(cover);
    int64_t cover_id = entry->primary_key;
    
    /* Query database */
    const char* sql = 
        "SELECT cover_type, cover_data, cover_data_fec, at_least, "
        "weight, goal, cover_flags "
        "FROM coveritems WHERE cover_id = ?";
    
    sqlite3_stmt* stmt;
    int rc = sqlite3_prepare_v2(ctx->db, sql, -1, &stmt, NULL);
    
    if (rc != SQLITE_OK) {
        ucis_set_error(ctx, "Failed to prepare cover query: %s", 
                      sqlite3_errmsg(ctx->db));
        return -1;
    }
    
    sqlite3_bind_int64(stmt, 1, cover_id);
    
    rc = sqlite3_step(stmt);
    
    if (rc == SQLITE_ROW) {
        data->type = sqlite3_column_int(stmt, 0);
        data->data = sqlite3_column_int64(stmt, 1);
        data->data_fec = sqlite3_column_int64(stmt, 2);
        data->at_least = sqlite3_column_int(stmt, 3);
        data->weight = sqlite3_column_int(stmt, 4);
        
        if (sqlite3_column_type(stmt, 5) != SQLITE_NULL) {
            data->goal = sqlite3_column_int(stmt, 5);
        } else {
            data->goal = 0;
        }
        
        data->flags = sqlite3_column_int(stmt, 6);
        
        sqlite3_finalize(stmt);
        return 0;
    }
    
    sqlite3_finalize(stmt);
    ucis_set_error(ctx, "Cover not found");
    return -1;
}

int ucis_SetCoverData(
    ucisT db,
    ucisCoverT cover,
    ucisCoverDataT* data)
{
    ucis_db_context_t* ctx = get_db_context(db);
    if (!ctx || !data) return -1;
    
    if (!ucis_validate_handle(cover, UCIS_HANDLE_COVER)) {
        ucis_set_error(ctx, "Invalid cover handle");
        return -1;
    }
    
    ucis_handle_entry_t* entry = ucis_get_handle_entry(cover);
    int64_t cover_id = entry->primary_key;
    
    /* Update coveritem */
    const char* sql = 
        "UPDATE coveritems SET "
        "cover_type = ?, cover_data = ?, cover_data_fec = ?, "
        "at_least = ?, weight = ?, goal = ?, cover_flags = ? "
        "WHERE cover_id = ?";
    
    sqlite3_stmt* stmt;
    int rc = sqlite3_prepare_v2(ctx->db, sql, -1, &stmt, NULL);
    
    if (rc != SQLITE_OK) {
        ucis_set_error(ctx, "Failed to prepare cover update: %s", 
                      sqlite3_errmsg(ctx->db));
        return -1;
    }
    
    /* Bind parameters */
    sqlite3_bind_int(stmt, 1, data->type);
    sqlite3_bind_int64(stmt, 2, data->data);
    sqlite3_bind_int64(stmt, 3, data->data_fec);
    sqlite3_bind_int(stmt, 4, data->at_least);
    sqlite3_bind_int(stmt, 5, data->weight);
    
    if (data->goal > 0) {
        sqlite3_bind_int(stmt, 6, data->goal);
    } else {
        sqlite3_bind_null(stmt, 6);
    }
    
    sqlite3_bind_int(stmt, 7, data->flags);
    sqlite3_bind_int64(stmt, 8, cover_id);
    
    /* Execute */
    rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    
    return (rc == SQLITE_DONE) ? 0 : -1;
}

int ucis_IncrementCoverData(
    ucisT db,
    ucisCoverT cover,
    int64_t increment)
{
    ucis_db_context_t* ctx = get_db_context(db);
    if (!ctx) return -1;
    
    if (!ucis_validate_handle(cover, UCIS_HANDLE_COVER)) {
        ucis_set_error(ctx, "Invalid cover handle");
        return -1;
    }
    
    ucis_handle_entry_t* entry = ucis_get_handle_entry(cover);
    int64_t cover_id = entry->primary_key;
    
    /* Atomic increment */
    const char* sql = 
        "UPDATE coveritems SET cover_data = cover_data + ? WHERE cover_id = ?";
    
    sqlite3_stmt* stmt;
    int rc = sqlite3_prepare_v2(ctx->db, sql, -1, &stmt, NULL);
    
    if (rc != SQLITE_OK) {
        ucis_set_error(ctx, "Failed to prepare cover increment: %s", 
                      sqlite3_errmsg(ctx->db));
        return -1;
    }
    
    sqlite3_bind_int64(stmt, 1, increment);
    sqlite3_bind_int64(stmt, 2, cover_id);
    
    rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    
    return (rc == SQLITE_DONE) ? 0 : -1;
}
