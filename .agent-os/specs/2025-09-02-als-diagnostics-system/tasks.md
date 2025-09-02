# Spec Tasks

These are the tasks to be completed for the spec detailed in @.agent-os/specs/2025-09-02-als-diagnostics-system/spec.md

> Created: 2025-09-02
> Status: In Progress - PyScript Foundation Complete

## Tasks

- [x] 1. Build Error Capture Infrastructure (COMPLETED)
  - [x] 1.1 Write tests for system_log event filtering and classification
  - [x] 1.2 Create input_text helpers for room-specific error storage
  - [x] 1.3 Implement system_log_event automation with room classification logic
  - [x] 1.4 Add error message truncation and timestamp formatting
  - [x] 1.5 Verify error capture system catches and classifies ALS errors correctly
  - [x] 1.6 Refactor implementation to use PyScript for improved maintainability

- [ ] 2. Fix Python Script Validation Issues
  - [ ] 2.1 Write tests for PyScript validation and error handling
  - [ ] 2.2 Fix als_learning_status.py validation issues (indentation, error handling)
  - [ ] 2.3 Fix als_error_management.py validation issues (JSON handling, room detection)
  - [ ] 2.4 Add proper exception handling to all PyScript functions
  - [ ] 2.5 Verify all PyScript functions pass validation and execute correctly

- [ ] 3. Implement Visual Health System
  - [ ] 3.1 Write tests for health pill calculation logic using PyScript
  - [ ] 3.2 Create room-specific health pill sensors (🟩/🟨/🟥) with PyScript backend
  - [ ] 3.3 Implement global health aggregation sensor using consolidated PyScript functions
  - [ ] 3.4 Add health status attributes (error counts, affected rooms, status text)
  - [ ] 3.5 Verify health pills accurately reflect system status in real-time

- [ ] 4. Build Smart Notification Framework
  - [ ] 4.1 Write tests for health status change detection using PyScript
  - [ ] 4.2 Create health status notification automation with 30-second delay
  - [ ] 4.3 Implement context-aware notification messages (critical/warning/healthy)
  - [ ] 4.4 Add deep link integration to diagnostic dashboard
  - [ ] 4.5 Verify notifications trigger correctly with proper HA 2025.8+ tag format

- [ ] 5. Create Diagnostic Dashboard Integration
  - [ ] 5.1 Write tests for diagnostic sensor data accuracy
  - [ ] 5.2 Implement system diagnostic sensor with learning status aggregation using PyScript
  - [ ] 5.3 Create configuration input helpers (retention, intervals, toggles)
  - [ ] 5.4 Add manual control interfaces for error clearing and system management
  - [ ] 5.5 Verify dashboard provides comprehensive system status and control capabilities

- [ ] 6. Implement Automated Maintenance System
  - [ ] 6.1 Write tests for periodic health check automation using PyScript
  - [ ] 6.2 Create 15-minute health validation and cleanup automation
  - [ ] 6.3 Implement configurable error retention management with PyScript backend
  - [ ] 6.4 Add manual error clearing and diagnostic report scripts
  - [ ] 6.5 Verify maintenance system prevents data buildup and maintains performance

## Implementation Notes

- **Completed:** Error capture infrastructure has been successfully implemented using PyScript functions
- **Current Focus:** Python script validation fixes are the immediate priority before continuing
- **Architecture:** All new implementations should leverage the existing PyScript foundation for consistency
- **Testing:** Each major task follows TDD approach: tests → implementation → verification