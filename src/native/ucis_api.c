/**
 * @file ucis_api.c
 * @brief Main UCIS API implementation - database lifecycle
 */

#include "ucis_impl.h"
#include "ucis.h"
#include <stdlib.h>
#include <string.h>

const char* ucis_GetAPIVersion(void) {
    return "1.0";
}

ucisT ucis_Open(const char* name) {
    sqlite3* db = NULL;
    int rc;
    
    /* Initialize handle table */
    ucis_init_handle_table();
    
    /* Open database */
    const char* db_name = name ? name : ":memory:";
    rc = sqlite3_open(db_name, &db);
    
    if (rc != SQLITE_OK) {
        if (db) sqlite3_close(db);
        return NULL;
    }
    
    /* Initialize schema */
    if (ucis_init_schema(db) != 0) {
        sqlite3_close(db);
        return NULL;
    }
    
    /* Create database context */
    ucis_db_context_t* ctx = calloc(1, sizeof(ucis_db_context_t));
    if (!ctx) {
        sqlite3_close(db);
        return NULL;
    }
    
    ctx->db = db;
    ctx->filename = name ? ucis_strdup(name) : NULL;
    ctx->is_writable = 1;
    ctx->in_transaction = 0;
    
    /* Allocate handle for database */
    ucisT handle = ucis_alloc_handle(UCIS_HANDLE_DB, db, 0);
    if (!handle) {
        free(ctx->filename);
        free(ctx);
        sqlite3_close(db);
        return NULL;
    }
    
    /* Store context as cached data */
    ucis_handle_entry_t* entry = ucis_get_handle_entry(handle);
    entry->cached_data = ctx;
    
    return handle;
}

void ucis_Close(ucisT db) {
    if (!ucis_validate_handle(db, UCIS_HANDLE_DB)) return;
    
    ucis_handle_entry_t* entry = ucis_get_handle_entry(db);
    ucis_db_context_t* ctx = (ucis_db_context_t*)entry->cached_data;
    
    if (ctx) {
        /* Close prepared statements */
        if (ctx->stmt_insert_scope) sqlite3_finalize(ctx->stmt_insert_scope);
        if (ctx->stmt_insert_cover) sqlite3_finalize(ctx->stmt_insert_cover);
        if (ctx->stmt_insert_history) sqlite3_finalize(ctx->stmt_insert_history);
        if (ctx->stmt_query_scope_by_id) sqlite3_finalize(ctx->stmt_query_scope_by_id);
        if (ctx->stmt_query_cover_by_id) sqlite3_finalize(ctx->stmt_query_cover_by_id);
        
        /* Close database */
        if (ctx->db) {
            sqlite3_close(ctx->db);
        }
        
        /* Free context */
        free(ctx->filename);
        free(ctx);
    }
    
    ucis_free_handle(db);
}

int ucis_Write(ucisT db, const char* name) {
    if (!ucis_validate_handle(db, UCIS_HANDLE_DB)) return -1;
    if (!name) return -1;
    
    ucis_handle_entry_t* entry = ucis_get_handle_entry(db);
    ucis_db_context_t* ctx = (ucis_db_context_t*)entry->cached_data;
    
    if (!ctx || !ctx->db) return -1;
    
    /* If already a file-backed database with same name, just checkpoint */
    if (ctx->filename && strcmp(ctx->filename, name) == 0) {
        sqlite3_wal_checkpoint(ctx->db, NULL);
        return 0;
    }
    
    /* Otherwise need to backup to new file */
    sqlite3* dest_db = NULL;
    int rc = sqlite3_open(name, &dest_db);
    
    if (rc != SQLITE_OK) {
        if (dest_db) sqlite3_close(dest_db);
        return -1;
    }
    
    /* Perform backup */
    sqlite3_backup* backup = sqlite3_backup_init(dest_db, "main", ctx->db, "main");
    if (backup) {
        sqlite3_backup_step(backup, -1);
        sqlite3_backup_finish(backup);
    }
    
    rc = sqlite3_errcode(dest_db);
    sqlite3_close(dest_db);
    
    return (rc == SQLITE_OK) ? 0 : -1;
}

const char* ucis_GetLastError(ucisT db) {
    if (!ucis_validate_handle(db, UCIS_HANDLE_DB)) {
        return "Invalid database handle";
    }
    
    ucis_handle_entry_t* entry = ucis_get_handle_entry(db);
    ucis_db_context_t* ctx = (ucis_db_context_t*)entry->cached_data;
    
    if (!ctx) return "Invalid database context";
    
    return ctx->last_error;
}
