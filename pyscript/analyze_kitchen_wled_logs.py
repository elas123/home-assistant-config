################################################################################
# Kitchen WLED Log Analysis v1.0
# Author: Claude Code
# Updated: 2025-09-03 14:45
# Status: 🚧 In Progress
# Purpose: Analyze Home Assistant logs for kitchen WLED day mode issues
################################################################################

# !!! PYSCRIPT LOG ANALYSIS FUNCTIONS (Kitchen WLED) !!!

import datetime
import re
from pathlib import Path

# --- Log Analysis Configuration ---

LOG_KEYWORDS = {
    "kitchen_entities": [
        "kitchen_main_lights",
        "sink_wled",
        "frig_strip",
        "aqara_motion_sensor_p1",
        "kitchen_iris_frig"
    ],
    "wled_keywords": [
        "wled",
        "sink_wled",
        "frig_strip",
        "night-100",
        "night",
        "preset"
    ],
    "day_mode_keywords": [
        "home_state",
        "Day",
        "day mode",
        "input_select"
    ],
    "automation_keywords": [
        "kitchen_motion",
        "automation",
        "trigger",
        "condition",
        "action"
    ]
}

ERROR_PATTERNS = {
    "entity_unavailable": r"Entity .+ is unavailable",
    "service_call_failed": r"Service call failed",
    "automation_error": r"Error executing automation",
    "wled_error": r"WLED.*error",
    "timeout": r"timeout|timed out",
    "connection_error": r"connection.*error|failed to connect"
}

# --- Helper Functions ---

def _info(msg): 
    log.info(f"[Kitchen Log Analysis] {msg}")

def _warn(msg): 
    log.warning(f"[Kitchen Log Analysis] {msg}")

def _error(msg): 
    log.error(f"[Kitchen Log Analysis] {msg}")

def get_recent_log_entries(hours_back=24):
    """Get recent Home Assistant log entries."""
    _info(f"Searching for log entries from last {hours_back} hours...")
    
    # In Home Assistant, logs are typically accessible through the logger integration
    # We'll use the persistent_notification to display findings since direct log file access
    # may not be available in PyScript environment
    
    log_analysis = {
        "search_period": f"{hours_back} hours",
        "timestamp": datetime.datetime.now().isoformat(),
        "method": "logger_integration_search",
        "findings": [],
        "recommendations": []
    }
    
    # Note: Direct log file reading may not be possible in PyScript
    # This function provides a framework for log analysis that could be enhanced
    # with actual log parsing if file access is available
    
    _info("Note: Direct log file access may be limited in PyScript environment")
    log_analysis["recommendations"].append(
        "Check Home Assistant logs manually in Developer Tools > Logs"
    )
    log_analysis["recommendations"].append(
        "Look for kitchen motion automation entries around the time of the issue"
    )
    
    return log_analysis

def analyze_automation_traces():
    """Analyze automation trace history for kitchen WLED issues."""
    _info("🔍 Analyzing automation traces...")
    
    trace_analysis = {
        "timestamp": datetime.datetime.now().isoformat(),
        "automation_checks": {},
        "trace_findings": [],
        "next_steps": []
    }
    
    # Check if kitchen motion automation exists and is enabled
    kitchen_automation_id = "kitchen_pyscript_morning_ramp_trigger"  # From YAML file
    
    try:
        # Check automation state
        automation_entity = f"automation.{kitchen_automation_id}"
        automation_state = state.get(automation_entity)
        
        trace_analysis["automation_checks"]["morning_ramp_automation"] = {
            "entity_id": automation_entity,
            "state": automation_state,
            "enabled": automation_state == "on"
        }
        
        if automation_state == "on":
            _info(f"✅ Kitchen morning ramp automation is enabled")
        elif automation_state == "off":
            _warn(f"⚠️ Kitchen morning ramp automation is disabled")
            trace_analysis["trace_findings"].append("Morning ramp automation is disabled")
        else:
            _error(f"❌ Kitchen morning ramp automation not found or unavailable")
            trace_analysis["trace_findings"].append("Morning ramp automation entity not available")
    
    except Exception as e:
        _error(f"Error checking automation state: {e}")
        trace_analysis["automation_checks"]["error"] = str(e)
    
    # Check for other kitchen-related automations
    try:
        # Look for any automation entities that might affect kitchen
        automation_entities = [
            entity_id for entity_id in state.names()
            if entity_id.startswith("automation.") and "kitchen" in entity_id.lower()
        ]
        
        trace_analysis["automation_checks"]["kitchen_automations_found"] = automation_entities
        
        for auto_entity in automation_entities:
            auto_state = state.get(auto_entity)
            trace_analysis["automation_checks"][auto_entity] = {
                "state": auto_state,
                "enabled": auto_state == "on"
            }
            _info(f"Found kitchen automation: {auto_entity} = {auto_state}")
    
    except Exception as e:
        _error(f"Error scanning for kitchen automations: {e}")
    
    # Recommendations for manual trace analysis
    trace_analysis["next_steps"] = [
        "Go to Developer Tools > Traces in Home Assistant UI",
        "Look for kitchen motion automation executions",
        "Check trace details for failed conditions or actions",
        "Look for WLED service call failures",
        "Check for mode transition timing issues"
    ]
    
    return trace_analysis

def analyze_state_history():
    """Analyze state history for key entities during the issue timeframe."""
    _info("📊 Analyzing entity state history...")
    
    history_analysis = {
        "timestamp": datetime.datetime.now().isoformat(),
        "entity_states": {},
        "state_transitions": [],
        "anomalies": [],
        "patterns": []
    }
    
    # Key entities to check
    key_entities = {
        "home_state": "input_select.home_state",
        "sink_wled": "light.sink_wled",
        "fridge_wled": "light.frig_strip",
        "kitchen_main": "light.kitchen_main_lights",
        "motion_1": "binary_sensor.aqara_motion_sensor_p1_occupancy",
        "motion_2": "binary_sensor.kitchen_iris_frig_occupancy"
    }
    
    # Get current states
    for name, entity_id in key_entities.items():
        try:
            current_state = state.get(entity_id)
            state_attrs = state.getattr(entity_id)
            
            history_analysis["entity_states"][name] = {
                "entity_id": entity_id,
                "current_state": current_state,
                "attributes": state_attrs,
                "available": current_state not in (None, "unknown", "unavailable")
            }
            
            _info(f"Entity state: {name} = {current_state}")
            
        except Exception as e:
            _error(f"Error getting state for {entity_id}: {e}")
            history_analysis["entity_states"][name] = {"error": str(e)}
    
    # Analyze patterns
    home_state = history_analysis["entity_states"].get("home_state", {}).get("current_state")
    sink_wled_state = history_analysis["entity_states"].get("sink_wled", {}).get("current_state")
    fridge_wled_state = history_analysis["entity_states"].get("fridge_wled", {}).get("current_state")
    
    if home_state == "Day":
        if sink_wled_state != "off" or fridge_wled_state != "off":
            history_analysis["anomalies"].append({
                "type": "wled_on_in_day_mode",
                "description": f"WLED lights on during day mode: sink={sink_wled_state}, fridge={fridge_wled_state}",
                "severity": "high"
            })
            _error(f"❌ WLED anomaly detected: lights on in day mode")
        else:
            history_analysis["patterns"].append("WLED lights correctly off in day mode")
            _info("✅ WLED lights correctly off in day mode")
    
    # Check for entity availability issues
    unavailable_entities = [
        name for name, data in history_analysis["entity_states"].items()
        if not data.get("available", False)
    ]
    
    if unavailable_entities:
        history_analysis["anomalies"].append({
            "type": "entity_unavailable",
            "description": f"Entities unavailable: {unavailable_entities}",
            "severity": "medium"
        })
        _warn(f"⚠️ Some entities unavailable: {unavailable_entities}")
    
    return history_analysis

def generate_log_analysis_report():
    """Generate comprehensive log analysis report."""
    _info("📄 Generating comprehensive log analysis report...")
    
    report = {
        "report_timestamp": datetime.datetime.now().isoformat(),
        "analysis_sections": {},
        "summary": {},
        "recommendations": [],
        "manual_steps": []
    }
    
    try:
        # Run all analysis functions
        _info("Running log entry analysis...")
        report["analysis_sections"]["log_entries"] = get_recent_log_entries(24)
        
        _info("Running automation trace analysis...")
        report["analysis_sections"]["automation_traces"] = analyze_automation_traces()
        
        _info("Running state history analysis...")
        report["analysis_sections"]["state_history"] = analyze_state_history()
        
        # Generate summary
        anomalies_found = len(report["analysis_sections"]["state_history"].get("anomalies", []))
        patterns_found = len(report["analysis_sections"]["state_history"].get("patterns", []))
        
        report["summary"] = {
            "anomalies_detected": anomalies_found,
            "normal_patterns": patterns_found,
            "overall_status": "anomalies_detected" if anomalies_found > 0 else "normal",
            "analysis_completeness": "partial_automated"
        }
        
        # Compile recommendations
        all_recommendations = []
        for section in report["analysis_sections"].values():
            if "recommendations" in section:
                all_recommendations.extend(section["recommendations"])
            if "next_steps" in section:
                all_recommendations.extend(section["next_steps"])
        
        report["recommendations"] = list(set(all_recommendations))  # Remove duplicates
        
        # Manual analysis steps
        report["manual_steps"] = [
            "1. Check Home Assistant logs for kitchen motion automation around the time of issue",
            "2. Review automation traces in Developer Tools > Traces",
            "3. Look for WLED service call failures or timeouts",
            "4. Check for day mode state transition timing",
            "5. Verify motion sensor triggering during the issue",
            "6. Check for any network connectivity issues with WLED devices"
        ]
        
        _info(f"📄 Report generated - {anomalies_found} anomalies detected")
        
    except Exception as e:
        report["error"] = str(e)
        _error(f"Error generating report: {e}")
    
    return report

# --- Service Functions ---

@service("pyscript.analyze_kitchen_wled_logs")
def analyze_kitchen_wled_logs(hours_back=24):
    """Analyze kitchen WLED logs for day mode issues."""
    _info("🚀 Starting kitchen WLED log analysis...")
    
    try:
        analysis_result = generate_log_analysis_report()
        
        # Create a summary for logging
        summary = analysis_result.get("summary", {})
        status = summary.get("overall_status", "unknown")
        anomalies = summary.get("anomalies_detected", 0)
        
        if status == "normal":
            _info("✅ Log analysis complete - no anomalies detected")
        else:
            _warn(f"⚠️ Log analysis complete - {anomalies} anomalies detected")
        
        # Log key findings
        state_history = analysis_result.get("analysis_sections", {}).get("state_history", {})
        for anomaly in state_history.get("anomalies", []):
            _error(f"Anomaly: {anomaly['description']}")
        
        for pattern in state_history.get("patterns", []):
            _info(f"Normal pattern: {pattern}")
        
        return analysis_result
        
    except Exception as e:
        _error(f"Kitchen WLED log analysis failed: {e}")
        return {"error": str(e), "timestamp": datetime.datetime.now().isoformat()}

@service("pyscript.kitchen_wled_quick_diagnosis")
def kitchen_wled_quick_diagnosis():
    """Quick diagnosis of current kitchen WLED state vs expected behavior."""
    _info("⚡ Quick kitchen WLED diagnosis...")
    
    diagnosis = {
        "timestamp": datetime.datetime.now().isoformat(),
        "current_states": {},
        "diagnosis": "unknown",
        "issues": [],
        "immediate_actions": []
    }
    
    try:
        # Get critical states
        home_state = state.get("input_select.home_state")
        sink_wled = state.get("light.sink_wled") 
        fridge_wled = state.get("light.frig_strip")
        motion_1 = state.get("binary_sensor.aqara_motion_sensor_p1_occupancy")
        motion_2 = state.get("binary_sensor.kitchen_iris_frig_occupancy")
        
        diagnosis["current_states"] = {
            "home_state": home_state,
            "sink_wled": sink_wled,
            "fridge_wled": fridge_wled,
            "motion_1": motion_1,
            "motion_2": motion_2,
            "any_motion": (motion_1 == "on" or motion_2 == "on")
        }
        
        # Quick diagnosis logic
        if home_state == "Day":
            # In day mode, WLEDs should be off unless there's recent motion
            if sink_wled == "off" and fridge_wled == "off":
                diagnosis["diagnosis"] = "normal"
                _info("✅ Day mode: WLEDs correctly off")
            else:
                diagnosis["diagnosis"] = "anomaly_detected"
                diagnosis["issues"].append(f"WLEDs on in day mode: sink={sink_wled}, fridge={fridge_wled}")
                diagnosis["immediate_actions"].append("Check if motion recently triggered")
                diagnosis["immediate_actions"].append("Verify kitchen motion automation logic")
                _error(f"❌ Day mode anomaly: WLEDs should be off")
        
        elif home_state in ["Evening", "Night", "Early Morning"]:
            # In non-day modes, behavior depends on motion
            diagnosis["diagnosis"] = "mode_dependent"
            _info(f"ℹ️ Non-day mode ({home_state}): WLED behavior depends on motion")
        
        else:
            diagnosis["diagnosis"] = "invalid_state" 
            diagnosis["issues"].append(f"Invalid or unknown home state: {home_state}")
            _error(f"❌ Invalid home state: {home_state}")
        
        # Check entity availability
        for name, state_val in diagnosis["current_states"].items():
            if state_val in (None, "unknown", "unavailable"):
                diagnosis["issues"].append(f"Entity unavailable: {name}")
                diagnosis["immediate_actions"].append(f"Check entity availability: {name}")
        
        _info(f"⚡ Quick diagnosis: {diagnosis['diagnosis']}")
        return diagnosis
        
    except Exception as e:
        diagnosis["diagnosis"] = "error"
        diagnosis["error"] = str(e)
        _error(f"Quick diagnosis failed: {e}")
        return diagnosis

@service("pyscript.kitchen_wled_trace_recent_activity")
def kitchen_wled_trace_recent_activity():
    """Trace recent kitchen WLED activity and automation executions."""
    _info("🔍 Tracing recent kitchen WLED activity...")
    
    trace_results = {
        "timestamp": datetime.datetime.now().isoformat(),
        "recent_activity": {},
        "automation_status": {},
        "entity_changes": [],
        "recommendations": []
    }
    
    try:
        # Check automation states
        kitchen_automations = [
            entity_id for entity_id in state.names() 
            if entity_id.startswith("automation.") and "kitchen" in entity_id.lower()
        ]
        
        for auto_id in kitchen_automations:
            auto_state = state.get(auto_id)
            auto_attrs = state.getattr(auto_id) or {}
            
            trace_results["automation_status"][auto_id] = {
                "state": auto_state,
                "last_triggered": auto_attrs.get("last_triggered"),
                "current": auto_attrs.get("current", 0),
                "max": auto_attrs.get("max", 0)
            }
            
            _info(f"Automation: {auto_id} = {auto_state}")
        
        # Get current entity states for activity tracking
        key_entities = [
            "input_select.home_state",
            "light.sink_wled", 
            "light.frig_strip",
            "binary_sensor.aqara_motion_sensor_p1_occupancy",
            "binary_sensor.kitchen_iris_frig_occupancy"
        ]
        
        for entity_id in key_entities:
            current_state = state.get(entity_id)
            entity_attrs = state.getattr(entity_id) or {}
            
            trace_results["recent_activity"][entity_id] = {
                "current_state": current_state,
                "last_changed": entity_attrs.get("last_changed"),
                "last_updated": entity_attrs.get("last_updated")
            }
        
        # Recommendations for further investigation
        trace_results["recommendations"] = [
            "Check automation trace history in HA Developer Tools",
            "Look for recent motion sensor triggers",
            "Verify WLED service call success/failure",
            "Check for day mode transitions around issue time"
        ]
        
        _info("🔍 Activity trace completed")
        return trace_results
        
    except Exception as e:
        trace_results["error"] = str(e)
        _error(f"Activity trace failed: {e}")
        return trace_results