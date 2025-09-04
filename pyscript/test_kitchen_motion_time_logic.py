# /config/pyscript/test_kitchen_motion_time_logic.py
# Test to verify if kitchen_motion.py has the same time comparison bug

from datetime import time as dt_time

def test_current_kitchen_motion_logic():
    """Test the EXACT logic currently in kitchen_motion.py"""
    print("🧪 TESTING CURRENT kitchen_motion.py LOGIC")
    print("=" * 50)
    
    # This is the EXACT logic from kitchen_motion.py lines 105-107
    def kitchen_motion_night_block_logic(current_time):
        morning_threshold = dt_time(4, 45, 0)  # 4:45 AM
        night_block_lifted = current_time >= morning_threshold
        return night_block_lifted
    
    test_cases = [
        (dt_time(23, 12, 0), "11:12 PM - The original bug time"),
        (dt_time(4, 45, 0), "4:45 AM - Should start allowing lights"),
        (dt_time(5, 30, 0), "5:30 AM - Work time"),
        (dt_time(8, 0, 0), "8:00 AM - Late morning"),
        (dt_time(1, 0, 0), "1:00 AM - Deep night"),
        (dt_time(22, 0, 0), "10:00 PM - Evening"),
        (dt_time(10, 0, 0), "10:00 AM - Mid morning"),
    ]
    
    print("Testing kitchen_motion.py logic: night_block_lifted = current_time >= morning_threshold")
    print()
    print("Time     | Description        | Block Lifted? | Expected?")
    print("---------|-------------------|---------------|----------")
    
    problematic_times = []
    
    for test_time, description in test_cases:
        result = kitchen_motion_night_block_logic(test_time)
        
        # What should the result be? Only morning hours should lift the block
        # According to your work schedule, you get up at 4:50 AM for work
        # So reasonable morning window would be 4:45 AM - 8:00 AM
        should_lift = dt_time(4, 45, 0) <= test_time <= dt_time(8, 0, 0)
        
        status = "✅ OK" if result == should_lift else "❌ BUG"
        if result != should_lift:
            problematic_times.append((test_time, description, result, should_lift))
            
        print(f"{test_time} | {description:17} | {str(result):13} | {status}")
    
    print()
    print("🔍 ANALYSIS:")
    if problematic_times:
        print("⚠️  BUGS FOUND in kitchen_motion.py!")
        for time_val, desc, got, expected in problematic_times:
            print(f"  {time_val} ({desc}): got {got}, should be {expected}")
        print()
        print("🔥 ROOT CAUSE: Same >= comparison bug as morning_ramp_system.py")
        print("   The logic treats 23:12:00 >= 04:45:00 as True (wrong!)")
    else:
        print("✅ No bugs found - logic appears correct")
    
    return problematic_times

def test_proposed_kitchen_motion_fix():
    """Test the proposed fix with morning window logic"""
    print()
    print("🧪 TESTING PROPOSED FIX for kitchen_motion.py")
    print("=" * 50)
    
    # Proposed fix: morning window logic
    def fixed_kitchen_motion_logic(current_time):
        morning_start = dt_time(4, 45, 0)  # 4:45 AM
        morning_end = dt_time(8, 0, 0)     # 8:00 AM
        night_block_lifted = morning_start <= current_time <= morning_end
        return night_block_lifted
    
    test_cases = [
        (dt_time(23, 12, 0), "11:12 PM - The original bug time", False),
        (dt_time(4, 45, 0), "4:45 AM - Should start allowing lights", True),
        (dt_time(5, 30, 0), "5:30 AM - Work time", True),
        (dt_time(8, 0, 0), "8:00 AM - End of morning window", True),
        (dt_time(1, 0, 0), "1:00 AM - Deep night", False),
        (dt_time(22, 0, 0), "10:00 PM - Evening", False),
        (dt_time(4, 44, 0), "4:44 AM - Just before window", False),
        (dt_time(8, 1, 0), "8:01 AM - Just after window", False),
    ]
    
    print("Testing FIXED logic: morning_start <= current_time <= morning_end")
    print()
    print("Time     | Description        | Block Lifted? | Expected | Status")
    print("---------|-------------------|---------------|----------|--------")
    
    all_correct = True
    
    for test_time, description, expected in test_cases:
        result = fixed_kitchen_motion_logic(test_time)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        if result != expected:
            all_correct = False
            
        print(f"{test_time} | {description:17} | {str(result):13} | {str(expected):8} | {status}")
    
    print()
    if all_correct:
        print("✅ PROPOSED FIX WORKS CORRECTLY!")
        print("   All test cases pass with morning window logic")
    else:
        print("❌ PROPOSED FIX HAS ISSUES!")
        print("   Some test cases failed")
    
    return all_correct

def compare_morning_ramp_vs_kitchen_motion():
    """Compare the logic patterns between morning_ramp and kitchen_motion"""
    print()
    print("🔍 COMPARING LOGIC PATTERNS")
    print("=" * 30)
    
    print("morning_ramp_system.py (FIXED):")
    print("  morning_start <= current_time <= morning_end")
    print("  Result: Only allows 4:45-8:00 AM")
    print()
    
    print("kitchen_motion.py (CURRENT):")
    print("  current_time >= morning_threshold")
    print("  Result: Allows any time >= 4:45 AM (including 11:12 PM!)")
    print()
    
    # Test the key bug case
    bug_time = dt_time(23, 12, 0)
    threshold = dt_time(4, 45, 0)
    
    # Morning ramp logic (fixed)
    ramp_result = dt_time(4, 45, 0) <= bug_time <= dt_time(8, 0, 0)
    
    # Kitchen motion logic (current)
    kitchen_result = bug_time >= threshold
    
    print(f"At 11:12 PM:")
    print(f"  morning_ramp (fixed): {ramp_result} ✅")
    print(f"  kitchen_motion (current): {kitchen_result} ❌")
    print()
    
    if kitchen_result == ramp_result:
        print("✅ Both systems have consistent logic")
    else:
        print("⚠️  INCONSISTENT LOGIC - kitchen_motion has the old bug!")

# Test runner service
@service("pyscript.test_kitchen_motion_time_logic")
def test_kitchen_motion_time_logic():
    """Test kitchen_motion.py time logic comprehensively"""
    try:
        print("🚨 TESTING kitchen_motion.py TIME LOGIC")
        print("=" * 60)
        
        # Test current logic
        bugs_found = test_current_kitchen_motion_logic()
        
        # Test proposed fix
        fix_works = test_proposed_kitchen_motion_fix()
        
        # Compare with morning_ramp
        compare_morning_ramp_vs_kitchen_motion()
        
        print()
        print("🏁 FINAL VERDICT:")
        if bugs_found:
            print(f"❌ kitchen_motion.py HAS BUGS ({len(bugs_found)} issues found)")
            if fix_works:
                print("✅ Proposed fix works correctly")
                print("🔧 RECOMMENDATION: Apply the morning window fix")
            else:
                print("❌ Proposed fix has issues - needs more work")
        else:
            print("✅ kitchen_motion.py appears to be working correctly")
            
        log.info("Kitchen motion time logic test completed")
        
    except Exception as e:
        log.error(f"Kitchen motion time test failed: {e}")

# Quick test service
@service("pyscript.quick_kitchen_motion_test") 
def quick_kitchen_motion_test():
    """Quick test of the 11:12 PM bug case"""
    bug_time = dt_time(23, 12, 0)
    threshold = dt_time(4, 45, 0)
    
    current_result = bug_time >= threshold
    fixed_result = dt_time(4, 45, 0) <= bug_time <= dt_time(8, 0, 0)
    
    print(f"11:12 PM kitchen motion test:")
    print(f"  Current logic: {current_result} (should be False)")
    print(f"  Fixed logic: {fixed_result} (correct)")
    print(f"  Bug confirmed: {current_result != fixed_result}")
    
    return current_result != fixed_result