################################################################################
# Database Schema Validation Service v1.0
# Author: Claude Code
# Updated: 2025-09-03 14:15
# Status: 🚧 In Progress
# Purpose: Comprehensive SQLite schema validation and migration service
################################################################################

# !!! PYSCRIPT FUNCTIONS (Schema Validation) !!!

import sqlite3
import datetime

# --- Schema Definitions ---

EXPECTED_SCHEMA = {
    "tables": {
        "adaptive_learning": {
            "columns": {
                "id": {
                    "type": "INTEGER",
                    "constraints": ["PRIMARY KEY", "AUTOINCREMENT"],
                    "nullable": False
                },
                "room": {
                    "type": "TEXT",
                    "constraints": ["NOT NULL", "CHECK(room != '')"],
                    "nullable": False
                },
                "condition_key": {
                    "type": "TEXT", 
                    "constraints": ["NOT NULL", "CHECK(condition_key != '')"],
                    "nullable": False
                },
                "brightness_percent": {
                    "type": "INTEGER",
                    "constraints": ["NOT NULL", "CHECK(brightness_percent >= 0 AND brightness_percent <= 100)"],
                    "nullable": False
                },
                "temperature_kelvin": {
                    "type": "INTEGER",
                    "constraints": ["CHECK(temperature_kelvin IS NULL OR (temperature_kelvin >= 2000 AND temperature_kelvin <= 7000))"],
                    "nullable": True
                },
                "timestamp": {
                    "type": "TEXT",
                    "constraints": ["NOT NULL", "CHECK(timestamp != '')"],
                    "nullable": False
                },
                "created_at": {
                    "type": "DATETIME",
                    "constraints": ["DEFAULT CURRENT_TIMESTAMP"],
                    "nullable": True
                }
            },
            "indexes": [
                {
                    "name": "idx_room_condition",
                    "columns": ["room", "condition_key"],
                    "unique": False
                },
                {
                    "name": "idx_timestamp",
                    "columns": ["timestamp"],
                    "unique": False
                },
                {
                    "name": "idx_room_timestamp",
                    "columns": ["room", "timestamp"],
                    "unique": False
                }
            ],
            "constraints": [
                "UNIQUE(room, condition_key, timestamp)"
            ]
        }
    }
}

# --- Schema Validation Functions ---

def validate_table_exists(cursor, table_name):
    """Validate that a table exists in the database."""
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
    """, (table_name,))
    
    result = cursor.fetchone()
    exists = result is not None
    
    log.info(f"{'✅' if exists else '❌'} Table '{table_name}': {'EXISTS' if exists else 'MISSING'}")
    
    return exists

def validate_table_columns(cursor, table_name, expected_columns):
    """Validate table column structure."""
    
    cursor.execute(f"PRAGMA table_info({table_name})")
    actual_columns = cursor.fetchall()
    
    # Convert to dictionary for easier comparison
    actual_cols = {}
    for col in actual_columns:
        actual_cols[col[1]] = {
            "type": col[2],
            "nullable": col[3] == 0,  # 0 = NOT NULL, 1 = NULL
            "default": col[4],
            "primary_key": col[5] == 1
        }
    
    validation_results = {
        "missing_columns": [],
        "type_mismatches": [],
        "constraint_issues": [],
        "extra_columns": []
    }
    
    # Check for missing columns and type mismatches
    for col_name, expected in expected_columns.items():
        if col_name not in actual_cols:
            validation_results["missing_columns"].append(col_name)
            log.error(f"❌ Column '{col_name}': MISSING")
        else:
            actual = actual_cols[col_name]
            
            # Check type
            if actual["type"].upper() != expected["type"].upper():
                validation_results["type_mismatches"].append({
                    "column": col_name,
                    "expected": expected["type"],
                    "actual": actual["type"]
                })
                log.error(f"❌ Column '{col_name}': Type mismatch (expected {expected['type']}, got {actual['type']})")
            
            # Check nullable constraint
            if actual["nullable"] != expected["nullable"]:
                validation_results["constraint_issues"].append({
                    "column": col_name,
                    "issue": f"Nullable mismatch (expected {expected['nullable']}, got {actual['nullable']})"
                })
                log.error(f"❌ Column '{col_name}': Nullable constraint mismatch")
            else:
                log.info(f"✅ Column '{col_name}': OK ({expected['type']}, nullable={expected['nullable']})")
    
    # Check for extra columns
    for col_name in actual_cols:
        if col_name not in expected_columns:
            validation_results["extra_columns"].append(col_name)
            log.warning(f"⚠️ Column '{col_name}': EXTRA (not in expected schema)")
    
    return validation_results

def validate_table_indexes(cursor, table_name, expected_indexes):
    """Validate table indexes."""
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='index' AND tbl_name=? AND name NOT LIKE 'sqlite_autoindex%'
    """, (table_name,))
    
    actual_indexes = [row[0] for row in cursor.fetchall()]
    expected_index_names = [idx["name"] for idx in expected_indexes]
    
    validation_results = {
        "missing_indexes": [],
        "extra_indexes": []
    }
    
    # Check for missing indexes
    for idx_name in expected_index_names:
        if idx_name not in actual_indexes:
            validation_results["missing_indexes"].append(idx_name)
            log.error(f"❌ Index '{idx_name}': MISSING")
        else:
            log.info(f"✅ Index '{idx_name}': EXISTS")
    
    # Check for extra indexes
    for idx_name in actual_indexes:
        if idx_name not in expected_index_names:
            validation_results["extra_indexes"].append(idx_name)
            log.warning(f"⚠️ Index '{idx_name}': EXTRA (not in expected schema)")
    
    return validation_results

def create_missing_columns(cursor, table_name, missing_columns, expected_schema):
    """Create missing columns with proper constraints."""
    
    migration_sql = []
    
    for col_name in missing_columns:
        col_def = expected_schema[col_name]
        
        # Build column definition
        col_sql = f"{col_name} {col_def['type']}"
        
        # Add constraints
        if col_def.get("constraints"):
            col_sql += " " + " ".join(col_def["constraints"])
        
        alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {col_sql}"
        migration_sql.append(alter_sql)
        
        try:
            cursor.execute(alter_sql)
            log.info(f"✅ Added column '{col_name}' to table '{table_name}'")
        except Exception as e:
            log.error(f"❌ Failed to add column '{col_name}': {e}")
            raise
    
    return migration_sql

def create_missing_indexes(cursor, table_name, missing_indexes, expected_schema):
    """Create missing indexes."""
    
    migration_sql = []
    
    for idx_name in missing_indexes:
        # Find the index definition
        idx_def = None
        for expected_idx in expected_schema:
            if expected_idx["name"] == idx_name:
                idx_def = expected_idx
                break
        
        if idx_def:
            columns_str = ", ".join(idx_def["columns"])
            unique_str = "UNIQUE " if idx_def.get("unique", False) else ""
            
            create_sql = f"CREATE {unique_str}INDEX {idx_name} ON {table_name}({columns_str})"
            migration_sql.append(create_sql)
            
            try:
                cursor.execute(create_sql)
                log.info(f"✅ Created index '{idx_name}' on table '{table_name}'")
            except Exception as e:
                log.error(f"❌ Failed to create index '{idx_name}': {e}")
                raise
    
    return migration_sql

# --- Main Schema Validation Service ---

@service("pyscript.validate_database_schema")
def validate_database_schema(auto_fix=False):
    """Comprehensive database schema validation with optional auto-fix."""
    
    log.info("🔍 Starting comprehensive database schema validation...")
    
    validation_results = {
        "overall_status": "unknown",
        "tables": {},
        "migrations_applied": [],
        "issues_found": [],
        "recommendations": [],
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    conn = None
    try:
        # Connect to database
        conn = sqlite3.connect("/config/home-assistant_v2.db", timeout=10.0)
        cursor = conn.cursor()
        
        # Validate each expected table
        for table_name, table_schema in EXPECTED_SCHEMA["tables"].items():
            log.info(f"\n{'='*50}")
            log.info(f"VALIDATING TABLE: {table_name}")
            log.info('='*50)
            
            table_results = {
                "exists": False,
                "columns": {"status": "unknown", "issues": []},
                "indexes": {"status": "unknown", "issues": []},
                "migrations": []
            }
            
            # Check if table exists
            table_exists = validate_table_exists(cursor, table_name)
            table_results["exists"] = table_exists
            
            if not table_exists:
                validation_results["issues_found"].append(f"Table '{table_name}' is missing")
                
                if auto_fix:
                    # Create the table
                    log.info(f"🔧 Creating missing table '{table_name}'...")
                    
                    # Build CREATE TABLE statement
                    column_defs = []
                    for col_name, col_def in table_schema["columns"].items():
                        col_sql = f"{col_name} {col_def['type']}"
                        if col_def.get("constraints"):
                            col_sql += " " + " ".join(col_def["constraints"])
                        column_defs.append(col_sql)
                    
                    # Add table constraints
                    if table_schema.get("constraints"):
                        column_defs.extend(table_schema["constraints"])
                    
                    create_sql = f"CREATE TABLE {table_name} ({', '.join(column_defs)})"
                    
                    try:
                        cursor.execute(create_sql)
                        table_results["migrations"].append(create_sql)
                        log.info(f"✅ Created table '{table_name}'")
                        
                        # Create indexes
                        for idx_def in table_schema["indexes"]:
                            columns_str = ", ".join(idx_def["columns"])
                            unique_str = "UNIQUE " if idx_def.get("unique", False) else ""
                            idx_sql = f"CREATE {unique_str}INDEX {idx_def['name']} ON {table_name}({columns_str})"
                            cursor.execute(idx_sql)
                            table_results["migrations"].append(idx_sql)
                            log.info(f"✅ Created index '{idx_def['name']}'")
                        
                        table_results["exists"] = True
                        table_results["columns"]["status"] = "created"
                        table_results["indexes"]["status"] = "created"
                        
                    except Exception as e:
                        log.error(f"❌ Failed to create table '{table_name}': {e}")
                        table_results["columns"]["issues"].append(f"Table creation failed: {e}")
                else:
                    validation_results["recommendations"].append(f"Create missing table '{table_name}'")
                    table_results["columns"]["status"] = "missing"
            
            else:
                # Validate columns
                log.info("📋 Validating columns...")
                column_validation = validate_table_columns(cursor, table_name, table_schema["columns"])
                
                if not any(column_validation.values()):
                    table_results["columns"]["status"] = "valid"
                    log.info("✅ All columns are valid")
                else:
                    table_results["columns"]["status"] = "issues_found"
                    table_results["columns"]["issues"] = column_validation
                    
                    if column_validation["missing_columns"]:
                        validation_results["issues_found"].extend([
                            f"Table '{table_name}' missing column '{col}'" 
                            for col in column_validation["missing_columns"]
                        ])
                        
                        if auto_fix:
                            log.info("🔧 Creating missing columns...")
                            migration_sql = create_missing_columns(
                                cursor, table_name, 
                                column_validation["missing_columns"], 
                                table_schema["columns"]
                            )
                            table_results["migrations"].extend(migration_sql)
                
                # Validate indexes
                log.info("📇 Validating indexes...")
                index_validation = validate_table_indexes(cursor, table_name, table_schema["indexes"])
                
                if not any(index_validation.values()):
                    table_results["indexes"]["status"] = "valid"
                    log.info("✅ All indexes are valid")
                else:
                    table_results["indexes"]["status"] = "issues_found"
                    table_results["indexes"]["issues"] = index_validation
                    
                    if index_validation["missing_indexes"]:
                        validation_results["issues_found"].extend([
                            f"Table '{table_name}' missing index '{idx}'"
                            for idx in index_validation["missing_indexes"]
                        ])
                        
                        if auto_fix:
                            log.info("🔧 Creating missing indexes...")
                            migration_sql = create_missing_indexes(
                                cursor, table_name,
                                index_validation["missing_indexes"],
                                table_schema["indexes"]
                            )
                            table_results["migrations"].extend(migration_sql)
            
            validation_results["tables"][table_name] = table_results
            validation_results["migrations_applied"].extend(table_results["migrations"])
        
        # Commit any migrations
        if auto_fix and validation_results["migrations_applied"]:
            conn.commit()
            log.info(f"✅ Committed {len(validation_results['migrations_applied'])} schema migrations")
        
        # Determine overall status
        total_issues = len(validation_results["issues_found"])
        if total_issues == 0:
            validation_results["overall_status"] = "valid"
        elif auto_fix and len(validation_results["migrations_applied"]) > 0:
            validation_results["overall_status"] = "fixed"
        else:
            validation_results["overall_status"] = "issues_found"
        
        log.info(f"\n{'='*50}")
        log.info("SCHEMA VALIDATION SUMMARY")
        log.info('='*50)
        log.info(f"Overall Status: {validation_results['overall_status'].upper()}")
        log.info(f"Issues Found: {total_issues}")
        log.info(f"Migrations Applied: {len(validation_results['migrations_applied'])}")
        
        if validation_results["recommendations"]:
            log.info("Recommendations:")
            for rec in validation_results["recommendations"]:
                log.info(f"  - {rec}")
        
        return validation_results
        
    except Exception as e:
        error_msg = f"Schema validation failed: {e}"
        log.error(f"❌ {error_msg}")
        
        validation_results["overall_status"] = "error"
        validation_results["error"] = error_msg
        return validation_results
    
    finally:
        if conn:
            conn.close()

# --- Schema Migration History ---

@service("pyscript.get_schema_migration_history")
def get_schema_migration_history():
    """Get history of schema migrations (if tracking table exists)."""
    
    try:
        conn = sqlite3.connect("/config/home-assistant_v2.db", timeout=10.0)
        cursor = conn.cursor()
        
        # Check if migration history table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='schema_migrations'
        """)
        
        if not cursor.fetchone():
            log.info("ℹ️ No schema migration history table found")
            return {"status": "no_history", "message": "Migration history not tracked"}
        
        # Get migration history
        cursor.execute("""
            SELECT migration_id, description, applied_at 
            FROM schema_migrations 
            ORDER BY applied_at DESC
        """)
        
        migrations = []
        for row in cursor.fetchall():
            migrations.append({
                "id": row[0],
                "description": row[1], 
                "applied_at": row[2]
            })
        
        conn.close()
        
        return {
            "status": "success",
            "migrations": migrations,
            "count": len(migrations)
        }
        
    except Exception as e:
        error_msg = f"Failed to get migration history: {e}"
        log.error(f"❌ {error_msg}")
        return {"status": "error", "message": error_msg}