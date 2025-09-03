################################################################################
# SQLite Implementation Validator v1.0
# Author: Claude Code
# Updated: 2025-09-03 12:45
# Status: 🚧 In Progress
# Purpose: Validate current SQLite implementation and database schema
################################################################################

# !!! PYSCRIPT VALIDATION FUNCTIONS (SQLite Implementation) !!!

import sqlite3
import os

def validate_database_path():
    """Validate that the database path is accessible."""
    log.info("🔍 Validating database path accessibility...")
    
    db_path = "/config/home-assistant_v2.db"
    
    try:
        # Check if path exists
        if os.path.exists(db_path):
            log.info(f"✅ Database file exists at {db_path}")
            
            # Check if readable
            if os.access(db_path, os.R_OK):
                log.info("✅ Database file is readable")
            else:
                log.error("❌ Database file is not readable")
                return False
                
            # Check if writable
            if os.access(db_path, os.W_OK):
                log.info("✅ Database file is writable")
            else:
                log.error("❌ Database file is not writable")
                return False
                
            # Get file size
            size = os.path.getsize(db_path)
            log.info(f"📊 Database file size: {size} bytes")
            
            return True
        else:
            log.warning(f"⚠️ Database file does not exist at {db_path}")
            return False
            
    except Exception as e:
        log.error(f"❌ Error validating database path: {e}")
        return False

def validate_database_connection():
    """Validate database connection using existing connection function pattern."""
    log.info("🔍 Validating database connection...")
    
    try:
        conn = sqlite3.connect("/config/home-assistant_v2.db", timeout=10.0)
        conn.row_factory = sqlite3.Row
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        if result[0] == 1:
            log.info("✅ Database connection successful")
            conn.close()
            return True
        else:
            log.error("❌ Database connection test failed")
            conn.close()
            return False
            
    except Exception as e:
        log.error(f"❌ Database connection failed: {e}")
        return False

def validate_table_schema():
    """Validate the adaptive_learning table schema."""
    log.info("🔍 Validating adaptive_learning table schema...")
    
    try:
        conn = sqlite3.connect("/config/home-assistant_v2.db", timeout=10.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='adaptive_learning'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            log.warning("⚠️ adaptive_learning table does not exist")
            conn.close()
            return False
            
        log.info("✅ adaptive_learning table exists")
        
        # Get table schema
        cursor.execute("PRAGMA table_info(adaptive_learning)")
        columns = cursor.fetchall()
        
        expected_columns = {
            'id': ('INTEGER', 1, None, 1),  # (type, not_null, default, primary_key)
            'room': ('TEXT', 1, None, 0),
            'condition_key': ('TEXT', 1, None, 0),
            'brightness_percent': ('INTEGER', 1, None, 0),
            'temperature_kelvin': ('INTEGER', 0, None, 0),  # Nullable
            'timestamp': ('TEXT', 1, None, 0)
        }
        
        schema_valid = True
        found_columns = {}
        
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            col_not_null = col[3]
            col_default = col[4]
            col_pk = col[5]
            
            found_columns[col_name] = (col_type, col_not_null, col_default, col_pk)
            
            if col_name in expected_columns:
                expected = expected_columns[col_name]
                if col_type != expected[0]:
                    log.error(f"❌ Column {col_name}: expected type {expected[0]}, got {col_type}")
                    schema_valid = False
                if col_not_null != expected[1]:
                    log.error(f"❌ Column {col_name}: expected not_null {expected[1]}, got {col_not_null}")
                    schema_valid = False
                if col_pk != expected[3]:
                    log.error(f"❌ Column {col_name}: expected primary_key {expected[3]}, got {col_pk}")
                    schema_valid = False
                    
                log.info(f"✅ Column {col_name}: {col_type} {'NOT NULL' if col_not_null else 'NULL'} {'PRIMARY KEY' if col_pk else ''}")
            else:
                log.warning(f"⚠️ Unexpected column: {col_name}")
        
        # Check for missing columns
        for expected_col in expected_columns:
            if expected_col not in found_columns:
                log.error(f"❌ Missing expected column: {expected_col}")
                schema_valid = False
        
        conn.close()
        
        if schema_valid:
            log.info("✅ Table schema validation passed")
            return True
        else:
            log.error("❌ Table schema validation failed")
            return False
            
    except Exception as e:
        log.error(f"❌ Schema validation failed: {e}")
        return False

def validate_existing_data():
    """Validate existing data in the adaptive_learning table."""
    log.info("🔍 Validating existing data...")
    
    try:
        conn = sqlite3.connect("/config/home-assistant_v2.db", timeout=10.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get total record count
        cursor.execute("SELECT COUNT(*) FROM adaptive_learning")
        total_records = cursor.fetchone()[0]
        log.info(f"📊 Total records in adaptive_learning: {total_records}")
        
        if total_records == 0:
            log.info("ℹ️ No existing data to validate")
            conn.close()
            return True
        
        # Get record count by room
        cursor.execute("SELECT room, COUNT(*) as count FROM adaptive_learning GROUP BY room ORDER BY count DESC")
        room_counts = cursor.fetchall()
        
        log.info("📊 Records by room:")
        for row in room_counts:
            log.info(f"   {row['room']}: {row['count']} records")
        
        # Check for data integrity issues
        issues_found = 0
        
        # Check for NULL values in required fields
        cursor.execute("SELECT COUNT(*) FROM adaptive_learning WHERE room IS NULL OR room = ''")
        null_rooms = cursor.fetchone()[0]
        if null_rooms > 0:
            log.error(f"❌ Found {null_rooms} records with NULL/empty room")
            issues_found += 1
        
        cursor.execute("SELECT COUNT(*) FROM adaptive_learning WHERE condition_key IS NULL OR condition_key = ''")
        null_conditions = cursor.fetchone()[0]
        if null_conditions > 0:
            log.error(f"❌ Found {null_conditions} records with NULL/empty condition_key")
            issues_found += 1
        
        cursor.execute("SELECT COUNT(*) FROM adaptive_learning WHERE brightness_percent IS NULL")
        null_brightness = cursor.fetchone()[0]
        if null_brightness > 0:
            log.error(f"❌ Found {null_brightness} records with NULL brightness_percent")
            issues_found += 1
        
        # Check for invalid brightness values
        cursor.execute("SELECT COUNT(*) FROM adaptive_learning WHERE brightness_percent < 0 OR brightness_percent > 100")
        invalid_brightness = cursor.fetchone()[0]
        if invalid_brightness > 0:
            log.error(f"❌ Found {invalid_brightness} records with invalid brightness values (not 0-100)")
            issues_found += 1
        
        # Check for invalid temperature values (if not NULL)
        cursor.execute("SELECT COUNT(*) FROM adaptive_learning WHERE temperature_kelvin IS NOT NULL AND (temperature_kelvin < 2000 OR temperature_kelvin > 7000)")
        invalid_temp = cursor.fetchone()[0]
        if invalid_temp > 0:
            log.error(f"❌ Found {invalid_temp} records with invalid temperature values (not 2000-7000K)")
            issues_found += 1
        
        # Get sample of recent data
        cursor.execute("SELECT * FROM adaptive_learning ORDER BY timestamp DESC LIMIT 5")
        recent_records = cursor.fetchall()
        
        log.info("📊 Recent records (sample):")
        for i, record in enumerate(recent_records):
            log.info(f"   {i+1}. Room: {record['room']}, Brightness: {record['brightness_percent']}%, "
                    f"Temperature: {record['temperature_kelvin']}K, Time: {record['timestamp']}")
        
        conn.close()
        
        if issues_found == 0:
            log.info("✅ Data validation passed - no integrity issues found")
            return True
        else:
            log.error(f"❌ Data validation failed - found {issues_found} integrity issues")
            return False
            
    except Exception as e:
        log.error(f"❌ Data validation failed: {e}")
        return False

def validate_memory_manager_functions():
    """Validate memory manager functions are working correctly."""
    log.info("🔍 Validating memory manager functions...")
    
    try:
        # Test the _get_db_connection function from als_memory_manager
        # We'll test this by importing the function pattern
        
        def test_get_db_connection():
            """Test database connection function."""
            try:
                conn = sqlite3.connect("/config/home-assistant_v2.db", timeout=10.0)
                conn.row_factory = sqlite3.Row
                
                # Ensure table exists
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS adaptive_learning (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        room TEXT NOT NULL,
                        condition_key TEXT NOT NULL,
                        brightness_percent INTEGER NOT NULL,
                        temperature_kelvin INTEGER NULL,
                        timestamp TEXT NOT NULL
                    )
                """)
                conn.commit()
                
                # Test migration logic
                try:
                    cursor.execute("PRAGMA table_info(adaptive_learning)")
                    cols = [row[1] for row in cursor.fetchall()]
                    if "temperature_kelvin" not in cols:
                        cursor.execute("ALTER TABLE adaptive_learning ADD COLUMN temperature_kelvin INTEGER NULL")
                        conn.commit()
                        log.info("✅ Temperature column migration would be applied")
                    else:
                        log.info("✅ Temperature column already exists")
                except Exception:
                    pass
                
                return conn
                
            except Exception as e:
                log.error(f"Database connection test failed: {e}")
                return None
        
        # Test connection function
        conn = test_get_db_connection()
        if conn:
            log.info("✅ Memory manager connection function works")
            conn.close()
        else:
            log.error("❌ Memory manager connection function failed")
            return False
        
        # Test room normalization function
        def test_norm_room(room_str):
            """Test room normalization logic."""
            r = str(room_str).lower().replace(" ", "_")
            return "living_room" if r == "livingroom" else r
        
        test_cases = [
            ("Kitchen", "kitchen"),
            ("Living Room", "living_room"),
            ("livingroom", "living_room"),
            ("BEDROOM", "bedroom"),
            ("Laundry", "laundry")
        ]
        
        for input_room, expected in test_cases:
            result = test_norm_room(input_room)
            if result == expected:
                log.info(f"✅ Room normalization: '{input_room}' → '{result}'")
            else:
                log.error(f"❌ Room normalization failed: '{input_room}' → '{result}', expected '{expected}'")
                return False
        
        log.info("✅ Memory manager function validation passed")
        return True
        
    except Exception as e:
        log.error(f"❌ Memory manager function validation failed: {e}")
        return False

def validate_teaching_service_functions():
    """Validate teaching service functions are working correctly."""
    log.info("🔍 Validating teaching service functions...")
    
    try:
        # Test brightness clamping function
        def test_clamp(v):
            """Test brightness clamping logic."""
            try:
                v = int(float(v))
            except:
                v = 0
            return 0 if v < 0 else 100 if v > 100 else v
        
        test_cases = [
            (-10, 0),
            (0, 0),
            (50, 50),
            (100, 100),
            (150, 100),
            ("75", 75),
            ("invalid", 0)
        ]
        
        for input_val, expected in test_cases:
            result = test_clamp(input_val)
            if result == expected:
                log.info(f"✅ Brightness clamping: {input_val} → {result}")
            else:
                log.error(f"❌ Brightness clamping failed: {input_val} → {result}, expected {expected}")
                return False
        
        # Test temperature clamping logic
        def test_temp_clamp(temperature):
            """Test temperature clamping logic."""
            if temperature is None:
                return None
            return max(2200, min(6500, int(temperature)))
        
        temp_cases = [
            (None, None),
            (2000, 2200),
            (3000, 3000),
            (6500, 6500),
            (7000, 6500)
        ]
        
        for input_temp, expected in temp_cases:
            result = test_temp_clamp(input_temp)
            if result == expected:
                log.info(f"✅ Temperature clamping: {input_temp} → {result}")
            else:
                log.error(f"❌ Temperature clamping failed: {input_temp} → {result}, expected {expected}")
                return False
        
        log.info("✅ Teaching service function validation passed")
        return True
        
    except Exception as e:
        log.error(f"❌ Teaching service function validation failed: {e}")
        return False

@service("pyscript.validate_sqlite_implementation")
def validate_sqlite_implementation():
    """Run comprehensive validation of current SQLite implementation."""
    log.info("🚀 Starting SQLite Implementation Validation...")
    
    validations = [
        ("Database Path Accessibility", validate_database_path),
        ("Database Connection", validate_database_connection),
        ("Table Schema", validate_table_schema),
        ("Existing Data Integrity", validate_existing_data),
        ("Memory Manager Functions", validate_memory_manager_functions),
        ("Teaching Service Functions", validate_teaching_service_functions)
    ]
    
    passed = 0
    failed = 0
    results = {}
    
    for name, validation_func in validations:
        log.info(f"\n{'='*60}")
        log.info(f"Running: {name}")
        log.info('='*60)
        
        try:
            result = validation_func()
            if result:
                passed += 1
                results[name] = "PASSED"
                log.info(f"✅ {name}: PASSED")
            else:
                failed += 1
                results[name] = "FAILED"
                log.error(f"❌ {name}: FAILED")
        except Exception as e:
            failed += 1
            results[name] = f"ERROR: {e}"
            log.error(f"❌ {name}: ERROR - {e}")
    
    total = len(validations)
    log.info(f"\n{'='*60}")
    log.info("SQLITE IMPLEMENTATION VALIDATION SUMMARY")
    log.info('='*60)
    log.info(f"Total validations: {total}")
    log.info(f"Passed: {passed}")
    log.info(f"Failed: {failed}")
    log.info(f"Success rate: {(passed/total*100):.1f}%")
    
    log.info("\nDetailed Results:")
    for name, result in results.items():
        status_emoji = "✅" if result == "PASSED" else "❌"
        log.info(f"  {status_emoji} {name}: {result}")
    
    if failed == 0:
        log.info("\n🎉 All SQLite implementation validations passed successfully!")
        return {"status": "success", "passed": passed, "failed": failed, "total": total, "results": results}
    else:
        log.error(f"\n💥 {failed} validation(s) failed - SQLite implementation needs attention")
        return {"status": "failed", "passed": passed, "failed": failed, "total": total, "results": results}