"""
/config/pyscript/morning_ramp_system.py
VERSION 1.3.3 — unique service name, no collisions; helper updates via services
"""

import sqlite3
from datetime import datetime, date, time, timedelta

# ---------- small helpers ----------
def _svc(domain_dot_service: str, **kwargs):
    dom, svc = domain_dot_service.split(".", 1)
    service.call(dom, svc, **kwargs)

def _norm(v, d=None): return d if v in (None, "", "unknown", "unavailable") else v
def _to_int(v, d=0):
    try: return int(float(v))
    except Exception: return d
def _state(eid, d=None):
    try: return _norm(state.get(str(eid)), d)
    except Exception: return d
def _exists(eid) -> bool:
    try: return state.get(eid) is not None
    except Exception: return False

# ---------- DB bootstrap (kept minimal) ----------
def _get_db_connection():
    try:
        return sqlite3.connect("/config/home-assistant_v2.db", timeout=10.0)
    except Exception as e:
        log.error(f"[MorningRamp] DB connect failed: {e}")
        return None

def _ensure_database_tables():
    db = _get_db_connection()
    if not db: return False
    try:
        cur = db.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS morning_ramp_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                completion_time TEXT NOT NULL,
                season TEXT NOT NULL,
                work_day BOOLEAN NOT NULL,
                duration_minutes INTEGER NOT NULL,
                trigger_source TEXT NOT NULL,
                weather_conditions TEXT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        db.commit()
        log.info("[MorningRamp] DB tables ensured")
        return True
    except Exception as e:
        log.error(f"[MorningRamp] DB table creation error: {e}")
        return False
    finally:
        try: db.close()
        except Exception: pass

# ---------- state gates ----------
def is_ramp_enabled(): return _state('input_boolean.sleep_in_ramp_system_enable', 'off') == 'on'
def is_ramp_active():  return _state('input_boolean.sleep_in_ramp_active', 'off') == 'on'

# optional helper for daily guard (if you create it)
LAST_RUN_HELPER = "input_text.morning_ramp_last_run_date"

def _already_ran_today() -> bool:
    # prefer input_text if present; fall back to daily_motion_lock
    if _exists(LAST_RUN_HELPER):
        s = _state(LAST_RUN_HELPER, "")
        try:
            return s and datetime.strptime(s, "%Y-%m-%d").date() == date.today()
        except Exception:
            return False
    return _state('input_boolean.daily_motion_lock') == 'on'

def _mark_ran_today():
    if _exists(LAST_RUN_HELPER):
        _svc("input_text.set_value", entity_id=LAST_RUN_HELPER, value=date.today().strftime("%Y-%m-%d"))
    _svc("input_boolean.turn_on", entity_id="input_boolean.daily_motion_lock")

# ---------- controller ----------
class RampController:
    def __init__(self):
        self.trigger_source = "N/A"

    def get_progress_percent(self):
        if not is_ramp_active(): return 0
        start_s = _state('input_datetime.ramp_start_time')
        dur = _to_int(_state('input_number.calculated_ramp_duration'), 45)
        if not start_s or dur == 0: return 0
        start_dt = datetime.fromisoformat(start_s.replace('Z',''))
        elapsed = (datetime.now() - start_dt).total_seconds() / 60
        return int(max(0, min(100, (elapsed / dur) * 100)))

    def start_ramp(self, trigger_sensor: str, motion_dt: datetime):
        log.info(f"[MorningRamp] Starting from sensor: {trigger_sensor}")
        self.trigger_source = trigger_sensor or "N/A"
        workday = _state('binary_sensor.working_today', 'off') == 'on'
        base = _to_int(_state('input_number.workday_ramp_base_duration'), 50) if workday \
               else _to_int(_state('input_number.offday_ramp_base_duration'), 75)
        duration = max(15, min(120, base))

        # active flag
        _svc("input_boolean.turn_on", entity_id="input_boolean.sleep_in_ramp_active")

        # timestamps & duration
        _svc("input_datetime.set_datetime",
             entity_id="input_datetime.ramp_start_time",
             datetime=motion_dt.strftime("%Y-%m-%d %H:%M:%S"))
        _svc("input_number.set_value",
             entity_id="input_number.calculated_ramp_duration",
             value=duration)
        _svc("input_datetime.set_datetime",
             entity_id="input_datetime.ramp_calculated_end_time",
             datetime=(motion_dt + timedelta(minutes=duration)).strftime("%Y-%m-%d %H:%M:%S"))
        _svc("input_datetime.set_datetime",
             entity_id="input_datetime.first_kitchen_motion_today",
             datetime=motion_dt.strftime("%Y-%m-%d %H:%M:%S"))

        # Detect work day based on motion timing
        motion_hour = motion_dt.hour
        motion_minute = motion_dt.minute
        is_work_window = (motion_hour == 4 and motion_minute >= 50) or (motion_hour == 5 and motion_minute == 0)
        
        # Set the motion-based work day detection entity
        state.set("pyscript.motion_work_day_detected", "on" if is_work_window else "off", 
                  {"friendly_name": "Motion Work Day Detected", 
                   "icon": "mdi:briefcase" if is_work_window else "mdi:home",
                   "motion_time": motion_dt.strftime("%H:%M:%S"),
                   "detected_as": "work_day" if is_work_window else "off_day"})
        
        log.info(f"[MorningRamp] Motion at {motion_dt.strftime('%H:%M:%S')} detected as {'WORK' if is_work_window else 'OFF'} day")

        # lock for the day & home state
        _svc("input_boolean.turn_on", entity_id="input_boolean.daily_motion_lock")
        _svc("input_select.select_option",
             entity_id="input_select.home_state",
             option="Early Morning")

        log.info(f"[MorningRamp] Ramp started: duration={duration}m, work_day={workday}")

    def end_ramp(self, reason="completed"):
        if is_ramp_active():
            _svc("input_boolean.turn_off", entity_id="input_boolean.sleep_in_ramp_active")
            log.info(f"[MorningRamp] Ramp ended: reason={reason}")

ramp_controller = RampController()

# ---------- UNIQUE SERVICE (no collisions) ----------
@service("pyscript.morning_ramp_first_motion")
def morning_ramp_first_motion(sensor=None, timestamp=None):
    """
    First motion after 04:45 while Home State = Night starts the ramp.
    One-per-day guard via input_text.morning_ramp_last_run_date (if present) or daily_motion_lock.
    """
    if not is_ramp_enabled():
        log.info("[MorningRamp] Ignored: ramp disabled")
        return
    if is_ramp_active():
        log.info("[MorningRamp] Ignored: ramp already active")
        return
    if _already_ran_today():
        log.info("[MorningRamp] Ignored: already ran today")
        return

    now = datetime.now()
    hs  = _state('input_select.home_state')

    if hs == 'Night' and now.time() >= time(4,45,0):
        ramp_controller.start_ramp(sensor, now)
        _mark_ran_today()
    else:
        log.info(f"[MorningRamp] Ignored: hs={hs}, now={now.strftime('%H:%M:%S')} (needs Night & >= 04:45)")

@service("pyscript.living_room_lamp_turned_off")
def living_room_lamp_turned_off(lamp=None, timestamp=None):
    if is_ramp_enabled() and is_ramp_active():
        ramp_controller.end_ramp(f"lamp_off_{lamp}")

@service("pyscript.emergency_disable_morning_ramp")
def emergency_disable_morning_ramp():
    log.warning("[MorningRamp] EMERGENCY DISABLE: Reverting to original YAML system")
    _svc("input_boolean.turn_off", entity_id="input_boolean.sleep_in_ramp_system_enable")
    if is_ramp_active():
        _svc("input_boolean.turn_off", entity_id="input_boolean.sleep_in_ramp_active")
    _svc("persistent_notification.create",
         message="Morning ramp PyScript system disabled. Original YAML system restored.",
         title="System Reverted")

# ---------- dashboard sensors ----------
@time_trigger("startup", "cron(* * * * *)")
def update_ramp_entities():
    if not is_ramp_enabled():
        state.set("sensor.morning_ramp_current_status", "Disabled",
                  {"icon": "mdi:power-off", "friendly_name": "Morning Ramp Status"})
        state.set("sensor.sleep_in_ramp_progress", 0,
                  {"unit_of_measurement": "%", "friendly_name": "Sleep In Ramp Progress"})
        state.set("sensor.morning_ramp_predicted_end_time", "N/A",
                  {"icon": "mdi:clock-outline", "friendly_name": "Predicted End Time"})
        state.set("sensor.morning_ramp_time_remaining", "N/A",
                  {"icon": "mdi:timer-outline", "friendly_name": "Time Remaining"})
        # learning placeholders
        state.set("sensor.morning_ramp_learning_data_count", 0,
                  {"icon": "mdi:database", "friendly_name": "Learning Samples"})
        state.set("sensor.morning_ramp_prediction_accuracy", "N/A",
                  {"icon": "mdi:target", "friendly_name": "Prediction Accuracy"})
        state.set("sensor.morning_ramp_learned_duration", "N/A",
                  {"icon": "mdi:school", "friendly_name": "Learned Duration"})
        state.set("sensor.morning_ramp_confidence_level", "N/A",
                  {"icon": "mdi:gauge", "friendly_name": "Prediction Confidence"})
        state.set("sensor.morning_ramp_weather_adjustment", "N/A",
                  {"icon": "mdi:weather-cloudy", "friendly_name": "Weather Adjustment"})
        state.set("sensor.morning_ramp_last_completion_time", "N/A",
                  {"icon": "mdi:history", "friendly_name": "Last Completion Time"})
        state.set("sensor.morning_ramp_trigger_source", "N/A",
                  {"icon": "mdi:gesture-tap", "friendly_name": "Triggered By"})
        return

    progress = ramp_controller.get_progress_percent()
    active = is_ramp_active()
    status = f"Active - {progress}% complete" if active else "Waiting for motion detection"

    state.set("sensor.morning_ramp_current_status", status,
              {"icon": "mdi:weather-sunrise" if active else "mdi:sleep",
               "friendly_name": "Morning Ramp Status"})
    state.set("sensor.sleep_in_ramp_progress", progress,
              {"unit_of_measurement": "%", "friendly_name": "Sleep In Ramp Progress"})

    if active:
        end_s = _state('input_datetime.ramp_calculated_end_time')
        if end_s:
            end_dt = datetime.fromisoformat(end_s.replace('Z',''))
            remaining = max(0, _to_int((end_dt - datetime.now()).total_seconds() / 60))
            state.set("sensor.morning_ramp_predicted_end_time", end_dt.strftime("%-I:%M %p"),
                      {"icon": "mdi:clock-outline", "friendly_name": "Predicted End Time"})
            state.set("sensor.morning_ramp_time_remaining", f"{remaining} min",
                      {"icon": "mdi:timer-outline", "friendly_name": "Time Remaining"})
        state.set("sensor.morning_ramp_trigger_source", ramp_controller.trigger_source,
                  {"icon": "mdi:gesture-tap", "friendly_name": "Triggered By"})
    else:
        state.set("sensor.morning_ramp_predicted_end_time", "N/A",
                  {"icon": "mdi:clock-outline", "friendly_name": "Predicted End Time"})
        state.set("sensor.morning_ramp_time_remaining", "N/A",
                  {"icon": "mdi:timer-outline", "friendly_name": "Time Remaining"})
        state.set("sensor.morning_ramp_trigger_source", "N/A",
                  {"icon": "mdi:gesture-tap", "friendly_name": "Triggered By"})

# ---------- midnight reset ----------
@time_trigger("cron(0 0 * * *)")
def daily_reset():
    if is_ramp_enabled():
        _svc('input_boolean.turn_off', entity_id='input_boolean.daily_motion_lock')
        if _exists(LAST_RUN_HELPER):
            _svc("input_text.set_value", entity_id=LAST_RUN_HELPER, value="")
        _svc("input_datetime.set_datetime",
             entity_id="input_datetime.first_kitchen_motion_today",
             datetime=datetime.now().strftime("%Y-%m-%d 00:00:00"))
        
        # Reset motion work day detection
        state.set("pyscript.motion_work_day_detected", "unknown", 
                  {"friendly_name": "Motion Work Day Detected",
                   "icon": "mdi:help-circle",
                   "motion_time": "not_detected_today",
                   "detected_as": "pending"})

# ---------- startup ----------
@time_trigger("startup")
def initialize_morning_ramp_system():
    log.info("[MorningRamp] Initializing...")
    _ensure_database_tables()
    update_ramp_entities()
    log.info("[MorningRamp] Ready")