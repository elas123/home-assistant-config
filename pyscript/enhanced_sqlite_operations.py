################################################################################
# Enhanced SQLite Operations v1.0
# Author: Claude Code
# Updated: 2025-09-03 13:45
# Status: 🚧 In Progress
# Purpose: Enhanced SQLite operations with proper error handling and reliability
################################################################################

# !!! PYSCRIPT FUNCTIONS (Enhanced SQLite Operations) !!!

import sqlite3
import time
import datetime

# --- Enhanced Database Connection with Retry Logic ---

def get_enhanced_db_connection(max_retries=3, retry_delay=1.0):
    """Enhanced database connection with retry logic and comprehensive error handling."""
    
    db_path = "/config/home-assistant_v2.db"
    
    for attempt in range(max_retries):
        try:
            log.info(f"🔌 Database connection attempt {attempt + 1}/{max_retries}")
            
            # Test file accessibility first
            import os
            if not os.path.exists(db_path):
                raise FileNotFoundError(f"Database file not found: {db_path}")
            
            if not os.access(db_path, os.R_OK | os.W_OK):
                raise PermissionError(f"Database file not accessible: {db_path}")
            
            # Establish connection with timeout
            conn = sqlite3.connect(db_path, timeout=10.0)
            conn.row_factory = sqlite3.Row
            
            # Test connection with a simple query
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            if result[0] != 1:
                raise sqlite3.OperationalError("Database connection test failed")
            
            # Set pragmas for better reliability
            cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
            cursor.execute("PRAGMA synchronous=NORMAL")  # Balance speed vs safety
            cursor.execute("PRAGMA temp_store=MEMORY")   # Use memory for temp tables
            cursor.execute("PRAGMA cache_size=10000")    # Larger cache
            
            log.info("✅ Database connection established with enhanced settings")
            return conn
            
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower() and attempt < max_retries - 1:
                log.warning(f"⏳ Database locked, retrying in {retry_delay}s (attempt {attempt + 1})")
                time.sleep(retry_delay)
                retry_delay *= 1.5  # Exponential backoff
                continue
            else:
                log.error(f"❌ SQLite operational error: {e}")
                raise
                
        except (FileNotFoundError, PermissionError) as e:
            log.error(f"❌ Database access error: {e}")
            raise
            
        except Exception as e:
            if attempt < max_retries - 1:
                log.warning(f"⚠️ Connection failed, retrying: {e}")
                time.sleep(retry_delay)
                retry_delay *= 1.5
                continue
            else:
                log.error(f"❌ Database connection failed after {max_retries} attempts: {e}")
                raise
    
    raise sqlite3.OperationalError(f"Failed to establish database connection after {max_retries} attempts")

def ensure_table_schema(conn):
    """Ensure the adaptive_learning table exists with correct schema."""
    
    try:
        cursor = conn.cursor()
        
        # Create table with enhanced schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS adaptive_learning (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room TEXT NOT NULL CHECK(room != ''),
                condition_key TEXT NOT NULL CHECK(condition_key != ''),
                brightness_percent INTEGER NOT NULL CHECK(brightness_percent >= 0 AND brightness_percent <= 100),
                temperature_kelvin INTEGER CHECK(temperature_kelvin IS NULL OR (temperature_kelvin >= 2000 AND temperature_kelvin <= 7000)),
                timestamp TEXT NOT NULL CHECK(timestamp != ''),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(room, condition_key, timestamp)
            )
        """)
        
        # Create indexes for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_room_condition ON adaptive_learning(room, condition_key)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON adaptive_learning(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_room_timestamp ON adaptive_learning(room, timestamp)")
        
        # Handle legacy table migration
        cursor.execute("PRAGMA table_info(adaptive_learning)")
        columns = [row[1] for row in cursor.fetchall()]
        
        missing_columns = []
        
        if "temperature_kelvin" not in columns:
            missing_columns.append("ALTER TABLE adaptive_learning ADD COLUMN temperature_kelvin INTEGER CHECK(temperature_kelvin IS NULL OR (temperature_kelvin >= 2000 AND temperature_kelvin <= 7000))")
        
        if "created_at" not in columns:
            missing_columns.append("ALTER TABLE adaptive_learning ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
        
        # Apply missing columns
        for alter_sql in missing_columns:
            try:
                cursor.execute(alter_sql)
                log.info(f"✅ Applied schema migration: {alter_sql.split('ADD COLUMN')[1].split()[0]}")
            except Exception as e:
                log.warning(f"⚠️ Schema migration warning: {e}")
        
        conn.commit()
        log.info("✅ Database schema validated and updated")
        return True
        
    except Exception as e:
        log.error(f"❌ Schema validation failed: {e}")
        return False

# --- Enhanced Teaching Operations ---

@service("pyscript.enhanced_als_teach_room")
def enhanced_als_teach_room(room=None, brightness=None, temperature=None):
    """Enhanced teaching service with comprehensive error handling and validation."""
    
    operation_start = time.time()
    ts_now = datetime.datetime.now()
    ts_iso = ts_now.isoformat(timespec="seconds")
    
    # Input validation
    validation_errors = []
    
    if not room:
        validation_errors.append("Room parameter is required")
    elif not isinstance(room, str) or room.strip() == "":
        validation_errors.append("Room must be a non-empty string")
    
    if brightness is None:
        validation_errors.append("Brightness parameter is required")
    else:
        try:
            brightness_val = int(float(brightness))
            if brightness_val < 0 or brightness_val > 100:
                validation_errors.append("Brightness must be between 0 and 100")
        except (ValueError, TypeError):
            validation_errors.append("Brightness must be a valid number")
            brightness_val = None
    
    if temperature is not None:
        try:
            temp_val = int(float(temperature))
            if temp_val < 2000 or temp_val > 7000:
                validation_errors.append("Temperature must be between 2000K and 7000K")
        except (ValueError, TypeError):
            validation_errors.append("Temperature must be a valid number")
            temp_val = None
    else:
        temp_val = None
    
    if validation_errors:
        error_msg = "Input validation failed: " + "; ".join(validation_errors)
        log.error(f"❌ {error_msg}")
        
        state.set("sensor.als_last_teach_status", "validation_error", {
            "friendly_name": "ALS Last Teach Status",
            "error": error_msg,
            "validation_errors": validation_errors,
            "last_attempt": ts_iso
        })
        return {"status": "error", "message": error_msg, "errors": validation_errors}
    
    # Normalize room name
    room_normalized = str(room).lower().replace(" ", "_")
    room_normalized = "living_room" if room_normalized == "livingroom" else room_normalized
    
    # Generate condition key with error handling
    try:
        def safe_state_get(entity_id, default=None):
            """Safely get state with proper error handling."""
            try:
                value = state.get(str(entity_id))
                return value if value not in [None, "", "unknown", "unavailable"] else default
            except Exception:
                return default
        
        def safe_attr_get(entity_id, attr_name, default=None):
            """Safely get attribute with proper error handling."""
            try:
                attrs = state.getattr(str(entity_id)) or {}
                value = attrs.get(attr_name)
                return value if value not in [None, "", "unknown", "unavailable"] else default
            except Exception:
                return default
        
        home_mode = safe_state_get("input_select.home_state", "Day")
        sun_elevation = safe_attr_get("sun.sun", "elevation", 0.0)
        cloud_coverage = safe_attr_get("weather.pirateweather", "cloud_coverage", 0)
        season = safe_state_get("sensor.current_season", "Summer")
        
        # Calculate sun bucket
        try:
            sun_el = float(sun_elevation)
            if sun_el < 0:
                sun_bucket = "Below_Horizon"
            elif sun_el < 15:
                sun_bucket = "Low_Sun" 
            elif sun_el < 40:
                sun_bucket = "Mid_Sun"
            else:
                sun_bucket = "High_Sun"
        except (ValueError, TypeError):
            sun_bucket = "High_Sun"
        
        # Calculate cloud bucket
        try:
            cloud_bucket = int(float(cloud_coverage) // 20 * 20)
            cloud_bucket = max(0, min(100, cloud_bucket))
        except (ValueError, TypeError):
            cloud_bucket = 0
        
        condition_key = f"{home_mode}_{sun_bucket}_{cloud_bucket}_{season}"
        
    except Exception as e:
        error_msg = f"Failed to generate condition key: {e}"
        log.error(f"❌ {error_msg}")
        
        state.set("sensor.als_last_teach_status", "condition_error", {
            "friendly_name": "ALS Last Teach Status", 
            "error": error_msg,
            "last_attempt": ts_iso
        })
        return {"status": "error", "message": error_msg}
    
    # Database operations with enhanced error handling
    conn = None
    try:
        # Get database connection with retry logic
        conn = get_enhanced_db_connection()
        
        # Ensure schema is correct
        if not ensure_table_schema(conn):
            raise sqlite3.OperationalError("Schema validation failed")
        
        cursor = conn.cursor()
        
        # Check for duplicate entries (prevent spam)
        cursor.execute("""
            SELECT COUNT(*) FROM adaptive_learning 
            WHERE room = ? AND condition_key = ? AND timestamp > datetime('now', '-1 minute')
        """, (room_normalized, condition_key))
        
        recent_count = cursor.fetchone()[0]
        if recent_count > 0:
            log.warning(f"⚠️ Duplicate teaching attempt blocked (recent entry exists)")
            
            state.set("sensor.als_last_teach_status", "duplicate_blocked", {
                "friendly_name": "ALS Last Teach Status",
                "message": "Duplicate entry blocked (recent teaching exists)",
                "room": room_normalized,
                "condition_key": condition_key,
                "last_attempt": ts_iso
            })
            return {"status": "blocked", "message": "Duplicate entry blocked"}
        
        # Insert new teaching sample with transaction
        cursor.execute("BEGIN TRANSACTION")
        
        try:
            cursor.execute("""
                INSERT INTO adaptive_learning 
                (room, condition_key, brightness_percent, temperature_kelvin, timestamp, created_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (room_normalized, condition_key, brightness_val, temp_val, ts_iso))
            
            # Get the inserted row ID
            new_row_id = cursor.lastrowid
            
            # Get updated sample count
            cursor.execute("""
                SELECT COUNT(*) FROM adaptive_learning 
                WHERE room = ? AND condition_key = ?
            """, (room_normalized, condition_key))
            sample_count = cursor.fetchone()[0]
            
            # Get total sample count for room
            cursor.execute("""
                SELECT COUNT(*) FROM adaptive_learning WHERE room = ?
            """, (room_normalized,))
            total_samples = cursor.fetchone()[0]
            
            cursor.execute("COMMIT")
            
            operation_time = (time.time() - operation_start) * 1000  # Convert to milliseconds
            
            # Success logging and state updates
            success_info = {
                "room": room_normalized,
                "brightness": brightness_val,
                "temperature": temp_val,
                "condition_key": condition_key,
                "sample_count": sample_count,
                "total_samples": total_samples,
                "row_id": new_row_id,
                "operation_time_ms": round(operation_time, 2),
                "timestamp": ts_iso
            }
            
            log.info(f"✅ [ALS TEACH SUCCESS] {success_info}")
            
            # Update status sensor
            state.set("sensor.als_last_teach_status", "success", {
                "friendly_name": "ALS Last Teach Status",
                "room": room_normalized,
                "brightness": brightness_val,
                "temperature": temp_val,
                "condition_key": condition_key,
                "sample_count": sample_count,
                "total_samples": total_samples,
                "operation_time_ms": round(operation_time, 2),
                "last_teach": ts_iso
            })
            
            # Update last teach state  
            state.set("pyscript.last_teach", "success", success_info)
            
            return {
                "status": "success",
                "data": success_info
            }
            
        except Exception as e:
            cursor.execute("ROLLBACK")
            raise
        
    except sqlite3.IntegrityError as e:
        error_msg = f"Database integrity error: {e}"
        log.error(f"❌ {error_msg}")
        
        state.set("sensor.als_last_teach_status", "integrity_error", {
            "friendly_name": "ALS Last Teach Status",
            "error": error_msg,
            "room": room_normalized,
            "condition_key": condition_key,
            "last_attempt": ts_iso
        })
        return {"status": "error", "message": error_msg, "type": "integrity_error"}
    
    except sqlite3.OperationalError as e:
        error_msg = f"Database operational error: {e}"
        log.error(f"❌ {error_msg}")
        
        state.set("sensor.als_last_teach_status", "operational_error", {
            "friendly_name": "ALS Last Teach Status",
            "error": error_msg,
            "last_attempt": ts_iso
        })
        return {"status": "error", "message": error_msg, "type": "operational_error"}
    
    except sqlite3.Error as e:
        error_msg = f"SQLite error: {e}"
        log.error(f"❌ {error_msg}")
        
        state.set("sensor.als_last_teach_status", "sqlite_error", {
            "friendly_name": "ALS Last Teach Status",
            "error": error_msg,
            "last_attempt": ts_iso
        })
        return {"status": "error", "message": error_msg, "type": "sqlite_error"}
    
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        log.error(f"❌ {error_msg}")
        
        state.set("sensor.als_last_teach_status", "unexpected_error", {
            "friendly_name": "ALS Last Teach Status",
            "error": error_msg,
            "last_attempt": ts_iso
        })
        return {"status": "error", "message": error_msg, "type": "unexpected_error"}
    
    finally:
        if conn:
            try:
                conn.close()
                log.debug("🔌 Database connection closed")
            except Exception as e:
                log.warning(f"⚠️ Error closing database connection: {e}")

# --- Enhanced Data Retrieval Operations ---

@service("pyscript.enhanced_get_learning_data")
def enhanced_get_learning_data(room=None, condition_key=None, limit=100, order_by="timestamp DESC"):
    """Enhanced data retrieval with comprehensive filtering and error handling."""
    
    if not room:
        return {"status": "error", "message": "Room parameter is required"}
    
    room_normalized = str(room).lower().replace(" ", "_")
    room_normalized = "living_room" if room_normalized == "livingroom" else room_normalized
    
    conn = None
    try:
        conn = get_enhanced_db_connection()
        cursor = conn.cursor()
        
        # Build query with dynamic WHERE clause
        base_query = "SELECT * FROM adaptive_learning WHERE room = ?"
        params = [room_normalized]
        
        if condition_key:
            base_query += " AND condition_key = ?"
            params.append(condition_key)
        
        # Validate order_by to prevent SQL injection
        valid_orders = ["timestamp DESC", "timestamp ASC", "brightness_percent DESC", "brightness_percent ASC"]
        if order_by not in valid_orders:
            order_by = "timestamp DESC"
        
        base_query += f" ORDER BY {order_by}"
        
        # Validate and apply limit
        try:
            limit_val = max(1, min(int(limit), 1000))  # Clamp between 1 and 1000
        except (ValueError, TypeError):
            limit_val = 100
        
        base_query += f" LIMIT {limit_val}"
        
        cursor.execute(base_query, params)
        results = cursor.fetchall()
        
        # Convert to list of dictionaries
        learning_data = []
        for row in results:
            learning_data.append({
                "id": row["id"],
                "room": row["room"],
                "condition_key": row["condition_key"],
                "brightness_percent": row["brightness_percent"],
                "temperature_kelvin": row["temperature_kelvin"],
                "timestamp": row["timestamp"],
                "created_at": row.get("created_at", row["timestamp"])
            })
        
        log.info(f"✅ Retrieved {len(learning_data)} learning records for room '{room_normalized}'")
        
        return {
            "status": "success",
            "room": room_normalized,
            "condition_key": condition_key,
            "count": len(learning_data),
            "data": learning_data
        }
        
    except Exception as e:
        error_msg = f"Failed to retrieve learning data: {e}"
        log.error(f"❌ {error_msg}")
        return {"status": "error", "message": error_msg}
    
    finally:
        if conn:
            conn.close()

# --- Enhanced Data Management Operations ---

@service("pyscript.enhanced_delete_learning_data")
def enhanced_delete_learning_data(room=None, condition_key=None, record_id=None, confirm=False):
    """Enhanced data deletion with safety checks and comprehensive logging."""
    
    if not confirm:
        return {"status": "error", "message": "Deletion requires confirm=True parameter"}
    
    conn = None
    try:
        conn = get_enhanced_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("BEGIN TRANSACTION")
        
        deleted_count = 0
        
        if record_id:
            # Delete specific record by ID
            cursor.execute("SELECT * FROM adaptive_learning WHERE id = ?", (record_id,))
            record_to_delete = cursor.fetchone()
            
            if record_to_delete:
                cursor.execute("DELETE FROM adaptive_learning WHERE id = ?", (record_id,))
                deleted_count = cursor.rowcount
                log.info(f"🗑️ Deleted record ID {record_id}: {dict(record_to_delete)}")
            else:
                cursor.execute("ROLLBACK")
                return {"status": "error", "message": f"Record ID {record_id} not found"}
        
        elif room and condition_key:
            # Delete by room and condition key
            room_normalized = str(room).lower().replace(" ", "_")
            room_normalized = "living_room" if room_normalized == "livingroom" else room_normalized
            
            cursor.execute("SELECT COUNT(*) FROM adaptive_learning WHERE room = ? AND condition_key = ?", 
                         (room_normalized, condition_key))
            count_to_delete = cursor.fetchone()[0]
            
            if count_to_delete > 0:
                cursor.execute("DELETE FROM adaptive_learning WHERE room = ? AND condition_key = ?", 
                             (room_normalized, condition_key))
                deleted_count = cursor.rowcount
                log.info(f"🗑️ Deleted {deleted_count} records for room '{room_normalized}', condition '{condition_key}'")
            else:
                cursor.execute("ROLLBACK")
                return {"status": "error", "message": f"No records found for room '{room_normalized}', condition '{condition_key}'"}
        
        elif room:
            # Delete all records for room
            room_normalized = str(room).lower().replace(" ", "_")
            room_normalized = "living_room" if room_normalized == "livingroom" else room_normalized
            
            cursor.execute("SELECT COUNT(*) FROM adaptive_learning WHERE room = ?", (room_normalized,))
            count_to_delete = cursor.fetchone()[0]
            
            if count_to_delete > 0:
                cursor.execute("DELETE FROM adaptive_learning WHERE room = ?", (room_normalized,))
                deleted_count = cursor.rowcount
                log.info(f"🗑️ Deleted {deleted_count} records for room '{room_normalized}'")
            else:
                cursor.execute("ROLLBACK")
                return {"status": "error", "message": f"No records found for room '{room_normalized}'"}
        
        else:
            cursor.execute("ROLLBACK")
            return {"status": "error", "message": "Must specify record_id, or room (with optional condition_key)"}
        
        cursor.execute("COMMIT")
        
        return {
            "status": "success",
            "deleted_count": deleted_count,
            "message": f"Successfully deleted {deleted_count} record(s)"
        }
        
    except Exception as e:
        if conn:
            try:
                cursor.execute("ROLLBACK")
            except:
                pass
        
        error_msg = f"Failed to delete learning data: {e}"
        log.error(f"❌ {error_msg}")
        return {"status": "error", "message": error_msg}
    
    finally:
        if conn:
            conn.close()

# --- Database Health Check ---

@service("pyscript.enhanced_sqlite_health_check")
def enhanced_sqlite_health_check():
    """Comprehensive SQLite database health check."""
    
    log.info("🏥 Starting enhanced SQLite health check...")
    
    health_results = {
        "overall_status": "unknown",
        "connection": {"status": "unknown"},
        "schema": {"status": "unknown"},
        "data_integrity": {"status": "unknown"},
        "performance": {"status": "unknown"},
        "issues": [],
        "recommendations": []
    }
    
    conn = None
    try:
        # Test connection
        start_time = time.time()
        conn = get_enhanced_db_connection()
        connection_time = (time.time() - start_time) * 1000
        
        health_results["connection"] = {
            "status": "healthy",
            "connection_time_ms": round(connection_time, 2)
        }
        
        if connection_time > 1000:
            health_results["issues"].append("Slow database connection")
            health_results["recommendations"].append("Check database file location and disk I/O")
        
        cursor = conn.cursor()
        
        # Check schema
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='adaptive_learning'")
        table_schema = cursor.fetchone()
        
        if table_schema:
            health_results["schema"]["status"] = "healthy"
            health_results["schema"]["table_exists"] = True
        else:
            health_results["schema"]["status"] = "missing"
            health_results["schema"]["table_exists"] = False
            health_results["issues"].append("adaptive_learning table missing")
        
        # Check indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='adaptive_learning'")
        indexes = [row[0] for row in cursor.fetchall()]
        health_results["schema"]["indexes"] = indexes
        
        # Data integrity checks
        cursor.execute("PRAGMA integrity_check")
        integrity_result = cursor.fetchone()[0]
        
        if integrity_result == "ok":
            health_results["data_integrity"]["status"] = "healthy"
        else:
            health_results["data_integrity"]["status"] = "corrupted"
            health_results["data_integrity"]["details"] = integrity_result
            health_results["issues"].append("Database integrity issues detected")
        
        # Performance checks
        cursor.execute("SELECT COUNT(*) FROM adaptive_learning")
        total_records = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT room) FROM adaptive_learning")
        unique_rooms = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT condition_key) FROM adaptive_learning")
        unique_conditions = cursor.fetchone()[0]
        
        health_results["performance"] = {
            "status": "healthy",
            "total_records": total_records,
            "unique_rooms": unique_rooms,
            "unique_conditions": unique_conditions
        }
        
        if total_records > 10000:
            health_results["recommendations"].append("Consider archiving old records")
        
        # Check for recent activity
        cursor.execute("""
            SELECT COUNT(*) FROM adaptive_learning 
            WHERE timestamp > datetime('now', '-7 days')
        """)
        recent_records = cursor.fetchone()[0]
        
        health_results["performance"]["recent_activity"] = recent_records
        
        if recent_records == 0:
            health_results["issues"].append("No recent learning activity")
        
        # Overall status
        if len(health_results["issues"]) == 0:
            health_results["overall_status"] = "healthy"
        elif any("corrupted" in str(issue) or "missing" in str(issue) for issue in health_results["issues"]):
            health_results["overall_status"] = "critical"
        else:
            health_results["overall_status"] = "warning"
        
        log.info(f"🏥 Health check completed: {health_results['overall_status'].upper()}")
        
        return health_results
        
    except Exception as e:
        error_msg = f"Health check failed: {e}"
        log.error(f"❌ {error_msg}")
        
        health_results["overall_status"] = "error"
        health_results["error"] = error_msg
        return health_results
    
    finally:
        if conn:
            conn.close()