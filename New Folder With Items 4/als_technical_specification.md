# 🔧 ALS Technical Specification Document
**Version:** 2.0  
**Date:** September 3, 2025  
**System:** Adaptive Learning Smart Lighting with Three-Tier Hierarchy

---

## 🏗️ SYSTEM ARCHITECTURE OVERVIEW

### **Core Components Stack:**
```
┌─────────────────────────────────────────────────────────────┐
│ 📱 iOS App (SwiftUI)                                        │
│ ├── ContentView (Room List & System Selectors)            │
│ ├── RoomDetailView (Teaching & Recording)                  │
│ ├── RecordingAnalysisView (NEW - Interactive Timeline)     │
│ └── SystemDashboardView (NEW - Performance Metrics)       │
└─────────────────────────────────────────────────────────────┘
                           ↓ REST API
┌─────────────────────────────────────────────────────────────┐
│ 🏠 Home Assistant Core                                      │
│ ├── 18+ YAML Configuration Packages                        │
│ ├── Sensor Entities (brightness, temperature)             │
│ ├── Service Calls (als_teach_room, ramp_recording)        │
│ └── Automation Triggers & Conditions                      │
└─────────────────────────────────────────────────────────────┘
                           ↓ PyScript
┌─────────────────────────────────────────────────────────────┐
│ 🐍 PyScript Backend Services                                │
│ ├── als_teaching_service.py (Learning algorithms)          │
│ ├── ramp_recording_system.py (Session capture)            │
│ ├── hierarchy_controller.py (NEW - System priority)       │
│ └── curve_generator.py (NEW - Smooth interpolation)       │
└─────────────────────────────────────────────────────────────┘
                           ↓ SQL
┌─────────────────────────────────────────────────────────────┐
│ 🗄️ SQLite Database                                          │
│ ├── learning_data (patterns, preferences)                  │
│ ├── recorded_sessions (manual adjustments)                │
│ ├── smooth_curves (generated automation data)             │
│ └── system_settings (room preferences, hierarchies)       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 THREE-TIER HIERARCHY SYSTEM

### **Priority Decision Tree:**
```python
def get_lighting_value(room, current_time, context):
    system_preference = get_room_system(room)
    
    # Tier 1: Recorded Data (Highest Priority)
    if system_preference >= RECORDED and has_recorded_curve(room, current_time):
        value = interpolate_recorded_curve(room, current_time)
        if validate_value(value):
            return value, "RECORDED"
    
    # Tier 2: Learned Data
    if system_preference >= LEARNED and has_learning_data(room, context):
        value = calculate_learned_preference(room, current_time, context)
        if validate_value(value):
            return value, "LEARNED"
    
    # Tier 3: Intelligent Data
    if system_preference >= INTELLIGENT:
        value = calculate_intelligent_lighting(room, current_time, weather_data)
        if validate_value(value):
            return value, "INTELLIGENT"
    
    # Tier 4: Manual Fallback
    return get_last_known_value(room), "MANUAL_FALLBACK"
```

### **System Types & Behaviors:**
```python
class SystemType(Enum):
    MANUAL = 0      # User control only, no automation
    INTELLIGENT = 1 # Weather + time calculations
    LEARNED = 2     # Statistical learning from patterns
    RECORDED = 3    # Smooth curves from recorded sessions

# Hierarchy Rules:
# RECORDED can fall back to → LEARNED → INTELLIGENT → MANUAL
# LEARNED can fall back to → INTELLIGENT → MANUAL
# INTELLIGENT can fall back to → MANUAL
# MANUAL has no fallback (pure user control)
```

---

## 📱 iOS APP TECHNICAL DETAILS

### **Current SwiftUI Architecture:**
```swift
// EXISTING STRUCTURE
ContentView.swift:
├── @State rooms: [Room] - Array of 7 configured rooms
├── NavigationView with List
├── Room icons, names, current brightness/temp display
└── NavigationLink to RoomDetailView

RoomDetailView.swift:
├── @State teachingMode, rampRecordingMode toggles
├── Brightness/Temperature sliders for teaching
├── Recording session management
├── Current settings display with refresh button
└── API integration (teachRoom, startRecording, etc.)

HomeAssistantAPI.swift:
├── Static baseURL and authentication token
├── teachRoom() - Send learning data
├── startRampRecording() - Begin session
├── stopRampRecording() - End session
├── fetchEntityState() - Get current values
└── getRampSessions() - Historical data
```

### **NEW COMPONENTS NEEDED:**

#### **1. System Selector Enhancement:**
```swift
// Add to Room model
struct Room: Identifiable {
    // ... existing properties
    var systemType: SystemType = .intelligent
    var availableSystems: [SystemType] = [.intelligent, .learned, .manual]
}

// New enum
enum SystemType: String, CaseIterable, Codable {
    case manual = "manual"
    case intelligent = "intelligent"
    case learned = "learned"
    case recorded = "recorded"
    
    var displayName: String {
        switch self {
        case .manual: return "Manual"
        case .intelligent: return "Intelligent"
        case .learned: return "Learned"
        case .recorded: return "Recorded Ramp"
        }
    }
    
    var icon: String {
        switch self {
        case .manual: return "hand.raised"
        case .intelligent: return "brain"
        case .learned: return "chart.line.uptrend.xyaxis"
        case .recorded: return "waveform.path"
        }
    }
}

// New UI Component
struct SystemSelectorView: View {
    @Binding var selectedSystem: SystemType
    let availableSystems: [SystemType]
    let room: Room
    
    var body: some View {
        HStack {
            Image(systemName: selectedSystem.icon)
                .foregroundColor(.blue)
            
            Picker("System Type", selection: $selectedSystem) {
                ForEach(availableSystems, id: \.self) { system in
                    HStack {
                        Image(systemName: system.icon)
                        Text(system.displayName)
                    }.tag(system)
                }
            }
            .pickerStyle(MenuPickerStyle())
        }
    }
}
```

#### **2. Recording Analysis Interface:**
```swift
struct RecordingAnalysisView: View {
    let session: RampSession
    @State private var dataPoints: [RecordingDataPoint] = []
    @State private var selectedPoint: RecordingDataPoint?
    @State private var curvePreview: [CGPoint] = []
    
    var body: some View {
        VStack {
            // Timeline scrubber
            TimelineView(dataPoints: $dataPoints, 
                        selectedPoint: $selectedPoint)
            
            // Data point details
            if let point = selectedPoint {
                DataPointDetailView(point: point,
                                  onApprove: approvePoint,
                                  onReject: rejectPoint)
            }
            
            // Curve preview
            CurvePreviewView(curveData: curvePreview)
            
            // Actions
            HStack {
                Button("Generate Curve") { generateCurve() }
                Button("Save & Use") { saveCurveAsRecorded() }
            }
        }
    }
}

struct RecordingDataPoint: Identifiable, Codable {
    let id: UUID
    let timestamp: Date
    let brightness: Int
    let temperature: Int?
    var approved: Bool = false
    var rejected: Bool = false
    let confidence: Double // Quality score
}
```

#### **3. API Extensions:**
```swift
extension HomeAssistantAPI {
    // System Management
    static func setRoomSystemType(_ room: String, systemType: SystemType) async throws {
        let url = URL(string: "\(baseURL)/api/services/pyscript/set_room_system")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let serviceData: [String: Any] = [
            "room": room,
            "system_type": systemType.rawValue
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: serviceData)
        let (_, _) = try await URLSession.shared.data(for: request)
    }
    
    // Recording Analysis
    static func getRecordingSessionDetails(_ sessionId: String) async throws -> RecordingSessionDetails {
        let url = URL(string: "\(baseURL)/api/services/pyscript/get_session_details")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let serviceData: [String: Any] = ["session_id": sessionId]
        request.httpBody = try JSONSerialization.data(withJSONObject: serviceData)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(RecordingSessionDetails.self, from: data)
    }
    
    static func approveDataPoint(_ sessionId: String, pointId: String) async throws {
        // Similar API call to approve specific data point
    }
    
    static func generateCurveFromSession(_ sessionId: String) async throws -> CurveData {
        // API call to generate smooth curve from approved points
    }
}
```

---

## 🐍 PYSCRIPT BACKEND ENHANCEMENTS

### **New Service Files Needed:**

#### **1. hierarchy_controller.py:**
```python
"""
ALS Hierarchy Controller
Manages the three-tier decision system for lighting automation
"""

import sqlite3
from datetime import datetime, time
import json

class HierarchyController:
    def __init__(self, hass):
        self.hass = hass
        self.db_path = "/config/als_database.db"
    
    @pyscript_executor
    def get_room_lighting(self, room: str, current_time: datetime = None):
        """Main decision point for room lighting values"""
        if current_time is None:
            current_time = datetime.now()
        
        # Get room's system preference
        system_type = self.get_room_system_preference(room)
        
        # Tier 1: Recorded Data
        if system_type in ["recorded", "learned", "intelligent"]:
            recorded_value = self.try_recorded_system(room, current_time)
            if recorded_value is not None:
                return {
                    "brightness": recorded_value["brightness"],
                    "temperature": recorded_value.get("temperature"),
                    "source": "RECORDED",
                    "confidence": recorded_value["confidence"]
                }
        
        # Tier 2: Learned Data
        if system_type in ["learned", "intelligent"]:
            learned_value = self.try_learned_system(room, current_time)
            if learned_value is not None:
                return {
                    "brightness": learned_value["brightness"],
                    "temperature": learned_value.get("temperature"),
                    "source": "LEARNED",
                    "confidence": learned_value["confidence"]
                }
        
        # Tier 3: Intelligent Data
        if system_type == "intelligent":
            intelligent_value = self.try_intelligent_system(room, current_time)
            if intelligent_value is not None:
                return {
                    "brightness": intelligent_value["brightness"],
                    "temperature": intelligent_value.get("temperature"),
                    "source": "INTELLIGENT",
                    "confidence": intelligent_value["confidence"]
                }
        
        # Tier 4: Manual Fallback
        return self.get_manual_fallback(room)
    
    def try_recorded_system(self, room: str, current_time: datetime):
        """Try to get value from recorded smooth curves"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Find active recorded curve for current time
            time_of_day = current_time.time()
            cursor.execute("""
                SELECT curve_data, confidence_score
                FROM smooth_curves sc
                JOIN recorded_sessions rs ON sc.session_id = rs.id
                WHERE rs.room = ? AND rs.status = 'active'
                AND ? BETWEEN rs.start_time AND rs.end_time
                ORDER BY confidence_score DESC
                LIMIT 1
            """, (room, time_of_day))
            
            result = cursor.fetchone()
            if result:
                curve_data = json.loads(result[0])
                return self.interpolate_curve(curve_data, current_time)
        
        return None
    
    def interpolate_curve(self, curve_data: dict, current_time: datetime) -> dict:
        """Interpolate brightness/temperature from smooth curve data"""
        # Implementation for smooth curve interpolation
        # Returns interpolated brightness/temperature values
        pass
    
    @service
    def set_room_system(room: str, system_type: str):
        """Service call to set room's automation system preference"""
        controller = HierarchyController(hass)
        controller.set_room_system_preference(room, system_type)
```

#### **2. curve_generator.py:**
```python
"""
Smooth Curve Generation from Recording Sessions
Creates butter-smooth lighting curves from manual adjustment data
"""

import numpy as np
from scipy import interpolate
from scipy.signal import savgol_filter
import sqlite3
import json

class CurveGenerator:
    def __init__(self, hass):
        self.hass = hass
        self.db_path = "/config/als_database.db"
    
    @pyscript_executor
    def generate_curve_from_session(self, session_id: str):
        """Generate smooth curve from approved recording session data"""
        
        # Get approved data points
        approved_points = self.get_approved_data_points(session_id)
        
        if len(approved_points) < 3:
            raise ValueError("Need at least 3 approved points to generate curve")
        
        # Separate time and brightness data
        times = [point['timestamp'] for point in approved_points]
        brightness_values = [point['brightness'] for point in approved_points]
        temp_values = [point['temperature'] for point in approved_points if point['temperature']]
        
        # Generate smooth curves
        brightness_curve = self.create_smooth_curve(times, brightness_values)
        temperature_curve = self.create_smooth_curve(times, temp_values) if temp_values else None
        
        # Calculate quality metrics
        quality_score = self.calculate_curve_quality(brightness_curve, approved_points)
        
        # Store generated curve
        curve_data = {
            "brightness_curve": brightness_curve.tolist(),
            "temperature_curve": temperature_curve.tolist() if temperature_curve is not None else None,
            "time_points": times,
            "algorithm": "savgol_spline_hybrid",
            "quality_score": quality_score
        }
        
        self.store_generated_curve(session_id, curve_data)
        
        return curve_data
    
    def create_smooth_curve(self, times: list, values: list) -> np.ndarray:
        """Create smooth curve using Savitzky-Golay filter + spline interpolation"""
        
        # Convert times to minutes from start
        time_minutes = [(t - times[0]).total_seconds() / 60 for t in times]
        
        # Apply Savitzky-Golay filter for smoothing
        if len(values) >= 5:
            smoothed = savgol_filter(values, window_length=min(5, len(values)), polyorder=2)
        else:
            smoothed = np.array(values)
        
        # Create high-resolution time points for interpolation
        min_time, max_time = min(time_minutes), max(time_minutes)
        high_res_times = np.linspace(min_time, max_time, num=100)
        
        # Spline interpolation for smooth curve
        spline = interpolate.UnivariateSpline(time_minutes, smoothed, s=0, k=3)
        smooth_curve = spline(high_res_times)
        
        # Ensure values stay within reasonable bounds
        smooth_curve = np.clip(smooth_curve, 1, 100)
        
        return smooth_curve
    
    def calculate_curve_quality(self, curve: np.ndarray, original_points: list) -> float:
        """Calculate quality score for generated curve"""
        # Metrics: smoothness, deviation from originals, realistic values
        smoothness = self.calculate_smoothness(curve)
        deviation = self.calculate_deviation(curve, original_points)
        realism = self.calculate_realism(curve)
        
        # Weighted average
        quality = (smoothness * 0.4) + (deviation * 0.4) + (realism * 0.2)
        return min(max(quality, 0.0), 1.0)
    
    @service
    def approve_data_point(session_id: str, point_id: str):
        """Service to approve a data point for curve generation"""
        generator = CurveGenerator(hass)
        generator.approve_point(session_id, point_id)
    
    @service
    def reject_data_point(session_id: str, point_id: str):
        """Service to reject a data point from curve generation"""
        generator = CurveGenerator(hass)
        generator.reject_point(session_id, point_id)
```

### **Enhanced Database Schema:**
```sql
-- System Preferences Table
CREATE TABLE IF NOT EXISTS room_system_preferences (
    room TEXT PRIMARY KEY,
    system_type TEXT NOT NULL, -- manual, intelligent, learned, recorded
    fallback_enabled BOOLEAN DEFAULT TRUE,
    priority_override BOOLEAN DEFAULT FALSE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recording Sessions Enhancement
CREATE TABLE IF NOT EXISTS recorded_sessions (
    id TEXT PRIMARY KEY,
    session_name TEXT NOT NULL,
    room TEXT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status TEXT DEFAULT 'recording', -- recording, analyzing, completed, active
    data_points INTEGER DEFAULT 0,
    approved_points INTEGER DEFAULT 0,
    quality_score REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recording Data Points
CREATE TABLE IF NOT EXISTS recording_data_points (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    brightness INTEGER NOT NULL,
    temperature INTEGER,
    approved BOOLEAN DEFAULT FALSE,
    rejected BOOLEAN DEFAULT FALSE,
    confidence_score REAL DEFAULT 1.0,
    FOREIGN KEY (session_id) REFERENCES recorded_sessions(id)
);

-- Generated Smooth Curves
CREATE TABLE IF NOT EXISTS smooth_curves (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    curve_data TEXT NOT NULL, -- JSON blob
    algorithm_used TEXT NOT NULL,
    quality_score REAL NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES recorded_sessions(id)
);

-- System Performance Metrics
CREATE TABLE IF NOT EXISTS system_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room TEXT NOT NULL,
    system_used TEXT NOT NULL,
    confidence_score REAL,
    user_override BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔌 API ENDPOINTS SPECIFICATION

### **NEW Home Assistant Services:**

#### **System Management:**
```yaml
# /config/packages/00_als_hierarchy_system.yaml

pyscript:
  - service: set_room_system
    description: Set automation system type for a room
    fields:
      room:
        description: Room name
        example: "bedroom"
      system_type:
        description: System type (manual, intelligent, learned, recorded)
        example: "recorded"
  
  - service: get_room_system
    description: Get current system type for a room
    fields:
      room:
        description: Room name
        example: "bedroom"
  
  - service: get_system_status
    description: Get overall system status and metrics
```

#### **Recording Analysis:**
```yaml
  - service: get_session_details
    description: Get detailed data for a recording session
    fields:
      session_id:
        description: Recording session ID
        example: "bedroom_2025_09_03_001"
  
  - service: approve_data_point
    description: Approve a data point for curve generation
    fields:
      session_id:
        description: Recording session ID
      point_id:
        description: Data point ID
  
  - service: reject_data_point
    description: Reject a data point from curve generation
    fields:
      session_id:
        description: Recording session ID
      point_id:
        description: Data point ID
  
  - service: generate_curve
    description: Generate smooth curve from approved points
    fields:
      session_id:
        description: Recording session ID
  
  - service: activate_curve
    description: Make a generated curve active for automation
    fields:
      session_id:
        description: Recording session ID
      curve_id:
        description: Generated curve ID
```

---

## 🎯 IMPLEMENTATION ROADMAP

### **Phase 1: Foundation (Days 1-3)**
1. **iOS App System Selectors**
   - Add SystemType enum and UI components
   - Implement dropdown menus in ContentView
   - Add API calls for system preference setting

2. **Backend Hierarchy Controller**
   - Create hierarchy_controller.py
   - Implement basic decision tree logic
   - Add database tables for system preferences

3. **Basic Integration Testing**
   - Test system preference setting/getting
   - Verify hierarchy fallback logic
   - Ensure existing functionality still works

### **Phase 2: Recording Analysis (Days 4-7)**
1. **Recording Analysis UI**
   - Create RecordingAnalysisView
   - Implement timeline scrubber
   - Add approve/reject functionality

2. **Curve Generation Backend**
   - Create curve_generator.py
   - Implement smooth curve algorithms
   - Add curve quality scoring

3. **API Integration**
   - Connect iOS app to curve generation
   - Test data point approval workflow
   - Validate curve quality metrics

### **Phase 3: Production Ready (Days 8-14)**
1. **Performance Optimization**
   - Database query optimization
   - Memory usage optimization
   - Response time improvements

2. **Error Handling & Recovery**
   - Comprehensive error handling
   - Fallback mechanisms
   - Recovery from corrupted data

3. **User Experience Polish**
   - Loading states and progress indicators
   - Better error messages
   - Intuitive UI/UX improvements

---

## 🧪 TESTING STRATEGY

### **Unit Testing:**
```swift
// iOS App Tests
class SystemHierarchyTests: XCTestCase {
    func testSystemTypeSelection() { }
    func testHierarchyFallback() { }
    func testAPIIntegration() { }
}

class RecordingAnalysisTests: XCTestCase {
    func testDataPointApproval() { }
    func testCurveGeneration() { }
    func testQualityScoring() { }
}
```

### **Integration Testing:**
- End-to-end recording session workflow
- System preference persistence
- API error handling
- Database integrity checks

### **Performance Testing:**
- Large recording session handling
- Multiple concurrent users
- Database performance under load
- Memory usage optimization

---

## 📊 MONITORING & METRICS

### **Key Performance Indicators:**
- System response time (< 200ms target)
- Curve generation accuracy (> 90% user satisfaction)
- System uptime (> 99.5%)
- Error rate (< 1% of operations)

### **Logging Strategy:**
```python
# Structured logging for debugging
logger.info("hierarchy_decision", {
    "room": room,
    "system_type": system_type,
    "source": source,
    "confidence": confidence,
    "fallback_used": fallback_used
})
```

---

**Document Version:** 2.0  
**Last Updated:** September 3, 2025  
**Next Review:** Weekly during development phase