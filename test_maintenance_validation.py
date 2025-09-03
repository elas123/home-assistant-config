#!/usr/bin/env python3
"""
Validation Tests for ALS Diagnostics Automated Maintenance System
This validates the system configuration and structure without importing PyScript code
"""

import os
import yaml
import json
import sys

def validate_maintenance_package():
    """Validate the maintenance package YAML structure"""
    print("Testing Automated Maintenance System Package...")
    
    package_path = "/Users/frank/home-assistant-project/packages/18_automated_maintenance_system.yaml"
    
    try:
        with open(package_path, 'r') as f:
            config = yaml.safe_load(f)
            
        # Test required sections exist
        required_sections = [
            'input_number', 'input_boolean', 'sensor', 'counter',
            'input_datetime', 'pyscript', 'automation', 'script'
        ]
        
        for section in required_sections:
            assert section in config, f"Missing required section: {section}"
            print(f"✓ {section} section found")
            
        # Test maintenance controls
        maintenance_controls = [
            'maintenance_error_retention_days',
            'maintenance_cleanup_interval_hours', 
            'maintenance_max_error_entries'
        ]
        
        for control in maintenance_controls:
            assert control in config['input_number'], f"Missing control: {control}"
            print(f"✓ Control {control} configured")
            
        # Test maintenance switches
        maintenance_switches = [
            'maintenance_auto_cleanup_enabled',
            'maintenance_performance_monitoring',
            'maintenance_debug_mode'
        ]
        
        for switch in maintenance_switches:
            assert switch in config['input_boolean'], f"Missing switch: {switch}"
            print(f"✓ Switch {switch} configured")
            
        # Test sensors
        sensors = config['sensor'][0]['sensors'] if 'sensors' in config['sensor'][0] else {}
        maintenance_sensors = [
            'maintenance_last_cleanup',
            'maintenance_cleanup_status',
            'maintenance_system_health',
            'maintenance_data_size_estimate'
        ]
        
        for sensor in maintenance_sensors:
            assert sensor in sensors, f"Missing sensor: {sensor}"
            print(f"✓ Sensor {sensor} configured")
            
        # Test automations
        automation_ids = [a.get('id', '') for a in config.get('automation', [])]
        required_automations = [
            'maintenance_periodic_health_check',
            'maintenance_periodic_cleanup',
            'maintenance_performance_alert',
            'maintenance_data_buildup_prevention'
        ]
        
        for auto_id in required_automations:
            assert auto_id in automation_ids, f"Missing automation: {auto_id}"
            print(f"✓ Automation {auto_id} configured")
            
        # Test scripts
        script_names = list(config.get('script', {}).keys())
        required_scripts = [
            'maintenance_manual_full_cleanup',
            'maintenance_clear_all_errors',
            'maintenance_generate_diagnostic_report',
            'maintenance_reset_counters'
        ]
        
        for script in required_scripts:
            assert script in script_names, f"Missing script: {script}"
            print(f"✓ Script {script} configured")
            
        print("\n✅ Maintenance package validation passed!")
        return True
        
    except Exception as e:
        print(f"❌ Maintenance package validation failed: {str(e)}")
        return False

def validate_maintenance_pyscript():
    """Validate the maintenance PyScript file structure"""
    print("\nTesting Maintenance PyScript Module...")
    
    pyscript_path = "/Users/frank/home-assistant-project/pyscript/maintenance_system.py"
    
    try:
        with open(pyscript_path, 'r') as f:
            content = f.read()
            
        # Test required functions exist
        required_functions = [
            'maintenance_health_check',
            'maintenance_automated_cleanup',
            'maintenance_emergency_cleanup', 
            'maintenance_full_cleanup',
            'maintenance_clear_all_errors',
            'maintenance_generate_report'
        ]
        
        for func in required_functions:
            assert f"def {func}(" in content, f"Missing function: {func}"
            print(f"✓ Function {func} found")
            
        # Test helper functions exist
        helper_functions = [
            '_get_system_health_data',
            '_validate_system_components',
            '_check_performance_issues',
            '_get_diagnostic_entities',
            '_cleanup_old_entries',
            '_cleanup_excess_entries'
        ]
        
        for helper in helper_functions:
            assert f"def {helper}(" in content, f"Missing helper function: {helper}"
            print(f"✓ Helper function {helper} found")
            
        # Test pyscript decorators
        assert "@pyscript_executor" in content, "Missing @pyscript_executor decorators"
        print("✓ PyScript decorators found")
        
        # Test error handling
        assert "try:" in content and "except Exception" in content, "Missing error handling"
        print("✓ Error handling implemented")
        
        # Test logging
        assert "logger" in content, "Missing logging implementation"
        print("✓ Logging implemented")
        
        print("\n✅ Maintenance PyScript validation passed!")
        return True
        
    except Exception as e:
        print(f"❌ Maintenance PyScript validation failed: {str(e)}")
        return False

def validate_system_integration():
    """Validate system integration points"""
    print("\nTesting System Integration...")
    
    try:
        # Check if all ALS diagnostic packages exist for integration
        packages_dir = "/Users/frank/home-assistant-project/packages"
        required_packages = [
            "01_diagnostic_core_entities.yaml",
            "02_system_validation_automation.yaml", 
            "03_comprehensive_error_tracking.yaml",
            "04_advanced_alert_management.yaml",
            "05_health_monitoring_dashboard.yaml",
            "18_automated_maintenance_system.yaml"
        ]
        
        existing_packages = []
        for package in required_packages:
            package_path = os.path.join(packages_dir, package)
            if os.path.exists(package_path):
                existing_packages.append(package)
                print(f"✓ Found package: {package}")
            else:
                print(f"⚠️  Package not found: {package}")
                
        # Check PyScript files
        pyscript_dir = "/Users/frank/home-assistant-project/pyscript"
        required_pyscripts = [
            "als_diagnostics.py",
            "maintenance_system.py"
        ]
        
        for script in required_pyscripts:
            script_path = os.path.join(pyscript_dir, script)
            if os.path.exists(script_path):
                print(f"✓ Found PyScript: {script}")
            else:
                print(f"⚠️  PyScript not found: {script}")
                
        print(f"\n✅ Found {len(existing_packages)} integration packages")
        return True
        
    except Exception as e:
        print(f"❌ Integration validation failed: {str(e)}")
        return False

def test_maintenance_configuration_values():
    """Test maintenance configuration has sensible defaults"""
    print("\nTesting Maintenance Configuration Values...")
    
    package_path = "/Users/frank/home-assistant-project/packages/18_automated_maintenance_system.yaml"
    
    try:
        with open(package_path, 'r') as f:
            config = yaml.safe_load(f)
            
        # Test input_number defaults
        retention_config = config['input_number']['maintenance_error_retention_days']
        assert retention_config['initial'] == 7, "Retention days should default to 7"
        assert retention_config['min'] >= 1, "Retention min should be at least 1"
        assert retention_config['max'] <= 90, "Retention max should be reasonable"
        print("✓ Error retention configuration validated")
        
        cleanup_config = config['input_number']['maintenance_cleanup_interval_hours']
        assert cleanup_config['initial'] == 24, "Cleanup interval should default to 24 hours"
        assert cleanup_config['min'] >= 1, "Cleanup interval min should be at least 1"
        print("✓ Cleanup interval configuration validated")
        
        max_entries_config = config['input_number']['maintenance_max_error_entries']
        assert max_entries_config['initial'] == 200, "Max entries should default to 200"
        assert max_entries_config['min'] >= 50, "Max entries min should be reasonable"
        print("✓ Max entries configuration validated")
        
        # Test boolean defaults
        auto_cleanup = config['input_boolean']['maintenance_auto_cleanup_enabled']
        assert auto_cleanup['initial'] is True, "Auto cleanup should be enabled by default"
        print("✓ Auto cleanup default validated")
        
        perf_monitoring = config['input_boolean']['maintenance_performance_monitoring']  
        assert perf_monitoring['initial'] is True, "Performance monitoring should be enabled"
        print("✓ Performance monitoring default validated")
        
        debug_mode = config['input_boolean']['maintenance_debug_mode']
        assert debug_mode['initial'] is False, "Debug mode should be disabled by default"
        print("✓ Debug mode default validated")
        
        print("\n✅ Configuration values validation passed!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration values validation failed: {str(e)}")
        return False

def test_automation_triggers():
    """Test automation triggers are properly configured"""
    print("\nTesting Automation Triggers...")
    
    package_path = "/Users/frank/home-assistant-project/packages/18_automated_maintenance_system.yaml"
    
    try:
        with open(package_path, 'r') as f:
            config = yaml.safe_load(f)
            
        automations = config.get('automation', [])
        
        # Test health check automation (15-minute trigger)
        health_check = next((a for a in automations if a.get('id') == 'maintenance_periodic_health_check'), None)
        assert health_check is not None, "Health check automation not found"
        
        trigger = health_check['trigger'][0]
        assert trigger['platform'] == 'time_pattern', "Health check should use time_pattern"
        assert trigger['minutes'] == '/15', "Health check should run every 15 minutes"
        print("✓ Health check trigger validated")
        
        # Test cleanup automation
        cleanup_auto = next((a for a in automations if a.get('id') == 'maintenance_periodic_cleanup'), None)
        assert cleanup_auto is not None, "Cleanup automation not found"
        
        cleanup_trigger = cleanup_auto['trigger'][0]
        assert cleanup_trigger['platform'] == 'time_pattern', "Cleanup should use time_pattern"
        assert cleanup_trigger['hours'] == '/1', "Cleanup should check hourly"
        print("✓ Cleanup trigger validated")
        
        # Test performance alert automation
        perf_alert = next((a for a in automations if a.get('id') == 'maintenance_performance_alert'), None)
        assert perf_alert is not None, "Performance alert automation not found"
        
        perf_trigger = perf_alert['trigger'][0]
        assert perf_trigger['platform'] == 'numeric_state', "Performance alert should use numeric_state"
        assert perf_trigger['entity_id'] == 'sensor.maintenance_system_health', "Should monitor health sensor"
        assert perf_trigger['below'] == 50, "Should trigger below 50% health"
        print("✓ Performance alert trigger validated")
        
        print("\n✅ Automation triggers validation passed!")
        return True
        
    except Exception as e:
        print(f"❌ Automation triggers validation failed: {str(e)}")
        return False

def run_all_tests():
    """Run all validation tests"""
    print("=" * 60)
    print("ALS Diagnostics Automated Maintenance System Validation")
    print("=" * 60)
    
    tests = [
        ("Package Structure", validate_maintenance_package),
        ("PyScript Module", validate_maintenance_pyscript), 
        ("System Integration", validate_system_integration),
        ("Configuration Values", test_maintenance_configuration_values),
        ("Automation Triggers", test_automation_triggers)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'-' * 40}")
        print(f"Running: {test_name}")
        print(f"{'-' * 40}")
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:<8} {test_name}")
        
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All maintenance system validation tests passed!")
        print("The Automated Maintenance System is ready for deployment.")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please review the issues above.")
        
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)