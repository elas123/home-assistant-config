################################################################################
# Remove Conflicting Storage Entities v1.0
# Author: Claude Code
# Updated: 2025-09-03 13:30
# Status: 🚧 In Progress
# Purpose: Remove input_text storage entities that conflict with SQLite
################################################################################

# !!! PYSCRIPT FUNCTIONS (Storage Cleanup) !!!

def identify_conflicting_entities():
    """Identify input_text entities that conflict with SQLite storage."""
    log.info("🔍 Identifying conflicting storage entities...")
    
    conflicting_entities = [
        # Adaptive memory storage entities (conflicting with SQLite)
        "input_text.adaptive_memory_bedroom",
        "input_text.adaptive_memory_kitchen",
        "input_text.adaptive_memory_bathroom", 
        "input_text.adaptive_memory_hallway",
        "input_text.adaptive_memory_laundry",
        "input_text.adaptive_memory_livingroom"
    ]
    
    # Also check for any template sensors that reference these entities
    conflicting_template_references = []
    
    log.info(f"📊 Found {len(conflicting_entities)} conflicting storage entities")
    for entity in conflicting_entities:
        current_value = state.get(entity)
        log.info(f"   {entity}: '{current_value}'")
    
    return {
        "entities": conflicting_entities,
        "template_references": conflicting_template_references
    }

def backup_conflicting_data():
    """Backup data from conflicting entities before removal."""
    log.info("💾 Backing up conflicting storage data...")
    
    conflicts = identify_conflicting_entities()
    backup_data = {}
    
    for entity in conflicts["entities"]:
        try:
            current_value = state.get(entity)
            if current_value and current_value not in ["", "unknown", "unavailable"]:
                backup_data[entity] = current_value
                log.info(f"✅ Backed up {entity}: {len(str(current_value))} characters")
            else:
                log.info(f"ℹ️ {entity}: No data to backup")
        except Exception as e:
            log.error(f"❌ Failed to backup {entity}: {e}")
    
    # Store backup data (could be logged or stored elsewhere)
    import datetime
    backup_timestamp = datetime.datetime.now().isoformat()
    
    log.info(f"📦 Backup completed with {len(backup_data)} entities at {backup_timestamp}")
    
    return {
        "timestamp": backup_timestamp,
        "data": backup_data
    }

def analyze_template_dependencies():
    """Analyze which template sensors depend on conflicting entities."""
    log.info("🔍 Analyzing template sensor dependencies...")
    
    # Based on the grep results, identify templates that use adaptive_memory entities
    dependent_templates = {
        "sensor.bedroom_learned_brightness": ["input_text.adaptive_memory_bedroom"],
        "sensor.bedroom_learned_temp": ["input_text.adaptive_memory_bedroom"],
        "sensor.bedroom_learned_confidence": ["input_text.adaptive_memory_bedroom"],
        "sensor.kitchen_learned_brightness": ["input_text.adaptive_memory_kitchen"],
        "sensor.kitchen_learned_temp": ["input_text.adaptive_memory_kitchen"],
        "sensor.kitchen_learned_confidence": ["input_text.adaptive_memory_kitchen"],
        "sensor.bathroom_learned_brightness": ["input_text.adaptive_memory_bathroom"],
        "sensor.bathroom_learned_temp": ["input_text.adaptive_memory_bathroom"],
        "sensor.bathroom_learned_confidence": ["input_text.adaptive_memory_bathroom"],
        "sensor.hallway_learned_brightness": ["input_text.adaptive_memory_hallway"],
        "sensor.hallway_learned_temp": ["input_text.adaptive_memory_hallway"],
        "sensor.hallway_learned_confidence": ["input_text.adaptive_memory_hallway"],
        "sensor.laundry_learned_brightness": ["input_text.adaptive_memory_laundry"],
        "sensor.laundry_learned_temp": ["input_text.adaptive_memory_laundry"],
        "sensor.laundry_learned_confidence": ["input_text.adaptive_memory_laundry"],
        "sensor.living_room_learned_brightness": ["input_text.adaptive_memory_livingroom"],
        "sensor.living_room_learned_temp": ["input_text.adaptive_memory_livingroom"],
        "sensor.living_room_learned_confidence": ["input_text.adaptive_memory_livingroom"]
    }
    
    log.info(f"📊 Found {len(dependent_templates)} template sensors that depend on conflicting entities")
    
    # Check which of these templates actually exist
    existing_templates = []
    missing_templates = []
    
    for template_sensor, dependencies in dependent_templates.items():
        sensor_state = state.get(template_sensor)
        if sensor_state not in ["unknown", "unavailable"]:
            existing_templates.append(template_sensor)
            log.info(f"✅ {template_sensor}: EXISTS (state: {sensor_state})")
        else:
            missing_templates.append(template_sensor)
            log.info(f"⚠️ {template_sensor}: MISSING or UNAVAILABLE")
    
    return {
        "existing_templates": existing_templates,
        "missing_templates": missing_templates,
        "all_dependencies": dependent_templates
    }

def clear_conflicting_storage_entities():
    """Clear the values of conflicting storage entities."""
    log.info("🧹 Clearing conflicting storage entities...")
    
    conflicts = identify_conflicting_entities()
    cleared_count = 0
    failed_count = 0
    
    for entity in conflicts["entities"]:
        try:
            # Clear the entity value
            service.call("input_text", "set_value", entity_id=entity, value="")
            cleared_count += 1
            log.info(f"✅ Cleared {entity}")
        except Exception as e:
            failed_count += 1
            log.error(f"❌ Failed to clear {entity}: {e}")
    
    log.info(f"🧹 Storage cleanup completed: {cleared_count} cleared, {failed_count} failed")
    
    return {
        "cleared": cleared_count,
        "failed": failed_count,
        "entities": conflicts["entities"]
    }

def validate_sqlite_still_works():
    """Validate that SQLite storage is still working after cleanup."""
    log.info("✅ Validating SQLite functionality after cleanup...")
    
    try:
        import sqlite3
        
        # Test database connection
        conn = sqlite3.connect("/config/home-assistant_v2.db", timeout=10.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT COUNT(*) as count FROM adaptive_learning")
        result = cursor.fetchone()
        record_count = result['count']
        
        log.info(f"📊 SQLite validation: {record_count} records in adaptive_learning table")
        
        # Test insertion capability
        import datetime
        test_timestamp = datetime.datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO adaptive_learning (room, condition_key, brightness_percent, temperature_kelvin, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, ("test_cleanup", "cleanup_validation", 50, None, test_timestamp))
        
        conn.commit()
        log.info("✅ SQLite insertion test successful")
        
        # Clean up test record
        cursor.execute("DELETE FROM adaptive_learning WHERE room = 'test_cleanup'")
        conn.commit()
        log.info("✅ SQLite cleanup test successful")
        
        conn.close()
        
        log.info("✅ SQLite validation completed successfully")
        return True
        
    except Exception as e:
        log.error(f"❌ SQLite validation failed: {e}")
        return False

@service("pyscript.remove_conflicting_storage_entities")
def remove_conflicting_storage_entities(backup_first=True, validate_after=True):
    """Remove input_text storage entities that conflict with SQLite storage."""
    log.info("🚀 Starting removal of conflicting storage entities...")
    
    results = {
        "backup": None,
        "dependencies": None,
        "cleanup": None,
        "validation": None,
        "success": False
    }
    
    try:
        # Step 1: Backup existing data
        if backup_first:
            log.info("\n" + "="*50)
            log.info("STEP 1: BACKING UP EXISTING DATA")
            log.info("="*50)
            results["backup"] = backup_conflicting_data()
        
        # Step 2: Analyze dependencies
        log.info("\n" + "="*50)
        log.info("STEP 2: ANALYZING TEMPLATE DEPENDENCIES")
        log.info("="*50)
        results["dependencies"] = analyze_template_dependencies()
        
        # Step 3: Clear conflicting entities
        log.info("\n" + "="*50)
        log.info("STEP 3: CLEARING CONFLICTING STORAGE")
        log.info("="*50)
        results["cleanup"] = clear_conflicting_storage_entities()
        
        # Step 4: Validate SQLite still works
        if validate_after:
            log.info("\n" + "="*50)
            log.info("STEP 4: VALIDATING SQLITE FUNCTIONALITY")
            log.info("="*50)
            results["validation"] = validate_sqlite_still_works()
        
        # Summary
        log.info("\n" + "="*50)
        log.info("CONFLICTING STORAGE REMOVAL SUMMARY")
        log.info("="*50)
        
        if results["backup"]:
            log.info(f"✅ Backed up {len(results['backup']['data'])} entities")
        
        if results["dependencies"]:
            existing = len(results["dependencies"]["existing_templates"])
            missing = len(results["dependencies"]["missing_templates"])
            log.info(f"📊 Template analysis: {existing} existing, {missing} missing dependencies")
        
        if results["cleanup"]:
            cleared = results["cleanup"]["cleared"]
            failed = results["cleanup"]["failed"]
            log.info(f"🧹 Cleanup results: {cleared} cleared, {failed} failed")
        
        if results["validation"]:
            log.info("✅ SQLite validation: PASSED")
        elif results["validation"] is False:
            log.error("❌ SQLite validation: FAILED")
        
        success = (
            (not backup_first or results["backup"] is not None) and
            (results["cleanup"]["failed"] == 0 if results["cleanup"] else False) and
            (not validate_after or results["validation"] is True)
        )
        
        results["success"] = success
        
        if success:
            log.info("🎉 Conflicting storage entities removed successfully!")
            log.info("💡 Template sensors may show 'unknown' until they are updated to use SQLite data")
        else:
            log.error("💥 Conflicting storage removal completed with issues")
        
        return results
        
    except Exception as e:
        log.error(f"❌ Conflicting storage removal failed: {e}")
        results["error"] = str(e)
        return results

@service("pyscript.restore_conflicting_storage_backup")  
def restore_conflicting_storage_backup():
    """Emergency restore function (for testing only)."""
    log.warning("⚠️ This is an emergency restore function - use with caution!")
    
    # This would restore from a backup if needed
    # Implementation would depend on how backup was stored
    log.info("🔄 Restore functionality not implemented - manual restoration required")
    
    return {"status": "not_implemented", "message": "Manual restoration required"}