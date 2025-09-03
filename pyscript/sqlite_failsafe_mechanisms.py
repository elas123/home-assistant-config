################################################################################
# SQLite Failsafe Mechanisms v1.0
# Author: Claude Code
# Updated: 2025-09-03 14:00
# Status: 🚧 In Progress  
# Purpose: Failsafe mechanisms for SQLite database operations
################################################################################

# !!! PYSCRIPT FUNCTIONS (SQLite Failsafe Mechanisms) !!!

import sqlite3
import time
import threading
import os
import datetime
from pathlib import Path

# --- Connection Pool Management ---

class SQLiteConnectionPool:
    """Thread-safe connection pool for SQLite operations."""
    
    def __init__(self, db_path, pool_size=5):
        self.db_path = db_path
        self.pool_size = pool_size
        self.connections = []
        self.available = []
        self.lock = threading.Lock()
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize the connection pool."""
        for _ in range(self.pool_size):
            try:
                conn = sqlite3.connect(self.db_path, timeout=10.0, check_same_thread=False)
                conn.row_factory = sqlite3.Row
                self.connections.append(conn)
                self.available.append(conn)
            except Exception as e:
                log.warning(f"⚠️ Failed to create pooled connection: {e}")
    
    def get_connection(self, timeout=30.0):
        """Get a connection from the pool with timeout."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            with self.lock:
                if self.available:
                    conn = self.available.pop()
                    try:
                        # Test connection
                        cursor = conn.cursor()
                        cursor.execute("SELECT 1")
                        cursor.fetchone()
                        return conn
                    except Exception:
                        # Connection is stale, create a new one
                        try:
                            new_conn = sqlite3.connect(self.db_path, timeout=10.0, check_same_thread=False)
                            new_conn.row_factory = sqlite3.Row
                            self.connections[self.connections.index(conn)] = new_conn
                            return new_conn
                        except Exception as e:
                            log.error(f"❌ Failed to recreate connection: {e}")
                            continue
            
            time.sleep(0.1)
        
        raise sqlite3.OperationalError("Connection pool timeout")
    
    def return_connection(self, conn):
        """Return a connection to the pool."""
        with self.lock:
            if conn in self.connections and conn not in self.available:
                self.available.append(conn)
    
    def close_all(self):
        """Close all connections in the pool."""
        with self.lock:
            for conn in self.connections:
                try:
                    conn.close()
                except Exception:
                    pass
            self.connections.clear()
            self.available.clear()

# Global connection pool
_connection_pool = None

def get_connection_pool():
    """Get or create the global connection pool."""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = SQLiteConnectionPool("/config/home-assistant_v2.db")
    return _connection_pool

# --- Circuit Breaker Pattern ---

class DatabaseCircuitBreaker:
    """Circuit breaker for database operations."""
    
    def __init__(self, failure_threshold=5, timeout=60, expected_exception=Exception):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time >= self.timeout:
                self.state = "HALF_OPEN"
                log.info("🔄 Circuit breaker entering HALF_OPEN state")
            else:
                raise sqlite3.OperationalError("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
                log.info("✅ Circuit breaker reset to CLOSED state")
            
            return result
            
        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                log.error(f"🚨 Circuit breaker opened after {self.failure_count} failures")
            
            raise e

# Global circuit breaker
_circuit_breaker = DatabaseCircuitBreaker()

# --- Database Backup and Recovery ---

@service("pyscript.create_database_backup")
def create_database_backup(backup_dir="/config/backups/adaptive_learning"):
    """Create a backup of the adaptive learning data."""
    
    try:
        # Ensure backup directory exists
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"adaptive_learning_backup_{timestamp}.sql")
        
        log.info(f"💾 Creating database backup: {backup_file}")
        
        pool = get_connection_pool()
        conn = pool.get_connection()
        
        try:
            # Create SQL dump
            with open(backup_file, 'w') as f:
                # Write schema
                cursor = conn.cursor()
                cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='adaptive_learning'")
                table_sql = cursor.fetchone()
                
                if table_sql:
                    f.write(f"{table_sql[0]};\n\n")
                    
                    # Write data
                    cursor.execute("SELECT * FROM adaptive_learning ORDER BY id")
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        values = []
                        for value in row:
                            if value is None:
                                values.append("NULL")
                            elif isinstance(value, str):
                                escaped_value = value.replace("'", "''")
                                values.append(f"'{escaped_value}'")
                            else:
                                values.append(str(value))
                        
                        insert_sql = f"INSERT INTO adaptive_learning VALUES ({', '.join(values)});\n"
                        f.write(insert_sql)
            
            file_size = os.path.getsize(backup_file)
            log.info(f"✅ Backup created successfully: {file_size} bytes")
            
            # Clean up old backups (keep last 10)
            backup_files = sorted([f for f in os.listdir(backup_dir) if f.startswith("adaptive_learning_backup_")])
            if len(backup_files) > 10:
                for old_file in backup_files[:-10]:
                    try:
                        os.remove(os.path.join(backup_dir, old_file))
                        log.info(f"🗑️ Cleaned up old backup: {old_file}")
                    except Exception as e:
                        log.warning(f"⚠️ Failed to clean up {old_file}: {e}")
            
            return {
                "status": "success",
                "backup_file": backup_file,
                "file_size": file_size,
                "timestamp": timestamp
            }
            
        finally:
            pool.return_connection(conn)
            
    except Exception as e:
        error_msg = f"Backup failed: {e}"
        log.error(f"❌ {error_msg}")
        return {"status": "error", "message": error_msg}

# --- Failsafe Database Operations ---

def safe_database_operation(operation_func, *args, max_retries=3, fallback_result=None, **kwargs):
    """Execute database operation with comprehensive failsafe mechanisms."""
    
    for attempt in range(max_retries):
        try:
            # Use circuit breaker
            result = _circuit_breaker.call(operation_func, *args, **kwargs)
            return result
            
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower() and attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 0.5  # Exponential backoff
                log.warning(f"⏳ Database locked, retrying in {wait_time}s (attempt {attempt + 1})")
                time.sleep(wait_time)
                continue
            else:
                log.error(f"❌ Database operational error: {e}")
                break
                
        except sqlite3.Error as e:
            log.error(f"❌ SQLite error: {e}")
            if attempt == max_retries - 1:
                # Last attempt - try database recovery
                log.warning("🔧 Attempting database recovery...")
                if attempt_database_recovery():
                    log.info("✅ Database recovery successful, retrying operation")
                    continue
            break
            
        except Exception as e:
            log.error(f"❌ Unexpected error: {e}")
            break
    
    log.warning(f"⚠️ Operation failed after {max_retries} attempts, returning fallback result")
    return fallback_result

def attempt_database_recovery():
    """Attempt to recover from database issues."""
    
    try:
        log.info("🔧 Starting database recovery attempt...")
        
        # Check if database file exists and is accessible
        db_path = "/config/home-assistant_v2.db"
        
        if not os.path.exists(db_path):
            log.error("❌ Database file does not exist")
            return False
        
        # Try to open and check integrity
        conn = sqlite3.connect(db_path, timeout=5.0)
        cursor = conn.cursor()
        
        try:
            # Check integrity
            cursor.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()[0]
            
            if integrity_result != "ok":
                log.error(f"❌ Database integrity check failed: {integrity_result}")
                conn.close()
                return False
            
            # Try to access the table
            cursor.execute("SELECT COUNT(*) FROM adaptive_learning LIMIT 1")
            count = cursor.fetchone()[0]
            
            log.info(f"✅ Database recovery successful - {count} records accessible")
            conn.close()
            return True
            
        except Exception as e:
            log.error(f"❌ Database recovery failed: {e}")
            conn.close()
            return False
            
    except Exception as e:
        log.error(f"❌ Database recovery attempt failed: {e}")
        return False

# --- Enhanced Teaching Service with Failsafes ---

@service("pyscript.failsafe_als_teach_room")
def failsafe_als_teach_room(room=None, brightness=None, temperature=None):
    """Teaching service with comprehensive failsafe mechanisms."""
    
    def _core_teaching_operation(room, brightness, temperature):
        """Core teaching operation wrapped in failsafe."""
        # Import the enhanced teaching function
        from enhanced_sqlite_operations import enhanced_als_teach_room
        return enhanced_als_teach_room(room, brightness, temperature)
    
    # Execute with failsafe mechanisms
    result = safe_database_operation(
        _core_teaching_operation,
        room, brightness, temperature,
        max_retries=3,
        fallback_result={
            "status": "error",
            "message": "Teaching operation failed with all failsafes exhausted",
            "failsafe_triggered": True
        }
    )
    
    # Log failsafe triggers
    if result and result.get("failsafe_triggered"):
        log.error("🚨 Failsafe teaching operation triggered")
        
        # Attempt to create a backup if not done recently
        try:
            create_database_backup()
        except Exception:
            pass
    
    return result

# --- Database Health Monitoring ---

@service("pyscript.monitor_database_health")
def monitor_database_health():
    """Continuous database health monitoring with automatic recovery."""
    
    health_issues = []
    
    try:
        # Check connection pool health
        pool = get_connection_pool()
        
        # Test getting a connection
        test_conn = pool.get_connection(timeout=5.0)
        pool.return_connection(test_conn)
        
        log.debug("✅ Connection pool healthy")
        
        # Check circuit breaker state
        if _circuit_breaker.state == "OPEN":
            health_issues.append("Circuit breaker is OPEN")
            log.warning("⚠️ Circuit breaker is OPEN")
        
        # Check database file
        db_path = "/config/home-assistant_v2.db"
        if not os.path.exists(db_path):
            health_issues.append("Database file missing")
            log.error("❌ Database file missing")
        else:
            # Check file permissions
            if not os.access(db_path, os.R_OK | os.W_OK):
                health_issues.append("Database file not accessible")
                log.error("❌ Database file not accessible")
        
        # Update health status
        if health_issues:
            state.set("sensor.sqlite_health_status", "unhealthy", {
                "friendly_name": "SQLite Health Status",
                "issues": health_issues,
                "last_check": datetime.datetime.now().isoformat()
            })
        else:
            state.set("sensor.sqlite_health_status", "healthy", {
                "friendly_name": "SQLite Health Status",
                "last_check": datetime.datetime.now().isoformat()
            })
        
        return {
            "status": "healthy" if not health_issues else "unhealthy",
            "issues": health_issues
        }
        
    except Exception as e:
        error_msg = f"Health monitoring failed: {e}"
        log.error(f"❌ {error_msg}")
        
        state.set("sensor.sqlite_health_status", "error", {
            "friendly_name": "SQLite Health Status",
            "error": error_msg,
            "last_check": datetime.datetime.now().isoformat()
        })
        
        return {
            "status": "error",
            "message": error_msg
        }

# --- Automatic Recovery Service ---

@service("pyscript.auto_recover_database")
def auto_recover_database(force=False):
    """Automatic database recovery service."""
    
    if not force:
        # Check if recovery is needed
        health_result = monitor_database_health()
        if health_result.get("status") == "healthy":
            return {"status": "skipped", "message": "Database is healthy, no recovery needed"}
    
    recovery_steps = []
    
    try:
        log.info("🔧 Starting automatic database recovery...")
        
        # Step 1: Reset circuit breaker
        if _circuit_breaker.state == "OPEN":
            _circuit_breaker.state = "CLOSED"
            _circuit_breaker.failure_count = 0
            recovery_steps.append("Reset circuit breaker")
            log.info("🔄 Circuit breaker reset")
        
        # Step 2: Reinitialize connection pool
        global _connection_pool
        if _connection_pool:
            _connection_pool.close_all()
        _connection_pool = SQLiteConnectionPool("/config/home-assistant_v2.db")
        recovery_steps.append("Reinitialized connection pool")
        log.info("🔄 Connection pool reinitialized")
        
        # Step 3: Test database connectivity
        test_result = attempt_database_recovery()
        if test_result:
            recovery_steps.append("Database connectivity verified")
            log.info("✅ Database connectivity verified")
        else:
            recovery_steps.append("Database connectivity test failed")
            log.error("❌ Database connectivity test failed")
        
        # Step 4: Create backup if possible
        try:
            backup_result = create_database_backup()
            if backup_result.get("status") == "success":
                recovery_steps.append("Emergency backup created")
                log.info("💾 Emergency backup created")
        except Exception as e:
            recovery_steps.append(f"Backup failed: {e}")
            log.warning(f"⚠️ Emergency backup failed: {e}")
        
        recovery_success = test_result
        
        log.info(f"🔧 Recovery completed: {'SUCCESS' if recovery_success else 'PARTIAL'}")
        
        return {
            "status": "success" if recovery_success else "partial",
            "recovery_steps": recovery_steps,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
    except Exception as e:
        error_msg = f"Auto recovery failed: {e}"
        log.error(f"❌ {error_msg}")
        
        return {
            "status": "error",
            "message": error_msg,
            "recovery_steps": recovery_steps
        }

# --- Cleanup and Maintenance ---

@service("pyscript.cleanup_database_resources")
def cleanup_database_resources():
    """Clean up database resources and connections."""
    
    try:
        log.info("🧹 Cleaning up database resources...")
        
        # Close connection pool
        global _connection_pool
        if _connection_pool:
            _connection_pool.close_all()
            _connection_pool = None
            log.info("✅ Connection pool closed")
        
        # Reset circuit breaker
        global _circuit_breaker
        _circuit_breaker.state = "CLOSED"
        _circuit_breaker.failure_count = 0
        _circuit_breaker.last_failure_time = None
        log.info("✅ Circuit breaker reset")
        
        return {"status": "success", "message": "Database resources cleaned up"}
        
    except Exception as e:
        error_msg = f"Cleanup failed: {e}"
        log.error(f"❌ {error_msg}")
        return {"status": "error", "message": error_msg}