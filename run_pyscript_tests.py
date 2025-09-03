#!/usr/bin/env python3
"""
PyScript Test Runner
Executes PyScript test files in a mock Home Assistant environment.
"""
import sys
import os
import importlib.util
from unittest.mock import patch
import traceback

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Import our mock environment
from pyscript_mock_env import *

def load_and_run_pyscript_tests():
    """Load and execute all PyScript test functions."""
    test_results = []
    test_files = [
        'pyscript/test_pyscript_validation.py',
        'pyscript/test_health_monitoring.py', 
        'pyscript/test_timing_functions.py',
        'pyscript/test_diagnostics_functions.py',
        'pyscript/test_kitchen_wled_day_mode.py'
    ]
    
    # Override the service decorator to handle both cases
    def service_decorator_wrapper(service_name_or_func=None):
        if callable(service_name_or_func):
            # Called as @service without parameters
            service_name_or_func._pyscript_service = None
            return service_name_or_func
        else:
            # Called as @service("name")
            def decorator(func):
                func._pyscript_service = service_name_or_func
                return func
            return decorator
    
    # Mock the /config/pyscript directory path
    def mock_listdir(path):
        if path == "/config/pyscript":
            return [f for f in os.listdir("pyscript") if f.endswith('.py')]
        return os.listdir(path)
    
    def mock_open_config_file(path, *args, **kwargs):
        if path.startswith("/config/pyscript/"):
            filename = path.replace("/config/pyscript/", "pyscript/")
            return open(filename, *args, **kwargs)
        return open(path, *args, **kwargs)
    
    # Make globals available for test files
    test_globals = {
        'service': service_decorator_wrapper,
        'state_trigger': state_trigger,
        'time_trigger': time_trigger,
        'log': log,
        'state': state,
        'task': task,
        'service_obj': service_obj,  # Rename to avoid conflict with decorator
        '__builtins__': __builtins__
    }
    
    for test_file in test_files:
        print(f"\n{'='*60}")
        print(f"Running tests from: {test_file}")
        print('='*60)
        
        try:
            # Read and execute the test file
            with open(test_file, 'r') as f:
                test_code = f.read()
            
            # Patch os functions for /config/pyscript path
            with patch('os.listdir', side_effect=mock_listdir), \
                 patch('builtins.open', side_effect=mock_open_config_file):
                
                # Execute the test file in our mock environment  
                exec(test_code, test_globals)
                
                # Find all functions with pyscript decorators
                test_functions = []
                for name, obj in test_globals.items():
                    if callable(obj) and (
                        hasattr(obj, '_pyscript_service') or 
                        hasattr(obj, '_pyscript_state_trigger') or
                        hasattr(obj, '_pyscript_time_trigger')
                    ):
                        test_functions.append((name, obj))
                
                # Run test functions that look like actual tests
                for func_name, func in test_functions:
                    if 'test' in func_name.lower() or func_name.startswith('run_'):
                        try:
                            print(f"\n✅ Executing: {func_name}")
                            result = func()
                            print(f"   Result: {result}")
                            test_results.append((test_file, func_name, 'PASS', result))
                        except Exception as e:
                            print(f"❌ {func_name} failed: {e}")
                            print(f"   Traceback: {traceback.format_exc()}")
                            test_results.append((test_file, func_name, 'FAIL', str(e)))
            
            print(f"\n✅ Completed: {test_file}")
            
        except Exception as e:
            print(f"❌ Failed to load {test_file}: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
            test_results.append((test_file, 'FILE_LOAD', 'FAIL', str(e)))
    
    return test_results

def print_test_summary(results):
    """Print a summary of test results."""
    print(f"\n{'='*80}")
    print("PYSCRIPT TEST SUMMARY")
    print('='*80)
    
    passed = len([r for r in results if r[2] == 'PASS'])
    failed = len([r for r in results if r[2] == 'FAIL'])
    
    print(f"✅ Passing: {passed} tests")
    print(f"❌ Failing: {failed} tests")
    
    if failed > 0:
        print(f"\nFailed Tests:")
        for test_file, func_name, status, result in results:
            if status == 'FAIL':
                print(f"❌ {func_name} ({test_file})")
                print(f"   Error: {result}")
                print(f"   Fix location: {test_file}")
                print(f"   Suggested approach: Check PyScript environment dependencies")
    
    print(f"\nReturning control for fixes.")
    return passed == len(results)

if __name__ == "__main__":
    results = load_and_run_pyscript_tests()
    all_passed = print_test_summary(results)
    sys.exit(0 if all_passed else 1)
