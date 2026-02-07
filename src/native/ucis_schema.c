/**
 * @file ucis_schema.c
 * @brief Database schema initialization
 */

#include "ucis_impl.h"
#include <string.h>

static const char* SCHEMA_DDL[] = {
    /* Enable foreign keys */
    "PRAGMA foreign_keys = ON;",
    
    /* Set WAL mode for better concurrency */
    "PRAGMA journal_mode = WAL;",
    
    /* Database metadata table */
    "CREATE TABLE IF NOT EXISTS db_metadata ("
    "  key TEXT PRIMARY KEY NOT NULL,"
    "  value TEXT"
    ");",
    
    "CREATE INDEX IF NOT EXISTS idx_db_metadata_key ON db_metadata(key);",
    
    /* Files table */
    "CREATE TABLE IF NOT EXISTS files ("
    "  file_id INTEGER PRIMARY KEY AUTOINCREMENT,"
    "  file_path TEXT NOT NULL UNIQUE,"
    "  file_hash TEXT,"
    "  file_table_id INTEGER"
    ");",
    
    "CREATE INDEX IF NOT EXISTS idx_files_path ON files(file_path);",
    
    /* Scopes table */
    "CREATE TABLE IF NOT EXISTS scopes ("
    "  scope_id INTEGER PRIMARY KEY AUTOINCREMENT,"
    "  parent_id INTEGER,"
    "  scope_type INTEGER NOT NULL,"
    "  scope_name TEXT NOT NULL,"
    "  scope_flags INTEGER DEFAULT 0,"
    "  weight INTEGER DEFAULT 1,"
    "  goal INTEGER,"
    "  limit_val INTEGER,"
    "  source_file_id INTEGER,"
    "  source_line INTEGER,"
    "  source_token INTEGER,"
    "  language_type INTEGER,"
    "  FOREIGN KEY (parent_id) REFERENCES scopes(scope_id) ON DELETE CASCADE,"
    "  FOREIGN KEY (source_file_id) REFERENCES files(file_id) ON DELETE SET NULL"
    ");",
    
    "CREATE INDEX IF NOT EXISTS idx_scopes_parent ON scopes(parent_id);",
    "CREATE INDEX IF NOT EXISTS idx_scopes_type ON scopes(scope_type);",
    "CREATE INDEX IF NOT EXISTS idx_scopes_name ON scopes(scope_name);",
    "CREATE INDEX IF NOT EXISTS idx_scopes_parent_name ON scopes(parent_id, scope_name);",
    
    /* Coveritems table */
    "CREATE TABLE IF NOT EXISTS coveritems ("
    "  cover_id INTEGER PRIMARY KEY AUTOINCREMENT,"
    "  scope_id INTEGER NOT NULL,"
    "  cover_index INTEGER NOT NULL,"
    "  cover_type INTEGER NOT NULL,"
    "  cover_name TEXT NOT NULL,"
    "  cover_flags INTEGER DEFAULT 0,"
    "  cover_data INTEGER DEFAULT 0,"
    "  cover_data_fec INTEGER DEFAULT 0,"
    "  at_least INTEGER DEFAULT 1,"
    "  weight INTEGER DEFAULT 1,"
    "  goal INTEGER,"
    "  limit_val INTEGER,"
    "  source_file_id INTEGER,"
    "  source_line INTEGER,"
    "  source_token INTEGER,"
    "  FOREIGN KEY (scope_id) REFERENCES scopes(scope_id) ON DELETE CASCADE,"
    "  FOREIGN KEY (source_file_id) REFERENCES files(file_id) ON DELETE SET NULL,"
    "  UNIQUE(scope_id, cover_index)"
    ");",
    
    "CREATE INDEX IF NOT EXISTS idx_coveritems_scope ON coveritems(scope_id);",
    "CREATE INDEX IF NOT EXISTS idx_coveritems_type ON coveritems(cover_type);",
    
    /* History nodes table */
    "CREATE TABLE IF NOT EXISTS history_nodes ("
    "  history_id INTEGER PRIMARY KEY AUTOINCREMENT,"
    "  parent_id INTEGER,"
    "  history_kind INTEGER NOT NULL,"
    "  logical_name TEXT NOT NULL,"
    "  physical_name TEXT,"
    "  test_status INTEGER,"
    "  sim_time_low INTEGER,"
    "  sim_time_high INTEGER,"
    "  time_unit INTEGER,"
    "  cpu_time REAL,"
    "  seed TEXT,"
    "  cmd_line TEXT,"
    "  compulsory INTEGER DEFAULT 0,"
    "  date TEXT,"
    "  user_name TEXT,"
    "  cost REAL,"
    "  version TEXT,"
    "  FOREIGN KEY (parent_id) REFERENCES history_nodes(history_id) ON DELETE CASCADE"
    ");",
    
    "CREATE INDEX IF NOT EXISTS idx_history_kind ON history_nodes(history_kind);",
    
    /* Properties tables */
    "CREATE TABLE IF NOT EXISTS scope_properties ("
    "  scope_id INTEGER NOT NULL,"
    "  property_key INTEGER NOT NULL,"
    "  property_type INTEGER NOT NULL,"
    "  int_value INTEGER,"
    "  real_value REAL,"
    "  string_value TEXT,"
    "  handle_value INTEGER,"
    "  PRIMARY KEY (scope_id, property_key),"
    "  FOREIGN KEY (scope_id) REFERENCES scopes(scope_id) ON DELETE CASCADE"
    ");",
    
    "CREATE TABLE IF NOT EXISTS coveritem_properties ("
    "  cover_id INTEGER NOT NULL,"
    "  property_key INTEGER NOT NULL,"
    "  property_type INTEGER NOT NULL,"
    "  int_value INTEGER,"
    "  real_value REAL,"
    "  string_value TEXT,"
    "  handle_value INTEGER,"
    "  PRIMARY KEY (cover_id, property_key),"
    "  FOREIGN KEY (cover_id) REFERENCES coveritems(cover_id) ON DELETE CASCADE"
    ");",
    
    "CREATE TABLE IF NOT EXISTS history_properties ("
    "  history_id INTEGER NOT NULL,"
    "  property_key INTEGER NOT NULL,"
    "  property_type INTEGER NOT NULL,"
    "  int_value INTEGER,"
    "  real_value REAL,"
    "  string_value TEXT,"
    "  handle_value INTEGER,"
    "  PRIMARY KEY (history_id, property_key),"
    "  FOREIGN KEY (history_id) REFERENCES history_nodes(history_id) ON DELETE CASCADE"
    ");",
    
    /* Attributes table */
    "CREATE TABLE IF NOT EXISTS attributes ("
    "  attr_id INTEGER PRIMARY KEY AUTOINCREMENT,"
    "  obj_kind INTEGER NOT NULL,"
    "  obj_id INTEGER NOT NULL,"
    "  attr_key TEXT NOT NULL,"
    "  attr_value TEXT,"
    "  UNIQUE(obj_kind, obj_id, attr_key)"
    ");",
    
    "CREATE INDEX IF NOT EXISTS idx_attributes_obj ON attributes(obj_kind, obj_id);",
    
    NULL  /* Sentinel */
};

int ucis_init_schema(sqlite3* db) {
    char error_msg[256];
    
    /* Execute all DDL statements */
    for (int i = 0; SCHEMA_DDL[i] != NULL; i++) {
        if (ucis_exec_sql(db, SCHEMA_DDL[i], error_msg) != 0) {
            return -1;
        }
    }
    
    /* Initialize metadata */
    const char* init_metadata = 
        "INSERT OR IGNORE INTO db_metadata (key, value) VALUES "
        "('UCIS_VERSION', '1.0'), "
        "('API_VERSION', '1.0'), "
        "('PATH_SEPARATOR', '/'), "
        "('CREATED_TIME', datetime('now'));";
    
    if (ucis_exec_sql(db, init_metadata, error_msg) != 0) {
        return -1;
    }
    
    return 0;
}
