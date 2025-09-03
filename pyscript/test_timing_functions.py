# /config/pyscript/test_timing_functions.py
# Test functions for timing data encoding/decoding in ALS system
# Tests the routine timing learning enhancement functionality

def test_time_encoding():
    """Test encoding time to minutes since midnight for storage."""
    # Test cases for different times of day
    test_cases = [
        ("07:25:00", 445),  # 7:25 AM = 7*60 + 25 = 445 minutes
        ("00:00:00", 0),    # Midnight = 0 minutes  
        ("12:00:00", 720),  # Noon = 12*60 = 720 minutes
        ("23:59:00", 1439), # 11:59 PM = 23*60 + 59 = 1439 minutes
        ("05:30:15", 330),  # 5:30:15 AM = 5*60 + 30 = 330 (ignore seconds)
    ]
    
    for time_str, expected_minutes in test_cases:
        result = encode_time_to_minutes(time_str)
        assert result == expected_minutes, f"Failed encoding {time_str}: got {result}, expected {expected_minutes}"
    
    log.info("✅ Time encoding tests passed")

def test_time_decoding():
    """Test decoding minutes since midnight back to time string."""
    test_cases = [
        (445, "07:25"),   # 445 minutes = 7:25 AM
        (0, "00:00"),     # 0 minutes = midnight
        (720, "12:00"),   # 720 minutes = noon  
        (1439, "23:59"),  # 1439 minutes = 11:59 PM
        (330, "05:30"),   # 330 minutes = 5:30 AM
    ]
    
    for minutes, expected_time in test_cases:
        result = decode_minutes_to_time(minutes)
        assert result == expected_time, f"Failed decoding {minutes}: got {result}, expected {expected_time}"
    
    log.info("✅ Time decoding tests passed")

def test_confidence_encoding():
    """Test encoding confidence percentage to temperature field."""
    test_cases = [
        (85.5, 855),    # 85.5% = 855 in temperature field
        (100.0, 1000),  # 100% = 1000
        (0.0, 0),       # 0% = 0
        (67.3, 673),    # 67.3% = 673
        (99.9, 999),    # 99.9% = 999
    ]
    
    for confidence_pct, expected_encoded in test_cases:
        result = encode_confidence_to_temp(confidence_pct)
        assert result == expected_encoded, f"Failed encoding confidence {confidence_pct}: got {result}, expected {expected_encoded}"
    
    log.info("✅ Confidence encoding tests passed")

def test_day_type_classification():
    """Test day type classification logic."""
    # This would normally use actual HA state, but we'll test the logic
    test_cases = [
        ("2025-01-15", True, "work"),     # Wednesday, work day
        ("2025-01-18", False, "weekend"), # Saturday, weekend  
        ("2025-01-19", False, "weekend"), # Sunday, weekend
        ("2025-01-01", False, "holiday"), # New Year's Day
        ("2025-12-25", False, "holiday"), # Christmas
    ]
    
    for date_str, is_workday, expected_type in test_cases:
        result = classify_day_type(date_str, is_workday)
        assert result == expected_type, f"Failed classifying {date_str}: got {result}, expected {expected_type}"
    
    log.info("✅ Day type classification tests passed")

def test_condition_key_generation():
    """Test condition key generation for timing data storage."""
    test_cases = [
        ("work", "winter", 36, "work_winter_36"),
        ("weekend", "summer", 25, "weekend_summer_25"),  
        ("holiday", "spring", 12, "holiday_spring_12"),
        ("work", "fall", 45, "work_fall_45"),
    ]
    
    for day_type, season, week, expected_key in test_cases:
        result = generate_condition_key(day_type, season, week)
        assert result == expected_key, f"Failed generating key: got {result}, expected {expected_key}"
    
    log.info("✅ Condition key generation tests passed")

# Helper functions that will be implemented in als_memory_manager.py
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

def classify_day_type(date_str, is_workday):
    """Classify day type based on date and workday sensor."""
    # Check for common holidays first
    month_day = date_str[5:]  # Get MM-DD part
    if month_day in ["01-01", "12-25", "07-04", "11-11"]:  # New Year, Christmas, July 4th, Veterans Day
        return "holiday"
    elif month_day.startswith("12-2") and month_day >= "12-24":  # Christmas Eve, Christmas, Boxing Day period
        return "holiday"
    elif not is_workday:
        return "weekend"
    return "work"
def generate_condition_key(day_type, season, week):
    """Generate condition key for timing data storage.""" 
    return f"{day_type}_{season}_{week}"

# Test runner function
@state_trigger("input_boolean.run_timing_tests", "on")
def run_all_timing_tests():
    """Run all timing function tests."""
    try:
        log.info("🧪 Running timing data encoding/decoding tests...")
        test_time_encoding()
        test_time_decoding() 
        test_confidence_encoding()
        test_day_type_classification()
        test_condition_key_generation()
        log.info("✅ All timing tests passed successfully!")
        
        # Turn off the test trigger
        service.call("input_boolean", "turn_off", entity_id="input_boolean.run_timing_tests")
        
    except Exception as e:
        log.error(f"❌ Timing tests failed: {e}")
        service.call("input_boolean", "turn_off", entity_id="input_boolean.run_timing_tests")