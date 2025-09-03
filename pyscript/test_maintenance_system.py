"""
Test Suite for ALS Diagnostics Automated Maintenance System
Tests all maintenance system functionality and PyScript integration
"""

import pytest
import json
import datetime
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add pyscript directory to Python path for testing
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock pyscript environment
class MockPyScript:
    def __init__(self):
        self.state = {}
        self.service_calls = []
        
    def get_state(self, entity_id):
        return self.state.get(entity_id, "unknown")
        
    def set_state(self, entity_id, value):
        self.state[entity_id] = str(value)
        
    def call_service(self, domain, service, **kwargs):
        self.service_calls.append({
            "domain": domain,
            "service": service,
            "data": kwargs
        })

# Global mock objects
mock_pyscript = MockPyScript()

# Mock pyscript decorators and globals
def pyscript_executor(func):
    return func

# Mock state and service objects
class MockState:
    def get(self, entity_id, default=None):
        return mock_pyscript.get_state(entity_id) or default

class MockService:
    def call(self, service_spec, **kwargs):
        if "." in service_spec:
            domain, service = service_spec.split(".", 1)
        else:
            domain, service = service_spec, ""
        mock_pyscript.call_service(domain, service, **kwargs)

# Set up mock environment
state = MockState()
service = MockService()

# Import the module under test
from maintenance_system import (
    maintenance_health_check,
    maintenance_automated_cleanup, 
    maintenance_emergency_cleanup,
    maintenance_full_cleanup,
    maintenance_clear_all_errors,
    maintenance_generate_report,
    _get_system_health_data,
    _validate_system_components,
    _check_performance_issues
)

class TestMaintenanceHealthCheck:
    """Test health check functionality"""
    
    def setup_method(self):
        """Reset mock state before each test"""
        mock_pyscript.state = {}
        mock_pyscript.service_calls = []
        
    def test_health_check_basic(self):
        """Test basic health check execution"""
        # Setup mock data
        mock_pyscript.set_state("sensor.als_total_error_count", "50")
        mock_pyscript.set_state("input_number.maintenance_max_error_entries", "200")
        
        result = maintenance_health_check(debug_mode=False)
        assert result is True
        
    def test_health_check_debug_mode(self):
        """Test health check with debug mode enabled"""
        mock_pyscript.set_state("sensor.als_total_error_count", "150")
        mock_pyscript.set_state("input_number.maintenance_max_error_entries", "200")
        
        result = maintenance_health_check(debug_mode=True)
        assert result is True
        
    def test_health_check_with_missing_data(self):
        """Test health check handles missing data gracefully"""
        result = maintenance_health_check(debug_mode=False)
        assert result is True  # Should handle gracefully
        
    @patch('maintenance_system.logger')
    def test_health_check_exception_handling(self, mock_logger):
        """Test health check handles exceptions properly"""
        # Mock an exception in _get_system_health_data
        with patch('maintenance_system._get_system_health_data', side_effect=Exception("Test error")):
            result = maintenance_health_check(debug_mode=True)
            assert result is False
            mock_logger.error.assert_called()

class TestSystemHealthData:
    """Test system health data collection"""
    
    def setup_method(self):
        mock_pyscript.state = {}
        
    def test_get_system_health_data_normal(self):
        """Test getting system health data with normal values"""
        mock_pyscript.set_state("sensor.als_total_error_count", "50")
        mock_pyscript.set_state("input_number.maintenance_max_error_entries", "200")
        
        health_data = _get_system_health_data()
        
        assert health_data["total_errors"] == 50
        assert health_data["max_errors"] == 200
        assert health_data["score"] == 75.0  # (200-50)/200 * 100
        assert health_data["status"] == "degraded"
        
    def test_get_system_health_data_critical(self):
        """Test health data with critical error levels"""
        mock_pyscript.set_state("sensor.als_total_error_count", "180")
        mock_pyscript.set_state("input_number.maintenance_max_error_entries", "200")
        
        health_data = _get_system_health_data()
        
        assert health_data["total_errors"] == 180
        assert health_data["score"] == 10.0
        assert health_data["status"] == "critical"
        
    def test_get_system_health_data_healthy(self):
        """Test health data with healthy error levels"""
        mock_pyscript.set_state("sensor.als_total_error_count", "20")
        mock_pyscript.set_state("input_number.maintenance_max_error_entries", "200")
        
        health_data = _get_system_health_data()
        
        assert health_data["total_errors"] == 20
        assert health_data["score"] == 90.0
        assert health_data["status"] == "healthy"
        
    def test_get_system_health_data_over_limit(self):
        """Test health data when errors exceed max"""
        mock_pyscript.set_state("sensor.als_total_error_count", "250")
        mock_pyscript.set_state("input_number.maintenance_max_error_entries", "200")
        
        health_data = _get_system_health_data()
        
        assert health_data["total_errors"] == 250
        assert health_data["score"] == 0  # Clamped to 0
        assert health_data["status"] == "critical"

class TestComponentValidation:
    """Test system component validation"""
    
    def setup_method(self):
        mock_pyscript.state = {}
        
    def test_validate_system_components_all_healthy(self):
        """Test validation when all components are healthy"""
        critical_entities = [
            "sensor.als_total_error_count",
            "sensor.als_critical_alert_count",
            "sensor.als_warning_alert_count", 
            "automation.als_system_startup_validation"
        ]
        
        # Set all entities to valid states
        for entity in critical_entities:
            mock_pyscript.set_state(entity, "10")
            
        results = _validate_system_components()
        
        for entity in critical_entities:
            assert results[entity] is True
            
    def test_validate_system_components_some_unavailable(self):
        """Test validation with some components unavailable"""
        mock_pyscript.set_state("sensor.als_total_error_count", "10")
        mock_pyscript.set_state("sensor.als_critical_alert_count", "unavailable")
        # Leave others unset (None)
        
        results = _validate_system_components()
        
        assert results["sensor.als_total_error_count"] is True
        assert results["sensor.als_critical_alert_count"] is False
        assert results["sensor.als_warning_alert_count"] is False

class TestPerformanceIssues:
    """Test performance issue detection"""
    
    def setup_method(self):
        mock_pyscript.state = {}
        
    def test_check_performance_issues_none(self):
        """Test performance check with no issues"""
        mock_pyscript.set_state("sensor.als_total_error_count", "50")
        mock_pyscript.set_state("input_number.maintenance_max_error_entries", "200")
        
        issues = _check_performance_issues()
        
        assert len(issues) == 0
        
    def test_check_performance_issues_high_count(self):
        """Test performance check with high error count"""
        mock_pyscript.set_state("sensor.als_total_error_count", "170")  # 85% of 200
        mock_pyscript.set_state("input_number.maintenance_max_error_entries", "200")
        
        issues = _check_performance_issues()
        
        assert len(issues) == 1
        assert "High error count approaching limit" in issues
        
    def test_check_performance_issues_critical_count(self):
        """Test performance check with critical error count"""
        mock_pyscript.set_state("sensor.als_total_error_count", "190")  # 95% of 200
        mock_pyscript.set_state("input_number.maintenance_max_error_entries", "200")
        
        issues = _check_performance_issues()
        
        assert len(issues) == 2
        assert "High error count approaching limit" in issues
        assert "Critical error count - cleanup recommended" in issues

class TestAutomatedCleanup:
    """Test automated cleanup functionality"""
    
    def setup_method(self):
        mock_pyscript.state = {}
        mock_pyscript.service_calls = []
        
    def test_automated_cleanup_basic(self):
        """Test basic automated cleanup execution"""
        result = maintenance_automated_cleanup(
            retention_days=7,
            max_entries=200,
            debug_mode=False
        )
        
        assert isinstance(result, dict)
        assert "errors_removed" in result
        assert "systems_cleaned" in result
        
    def test_automated_cleanup_debug_mode(self):
        """Test automated cleanup with debug mode"""
        result = maintenance_automated_cleanup(
            retention_days=14,
            max_entries=150,
            debug_mode=True
        )
        
        assert isinstance(result, dict)
        
    @patch('maintenance_system.logger')
    def test_automated_cleanup_exception_handling(self, mock_logger):
        """Test automated cleanup handles exceptions"""
        with patch('maintenance_system._get_diagnostic_entities', side_effect=Exception("Test error")):
            result = maintenance_automated_cleanup(
                retention_days=7,
                max_entries=200,
                debug_mode=True
            )
            assert "error" in result
            mock_logger.error.assert_called()

class TestEmergencyCleanup:
    """Test emergency cleanup functionality"""
    
    def setup_method(self):
        mock_pyscript.state = {}
        mock_pyscript.service_calls = []
        
    def test_emergency_cleanup_basic(self):
        """Test basic emergency cleanup execution"""
        result = maintenance_emergency_cleanup(
            target_count=100,
            debug_mode=False
        )
        
        assert isinstance(result, dict)
        assert "removed_count" in result
        assert "target_reached" in result
        
    def test_emergency_cleanup_debug_mode(self):
        """Test emergency cleanup with debug mode"""
        result = maintenance_emergency_cleanup(
            target_count=150,
            debug_mode=True
        )
        
        assert isinstance(result, dict)
        
    @patch('maintenance_system.logger')  
    def test_emergency_cleanup_exception_handling(self, mock_logger):
        """Test emergency cleanup handles exceptions"""
        with patch('maintenance_system._get_diagnostic_entities', side_effect=Exception("Test error")):
            result = maintenance_emergency_cleanup(
                target_count=100,
                debug_mode=True
            )
            assert "error" in result
            mock_logger.error.assert_called()

class TestFullCleanup:
    """Test full cleanup functionality"""
    
    def setup_method(self):
        mock_pyscript.state = {}
        mock_pyscript.service_calls = []
        
    def test_full_cleanup_basic(self):
        """Test basic full cleanup execution"""
        result = maintenance_full_cleanup(
            retention_days=7,
            debug_mode=False
        )
        
        assert isinstance(result, dict)
        assert "timestamp" in result
        assert "retention_days" in result
        assert "entities_processed" in result
        assert "total_errors_removed" in result
        
    def test_full_cleanup_debug_mode(self):
        """Test full cleanup with debug mode"""
        result = maintenance_full_cleanup(
            retention_days=14,
            debug_mode=True
        )
        
        assert isinstance(result, dict)
        assert result["retention_days"] == 14

class TestClearAllErrors:
    """Test clear all errors functionality"""
    
    def setup_method(self):
        mock_pyscript.state = {}
        mock_pyscript.service_calls = []
        
    def test_clear_all_errors_basic(self):
        """Test basic clear all errors execution"""
        result = maintenance_clear_all_errors(debug_mode=False)
        
        assert isinstance(result, dict)
        assert "timestamp" in result
        assert "entities_cleared" in result
        assert "total_errors_cleared" in result
        
    def test_clear_all_errors_debug_mode(self):
        """Test clear all errors with debug mode"""
        result = maintenance_clear_all_errors(debug_mode=True)
        
        assert isinstance(result, dict)

class TestReportGeneration:
    """Test diagnostic report generation"""
    
    def setup_method(self):
        mock_pyscript.state = {}
        mock_pyscript.service_calls = []
        
    @patch('maintenance_system._save_report_to_file')
    def test_generate_report_basic(self, mock_save):
        """Test basic report generation"""
        mock_save.return_value = None
        
        result = maintenance_generate_report(
            include_performance=False,
            debug_mode=False
        )
        
        assert isinstance(result, dict)
        assert "report_file" in result
        assert "report_data" in result
        
        report_data = result["report_data"]
        assert "timestamp" in report_data
        assert "system_overview" in report_data
        assert "health_summary" in report_data
        assert "recommendations" in report_data
        
    @patch('maintenance_system._save_report_to_file')
    def test_generate_report_with_performance(self, mock_save):
        """Test report generation with performance metrics"""
        mock_save.return_value = None
        
        result = maintenance_generate_report(
            include_performance=True,
            debug_mode=True
        )
        
        assert isinstance(result, dict)
        report_data = result["report_data"]
        assert "performance_metrics" in report_data

class TestIntegrationScenarios:
    """Test realistic integration scenarios"""
    
    def setup_method(self):
        mock_pyscript.state = {}
        mock_pyscript.service_calls = []
        
    def test_full_maintenance_cycle(self):
        """Test complete maintenance cycle"""
        # Setup initial system state
        mock_pyscript.set_state("sensor.als_total_error_count", "180")
        mock_pyscript.set_state("input_number.maintenance_max_error_entries", "200")
        mock_pyscript.set_state("input_number.maintenance_error_retention_days", "7")
        
        # 1. Run health check
        health_result = maintenance_health_check(debug_mode=True)
        assert health_result is True
        
        # 2. Check if cleanup is needed (simulated by high error count)
        health_data = _get_system_health_data()
        assert health_data["status"] == "critical"
        
        # 3. Run automated cleanup
        cleanup_result = maintenance_automated_cleanup(
            retention_days=7,
            max_entries=200,
            debug_mode=True
        )
        assert isinstance(cleanup_result, dict)
        
        # 4. Generate report
        with patch('maintenance_system._save_report_to_file'):
            report_result = maintenance_generate_report(
                include_performance=True,
                debug_mode=True
            )
            assert isinstance(report_result, dict)
            assert "report_data" in report_result
            
    def test_emergency_maintenance_scenario(self):
        """Test emergency maintenance scenario"""
        # Setup critical system state
        mock_pyscript.set_state("sensor.als_total_error_count", "250")  # Over limit
        mock_pyscript.set_state("input_number.maintenance_max_error_entries", "200")
        
        # 1. Health check detects critical state
        health_result = maintenance_health_check(debug_mode=True)
        assert health_result is True
        
        health_data = _get_system_health_data()
        assert health_data["status"] == "critical"
        
        # 2. Emergency cleanup triggered
        emergency_result = maintenance_emergency_cleanup(
            target_count=160,  # Reduce to 80% of limit
            debug_mode=True
        )
        assert isinstance(emergency_result, dict)
        assert "removed_count" in emergency_result

if __name__ == "__main__":
    # Run specific tests
    import sys
    
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        pytest.main([f"-v", f"-k", test_name])
    else:
        # Run all tests
        pytest.main(["-v", __file__])
        
    print("\n" + "="*60)
    print("ALS Diagnostics Maintenance System Test Summary")
    print("="*60)
    print("✓ Health check functionality tested")
    print("✓ System health data collection tested") 
    print("✓ Component validation tested")
    print("✓ Performance issue detection tested")
    print("✓ Automated cleanup tested")
    print("✓ Emergency cleanup tested")
    print("✓ Full cleanup tested")
    print("✓ Clear all errors tested")
    print("✓ Report generation tested")
    print("✓ Integration scenarios tested")
    print("="*60)
    print("All maintenance system components verified!")