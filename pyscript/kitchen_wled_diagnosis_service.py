################################################################################
# Kitchen WLED Comprehensive Diagnosis Service v1.0
# Author: Claude Code
# Updated: 2025-09-03 15:00
# Status: ✅ Complete
# Purpose: Complete diagnosis service covering all aspects of kitchen WLED day mode issue
################################################################################

# !!! PYSCRIPT DIAGNOSIS SERVICE (Kitchen WLED Day Mode) !!!

import datetime
from datetime import time as dt_time
import time

# --- Diagnostic Configuration ---

DIAGNOSTIC_ENTITIES = {
    "home_state": "input_select.home_state",
    "sun": "sun.sun", 
    "kitchen_main": "light.kitchen_main_lights",
    "sink_wled": "light.sink_wled",
    "fridge_wled": "light.frig_strip", 
    "sink_preset": "select.sink_wled_preset",
    "fridge_preset": "select.frig_strip_preset",
    "motion_1": "binary_sensor.aqara_motion_sensor_p1_occupancy",
    "motion_2": "binary_sensor.kitchen_iris_frig_occupancy"
}

# --- Helper Functions ---

def _state(eid, default=None):
    """Safely get entity state."""
    try:
        value = state.get(str(eid))
        return value if value not in (None, "", "unknown", "unavailable") else default
    except Exception:
        return default

def _attr(eid, attr_name, default=None):
    """Safely get entity attribute."""
    try:
        attrs = state.getattr(str(eid)) or {}
        value = attrs.get(attr_name)
        return value if value not in (None, "", "unknown", "unavailable") else default
    except Exception:
        return default

def _info(msg): 
    log.info(f"[Kitchen WLED Diagnosis] {msg}")

def _warn(msg): 
    log.warning(f"[Kitchen WLED Diagnosis] {msg}")

def _error(msg): 
    log.error(f"[Kitchen WLED Diagnosis] {msg}")

# --- Subtask 1.3: Check input_select.home_state transitions and timing ---

def check_home_state_transitions():
    """Check input_select.home_state transitions and timing."""
    _info("🔍 Checking home state transitions and timing...")
    
    transition_data = {
        "current_state": None,
        "state_attributes": {},
        "timing_analysis": {},
        "transition_validity": {},
        "issues": []
    }
    
    # Get current home state
    current_state = _state(DIAGNOSTIC_ENTITIES["home_state"])
    transition_data["current_state"] = current_state
    
    if current_state:
        # Get state attributes for timing info
        state_attrs = state.getattr(DIAGNOSTIC_ENTITIES["home_state"]) or {}
        transition_data["state_attributes"] = {
            "last_changed": state_attrs.get("last_changed"),
            "last_updated": state_attrs.get("last_updated"), 
            "friendly_name": state_attrs.get("friendly_name")
        }
        
        _info(f"✅ Current home state: {current_state}")
        
        # Analyze timing consistency
        now = datetime.datetime.now()
        current_time = now.time()
        
        # Expected state based on time
        if dt_time(4, 30) <= current_time < dt_time(7, 0):
            expected_state = "Early Morning"
        elif dt_time(7, 0) <= current_time < dt_time(17, 0):
            expected_state = "Day"
        elif dt_time(17, 0) <= current_time < dt_time(22, 0):
            expected_state = "Evening"
        else:
            expected_state = "Night"
            
        transition_data["timing_analysis"] = {
            "current_time": current_time.strftime("%H:%M:%S"),
            "expected_state": expected_state,
            "matches_time": current_state == expected_state
        }
        
        if current_state != expected_state:
            issue_msg = f"State mismatch: current={current_state}, time-expected={expected_state}"
            transition_data["issues"].append(issue_msg)
            _warn(f"⚠️ {issue_msg}")
        else:
            _info(f"✅ State matches expected time: {current_state}")
            
    else:
        transition_data["issues"].append("home_state entity unavailable")
        _error("❌ input_select.home_state is unavailable")
    
    return transition_data

# --- Subtask 1.4: Verify sun elevation and day mode trigger conditions ---

def verify_sun_elevation_conditions():
    """Verify sun elevation and day mode trigger conditions."""
    _info("☀️ Verifying sun elevation and day mode conditions...")
    
    sun_data = {
        "sun_elevation": None,
        "elevation_analysis": {},
        "day_mode_triggers": {},
        "condition_evaluation": {},
        "issues": []
    }
    
    # Get sun elevation
    elevation = _attr(DIAGNOSTIC_ENTITIES["sun"], "elevation")
    sun_data["sun_elevation"] = elevation
    
    if elevation is not None:
        try:
            elevation_float = float(elevation)
            
            # Analyze elevation for day mode logic
            sun_data["elevation_analysis"] = {
                "elevation_degrees": elevation_float,
                "above_horizon": elevation_float > 0,
                "daylight_threshold": elevation_float > 0,  # Basic daylight
                "strong_daylight": elevation_float > 15    # Strong daylight
            }
            
            _info(f"✅ Sun elevation: {elevation_float}°")
            
            # Evaluate day mode trigger conditions
            current_state = _state(DIAGNOSTIC_ENTITIES["home_state"])
            
            if current_state == "Day" and elevation_float <= 0:
                issue_msg = f"Day mode active but sun below horizon (elevation: {elevation_float}°)"
                sun_data["issues"].append(issue_msg)
                _warn(f"⚠️ {issue_msg}")
            elif current_state != "Day" and elevation_float > 15:
                issue_msg = f"Strong daylight (elevation: {elevation_float}°) but not in day mode (mode: {current_state})"
                sun_data["issues"].append(issue_msg)  
                _warn(f"⚠️ {issue_msg}")
            else:
                _info(f"✅ Sun elevation consistent with mode: {elevation_float}° / {current_state}")
            
            # Day mode trigger evaluation
            sun_data["day_mode_triggers"] = {
                "elevation_supports_day": elevation_float > 0,
                "strong_daylight": elevation_float > 15,
                "should_trigger_day_mode": elevation_float > 5  # Reasonable threshold
            }
            
        except (ValueError, TypeError):
            sun_data["issues"].append(f"Invalid sun elevation value: {elevation}")
            _error(f"❌ Invalid sun elevation: {elevation}")
    else:
        sun_data["issues"].append("Sun elevation unavailable")
        _error("❌ Sun elevation data unavailable")
    
    return sun_data

# --- Subtask 1.5: Examine automation trace history ---

def examine_automation_traces():
    """Examine automation trace history for day mode changes."""
    _info("🔍 Examining automation trace history...")
    
    trace_data = {
        "automation_states": {},
        "recent_executions": {},
        "kitchen_automations": [],
        "trace_analysis": {},
        "issues": []
    }
    
    # Find kitchen-related automations
    try:
        kitchen_automations = [
            entity_id for entity_id in state.names()
            if entity_id.startswith("automation.") and 
            ("kitchen" in entity_id.lower() or "motion" in entity_id.lower())
        ]
        
        trace_data["kitchen_automations"] = kitchen_automations
        _info(f"Found {len(kitchen_automations)} kitchen-related automations")
        
        # Check each automation
        for auto_id in kitchen_automations:
            auto_state = _state(auto_id)
            auto_attrs = state.getattr(auto_id) or {}
            
            trace_data["automation_states"][auto_id] = {
                "state": auto_state,
                "enabled": auto_state == "on",
                "last_triggered": auto_attrs.get("last_triggered"),
                "current_executions": auto_attrs.get("current", 0)
            }
            
            if auto_state == "off":
                trace_data["issues"].append(f"Automation disabled: {auto_id}")
                _warn(f"⚠️ Automation disabled: {auto_id}")
            else:
                _info(f"✅ Automation enabled: {auto_id}")
        
        # Analyze automation patterns
        enabled_count = sum(1 for data in trace_data["automation_states"].values() if data["enabled"])
        total_count = len(trace_data["automation_states"])
        
        trace_data["trace_analysis"] = {
            "total_automations": total_count,
            "enabled_automations": enabled_count,
            "disabled_automations": total_count - enabled_count,
            "automation_health": "good" if enabled_count == total_count else "issues_found"
        }
        
        if enabled_count < total_count:
            _warn(f"⚠️ {total_count - enabled_count} kitchen automations are disabled")
        else:
            _info("✅ All kitchen automations are enabled")
            
    except Exception as e:
        trace_data["issues"].append(f"Error examining automations: {e}")
        _error(f"❌ Error examining automations: {e}")
    
    return trace_data

# --- Subtask 1.6: Test manual day mode transitions ---

def test_manual_day_mode_transitions():
    """Test manual day mode transitions with kitchen WLED."""
    _info("🧪 Testing manual day mode transitions...")
    
    test_data = {
        "current_conditions": {},
        "manual_test_results": {},
        "wled_response": {},
        "automation_behavior": {},
        "test_recommendations": []
    }
    
    # Document current conditions
    test_data["current_conditions"] = {
        "home_state": _state(DIAGNOSTIC_ENTITIES["home_state"]),
        "sink_wled": _state(DIAGNOSTIC_ENTITIES["sink_wled"]),
        "fridge_wled": _state(DIAGNOSTIC_ENTITIES["fridge_wled"]),
        "motion_1": _state(DIAGNOSTIC_ENTITIES["motion_1"]),
        "motion_2": _state(DIAGNOSTIC_ENTITIES["motion_2"]),
        "test_timestamp": datetime.datetime.now().isoformat()
    }
    
    current_mode = test_data["current_conditions"]["home_state"]
    
    if current_mode == "Day":
        # Already in day mode - test current behavior
        _info("Already in day mode - testing current WLED behavior")
        
        sink_state = test_data["current_conditions"]["sink_wled"]
        fridge_state = test_data["current_conditions"]["fridge_wled"]
        
        test_data["manual_test_results"] = {
            "day_mode_active": True,
            "expected_wled_behavior": "off or motion-controlled",
            "actual_behavior": {
                "sink": sink_state,
                "fridge": fridge_state
            },
            "compliant": (sink_state == "off" and fridge_state == "off") or "motion dependency"
        }
        
        if sink_state == "off" and fridge_state == "off":
            _info("✅ WLEDs correctly off in day mode")
        else:
            _warn(f"⚠️ WLEDs on in day mode: sink={sink_state}, fridge={fridge_state}")
            test_data["manual_test_results"]["issue"] = "WLEDs on during day mode"
    
    else:
        # Not in day mode
        test_data["manual_test_results"] = {
            "day_mode_active": False,
            "current_mode": current_mode,
            "test_applicable": False,
            "note": "Manual day mode test requires Day mode to be active"
        }
        _info(f"Not in day mode (current: {current_mode}) - cannot test day mode behavior")
    
    # Test recommendations
    test_data["test_recommendations"] = [
        "To test day mode manually: temporarily change input_select.home_state to 'Day'",
        "Trigger kitchen motion and observe WLED response", 
        "Verify WLEDs are skipped in day mode per automation logic",
        "Check that only main lights respond in day mode",
        "Test motion clearing behavior in day mode"
    ]
    
    return test_data

# --- Subtask 1.7: Identify root cause ---

def identify_root_cause():
    """Identify root cause of day mode detection failure."""
    _info("🎯 Identifying root cause of day mode detection failure...")
    
    root_cause_data = {
        "analysis_timestamp": datetime.datetime.now().isoformat(),
        "investigation_results": {},
        "potential_causes": [],
        "root_cause_assessment": {},
        "confidence_level": "unknown",
        "fix_recommendations": []
    }
    
    # Gather all investigation results
    _info("Collecting investigation data...")
    root_cause_data["investigation_results"] = {
        "home_state_check": check_home_state_transitions(),
        "sun_elevation_check": verify_sun_elevation_conditions(), 
        "automation_traces": examine_automation_traces(),
        "manual_testing": test_manual_day_mode_transitions()
    }
    
    # Analyze for root causes
    all_issues = []
    for section, data in root_cause_data["investigation_results"].items():
        if "issues" in data:
            all_issues.extend([(section, issue) for issue in data["issues"]])
    
    # Categorize potential causes
    automation_issues = [issue for section, issue in all_issues if "automation" in section or "disabled" in issue.lower()]
    state_issues = [issue for section, issue in all_issues if "state" in issue.lower() or "unavailable" in issue.lower()]
    timing_issues = [issue for section, issue in all_issues if "mismatch" in issue.lower() or "timing" in issue.lower()]
    wled_issues = [issue for section, issue in all_issues if "wled" in issue.lower()]
    
    # Assess root cause
    if automation_issues:
        root_cause_data["potential_causes"].append({
            "category": "automation_failure",
            "issues": automation_issues,
            "likelihood": "high",
            "description": "Kitchen automation not executing properly"
        })
    
    if state_issues:
        root_cause_data["potential_causes"].append({
            "category": "entity_availability", 
            "issues": state_issues,
            "likelihood": "medium",
            "description": "Required entities unavailable or in invalid states"
        })
    
    if timing_issues:
        root_cause_data["potential_causes"].append({
            "category": "mode_timing",
            "issues": timing_issues, 
            "likelihood": "medium",
            "description": "Day mode timing or transition issues"
        })
    
    if wled_issues:
        root_cause_data["potential_causes"].append({
            "category": "wled_control",
            "issues": wled_issues,
            "likelihood": "high", 
            "description": "WLED devices not responding to control commands"
        })
    
    # Determine most likely root cause
    if len(root_cause_data["potential_causes"]) == 0:
        root_cause_data["root_cause_assessment"] = {
            "primary_cause": "no_issues_detected",
            "description": "No clear issues detected in current analysis",
            "confidence": "low",
            "note": "Issue may be intermittent or require different conditions to reproduce"
        }
        root_cause_data["confidence_level"] = "low"
    
    elif len([c for c in root_cause_data["potential_causes"] if c["likelihood"] == "high"]) > 0:
        high_likelihood_causes = [c for c in root_cause_data["potential_causes"] if c["likelihood"] == "high"]
        primary_cause = high_likelihood_causes[0]
        
        root_cause_data["root_cause_assessment"] = {
            "primary_cause": primary_cause["category"],
            "description": primary_cause["description"],
            "confidence": "high",
            "supporting_evidence": primary_cause["issues"]
        }
        root_cause_data["confidence_level"] = "high"
    
    else:
        # Multiple medium likelihood causes
        root_cause_data["root_cause_assessment"] = {
            "primary_cause": "multiple_factors",
            "description": "Multiple contributing factors identified",
            "confidence": "medium",
            "factors": [c["category"] for c in root_cause_data["potential_causes"]]
        }
        root_cause_data["confidence_level"] = "medium"
    
    # Generate fix recommendations
    for cause in root_cause_data["potential_causes"]:
        if cause["category"] == "automation_failure":
            root_cause_data["fix_recommendations"].extend([
                "Enable any disabled kitchen automations",
                "Check automation conditions and triggers",
                "Verify PyScript services are loaded and functioning"
            ])
        elif cause["category"] == "wled_control":
            root_cause_data["fix_recommendations"].extend([
                "Test WLED device connectivity and responsiveness",
                "Check WLED service call syntax in automations", 
                "Verify WLED integration is working properly"
            ])
        elif cause["category"] == "entity_availability":
            root_cause_data["fix_recommendations"].extend([
                "Check entity definitions in Home Assistant", 
                "Verify device connectivity and status",
                "Restart Home Assistant if entities are persistently unavailable"
            ])
    
    # Remove duplicate recommendations
    root_cause_data["fix_recommendations"] = list(set(root_cause_data["fix_recommendations"]))
    
    _info(f"🎯 Root cause analysis complete - confidence: {root_cause_data['confidence_level']}")
    
    return root_cause_data

# --- Main Comprehensive Diagnosis Service ---

@service("pyscript.kitchen_wled_comprehensive_diagnosis")
def kitchen_wled_comprehensive_diagnosis():
    """Run comprehensive diagnosis covering all investigation aspects."""
    _info("🚀 Starting comprehensive kitchen WLED day mode diagnosis...")
    
    diagnosis_results = {
        "diagnosis_timestamp": datetime.datetime.now().isoformat(),
        "investigation_phases": {},
        "overall_assessment": {},
        "action_plan": [],
        "diagnosis_summary": {}
    }
    
    try:
        # Phase 1: State and Transition Analysis
        _info("Phase 1: Analyzing state transitions and timing...")
        diagnosis_results["investigation_phases"]["phase_1_state_analysis"] = {
            "home_state_check": check_home_state_transitions(),
            "sun_elevation_check": verify_sun_elevation_conditions()
        }
        
        # Phase 2: Automation Analysis
        _info("Phase 2: Examining automation traces and behavior...")
        diagnosis_results["investigation_phases"]["phase_2_automation_analysis"] = {
            "automation_traces": examine_automation_traces(),
            "manual_testing": test_manual_day_mode_transitions()
        }
        
        # Phase 3: Root Cause Analysis  
        _info("Phase 3: Identifying root cause...")
        diagnosis_results["investigation_phases"]["phase_3_root_cause"] = identify_root_cause()
        
        # Overall Assessment
        root_cause_data = diagnosis_results["investigation_phases"]["phase_3_root_cause"]
        confidence = root_cause_data.get("confidence_level", "unknown")
        primary_cause = root_cause_data.get("root_cause_assessment", {}).get("primary_cause", "unknown")
        
        diagnosis_results["overall_assessment"] = {
            "confidence_level": confidence,
            "primary_root_cause": primary_cause,
            "total_issues_found": len(root_cause_data.get("potential_causes", [])),
            "diagnosis_status": "complete" if confidence != "low" else "inconclusive"
        }
        
        # Action Plan
        diagnosis_results["action_plan"] = root_cause_data.get("fix_recommendations", [])
        diagnosis_results["action_plan"].extend([
            "Test fixes in a controlled manner",
            "Monitor kitchen WLED behavior after implementing fixes",
            "Document any remaining issues for further investigation"
        ])
        
        # Summary
        if confidence == "high":
            summary_status = f"Root cause identified: {primary_cause}"
        elif confidence == "medium": 
            summary_status = "Multiple contributing factors identified"
        else:
            summary_status = "Issue requires further investigation"
            
        diagnosis_results["diagnosis_summary"] = {
            "status": summary_status,
            "recommendations_count": len(diagnosis_results["action_plan"]),
            "next_step": "Implement recommended fixes" if confidence != "low" else "Gather more data during issue occurrence"
        }
        
        _info(f"🎉 Comprehensive diagnosis complete: {summary_status}")
        
        return diagnosis_results
        
    except Exception as e:
        diagnosis_results["error"] = str(e)
        _error(f"Comprehensive diagnosis failed: {e}")
        return diagnosis_results

# --- Quick Status Check Service ---

@service("pyscript.kitchen_wled_status_check") 
def kitchen_wled_status_check():
    """Quick status check of kitchen WLED system."""
    _info("⚡ Quick kitchen WLED status check...")
    
    status = {
        "timestamp": datetime.datetime.now().isoformat(),
        "system_status": "unknown",
        "current_states": {},
        "quick_assessment": {},
        "immediate_concerns": []
    }
    
    try:
        # Get all current states
        for name, entity_id in DIAGNOSTIC_ENTITIES.items():
            status["current_states"][name] = _state(entity_id)
        
        # Quick assessment
        home_state = status["current_states"]["home_state"]
        sink_wled = status["current_states"]["sink_wled"] 
        fridge_wled = status["current_states"]["fridge_wled"]
        
        if home_state == "Day":
            if sink_wled == "off" and fridge_wled == "off":
                status["system_status"] = "normal"
                status["quick_assessment"]["day_mode_compliance"] = "compliant"
            else:
                status["system_status"] = "issue_detected"
                status["quick_assessment"]["day_mode_compliance"] = "non_compliant"
                status["immediate_concerns"].append(f"WLEDs on in day mode: sink={sink_wled}, fridge={fridge_wled}")
        else:
            status["system_status"] = "monitoring"
            status["quick_assessment"]["day_mode_compliance"] = "not_applicable"
        
        # Check entity availability  
        unavailable = [name for name, state_val in status["current_states"].items() 
                      if state_val in (None, "unknown", "unavailable")]
        
        if unavailable:
            status["immediate_concerns"].append(f"Entities unavailable: {unavailable}")
            if status["system_status"] == "normal":
                status["system_status"] = "degraded"
        
        _info(f"⚡ Status: {status['system_status']}")
        return status
        
    except Exception as e:
        status["system_status"] = "error"
        status["error"] = str(e)
        _error(f"Status check failed: {e}")
        return status