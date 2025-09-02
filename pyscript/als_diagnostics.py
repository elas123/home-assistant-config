################################################################################
# ALS DIAGNOSTICS SYSTEM - PYSCRIPT FUNCTIONS v1.1
# Author: Claude
# Updated: 2025-09-02 15:12
# Status: ✅ Service Decorators Fixed
# Purpose: Complex diagnostics logic functions for ALS error management
################################################################################

import json
from datetime import datetime

# !!! DIAGNOSTICS CORE FUNCTIONS !!!

@service("pyscript.should_capture_als_error")
def should_capture_als_error(message=""):
    """Determine if error message should trigger ALS diagnostics capture."""
    if not message:
        return False
    
    message_lower = message.lower()
    keywords = [
        'adaptive', 'intelligent', 'bedroom', 'kitchen', 'bathroom',
        'hallway', 'laundry', 'livingroom', 'living room', 
        'routine_timing', 'als_'
    ]
    
    return any(keyword in message_lower for keyword in keywords)

@service("pyscript.classify_error_by_room")
def classify_error_by_room(message=""):
    """Classify error message by room and return target entities."""
    if not message:
        return {"room": "global", "entity": "input_text.latest_system_error", "feed_entity": "input_text.system_error_feed"}
    
    message_lower = message.lower()
    
    room_mapping = {
        'bedroom': {
            'keywords': ['bedroom'],
            'entity': 'input_text.als_error_bedroom',
            'feed_entity': 'input_text.als_error_feed_bedroom'
        },
        'kitchen': {
            'keywords': ['kitchen'],
            'entity': 'input_text.als_error_kitchen', 
            'feed_entity': 'input_text.als_error_feed_kitchen'
        },
        'livingroom': {
            'keywords': ['livingroom', 'living room'],
            'entity': 'input_text.als_error_livingroom',
            'feed_entity': 'input_text.als_error_feed_livingroom'
        },
        'bathroom': {
            'keywords': ['bathroom'],
            'entity': 'input_text.als_error_bathroom',
            'feed_entity': 'input_text.als_error_feed_bathroom'
        },
        'hallway': {
            'keywords': ['hallway'],
            'entity': 'input_text.als_error_hallway',
            'feed_entity': 'input_text.als_error_feed_hallway'
        },
        'laundry': {
            'keywords': ['laundry'],
            'entity': 'input_text.als_error_laundry',
            'feed_entity': 'input_text.als_error_feed_laundry'
        }
    }
    
    for room, config in room_mapping.items():
        if any(keyword in message_lower for keyword in config['keywords']):
            return {
                "room": room,
                "entity": config['entity'],
                "feed_entity": config['feed_entity']
            }
    
    # Default to global
    return {
        "room": "global", 
        "entity": "input_text.latest_system_error",
        "feed_entity": "input_text.system_error_feed"
    }

@service("pyscript.format_error_message")
def format_error_message(message="", level="ERROR", timestamp=""):
    """Format error message with timestamp and truncation."""
    if not timestamp:
        timestamp = datetime.now().strftime('%H:%M:%S')
    
    formatted = f"{timestamp}: {level} - {message}"
    return formatted[:100] if len(formatted) > 100 else formatted

@service("pyscript.update_error_feed")
def update_error_feed(feed_entity="", error_message="", max_items=5):
    """Update error feed with rotation logic."""
    try:
        current_feed_raw = state.get(feed_entity) or "[]"
        if current_feed_raw in ['unknown', 'unavailable', '']:
            current_feed = []
        else:
            current_feed = json.loads(current_feed_raw)
        
        # Add new error
        updated_feed = current_feed + [error_message]
        
        # Rotate if exceeding max
        if len(updated_feed) > max_items:
            updated_feed = updated_feed[-max_items:]
        
        # Update the feed
        service.call("input_text", "set_value", 
                    entity_id=feed_entity, 
                    value=json.dumps(updated_feed))
        
        if state.get('input_boolean.als_verbose_logging') == 'on':
            log.info(f"Updated {feed_entity} with new error (total: {len(updated_feed)})")
            
    except Exception as e:
        log.error(f"Failed to update error feed {feed_entity}: {e}")

@service("pyscript.process_als_error")
def process_als_error(message="", level="ERROR", source="Unknown"):
    """Main error processing function - replaces complex YAML template logic."""
    try:
        # Check if we should capture this error
        if not should_capture_als_error(message):
            return
        
        # Format the error message
        formatted_error = format_error_message(message, level)
        
        # Classify by room
        room_info = classify_error_by_room(message)
        
        # Update room-specific error status
        service.call("input_text", "set_value",
                    entity_id=room_info["entity"],
                    value=formatted_error)
        
        # Update error feed
        max_items = 5 if room_info["room"] != "global" else 20
        update_error_feed(room_info["feed_entity"], formatted_error, max_items)
        
        # Log the processing
        if state.get('input_boolean.als_verbose_logging') == 'on':
            log.info(f"Processed ALS error for {room_info['room']}: {formatted_error[:50]}...")
            
    except Exception as e:
        log.error(f"Failed to process ALS error: {e}")

# !!! HEALTH MONITORING FUNCTIONS !!!

@service("pyscript.calculate_room_health_pill")
def calculate_room_health_pill(room=""):
    """Calculate health pill status for a specific room."""
    try:
        if not room or room == "global":
            return "🟩"
        
        # Get room error feed
        feed_entity = f"input_text.als_error_feed_{room}"
        feed_raw = state.get(feed_entity) or "[]"
        
        if feed_raw in ['unknown', 'unavailable', '']:
            return "🟩"
        
        errors = json.loads(feed_raw)
        
        if not errors:
            return "🟩"
        
        # Check error levels (most recent errors have priority)
        for error in reversed(errors[-3:]):  # Check last 3 errors
            error_upper = error.upper()
            if 'CRITICAL' in error_upper or 'ERROR' in error_upper:
                return "🟥"
        
        # Check for warnings
        for error in reversed(errors[-3:]):
            if 'WARNING' in error.upper():
                return "🟨"
        
        return "🟩"
        
    except Exception as e:
        log.error(f"Failed to calculate health pill for {room}: {e}")
        return "🟥"

@service("pyscript.calculate_global_health_status")
def calculate_global_health_status():
    """Calculate overall system health status."""
    try:
        rooms = ['bedroom', 'kitchen', 'livingroom', 'bathroom', 'hallway', 'laundry']
        room_statuses = []
        
        for room in rooms:
            status = calculate_room_health_pill(room)
            room_statuses.append(status)
        
        # Global health is worst of all rooms
        if "🟥" in room_statuses:
            return "critical"
        elif "🟨" in room_statuses:  
            return "warning"
        else:
            return "healthy"
            
    except Exception as e:
        log.error(f"Failed to calculate global health: {e}")
        return "critical"

# !!! UTILITY FUNCTIONS !!!

@service("pyscript.clear_room_errors")
def clear_room_errors(room=""):
    """Clear all errors for a specific room."""
    try:
        if room == "all":
            rooms = ['bedroom', 'kitchen', 'livingroom', 'bathroom', 'hallway', 'laundry']
            for r in rooms:
                clear_room_errors(r)
            # Also clear global
            service.call("input_text", "set_value", entity_id="input_text.latest_system_error", value="")
            service.call("input_text", "set_value", entity_id="input_text.system_error_feed", value="[]")
            return
        
        if room and room != "global":
            # Clear room error status
            service.call("input_text", "set_value", 
                        entity_id=f"input_text.als_error_{room}", 
                        value="")
            
            # Clear room error feed
            service.call("input_text", "set_value",
                        entity_id=f"input_text.als_error_feed_{room}",
                        value="[]")
            
            log.info(f"🧹 Cleared all errors for {room}")
        
    except Exception as e:
        log.error(f"Failed to clear errors for {room}: {e}")

# !!! DIAGNOSTIC MAINTENANCE !!!

@time_trigger("cron(*/15 * * * *)")  # Every 15 minutes
def periodic_health_check():
    """Periodic health validation and cleanup."""
    try:
        if state.get('input_boolean.als_diagnostics_enabled') != 'on':
            return
        
        # Update global health status
        health_status = calculate_global_health_status()
        service.call("input_text", "set_value",
                    entity_id="input_text.als_global_health_status", 
                    value=health_status)
        
        if state.get('input_boolean.als_verbose_logging') == 'on':
            log.info(f"🏥 Health check completed - Global status: {health_status}")
            
    except Exception as e:
        log.error(f"Failed periodic health check: {e}")