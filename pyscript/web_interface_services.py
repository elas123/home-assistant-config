# /config/pyscript/web_interface_services.py
# Services for the web-based memory manager interface

import sqlite3
import json
import datetime

def _get_db_connection():
    """Connect to HA SQLite DB and ensure schema is compatible."""
    try:
        conn = sqlite3.connect("/config/home-assistant_v2.db", timeout=10.0)
        conn.row_factory = sqlite3.Row
        # Ensure expected table/columns exist
        try:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS adaptive_learning (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room TEXT NOT NULL,
                    condition_key TEXT NOT NULL,
                    brightness_percent INTEGER NOT NULL,
                    temperature_kelvin INTEGER NULL,
                    timestamp TEXT NOT NULL
                )
                """
            )
            # Add missing column if needed (legacy installs)
            cur.execute("PRAGMA table_info(adaptive_learning)")
            cols = [row[1] for row in cur.fetchall()]
            if "temperature_kelvin" not in cols:
                cur.execute("ALTER TABLE adaptive_learning ADD COLUMN temperature_kelvin INTEGER NULL")
                conn.commit()
        except Exception as _:
            pass
        return conn
    except Exception as e:
        log.error(f"Failed to connect to SQLite database: {e}")
        return None

@service("pyscript.get_room_memory_data")
def get_room_memory_data(room=None):
    """Get all memory data for a specific room from SQLite database."""
    if not room:
        log.error("Room parameter is required")
        return {"success": False, "error": "Room parameter required"}
    
    db_conn = _get_db_connection()
    if not db_conn:
        return {"success": False, "error": "Database connection failed"}
    
    try:
        cursor = db_conn.cursor()
        
        # Get all data for this room, ordered by condition_key and timestamp
        cursor.execute("""
            SELECT id, condition_key, brightness_percent, temperature_kelvin, timestamp 
            FROM adaptive_learning 
            WHERE room = ? 
            ORDER BY condition_key, timestamp
        """, (room,))
        
        results = cursor.fetchall()
        
        # Convert to list of dictionaries
        data = []
        for row in results:
            data.append({
                "id": row["id"],
                "condition_key": row["condition_key"],
                "brightness_percent": row["brightness_percent"],
                "temperature_kelvin": row["temperature_kelvin"],
                "timestamp": row["timestamp"]
            })
        
        db_conn.close()
        
        # Set state with result for web interface to read
        state.set(f"sensor.room_memory_{room}", "loaded", {
            "friendly_name": f"{room.title()} Memory Data",
            "data": data,
            "record_count": len(data),
            "last_updated": datetime.datetime.now().isoformat()
        })
        
        log.info(f"Retrieved {len(data)} memory records for {room}")
        return {"success": True, "data": data}
        
    except Exception as e:
        log.error(f"Error retrieving memory data for {room}: {e}")
        if db_conn:
            db_conn.close()
        return {"success": False, "error": str(e)}

@service("pyscript.als_delete_sample_sqlite")
def als_delete_sample_sqlite(room=None, condition_key=None, sample_index=None):
    """Delete a specific sample by index from SQLite database."""
    if not all([room, condition_key, sample_index is not None]):
        log.error("Room, condition_key, and sample_index are required")
        return {"success": False, "error": "Missing required parameters"}
    
    db_conn = _get_db_connection()
    if not db_conn:
        return {"success": False, "error": "Database connection failed"}
    
    try:
        cursor = db_conn.cursor()
        
        # Get all records for this room/condition, ordered by timestamp (same order as web interface)
        cursor.execute("""
            SELECT id FROM adaptive_learning 
            WHERE room = ? AND condition_key = ? 
            ORDER BY timestamp
        """, (room, condition_key))
        
        records = cursor.fetchall()
        
        if sample_index >= len(records):
            log.error(f"Sample index {sample_index} out of range (max: {len(records)-1})")
            return {"success": False, "error": "Sample index out of range"}
        
        # Get the ID of the record at the specified index
        record_id = records[sample_index]["id"]
        
        # Delete the specific record
        cursor.execute("DELETE FROM adaptive_learning WHERE id = ?", (record_id,))
        db_conn.commit()
        
        log.info(f"Deleted sample ID {record_id} for {room}/{condition_key} at index {sample_index}")
        
        db_conn.close()
        return {"success": True, "deleted_id": record_id}
        
    except Exception as e:
        log.error(f"Error deleting sample: {e}")
        if db_conn:
            db_conn.close()
        return {"success": False, "error": str(e)}

@service("pyscript.get_all_memory_stats")
def get_all_memory_stats():
    """Get summary statistics for all rooms."""
    db_conn = _get_db_connection()
    if not db_conn:
        return {"success": False, "error": "Database connection failed"}
    
    try:
        cursor = db_conn.cursor()
        
        # Get stats per room
        cursor.execute("""
            SELECT room, 
                   COUNT(*) as total_samples,
                   COUNT(DISTINCT condition_key) as conditions,
                   MIN(timestamp) as first_sample,
                   MAX(timestamp) as last_sample
            FROM adaptive_learning 
            GROUP BY room
            ORDER BY room
        """)
        
        results = cursor.fetchall()
        stats = {}
        
        for row in results:
            stats[row["room"]] = {
                "total_samples": row["total_samples"],
                "conditions": row["conditions"], 
                "first_sample": row["first_sample"],
                "last_sample": row["last_sample"]
            }
        
        db_conn.close()
        
        # Set sensor for web interface
        state.set("sensor.memory_stats_summary", "loaded", {
            "friendly_name": "Memory Statistics Summary",
            "stats": stats,
            "total_rooms": len(stats),
            "last_updated": datetime.datetime.now().isoformat()
        })
        
        return {"success": True, "stats": stats}
        
    except Exception as e:
        log.error(f"Error getting memory stats: {e}")
        if db_conn:
            db_conn.close()
        return {"success": False, "error": str(e)}

# Auto-load stats on startup
@time_trigger("startup")
def startup_load_stats():
    """Load memory stats on startup."""
    get_all_memory_stats()


# Minimal stub so the Teaching Dashboard "Apply Settings" button succeeds.
@service("pyscript.apply_room_settings")
def apply_room_settings(room=None, brightness=None, temperature=None):
    try:
        info = {
            "room": room,
            "brightness": brightness,
            "temperature": temperature,
            "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        }
        log.info(f"[ALS APPLY STUB] {info}")
        state.set("sensor.als_last_apply", "ok", {"friendly_name": "ALS Last Apply", **info})
        return {"success": True, **info}
    except Exception as e:
        log.error(f"Apply settings error: {e}")
        return {"success": False, "error": str(e)}
