#!/usr/bin/env python3
"""
Problematic Kitchen WLED Test Scenarios
Tests various failure conditions to validate diagnostic capabilities.
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

class ProblematicMockState:
    """Mock state with various problem scenarios."""
    
    def __init__(self, scenario="normal"):
        self.scenario = scenario
        self._setup_scenario()
    
    def _setup_scenario(self):
        if self.scenario == "wled_on_in_day_mode":
            # Scenario: WLEDs incorrectly on during day mode
            self._states = {
                'input_select.home_state': 'Day',
                'sun.sun': '25.0',  # High sun elevation
                'light.kitchen_main_lights': 'on',
                'light.sink_wled': 'on',  # Problem: on in day mode
                'light.frig_strip': 'on',  # Problem: on in day mode
                'select.sink_wled_preset': 'night-100',
                'select.frig_strip_preset': 'night-100',
                'binary_sensor.aqara_motion_sensor_p1_occupancy': 'on',
                'binary_sensor.kitchen_iris_frig_occupancy': 'off'
            }
            self._attributes = {
                'sun.sun': {'elevation': 25.0},
                'input_select.home_state': {
                    'last_changed': (datetime.datetime.now() - datetime.timedelta(minutes=5)).isoformat(),
                    'friendly_name': 'Home State'
                }
            }
        elif self.scenario == "mode_mismatch":
            # Scenario: Mode doesn't match time/sun conditions
            self._states = {
                'input_select.home_state': 'Night',  # Problem: Night mode during daytime
                'sun.sun': '30.0',  # High sun elevation
                'light.kitchen_main_lights': 'off',
                'light.sink_wled': 'off',
                'light.frig_strip': 'off',
                'select.sink_wled_preset': 'night-100',
                'select.frig_strip_preset': 'night-100',
                'binary_sensor.aqara_motion_sensor_p1_occupancy': 'off',
                'binary_sensor.kitchen_iris_frig_occupancy': 'off'
            }
            self._attributes = {
                'sun.sun': {'elevation': 30.0},
                'input_select.home_state': {
                    'last_changed': datetime.datetime.now().isoformat(),
                    'friendly_name': 'Home State'
                }
            }
        elif self.scenario == "entities_unavailable":
            # Scenario: Key entities unavailable
            self._states = {
                'input_select.home_state': 'unknown',  # Problem: unavailable
                'sun.sun': 'unavailable',  # Problem: unavailable
                'light.kitchen_main_lights': 'unavailable',
                'light.sink_wled': 'on',
                'light.frig_strip': 'unavailable',  # Problem: unavailable
                'select.sink_wled_preset': 'night-100',
                'select.frig_strip_preset': 'unavailable',
                'binary_sensor.aqara_motion_sensor_p1_occupancy': 'unknown',
                'binary_sensor.kitchen_iris_frig_occupancy': 'off'
            }
            self._attributes = {
                'sun.sun': {},
                'input_select.home_state': {}
            }
        else:
            # Normal scenario
            self._states = {
                'input_select.home_state': 'Day',
                'sun.sun': '15.0',
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

def run_problematic_scenarios():
    """Run tests against various problematic scenarios."""
    scenarios = [
        ("normal", "Normal operation - WLEDs off in day mode"),
        ("wled_on_in_day_mode", "Problem: WLEDs incorrectly on during day mode"), 
        ("mode_mismatch", "Problem: Mode doesn't match sun/time conditions"),
        ("entities_unavailable", "Problem: Key entities unavailable")
    ]
    
    all_results = []
    
    for scenario_name, description in scenarios:
        print(f"\n{'='*80}")
        print(f"TESTING SCENARIO: {scenario_name}")
        print(f"Description: {description}")
        print('='*80)
        
        # Create mock objects for this scenario
        log = EnhancedMockLogger()
        state = ProblematicMockState(scenario_name)
        
        def service_decorator(service_name=None):
            def decorator(func):
                func._pyscript_service = service_name
                return func
            return decorator
        
        # Test globals
        test_globals = {
            'log': log,
            'state': state,
            'service': service_decorator,
            'datetime': datetime,
            '__builtins__': __builtins__
        }
        
        # Run just the comprehensive diagnosis function
        try:
            with open('pyscript/kitchen_wled_diagnosis_service.py', 'r') as f:
                test_code = f.read()
            
            exec(test_code, test_globals)
            
            # Run the comprehensive diagnosis
            if 'kitchen_wled_comprehensive_diagnosis' in test_globals:
                diagnosis_func = test_globals['kitchen_wled_comprehensive_diagnosis']
                result = diagnosis_func()
                
                # Analyze the result
                confidence = result.get('overall_assessment', {}).get('confidence_level', 'unknown')
                primary_cause = result.get('overall_assessment', {}).get('primary_root_cause', 'unknown')
                issues_count = result.get('overall_assessment', {}).get('total_issues_found', 0)
                
                print(f"\n--- DIAGNOSIS RESULTS ---")
                print(f"Confidence Level: {confidence}")
                print(f"Primary Root Cause: {primary_cause}")
                print(f"Issues Found: {issues_count}")
                
                # Show specific issues found
                if 'investigation_phases' in result and 'phase_3_root_cause' in result['investigation_phases']:
                    potential_causes = result['investigation_phases']['phase_3_root_cause'].get('potential_causes', [])
                    if potential_causes:
                        print(f"\nPOTENTIAL CAUSES:")
                        for cause in potential_causes:
                            print(f"  - {cause['category']}: {cause['description']} (likelihood: {cause['likelihood']})")
                
                # Show recommendations
                recommendations = result.get('action_plan', [])
                if recommendations:
                    print(f"\nRECOMMENDATIONS:")
                    for i, rec in enumerate(recommendations, 1):
                        print(f"  {i}. {rec}")
                
                status = "PASS" if scenario_name == "normal" else ("DETECTED" if issues_count > 0 else "MISSED")
                all_results.append((scenario_name, status, issues_count, primary_cause))
                
        except Exception as e:
            print(f"❌ Failed to run scenario {scenario_name}: {e}")
            all_results.append((scenario_name, "ERROR", 0, str(e)))
    
    return all_results

def summarize_diagnostic_capability(results):
    """Summarize the diagnostic system's capability."""
    print(f"\n{'='*80}")
    print("DIAGNOSTIC SYSTEM CAPABILITY ANALYSIS")
    print('='*80)
    
    detected = len([r for r in results if r[1] == "DETECTED"])
    passed = len([r for r in results if r[1] == "PASS"]) 
    missed = len([r for r in results if r[1] == "MISSED"])
    errors = len([r for r in results if r[1] == "ERROR"])
    
    print(f"✅ Normal scenarios handled: {passed}")
    print(f"🔍 Issues detected: {detected}")
    print(f"❌ Issues missed: {missed}")
    print(f"⚠️  Errors: {errors}")
    
    print(f"\n--- DETAILED RESULTS ---")
    for scenario, status, issues, cause in results:
        emoji = {"PASS": "✅", "DETECTED": "🔍", "MISSED": "❌", "ERROR": "⚠️"}[status]
        print(f"{emoji} {scenario}: {status} - {issues} issues - {cause}")
    
    # Overall assessment
    total_problem_scenarios = len([r for r in results if r[0] != "normal"])
    detected_problems = len([r for r in results if r[1] == "DETECTED"])
    
    if total_problem_scenarios > 0:
        detection_rate = (detected_problems / total_problem_scenarios) * 100
        print(f"\n--- DIAGNOSTIC EFFECTIVENESS ---")
        print(f"Problem Detection Rate: {detection_rate:.1f}% ({detected_problems}/{total_problem_scenarios})")
        
        if detection_rate >= 80:
            print("🎉 EXCELLENT: Diagnostic system effectively detects most issues")
        elif detection_rate >= 60:
            print("👍 GOOD: Diagnostic system detects majority of issues")  
        elif detection_rate >= 40:
            print("⚠️  FAIR: Diagnostic system detects some issues but needs improvement")
        else:
            print("❌ POOR: Diagnostic system misses most issues")
    
    return detection_rate if total_problem_scenarios > 0 else 100

if __name__ == "__main__":
    results = run_problematic_scenarios()
    detection_rate = summarize_diagnostic_capability(results)
    
    # Return appropriate exit code
    sys.exit(0 if detection_rate >= 60 else 1)
