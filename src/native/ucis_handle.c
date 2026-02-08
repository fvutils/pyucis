/**
 * @file ucis_handle.c
 * @brief Handle management implementation
 */

#include "ucis_impl.h"
#include <stdlib.h>
#include <string.h>

/* Initial capacity for handle table */
#define INITIAL_CAPACITY 256

/* Global handle table */
ucis_handle_table_t g_handle_table = {NULL, 0, 0};

void ucis_init_handle_table(void) {
    if (g_handle_table.entries == NULL) {
        g_handle_table.capacity = INITIAL_CAPACITY;
        g_handle_table.entries = calloc(INITIAL_CAPACITY, sizeof(ucis_handle_entry_t));
        g_handle_table.count = 0;
    }
}

void ucis_cleanup_handle_table(void) {
    if (g_handle_table.entries) {
        free(g_handle_table.entries);
        g_handle_table.entries = NULL;
        g_handle_table.capacity = 0;
        g_handle_table.count = 0;
    }
}

void* ucis_alloc_handle(ucis_handle_type_t type, sqlite3* db, int64_t primary_key) {
    ucis_init_handle_table();
    
    /* Find free slot or expand */
    size_t index = g_handle_table.count;
    if (index >= g_handle_table.capacity) {
        /* Expand table */
        size_t new_capacity = g_handle_table.capacity * 2;
        ucis_handle_entry_t* new_entries = realloc(
            g_handle_table.entries,
            new_capacity * sizeof(ucis_handle_entry_t)
        );
        if (!new_entries) return NULL;
        
        memset(new_entries + g_handle_table.capacity, 0,
               g_handle_table.capacity * sizeof(ucis_handle_entry_t));
        
        g_handle_table.entries = new_entries;
        g_handle_table.capacity = new_capacity;
    }
    
    /* Allocate entry */
    ucis_handle_entry_t* entry = &g_handle_table.entries[index];
    entry->type = type;
    entry->db = db;
    entry->primary_key = primary_key;
    entry->cached_data = NULL;
    
    g_handle_table.count++;
    
    /* Return pointer to entry as handle */
    return (void*)entry;
}

ucis_handle_entry_t* ucis_get_handle_entry(void* handle) {
    if (!handle) return NULL;
    
    ucis_handle_entry_t* entry = (ucis_handle_entry_t*)handle;
    
    /* Validate handle is within table bounds */
    if (entry < g_handle_table.entries ||
        entry >= g_handle_table.entries + g_handle_table.count) {
        return NULL;
    }
    
    return entry;
}

int ucis_validate_handle(void* handle, ucis_handle_type_t expected_type) {
    ucis_handle_entry_t* entry = ucis_get_handle_entry(handle);
    if (!entry) return 0;
    if (entry->type != expected_type) return 0;
    return 1;
}

void ucis_free_handle(void* handle) {
    ucis_handle_entry_t* entry = ucis_get_handle_entry(handle);
    if (!entry) return;
    
    /* Don't free cached_data here - caller is responsible
     * (e.g., ucis_Close frees the context) */
    
    /* Mark as unused */
    entry->type = UCIS_HANDLE_DB;  /* Reset type */
    entry->db = NULL;
    entry->primary_key = -1;
    entry->cached_data = NULL;
}
