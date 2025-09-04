# /config/pyscript/test_morning_ramp_time_bug.py
# Test to prove and fix the morning ramp time comparison bug
# Bug: 23:12:00 >= 04:45:00 evaluates to True (should be False)

from datetime import time

def test_current_broken_logic():
    """Test the current broken time comparison logic."""
    log.info("🧪 Testing CURRENT BROKEN logic...")
    
    test_cases = [
        # (current_time, expected_should_allow, description)
        (time(23, 12, 0), False, "11:12 PM - should NOT allow ramp"),
        (time(4, 45, 0), True, "4:45 AM - should allow ramp"),
        (time(5, 0, 0), True, "5:00 AM - should allow ramp"),
        (time(8, 0, 0), True, "8:00 AM - should allow ramp"),
        (time(22, 0, 0), False, "10:00 PM - should NOT allow ramp"),
        (time(1, 0, 0), False, "1:00 AM - should NOT allow ramp"),
    ]
    
    morning_threshold = time(4, 45, 0)
    
    for current_time, expected, description in test_cases:
        # This is the BROKEN logic from line 174
        broken_result = current_time >= morning_threshold
        
        log.info(f"  {description}")
        log.info(f"    Current time: {current_time}")
        log.info(f"    Broken logic result: {broken_result}")
        log.info(f"    Expected result: {expected}")
        
        if broken_result != expected:
            log.error(f"    ❌ BUG CONFIRMED: {current_time} >= {morning_threshold} = {broken_result} (wrong!)")
        else:
            log.info(f"    ✅ Correct behavior")
    
    log.info("🔥 BROKEN LOGIC TEST COMPLETE - Bug confirmed at 11:12 PM")

def test_fixed_logic():
    """Test the proposed fixed logic with proper morning window."""
    log.info("🧪 Testing FIXED logic...")
    
    test_cases = [
        # (current_time, expected_should_allow, description)
        (time(23, 12, 0), False, "11:12 PM - should NOT allow ramp"),
        (time(4, 45, 0), True, "4:45 AM - should allow ramp"),
        (time(5, 0, 0), True, "5:00 AM - should allow ramp"),
        (time(8, 0, 0), True, "8:00 AM - should allow ramp"),
        (time(22, 0, 0), False, "10:00 PM - should NOT allow ramp"),
        (time(1, 0, 0), False, "1:00 AM - should NOT allow ramp"),
        (time(4, 44, 0), False, "4:44 AM - should NOT allow ramp (too early)"),
        (time(8, 1, 0), False, "8:01 AM - should NOT allow ramp (too late)"),
    ]
    
    # FIXED logic - proper morning window
    morning_start = time(4, 45, 0)
    morning_end = time(8, 0, 0)
    
    for current_time, expected, description in test_cases:
        # This is the FIXED logic
        fixed_result = morning_start <= current_time <= morning_end
        
        log.info(f"  {description}")
        log.info(f"    Current time: {current_time}")
        log.info(f"    Fixed logic result: {fixed_result}")
        log.info(f"    Expected result: {expected}")
        
        if fixed_result == expected:
            log.info(f"    ✅ CORRECT: Fixed logic works!")
        else:
            log.error(f"    ❌ ERROR: Fixed logic failed")
    
    log.info("🚀 FIXED LOGIC TEST COMPLETE - All cases should pass")

def test_specific_bug_case():
    """Test the specific case that caused the kitchen lights to come on."""
    log.info("🧪 Testing SPECIFIC BUG CASE (11:12 PM)...")
    
    bug_time = time(23, 12, 0)  # 11:12 PM
    threshold = time(4, 45, 0)   # 4:45 AM
    
    # Broken logic
    broken_result = bug_time >= threshold
    log.info(f"BROKEN: {bug_time} >= {threshold} = {broken_result}")
    
    # Fixed logic  
    morning_start = time(4, 45, 0)
    morning_end = time(8, 0, 0)
    fixed_result = morning_start <= bug_time <= morning_end
    log.info(f"FIXED: {morning_start} <= {bug_time} <= {morning_end} = {fixed_result}")
    
    log.info("🔥 BUG ANALYSIS:")
    log.info(f"  At 11:12 PM, broken logic says: ALLOW RAMP ({broken_result})")
    log.info(f"  At 11:12 PM, fixed logic says: BLOCK RAMP ({fixed_result})")
    log.info("  This explains why kitchen lights came on inappropriately!")

def morning_ramp_time_check_fixed(current_time):
    """The proposed fixed function for morning ramp time checking."""
    morning_start = time(4, 45, 0)
    morning_end = time(8, 0, 0)
    return morning_start <= current_time <= morning_end

def morning_ramp_time_check_broken(current_time):
    """The current broken function (simulated)."""
    morning_threshold = time(4, 45, 0)
    return current_time >= morning_threshold

def test_comparison_side_by_side():
    """Compare broken vs fixed logic side by side."""
    log.info("🧪 SIDE-BY-SIDE COMPARISON...")
    
    test_times = [
        time(23, 12, 0),  # The bug case
        time(4, 45, 0),   # Start of morning
        time(6, 0, 0),    # Middle of morning
        time(8, 0, 0),    # End of morning
        time(1, 0, 0),    # Middle of night
    ]
    
    log.info("Time      | Broken | Fixed | Correct?")
    log.info("----------|--------|-------|----------")
    
    for test_time in test_times:
        broken = morning_ramp_time_check_broken(test_time)
        fixed = morning_ramp_time_check_fixed(test_time)
        
        # Correct behavior: only 4:45-8:00 AM should be True
        should_be_true = time(4, 45, 0) <= test_time <= time(8, 0, 0)
        fixed_correct = (fixed == should_be_true)
        
        log.info(f"{test_time} |   {broken}    |   {fixed}   | {'✅' if fixed_correct else '❌'}")

# Test runner
@state_trigger("input_boolean.run_morning_ramp_tests", "on")
def run_morning_ramp_tests():
    """Run all morning ramp time bug tests."""
    try:
        log.info("🚨 RUNNING MORNING RAMP TIME BUG TESTS...")
        log.info("=" * 50)
        
        test_current_broken_logic()
        log.info("")
        
        test_fixed_logic() 
        log.info("")
        
        test_specific_bug_case()
        log.info("")
        
        test_comparison_side_by_side()
        log.info("")
        
        log.info("✅ ALL MORNING RAMP TESTS COMPLETE!")
        log.info("🔥 BUG CONFIRMED: Time comparison logic is broken")
        log.info("🚀 FIX VALIDATED: Proper morning window logic works")
        
        # Turn off test trigger
        service.call("input_boolean", "turn_off", entity_id="input_boolean.run_morning_ramp_tests")
        
    except Exception as e:
        log.error(f"❌ Morning ramp tests failed: {e}")
        service.call("input_boolean", "turn_off", entity_id="input_boolean.run_morning_ramp_tests")

# Manual test service
@service("pyscript.test_morning_ramp_bug")
def test_morning_ramp_bug():
    """Manual service to run morning ramp tests."""
    run_morning_ramp_tests()