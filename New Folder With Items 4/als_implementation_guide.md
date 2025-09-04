# 🚀 ALS Implementation & Development Guide
**Development Phase:** Active Implementation  
**Target Completion:** 2-3 weeks  
**Current Priority:** Three-Tier Hierarchy System

---

## 🎯 IMPLEMENTATION WORKFLOW DIAGRAMS

### **Current User Flow (Existing System):**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Opens    │───▶│  Select Room    │───▶│   Room Detail   │
│   iOS App       │    │   from List     │    │     View        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Teaching      │◀───│  Toggle Mode    │◀───│  Choose Action  │
│     Mode        │    │   Selection     │    │  (Teach/Record) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                     │
         ▼                        ▼                     ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Set Brightness/ │    │  Start/Stop     │    │  View Past      │
│  Temperature    │    │   Recording     │    │   Sessions      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                     │
         ▼                        ▼                     ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Send Data     │    │   Save Session  │    │ Session History │
│  to HA/PyScript │    │   to Database   │    │   Display       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **NEW Enhanced User Flow (Target Implementation):**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Opens    │───▶│  Select Room    │───▶│   Room Detail   │
│   iOS App       │    │   from List     │    │  + System Type  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐                          ┌─────────────────┐
│  System Type    │◀─────────────────────────│ Choose System   │
│   Dropdown      │                          │   Type for      │
│ [Manual ▼]      │                          │     Room        │
│ [Intelligent ▼] │                          └─────────────────┘
│ [Learned ▼]     │                                    │
│ [Recorded ▼]    │                                    ▼
└─────────────────┘                          ┌─────────────────┐
         │                                   │   Additional    │
         ▼                                   │    Actions      │
┌─────────────────┐    ┌─────────────────┐   │ (Teach/Record)  │
│   Teaching      │◀───│  Action Based   │◀──┤                 │
│     Mode        │    │    on System    │   │ + NEW:          │
└─────────────────┘    │     Type        │   │ Analyze         │
         │              └─────────────────┘   │ Recording       │
         ▼                        │           └─────────────────┘
┌─────────────────┐              ▼                     │
│ Enhanced Teach  │    ┌─────────────────┐           ▼
│ (now aware of   │    │ Enhanced Record │   ┌─────────────────┐
│ system hierarchy│    │ (2-3hr sessions,│   │ Recording       │
│ and recorded    │    │ quality scoring)│   │ Analysis View   │
│ data conflicts) │    │                 │   │ (Interactive    │
└─────────────────┘    └─────────────────┘   │ Timeline)       │
         │                        │          └─────────────────┘
         ▼                        ▼                    │
┌─────────────────┐    ┌─────────────────┐           ▼
│  Send Enhanced  │    │ Enhanced Session│   ┌─────────────────┐
│  Learning Data  │    │ Data + Metadata │   │ Approve/Reject  │
│ (with hierarchy │    │ (quality score, │   │  Data Points    │
│  preferences)   │    │ confidence)     │   │                 │
└─────────────────┘    └─────────────────┘   └─────────────────┘
         │                        │                    │
         ▼                        ▼                    ▼
┌─────────────────┐    ┌─────────────────┐   ┌─────────────────┐
│ PyScript        │    │ Database Update │   │ Generate Smooth │
│ Hierarchy       │    │ + System Status │   │ Curve + Preview │
│ Decision        │    │ Metrics         │   │                 │
└─────────────────┘    └─────────────────┘   └─────────────────┘
                                                       │
                                                       ▼
                                             ┌─────────────────┐
                                             │ Save as Active  │
                                             │ "Recorded" Data │
                                             │ for Automation  │
                                             └─────────────────┘
```

---

## 📝 DETAILED IMPLEMENTATION STEPS

### **PHASE 1: iOS App System Selector (Days 1-2)**

#### **Step 1.1: Enhance Room Model**
```swift
// File: Models/Room.swift (New file to create)
import Foundation

enum SystemType: String, CaseIterable, Codable {
    case manual = "manual"
    case intelligent = "intelligent"
    case learned = "learned"
    case recorded = "recorded"
    
    var displayName: String {
        switch self {
        case .manual: return "Manual Control"
        case .intelligent: return "Weather + Time"
        case .learned: return "Learning Mode"
        case .recorded: return "Recorded Ramp"
        }
    }
    
    var description: String {
        switch self {
        case .manual: return "Direct user control only"
        case .intelligent: return "Automatic based on weather/time"
        case .learned: return "Learns from your patterns"
        case .recorded: return "Uses smooth recorded curves"
        }
    }
    
    var icon: String {
        switch self {
        case .manual: return "hand.raised.fill"
        case .intelligent: return "brain.head.profile"
        case .learned: return "chart.line.uptrend.xyaxis"
        case .recorded: return "waveform.path.ecg"
        }
    }
    
    var color: Color {
        switch self {
        case .manual: return .gray
        case .intelligent: return .blue
        case .learned: return .green
        case .recorded: return .purple
        }
    }
}

// UPDATE existing Room struct in ContentView.swift:
struct Room: Identifiable {
    let id = UUID()
    let name: String
    let icon: String
    let brightnessEntity: String
    let temperatureEntity: String
    let supportsTemperature: Bool
    var brightness: Int = 0
    var temperature: Int = 3000
    
    // NEW PROPERTIES:
    var currentSystemType: SystemType = .intelligent
    var availableSystemTypes: [SystemType] = [.manual, .intelligent, .learned]
    var hasRecordedData: Bool = false
    var systemLastUpdated: Date = Date()
}
```

#### **Step 1.2: Create System Selector UI Component**
```swift
// File: Views/SystemSelectorView.swift (New file to create)
import SwiftUI

struct SystemSelectorView: View {
    @Binding var selectedSystem: SystemType
    let availableSystems: [SystemType]
    let hasRecordedData: Bool
    let onSystemChange: (SystemType) -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Automation System")
                .font(.headline)
                .foregroundColor(.primary)
            
            // System Type Cards
            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: 12) {
                ForEach(availableSystems, id: \.self) { systemType in
                    SystemTypeCard(
                        systemType: systemType,
                        isSelected: selectedSystem == systemType,
                        isAvailable: isSystemAvailable(systemType),
                        onTap: {
                            selectedSystem = systemType
                            onSystemChange(systemType)
                        }
                    )
                }
            }
            
            // Current System Status
            HStack {
                Image(systemName: selectedSystem.icon)
                    .foregroundColor(selectedSystem.color)
                Text("Currently using: \(selectedSystem.displayName)")
                    .font(.caption)
                    .foregroundColor(.secondary)
                Spacer()
            }
            .padding(.top, 8)
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
    
    private func isSystemAvailable(_ systemType: SystemType) -> Bool {
        switch systemType {
        case .recorded:
            return hasRecordedData
        default:
            return true
        }
    }
}

struct SystemTypeCard: View {
    let systemType: SystemType
    let isSelected: Bool
    let isAvailable: Bool
    let onTap: () -> Void
    
    var body: some View {
        Button(action: onTap) {
            VStack(spacing: 8) {
                Image(systemName: systemType.icon)
                    .font(.title2)
                    .foregroundColor(isSelected ? .white : systemType.color)
                
                Text(systemType.displayName)
                    .font(.caption)
                    .fontWeight(.medium)
                    .foregroundColor(isSelected ? .white : .primary)
                    .multilineTextAlignment(.center)
                
                if !isAvailable {
                    Text("Not Available")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }
            .frame(height: 80)
            .frame(maxWidth: .infinity)
            .background(
                RoundedRectangle(cornerRadius: 8)
                    .fill(isSelected ? systemType.color : Color(.systemBackground))
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(systemType.color, lineWidth: isSelected ? 0 : 1)
                    )
            )
        }
        .disabled(!isAvailable)
        .opacity(isAvailable ? 1.0 : 0.6)
    }
}
```

#### **Step 1.3: Update ContentView to Show System Types**
```swift
// ADD to ContentView.swift in the room list items:

// REPLACE the existing VStack in NavigationLink with:
VStack(alignment: .leading) {
    Text(room.name)
        .font(.headline)
        .foregroundColor(.primary)
    
    // System status line
    HStack {
        Image(systemName: room.currentSystemType.icon)
            .foregroundColor(room.currentSystemType.color)
            .font(.caption)
        
        Text(room.currentSystemType.displayName)
            .font(.caption)
            .foregroundColor(.secondary)
        
        Text("•")
            .font(.caption)
            .foregroundColor(.secondary)
        
        Text(room.supportsTemperature ? "\(room.brightness)% • \(room.temperature)K" : "\(room.brightness)%")
            .font(.caption)
            .foregroundColor(.secondary)
    }
}
```

#### **Step 1.4: Update RoomDetailView with System Selector**
```swift
// ADD to RoomDetailView.swift at the top of the ScrollView VStack:

SystemSelectorView(
    selectedSystem: $room.currentSystemType,
    availableSystems: determineAvailableSystems(),
    hasRecordedData: room.hasRecordedData,
    onSystemChange: { newSystemType in
        Task {
            await updateRoomSystemType(newSystemType)
        }
    }
)

// ADD these functions to RoomDetailView:
private func determineAvailableSystems() -> [SystemType] {
    var available: [SystemType] = [.manual, .intelligent, .learned]
    
    if room.hasRecordedData {
        available.append(.recorded)
    }
    
    return available
}

private func updateRoomSystemType(_ systemType: SystemType) async {
    do {
        try await HomeAssistantAPI.setRoomSystemType(
            room.name.lowercased().replacingOccurrences(of: " ", with: "_"),
            systemType: systemType
        )
        
        // Update local room data
        room.currentSystemType = systemType
        room.systemLastUpdated = Date()
        
        // Refresh current settings to show any changes
        await refreshData()
        
    } catch {
        print("Error updating room system type: \(error)")
        // TODO: Show user-friendly error message
    }
}
```

### **PHASE 2: PyScript Hierarchy Backend (Days 2-3)**

#### **Step 2.1: Create Hierarchy Controller Service**
```python
# File: /config/pyscript/hierarchy_controller.py

"""
ALS Hierarchy Controller - Main decision engine for lighting automation
Implements the three-tier priority system: Recorded → Learned → Intelligent → Manual
"""

import sqlite3
import json
import logging
from datetime import datetime, time
from typing import Optional, Dict, Any

_LOGGER = logging.getLogger(__name__)

class HierarchyController:
    def __init__(self, hass):
        self.hass = hass
        self.db_path = "/config/als_database.db"
        self.initialize_database()
    
    def initialize_database(self):
        """Create necessary database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Room System Preferences
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS room_system_preferences (
                    room TEXT PRIMARY KEY,
                    system_type TEXT NOT NULL DEFAULT 'intelligent',
                    fallback_enabled BOOLEAN DEFAULT TRUE,
                    priority_override BOOLEAN DEFAULT FALSE,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # System Performance Metrics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hierarchy_decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room TEXT NOT NULL,
                    requested_system TEXT,
                    actual_system TEXT,
                    fallback_reason TEXT,
                    confidence_score REAL,
                    brightness_value INTEGER,
                    temperature_value INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    @pyscript_executor
    def get_room_lighting_decision(self, room: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main entry point for lighting decisions
        Returns lighting values based on room's system preference and hierarchy
        """
        if context is None:
            context = {
                "current_time": datetime.now(),
                "weather": self.get_weather_data(),
                "user_present": self.is_user_present(room)
            }
        
        # Get room's preferred system
        system_preference = self.get_room_system_preference(room)
        
        _LOGGER.info(f"Making lighting decision for {room} with system preference: {system_preference}")
        
        decision_result = {
            "room": room,
            "requested_system": system_preference,
            "actual_system": None,
            "brightness": None,
            "temperature": None,
            "confidence": 0.0,
            "fallback_reason": None,
            "timestamp": context["current_time"].isoformat()
        }
        
        # Try systems in hierarchy order
        systems_to_try = self.get_systems_hierarchy(system_preference)
        
        for system_type in systems_to_try:
            try:
                result = self.try_system(room, system_type, context)
                if result and result["success"]:
                    decision_result.update({
                        "actual_system": system_type,
                        "brightness": result["brightness"],
                        "temperature": result.get("temperature"),
                        "confidence": result.get("confidence", 0.5),
                        "fallback_reason": result.get("fallback_reason")
                    })
                    break
            except Exception as e:
                _LOGGER.error(f"Error trying system {system_type} for room {room}: {e}")
                continue
        
        # Log the decision
        self.log_hierarchy_decision(decision_result)
        
        return decision_result
    
    def get_systems_hierarchy(self, preferred_system: str) -> list:
        """Get ordered list of systems to try based on preference"""
        hierarchy_map = {
            "recorded": ["recorded", "learned", "intelligent", "manual"],
            "learned": ["learned", "intelligent", "manual"],
            "intelligent": ["intelligent", "manual"],
            "manual": ["manual"]
        }
        return hierarchy_map.get(preferred_system, ["manual"])
    
    def try_system(self, room: str, system_type: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Try to get lighting values from a specific system"""
        
        if system_type == "recorded":
            return self.try_recorded_system(room, context)
        elif system_type == "learned":
            return self.try_learned_system(room, context)
        elif system_type == "intelligent":
            return self.try_intelligent_system(room, context)
        elif system_type == "manual":
            return self.try_manual_fallback(room, context)
        
        return None
    
    def try_recorded_system(self, room: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Try to get values from recorded smooth curves"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                current_time = context["current_time"].time()
                
                # Find active recorded curve that covers current time
                cursor.execute("""
                    SELECT sc.curve_data, sc.quality_score, rs.session_name
                    FROM smooth_curves sc
                    JOIN recorded_sessions rs ON sc.session_id = rs.id
                    WHERE rs.room = ? AND rs.status = 'active' AND sc.is_active = 1
                    ORDER BY sc.quality_score DESC
                    LIMIT 1
                """, (room,))
                
                result = cursor.fetchone()
                if result:
                    curve_data = json.loads(result[0])
                    quality_score = result[1]
                    session_name = result[2]
                    
                    # Interpolate current value from curve
                    interpolated = self.interpolate_curve_value(curve_data, current_time)
                    
                    if interpolated:
                        return {
                            "success": True,
                            "brightness": interpolated["brightness"],
                            "temperature": interpolated.get("temperature"),
                            "confidence": quality_score,
                            "source": f"recorded_curve_{session_name}"
                        }
        
        except Exception as e:
            _LOGGER.error(f"Error in recorded system for room {room}: {e}")
        
        return {"success": False, "fallback_reason": "no_recorded_data"}
    
    def try_learned_system(self, room: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Try to get values from learned patterns (existing ALS system)"""
        try:
            # Call existing ALS learning system
            brightness_entity = f"sensor.{room}_intelligent_brightness"
            temperature_entity = f"sensor.intelligent_temperature_{room}"
            
            brightness_state = self.hass.states.get(brightness_entity)
            temp_state = self.hass.states.get(temperature_entity)
            
            if brightness_state and brightness_state.state not in ['unknown', 'unavailable']:
                brightness = int(brightness_state.state)
                temperature = None
                
                if temp_state and temp_state.state not in ['unknown', 'unavailable']:
                    temperature = int(temp_state.state)
                
                return {
                    "success": True,
                    "brightness": brightness,
                    "temperature": temperature,
                    "confidence": 0.8,  # High confidence in learned system
                    "source": "learned_patterns"
                }
        
        except Exception as e:
            _LOGGER.error(f"Error in learned system for room {room}: {e}")
        
        return {"success": False, "fallback_reason": "learned_system_unavailable"}
    
    def try_intelligent_system(self, room: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Try to get values from intelligent weather/time calculations"""
        try:
            # This would call your existing intelligent lighting calculations
            # For now, simplified example based on time of day
            current_hour = context["current_time"].hour
            
            if 6 <= current_hour <= 8:  # Morning
                brightness = 85
            elif 9 <= current_hour <= 17:  # Day
                brightness = 95
            elif 18 <= current_hour <= 21:  # Evening
                brightness = 60
            else:  # Night
                brightness = 30
            
            return {
                "success": True,
                "brightness": brightness,
                "temperature": 3000,  # Default warm white
                "confidence": 0.6,
                "source": "intelligent_calculation"
            }
        
        except Exception as e:
            _LOGGER.error(f"Error in intelligent system for room {room}: {e}")
        
        return {"success": False, "fallback_reason": "intelligent_calculation_failed"}
    
    def try_manual_fallback(self, room: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Manual fallback - get last known good values"""
        try:
            # Get last known brightness from entity state
            brightness_entity = f"sensor.{room}_intelligent_brightness"
            state = self.hass.states.get(brightness_entity)
            
            brightness = 50  # Default fallback
            if state and state.state not in ['unknown', 'unavailable']:
                brightness = int(state.state)
            
            return {
                "success": True,
                "brightness": brightness,
                "temperature": 3000,
                "confidence": 0.3,
                "source": "manual_fallback"
            }
        
        except Exception as e:
            _LOGGER.error(f"Error in manual fallback for room {room}: {e}")
            return {
                "success": True,
                "brightness": 50,
                "temperature": 3000,
                "confidence": 0.1,
                "source": "emergency_fallback"
            }

# Service Definitions for Home Assistant
@service
def set_room_system(room: str, system_type: str):
    """Set the automation system type for a room"""
    controller = HierarchyController(hass)
    controller.set_room_system_preference(room, system_type)

@service
def get_room_lighting(room: str):
    """Get current lighting recommendation for a room"""
    controller = HierarchyController(hass)
    result = controller.get_room_lighting_decision(room)
    
    # Update Home Assistant sensors with the result
    hass.states.set(f"sensor.{room}_hierarchy_decision", result["actual_system"], {
        "brightness": result["brightness"],
        "temperature": result["temperature"],
        "confidence": result["confidence"],
        "requested_system": result["requested_system"],
        "fallback_reason": result.get("fallback_reason"),
        "timestamp": result["timestamp"]
    })
    
    return result

@service
def get_system_status():
    """Get overall system status and metrics"""
    controller = HierarchyController(hass)
    return controller.get_system_status()
```

### **PHASE 3: Recording Analysis Interface (Days 4-6)**

#### **Step 3.1: Create Recording Analysis View**
```swift
// File: Views/RecordingAnalysisView.swift (New file to create)
import SwiftUI
import Charts

struct RecordingAnalysisView: View {
    let session: RampSession
    @State private var sessionDetails: RecordingSessionDetails?
    @State private var selectedPointIndex: Int?
    @State private var curvePreview: [CurvePoint] = []
    @State private var isGeneratingCurve = false
    @State private var showingCurvePreview = false
    @Environment(\.presentationMode) var presentationMode
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Session Info Header
                    SessionInfoCard(session: session)
                    
                    // Data Points Timeline
                    if let details = sessionDetails {
                        DataPointsTimelineView(
                            dataPoints: details.dataPoints,
                            selectedIndex: $selectedPointIndex,
                            onApprove: approvePoint,
                            onReject: rejectPoint
                        )
                        
                        // Selected Point Details
                        if let selectedIndex = selectedPointIndex,
                           selectedIndex < details.dataPoints.count {
                            DataPointDetailCard(
                                point: details.dataPoints[selectedIndex],
                                onApprove: { approvePoint(at: selectedIndex) },
                                onReject: { rejectPoint(at: selectedIndex) }
                            )
                        }
                        
                        // Curve Generation Section
                        CurveGenerationSection(
                            approvedCount: details.dataPoints.filter { $0.approved }.count,
                            isGenerating: $isGeneratingCurve,
                            showingPreview: $showingCurvePreview,
                            curvePreview: curvePreview,
                            onGenerateCurve: generateCurve,
                            onSaveCurve: saveCurveAsActive
                        )
                    }
                }
                .padding()
            }
            .navigationTitle("Analyze Recording")
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarItems(
                leading: Button("Cancel") {
                    presentationMode.wrappedValue.dismiss()
                },
                trailing: Button("Done") {
                    presentationMode.wrappedValue.dismiss()
                }
                .disabled(sessionDetails?.dataPoints.filter { $0.approved }.count ?? 0 < 3)
            )
        }
        .onAppear {
            Task {
                await loadSessionDetails()
            }
        }
        .sheet(isPresented: $showingCurvePreview) {
            CurvePreviewView(curveData: curvePreview)
        }
    }
    
    private func loadSessionDetails() async {
        do {
            sessionDetails = try await HomeAssistantAPI.getRecordingSessionDetails(session.id)
        } catch {
            print("Error loading session details: \(error)")
        }
    }
    
    private func approvePoint(at index: Int) {
        guard var details = sessionDetails,
              index < details.dataPoints.count else { return }
        
        details.dataPoints[index].approved = true
        details.dataPoints[index].rejected = false
        sessionDetails = details
        
        Task {
            try await HomeAssistantAPI.approveDataPoint(session.id, pointId: details.dataPoints[index].id)
        }
    }
    
    private func rejectPoint(at index: Int) {
        guard var details = sessionDetails,
              index < details.dataPoints.count else { return }
        
        details.dataPoints[index].approved = false
        details.dataPoints[index].rejected = true
        sessionDetails = details
        
        Task {
            try await HomeAssistantAPI.rejectDataPoint(session.id, pointId: details.dataPoints[index].id)
        }
    }
    
    private func generateCurve() {
        isGeneratingCurve = true
        
        Task {
            do {
                let curveData = try await HomeAssistantAPI.generateCurveFromSession(session.id)
                curvePreview = curveData.points
                showingCurvePreview = true
            } catch {
                print("Error generating curve: \(error)")
            }
            isGeneratingCurve = false
        }
    }
    
    private func saveCurveAsActive() {
        Task {
            do {
                try await HomeAssistantAPI.activateGeneratedCurve(session.id)
                presentationMode.wrappedValue.dismiss()
            } catch {
                print("Error activating curve: \(error)")
            }
        }
    }
}

// Supporting Models
struct RecordingSessionDetails: Codable {
    let sessionId: String
    let sessionName: String
    let room: String
    let totalDuration: TimeInterval
    var dataPoints: [RecordingDataPoint]
    let qualityScore: Double
}

struct RecordingDataPoint: Identifiable, Codable {
    let id: String
    let timestamp: Date
    let brightness: Int
    let temperature: Int?
    var approved: Bool = false
    var rejected: Bool = false
    let confidenceScore: Double
    let changeReason: String? // "manual_adjustment", "motion_trigger", etc.
}

struct CurvePoint: Identifiable {
    let id = UUID()
    let time: TimeInterval // Minutes from session start
    let brightness: Double
    let temperature: Double?
}

struct CurveData: Codable {
    let sessionId: String
    let points: [CurvePoint]
    let qualityScore: Double
    let algorithm: String
}
```

---

## 🎯 TESTING & VALIDATION CHECKLIST

### **Phase 1 Testing (System Selectors):**
- [ ] Room system type can be selected via dropdown
- [ ] System preference is saved to Home Assistant
- [ ] Room list shows current system type with correct icon/color
- [ ] "Recorded" option only shows when recorded data exists
- [ ] System changes trigger appropriate backend updates

### **Phase 2 Testing (Hierarchy Backend):**
- [ ] Hierarchy decision logic follows correct priority order
- [ ] Fallback systems work when primary system fails
- [ ] Database logging captures all decision data
- [ ] Performance meets < 200ms response time target
- [ ] Error handling gracefully manages system failures

### **Phase 3 Testing (Recording Analysis):**
- [ ] Recording session data loads correctly in timeline
- [ ] Data point approve/reject functionality works
- [ ] Curve generation produces smooth, realistic curves
- [ ] Generated curves can be activated for automation
- [ ] Quality scoring accurately reflects curve usefulness

### **Integration Testing:**
- [ ] End-to-end recording → analysis → activation workflow
- [ ] System switching doesn't break existing functionality
- [ ] Multiple users can interact with system simultaneously
- [ ] Database integrity maintained under concurrent operations
- [ ] iOS app handles network errors gracefully

---

## 🚨 CRITICAL SUCCESS FACTORS

### **Must-Have Features for Launch:**
1. **System selector works reliably** in iOS app
2. **Hierarchy fallback is bulletproof** - never leaves lights in bad state
3. **Recording analysis is intuitive** for non-technical users
4. **Curve generation produces high-quality results** (90%+ user satisfaction)
5. **Existing functionality remains unbroken** during upgrade

### **Performance Requirements:**
- System decision: < 200ms response time
- iOS app responsiveness: < 100ms UI updates
- Database operations: < 50ms for simple queries
- Curve generation: < 5 seconds for typical session

### **Error Recovery Requirements:**
- Database corruption: Auto-backup and recovery
- Network failures: Local fallback with sync when reconnected
- Malformed data: Graceful degradation, not system crash
- User mistakes: Undo functionality for critical operations

---

## 📈 MONITORING & SUCCESS METRICS

### **Key Performance Indicators:**
- **User Satisfaction:** > 90% positive feedback on curve quality
- **System Reliability:** < 1% fallback to emergency manual mode
- **Performance:** 99.5% of operations complete within target time
- **Adoption:** 80% of rooms using recorded or learned systems within 30 days

### **Monitoring Dashboard (Future Enhancement):**
```swift
// iOS App System Status Screen
struct SystemStatusDashboard: View {
    var body: some View {
        VStack {
            // System Health Indicators
            SystemHealthCard()
            
            // Room Performance Metrics
            RoomPerformanceList()
            
            // Recent System Decisions
            RecentDecisionsList()
            
            // Curve Quality Metrics
            CurveQualityMetrics()
        }
    }
}
```

---

**Implementation Guide Version:** 1.0  
**Last Updated:** September 3, 2025  
**Status:** Ready for development - start with Phase 1  
**Next Review:** Daily during active development