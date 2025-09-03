################################################################################
# VISUAL HEALTH MONITORING TEST SUITE v1.0
# Author: Claude
# Updated: 2025-09-02 15:25
# Status: ✅ Complete Implementation
# Purpose: Test suite for health pill calculation and visual monitoring system
################################################################################

import json
from datetime import datetime, timedelta

# !!! HEALTH PILL CALCULATION TESTS !!!

@service("pyscript.test_room_health_calculation")
def test_room_health_calculation():
    """Test room-specific health pill calculation logic."""
    try:
        log.info("🧪 Testing room health pill calculations...")
        test_results = []
        
        # Test cases for room health calculation
        test_cases = [
            # (error_feed_content, expected_health, description)
            ('[]', '🟩', 'Empty error feed should be healthy'),
            ('["12:00:00: INFO - Normal operation"]', '🟩', 'Info messages should be healthy'),
            ('["12:00:00: WARNING - Minor issue"]', '🟨', 'Warning should be yellow'),
            ('["12:00:00: ERROR - Something failed"]', '🟥', 'Error should be red'),
            ('["12:00:00: CRITICAL - System failure"]', '🟥', 'Critical should be red'),
            ('["11:00:00: WARNING - Issue", "12:00:00: ERROR - Failure"]', '🟥', 'Mixed errors should use worst case'),
        ]
        
        for feed_content, expected_health, description in test_cases:
            # Mock the error feed content
            result_health = _calculate_health_from_feed(feed_content)
            
            if result_health == expected_health:
                test_results.append(f"✅ {description}")
            else:
                test_results.append(f"❌ {description} - Got {result_health}, expected {expected_health}")
        
        # Store test results
        service.call("input_text", "set_value",
                    entity_id="input_text.health_calculation_test_results",
                    value="\n".join(test_results[:10]))
        
        log.info(f"Health calculation tests completed: {len([r for r in test_results if '✅' in r])}/{len(test_results)} passed")
        return test_results
        
    except Exception as e:
        log.error(f"Health calculation test failed: {e}")
        return [f"❌ Test suite failed: {e}"]

@service("pyscript.test_global_health_aggregation")  
def test_global_health_aggregation():
    """Test global health status aggregation from multiple rooms."""
    try:
        log.info("🧪 Testing global health aggregation logic...")
        test_results = []
        
        # Test cases for global health aggregation
        test_cases = [
            # (room_healths, expected_global, description)
            (['🟩', '🟩', '🟩', '🟩'], '🟩', 'All green should be green'),
            (['🟩', '🟨', '🟩', '🟩'], '🟨', 'Any yellow should make global yellow'),
            (['🟩', '🟩', '🟩', '🟥'], '🟥', 'Any red should make global red'),
            (['🟨', '🟥', '🟩', '🟨'], '🟥', 'Mixed with red should be red'),
            (['🟨', '🟨', '🟩', '🟩'], '🟨', 'Multiple yellow should be yellow'),
        ]
        
        for room_healths, expected_global, description in test_cases:
            result_global = _aggregate_room_healths(room_healths)
            
            if result_global == expected_global:
                test_results.append(f"✅ {description}")
            else:
                test_results.append(f"❌ {description} - Got {result_global}, expected {expected_global}")
        
        # Store test results
        service.call("input_text", "set_value",
                    entity_id="input_text.global_health_test_results", 
                    value="\n".join(test_results[:10]))
        
        log.info(f"Global health tests completed: {len([r for r in test_results if '✅' in r])}/{len(test_results)} passed")
        return test_results
        
    except Exception as e:
        log.error(f"Global health test failed: {e}")
        return [f"❌ Test suite failed: {e}"]

@service("pyscript.test_health_attributes_generation")
def test_health_attributes_generation():
    """Test health status attribute generation (error counts, room details, etc.)."""
    try:
        log.info("🧪 Testing health attribute generation...")
        test_results = []
        
        # Mock error data for attribute testing
        mock_room_errors = {
            'kitchen': ['12:00:00: ERROR - Kitchen issue'],
            'bedroom': [],
            'livingroom': ['11:00:00: WARNING - Living room warning'],
        }
        
        # Test error count calculation
        total_errors = _count_total_errors(mock_room_errors)
        if total_errors == 2:
            test_results.append("✅ Total error count calculation correct")
        else:
            test_results.append(f"❌ Total error count: got {total_errors}, expected 2")
        
        # Test affected rooms calculation
        affected_rooms = _get_affected_rooms(mock_room_errors)
        expected_rooms = ['kitchen', 'livingroom']
        if set(affected_rooms) == set(expected_rooms):
            test_results.append("✅ Affected rooms calculation correct")
        else:
            test_results.append(f"❌ Affected rooms: got {affected_rooms}, expected {expected_rooms}")
        
        # Test status text generation
        status_text = _generate_status_text(mock_room_errors)
        if 'kitchen' in status_text and 'livingroom' in status_text:
            test_results.append("✅ Status text generation includes affected rooms")
        else:
            test_results.append(f"❌ Status text missing room details: {status_text}")
        
        # Store test results
        service.call("input_text", "set_value",
                    entity_id="input_text.health_attributes_test_results",
                    value="\n".join(test_results[:10]))
        
        log.info(f"Health attributes tests completed: {len([r for r in test_results if '✅' in r])}/{len(test_results)} passed")
        return test_results
        
    except Exception as e:
        log.error(f"Health attributes test failed: {e}")
        return [f"❌ Test suite failed: {e}"]

# !!! HELPER FUNCTIONS FOR TESTING !!!

def _calculate_health_from_feed(feed_json_string):
    """Helper function to calculate health from error feed JSON string."""
    try:
        if not feed_json_string or feed_json_string == '[]':
            return '🟩'
        
        errors = json.loads(feed_json_string)
        if not errors:
            return '🟩'
        
        # Check recent errors for severity
        for error in reversed(errors[-3:]):  # Check last 3 errors
            error_upper = error.upper()
            if 'CRITICAL' in error_upper or 'ERROR' in error_upper:
                return '🟥'
        
        # Check for warnings
        for error in reversed(errors[-3:]):
            if 'WARNING' in error.upper():
                return '🟨'
        
        return '🟩'
        
    except Exception as e:
        log.error(f"Health calculation helper failed: {e}")
        return '🟥'

def _aggregate_room_healths(room_health_list):
    """Helper function to aggregate room healths into global health."""
    if '🟥' in room_health_list:
        return '🟥'
    elif '🟨' in room_health_list:
        return '🟨'
    else:
        return '🟩'

def _count_total_errors(room_errors_dict):
    """Helper function to count total errors across all rooms."""
    return sum(len(errors) for errors in room_errors_dict.values())

def _get_affected_rooms(room_errors_dict):
    """Helper function to get list of rooms with errors."""
    return [room for room, errors in room_errors_dict.items() if errors]

def _generate_status_text(room_errors_dict):
    """Helper function to generate descriptive status text."""
    affected_rooms = _get_affected_rooms(room_errors_dict)
    total_errors = _count_total_errors(room_errors_dict)
    
    if not affected_rooms:
        return "All systems healthy"
    elif len(affected_rooms) == 1:
        return f"Issues in {affected_rooms[0]} ({total_errors} error{'s' if total_errors > 1 else ''})"
    else:
        room_list = ', '.join(affected_rooms)
        return f"Issues in {room_list} ({total_errors} total errors)"

# !!! COMPREHENSIVE TEST RUNNER !!!

@service("pyscript.run_all_health_monitoring_tests")
def run_all_health_monitoring_tests():
    """Run complete health monitoring test suite."""
    try:
        log.info("🧪 Starting comprehensive health monitoring test suite...")
        
        # Run all test categories
        room_tests = test_room_health_calculation()
        global_tests = test_global_health_aggregation()
        attributes_tests = test_health_attributes_generation()
        
        # Calculate overall results
        all_tests = room_tests + global_tests + attributes_tests
        passed_tests = len([t for t in all_tests if '✅' in t])
        total_tests = len(all_tests)
        
        if passed_tests == total_tests:
            status = f"✅ All {total_tests} health monitoring tests passed"
        else:
            failed_tests = total_tests - passed_tests
            status = f"⚠️ {passed_tests}/{total_tests} tests passed ({failed_tests} failures)"
        
        # Store overall status
        service.call("input_text", "set_value",
                    entity_id="input_text.health_monitoring_test_status",
                    value=status)
        
        log.info(f"Health monitoring test suite completed: {status}")
        return all_tests
        
    except Exception as e:
        log.error(f"Health monitoring test suite failed: {e}")
        service.call("input_text", "set_value",
                    entity_id="input_text.health_monitoring_test_status",
                    value="❌ Test suite failed")
        return [f"❌ Test suite failed: {e}"]

# !!! AUTOMATED TEST SCHEDULING !!!

@time_trigger("cron(0 */4 * * *)")  # Every 4 hours
def periodic_health_monitoring_test():
    """Automated health monitoring system validation."""
    try:
        if state.get('input_boolean.health_monitoring_auto_test') == 'on':
            log.info("🔍 Running scheduled health monitoring tests...")
            results = run_all_health_monitoring_tests()
            
            failed_tests = [r for r in results if '❌' in r]
            if failed_tests:
                log.warning(f"Scheduled health tests found {len(failed_tests)} failures")
            else:
                log.info("✅ Scheduled health monitoring tests passed")
                
    except Exception as e:
        log.error(f"Scheduled health monitoring tests failed: {e}")