/**
 * @file ucis_util.c
 * @brief Utility functions
 */

#include "ucis_impl.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdarg.h>

char* ucis_strdup(const char* str) {
    if (!str) return NULL;
    size_t len = strlen(str);
    char* dup = malloc(len + 1);
    if (dup) {
        memcpy(dup, str, len + 1);
    }
    return dup;
}

void ucis_set_error(ucis_db_context_t* ctx, const char* fmt, ...) {
    if (!ctx) return;
    
    va_list args;
    va_start(args, fmt);
    vsnprintf(ctx->last_error, sizeof(ctx->last_error), fmt, args);
    va_end(args);
}

int ucis_exec_sql(sqlite3* db, const char* sql, char* error_msg) {
    char* err = NULL;
    int rc = sqlite3_exec(db, sql, NULL, NULL, &err);
    
    if (rc != SQLITE_OK) {
        if (error_msg && err) {
            snprintf(error_msg, 256, "%s", err);
        }
        sqlite3_free(err);
        return -1;
    }
    
    return 0;
}

int64_t ucis_last_insert_rowid(sqlite3* db) {
    return sqlite3_last_insert_rowid(db);
}
