#!/usr/bin/env python3
"""
Final Comprehensive Kitchen WLED Day Mode Test
Tests the actual kitchen motion automation logic against various scenarios.
"""
import sys
import os
import datetime
from datetime import time as dt_time
import time
import asyncio

class ComprehensiveTestLogger:
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
            'kwargs': kwargs,
            'timestamp': datetime.datetime.now().isoformat()
        }
        self.calls.append(call_record)
        print(f"[SERVICE CALL] {domain}.{service_name} with {kwargs}")
        return True
    
    def get_calls(self):
        return self.calls
    
    def clear_calls(self):
        self.calls = []

class KitchenTestState:
    def __init__(self, scenario="day_mode_normal"):
        self.scenario = scenario
        self._setup_scenario()
        
    def _setup_scenario(self):
        base_states = {
            'select.sink_wled_preset': 'off',
            'select.frig_strip_preset': 'off', 
            'light.sink_wled': 'off',
            'light.frig_strip': 'off',
            'light.kitchen_main_lights': 'off',
            'sensor.kitchen_target_brightness': '50',
            'binary_sensor.aqara_motion_sensor_p1_occupancy': 'off',
            'binary_sensor.kitchen_iris_frig_occupancy': 'off'
        }
        
        if self.scenario == "day_mode_normal":
            # Day mode with motion trigger
            base_states.update({
                'input_select.home_state': 'Day',
                'binary_sensor.aqara_motion_sensor_p1_occupancy': 'on'
            })
        elif self.scenario == "day_mode_both_motion":
            # Day mode with both motion sensors triggered
            base_states.update({
                'input_select.home_state': 'Day',
                'binary_sensor.aqara_motion_sensor_p1_occupancy': 'on',
                'binary_sensor.kitchen_iris_frig_occupancy': 'on'
            })
        elif self.scenario == "evening_mode_motion":
            # Evening mode for comparison
            base_states.update({
                'input_select.home_state': 'Evening',
                'binary_sensor.aqara_motion_sensor_p1_occupancy': 'on'
            })
        elif self.scenario == "night_mode_motion":
            # Night mode with time restrictions
            base_states.update({
                'input_select.home_state': 'Night',
                'binary_sensor.aqara_motion_sensor_p1_occupancy': 'on'
            })
        elif self.scenario == "day_mode_motion_clear":
            # Day mode with motion clearing
            base_states.update({
                'input_select.home_state': 'Day',
                'binary_sensor.aqara_motion_sensor_p1_occupancy': 'off',
                'binary_sensor.kitchen_iris_frig_occupancy': 'off'
            })
            
        self._states = base_states
    
    def get(self, entity_id, default=None):
        return self._states.get(entity_id, default)
    
    def set(self, entity_id, value):
        self._states[entity_id] = value

def run_kitchen_automation_test(scenario_name, description):
    """Run a specific kitchen automation test scenario."""
    print(f"\n{'='*80}")
    print(f"TESTING SCENARIO: {scenario_name}")
    print(f"Description: {description}")
    print('='*80)
    
    # Setup test environment
    log = ComprehensiveTestLogger()
    state = KitchenTestState(scenario_name)
    service = MockService()
    
    # Load the kitchen automation logic
    test_globals = {
        'log': log,
        'state': state,
        'service': service,
        'datetime': datetime,
        'dt_time': dt_time,
        'time': time,
        'asyncio': asyncio,
        '__builtins__': __builtins__
    }
    
    try:
        with open('pyscript/kitchen_motion.py', 'r') as f:
            automation_code = f.read()
        
        # Execute the automation code
        exec(automation_code, test_globals)
        
        # Test the core motion logic
        print(f"\n--- TESTING MOTION LOGIC ---")
        print(f"Current state: {state.get('input_select.home_state')}")
        print(f"Motion 1: {state.get('binary_sensor.aqara_motion_sensor_p1_occupancy')}")
        print(f"Motion 2: {state.get('binary_sensor.kitchen_iris_frig_occupancy')}")
        
        # Call the _apply_for_motion function directly
        _apply_for_motion = test_globals.get('_apply_for_motion')
        _any_motion_active = test_globals.get('_any_motion_active')
        
        if _apply_for_motion and _any_motion_active:
            motion_active = _any_motion_active()
            print(f"Any motion active: {motion_active}")
            
            service.clear_calls()  # Clear any previous calls
            
            # Test motion trigger
            _apply_for_motion(motion_active, f"test_{scenario_name}")
            
            # Analyze service calls
            calls = service.get_calls()
            print(f"\n--- SERVICE CALLS MADE ({len(calls)} total) ---")
            
            wled_calls = []
            main_light_calls = []
            
            for call in calls:
                print(f"  {call['domain']}.{call['service']} -> {call['kwargs']}")
                
                if call['domain'] == 'select' and 'wled' in str(call['kwargs']):
                    wled_calls.append(call)
                elif call['domain'] == 'light' and 'kitchen_main' in str(call['kwargs']):
                    main_light_calls.append(call)
            
            # Analysis
            print(f"\n--- BEHAVIOR ANALYSIS ---")
            home_state = state.get('input_select.home_state')
            
            if home_state == 'Day':
                print(f"Expected behavior in Day mode:")
                print(f"  - WLED calls: NONE (should be skipped)")
                print(f"  - Main light calls: YES (motion-activated)")
                
                if len(wled_calls) == 0:
                    print(f"✅ CORRECT: No WLED calls in day mode")
                else:
                    print(f"❌ ERROR: Found {len(wled_calls)} WLED calls in day mode (should be 0)")
                    
                if len(main_light_calls) > 0:
                    print(f"✅ CORRECT: Main light activated in day mode")
                else:
                    print(f"⚠️  WARNING: No main light calls (expected in day mode)")
                    
            else:
                print(f"Expected behavior in {home_state} mode:")
                print(f"  - WLED calls: YES (motion-activated)")
                print(f"  - Main light calls: DEPENDS (mode-specific rules)")
                
                if len(wled_calls) > 0:
                    print(f"✅ CORRECT: WLED calls found in {home_state} mode")
                else:
                    print(f"⚠️  Note: No WLED calls in {home_state} mode")
            
            # Day mode compliance check
            day_mode_compliant = True
            compliance_issues = []
            
            if home_state == 'Day' and len(wled_calls) > 0:
                day_mode_compliant = False
                compliance_issues.append(f"WLEDs activated in day mode (found {len(wled_calls)} calls)")
            
            result = {
                'scenario': scenario_name,
                'compliant': day_mode_compliant,
                'issues': compliance_issues,
                'wled_calls': len(wled_calls),
                'main_light_calls': len(main_light_calls),
                'total_service_calls': len(calls)
            }
            
            return result
            
        else:
            return {'scenario': scenario_name, 'error': 'Could not load automation functions'}
            
    except Exception as e:
        return {'scenario': scenario_name, 'error': str(e)}

def run_comprehensive_kitchen_test():
    """Run all kitchen WLED test scenarios."""
    print("=" * 100)
    print("COMPREHENSIVE KITCHEN WLED DAY MODE DETECTION AND DIAGNOSIS SYSTEM TESTS")
    print("=" * 100)
    
    test_scenarios = [
        ("day_mode_normal", "Day mode with single motion sensor triggered"),
        ("day_mode_both_motion", "Day mode with both motion sensors triggered"),
        ("evening_mode_motion", "Evening mode with motion (for comparison)"),
        ("night_mode_motion", "Night mode with motion (for comparison)"),
        ("day_mode_motion_clear", "Day mode with no motion (clear state)")
    ]
    
    results = []
    
    for scenario, description in test_scenarios:
        result = run_kitchen_automation_test(scenario, description)
        results.append(result)
    
    # Final analysis
    print(f"\n{'='*100}")
    print("FINAL TEST ANALYSIS AND DIAGNOSIS")
    print('='*100)
    
    passing_tests = [r for r in results if r.get('compliant', False) and 'error' not in r]
    failing_tests = [r for r in results if not r.get('compliant', True) or 'error' in r]
    
    print(f"✅ Passing: {len(passing_tests)} tests")
    print(f"❌ Failing: {len(failing_tests)} tests")
    
    # Day mode specific analysis
    day_mode_tests = [r for r in results if 'day_mode' in r['scenario']]
    day_mode_compliant = [r for r in day_mode_tests if r.get('compliant', False)]
    
    print(f"\n--- DAY MODE COMPLIANCE ANALYSIS ---")
    print(f"Day mode tests: {len(day_mode_tests)}")
    print(f"Day mode compliant: {len(day_mode_compliant)}")
    
    if len(day_mode_compliant) == len(day_mode_tests):
        print(f"🎉 EXCELLENT: All day mode tests are compliant")
        print(f"✅ Kitchen WLED system correctly skips WLEDs in day mode")
    else:
        print(f"❌ ISSUES DETECTED: {len(day_mode_tests) - len(day_mode_compliant)} non-compliant day mode tests")
        
    # Root cause analysis
    print(f"\n--- ROOT CAUSE ANALYSIS ---")
    for result in failing_tests:
        print(f"❌ Failed test: {result['scenario']}")
        if 'error' in result:
            print(f"   Error: {result['error']}")
            print(f"   Fix location: pyscript/kitchen_motion.py")
            print(f"   Suggested approach: Debug automation loading/execution")
        else:
            for issue in result.get('issues', []):
                print(f"   Issue: {issue}")
                print(f"   Fix location: pyscript/kitchen_motion.py lines 96-100")
                print(f"   Suggested approach: Verify day mode WLED skip logic")
    
    # Recommendations
    print(f"\n--- RECOMMENDATIONS ---")
    if len(failing_tests) == 0:
        print("✅ System is functioning correctly:")
        print("  1. Day mode detection is working properly")
        print("  2. WLED behavior complies with day mode expectations") 
        print("  3. Automation condition logic is correct")
        print("  4. Root cause identification is not needed (no issues)")
        print("  5. Continue monitoring for any intermittent issues")
    else:
        print("🔧 Issues found - implement these fixes:")
        print("  1. Review kitchen_motion.py day mode logic (lines 96-100)")
        print("  2. Test WLED service calls in Home Assistant")
        print("  3. Verify entity states and availability")
        print("  4. Check automation trigger conditions")
        print("  5. Monitor system behavior after fixes")
    
    print(f"\nReturning control for fixes.")
    
    return {
        'total_tests': len(results),
        'passing': len(passing_tests),
        'failing': len(failing_tests),
        'day_mode_compliance_rate': (len(day_mode_compliant) / len(day_mode_tests)) * 100 if day_mode_tests else 0
    }

if __name__ == "__main__":
    summary = run_comprehensive_kitchen_test()
    
    # Exit with appropriate code
    exit_code = 0 if summary['failing'] == 0 else 1
    print(f"\nTest Summary: {summary['passing']}/{summary['total_tests']} passing")
    print(f"Day Mode Compliance: {summary['day_mode_compliance_rate']:.1f}%")
    sys.exit(exit_code)
