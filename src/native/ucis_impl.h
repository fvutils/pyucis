/**
 * @file ucis_impl.h
 * @brief Internal implementation structures
 */

#ifndef UCIS_IMPL_H
#define UCIS_IMPL_H

#include "sqlite3.h"
#include "ucis_types.h"
#include <stddef.h>

/* Handle type enumeration */
typedef enum {
    UCIS_HANDLE_DB,
    UCIS_HANDLE_SCOPE,
    UCIS_HANDLE_COVER,
    UCIS_HANDLE_HISTORY,
    UCIS_HANDLE_FILE
} ucis_handle_type_t;

/* Handle entry structure */
typedef struct {
    ucis_handle_type_t type;
    sqlite3* db;
    int64_t primary_key;
    void* cached_data;
} ucis_handle_entry_t;

/* Handle table */
typedef struct {
    ucis_handle_entry_t* entries;
    size_t capacity;
    size_t count;
} ucis_handle_table_t;

/* Database context */
typedef struct {
    sqlite3* db;
    char* filename;
    int is_writable;
    
    /* Prepared statements */
    sqlite3_stmt* stmt_insert_scope;
    sqlite3_stmt* stmt_insert_cover;
    sqlite3_stmt* stmt_insert_history;
    sqlite3_stmt* stmt_query_scope_by_id;
    sqlite3_stmt* stmt_query_cover_by_id;
    
    /* Transaction state */
    int in_transaction;
    
    /* Error info */
    char last_error[256];
} ucis_db_context_t;

/* Global handle table */
extern ucis_handle_table_t g_handle_table;

/* Handle management functions */
void* ucis_alloc_handle(ucis_handle_type_t type, sqlite3* db, int64_t primary_key);
int ucis_validate_handle(void* handle, ucis_handle_type_t expected_type);
ucis_handle_entry_t* ucis_get_handle_entry(void* handle);
void ucis_free_handle(void* handle);
void ucis_init_handle_table(void);
void ucis_cleanup_handle_table(void);

/* SQL helper functions */
int ucis_exec_sql(sqlite3* db, const char* sql, char* error_msg);
int64_t ucis_last_insert_rowid(sqlite3* db);

/* Schema initialization */
int ucis_init_schema(sqlite3* db);

/* Utility functions */
char* ucis_strdup(const char* str);
void ucis_set_error(ucis_db_context_t* ctx, const char* fmt, ...);

#endif /* UCIS_IMPL_H */
