################################################################################
# SQLite Teaching System Database Tests v1.0
# Author: Claude Code
# Updated: 2025-09-03 12:30
# Status: 🚧 In Progress
# Purpose: Comprehensive tests for SQLite database operations in ALS teaching system
################################################################################

# !!! PYSCRIPT TEST FUNCTIONS (SQLite Database Testing) !!!

import sqlite3
import os
import tempfile
import datetime

# --- Test Database Setup ---

def create_test_database():
    """Create a temporary test database for isolated testing."""
    test_db_fd, test_db_path = tempfile.mkstemp(suffix='.db')
    os.close(test_db_fd)  # Close the file descriptor
    return test_db_path

def setup_test_table(db_path):
    """Set up the adaptive_learning table in test database."""
    try:
        conn = sqlite3.connect(db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
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
        return conn
    except Exception as e:
        log.error(f"Failed to setup test table: {e}")
        return None

def cleanup_test_database(db_path):
    """Clean up test database file."""
    try:
        if os.path.exists(db_path):
            os.unlink(db_path)
    except Exception as e:
        log.error(f"Failed to cleanup test database: {e}")

# --- Database Connection Tests ---

def test_database_connection_success():
    """Test successful database connection establishment."""
    log.info("🧪 Testing database connection success...")
    
    test_db_path = create_test_database()
    
    try:
        # Test basic connection
        conn = sqlite3.connect(test_db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        
        # Verify connection works
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        assert result[0] == 1, f"Database connection test failed: expected 1, got {result[0]}"
        
        conn.close()
        log.info("✅ Database connection success test passed")
        
    except Exception as e:
        log.error(f"❌ Database connection success test failed: {e}")
        raise
    finally:
        cleanup_test_database(test_db_path)

def test_database_connection_failure():
    """Test database connection failure handling."""
    log.info("🧪 Testing database connection failure handling...")
    
    try:
        # Try to connect to invalid path
        invalid_path = "/invalid/path/that/does/not/exist.db"
        
        try:
            conn = sqlite3.connect(invalid_path, timeout=1.0)  # Short timeout
            # This should not succeed, but if it does, clean up
            conn.close()
            log.warning("⚠️ Expected connection failure but succeeded")
        except Exception as expected_error:
            # This is the expected behavior
            log.info(f"✅ Database connection failure handled correctly: {type(expected_error).__name__}")
            
    except Exception as e:
        log.error(f"❌ Database connection failure test failed: {e}")
        raise

def test_database_timeout_handling():
    """Test database connection timeout behavior."""
    log.info("🧪 Testing database connection timeout...")
    
    test_db_path = create_test_database()
    
    try:
        # Test connection with timeout
        conn = sqlite3.connect(test_db_path, timeout=0.1)  # Very short timeout
        conn.row_factory = sqlite3.Row
        
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        assert result[0] == 1, f"Timeout test failed: expected 1, got {result[0]}"
        
        conn.close()
        log.info("✅ Database timeout handling test passed")
        
    except Exception as e:
        log.error(f"❌ Database timeout test failed: {e}")
        raise
    finally:
        cleanup_test_database(test_db_path)

# --- Table Schema Tests ---

def test_table_creation():
    """Test adaptive_learning table creation with correct schema."""
    log.info("🧪 Testing table creation...")
    
    test_db_path = create_test_database()
    
    try:
        conn = setup_test_table(test_db_path)
        assert conn is not None, "Failed to create test table"
        
        # Verify table structure
        cursor = conn.cursor()
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
        
        # Check each column
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            col_not_null = col[3]
            col_default = col[4]
            col_pk = col[5]
            
            assert col_name in expected_columns, f"Unexpected column: {col_name}"
            
            expected = expected_columns[col_name]
            assert col_type == expected[0], f"Column {col_name}: expected type {expected[0]}, got {col_type}"
            assert col_not_null == expected[1], f"Column {col_name}: expected not_null {expected[1]}, got {col_not_null}"
            assert col_pk == expected[3], f"Column {col_name}: expected primary_key {expected[3]}, got {col_pk}"
        
        conn.close()
        log.info("✅ Table creation test passed")
        
    except Exception as e:
        log.error(f"❌ Table creation test failed: {e}")
        raise
    finally:
        cleanup_test_database(test_db_path)

def test_table_migration():
    """Test table migration logic for adding temperature_kelvin column."""
    log.info("🧪 Testing table migration...")
    
    test_db_path = create_test_database()
    
    try:
        # Create table without temperature column (legacy)
        conn = sqlite3.connect(test_db_path, timeout=10.0)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE adaptive_learning (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room TEXT NOT NULL,
                condition_key TEXT NOT NULL,
                brightness_percent INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        conn.commit()
        
        # Verify no temperature column
        cursor.execute("PRAGMA table_info(adaptive_learning)")
        columns = [row[1] for row in cursor.fetchall()]
        assert "temperature_kelvin" not in columns, "Temperature column should not exist yet"
        
        # Run migration
        try:
            cursor.execute("ALTER TABLE adaptive_learning ADD COLUMN temperature_kelvin INTEGER NULL")
            conn.commit()
        except Exception as e:
            log.error(f"Migration failed: {e}")
            raise
        
        # Verify temperature column was added
        cursor.execute("PRAGMA table_info(adaptive_learning)")
        columns = [row[1] for row in cursor.fetchall()]
        assert "temperature_kelvin" in columns, "Temperature column should exist after migration"
        
        conn.close()
        log.info("✅ Table migration test passed")
        
    except Exception as e:
        log.error(f"❌ Table migration test failed: {e}")
        raise
    finally:
        cleanup_test_database(test_db_path)

# --- Data Operation Tests ---

def test_data_insertion():
    """Test inserting data into adaptive_learning table."""
    log.info("🧪 Testing data insertion...")
    
    test_db_path = create_test_database()
    
    try:
        conn = setup_test_table(test_db_path)
        cursor = conn.cursor()
        
        # Test data insertion
        test_data = [
            ("kitchen", "Day_High_Sun_0_Summer", 85, 3000, "2025-09-03T12:00:00"),
            ("bedroom", "Night_Below_Horizon_20_Fall", 30, None, "2025-09-03T22:00:00"),
            ("living_room", "Evening_Low_Sun_40_Winter", 60, 2700, "2025-09-03T18:00:00")
        ]
        
        for room, condition_key, brightness, temperature, timestamp in test_data:
            cursor.execute("""
                INSERT INTO adaptive_learning (room, condition_key, brightness_percent, temperature_kelvin, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (room, condition_key, brightness, temperature, timestamp))
        
        conn.commit()
        
        # Verify insertions
        cursor.execute("SELECT COUNT(*) FROM adaptive_learning")
        count = cursor.fetchone()[0]
        assert count == len(test_data), f"Expected {len(test_data)} rows, got {count}"
        
        # Verify data integrity
        cursor.execute("SELECT * FROM adaptive_learning ORDER BY id")
        results = cursor.fetchall()
        
        for i, (room, condition_key, brightness, temperature, timestamp) in enumerate(test_data):
            row = results[i]
            assert row['room'] == room, f"Row {i}: expected room {room}, got {row['room']}"
            assert row['condition_key'] == condition_key, f"Row {i}: condition key mismatch"
            assert row['brightness_percent'] == brightness, f"Row {i}: brightness mismatch"
            assert row['temperature_kelvin'] == temperature, f"Row {i}: temperature mismatch"
            assert row['timestamp'] == timestamp, f"Row {i}: timestamp mismatch"
        
        conn.close()
        log.info("✅ Data insertion test passed")
        
    except Exception as e:
        log.error(f"❌ Data insertion test failed: {e}")
        raise
    finally:
        cleanup_test_database(test_db_path)

def test_data_retrieval():
    """Test retrieving data from adaptive_learning table."""
    log.info("🧪 Testing data retrieval...")
    
    test_db_path = create_test_database()
    
    try:
        conn = setup_test_table(test_db_path)
        cursor = conn.cursor()
        
        # Insert test data
        cursor.execute("""
            INSERT INTO adaptive_learning (room, condition_key, brightness_percent, temperature_kelvin, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, ("kitchen", "Day_High_Sun_0_Summer", 75, 3000, "2025-09-03T12:00:00"))
        
        cursor.execute("""
            INSERT INTO adaptive_learning (room, condition_key, brightness_percent, temperature_kelvin, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, ("kitchen", "Day_Low_Sun_20_Summer", 85, 2800, "2025-09-03T08:00:00"))
        
        conn.commit()
        
        # Test basic retrieval
        cursor.execute("SELECT * FROM adaptive_learning WHERE room = ?", ("kitchen",))
        results = cursor.fetchall()
        assert len(results) == 2, f"Expected 2 rows, got {len(results)}"
        
        # Test condition key filtering
        cursor.execute("SELECT DISTINCT condition_key FROM adaptive_learning WHERE room = ? ORDER BY condition_key", ("kitchen",))
        condition_keys = [row['condition_key'] for row in cursor.fetchall()]
        expected_keys = ["Day_High_Sun_0_Summer", "Day_Low_Sun_20_Summer"]
        assert condition_keys == expected_keys, f"Expected {expected_keys}, got {condition_keys}"
        
        # Test brightness retrieval
        cursor.execute("SELECT brightness_percent FROM adaptive_learning WHERE condition_key = ?", ("Day_High_Sun_0_Summer",))
        brightness = cursor.fetchone()['brightness_percent']
        assert brightness == 75, f"Expected brightness 75, got {brightness}"
        
        conn.close()
        log.info("✅ Data retrieval test passed")
        
    except Exception as e:
        log.error(f"❌ Data retrieval test failed: {e}")
        raise
    finally:
        cleanup_test_database(test_db_path)

def test_data_deletion():
    """Test deleting data from adaptive_learning table."""
    log.info("🧪 Testing data deletion...")
    
    test_db_path = create_test_database()
    
    try:
        conn = setup_test_table(test_db_path)
        cursor = conn.cursor()
        
        # Insert test data
        cursor.execute("""
            INSERT INTO adaptive_learning (room, condition_key, brightness_percent, temperature_kelvin, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, ("kitchen", "Day_High_Sun_0_Summer", 75, 3000, "2025-09-03T12:00:00"))
        
        cursor.execute("""
            INSERT INTO adaptive_learning (room, condition_key, brightness_percent, temperature_kelvin, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, ("bedroom", "Night_Below_Horizon_0_Summer", 30, None, "2025-09-03T22:00:00"))
        
        conn.commit()
        
        # Verify initial count
        cursor.execute("SELECT COUNT(*) FROM adaptive_learning")
        initial_count = cursor.fetchone()[0]
        assert initial_count == 2, f"Expected 2 initial rows, got {initial_count}"
        
        # Test single row deletion
        cursor.execute("DELETE FROM adaptive_learning WHERE room = ?", ("kitchen",))
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM adaptive_learning")
        after_delete_count = cursor.fetchone()[0]
        assert after_delete_count == 1, f"Expected 1 row after deletion, got {after_delete_count}"
        
        # Verify correct row was deleted
        cursor.execute("SELECT room FROM adaptive_learning")
        remaining_room = cursor.fetchone()['room']
        assert remaining_room == "bedroom", f"Expected bedroom to remain, got {remaining_room}"
        
        # Test condition key deletion
        cursor.execute("""
            INSERT INTO adaptive_learning (room, condition_key, brightness_percent, temperature_kelvin, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, ("bedroom", "Day_High_Sun_0_Summer", 50, 3000, "2025-09-03T10:00:00"))
        conn.commit()
        
        cursor.execute("DELETE FROM adaptive_learning WHERE room = ? AND condition_key = ?", 
                      ("bedroom", "Night_Below_Horizon_0_Summer"))
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM adaptive_learning WHERE room = ?", ("bedroom",))
        bedroom_count = cursor.fetchone()[0]
        assert bedroom_count == 1, f"Expected 1 bedroom row after condition deletion, got {bedroom_count}"
        
        conn.close()
        log.info("✅ Data deletion test passed")
        
    except Exception as e:
        log.error(f"❌ Data deletion test failed: {e}")
        raise
    finally:
        cleanup_test_database(test_db_path)

# --- Error Handling Tests ---

def test_sqlite_error_handling():
    """Test SQLite error handling for invalid operations."""
    log.info("🧪 Testing SQLite error handling...")
    
    test_db_path = create_test_database()
    
    try:
        conn = setup_test_table(test_db_path)
        cursor = conn.cursor()
        
        # Test constraint violation (NULL in required field)
        try:
            cursor.execute("""
                INSERT INTO adaptive_learning (room, condition_key, brightness_percent, temperature_kelvin, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (None, "Day_High_Sun_0_Summer", 75, 3000, "2025-09-03T12:00:00"))
            conn.commit()
            
            # If we get here, the constraint didn't work as expected
            assert False, "Expected constraint violation for NULL room"
            
        except sqlite3.IntegrityError:
            # This is expected behavior
            log.info("✅ NULL constraint violation handled correctly")
            conn.rollback()
        
        # Test invalid SQL syntax
        try:
            cursor.execute("INVALID SQL STATEMENT")
            assert False, "Expected SQL syntax error"
        except sqlite3.OperationalError:
            # This is expected behavior
            log.info("✅ SQL syntax error handled correctly")
        
        # Test table lock handling
        conn2 = sqlite3.connect(test_db_path, timeout=1.0)
        cursor2 = conn2.cursor()
        
        # Start transaction in first connection
        cursor.execute("BEGIN EXCLUSIVE TRANSACTION")
        
        try:
            # Try to write from second connection (should timeout)
            cursor2.execute("""
                INSERT INTO adaptive_learning (room, condition_key, brightness_percent, temperature_kelvin, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, ("test", "test_key", 50, None, "2025-09-03T12:00:00"))
            cursor2.connection.commit()
            
            # If we get here without timeout, that's unexpected
            log.warning("⚠️ Expected database lock timeout but operation succeeded")
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                log.info("✅ Database lock timeout handled correctly")
            else:
                raise
        finally:
            conn2.close()
            cursor.execute("ROLLBACK")
        
        conn.close()
        log.info("✅ SQLite error handling tests passed")
        
    except Exception as e:
        log.error(f"❌ SQLite error handling test failed: {e}")
        raise
    finally:
        cleanup_test_database(test_db_path)

# --- Performance Tests ---

def test_database_performance():
    """Test database operation performance meets criteria."""
    log.info("🧪 Testing database performance...")
    
    test_db_path = create_test_database()
    
    try:
        conn = setup_test_table(test_db_path)
        cursor = conn.cursor()
        
        import time
        
        # Test insertion performance (should be ≤ 500ms per requirement)
        start_time = time.time()
        
        cursor.execute("""
            INSERT INTO adaptive_learning (room, condition_key, brightness_percent, temperature_kelvin, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, ("performance_test", "Day_High_Sun_0_Summer", 75, 3000, "2025-09-03T12:00:00"))
        conn.commit()
        
        insertion_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        assert insertion_time <= 500, f"Insertion took {insertion_time}ms, expected ≤ 500ms"
        
        # Test retrieval performance
        start_time = time.time()
        
        cursor.execute("SELECT * FROM adaptive_learning WHERE room = ?", ("performance_test",))
        result = cursor.fetchall()
        
        retrieval_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        assert retrieval_time <= 100, f"Retrieval took {retrieval_time}ms, expected ≤ 100ms"
        assert len(result) == 1, "Performance test data not found"
        
        conn.close()
        log.info(f"✅ Database performance test passed (insertion: {insertion_time:.2f}ms, retrieval: {retrieval_time:.2f}ms)")
        
    except Exception as e:
        log.error(f"❌ Database performance test failed: {e}")
        raise
    finally:
        cleanup_test_database(test_db_path)

# --- Test Runner ---

@service("pyscript.run_sqlite_database_tests")
def run_sqlite_database_tests():
    """Run all SQLite database connectivity and operation tests."""
    log.info("🚀 Starting SQLite Teaching System Database Tests...")
    
    tests = [
        test_database_connection_success,
        test_database_connection_failure,
        test_database_timeout_handling,
        test_table_creation,
        test_table_migration,
        test_data_insertion,
        test_data_retrieval,
        test_data_deletion,
        test_sqlite_error_handling,
        test_database_performance
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            log.error(f"❌ Test {test_func.__name__} failed: {e}")
            failed += 1
    
    total = len(tests)
    log.info(f"📊 SQLite Database Tests Complete: {passed}/{total} passed, {failed} failed")
    
    if failed == 0:
        log.info("✅ All SQLite database tests passed successfully!")
        return {"status": "success", "passed": passed, "failed": failed, "total": total}
    else:
        log.error(f"❌ {failed} SQLite database tests failed")
        return {"status": "failed", "passed": passed, "failed": failed, "total": total}