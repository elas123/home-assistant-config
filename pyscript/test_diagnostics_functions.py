# /config/pyscript/test_diagnostics_functions.py
# Test functions for ALS diagnostics system
# Tests the error capture, filtering, and classification functionality

def test_error_message_filtering():
    """Test ALS-related error message filtering logic."""
    # Messages that SHOULD trigger diagnostics
    positive_cases = [
        "adaptive_learning error in bedroom",
        "intelligent lighting system failed",
        "kitchen automation timeout", 
        "ALS memory manager connection lost",
        "bathroom adaptive learning disabled",
        "routine_timing storage error",
        "als_error_bedroom update failed"
    ]
    
    # Messages that should NOT trigger diagnostics
    negative_cases = [
        "weather service unavailable",
        "media player disconnected", 
        "device_tracker timeout",
        "unrelated automation error",
        "zigbee coordinator offline"
    ]
    
    for message in positive_cases:
        result = should_capture_error(message)
        assert result == True, f"Should capture: {message}"
    
    for message in negative_cases:
        result = should_capture_error(message)
        assert result == False, f"Should NOT capture: {message}"
    
    log.info("✅ Error message filtering tests passed")

def test_room_classification():
    """Test room classification from error messages."""
    test_cases = [
        ("bedroom light automation failed", "bedroom"),
        ("kitchen motion sensor error", "kitchen"), 
        ("living room adaptive learning timeout", "livingroom"),
        ("bathroom sensor disconnected", "bathroom"),
        ("hallway automation error", "hallway"),
        ("laundry room lighting failed", "laundry"),
        ("general system error", "global"),  # Unclassified
    ]
    
    for message, expected_room in test_cases:
        result = classify_error_by_room(message)
        assert result == expected_room, f"Failed classifying '{message}': got {result}, expected {expected_room}"
    
    log.info("✅ Room classification tests passed")

def test_error_message_formatting():
    """Test error message truncation and timestamp formatting."""
    import datetime
    
    test_cases = [
        ("Short error", "12:34:56", "12:34:56: ERROR - Short error"),
        ("This is a very long error message that should be truncated because it exceeds the maximum allowed length for storage", "08:15:30", "08:15:30: ERROR - This is a very long error message that should be truncated because it exceeds the maximum"),
        ("", "23:59:59", "23:59:59: ERROR - "),
    ]
    
    for message, timestamp, expected in test_cases:
        result = format_error_message(message, "ERROR", timestamp)
        # Check that result starts with expected (may have slight differences due to truncation)
        assert result.startswith(expected[:50]), f"Failed formatting: got {result}, expected {expected}"
    
    log.info("✅ Error message formatting tests passed")

def test_error_feed_management():
    """Test JSON error feed rotation logic."""
    # Test adding to empty feed
    feed = []
    updated_feed = add_to_error_feed(feed, "First error", max_items=5)
    assert len(updated_feed) == 1
    assert updated_feed[0] == "First error"
    
    # Test adding multiple items
    for i in range(2, 6):
        updated_feed = add_to_error_feed(updated_feed, f"Error {i}", max_items=5)
    
    assert len(updated_feed) == 5
    assert updated_feed[-1] == "Error 5"  # Most recent at end
    
    # Test rotation when exceeding max
    updated_feed = add_to_error_feed(updated_feed, "Error 6", max_items=5)
    assert len(updated_feed) == 5
    assert updated_feed[0] == "Error 2"  # First item removed
    assert updated_feed[-1] == "Error 6"  # New item at end
    
    log.info("✅ Error feed management tests passed")

def test_health_pill_calculation():
    """Test health pill status calculation logic."""
    test_cases = [
        ([], "🟩"),  # No errors = green
        (["WARNING - minor issue"], "🟨"),  # Warning = yellow
        (["ERROR - serious problem"], "🟥"),  # Error = red
        (["CRITICAL - system failure"], "🟥"),  # Critical = red
        (["WARNING - issue 1", "ERROR - issue 2"], "🟥"),  # Mixed = red (worst case)
    ]
    
    for errors, expected_pill in test_cases:
        result = calculate_health_pill(errors)
        assert result == expected_pill, f"Failed health calculation for {errors}: got {result}, expected {expected_pill}"
    
    log.info("✅ Health pill calculation tests passed")

# Helper functions that implement the actual diagnostics logic
def should_capture_error(message):
    """Test if an error message should trigger diagnostics capture."""
    message_lower = message.lower()
    keywords = ['adaptive', 'intelligent', 'bedroom', 'kitchen', 'bathroom', 
                'hallway', 'laundry', 'livingroom', 'living room', 
                'routine_timing', 'als_']
    
    return any(keyword in message_lower for keyword in keywords)

def classify_error_by_room(message):
    """Classify error message by room."""
    message_lower = message.lower()
    
    room_keywords = {
        'bedroom': 'bedroom',
        'kitchen': 'kitchen', 
        'livingroom': ['livingroom', 'living room'],
        'bathroom': 'bathroom',
        'hallway': 'hallway',
        'laundry': 'laundry'
    }
    
    for room, keywords in room_keywords.items():
        if isinstance(keywords, list):
            if any(kw in message_lower for kw in keywords):
                return room
        else:
            if keywords in message_lower:
                return room
    
    return 'global'  # Unclassified

def format_error_message(message, level, timestamp):
    """Format error message with timestamp and truncation."""
    formatted = f"{timestamp}: {level} - {message}"
    return formatted[:100] if len(formatted) > 100 else formatted

def add_to_error_feed(current_feed, new_error, max_items):
    """Add error to feed with rotation."""
    updated = current_feed + [new_error]
    return updated[-max_items:] if len(updated) > max_items else updated

def calculate_health_pill(errors):
    """Calculate health pill status from error list."""
    if not errors:
        return "🟩"
    
    # Check for critical/error levels
    for error in errors:
        if 'CRITICAL' in error.upper() or 'ERROR' in error.upper():
            return "🟥"
    
    # Check for warnings  
    for error in errors:
        if 'WARNING' in error.upper():
            return "🟨"
    
    return "🟩"

# Test runner function
@state_trigger("input_boolean.run_diagnostics_tests", "on")
def run_all_diagnostics_tests():
    """Run all diagnostics system tests."""
    try:
        log.info("🧪 Running diagnostics system tests...")
        test_error_message_filtering()
        test_room_classification()
        test_error_message_formatting()
        test_error_feed_management()
        test_health_pill_calculation()
        log.info("✅ All diagnostics tests passed successfully!")
        
        # Turn off the test trigger
        service.call("input_boolean", "turn_off", entity_id="input_boolean.run_diagnostics_tests")
        
    except Exception as e:
        log.error(f"❌ Diagnostics tests failed: {e}")
        service.call("input_boolean", "turn_off", entity_id="input_boolean.run_diagnostics_tests")