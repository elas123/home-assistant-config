# /config/pyscript/als_memory_manager.py
# Uses PyMySQL for storage management - HARDCODED TEST VERSION
# !!! PYSCRIPT FUNCTIONS (motion detection, overrides) !!!
import sqlite3

# --- Database Connection (SQLITE VERSION) ---
def _get_db_connection():
    """Connect to Home Assistant's SQLite database."""
    try:
        conn = sqlite3.connect("/config/home-assistant_v2.db", timeout=10.0)
        conn.row_factory = sqlite3.Row  # Makes results easier to work with
        
        # Ensure table exists
        cursor = conn.cursor()
        # Ensure table exists with temperature support
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
        # Migrate if legacy table missing temperature column
        try:
            cursor.execute("PRAGMA table_info(adaptive_learning)")
            cols = [row[1] for row in cursor.fetchall()]
            if "temperature_kelvin" not in cols:
                cursor.execute("ALTER TABLE adaptive_learning ADD COLUMN temperature_kelvin INTEGER NULL")
                conn.commit()
        except Exception as _:
            # Non-fatal; reading code tolerates NULLs
            pass
        
        return conn
        
    except Exception as e:
        log.error(f"Failed to connect to SQLite database from memory manager: {e}")
        return None

# --- Helper Functions ---
def _norm_room(room_str):
    """Normalizes room name from Lovelace."""
    r = str(room_str).lower().replace(" ", "_")
    return "living_room" if r == "livingroom" else r

# --- Services to Power the Form ---

@state_trigger("input_select.als_teaching_room")
def populate_condition_keys(value=None):
    """When a room is selected, this populates the second dropdown with its condition keys from the database."""
    room_key = _norm_room(value)
    options = ["No learned data for this room"]

    db_conn = _get_db_connection()
    if db_conn:
        try:
            cursor = db_conn.cursor()
            sql = "SELECT DISTINCT condition_key FROM adaptive_learning WHERE room = ? ORDER BY condition_key"
            cursor.execute(sql, (room_key,))
            results = cursor.fetchall()
            if results:
                options = [row['condition_key'] for row in results]
        except Exception as e:
            log.error(f"Error fetching condition keys: {e}")
        finally:
            if db_conn:
                db_conn.close()

    service.call("input_select", "set_options", entity_id="input_select.als_memory_condition_key", options=options)
    service.call("input_select", "select_option", entity_id="input_select.als_memory_condition_key", option=options[0])
    service.call("input_select", "set_options", entity_id="input_select.als_memory_sample", options=["Select a condition first"])


@state_trigger("input_select.als_memory_condition_key")
def populate_samples(value=None):
    """When a condition key is selected, this populates the third dropdown with its individual samples from the database."""
    condition_key = value
    room_key = _norm_room(state.get("input_select.als_teaching_room"))
    options = ["No samples for this condition"]

    db_conn = _get_db_connection()
    if db_conn:
        try:
            cursor = db_conn.cursor()
            sql = "SELECT id, brightness_percent FROM adaptive_learning WHERE room = ? AND condition_key = ? ORDER BY timestamp"
            cursor.execute(sql, (room_key, condition_key))
            results = cursor.fetchall()
            if results:
                options = [f"ID {row['id']}: {row['brightness_percent']}%" for row in results]
        except Exception as e:
            log.error(f"Error fetching samples: {e}")
        finally:
            if db_conn:
                db_conn.close()

    service.call("input_select", "set_options", entity_id="input_select.als_memory_sample", options=options)
    service.call("input_select", "select_option", entity_id="input_select.als_memory_sample", option=options[0])

@service("pyscript.als_delete_selected_sample")
def als_delete_selected_sample():
    """Deletes the single sample currently selected in the dropdowns from the database."""
    selected_sample_str = state.get("input_select.als_memory_sample")

    try:
        sample_id = int(selected_sample_str.split(":")[0].replace("ID ", ""))
    except (ValueError, AttributeError):
        log.error("Could not determine which sample ID to delete.")
        return

    db_conn = _get_db_connection()
    if db_conn:
        try:
            cursor = db_conn.cursor()
            sql = "DELETE FROM adaptive_learning WHERE id = ?"
            cursor.execute(sql, (sample_id,))
            db_conn.commit()
            log.info(f"Deleted sample with ID {sample_id} from the database.")

            populate_condition_keys(value=state.get("input_select.als_teaching_room"))
        except Exception as e:
            log.error(f"Error deleting sample: {e}")
        finally:
            if db_conn:
                db_conn.close()

@service("pyscript.als_delete_condition_key")
def als_delete_condition_key(room=None, condition_key=None):
    """Deletes all samples for a given condition key in a room's memory from the database."""
    room_key = _norm_room(room)

    db_conn = _get_db_connection()
    if db_conn:
        try:
            cursor = db_conn.cursor()
            sql = "DELETE FROM adaptive_learning WHERE room = ? AND condition_key = ?"
            cursor.execute(sql, (room_key, condition_key))
            db_conn.commit()
            log.info(f"Deleted all samples for condition key '{condition_key}' from {room_key}")
        except Exception as e:
            log.error(f"Error deleting condition key: {e}")
        finally:
            if db_conn:
                db_conn.close()

# --- Timing Data Functions (Routine Learning Enhancement) ---

def encode_time_to_minutes(time_str):
    """Convert time string (HH:MM:SS) to minutes since midnight."""
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    return hours * 60 + minutes

def decode_minutes_to_time(minutes):
    """Convert minutes since midnight to time string (HH:MM)."""
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"

def encode_confidence_to_temp(confidence_pct):
    """Encode confidence percentage to temperature field (0-1000)."""
    return int(confidence_pct * 10)

def decode_temp_to_confidence(temp_value):
    """Decode temperature field back to confidence percentage."""
    return temp_value / 10.0 if temp_value else 0.0

def get_current_season():
    """Determine current season based on date."""
    import datetime
    month = datetime.datetime.now().month
    
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer" 
    else:  # 9, 10, 11
        return "fall"

def get_week_of_year():
    """Get current week number of the year."""
    import datetime
    return datetime.datetime.now().isocalendar()[1]

def classify_day_type():
    """Classify current day type based on workday sensor."""
    workday_state = state.get("binary_sensor.workday_sensor")
    
    if workday_state == "on":
        return "work"
    else:
        # Could add holiday detection logic here in the future
        return "weekend"

def generate_timing_condition_key(day_type=None, season=None, week=None):
    """Generate condition key for timing data storage."""
    if not day_type:
        day_type = classify_day_type()
    if not season:
        season = get_current_season()
    if not week:
        week = get_week_of_year()
    
    return f"{day_type}_{season}_{week}"

@service("pyscript.store_routine_timing")
def store_routine_timing(completion_time_str=None, confidence_pct=85.0):
    """Store routine completion timing in ALS database."""
    if not completion_time_str:
        import datetime
        completion_time_str = datetime.datetime.now().strftime("%H:%M:%S")
    
    # Encode timing data for storage
    minutes_encoded = encode_time_to_minutes(completion_time_str)
    confidence_encoded = encode_confidence_to_temp(confidence_pct)
    condition_key = generate_timing_condition_key()
    
    db_conn = _get_db_connection()
    if db_conn:
        try:
            cursor = db_conn.cursor()
            sql = """
                INSERT INTO adaptive_learning 
                (room, condition_key, brightness_percent, temperature_kelvin, timestamp)
                VALUES (?, ?, ?, ?, datetime('now'))
            """
            cursor.execute(sql, (
                "routine_timing",
                condition_key, 
                minutes_encoded,
                confidence_encoded
            ))
            db_conn.commit()
            log.info(f"Stored routine timing: {completion_time_str} ({condition_key}) with {confidence_pct}% confidence")
            
        except Exception as e:
            log.error(f"Error storing routine timing: {e}")
        finally:
            if db_conn:
                db_conn.close()

@service("pyscript.get_timing_patterns") 
def get_timing_patterns(day_type=None, season=None, limit=30):
    """Retrieve timing patterns for analysis."""
    room_key = "routine_timing"
    patterns = []
    
    db_conn = _get_db_connection()
    if db_conn:
        try:
            cursor = db_conn.cursor()
            
            # Build query based on filters
            where_clauses = ["room = ?"]
            params = [room_key]
            
            if day_type:
                where_clauses.append("condition_key LIKE ?")
                params.append(f"{day_type}_%")
            
            if season:
                where_clauses.append("condition_key LIKE ?")
                params.append(f"%_{season}_%")
            
            sql = f"""
                SELECT condition_key, brightness_percent, temperature_kelvin, timestamp
                FROM adaptive_learning 
                WHERE {' AND '.join(where_clauses)}
                ORDER BY timestamp DESC
                LIMIT ?
            """
            params.append(limit)
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            for row in results:
                patterns.append({
                    'condition_key': row['condition_key'],
                    'completion_time': decode_minutes_to_time(row['brightness_percent']),
                    'completion_minutes': row['brightness_percent'],
                    'confidence': decode_temp_to_confidence(row['temperature_kelvin']),
                    'timestamp': row['timestamp']
                })
                
        except Exception as e:
            log.error(f"Error retrieving timing patterns: {e}")
        finally:
            if db_conn:
                db_conn.close()
    
    return patterns

@service("pyscript.analyze_timing_patterns")
def analyze_timing_patterns(day_type=None, season=None, min_samples=3):
    """Analyze timing patterns and generate predictions."""
    patterns = get_timing_patterns(day_type=day_type, season=season, limit=90)
    
    if len(patterns) < min_samples:
        return {
            'prediction': None,
            'confidence': 0.0,
            'sample_count': len(patterns),
            'message': f'Insufficient data: need {min_samples} samples, have {len(patterns)}'
        }
    
    # Calculate statistics
    completion_times = [p['completion_minutes'] for p in patterns]
    confidences = [p['confidence'] for p in patterns]
    
    # Calculate weighted average (recent patterns weighted more heavily)
    total_weight = 0
    weighted_sum = 0
    
    for i, (minutes, conf) in enumerate(zip(completion_times, confidences)):
        # Recent patterns get higher weight (index 0 is most recent)
        recency_weight = 1.0 - (i / len(completion_times)) * 0.3  # 30% decay
        confidence_weight = conf / 100.0  # Convert percentage to 0-1
        
        weight = recency_weight * confidence_weight
        weighted_sum += minutes * weight
        total_weight += weight
    
    predicted_minutes = int(weighted_sum / total_weight) if total_weight > 0 else int(sum(completion_times) / len(completion_times))
    predicted_time = decode_minutes_to_time(predicted_minutes)
    
    # Calculate confidence based on consistency
    import statistics
    std_dev = statistics.stdev(completion_times) if len(completion_times) > 1 else 0
    avg_confidence = sum(confidences) / len(confidences)
    
    # Lower standard deviation = higher confidence
    consistency_factor = max(0, 100 - std_dev * 2)  # 2 minutes std dev = 4 point penalty
    final_confidence = min(100, (avg_confidence + consistency_factor) / 2)
    
    return {
        'prediction': predicted_time,
        'prediction_minutes': predicted_minutes,
        'confidence': round(final_confidence, 1),
        'sample_count': len(patterns),
        'std_deviation': round(std_dev, 1),
        'avg_confidence': round(avg_confidence, 1),
        'recent_patterns': [{'time': p['completion_time'], 'date': p['timestamp'][:10]} for p in patterns[:5]]
    }

@service("pyscript.predict_routine_end_time")
def predict_routine_end_time():
    """Predict when current routine will end based on learned patterns."""
    current_day_type = classify_day_type()
    current_season = get_current_season()
    
    # Try specific match first (day_type + season)
    analysis = analyze_timing_patterns(day_type=current_day_type, season=current_season)
    
    if analysis['confidence'] < 60 or analysis['sample_count'] < 3:
        # Fall back to day type only
        analysis = analyze_timing_patterns(day_type=current_day_type)
        
        if analysis['confidence'] < 40 or analysis['sample_count'] < 2:
            # Fall back to all patterns
            analysis = analyze_timing_patterns()
    
    # Log the prediction
    if analysis['prediction']:
        log.info(f"Routine end prediction: {analysis['prediction']} ({analysis['confidence']}% confidence, {analysis['sample_count']} samples)")
    else:
        log.warning(f"No routine prediction available: {analysis['message']}")
    
    return analysis
