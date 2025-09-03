################################################################################
# Database Accessibility Tests v1.0
# Author: Claude Code
# Updated: 2025-09-03 13:00
# Status: 🚧 In Progress
# Purpose: Test SQLite database path accessibility and connection reliability
################################################################################

# !!! PYSCRIPT TEST FUNCTIONS (Database Accessibility) !!!

import sqlite3
import os
import time
import threading

def test_database_file_access():
    """Test basic file system access to the database."""
    log.info("🔍 Testing database file accessibility...")
    
    db_path = "/config/home-assistant_v2.db"
    
    try:
        # Test file existence
        if os.path.exists(db_path):
            log.info(f"✅ Database file exists: {db_path}")
        else:
            log.error(f"❌ Database file does not exist: {db_path}")
            return False
        
        # Test read permission
        if os.access(db_path, os.R_OK):
            log.info("✅ Database file is readable")
        else:
            log.error("❌ Database file is not readable")
            return False
        
        # Test write permission
        if os.access(db_path, os.W_OK):
            log.info("✅ Database file is writable")
        else:
            log.error("❌ Database file is not writable")
            return False
        
        # Get file stats
        stat_info = os.stat(db_path)
        file_size = stat_info.st_size
        last_modified = time.ctime(stat_info.st_mtime)
        
        log.info(f"📊 Database file size: {file_size:,} bytes")
        log.info(f"📅 Last modified: {last_modified}")
        
        # Test if file is locked by another process
        try:
            # Try to open with a very short timeout
            test_conn = sqlite3.connect(db_path, timeout=1.0)
            test_conn.close()
            log.info("✅ Database file is not locked")
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                log.warning("⚠️ Database may be locked by another process")
            else:
                log.error(f"❌ Database access error: {e}")
                return False
        
        return True
        
    except Exception as e:
        log.error(f"❌ File access test failed: {e}")
        return False

def test_connection_establishment():
    """Test basic database connection establishment."""
    log.info("🔍 Testing database connection establishment...")
    
    db_path = "/config/home-assistant_v2.db"
    
    try:
        # Test basic connection
        start_time = time.time()
        conn = sqlite3.connect(db_path, timeout=10.0)
        connection_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        log.info(f"⏱️ Connection established in {connection_time:.2f}ms")
        
        # Test row factory setting
        conn.row_factory = sqlite3.Row
        log.info("✅ Row factory configured")
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test_value")
        result = cursor.fetchone()
        
        if result['test_value'] == 1:
            log.info("✅ Basic query successful")
        else:
            log.error(f"❌ Basic query failed: expected 1, got {result['test_value']}")
            conn.close()
            return False
        
        # Test transaction capability
        cursor.execute("BEGIN TRANSACTION")
        cursor.execute("SELECT 2 as transaction_test")
        result = cursor.fetchone()
        cursor.execute("COMMIT")
        
        if result['transaction_test'] == 2:
            log.info("✅ Transaction capability verified")
        else:
            log.error("❌ Transaction test failed")
            conn.close()
            return False
        
        conn.close()
        log.info("✅ Connection closed successfully")
        
        # Performance check - connection should be established quickly
        if connection_time > 1000:  # 1 second
            log.warning(f"⚠️ Slow connection time: {connection_time:.2f}ms (>1000ms)")
        elif connection_time > 100:  # 100ms
            log.info(f"ℹ️ Moderate connection time: {connection_time:.2f}ms")
        else:
            log.info(f"🚀 Fast connection time: {connection_time:.2f}ms")
        
        return True
        
    except Exception as e:
        log.error(f"❌ Connection establishment failed: {e}")
        return False

def test_connection_timeout_behavior():
    """Test connection timeout behavior under different scenarios."""
    log.info("🔍 Testing connection timeout behavior...")
    
    db_path = "/config/home-assistant_v2.db"
    
    try:
        # Test normal timeout
        start_time = time.time()
        conn = sqlite3.connect(db_path, timeout=5.0)
        actual_time = (time.time() - start_time) * 1000
        
        if actual_time < 5000:  # Should connect much faster than timeout
            log.info(f"✅ Normal connection within timeout: {actual_time:.2f}ms")
        else:
            log.warning(f"⚠️ Connection took long time: {actual_time:.2f}ms")
        
        conn.close()
        
        # Test very short timeout (still should work if not locked)
        try:
            start_time = time.time()
            conn = sqlite3.connect(db_path, timeout=0.1)  # 100ms
            actual_time = (time.time() - start_time) * 1000
            
            log.info(f"✅ Short timeout connection successful: {actual_time:.2f}ms")
            conn.close()
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                log.info("ℹ️ Short timeout failed due to lock (expected behavior)")
            else:
                log.error(f"❌ Short timeout failed unexpectedly: {e}")
                return False
        
        return True
        
    except Exception as e:
        log.error(f"❌ Timeout behavior test failed: {e}")
        return False

def test_concurrent_connections():
    """Test multiple concurrent connections to the database."""
    log.info("🔍 Testing concurrent database connections...")
    
    db_path = "/config/home-assistant_v2.db"
    results = []
    
    def test_connection(conn_id):
        """Test function for concurrent connections."""
        try:
            start_time = time.time()
            conn = sqlite3.connect(db_path, timeout=10.0)
            conn.row_factory = sqlite3.Row
            
            # Perform a simple query
            cursor = conn.cursor()
            cursor.execute(f"SELECT {conn_id} as connection_id")
            result = cursor.fetchone()
            
            connection_time = (time.time() - start_time) * 1000
            
            if result['connection_id'] == conn_id:
                results.append({"id": conn_id, "success": True, "time": connection_time})
                log.info(f"✅ Connection {conn_id} successful ({connection_time:.2f}ms)")
            else:
                results.append({"id": conn_id, "success": False, "error": "Query mismatch"})
                log.error(f"❌ Connection {conn_id} query failed")
            
            conn.close()
            
        except Exception as e:
            results.append({"id": conn_id, "success": False, "error": str(e)})
            log.error(f"❌ Connection {conn_id} failed: {e}")
    
    try:
        # Create multiple threads for concurrent connections
        threads = []
        num_connections = 5
        
        log.info(f"🚀 Starting {num_connections} concurrent connections...")
        
        for i in range(num_connections):
            thread = threading.Thread(target=test_connection, args=(i + 1,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Analyze results
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        log.info(f"📊 Concurrent connection results: {successful}/{num_connections} successful")
        
        if successful == num_connections:
            log.info("✅ All concurrent connections successful")
            
            # Check performance
            avg_time = sum(r["time"] for r in results if r["success"]) / successful
            log.info(f"📈 Average connection time: {avg_time:.2f}ms")
            
            return True
        else:
            log.error(f"❌ {failed} concurrent connections failed")
            for result in results:
                if not result["success"]:
                    log.error(f"   Connection {result['id']}: {result.get('error', 'Unknown error')}")
            return False
        
    except Exception as e:
        log.error(f"❌ Concurrent connection test failed: {e}")
        return False

def test_connection_recovery():
    """Test database connection recovery after failures."""
    log.info("🔍 Testing connection recovery capabilities...")
    
    db_path = "/config/home-assistant_v2.db"
    
    try:
        # Test recovery from connection timeout
        def test_recovery_after_timeout():
            """Test recovery after a timeout scenario."""
            try:
                # First, establish a normal connection
                conn1 = sqlite3.connect(db_path, timeout=10.0)
                log.info("✅ Initial connection established")
                
                # Start a long transaction to potentially cause conflicts
                cursor1 = conn1.cursor()
                cursor1.execute("BEGIN EXCLUSIVE TRANSACTION")
                
                # Try to connect from another "process" (short timeout)
                try:
                    conn2 = sqlite3.connect(db_path, timeout=0.1)
                    conn2.close()
                    log.info("✅ Second connection succeeded (no conflict)")
                except sqlite3.OperationalError:
                    log.info("ℹ️ Second connection timed out (expected)")
                
                # End the transaction and close first connection
                cursor1.execute("ROLLBACK")
                conn1.close()
                
                # Now try to connect again - should work
                conn3 = sqlite3.connect(db_path, timeout=10.0)
                cursor3 = conn3.cursor()
                cursor3.execute("SELECT 1")
                result = cursor3.fetchone()
                conn3.close()
                
                if result[0] == 1:
                    log.info("✅ Connection recovery after timeout successful")
                    return True
                else:
                    log.error("❌ Connection recovery query failed")
                    return False
                
            except Exception as e:
                log.error(f"❌ Recovery test failed: {e}")
                return False
        
        # Test multiple recovery attempts
        recovery_success = True
        for attempt in range(3):
            log.info(f"🔄 Recovery test attempt {attempt + 1}")
            if not test_recovery_after_timeout():
                recovery_success = False
                break
        
        if recovery_success:
            log.info("✅ Connection recovery tests passed")
        else:
            log.error("❌ Connection recovery tests failed")
        
        return recovery_success
        
    except Exception as e:
        log.error(f"❌ Connection recovery test failed: {e}")
        return False

def test_database_operations_reliability():
    """Test reliability of basic database operations."""
    log.info("🔍 Testing database operations reliability...")
    
    db_path = "/config/home-assistant_v2.db"
    
    try:
        conn = sqlite3.connect(db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Test table existence check
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='adaptive_learning'")
        table_result = cursor.fetchone()
        
        if table_result:
            log.info("✅ adaptive_learning table exists")
            
            # Test basic operations on existing table
            # Count records
            cursor.execute("SELECT COUNT(*) as count FROM adaptive_learning")
            count_result = cursor.fetchone()
            record_count = count_result['count']
            log.info(f"📊 Current record count: {record_count}")
            
            # Test SELECT with conditions
            cursor.execute("SELECT COUNT(*) as room_count FROM adaptive_learning WHERE room IS NOT NULL")
            room_count = cursor.fetchone()['room_count']
            log.info(f"📊 Records with valid rooms: {room_count}")
            
            # Test aggregation queries
            cursor.execute("SELECT room, COUNT(*) as count FROM adaptive_learning GROUP BY room LIMIT 5")
            room_stats = cursor.fetchall()
            
            log.info("📈 Top rooms by record count:")
            for stat in room_stats:
                log.info(f"   {stat['room']}: {stat['count']} records")
            
            # Test transaction reliability
            cursor.execute("BEGIN TRANSACTION")
            
            # Insert a test record
            test_timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
            cursor.execute("""
                INSERT INTO adaptive_learning (room, condition_key, brightness_percent, temperature_kelvin, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, ("test_room", "test_condition", 50, None, test_timestamp))
            
            # Verify insert
            cursor.execute("SELECT COUNT(*) as count FROM adaptive_learning WHERE room = 'test_room'")
            test_count = cursor.fetchone()['count']
            
            if test_count == 1:
                log.info("✅ Test record inserted successfully")
                
                # Rollback the test insert
                cursor.execute("ROLLBACK")
                
                # Verify rollback worked
                cursor.execute("SELECT COUNT(*) as count FROM adaptive_learning WHERE room = 'test_room'")
                after_rollback = cursor.fetchone()['count']
                
                if after_rollback == 0:
                    log.info("✅ Transaction rollback successful")
                else:
                    log.error("❌ Transaction rollback failed")
                    return False
            else:
                log.error("❌ Test record insert failed")
                cursor.execute("ROLLBACK")
                return False
            
        else:
            log.warning("⚠️ adaptive_learning table does not exist")
            # This might be expected in a fresh installation
        
        conn.close()
        log.info("✅ Database operations reliability test passed")
        return True
        
    except Exception as e:
        log.error(f"❌ Database operations reliability test failed: {e}")
        return False

@service("pyscript.test_database_accessibility")
def test_database_accessibility():
    """Run comprehensive database accessibility and connection reliability tests."""
    log.info("🚀 Starting Database Accessibility Tests...")
    
    tests = [
        ("Database File Access", test_database_file_access),
        ("Connection Establishment", test_connection_establishment),
        ("Connection Timeout Behavior", test_connection_timeout_behavior),
        ("Concurrent Connections", test_concurrent_connections),
        ("Connection Recovery", test_connection_recovery),
        ("Database Operations Reliability", test_database_operations_reliability)
    ]
    
    passed = 0
    failed = 0
    results = {}
    
    for test_name, test_func in tests:
        log.info(f"\n{'='*50}")
        log.info(f"Running: {test_name}")
        log.info('='*50)
        
        try:
            result = test_func()
            if result:
                passed += 1
                results[test_name] = "PASSED"
                log.info(f"✅ {test_name}: PASSED")
            else:
                failed += 1
                results[test_name] = "FAILED"
                log.error(f"❌ {test_name}: FAILED")
        except Exception as e:
            failed += 1
            results[test_name] = f"ERROR: {e}"
            log.error(f"❌ {test_name}: ERROR - {e}")
    
    total = len(tests)
    log.info(f"\n{'='*50}")
    log.info("DATABASE ACCESSIBILITY TEST SUMMARY")
    log.info('='*50)
    log.info(f"Total tests: {total}")
    log.info(f"Passed: {passed}")
    log.info(f"Failed: {failed}")
    log.info(f"Success rate: {(passed/total*100):.1f}%")
    
    if failed == 0:
        log.info("\n🎉 All database accessibility tests passed!")
        return {"status": "success", "passed": passed, "failed": failed, "total": total, "results": results}
    else:
        log.error(f"\n💥 {failed} test(s) failed - database accessibility issues detected")
        return {"status": "failed", "passed": passed, "failed": failed, "total": total, "results": results}