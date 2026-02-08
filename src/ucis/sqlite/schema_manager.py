# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Schema manager for SQLite UCIS database.
Creates and manages database schema based on sqlite_schema.md
"""

import sqlite3
from datetime import datetime

SCHEMA_VERSION = "1.0"

def create_schema(conn: sqlite3.Connection):
    """Create all tables and indexes for UCIS database"""
    
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Set WAL mode for better concurrency
    cursor.execute("PRAGMA journal_mode = WAL")
    
    # 1. Database Metadata
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS db_metadata (
            key TEXT PRIMARY KEY NOT NULL,
            value TEXT
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_db_metadata_key ON db_metadata(key)")
    
    # 2. Files
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            file_id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL UNIQUE,
            file_hash TEXT,
            file_table_id INTEGER,
            UNIQUE(file_path)
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_path ON files(file_path)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_hash ON files(file_hash) WHERE file_hash IS NOT NULL")
    
    # 3. Scopes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scopes (
            scope_id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER,
            scope_type INTEGER NOT NULL,
            scope_name TEXT NOT NULL,
            scope_flags INTEGER DEFAULT 0,
            weight INTEGER DEFAULT 1,
            goal INTEGER,
            limit_val INTEGER,
            source_file_id INTEGER,
            source_line INTEGER,
            source_token INTEGER,
            language_type INTEGER,
            
            FOREIGN KEY (parent_id) REFERENCES scopes(scope_id) ON DELETE CASCADE,
            FOREIGN KEY (source_file_id) REFERENCES files(file_id) ON DELETE SET NULL
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scopes_parent ON scopes(parent_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scopes_type ON scopes(scope_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scopes_name ON scopes(scope_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scopes_parent_name ON scopes(parent_id, scope_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scopes_parent_type_name ON scopes(parent_id, scope_type, scope_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scopes_source ON scopes(source_file_id, source_line) WHERE source_file_id IS NOT NULL")
    
    # 4. Cover Items
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coveritems (
            cover_id INTEGER PRIMARY KEY AUTOINCREMENT,
            scope_id INTEGER NOT NULL,
            cover_index INTEGER NOT NULL,
            cover_type INTEGER NOT NULL,
            cover_name TEXT NOT NULL,
            cover_flags INTEGER DEFAULT 0,
            cover_data INTEGER DEFAULT 0,
            cover_data_fec INTEGER DEFAULT 0,
            at_least INTEGER DEFAULT 1,
            weight INTEGER DEFAULT 1,
            goal INTEGER,
            limit_val INTEGER,
            source_file_id INTEGER,
            source_line INTEGER,
            source_token INTEGER,
            
            FOREIGN KEY (scope_id) REFERENCES scopes(scope_id) ON DELETE CASCADE,
            FOREIGN KEY (source_file_id) REFERENCES files(file_id) ON DELETE SET NULL,
            UNIQUE(scope_id, cover_index)
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_coveritems_scope ON coveritems(scope_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_coveritems_type ON coveritems(cover_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_coveritems_name ON coveritems(cover_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_coveritems_scope_index ON coveritems(scope_id, cover_index)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_coveritems_source ON coveritems(source_file_id, source_line) WHERE source_file_id IS NOT NULL")
    
    # 5. History Nodes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history_nodes (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER,
            history_kind INTEGER NOT NULL,
            logical_name TEXT NOT NULL,
            physical_name TEXT,
            test_status INTEGER,
            sim_time_low INTEGER,
            sim_time_high INTEGER,
            time_unit INTEGER,
            cpu_time REAL,
            seed TEXT,
            cmd_line TEXT,
            compulsory INTEGER DEFAULT 0,
            date TEXT,
            user_name TEXT,
            cost REAL,
            version TEXT,
            
            FOREIGN KEY (parent_id) REFERENCES history_nodes(history_id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_parent ON history_nodes(parent_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_kind ON history_nodes(history_kind)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_logical ON history_nodes(logical_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_status ON history_nodes(test_status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_date ON history_nodes(date) WHERE date IS NOT NULL")
    
    # 6. Coveritem Tests
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coveritem_tests (
            cover_id INTEGER NOT NULL,
            history_id INTEGER NOT NULL,
            count_contribution INTEGER DEFAULT 0,
            
            PRIMARY KEY (cover_id, history_id),
            FOREIGN KEY (cover_id) REFERENCES coveritems(cover_id) ON DELETE CASCADE,
            FOREIGN KEY (history_id) REFERENCES history_nodes(history_id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_coveritem_tests_cover ON coveritem_tests(cover_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_coveritem_tests_history ON coveritem_tests(history_id)")
    
    # 7. Properties Tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scope_properties (
            scope_id INTEGER NOT NULL,
            property_key INTEGER NOT NULL,
            property_type INTEGER NOT NULL,
            int_value INTEGER,
            real_value REAL,
            string_value TEXT,
            handle_value INTEGER,
            
            PRIMARY KEY (scope_id, property_key),
            FOREIGN KEY (scope_id) REFERENCES scopes(scope_id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scope_props_key ON scope_properties(property_key)")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coveritem_properties (
            cover_id INTEGER NOT NULL,
            property_key INTEGER NOT NULL,
            property_type INTEGER NOT NULL,
            int_value INTEGER,
            real_value REAL,
            string_value TEXT,
            handle_value INTEGER,
            
            PRIMARY KEY (cover_id, property_key),
            FOREIGN KEY (cover_id) REFERENCES coveritems(cover_id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cover_props_key ON coveritem_properties(property_key)")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history_properties (
            history_id INTEGER NOT NULL,
            property_key INTEGER NOT NULL,
            property_type INTEGER NOT NULL,
            int_value INTEGER,
            real_value REAL,
            string_value TEXT,
            handle_value INTEGER,
            
            PRIMARY KEY (history_id, property_key),
            FOREIGN KEY (history_id) REFERENCES history_nodes(history_id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_props_key ON history_properties(property_key)")
    
    # 8. Attributes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attributes (
            attr_id INTEGER PRIMARY KEY AUTOINCREMENT,
            obj_kind INTEGER NOT NULL,
            obj_id INTEGER NOT NULL,
            attr_key TEXT NOT NULL,
            attr_value TEXT,
            
            UNIQUE(obj_kind, obj_id, attr_key)
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_attributes_obj ON attributes(obj_kind, obj_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_attributes_key ON attributes(attr_key)")
    
    # 9. Tags
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_name TEXT NOT NULL UNIQUE
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(tag_name)")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS object_tags (
            obj_kind INTEGER NOT NULL,
            obj_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            
            PRIMARY KEY (obj_kind, obj_id, tag_id),
            FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_object_tags_obj ON object_tags(obj_kind, obj_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_object_tags_tag ON object_tags(tag_id)")
    
    # 10. Toggle Bits
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS toggle_bits (
            toggle_id INTEGER PRIMARY KEY AUTOINCREMENT,
            cover_id INTEGER NOT NULL,
            bit_index INTEGER NOT NULL,
            bit_type INTEGER NOT NULL,
            toggle_01 INTEGER DEFAULT 0,
            toggle_10 INTEGER DEFAULT 0,
            
            FOREIGN KEY (cover_id) REFERENCES coveritems(cover_id) ON DELETE CASCADE,
            UNIQUE(cover_id, bit_index)
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_toggle_bits_cover ON toggle_bits(cover_id)")
    
    # 11. FSM States
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fsm_states (
            state_id INTEGER PRIMARY KEY AUTOINCREMENT,
            scope_id INTEGER NOT NULL,
            state_name TEXT NOT NULL,
            state_index INTEGER NOT NULL,
            
            FOREIGN KEY (scope_id) REFERENCES scopes(scope_id) ON DELETE CASCADE,
            UNIQUE(scope_id, state_index)
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fsm_states_scope ON fsm_states(scope_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fsm_states_name ON fsm_states(state_name)")
    
    # 12. FSM Transitions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fsm_transitions (
            cover_id INTEGER NOT NULL,
            from_state_id INTEGER NOT NULL,
            to_state_id INTEGER NOT NULL,
            
            PRIMARY KEY (cover_id),
            FOREIGN KEY (cover_id) REFERENCES coveritems(cover_id) ON DELETE CASCADE,
            FOREIGN KEY (from_state_id) REFERENCES fsm_states(state_id) ON DELETE CASCADE,
            FOREIGN KEY (to_state_id) REFERENCES fsm_states(state_id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fsm_trans_from ON fsm_transitions(from_state_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fsm_trans_to ON fsm_transitions(to_state_id)")
    
    # 13. Cross Coverpoints
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cross_coverpoints (
            cross_scope_id INTEGER NOT NULL,
            coverpoint_scope_id INTEGER NOT NULL,
            cvp_index INTEGER NOT NULL,
            
            PRIMARY KEY (cross_scope_id, cvp_index),
            FOREIGN KEY (cross_scope_id) REFERENCES scopes(scope_id) ON DELETE CASCADE,
            FOREIGN KEY (coverpoint_scope_id) REFERENCES scopes(scope_id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cross_cvps_cross ON cross_coverpoints(cross_scope_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cross_cvps_cvp ON cross_coverpoints(coverpoint_scope_id)")
    
    # 14. Formal Data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS formal_data (
            cover_id INTEGER PRIMARY KEY,
            formal_status INTEGER,
            formal_radius INTEGER,
            witness_file TEXT,
            
            FOREIGN KEY (cover_id) REFERENCES coveritems(cover_id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_formal_status ON formal_data(formal_status)")
    
    # 15. Design Units
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS design_units (
            du_id INTEGER PRIMARY KEY AUTOINCREMENT,
            du_scope_id INTEGER NOT NULL UNIQUE,
            du_name TEXT NOT NULL,
            du_type INTEGER NOT NULL,
            
            FOREIGN KEY (du_scope_id) REFERENCES scopes(scope_id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_design_units_name ON design_units(du_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_design_units_type ON design_units(du_type)")
    
    conn.commit()


def initialize_metadata(conn: sqlite3.Connection):
    """Initialize database metadata"""
    cursor = conn.cursor()
    
    # Insert default metadata
    metadata = [
        ('UCIS_VERSION', '1.0'),
        ('API_VERSION', '1.0'),
        ('SCHEMA_VERSION', SCHEMA_VERSION),
        ('PATH_SEPARATOR', '/'),
        ('CREATED_TIME', datetime.now().isoformat())
    ]
    
    cursor.executemany(
        "INSERT OR IGNORE INTO db_metadata (key, value) VALUES (?, ?)",
        metadata
    )
    
    conn.commit()


def get_schema_version(conn: sqlite3.Connection) -> str:
    """Get the schema version of the database"""
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM db_metadata WHERE key = 'SCHEMA_VERSION'")
    row = cursor.fetchone()
    return row[0] if row else None


def check_schema_exists(conn: sqlite3.Connection) -> bool:
    """Check if the schema has been created"""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='db_metadata'"
    )
    return cursor.fetchone() is not None
