################################################################################
# Kitchen WLED Day Mode Detection Tests v1.0
# Author: Claude Code
# Updated: 2025-09-03 14:30
# Status: 🚧 In Progress
# Purpose: Test and diagnose kitchen WLED day mode detection and automation issues
################################################################################

# !!! PYSCRIPT TEST FUNCTIONS (Kitchen WLED Day Mode Detection) !!!

import datetime
from datetime import time as dt_time

# --- Test Data and Expected Values ---

# Critical entities for day mode detection
DAY_MODE_ENTITIES = {
    "home_state": "input_select.home_state",
    "sun_elevation": "sun.sun",
    "kitchen_main": "light.kitchen_main_lights",
    "sink_wled": "light.sink_wled",
    "fridge_wled": "light.frig_strip",
    "sink_preset": "select.sink_wled_preset",
    "fridge_preset": "select.frig_strip_preset"
}

# Expected day mode behaviors
EXPECTED_DAY_MODE_BEHAVIOR = {
    "wled_should_be_off": True,
    "main_lights_brightness_source": "sensor.kitchen_target_brightness",
    "allowed_modes": {"Day", "Evening", "Night", "Early Morning"},
    "day_mode_wled_skip": True  # WLEDs should be skipped in Day mode
}

# --- Helper Functions ---

def _state(eid, default=None):
    """Safely get entity state with fallback."""
    try:
        value = state.get(str(eid))
        return value if value not in (None, "", "unknown", "unavailable") else default
    except Exception:
        return default

def _attr(eid, attr_name, default=None):
    """Safely get entity attribute with fallback."""
    try:
        attrs = state.getattr(str(eid)) or {}
        value = attrs.get(attr_name)
        return value if value not in (None, "", "unknown", "unavailable") else default
    except Exception:
        return default

def _info(msg): 
    log.info(f"[Kitchen WLED Test] {msg}")

def _warn(msg): 
    log.warning(f"[Kitchen WLED Test] {msg}")

def _error(msg): 
    log.error(f"[Kitchen WLED Test] {msg}")

# --- Day Mode Detection Tests ---

def test_day_mode_state_detection():
    """Test current day mode state detection and validation."""
    _info("🔍 Testing day mode state detection...")
    
    test_results = {
        "home_state": None,
        "sun_elevation": None,
        "entity_availability": {},
        "mode_validity": None,
        "issues": []
    }
    
    # Test home state detection
    current_mode = _state(DAY_MODE_ENTITIES["home_state"], "unknown")
    test_results["home_state"] = current_mode
    
    if current_mode == "unknown":
        test_results["issues"].append("❌ input_select.home_state is unavailable")
        _error("Home state entity unavailable")
    elif current_mode not in EXPECTED_DAY_MODE_BEHAVIOR["allowed_modes"]:
        test_results["issues"].append(f"❌ Invalid home state: {current_mode}")
        _error(f"Invalid home state: {current_mode}")
    else:
        _info(f"✅ Home state: {current_mode}")
    
    # Test sun elevation
    sun_elevation = _attr(DAY_MODE_ENTITIES["sun_elevation"], "elevation", "unknown")
    test_results["sun_elevation"] = sun_elevation
    
    try:
        elevation_float = float(sun_elevation)
        _info(f"✅ Sun elevation: {elevation_float}°")
        
        # Determine expected sun bucket for day mode logic
        if elevation_float < 0:
            sun_bucket = "Below_Horizon"
        elif elevation_float < 15:
            sun_bucket = "Low_Sun"
        elif elevation_float < 40:
            sun_bucket = "Mid_Sun"
        else:
            sun_bucket = "High_Sun"
        
        test_results["sun_bucket"] = sun_bucket
        _info(f"✅ Sun bucket: {sun_bucket}")
        
    except (ValueError, TypeError):
        test_results["issues"].append(f"❌ Invalid sun elevation: {sun_elevation}")
        _error(f"Sun elevation not numeric: {sun_elevation}")
    
    # Test entity availability
    for name, entity_id in DAY_MODE_ENTITIES.items():
        entity_state = _state(entity_id)
        test_results["entity_availability"][name] = {
            "entity_id": entity_id,
            "state": entity_state,
            "available": entity_state not in (None, "unknown", "unavailable")
        }
        
        if entity_state in (None, "unknown", "unavailable"):
            test_results["issues"].append(f"❌ Entity unavailable: {entity_id}")
            _error(f"Entity unavailable: {entity_id}")
        else:
            _info(f"✅ Entity available: {entity_id} = {entity_state}")
    
    # Validate mode consistency
    if current_mode == "Day":
        test_results["mode_validity"] = "day_mode_active"
        _info("✅ Day mode is currently active")
        
        # In day mode, WLEDs should be off or skipped
        sink_state = _state(DAY_MODE_ENTITIES["sink_wled"])
        fridge_state = _state(DAY_MODE_ENTITIES["fridge_wled"])
        
        if sink_state == "off" and fridge_state == "off":
            _info("✅ WLEDs are OFF in day mode (expected behavior)")
        else:
            test_results["issues"].append(f"⚠️ WLEDs may be on in day mode: sink={sink_state}, fridge={fridge_state}")
            _warn(f"WLEDs state in day mode: sink={sink_state}, fridge={fridge_state}")
    
    return test_results

def test_day_mode_transitions():
    """Test day mode transition detection and timing."""
    _info("🔍 Testing day mode transition patterns...")
    
    transition_results = {
        "current_time": datetime.datetime.now().isoformat(),
        "current_mode": None,
        "expected_transitions": {},
        "transition_logic": {},
        "timing_analysis": {}
    }
    
    current_mode = _state(DAY_MODE_ENTITIES["home_state"])
    transition_results["current_mode"] = current_mode
    
    # Analyze current time against expected mode transitions
    now = datetime.datetime.now()
    current_time = now.time()
    
    # Expected transition times (approximate - may vary based on sun/season)
    expected_transitions = {
        "Night_to_Early_Morning": dt_time(4, 30, 0),
        "Early_Morning_to_Day": dt_time(7, 0, 0),
        "Day_to_Evening": dt_time(17, 0, 0),  # Varies by season
        "Evening_to_Night": dt_time(22, 0, 0)
    }
    
    transition_results["expected_transitions"] = {
        k: v.strftime("%H:%M:%S") for k, v in expected_transitions.items()
    }
    
    # Determine if current mode matches expected time
    time_based_expected_mode = None
    if dt_time(4, 30, 0) <= current_time < dt_time(7, 0, 0):
        time_based_expected_mode = "Early Morning"
    elif dt_time(7, 0, 0) <= current_time < dt_time(17, 0, 0):
        time_based_expected_mode = "Day"
    elif dt_time(17, 0, 0) <= current_time < dt_time(22, 0, 0):
        time_based_expected_mode = "Evening"
    else:
        time_based_expected_mode = "Night"
    
    transition_results["time_based_expected"] = time_based_expected_mode
    transition_results["mode_matches_time"] = (current_mode == time_based_expected_mode)
    
    if current_mode != time_based_expected_mode:
        _warn(f"Mode mismatch: current={current_mode}, time-expected={time_based_expected_mode}")
        transition_results["timing_analysis"]["mismatch"] = True
    else:
        _info(f"✅ Mode matches time: {current_mode} at {current_time.strftime('%H:%M:%S')}")
        transition_results["timing_analysis"]["mismatch"] = False
    
    # Test sun-based day mode logic
    sun_elevation = _attr(DAY_MODE_ENTITIES["sun_elevation"], "elevation")
    if sun_elevation is not None:
        try:
            elevation_float = float(sun_elevation)
            sun_based_day_mode = elevation_float > 0  # Simplified day detection
            
            transition_results["sun_based_day"] = sun_based_day_mode
            transition_results["sun_mode_match"] = (
                (current_mode == "Day" and sun_based_day_mode) or
                (current_mode != "Day" and not sun_based_day_mode)
            )
            
            if sun_based_day_mode and current_mode != "Day":
                _warn(f"Sun indicates day mode (elevation={elevation_float}°) but mode is {current_mode}")
            elif not sun_based_day_mode and current_mode == "Day":
                _warn(f"Mode is Day but sun below horizon (elevation={elevation_float}°)")
            else:
                _info(f"✅ Sun and mode consistent: elevation={elevation_float}°, mode={current_mode}")
                
        except (ValueError, TypeError):
            transition_results["sun_based_day"] = None
            _error(f"Invalid sun elevation for analysis: {sun_elevation}")
    
    return transition_results

def test_kitchen_wled_day_mode_behavior():
    """Test kitchen WLED behavior specifically in day mode."""
    _info("🔍 Testing kitchen WLED day mode behavior...")
    
    behavior_results = {
        "current_mode": None,
        "wled_states": {},
        "expected_behavior": {},
        "compliance": {},
        "automation_analysis": {}
    }
    
    current_mode = _state(DAY_MODE_ENTITIES["home_state"])
    behavior_results["current_mode"] = current_mode
    
    # Get current WLED states
    wled_entities = {
        "sink_light": DAY_MODE_ENTITIES["sink_wled"],
        "fridge_light": DAY_MODE_ENTITIES["fridge_wled"],
        "sink_preset": DAY_MODE_ENTITIES["sink_preset"],
        "fridge_preset": DAY_MODE_ENTITIES["fridge_preset"]
    }
    
    for name, entity_id in wled_entities.items():
        state_val = _state(entity_id)
        behavior_results["wled_states"][name] = {
            "entity_id": entity_id,
            "state": state_val
        }
        _info(f"WLED state: {name} ({entity_id}) = {state_val}")
    
    # Analyze expected vs actual behavior
    if current_mode == "Day":
        # In day mode, WLEDs should be off or not activated
        expected_sink_state = "off"
        expected_fridge_state = "off"
        
        behavior_results["expected_behavior"] = {
            "sink_should_be": expected_sink_state,
            "fridge_should_be": expected_fridge_state,
            "reason": "Day mode - natural light available, WLEDs not needed"
        }
        
        actual_sink = behavior_results["wled_states"]["sink_light"]["state"]
        actual_fridge = behavior_results["wled_states"]["fridge_light"]["state"]
        
        sink_compliant = (actual_sink == expected_sink_state)
        fridge_compliant = (actual_fridge == expected_fridge_state)
        
        behavior_results["compliance"] = {
            "sink_compliant": sink_compliant,
            "fridge_compliant": fridge_compliant,
            "overall_compliant": sink_compliant and fridge_compliant
        }
        
        if not sink_compliant:
            _error(f"❌ Sink WLED non-compliant in day mode: expected={expected_sink_state}, actual={actual_sink}")
        else:
            _info(f"✅ Sink WLED compliant: {actual_sink}")
            
        if not fridge_compliant:
            _error(f"❌ Fridge WLED non-compliant in day mode: expected={expected_fridge_state}, actual={actual_fridge}")
        else:
            _info(f"✅ Fridge WLED compliant: {actual_fridge}")
    
    else:
        behavior_results["expected_behavior"] = {
            "note": f"Not in day mode (current: {current_mode}), WLED behavior varies by motion and mode"
        }
        behavior_results["compliance"] = {"not_applicable": True}
        _info(f"ℹ️ Not in day mode (current: {current_mode}), skipping day mode compliance check")
    
    return behavior_results

def test_automation_condition_logic():
    """Test the automation condition logic that controls WLED behavior."""
    _info("🔍 Testing automation condition logic...")
    
    condition_results = {
        "kitchen_motion_states": {},
        "automation_conditions": {},
        "condition_evaluation": {},
        "logic_analysis": {}
    }
    
    # Test motion sensor states
    motion_entities = {
        "motion_1": "binary_sensor.aqara_motion_sensor_p1_occupancy",
        "motion_2": "binary_sensor.kitchen_iris_frig_occupancy"
    }
    
    for name, entity_id in motion_entities.items():
        motion_state = _state(entity_id)
        condition_results["kitchen_motion_states"][name] = {
            "entity_id": entity_id,
            "state": motion_state,
            "active": motion_state == "on"
        }
        _info(f"Motion sensor: {name} ({entity_id}) = {motion_state}")
    
    any_motion_active = any(
        data["active"] for data in condition_results["kitchen_motion_states"].values()
    )
    condition_results["any_motion_active"] = any_motion_active
    
    # Test automation conditions from kitchen_motion.py logic
    current_mode = _state(DAY_MODE_ENTITIES["home_state"])
    allowed_modes = {"Day", "Evening", "Night", "Early Morning"}
    
    mode_allowed = current_mode in allowed_modes
    day_mode_active = (current_mode == "Day")
    
    condition_results["automation_conditions"] = {
        "current_mode": current_mode,
        "mode_allowed": mode_allowed,
        "day_mode_active": day_mode_active,
        "should_skip_wled_in_day": day_mode_active  # Key logic from kitchen_motion.py
    }
    
    # Evaluate the specific day mode logic
    if day_mode_active:
        # From kitchen_motion.py line 96-100: WLEDs are skipped in Day mode
        condition_results["condition_evaluation"] = {
            "wled_action_expected": "skip",
            "reason": "Day mode detected - WLEDs should be skipped per automation logic",
            "code_reference": "kitchen_motion.py lines 96-100"
        }
        _info("✅ Day mode logic: WLEDs should be skipped (expected behavior)")
    else:
        condition_results["condition_evaluation"] = {
            "wled_action_expected": "normal_operation",
            "reason": f"Not in day mode ({current_mode}) - normal WLED motion control",
            "motion_dependent": True
        }
        _info(f"ℹ️ Non-day mode ({current_mode}): WLEDs follow normal motion logic")
    
    # Analyze main light behavior
    if any_motion_active and mode_allowed:
        if day_mode_active:
            # Main lights should still work in day mode (only WLEDs are skipped)
            condition_results["main_light_expected"] = "on_with_learned_brightness"
        else:
            condition_results["main_light_expected"] = "on_with_learned_brightness"
    else:
        condition_results["main_light_expected"] = "depends_on_clear_logic"
    
    return condition_results

# --- Integration Test Functions ---

@service("pyscript.test_day_mode_detection_full")
def test_day_mode_detection_full():
    """Run complete day mode detection test suite."""
    _info("🚀 Starting comprehensive day mode detection tests...")
    
    test_suite_results = {
        "test_timestamp": datetime.datetime.now().isoformat(),
        "overall_status": "unknown",
        "test_results": {},
        "issues_found": [],
        "recommendations": []
    }
    
    try:
        # Run all individual tests
        _info("Running test 1/4: Day mode state detection")
        test_suite_results["test_results"]["state_detection"] = test_day_mode_state_detection()
        
        _info("Running test 2/4: Day mode transitions")
        test_suite_results["test_results"]["transitions"] = test_day_mode_transitions()
        
        _info("Running test 3/4: WLED behavior analysis")
        test_suite_results["test_results"]["wled_behavior"] = test_kitchen_wled_day_mode_behavior()
        
        _info("Running test 4/4: Automation condition logic")
        test_suite_results["test_results"]["condition_logic"] = test_automation_condition_logic()
        
        # Collect all issues
        for test_name, test_data in test_suite_results["test_results"].items():
            if "issues" in test_data:
                test_suite_results["issues_found"].extend(test_data["issues"])
        
        # Determine overall status
        total_issues = len(test_suite_results["issues_found"])
        if total_issues == 0:
            test_suite_results["overall_status"] = "healthy"
            _info("✅ All day mode detection tests passed")
        elif total_issues <= 3:
            test_suite_results["overall_status"] = "warning"
            _warn(f"⚠️ {total_issues} issues found in day mode detection")
        else:
            test_suite_results["overall_status"] = "critical"
            _error(f"❌ {total_issues} critical issues found")
        
        # Generate recommendations
        current_mode = _state(DAY_MODE_ENTITIES["home_state"])
        if current_mode == "Day":
            wled_behavior = test_suite_results["test_results"].get("wled_behavior", {})
            if not wled_behavior.get("compliance", {}).get("overall_compliant", True):
                test_suite_results["recommendations"].append(
                    "Check kitchen motion automation - WLEDs should be OFF in day mode"
                )
        
        if any("unavailable" in issue for issue in test_suite_results["issues_found"]):
            test_suite_results["recommendations"].append(
                "Check Home Assistant entity states - some required entities are unavailable"
            )
        
        _info(f"📊 Test suite completed: {test_suite_results['overall_status']} status")
        return test_suite_results
        
    except Exception as e:
        test_suite_results["overall_status"] = "error"
        test_suite_results["error"] = str(e)
        _error(f"Test suite failed: {e}")
        return test_suite_results

# --- Manual Test Services ---

@service("pyscript.kitchen_wled_manual_day_mode_test")
def kitchen_wled_manual_day_mode_test():
    """Manually test day mode transition with kitchen WLED."""
    _info("🧪 Manual day mode test - simulating day mode conditions")
    
    # Get current states
    current_mode = _state(DAY_MODE_ENTITIES["home_state"])
    _info(f"Current mode before test: {current_mode}")
    
    # Test the core logic from kitchen_motion.py
    test_results = {
        "before_test": {
            "mode": current_mode,
            "sink_wled": _state(DAY_MODE_ENTITIES["sink_wled"]),
            "fridge_wled": _state(DAY_MODE_ENTITIES["fridge_wled"])
        }
    }
    
    if current_mode == "Day":
        _info("✅ Already in day mode - testing current behavior")
        
        # Simulate motion trigger in day mode
        _info("Simulating motion trigger logic in day mode...")
        
        # From kitchen_motion.py: In day mode, WLEDs should be skipped
        _info("Expected: WLEDs should be SKIPPED in day mode")
        _info("Expected: Only main lights should respond to motion")
        
        # Check if WLEDs are currently off (expected)
        sink_state = _state(DAY_MODE_ENTITIES["sink_wled"])
        fridge_state = _state(DAY_MODE_ENTITIES["fridge_wled"])
        
        if sink_state == "off" and fridge_state == "off":
            _info("✅ WLEDs are correctly OFF in day mode")
            test_results["wled_compliance"] = "compliant"
        else:
            _error(f"❌ WLEDs should be OFF in day mode: sink={sink_state}, fridge={fridge_state}")
            test_results["wled_compliance"] = "non_compliant"
            test_results["issue"] = f"WLEDs on in day mode: sink={sink_state}, fridge={fridge_state}"
    
    else:
        _warn(f"Not currently in day mode (mode: {current_mode})")
        _info("Cannot perform day mode test - consider manual mode change or wait for day mode")
        test_results["test_applicable"] = False
    
    test_results["test_timestamp"] = datetime.datetime.now().isoformat()
    return test_results

@service("pyscript.kitchen_wled_debug_day_mode_issue")
def kitchen_wled_debug_day_mode_issue():
    """Debug specific day mode issue where WLED didn't turn off."""
    _info("🐞 Debugging kitchen WLED day mode issue...")
    
    debug_results = {
        "debug_timestamp": datetime.datetime.now().isoformat(),
        "current_states": {},
        "automation_analysis": {},
        "potential_causes": [],
        "next_steps": []
    }
    
    # Collect all current states
    for name, entity_id in DAY_MODE_ENTITIES.items():
        debug_results["current_states"][name] = {
            "entity_id": entity_id,
            "state": _state(entity_id),
            "attributes": state.getattr(entity_id) if state.exist(entity_id) else None
        }
    
    current_mode = debug_results["current_states"]["home_state"]["state"]
    
    # Analyze potential failure points
    if current_mode != "Day":
        debug_results["potential_causes"].append(
            f"Not currently in day mode (mode: {current_mode}) - issue may be mode transition related"
        )
    
    # Check WLED states
    sink_state = debug_results["current_states"]["sink_wled"]["state"]
    fridge_state = debug_results["current_states"]["fridge_wled"]["state"]
    
    if current_mode == "Day" and (sink_state != "off" or fridge_state != "off"):
        debug_results["potential_causes"].append(
            "WLED lights are on in day mode - automation logic may not be working"
        )
        debug_results["next_steps"].append("Check kitchen_motion.py automation logic")
        debug_results["next_steps"].append("Verify motion sensor triggers are working")
    
    # Check entity availability
    unavailable_entities = [
        name for name, data in debug_results["current_states"].items()
        if data["state"] in (None, "unknown", "unavailable")
    ]
    
    if unavailable_entities:
        debug_results["potential_causes"].append(
            f"Unavailable entities: {unavailable_entities}"
        )
        debug_results["next_steps"].append("Check entity availability in Home Assistant")
    
    # Automation analysis
    debug_results["automation_analysis"] = {
        "expected_day_mode_behavior": "WLEDs should be skipped (not turned on) in day mode",
        "code_location": "kitchen_motion.py lines 96-100",
        "condition_check": f"if hs != 'Day' (current mode: {current_mode})",
        "motion_dependency": "Logic only applies when motion is detected"
    }
    
    _info(f"🐞 Debug complete - found {len(debug_results['potential_causes'])} potential causes")
    
    return debug_results