# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-09-02-als-diagnostics-system/spec.md

> Created: 2025-09-02
> Version: 1.0.0

## Technical Requirements

### Error Capture Engine
- **system_log Event Monitoring**: Continuous listening for ERROR, CRITICAL, and WARNING level system_log_event triggers
- **Intelligent Error Filtering**: Keyword-based classification for ALS-related errors (adaptive, intelligent, room names)
- **Room Classification Logic**: Automated error sorting by room location using message content analysis
- **Queue-based Processing**: Queued automation mode with silent max_exceeded handling for high-volume error scenarios
- **Error Message Truncation**: 100-character limit for error storage with timestamp prefixing

### Data Storage Architecture
- **Input Text Helpers**: Room-specific error storage using input_text entities (als_error_bedroom, als_error_kitchen, etc.)
- **Error Feed Management**: JSON-based circular buffers maintaining last 5 errors per room, last 20 global errors
- **Global Error Storage**: Centralized system error tracking with latest_system_error and system_error_feed entities
- **Health Status Storage**: Persistent health state tracking via input_text.als_global_health_status
- **Configuration Storage**: Input helpers for error retention, health check intervals, and system toggles

### Visual Health System
- **Health Pill Sensors**: Template sensors generating 🟩/🟨/🟥 indicators for each room and global system status
- **Health Aggregation Logic**: Multi-level health status calculation from room-level to system-level indicators
- **Status Attribution**: Rich sensor attributes including error counts, affected rooms, and descriptive status text
- **Real-time Updates**: Template-based sensors with automatic recalculation on state changes
- **Icon Integration**: Dynamic MDI icon selection based on health status (check-circle, alert, alert-circle)

### Notification Framework  
- **Health Change Detection**: State-based triggers with 30-second delay for status change confirmation
- **Smart Notification Logic**: Conditional messaging based on health pill status (critical/warning/healthy)
- **Deep Link Integration**: Dashboard URL embedding for direct navigation to diagnostic interfaces
- **Notification Tagging**: Proper tag-based notification management (HA 2025.8+ compliant, not notification_id)
- **Persistent Notifications**: Using notify.persistent_notification for reliable delivery and dashboard integration

### Diagnostic Dashboard Integration
- **Rich Data Sources**: Comprehensive sensor data for dashboard visualization including error feeds, health pills, system diagnostics
- **Manual Control Interface**: Input boolean helpers for system enable/disable, notification control, verbose logging
- **Configuration Management**: Input number helpers for error retention periods and health check intervals  
- **Diagnostic Reporting**: Automated report generation with system-wide status aggregation
- **Script Integration**: Manual error clearing, diagnostic report generation, and maintenance script interfaces

### Automated Maintenance System
- **Periodic Health Checks**: Time pattern automation (15-minute intervals) for system validation and cleanup
- **Error Feed Rotation**: Automatic old error removal with configurable retention periods (1-30 days)
- **Cleanup Scripts**: Manual and automated error clearing with room-specific and global clearing capabilities
- **Verbose Logging Control**: Conditional logging behavior based on system configuration
- **Health Status Validation**: Automated verification of sensor states and error feed integrity

### Performance Requirements
- **Error Processing Latency**: System log events processed within 2 seconds of occurrence
- **Memory Efficiency**: Maximum 10MB additional storage for error feeds and health status data
- **Dashboard Responsiveness**: Health pill updates reflected in dashboards within 5 seconds
- **Notification Reliability**: 99%+ notification delivery rate with proper deep linking functionality
- **System Reliability**: Graceful handling of malformed error messages and sensor state corruption

## Approach

### Architecture Pattern
The system follows an event-driven architecture with three primary layers:
1. **Capture Layer**: system_log event listeners with intelligent filtering
2. **Processing Layer**: Error classification, room assignment, and health status calculation
3. **Presentation Layer**: Health pills, notifications, and dashboard integration

### Data Flow
1. System log events trigger error capture automations
2. Errors are filtered, classified, and stored in room-specific input_text entities
3. Template sensors aggregate error data into health pills
4. Health status changes trigger notifications with deep links
5. Periodic maintenance automations clean up old data and validate system health

### Error Processing Pipeline
```
system_log_event → Filter (ALS keywords) → Classify (Room) → Store (input_text) → 
Update Health Pills → Trigger Notifications → Dashboard Display
```

### Health Status Calculation
- **Green (🟩)**: No errors in last 24 hours
- **Yellow (🟨)**: Warning level errors present
- **Red (🟥)**: Critical/Error level events detected

## External Dependencies

### Core Home Assistant Components
- **Home Assistant Core**: system_log_event triggers and persistent notification service
- **Template Platform**: Template sensors for health pills and diagnostic aggregation
- **Input Helpers**: input_text, input_number, and input_boolean components for data storage and configuration
- **Logbook Integration**: logbook.log service for diagnostic message logging
- **Time Pattern Triggers**: Home Assistant time_pattern triggers for periodic maintenance
- **Dashboard Framework**: Home Assistant Lovelace for diagnostic dashboard integration

### Data Processing Dependencies
- **JSON Processing**: Native Jinja2 to_json/from_json filters for error feed management
- **Template Engine**: Jinja2 templating for complex data manipulation and health calculations
- **State Management**: Home Assistant state persistence for configuration and error storage

### Integration Requirements
- **Notification Services**: notify.persistent_notification for reliable message delivery
- **Script Platform**: Home Assistant script component for manual maintenance operations
- **Automation Platform**: Home Assistant automation component with queue mode support
- **Sensor Platform**: Template sensor platform for health pill generation

### Version Compatibility
- **Home Assistant**: 2025.8+ (for proper notification tagging support)
- **Frontend**: Modern Lovelace dashboard support required
- **Mobile App**: Home Assistant Companion app for notification deep linking