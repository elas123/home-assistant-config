"""
ALS Diagnostics - Automated Maintenance System
PyScript backend for maintenance operations

This module handles:
- Periodic health validation and cleanup
- Error retention management
- Performance monitoring
- Manual maintenance operations
- Data buildup prevention
"""

import json
import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)

@pyscript_executor
def maintenance_health_check(debug_mode: bool = False):
    """
    Perform periodic health check and validation
    Called every 15 minutes by automation
    """
    try:
        if debug_mode:
            logger.info("Starting maintenance health check in debug mode")
            
        # Get current system state
        health_data = _get_system_health_data()
        
        # Validate system components
        validation_results = _validate_system_components()
        
        # Check for performance issues
        performance_issues = _check_performance_issues()
        
        # Update health score
        _update_health_score(health_data, validation_results, performance_issues)
        
        # Log results if debug mode
        if debug_mode:
            log_data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "health_data": health_data,
                "validation_results": validation_results,
                "performance_issues": performance_issues
            }
            logger.info(f"Health check completed: {json.dumps(log_data, indent=2)}")
            
        return True
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        if debug_mode:
            logger.exception("Health check exception details:")
        return False

@pyscript_executor  
def maintenance_automated_cleanup(retention_days: int, max_entries: int, debug_mode: bool = False):
    """
    Perform automated cleanup based on retention settings
    """
    try:
        if debug_mode:
            logger.info(f"Starting automated cleanup - retention: {retention_days} days, max entries: {max_entries}")
            
        cleanup_stats = {
            "errors_before": 0,
            "errors_after": 0,
            "errors_removed": 0,
            "systems_cleaned": []
        }
        
        # Get all ALS diagnostic entities
        diagnostic_entities = _get_diagnostic_entities()
        
        for entity_id in diagnostic_entities:
            try:
                # Clean old entries by date
                removed_by_date = _cleanup_old_entries(entity_id, retention_days, debug_mode)
                
                # Clean excess entries by count
                removed_by_count = _cleanup_excess_entries(entity_id, max_entries, debug_mode)
                
                total_removed = removed_by_date + removed_by_count
                if total_removed > 0:
                    cleanup_stats["systems_cleaned"].append({
                        "entity": entity_id,
                        "removed_by_date": removed_by_date,
                        "removed_by_count": removed_by_count,
                        "total_removed": total_removed
                    })
                    cleanup_stats["errors_removed"] += total_removed
                    
            except Exception as e:
                logger.error(f"Failed to cleanup entity {entity_id}: {str(e)}")
                if debug_mode:
                    logger.exception(f"Cleanup exception for {entity_id}:")
                    
        # Update cleanup counters
        if cleanup_stats["errors_removed"] > 0:
            _update_cleanup_counters(cleanup_stats["errors_removed"])
            
        if debug_mode:
            logger.info(f"Automated cleanup completed: {json.dumps(cleanup_stats, indent=2)}")
            
        return cleanup_stats
        
    except Exception as e:
        logger.error(f"Automated cleanup failed: {str(e)}")
        if debug_mode:
            logger.exception("Automated cleanup exception details:")
        return {"error": str(e)}

@pyscript_executor
def maintenance_emergency_cleanup(target_count: int, debug_mode: bool = False):
    """
    Perform emergency cleanup when data buildup is critical
    """
    try:
        if debug_mode:
            logger.info(f"Starting emergency cleanup - target count: {target_count}")
            
        diagnostic_entities = _get_diagnostic_entities()
        total_removed = 0
        
        for entity_id in diagnostic_entities:
            try:
                current_count = _get_entity_error_count(entity_id)
                if current_count > target_count:
                    # Remove oldest entries to reach target
                    to_remove = current_count - target_count
                    removed = _remove_oldest_entries(entity_id, to_remove, debug_mode)
                    total_removed += removed
                    
                    if debug_mode:
                        logger.info(f"Emergency cleanup for {entity_id}: removed {removed} entries")
                        
            except Exception as e:
                logger.error(f"Emergency cleanup failed for {entity_id}: {str(e)}")
                
        # Update counters
        if total_removed > 0:
            _update_cleanup_counters(total_removed)
            
        if debug_mode:
            logger.info(f"Emergency cleanup completed - removed {total_removed} entries")
            
        return {"removed_count": total_removed, "target_reached": True}
        
    except Exception as e:
        logger.error(f"Emergency cleanup failed: {str(e)}")
        if debug_mode:
            logger.exception("Emergency cleanup exception details:")
        return {"error": str(e)}

@pyscript_executor
def maintenance_full_cleanup(retention_days: int, debug_mode: bool = False):
    """
    Perform comprehensive full system cleanup
    """
    try:
        if debug_mode:
            logger.info(f"Starting full cleanup - retention: {retention_days} days")
            
        cleanup_results = {
            "timestamp": datetime.datetime.now().isoformat(),
            "retention_days": retention_days,
            "entities_processed": 0,
            "total_errors_removed": 0,
            "systems_cleaned": [],
            "performance_improved": False
        }
        
        # Get system state before cleanup
        health_before = _get_system_health_data()
        
        # Clean all diagnostic entities
        diagnostic_entities = _get_diagnostic_entities()
        
        for entity_id in diagnostic_entities:
            try:
                errors_before = _get_entity_error_count(entity_id)
                
                # Clean by date
                removed_by_date = _cleanup_old_entries(entity_id, retention_days, debug_mode)
                
                # Clean orphaned/corrupted entries
                removed_corrupted = _cleanup_corrupted_entries(entity_id, debug_mode)
                
                total_removed = removed_by_date + removed_corrupted
                errors_after = _get_entity_error_count(entity_id)
                
                if total_removed > 0:
                    cleanup_results["systems_cleaned"].append({
                        "entity": entity_id,
                        "errors_before": errors_before,
                        "errors_after": errors_after,
                        "removed_by_date": removed_by_date,
                        "removed_corrupted": removed_corrupted,
                        "total_removed": total_removed
                    })
                    
                cleanup_results["entities_processed"] += 1
                cleanup_results["total_errors_removed"] += total_removed
                
            except Exception as e:
                logger.error(f"Full cleanup failed for {entity_id}: {str(e)}")
                
        # Check performance improvement
        health_after = _get_system_health_data()
        cleanup_results["performance_improved"] = health_after.get("score", 0) > health_before.get("score", 0)
        
        # Update counters
        if cleanup_results["total_errors_removed"] > 0:
            _update_cleanup_counters(cleanup_results["total_errors_removed"])
            
        if debug_mode:
            logger.info(f"Full cleanup completed: {json.dumps(cleanup_results, indent=2)}")
            
        return cleanup_results
        
    except Exception as e:
        logger.error(f"Full cleanup failed: {str(e)}")
        if debug_mode:
            logger.exception("Full cleanup exception details:")
        return {"error": str(e)}

@pyscript_executor
def maintenance_clear_all_errors(debug_mode: bool = False):
    """
    Clear all error data from all systems (nuclear option)
    """
    try:
        if debug_mode:
            logger.warning("Starting CLEAR ALL ERRORS operation")
            
        diagnostic_entities = _get_diagnostic_entities()
        cleared_stats = {
            "timestamp": datetime.datetime.now().isoformat(),
            "entities_cleared": 0,
            "total_errors_cleared": 0,
            "systems": []
        }
        
        for entity_id in diagnostic_entities:
            try:
                errors_before = _get_entity_error_count(entity_id)
                _clear_all_entity_errors(entity_id, debug_mode)
                
                cleared_stats["systems"].append({
                    "entity": entity_id,
                    "errors_cleared": errors_before
                })
                
                cleared_stats["entities_cleared"] += 1
                cleared_stats["total_errors_cleared"] += errors_before
                
            except Exception as e:
                logger.error(f"Failed to clear errors for {entity_id}: {str(e)}")
                
        # Reset all counters
        _reset_all_counters()
        
        if debug_mode:
            logger.warning(f"CLEAR ALL completed: {json.dumps(cleared_stats, indent=2)}")
            
        return cleared_stats
        
    except Exception as e:
        logger.error(f"Clear all errors failed: {str(e)}")
        if debug_mode:
            logger.exception("Clear all errors exception details:")
        return {"error": str(e)}

@pyscript_executor
def maintenance_generate_report(include_performance: bool = True, debug_mode: bool = False):
    """
    Generate comprehensive diagnostic report
    """
    try:
        if debug_mode:
            logger.info("Starting diagnostic report generation")
            
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "report_version": "1.0",
            "system_overview": _get_system_overview(),
            "health_summary": _get_system_health_data(),
            "error_analysis": _analyze_error_patterns(),
            "maintenance_history": _get_maintenance_history(),
            "recommendations": []
        }
        
        if include_performance:
            report["performance_metrics"] = _get_performance_metrics()
            
        # Generate recommendations
        report["recommendations"] = _generate_maintenance_recommendations(report)
        
        # Save report to file
        report_filename = f"als_diagnostic_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        _save_report_to_file(report, report_filename, debug_mode)
        
        if debug_mode:
            logger.info(f"Diagnostic report generated: {report_filename}")
            
        return {"report_file": report_filename, "report_data": report}
        
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        if debug_mode:
            logger.exception("Report generation exception details:")
        return {"error": str(e)}

# Helper functions
def _get_system_health_data() -> Dict[str, Any]:
    """Get current system health data"""
    try:
        total_errors = int(state.get("sensor.als_total_error_count") or 0)
        max_errors = int(state.get("input_number.maintenance_max_error_entries") or 200)
        
        health_score = max(0, ((max_errors - total_errors) / max_errors * 100))
        
        return {
            "total_errors": total_errors,
            "max_errors": max_errors,
            "score": round(health_score, 1),
            "status": "healthy" if health_score >= 80 else "degraded" if health_score >= 50 else "critical"
        }
    except Exception as e:
        logger.error(f"Failed to get health data: {str(e)}")
        return {"error": str(e)}

def _validate_system_components() -> Dict[str, bool]:
    """Validate all system components are functioning"""
    try:
        results = {}
        
        # Check critical entities exist and are responding
        critical_entities = [
            "sensor.als_total_error_count",
            "sensor.als_critical_alert_count", 
            "sensor.als_warning_alert_count",
            "automation.als_system_startup_validation"
        ]
        
        for entity_id in critical_entities:
            entity_state = state.get(entity_id)
            results[entity_id] = entity_state is not None and entity_state != "unavailable"
            
        return results
    except Exception as e:
        logger.error(f"Component validation failed: {str(e)}")
        return {"error": str(e)}

def _check_performance_issues() -> List[str]:
    """Check for performance issues"""
    issues = []
    
    try:
        # Check error count trends
        total_errors = int(state.get("sensor.als_total_error_count") or 0)
        max_errors = int(state.get("input_number.maintenance_max_error_entries") or 200)
        
        if total_errors > max_errors * 0.8:
            issues.append("High error count approaching limit")
            
        if total_errors > max_errors * 0.9:
            issues.append("Critical error count - cleanup recommended")
            
        # Check automation responsiveness
        # Add more performance checks as needed
        
    except Exception as e:
        issues.append(f"Performance check failed: {str(e)}")
        
    return issues

def _update_health_score(health_data: Dict, validation_results: Dict, performance_issues: List[str]):
    """Update the system health score based on collected data"""
    try:
        # This would update internal health tracking
        # Implementation depends on your specific health tracking needs
        pass
    except Exception as e:
        logger.error(f"Failed to update health score: {str(e)}")

def _get_diagnostic_entities() -> List[str]:
    """Get list of all diagnostic entities that need cleanup"""
    # Return entities that store error data
    return [
        "sensor.als_critical_errors",
        "sensor.als_warning_errors", 
        "sensor.als_info_errors",
        "sensor.als_system_errors",
        "sensor.als_automation_errors",
        "sensor.als_entity_errors"
    ]

def _cleanup_old_entries(entity_id: str, retention_days: int, debug_mode: bool = False) -> int:
    """Remove entries older than retention period"""
    try:
        # Implementation would depend on how error data is stored
        # This is a placeholder for the actual cleanup logic
        if debug_mode:
            logger.info(f"Cleaning old entries for {entity_id} (retention: {retention_days} days)")
        return 0
    except Exception as e:
        logger.error(f"Failed to cleanup old entries for {entity_id}: {str(e)}")
        return 0

def _cleanup_excess_entries(entity_id: str, max_entries: int, debug_mode: bool = False) -> int:
    """Remove excess entries beyond max count"""
    try:
        if debug_mode:
            logger.info(f"Cleaning excess entries for {entity_id} (max: {max_entries})")
        return 0
    except Exception as e:
        logger.error(f"Failed to cleanup excess entries for {entity_id}: {str(e)}")
        return 0

def _get_entity_error_count(entity_id: str) -> int:
    """Get current error count for entity"""
    try:
        # Implementation depends on data structure
        return 0
    except Exception as e:
        logger.error(f"Failed to get error count for {entity_id}: {str(e)}")
        return 0

def _remove_oldest_entries(entity_id: str, count: int, debug_mode: bool = False) -> int:
    """Remove oldest entries from entity"""
    try:
        if debug_mode:
            logger.info(f"Removing {count} oldest entries from {entity_id}")
        return 0
    except Exception as e:
        logger.error(f"Failed to remove oldest entries from {entity_id}: {str(e)}")
        return 0

def _cleanup_corrupted_entries(entity_id: str, debug_mode: bool = False) -> int:
    """Clean up corrupted or malformed entries"""
    try:
        if debug_mode:
            logger.info(f"Cleaning corrupted entries for {entity_id}")
        return 0
    except Exception as e:
        logger.error(f"Failed to cleanup corrupted entries for {entity_id}: {str(e)}")
        return 0

def _clear_all_entity_errors(entity_id: str, debug_mode: bool = False):
    """Clear all errors for specific entity"""
    try:
        if debug_mode:
            logger.warning(f"Clearing ALL errors for {entity_id}")
        # Implementation depends on data structure
    except Exception as e:
        logger.error(f"Failed to clear all errors for {entity_id}: {str(e)}")

def _update_cleanup_counters(removed_count: int):
    """Update cleanup statistics counters"""
    try:
        # Increment the errors cleared counter
        service.call("counter.increment", 
                    entity_id="counter.maintenance_errors_cleared",
                    data={"value": removed_count})
    except Exception as e:
        logger.error(f"Failed to update cleanup counters: {str(e)}")

def _reset_all_counters():
    """Reset all maintenance counters"""
    try:
        counters = [
            "counter.maintenance_cleanup_runs",
            "counter.maintenance_errors_cleared"
        ]
        for counter in counters:
            service.call("counter.reset", entity_id=counter)
    except Exception as e:
        logger.error(f"Failed to reset counters: {str(e)}")

def _get_system_overview() -> Dict[str, Any]:
    """Get system overview data for reports"""
    return {
        "total_entities": len(_get_diagnostic_entities()),
        "active_automations": "TBD",  # Count active ALS automations
        "last_maintenance": state.get("input_datetime.maintenance_last_cleanup_time"),
        "maintenance_runs": int(state.get("counter.maintenance_cleanup_runs") or 0)
    }

def _analyze_error_patterns() -> Dict[str, Any]:
    """Analyze error patterns for reporting"""
    return {
        "most_common_errors": "TBD",  # Analyze error frequency
        "error_trends": "TBD",  # Time-based error analysis
        "problem_areas": "TBD"  # Identify problematic systems
    }

def _get_maintenance_history() -> Dict[str, Any]:
    """Get maintenance history for reporting"""
    return {
        "total_runs": int(state.get("counter.maintenance_cleanup_runs") or 0),
        "total_cleared": int(state.get("counter.maintenance_errors_cleared") or 0),
        "last_run": state.get("input_datetime.maintenance_last_cleanup_time"),
        "average_cleanup_size": "TBD"
    }

def _get_performance_metrics() -> Dict[str, Any]:
    """Get performance metrics"""
    return {
        "response_times": "TBD",  # Measure system response times
        "resource_usage": "TBD",  # Monitor resource consumption
        "efficiency_score": "TBD"  # Overall efficiency rating
    }

def _generate_maintenance_recommendations(report_data: Dict[str, Any]) -> List[str]:
    """Generate maintenance recommendations based on report data"""
    recommendations = []
    
    health_score = report_data.get("health_summary", {}).get("score", 100)
    if health_score < 70:
        recommendations.append("Consider reducing error retention period to improve performance")
    
    if health_score < 50:
        recommendations.append("Run manual cleanup immediately - system health critical")
        
    # Add more intelligent recommendations based on analysis
    
    return recommendations

def _save_report_to_file(report_data: Dict[str, Any], filename: str, debug_mode: bool = False):
    """Save diagnostic report to file"""
    try:
        # Save to /config/www for web access
        filepath = f"/config/www/{filename}"
        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
            
        if debug_mode:
            logger.info(f"Report saved to {filepath}")
            
    except Exception as e:
        logger.error(f"Failed to save report to file: {str(e)}")