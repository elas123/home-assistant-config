# Spec Requirements Document

> Spec: Routine Timing Learning Enhancement
> Created: 2025-09-02
> Status: Planning

## Overview

Extend the existing Adaptive Learning System (ALS) to learn behavioral timing patterns from actual light usage, enabling the system to predict optimal routine completion times and replace fixed schedules with personalized, adaptive timing intelligence using the proven ALS infrastructure.

## User Stories

### Homeowner Seeking Reliable Morning Automation

As a homeowner with varying morning routines, I want the system to learn when I actually finish my morning routine (by monitoring when I turn off living room lights), so that my lighting automation ends at the perfect time without relying on unreliable sun elevation or device tracker data.

The system will observe patterns like "On winter work days, Frank typically ends his routine at 7:25 AM" and automatically adjust lighting ramp timing to conclude naturally around that predicted time. This eliminates the current issues with inconsistent Early Morning mode endings and provides personalized automation that adapts to seasonal changes and routine variations.

### Smart Home User Wanting Unified Logic  

As a smart home enthusiast, I want a single learning algorithm that works for both work and non-work days, so that I don't need to maintain complex dual-logic systems with separate conditional workflows.

The timing learning enhancement will leverage the existing ALS pattern recognition infrastructure for all day types (work days, weekends, holidays) by storing timing data in the current adaptive_learning table using specialized room identifiers. This provides consistent, predictable behavior while reusing proven data management and learning algorithms.

### Adaptive Automation Enthusiast

As someone who values self-improving technology, I want the system to automatically adapt to changes in my routine over time, so that my home automation stays optimized without manual intervention.

The learning system will continuously monitor patterns, detect routine changes, and gradually adapt predictions while maintaining confidence scoring to ensure reliability during transition periods.

## Spec Scope

1. **Timing Capture Automation** - Detect and record living room light turn-off events during Early Morning mode, storing completion times in existing adaptive_learning table
2. **ALS Integration Enhancement** - Extend existing als_memory_manager.py functions to handle timing data alongside brightness learning using encoded time values
3. **Prediction Logic** - Develop analysis functions that read timing patterns from existing ALS data structure and calculate predicted routine end times
4. **Home State Integration** - Update existing Early Morning end logic to use ALS-based timing predictions while maintaining current fallback mechanisms
5. **Learning Dashboard Extensions** - Enhance existing ALS interface to show timing learning progress, prediction accuracy, and manual override controls

## Out of Scope

- Voice control integration for the teaching system
- Mobile app companion features  
- Integration with external fitness trackers or sleep monitors
- Multi-user pattern learning (focused on single household patterns)
- Real-time pattern adjustment during the same day (daily patterns only)

## Expected Deliverable

1. **Enhanced ALS System** - Existing adaptive learning infrastructure successfully captures and analyzes routine timing patterns alongside current brightness learning
2. **Accurate Timing Predictions** - System provides reliable routine end time predictions with >80% accuracy after initial learning period, using existing ALS data structures
3. **Seamless Integration** - Updated Home Assistant packages integrate timing predictions into existing automation without breaking current ALS functionality or requiring database changes

## Spec Documentation

- Tasks: @.agent-os/specs/2025-09-02-kitchen-teaching-system/tasks.md
- Technical Specification: @.agent-os/specs/2025-09-02-kitchen-teaching-system/sub-specs/technical-spec.md