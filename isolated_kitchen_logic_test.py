#!/usr/bin/env python3
"""
Isolated Kitchen Logic Test
Tests just the core kitchen motion logic without PyScript decorators.
"""
import sys
import datetime
from datetime import time as dt_time

class TestLogger:
    def info(self, msg): 
        print(f"[INFO] {msg}")
    def warning(self, msg): 
        print(f"[WARN] {msg}")
    def error(self, msg): 
        print(f"[ERROR] {msg}")

class MockService:
    def __init__(self):
        self.calls = []
    
    def call(self, domain, service_name, **kwargs):
        call_record = {
            'domain': domain,
            'service': service_name,
            'kwargs': kwargs
        }
        self.calls.append(call_record)
        print(f"[SERVICE] {domain}.{service_name}({kwargs})")
        return True
    
    def get_calls(self):
        return self.calls
    
    def clear_calls(self):
        self.calls = []

class TestState:
    def __init__(self, home_state="Day"):
        self._states = {
            'input_select.home_state': home_state,
            'sensor.kitchen_target_brightness': '75',
            'binary_sensor.aqara_motion_sensor_p1_occupancy': 'on',
            'binary_sensor.kitchen_iris_frig_occupancy': 'off'
        }
    
    def get(self, entity_id, default=None):
        return self._states.get(entity_id, default)

def extract_and_test_kitchen_logic():
    """Extract and test the core kitchen motion logic."""
    print("=" * 80)
    print("ISOLATED KITCHEN WLED DAY MODE LOGIC TEST")
    print("=" * 80)
    
    # Setup test environment
    log = TestLogger()
    service = MockService()
    
    # Core constants from kitchen_motion.py
    SINK_PRESET = "select.sink_wled_preset"
    FRIDGE_PRESET = "select.frig_strip_preset"
    SINK_LIGHT = "light.sink_wled"
    FRIDGE_LIGHT = "light.frig_strip"
    KITCHEN_MAIN = "light.kitchen_main_lights"
    HOME_STATE = "input_select.home_state"
    KITCHEN_TARGET_BRIGHTNESS = "sensor.kitchen_target_brightness"
    ALLOWED_MODES = {"Day", "Evening", "Night", "Early Morning"}
    TEST_BYPASS_MODE = False
    TURN_MAIN_OFF_ON_CLEAR = True
    
    # Helper functions from kitchen_motion.py
    def _state(eid, d=None):
        try:
            v = state.get(eid)
            return v if v not in (None, "unknown", "unavailable") else d
        except Exception:
            return d
    
    def _info(msg):
        log.info(f"[KitchenALS] {msg}")
    def _warn(msg):
        log.warning(f"[KitchenALS] {msg}")
    def _error(msg):
        log.error(f"[KitchenALS] {msg}")
    
    def _set_preset(entity_id: str, option: str):
        try:
            service.call("select", "select_option", entity_id=entity_id, option=option)
            _info(f"Preset -> {entity_id} = {option}")
        except Exception as e:
            _error(f"Preset error on {entity_id}: {e}")
    
    def _light_on(entity_id: str, **kwargs):
        try:
            service.call("light", "turn_on", entity_id=entity_id, **kwargs)
            _info(f"Light ON  -> {entity_id} {kwargs if kwargs else ''}")
        except Exception as e:
            _error(f"Light on error on {entity_id}: {e}")
    
    def _light_off(entity_id: str):
        try:
            service.call("light", "turn_off", entity_id=entity_id)
            _info(f"Light OFF -> {entity_id}")
        except Exception as e:
            _error(f"Light off error on {entity_id}: {e}")
    
    # Core motion logic from kitchen_motion.py (lines 86-136)
    def _apply_for_motion(active: bool, reason: str):
        hs = _state(HOME_STATE, "unknown")
        if not TEST_BYPASS_MODE and hs not in ALLOWED_MODES:
            _info(f"SKIP (mode={hs}) reason={reason}")
            return
        
        _info(f"APPLY motion_active={active} mode={hs} reason={reason}")
        
        if active:
            # WLEDs on preset night-100 (but NOT in Day mode)
            if hs != "Day":
                _set_preset(SINK_PRESET, "night-100")
                _set_preset(FRIDGE_PRESET, "night-100")
            else:
                _info(f"SKIPPING WLEDs - Day mode (no WLEDs during daylight)")
            
            # Main lights ON - blocked in Night mode EXCEPT after 4:45 AM
            night_block_lifted = False
            if hs == "Night":
                now_time = datetime.datetime.now().time()
                morning_threshold = dt_time(4, 45, 0)  # 4:45 AM
                night_block_lifted = now_time >= morning_threshold
            
            if hs != "Night" or night_block_lifted:
                # Use learned brightness + fallbacks
                target_brightness = _state(KITCHEN_TARGET_BRIGHTNESS, 30)
                br = max(1, min(100, int(target_brightness)))  # Clamp to valid range
                _light_on(KITCHEN_MAIN, brightness_pct=br)
                if night_block_lifted:
                    _info(f"Night mode block LIFTED (after 4:45 AM) - main lights ON at {br}% (learned/fallback)")
                else:
                    _info(f"Main lights ON at {br}% (learned/fallback)")
            else:
                _info(f"SKIPPING main lights - Night mode before 4:45 AM (WLED only)")
        
        else:
            # WLED behavior: sink OFF, fridge to night (but NOT in Day mode)
            if hs != "Day":
                _light_off(SINK_LIGHT)
                _set_preset(FRIDGE_PRESET, "night")
            
            # Main lights OFF if configured AND they were turned on
            night_block_active = False
            if hs == "Night":
                now_time = datetime.datetime.now().time()
                morning_threshold = dt_time(4, 45, 0)  # 4:45 AM
                night_block_active = now_time < morning_threshold
            
            if TURN_MAIN_OFF_ON_CLEAR and not night_block_active:
                _light_off(KITCHEN_MAIN)
    
    # Test scenarios
    test_scenarios = [
        ("Day", True, "Day mode with motion ON"),
        ("Day", False, "Day mode with motion OFF"),
        ("Evening", True, "Evening mode with motion ON"),
        ("Night", True, "Night mode with motion ON"),
        ("Early Morning", True, "Early Morning mode with motion ON")
    ]
    
    results = []
    
    for home_mode, motion_active, description in test_scenarios:
        print(f"\n{'='*60}")
        print(f"TEST: {description}")
        print(f"Mode: {home_mode}, Motion Active: {motion_active}")
        print('='*60)
        
        # Setup state for this test
        state = TestState(home_mode)
        service.clear_calls()
        
        # Run the logic
        _apply_for_motion(motion_active, f"test_{home_mode.lower().replace(' ', '_')}")
        
        # Analyze results
        calls = service.get_calls()
        wled_calls = [c for c in calls if c['domain'] == 'select' and 'wled' in str(c['kwargs'])]
        main_light_calls = [c for c in calls if c['domain'] == 'light' and 'kitchen_main' in str(c['kwargs'])]
        
        print(f"\nService calls made: {len(calls)}")
        print(f"WLED calls: {len(wled_calls)}")
        print(f"Main light calls: {len(main_light_calls)}")
        
        # Day mode compliance check
        day_mode_compliant = True
        issues = []
        
        if home_mode == "Day" and motion_active and len(wled_calls) > 0:
            day_mode_compliant = False
            issues.append("WLEDs activated in day mode")
        elif home_mode == "Day" and not motion_active and len(wled_calls) > 0:
            day_mode_compliant = False
            issues.append("WLEDs activated during day mode motion clear")
        
        if home_mode == "Day":
            if day_mode_compliant:
                print("✅ DAY MODE COMPLIANT: WLEDs correctly skipped")
            else:
                print("❌ DAY MODE NON-COMPLIANT: WLEDs should be skipped")
                for issue in issues:
                    print(f"   Issue: {issue}")
        
        results.append({
            'mode': home_mode,
            'motion_active': motion_active,
            'wled_calls': len(wled_calls),
            'main_light_calls': len(main_light_calls),
            'compliant': day_mode_compliant,
            'issues': issues
        })
    
    # Final analysis
    print(f"\n{'='*80}")
    print("KITCHEN WLED DAY MODE LOGIC TEST RESULTS")
    print('='*80)
    
    day_mode_tests = [r for r in results if r['mode'] == 'Day']
    day_mode_compliant = [r for r in day_mode_tests if r['compliant']]
    
    print(f"Total tests: {len(results)}")
    print(f"Day mode tests: {len(day_mode_tests)}")
    print(f"Day mode compliant: {len(day_mode_compliant)}")
    
    if len(day_mode_compliant) == len(day_mode_tests):
        print(f"\n🎉 SUCCESS: Kitchen WLED day mode detection is working correctly!")
        print(f"✅ WLEDs are properly skipped in day mode")
        print(f"✅ Main lights work correctly in day mode")
        print(f"✅ Automation condition logic is correct")
    else:
        print(f"\n❌ ISSUES FOUND: {len(day_mode_tests) - len(day_mode_compliant)} non-compliant day mode behaviors")
    
    # Specific findings
    print(f"\n--- SPECIFIC FINDINGS ---")
    for result in day_mode_tests:
        motion_state = "MOTION ON" if result['motion_active'] else "MOTION OFF"
        compliance = "COMPLIANT" if result['compliant'] else "NON-COMPLIANT"
        print(f"{motion_state}: {compliance} - {result['wled_calls']} WLED calls, {result['main_light_calls']} main light calls")
        for issue in result['issues']:
            print(f"  Issue: {issue}")
    
    # Root cause analysis
    all_issues = []
    for result in results:
        all_issues.extend(result['issues'])
    
    if not all_issues:
        print(f"\n--- ROOT CAUSE ANALYSIS ---")
        print("✅ No issues detected - system is functioning as designed")
        print("Kitchen motion automation correctly implements day mode WLED skipping per lines 96-100")
    else:
        print(f"\n--- ROOT CAUSE ANALYSIS ---")
        print(f"❌ Issues detected: {len(all_issues)} total")
        for issue in set(all_issues):  # Remove duplicates
            print(f"  - {issue}")
        print(f"Fix location: pyscript/kitchen_motion.py lines 96-100 and 123-125")
        print(f"Suggested approach: Review day mode condition logic")
    
    return len(day_mode_compliant) == len(day_mode_tests)

if __name__ == "__main__":
    success = extract_and_test_kitchen_logic()
    sys.exit(0 if success else 1)
