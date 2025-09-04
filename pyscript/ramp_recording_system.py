# /config/pyscript/ramp_recording_system.py
# Advanced Ramp Recording & Analysis System with Seamless Curve Generation

import datetime
import sqlite3
import json
import asyncio
from scipy.interpolate import CubicSpline
import numpy as np

# Database connection
def _get_db_connection():
    """Connect to Home Assistant's SQLite database."""
    try:
        return sqlite3.connect("/config/home-assistant_v2.db", timeout=10.0)
    except Exception as e:
        log.error(f"Failed to connect to SQLite database: {e}")
        return None

# Utility functions
def _state(eid, d=None):
    try: return state.get(str(eid)) if state.get(str(eid)) not in (None, "", "unknown", "unavailable") else d
    except: return d

def _to_int(v, d=0):
    try: return int(float(v))
    except: return d

# ===== RAMP RECORDING SERVICES =====

@service("pyscript.start_ramp_recording")
def start_ramp_recording(room=None, session_name=None):
    """
    Start recording brightness changes for ramp analysis.
    Creates a new recording session and sets up monitoring.
    """
    if not room or not session_name:
        log.error("start_ramp_recording: 'room' and 'session_name' are required.")
        return
    
    session_id = f"{room}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    start_time = datetime.datetime.now().isoformat()
    
    # Create recording session
    db_conn = _get_db_connection()
    if not db_conn:
        return
        
    try:
        cursor = db_conn.cursor()
        
        # Create ramp recordings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ramp_recordings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                room TEXT NOT NULL,
                session_name TEXT NOT NULL,
                brightness INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                trigger_source TEXT,
                context_data TEXT
            )
        """)
        
        # Create session metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ramp_sessions (
                session_id TEXT PRIMARY KEY,
                room TEXT NOT NULL,
                session_name TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NULL,
                status TEXT DEFAULT 'recording',
                total_changes INTEGER DEFAULT 0,
                manual_changes INTEGER DEFAULT 0
            )
        """)
        
        # Insert session record
        cursor.execute("""
            INSERT INTO ramp_sessions (session_id, room, session_name, start_time)
            VALUES (?, ?, ?, ?)
        """, (session_id, room, session_name, start_time))
        
        db_conn.commit()
        
        # Set recording state in Home Assistant
        state.set("input_boolean.ramp_recording_active", "on")
        state.set("input_text.current_recording_session", session_id)
        state.set("input_text.current_recording_room", room)
        state.set("input_text.current_recording_name", session_name)
        
        # Schedule hourly reminder notification
        task.create(send_recording_reminder, hour=1)
        
        log.info(f"[RAMP RECORDING] Started session {session_id} for {room}")
        
        # Return session info to app
        state.set("sensor.ramp_recording_status", "recording", {
            "friendly_name": "Ramp Recording Status",
            "session_id": session_id,
            "room": room,
            "session_name": session_name,
            "start_time": start_time
        })
        
    except sqlite3.Error as e:
        log.error(f"start_ramp_recording: SQLite error: {e}")
    finally:
        if db_conn:
            db_conn.close()

@service("pyscript.stop_ramp_recording")
def stop_ramp_recording():
    """
    Stop current recording session and trigger analysis.
    """
    session_id = _state("input_text.current_recording_session")
    if not session_id:
        log.error("No active recording session found")
        return
    
    end_time = datetime.datetime.now().isoformat()
    
    # Update session as completed
    db_conn = _get_db_connection()
    if not db_conn:
        return
        
    try:
        cursor = db_conn.cursor()
        
        # Get session info
        cursor.execute("SELECT room, session_name, start_time FROM ramp_sessions WHERE session_id = ?", (session_id,))
        session_info = cursor.fetchone()
        
        if not session_info:
            log.error(f"Session {session_id} not found")
            return
            
        room, session_name, start_time = session_info
        
        # Update session as completed
        cursor.execute("""
            UPDATE ramp_sessions 
            SET end_time = ?, status = 'completed'
            WHERE session_id = ?
        """, (end_time, session_id))
        
        # Count changes
        cursor.execute("SELECT COUNT(*) FROM ramp_recordings WHERE session_id = ?", (session_id,))
        total_changes = cursor.fetchone()[0]
        
        cursor.execute("""
            UPDATE ramp_sessions 
            SET total_changes = ?
            WHERE session_id = ?
        """, (total_changes, session_id))
        
        db_conn.commit()
        
        # Clear recording state
        state.set("input_boolean.ramp_recording_active", "off")
        state.set("input_text.current_recording_session", "")
        state.set("input_text.current_recording_room", "")
        state.set("input_text.current_recording_name", "")
        
        log.info(f"[RAMP RECORDING] Stopped session {session_id}. Total changes: {total_changes}")
        
        # Trigger analysis
        task.create(analyze_ramp_recording, session_id=session_id)
        
    except sqlite3.Error as e:
        log.error(f"stop_ramp_recording: SQLite error: {e}")
    finally:
        if db_conn:
            db_conn.close()

@task_unique("send_recording_reminder")
def send_recording_reminder():
    """
    Send hourly reminder notifications during recording.
    """
    if not _state("input_boolean.ramp_recording_active") == "on":
        return  # Recording stopped
    
    session_id = _state("input_text.current_recording_session")
    room = _state("input_text.current_recording_room") 
    session_name = _state("input_text.current_recording_name")
    
    # Get recording duration and change count
    db_conn = _get_db_connection()
    if db_conn:
        try:
            cursor = db_conn.cursor()
            cursor.execute("""
                SELECT start_time, COUNT(r.id) as changes 
                FROM ramp_sessions s 
                LEFT JOIN ramp_recordings r ON s.session_id = r.session_id
                WHERE s.session_id = ?
                GROUP BY s.session_id
            """, (session_id,))
            
            result = cursor.fetchone()
            if result:
                start_time_str, changes = result
                start_time = datetime.datetime.fromisoformat(start_time_str)
                duration = datetime.datetime.now() - start_time
                hours = int(duration.total_seconds() / 3600)
                
                # Send rich notification
                service.call("notify", "mobile_app_franks_iphone", 
                    title="🎬 Recording Still Active",
                    message=f"{room} {session_name} - {hours}h recorded, {changes} changes",
                    data={
                        "push": {
                            "category": "RAMP_RECORDING",
                            "thread-id": "ramp-session"
                        },
                        "actions": [
                            {
                                "action": "STOP_RECORDING",
                                "title": "✅ Stop & Analyze", 
                                "icon": "sfsymbols:stop.circle.fill"
                            },
                            {
                                "action": "CONTINUE_1HR",
                                "title": "⏰ Continue 1hr",
                                "icon": "sfsymbols:clock"
                            },
                            {
                                "action": "CONTINUE_2HR", 
                                "title": "⏰ Continue 2hr",
                                "icon": "sfsymbols:clock.badge.plus"
                            }
                        ]
                    }
                )
                
        except sqlite3.Error as e:
            log.error(f"send_recording_reminder: SQLite error: {e}")
        finally:
            db_conn.close()
    
    # Schedule next reminder
    task.create(send_recording_reminder, hour=1)

@task_unique("analyze_ramp_recording")  
def analyze_ramp_recording(session_id=None):
    """
    Analyze completed recording session and create smooth ramp profile.
    Cross-references with HA logs to filter manual vs automated changes.
    """
    if not session_id:
        return
        
    db_conn = _get_db_connection()
    if not db_conn:
        return
    
    try:
        cursor = db_conn.cursor()
        
        # Get session info
        cursor.execute("""
            SELECT room, session_name, start_time, end_time 
            FROM ramp_sessions 
            WHERE session_id = ?
        """, (session_id,))
        
        session_info = cursor.fetchone()
        if not session_info:
            log.error(f"Session {session_id} not found for analysis")
            return
            
        room, session_name, start_time_str, end_time_str = session_info
        start_time = datetime.datetime.fromisoformat(start_time_str)
        end_time = datetime.datetime.fromisoformat(end_time_str)
        
        # Get all recorded changes
        cursor.execute("""
            SELECT brightness, timestamp 
            FROM ramp_recordings 
            WHERE session_id = ? 
            ORDER BY timestamp
        """, (session_id,))
        
        raw_data = cursor.fetchall()
        
        if len(raw_data) < 2:
            log.warning(f"Insufficient data points ({len(raw_data)}) for analysis")
            return
        
        # TODO: Cross-reference with HA logs to filter manual changes only
        # For now, using all data points
        
        # Create smooth ramp curve
        timestamps = []
        brightness_values = []
        
        for brightness, timestamp_str in raw_data:
            dt = datetime.datetime.fromisoformat(timestamp_str)
            # Convert to seconds from start
            seconds_from_start = (dt - start_time).total_seconds()
            timestamps.append(seconds_from_start)
            brightness_values.append(brightness)
        
        # Generate seamless curve using cubic spline
        total_duration = (end_time - start_time).total_seconds()
        
        if len(timestamps) >= 3:  # Need at least 3 points for cubic spline
            # Create smooth curve with 1-second resolution
            smooth_times = np.arange(0, total_duration, 1)  # Every second
            spline = CubicSpline(timestamps, brightness_values, bc_type='natural')
            smooth_brightness = spline(smooth_times)
            
            # Clamp values to valid range
            smooth_brightness = np.clip(smooth_brightness, 1, 100)
            
            # Create ramp profile data
            ramp_profile = {
                "session_id": session_id,
                "room": room,
                "session_name": session_name,
                "duration_seconds": int(total_duration),
                "original_points": len(raw_data),
                "smooth_points": len(smooth_brightness),
                "curve_data": [
                    {"time": int(t), "brightness": int(b)} 
                    for t, b in zip(smooth_times, smooth_brightness)
                ],
                "analysis": {
                    "start_brightness": int(brightness_values[0]),
                    "end_brightness": int(brightness_values[-1]),
                    "max_brightness": int(max(brightness_values)),
                    "min_brightness": int(min(brightness_values)),
                    "total_change": int(brightness_values[-1] - brightness_values[0])
                }
            }
            
            # Save ramp profile
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ramp_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    room TEXT NOT NULL,
                    profile_name TEXT NOT NULL,
                    duration_seconds INTEGER NOT NULL,
                    profile_data TEXT NOT NULL,
                    created_time TEXT NOT NULL,
                    status TEXT DEFAULT 'ready'
                )
            """)
            
            cursor.execute("""
                INSERT OR REPLACE INTO ramp_profiles 
                (session_id, room, profile_name, duration_seconds, profile_data, created_time)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id, 
                room, 
                session_name,
                int(total_duration),
                json.dumps(ramp_profile),
                datetime.datetime.now().isoformat()
            ))
            
            db_conn.commit()
            
            # Send completion notification
            service.call("notify", "mobile_app_franks_iphone",
                title="🎉 Ramp Analysis Complete!",
                message=f"{session_name} - Smooth curve created from {len(raw_data)} points",
                data={
                    "push": {
                        "category": "RAMP_ANALYSIS",
                        "thread-id": "ramp-analysis"
                    }
                }
            )
            
            log.info(f"[RAMP ANALYSIS] Created smooth profile for {session_id}: {len(raw_data)} → {len(smooth_brightness)} points")
            
        else:
            log.warning(f"Not enough points for cubic spline interpolation: {len(timestamps)}")
            
    except Exception as e:
        log.error(f"analyze_ramp_recording: Error: {e}")
    finally:
        if db_conn:
            db_conn.close()

@service("pyscript.get_ramp_profiles")
def get_ramp_profiles(room=None):
    """
    Get available ramp profiles for a room.
    """
    db_conn = _get_db_connection()
    if not db_conn:
        return []
    
    try:
        cursor = db_conn.cursor()
        
        query = "SELECT session_id, profile_name, duration_seconds, created_time, status FROM ramp_profiles"
        params = ()
        
        if room:
            query += " WHERE room = ?"
            params = (room,)
            
        query += " ORDER BY created_time DESC"
        
        cursor.execute(query, params)
        profiles = cursor.fetchall()
        
        return [
            {
                "session_id": row[0],
                "name": row[1], 
                "duration": f"{row[2]//3600}h {(row[2]%3600)//60}m",
                "created": row[3],
                "status": row[4]
            }
            for row in profiles
        ]
        
    except sqlite3.Error as e:
        log.error(f"get_ramp_profiles: SQLite error: {e}")
        return []
    finally:
        if db_conn:
            db_conn.close()

@service("pyscript.delete_ramp_profile")
def delete_ramp_profile(session_id=None):
    """
    Delete a ramp profile and its associated data.
    """
    if not session_id:
        return
        
    db_conn = _get_db_connection()
    if not db_conn:
        return
        
    try:
        cursor = db_conn.cursor()
        
        # Delete ramp profile
        cursor.execute("DELETE FROM ramp_profiles WHERE session_id = ?", (session_id,))
        
        # Delete recording data  
        cursor.execute("DELETE FROM ramp_recordings WHERE session_id = ?", (session_id,))
        
        # Delete session data
        cursor.execute("DELETE FROM ramp_sessions WHERE session_id = ?", (session_id,))
        
        db_conn.commit()
        
        log.info(f"[RAMP PROFILES] Deleted profile {session_id}")
        
    except sqlite3.Error as e:
        log.error(f"delete_ramp_profile: SQLite error: {e}")
    finally:
        if db_conn:
            db_conn.close()

# ===== LIGHT CHANGE MONITORING =====

@state_trigger("light.lamp_1", "light.lamp_2", "light.closet", 
               "light.kitchen_wled", "light.living_room_main", 
               "light.bathroom_main", "light.hallway", "light.laundry")
def monitor_light_changes(trigger_entity=None, new_state=None, old_state=None, **kwargs):
    """
    Monitor light changes during active recording sessions.
    Only logs MANUAL changes, filters out automation triggers.
    """
    if not _state("input_boolean.ramp_recording_active") == "on":
        return  # No active recording
        
    session_id = _state("input_text.current_recording_session")
    recording_room = _state("input_text.current_recording_room")
    
    if not session_id or not recording_room:
        return
    
    # Map entities to rooms (simplified mapping)
    entity_room_map = {
        "light.lamp_1": "bedroom",
        "light.lamp_2": "bedroom", 
        "light.closet": "closet",
        "light.kitchen_wled": "kitchen",
        "light.living_room_main": "living_room",
        "light.bathroom_main": "bathroom",
        "light.hallway": "hallway",
        "light.laundry": "laundry"
    }
    
    entity_room = entity_room_map.get(trigger_entity)
    if entity_room != recording_room.replace(" ", "_").lower():
        return  # Not the room being recorded
    
    # Check if this was a manual change (vs automation)
    context = kwargs.get('context', {})
    trigger_source = context.get('origin', 'unknown')
    
    # Only record manual changes
    if trigger_source not in ['LOCAL', 'REMOTE']:  # Manual sources
        return
    
    # Extract brightness from new state
    if not new_state or new_state.state == 'off':
        brightness = 0
    else:
        brightness = new_state.attributes.get('brightness_pct', 0)
        if not brightness:
            # Try to get from brightness attribute (0-255)
            raw_brightness = new_state.attributes.get('brightness', 0)
            brightness = int((raw_brightness / 255) * 100) if raw_brightness else 0
    
    # Record the change
    db_conn = _get_db_connection()
    if db_conn:
        try:
            cursor = db_conn.cursor()
            
            cursor.execute("""
                INSERT INTO ramp_recordings 
                (session_id, room, brightness, timestamp, trigger_source, context_data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                recording_room,
                brightness,
                datetime.datetime.now().isoformat(),
                trigger_source,
                json.dumps(context)
            ))
            
            db_conn.commit()
            
            log.debug(f"[RAMP RECORDING] Logged {recording_room} brightness change: {brightness}%")
            
        except sqlite3.Error as e:
            log.error(f"monitor_light_changes: SQLite error: {e}")
        finally:
            db_conn.close()