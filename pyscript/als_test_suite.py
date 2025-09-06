"""
ALS Comprehensive Test Suite with Hypothesis Property-Based Testing
Validates the three-tier architecture under all possible conditions
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant
from datetime import datetime, time, timedelta
import json
import sqlite3
from typing import Dict, Any, Optional
import tempfile
import os

# Import our ALS modules (these will be the actual implementation)
from central_timing_service import CentralTimingService
from morning_ramp_modern import MorningRampExecutor
from hierarchy_controller import HierarchyController

# Test strategies for generating valid inputs
brightness_strategy = st.integers(min_value=1, max_value=100)
temperature_strategy = st.integers(min_value=1800, max_value=6500)
time_strategy = st.times()
datetime_strategy = st.datetimes(
    min_value=datetime(2024, 1, 1),
    max_value=datetime(2025, 12, 31)
)
room_strategy = st.sampled_from([
    "living_room", "kitchen", "bedroom", "bathroom", "hallway", "laundry"
])
system_type_strategy = st.sampled_from([
    "recorded", "learned", "intelligent", "manual"
])

class ALSTestSuite:
    """Main test suite for ALS system validation"""
    
    def __init__(self):
        self.temp_db = tempfile.mktemp(suffix='.db')
        self.timing_service = CentralTimingService()
        self.ramp_executor = MorningRampExecutor()
        self.hierarchy_controller = HierarchyController(db_path=self.temp_db)
        
    def cleanup(self):
        if os.path.exists(self.temp_db):
            os.remove(self.temp_db)

# Property-Based Tests for Core Functions

@given(
    room=room_strategy,
    current_time=datetime_strategy,
    brightness=brightness_strategy,
    temperature=temperature_strategy
)
@settings(max_examples=500, deadline=5000)  # Run 500 random scenarios
def test_hierarchy_decision_always_valid(room, current_time, brightness, temperature):
    """Test that hierarchy decisions are always valid regardless of input"""
    suite = ALSTestSuite()
    
    try:
        context = {
            "current_time": current_time,
            "weather": {"cloud_coverage": 50, "condition": "clear"},
            "user_present": True
        }
        
        result = suite.hierarchy_controller.get_room_lighting_decision(room, context)
        
        # Properties that MUST always be true:
        assert result is not None, "Result cannot be None"
        assert "actual_system" in result, "Must specify which system was used"
        assert result["actual_system"] in ["recorded", "learned", "intelligent", "manual"], \
            f"Invalid system type: {result['actual_system']}"
        
        # Brightness must always be valid
        assert 1 <= result["brightness"] <= 100, \
            f"Invalid brightness: {result['brightness']}"
        
        # Temperature must be valid if provided
        if result.get("temperature"):
            assert 1800 <= result["temperature"] <= 6500, \
                f"Invalid temperature: {result['temperature']}"
        
        # Confidence must be between 0 and 1
        assert 0.0 <= result["confidence"] <= 1.0, \
            f"Invalid confidence: {result['confidence']}"
        
        # Must have a timestamp
        assert "timestamp" in result, "Must include timestamp"
        
    finally:
        suite.cleanup()

@given(
    workday=st.booleans(),
    motion_time=time_strategy,
    current_date=st.dates()
)
@settings(max_examples=200)
def test_morning_ramp_timing_calculations(workday, motion_time, current_date):
    """Test morning ramp timing calculations under all scenarios"""
    suite = ALSTestSuite()
    
    try:
        # Convert time to datetime for testing
        motion_datetime = datetime.combine(current_date, motion_time)
        
        # Only test reasonable morning hours (4 AM to 10 AM)
        assume(4 <= motion_time.hour <= 10)
        
        result = suite.timing_service.calculate_ramp_schedule(
            motion_datetime=motion_datetime,
            is_workday=workday
        )
        
        # Properties that must hold:
        assert result["ramp_duration"] >= 15, "Minimum 15-minute ramp"
        assert result["ramp_duration"] <= 120, "Maximum 2-hour ramp"
        
        # End time must be after start time
        start_time = datetime.fromisoformat(result["start_time"])
        end_time = datetime.fromisoformat(result["end_time"])
        assert end_time > start_time, "End time must be after start time"
        
        # Ramp should not extend past reasonable day start (11 AM)
        assert end_time.hour <= 11, "Ramp should not go past 11 AM"
        
    finally:
        suite.cleanup()

@given(
    initial_brightness=brightness_strategy,
    target_brightness=brightness_strategy,
    duration_minutes=st.integers(min_value=15, max_value=120),
    current_progress=st.floats(min_value=0.0, max_value=1.0)
)
def test_ramp_interpolation_properties(initial_brightness, target_brightness, duration_minutes, current_progress):
    """Test that ramp interpolation always produces smooth, valid results"""
    suite = ALSTestSuite()
    
    try:
        result = suite.ramp_executor.calculate_ramp_value(
            initial_value=initial_brightness,
            target_value=target_brightness,
            progress=current_progress,
            curve_type="smooth"
        )
        
        # Must produce valid brightness
        assert 1 <= result <= 100, f"Interpolated brightness out of range: {result}"
        
        # At 0% progress, should equal initial value (within 1 unit for rounding)
        if current_progress == 0.0:
            assert abs(result - initial_brightness) <= 1
        
        # At 100% progress, should equal target value (within 1 unit for rounding)  
        if current_progress == 1.0:
            assert abs(result - target_brightness) <= 1
        
        # Result should be between initial and target values
        min_val = min(initial_brightness, target_brightness)
        max_val = max(initial_brightness, target_brightness)
        assert min_val <= result <= max_val, "Result must be between initial and target"
        
    finally:
        suite.cleanup()

# Stateful Testing for Complex Scenarios
class ALSStateMachine(RuleBasedStateMachine):
    """Stateful testing to verify system behavior over time"""
    
    def __init__(self):
        super().__init__()
        self.suite = ALSTestSuite()
        self.system_states = {}
        
    @rule(
        room=room_strategy,
        system_type=system_type_strategy
    )
    def set_room_system(self, room, system_type):
        """Test setting room system preferences"""
        self.suite.hierarchy_controller.set_room_system_preference(room, system_type)
        self.system_states[room] = system_type
        
    @rule(room=room_strategy)
    def get_lighting_decision(self, room):
        """Test getting lighting decisions"""
        result = self.suite.hierarchy_controller.get_room_lighting_decision(room)
        
        # If we set a system preference, it should be respected (or have valid fallback)
        if room in self.system_states:
            preferred = self.system_states[room]
            actual = result["actual_system"]
            
            # Either uses preferred system or falls back with reason
            if actual != preferred:
                assert result.get("fallback_reason"), \
                    f"Used {actual} instead of {preferred} without fallback reason"
    
    @invariant()
    def database_integrity(self):
        """Database should always be in valid state"""
        try:
            with sqlite3.connect(self.suite.temp_db) as conn:
                cursor = conn.cursor()
                
                # Check that all room preferences are valid
                cursor.execute("SELECT room, system_type FROM room_system_preferences")
                for row in cursor.fetchall():
                    room, system_type = row
                    assert system_type in ["recorded", "learned", "intelligent", "manual"], \
                        f"Invalid system type in DB: {system_type}"
                        
        except sqlite3.Error as e:
            pytest.fail(f"Database integrity error: {e}")
    
    def teardown(self):
        self.suite.cleanup()

# Integration Tests
class TestALSIntegration:
    """Test the complete ALS system integration"""
    
    def setup_method(self):
        self.suite = ALSTestSuite()
        
    def teardown_method(self):
        self.suite.cleanup()
    
    @given(
        scenario_data=st.lists(
            st.tuples(
                room_strategy,
                datetime_strategy,
                system_type_strategy
            ),
            min_size=1,
            max_size=20
        )
    )
    def test_multi_room_scenarios(self, scenario_data):
        """Test complex multi-room scenarios"""
        results = []
        
        for room, timestamp, preferred_system in scenario_data:
            # Set room preference
            self.suite.hierarchy_controller.set_room_system_preference(room, preferred_system)
            
            # Get lighting decision
            context = {"current_time": timestamp}
            result = self.suite.hierarchy_controller.get_room_lighting_decision(room, context)
            results.append((room, result))
            
            # Validate result
            assert result["brightness"] is not None
            assert 1 <= result["brightness"] <= 100
        
        # Ensure no conflicts between rooms
        room_systems = {}
        for room, result in results:
            if room in room_systems:
                # Same room should get consistent results for same time
                prev_result = room_systems[room]
                if prev_result["timestamp"] == result["timestamp"]:
                    assert prev_result["brightness"] == result["brightness"]
            room_systems[room] = result

# Performance and Stress Tests
@given(
    num_requests=st.integers(min_value=10, max_value=100),
    rooms=st.lists(room_strategy, min_size=1, max_size=6, unique=True)
)
@settings(max_examples=50, deadline=10000)
def test_system_performance_under_load(num_requests, rooms):
    """Test system performance under concurrent load"""
    suite = ALSTestSuite()
    
    try:
        import time
        start_time = time.time()
        
        # Simulate rapid requests
        for i in range(num_requests):
            room = rooms[i % len(rooms)]
            result = suite.hierarchy_controller.get_room_lighting_decision(room)
            assert result is not None
        
        elapsed = time.time() - start_time
        
        # Performance requirement: < 200ms per request on average
        avg_time_per_request = (elapsed / num_requests) * 1000  # Convert to ms
        assert avg_time_per_request < 200, \
            f"Performance requirement failed: {avg_time_per_request:.2f}ms per request"
        
    finally:
        suite.cleanup()

# Edge Case Tests
@given(
    edge_case=st.sampled_from([
        "midnight_transition",
        "daylight_saving_time",
        "leap_year_feb29",
        "extreme_weather",
        "database_corruption",
        "network_failure"
    ])
)
def test_edge_cases(edge_case):
    """Test system behavior in edge cases"""
    suite = ALSTestSuite()
    
    try:
        if edge_case == "midnight_transition":
            # Test behavior exactly at midnight
            midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            context = {"current_time": midnight}
            result = suite.hierarchy_controller.get_room_lighting_decision("living_room", context)
            assert result["brightness"] is not None
            
        elif edge_case == "extreme_weather":
            # Test with extreme weather conditions
            context = {
                "current_time": datetime.now(),
                "weather": {"cloud_coverage": 100, "condition": "storm"}
            }
            result = suite.hierarchy_controller.get_room_lighting_decision("living_room", context)
            assert result["brightness"] >= 50  # Should boost for dark conditions
            
        # Add more edge cases as needed
        
    finally:
        suite.cleanup()

if __name__ == "__main__":
    print("🧪 Running ALS Comprehensive Test Suite...")
    print("⚡ Testing with Hypothesis property-based testing...")
    
    # Run a quick validation
    suite = ALSTestSuite()
    try:
        result = suite.hierarchy_controller.get_room_lighting_decision("living_room")
        print(f"✅ Basic system check passed: {result['actual_system']} system active")
        print(f"💡 Brightness: {result['brightness']}%, Confidence: {result['confidence']:.2f}")
        
        print("\n🚀 System ready for comprehensive testing!")
        print("Run: pytest als_test_suite.py -v --hypothesis-show-statistics")
        
    finally:
        suite.cleanup()