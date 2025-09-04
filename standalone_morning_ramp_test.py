#!/usr/bin/env python3
"""
Test script for Morning Ramp System
Run this to validate the logic before deploying to Home Assistant
"""

import sqlite3
from datetime import datetime, time, date, timedelta
from unittest.mock import Mock, patch
import sys
import os

# Mock the pyscript environment
class MockState:
    def __init__(self):
        self.states = {}
    
    def get(self, entity_id):
        return self.states.get(entity_id, "unknown")
    
    def set(self, entity_id, value, attributes=None):
        self.states[entity_id] = value

class MockService:
    def call(self, domain, service, **kwargs):
        print(f"Service called: {domain}.{service} with {kwargs}")
        return None

class MockLog:
    def info(self, msg):
        print(f"INFO: {msg}")
    
    def error(self, msg):
        print(f"ERROR: {msg}")
    
    def warning(self, msg):
        print(f"WARNING: {msg}")
    
    def debug(self, msg):
        print(f"DEBUG: {msg}")

# Mock globals
state = MockState()
service = MockService()
log = MockLog()

# Import the functions from your script (we'll test them individually)
def _norm(v, d=None):
    return d if v in (None, "", "unknown", "unavailable") else v

def _to_int(v, d=0):
    try:
        return int(float(v))
    except Exception:
        return d

def _state(eid, d=None):
    try:
        return _norm(state.get(str(eid)), d)
    except Exception:
        return d

def _exists(eid) -> bool:
    try:
        return state.get(eid) is not None
    except Exception:
        return False

def is_ramp_enabled():
    return _state('input_boolean.sleep_in_ramp_system_enable', 'off') == 'on'

def is_ramp_active():
    return _state('input_boolean.sleep_in_ramp_active', 'off') == 'on'

def _already_ran_today() -> bool:
    LAST_RUN_HELPER = "input_text.morning_ramp_last_run_date"
    if _exists(LAST_RUN_HELPER):
        s = _state(LAST_RUN_HELPER, "")
        try:
            return s and datetime.strptime(s, "%Y-%m-%d").date() == date.today()
        except Exception:
            return False
    return _state('input_boolean.daily_motion_lock') == 'on'

class RampController:
    def __init__(self):
        self.trigger_source = "N/A"

    def get_progress_percent(self):
        if not is_ramp_active():
            return 0
        
        # Mock these for testing
        state.states['input_datetime.ramp_start_time'] = '2024-01-01 06:00:00'
        state.states['input_number.calculated_ramp_duration'] = '45'
        
        start_s = _state('input_datetime.ramp_start_time')
        dur = _to_int(_state('input_number.calculated_ramp_duration'), 45)
        
        if not start_s or dur == 0:
            return 0
        
        start_dt = datetime.fromisoformat(start_s.replace('Z', ''))
        elapsed = (datetime.now() - start_dt).total_seconds() / 60
        return int(max(0, min(100, (elapsed / dur) * 100)))

    def start_ramp(self, trigger_sensor: str, motion_dt: datetime):
        print(f"Starting ramp from sensor: {trigger_sensor}")
        self.trigger_source = trigger_sensor or "N/A"
        
        # Mock workday detection
        workday = _state('binary_sensor.working_today', 'off') == 'on'
        base = _to_int(_state('input_number.workday_ramp_base_duration'), 50) if workday \
               else _to_int(_state('input_number.offday_ramp_base_duration'), 75)
        duration = max(15, min(120, base))
        
        print(f"Ramp duration: {duration}m, workday: {workday}")
        
        # Test work day detection logic
        motion_hour = motion_dt.hour
        motion_minute = motion_dt.minute
        is_work_window = (motion_hour == 4 and motion_minute >= 50) or (motion_hour == 5 and motion_minute == 0)
        
        print(f"Motion at {motion_dt.strftime('%H:%M:%S')} detected as {'WORK' if is_work_window else 'OFF'} day")
        
        return duration, workday, is_work_window

def test_morning_window_logic():
    """Test the morning time window detection"""
    print("\n=== Testing Morning Window Logic ===")
    
    test_cases = [
        # (hour, minute, expected_result, description)
        (4, 44, False, "Before morning window (4:44)"),
        (4, 45, True, "Start of morning window (4:45)"),
        (6, 30, True, "Middle of morning window (6:30)"),
        (7, 59, True, "End of morning window (7:59)"),
        (8, 0, True, "Exactly end of morning window (8:00)"),
        (8, 1, False, "After morning window (8:01)"),
        (12, 0, False, "Noon (should be False)"),
        (0, 0, False, "Midnight (should be False)"),
    ]
    
    for hour, minute, expected, description in test_cases:
        test_time = time(hour, minute)
        morning_start = time(4, 45)
        morning_end = time(8, 0)
        result = morning_start <= test_time <= morning_end
        
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: {description} -> {result} (expected {expected})")

def test_work_day_detection():
    """Test the work day detection logic"""
    print("\n=== Testing Work Day Detection Logic ===")
    
    test_cases = [
        # (hour, minute, expected_result, description)
        (4, 49, False, "4:49 AM (before work window)"),
        (4, 50, True, "4:50 AM (start of work window)"),
        (4, 59, True, "4:59 AM (work window)"),
        (5, 0, True, "5:00 AM (work window)"),
        (5, 1, False, "5:01 AM (after work window)"),
        (6, 0, False, "6:00 AM (should be False)"),
    ]
    
    for hour, minute, expected, description in test_cases:
        motion_dt = datetime(2024, 1, 1, hour, minute)
        motion_hour = motion_dt.hour
        motion_minute = motion_dt.minute
        result = (motion_hour == 4 and motion_minute >= 50) or (motion_hour == 5 and motion_minute == 0)
        
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: {description} -> {result} (expected {expected})")

def test_ramp_controller():
    """Test the ramp controller logic"""
    print("\n=== Testing Ramp Controller ===")
    
    controller = RampController()
    
    # Test 1: Normal work day motion
    print("\nTest 1: Work day motion at 4:55 AM")
    motion_dt = datetime(2024, 1, 1, 4, 55)
    duration, workday, is_work = controller.start_ramp("test_sensor", motion_dt)
    print(f"Duration: {duration}m, Workday: {workday}, Is Work Window: {is_work}")
    
    # Test 2: Off day motion
    print("\nTest 2: Off day motion at 6:30 AM")
    motion_dt = datetime(2024, 1, 1, 6, 30)
    duration, workday, is_work = controller.start_ramp("test_sensor", motion_dt)
    print(f"Duration: {duration}m, Workday: {workday}, Is Work Window: {is_work}")

def test_daily_lock():
    """Test the daily run lock mechanism"""
    print("\n=== Testing Daily Run Lock ===")
    
    # Reset state
    state.states = {}
    
    # Test with input_text helper
    state.states['input_text.morning_ramp_last_run_date'] = date.today().strftime("%Y-%m-%d")
    result = _already_ran_today()
    print(f"With today's date in input_text: {result} (should be True)")
    
    # Test with yesterday's date
    state.states['input_text.morning_ramp_last_run_date'] = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    result = _already_ran_today()
    print(f"With yesterday's date in input_text: {result} (should be False)")
    
    # Test with daily_motion_lock
    state.states = {}
    state.states['input_boolean.daily_motion_lock'] = 'on'
    result = _already_ran_today()
    print(f"With daily_motion_lock on: {result} (should be True)")

def test_service_triggers():
    """Test the service trigger conditions"""
    print("\n=== Testing Service Trigger Conditions ===")
    
    # Set up test state
    state.states = {
        'input_boolean.sleep_in_ramp_system_enable': 'on',
        'input_boolean.sleep_in_ramp_active': 'off',
        'input_select.home_state': 'Night'
    }
    
    # Test cases for different times and home states
    test_cases = [
        # (time, home_state, should_trigger, description)
        ((4, 44), 'Night', False, "4:44 AM, Night mode"),
        ((4, 45), 'Night', True, "4:45 AM, Night mode"),
        ((6, 0), 'Night', True, "6:00 AM, Night mode"),
        ((7, 59), 'Night', True, "7:59 AM, Night mode"),
        ((8, 0), 'Night', True, "8:00 AM, Night mode"),
        ((8, 1), 'Night', False, "8:01 AM, Night mode"),
        ((6, 0), 'Day', False, "6:00 AM, Day mode"),
        ((6, 0), 'Evening', False, "6:00 AM, Evening mode"),
    ]
    
    for (hour, minute), home_state, should_trigger, description in test_cases:
        state.states['input_select.home_state'] = home_state
        test_time = time(hour, minute)
        morning_start = time(4, 45)
        morning_end = time(8, 0)
        in_morning_window = morning_start <= test_time <= morning_end
        
        # This mimics the logic from your service
        would_trigger = (home_state == 'Night' and in_morning_window)
        
        status = "PASS" if would_trigger == should_trigger else "FAIL"
        print(f"{status}: {description} -> {would_trigger} (expected {should_trigger})")

def main():
    """Run all tests"""
    print("Morning Ramp System Test Suite")
    print("=" * 50)
    
    test_morning_window_logic()
    test_work_day_detection()
    test_ramp_controller()
    test_daily_lock()
    test_service_triggers()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    
    # Ask user if they want to see the critical issue
    print("\nCRITICAL ISSUE DETECTED:")
    print("The work day detection logic only detects:")
    print("  - 4:50 AM to 4:59 AM as work days")
    print("  - Exactly 5:00 AM as work day")
    print("  - All other times (including 5:01 AM to 5:59 AM) as non-work days")
    print("\nThis seems very restrictive. Did you intend this behavior?")

if __name__ == "__main__":
    main()