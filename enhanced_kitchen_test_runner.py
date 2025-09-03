#!/usr/bin/env python3
"""
Enhanced Kitchen WLED Test Runner
Runs kitchen WLED day mode detection tests with enhanced mock environment.
"""
import sys
import os
import datetime
from unittest.mock import Mock, patch

class EnhancedMockLogger:
    def info(self, msg): 
        print(f"[INFO] {msg}")
    def warning(self, msg): 
        print(f"[WARN] {msg}")
    def error(self, msg): 
        print(f"[ERROR] {msg}")

class EnhancedMockState:
    def __init__(self):
        # Mock realistic kitchen WLED states
        self._states = {
            'input_select.home_state': 'Day',
            'sun.sun': '15.0',  # Sun elevation
            'light.kitchen_main_lights': 'on',
            'light.sink_wled': 'off',
            'light.frig_strip': 'off',
            'select.sink_wled_preset': 'night-100',
            'select.frig_strip_preset': 'night-100',
            'binary_sensor.aqara_motion_sensor_p1_occupancy': 'off',
            'binary_sensor.kitchen_iris_frig_occupancy': 'off'
        }
        
        self._attributes = {
            'sun.sun': {'elevation': 15.0},
            'input_select.home_state': {
                'last_changed': datetime.datetime.now().isoformat(),
                'friendly_name': 'Home State'
            }
        }
    
    def get(self, entity_id, default=None):
        return self._states.get(entity_id, default)
    
    def set(self, entity_id, value):
        self._states[entity_id] = value
    
    def getattr(self, entity_id):
        return self._attributes.get(entity_id, {})
    
    def exist(self, entity_id):
        return entity_id in self._states
    
    def names(self):
        return list(self._states.keys())

# Enhanced mocks
log = EnhancedMockLogger()
state = EnhancedMockState()

def service_decorator(service_name=None):
    def decorator(func):
        func._pyscript_service = service_name
        return func
    return decorator

service = service_decorator

# Test globals for execution
test_globals = {
    'log': log,
    'state': state,
    'service': service,
    'datetime': datetime,
    '__builtins__': __builtins__
}

def run_kitchen_wled_tests():
    """Run all kitchen WLED tests."""
    print("=" * 80)
    print("KITCHEN WLED DAY MODE DETECTION AND DIAGNOSIS TESTS")
    print("=" * 80)
    
    test_files = [
        'pyscript/test_kitchen_wled_day_mode.py',
        'pyscript/analyze_kitchen_wled_logs.py', 
        'pyscript/kitchen_wled_diagnosis_service.py'
    ]
    
    all_results = []
    
    for test_file in test_files:
        print(f"\n{'='*60}")
        print(f"Testing: {test_file}")
        print('='*60)
        
        try:
            with open(test_file, 'r') as f:
                test_code = f.read()
            
            # Execute the test file
            local_globals = test_globals.copy()
            exec(test_code, local_globals)
            
            # Find service functions (test functions)
            service_functions = []
            for name, obj in local_globals.items():
                if callable(obj) and hasattr(obj, '_pyscript_service'):
                    service_functions.append((name, obj))
            
            print(f"Found {len(service_functions)} service functions to test")
            
            # Execute service functions
            for func_name, func in service_functions:
                try:
                    print(f"\n✅ Testing: {func_name}")
                    result = func()
                    
                    # Analyze results
                    if isinstance(result, dict):
                        if 'issues' in result and result['issues']:
                            print(f"❌ Issues found in {func_name}:")
                            for issue in result['issues']:
                                print(f"   - {issue}")
                            all_results.append((test_file, func_name, 'ISSUES', result))
                        else:
                            print(f"✅ {func_name} completed successfully")
                            all_results.append((test_file, func_name, 'PASS', result))
                    else:
                        print(f"✅ {func_name} executed")
                        all_results.append((test_file, func_name, 'PASS', result))
                        
                except Exception as e:
                    print(f"❌ {func_name} failed: {e}")
                    all_results.append((test_file, func_name, 'FAIL', str(e)))
            
        except Exception as e:
            print(f"❌ Failed to load {test_file}: {e}")
            all_results.append((test_file, 'LOAD_ERROR', 'FAIL', str(e)))
    
    return all_results

def analyze_results(results):
    """Analyze test results and provide detailed output."""
    print(f"\n{'='*80}")
    print("TEST ANALYSIS RESULTS")
    print('='*80)
    
    passing = len([r for r in results if r[2] == 'PASS'])
    issues = len([r for r in results if r[2] == 'ISSUES'])
    failing = len([r for r in results if r[2] == 'FAIL'])
    
    print(f"✅ Passing: {passing} tests")
    print(f"⚠️  With Issues: {issues} tests")  
    print(f"❌ Failing: {failing} tests")
    
    # Day mode state detection analysis
    print(f"\n--- DAY MODE STATE DETECTION ---")
    current_mode = state.get('input_select.home_state')
    sun_elevation = state.getattr('sun.sun').get('elevation', 0)
    sink_wled = state.get('light.sink_wled')
    fridge_wled = state.get('light.frig_strip')
    
    print(f"Current system state: {current_mode}")
    print(f"Sun elevation: {sun_elevation}°")
    print(f"WLED compliance in day mode:")
    print(f"  - Sink WLED: {sink_wled} ({'✅ COMPLIANT' if sink_wled == 'off' else '❌ NON-COMPLIANT'})")
    print(f"  - Fridge WLED: {fridge_wled} ({'✅ COMPLIANT' if fridge_wled == 'off' else '❌ NON-COMPLIANT'})")
    
    # Root cause analysis
    print(f"\n--- ROOT CAUSE ANALYSIS ---")
    if current_mode == "Day" and (sink_wled != "off" or fridge_wled != "off"):
        print("❌ ISSUE DETECTED: WLED lights are on during day mode")
        print("Possible causes:")
        print("  1. Kitchen motion automation not correctly handling day mode")
        print("  2. WLED service calls not executing properly")
        print("  3. Motion sensors triggering outside expected conditions")
        print("  4. Day mode state transitions occurring at wrong times")
    else:
        print("✅ No day mode compliance issues detected with current mock data")
    
    # Recommendations
    print(f"\n--- RECOMMENDATIONS ---")
    if failing > 0:
        print("🔧 IMMEDIATE ACTIONS:")
        for test_file, func_name, status, result in results:
            if status == 'FAIL':
                print(f"  - Fix {func_name} in {test_file}")
                if "unavailable" in str(result):
                    print(f"    Suggested approach: Check entity availability in Home Assistant")
                elif "automation" in str(result):
                    print(f"    Suggested approach: Review automation logic and conditions")
                else:
                    print(f"    Suggested approach: Debug specific error: {result}")
    
    if issues > 0:
        print("⚠️  MONITORING NEEDED:")
        for test_file, func_name, status, result in results:
            if status == 'ISSUES' and isinstance(result, dict):
                for issue in result.get('issues', []):
                    print(f"  - {issue}")
    
    print(f"\nReturning control for fixes.")
    
    return {
        'passing': passing,
        'issues': issues,
        'failing': failing,
        'recommendations': []
    }

if __name__ == "__main__":
    results = run_kitchen_wled_tests()
    analysis = analyze_results(results)
    
    # Exit with appropriate code
    exit_code = 0 if analysis['failing'] == 0 else 1
    sys.exit(exit_code)
