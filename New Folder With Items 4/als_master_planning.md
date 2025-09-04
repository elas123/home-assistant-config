# 🏠 ALS Smart Lighting System - Master Planning Document
**Date Created:** September 3, 2025  
**System Status:** Advanced Development Phase  
**Current Focus:** Three-Tier Hierarchy + Recording System Implementation

---

## 📋 CURRENT SYSTEM OVERVIEW

### ✅ **What's Already Built & Working:**
- **18+ Home Assistant Configuration Packages**
- **Complete PyScript Backend** with SQLite integration
- **iOS Swift App** with Teaching Mode & Basic Ramp Recording
- **Adaptive Learning System** (weather + time + season awareness)
- **Morning Ramp System** with routine learning
- **Multi-room Intelligence** (6 rooms fully configured)
- **Diagnostic & Health Monitoring** with error tracking
- **Automated Maintenance System**

### 🎯 **Core Architecture Components:**
```
📱 SwiftUI iOS App → 🏠 Home Assistant → 🐍 PyScript → 🗄️ SQLite Database
```

---

## 🚀 NEW THREE-TIER LIGHTING HIERARCHY

### **Priority System Architecture:**
```
1. 🎬 RECORDED DATA     (Smooth curves from manual session analysis)
2. 🧠 LEARNED DATA      (Statistical learning from usage patterns)  
3. 📊 INTELLIGENT DATA  (Weather/time calculations)
4. 🎛️ MANUAL FALLBACK   (Direct user control)
```

### **iOS App Master Controller:**
Each room gets a **system selector dropdown**:
```
Bedroom:     [Recorded Ramp ▼]
Kitchen:     [Intelligent   ▼] 
Living Room: [Learned       ▼]
Bathroom:    [Manual        ▼]
```

---

## 🎯 IMMEDIATE TO-DO LIST (Priority Order)

### **🔥 CRITICAL - Phase 1 (Next 2-3 Days)**
1. **Complete iOS System Selector Interface**
   - [ ] Add dropdown to each room in ContentView
   - [ ] Create SystemType enum (Recorded, Learned, Intelligent, Manual)
   - [ ] Add API calls to update room system preferences
   - [ ] Store system selections in Home Assistant

2. **Finish Recording Analysis Frontend**
   - [ ] Create interactive data point approval interface
   - [ ] Add smooth curve generation visualization
   - [ ] Implement approve/reject functionality
   - [ ] Create recording session management screen

3. **Build PyScript Hierarchy Controller**
   - [ ] Create system priority decision logic
   - [ ] Add hierarchy override functionality
   - [ ] Implement recorded data integration
   - [ ] Add system fallback mechanisms

### **🟡 HIGH PRIORITY - Phase 2 (1-2 Weeks)**
4. **Recording System Enhancements**
   - [ ] 2-3 hour session capture optimization
   - [ ] Advanced data point filtering
   - [ ] Curve smoothing algorithms
   - [ ] Session quality scoring

5. **iOS App Feature Completion**
   - [ ] Real-time system switching
   - [ ] Recording session analytics
   - [ ] System performance metrics
   - [ ] Error handling improvements

6. **Backend Integration**
   - [ ] Recorded data storage system
   - [ ] System preference persistence
   - [ ] Performance monitoring
   - [ ] Backup/restore functionality

### **🔵 MEDIUM PRIORITY - Phase 3 (2-4 Weeks)**
7. **Advanced Features**
   - [ ] Multi-day recording sessions
   - [ ] Pattern recognition improvements
   - [ ] Cross-room learning
   - [ ] Seasonal adaptation enhancements

8. **Documentation & Testing**
   - [ ] Complete system documentation
   - [ ] User guides and setup instructions
   - [ ] Automated testing suite
   - [ ] Performance benchmarks

---

## 🏗️ TECHNICAL ARCHITECTURE DETAILS

### **Current File Structure:**
```
📁 iOS App (SwiftUI)
├── ContentView.swift (Room list & navigation)
├── RoomDetailView.swift (Teaching & recording modes)
├── Smart_Light_TeachingApp.swift (App entry point)
└── Models & API (HomeAssistantAPI)

📁 Home Assistant Integration
├── 18+ YAML configuration packages
├── PyScript services (als_teach_room, start_ramp_recording, etc.)
├── SQLite database integration
├── Sensor entities for each room
└── Automation triggers and conditions
```

### **API Integration Points:**
- `teachRoom()` - Send manual settings to learning system
- `startRampRecording()` - Begin session recording
- `stopRampRecording()` - End session and store data
- `fetchEntityState()` - Get current room brightness/temperature
- `getRampSessions()` - Retrieve historical sessions

### **Database Schema (Planned):**
```sql
-- System Preferences
rooms_system_settings (room, system_type, priority, enabled)

-- Recorded Data
recorded_sessions (id, room, session_name, start_time, end_time, data_points, quality_score)
recorded_data_points (session_id, timestamp, brightness, temperature, approved)

-- Generated Curves
smooth_curves (session_id, curve_data, algorithm_used, confidence_score)
```

---

## 🎬 RECORDING SYSTEM DETAILS

### **Current Recording Flow:**
1. User enters session name
2. App calls `startRampRecording()` API
3. Manual light adjustments are captured
4. User stops recording when satisfied
5. Data stored in Home Assistant/SQLite

### **Planned Enhancement Flow:**
1. **Extended Recording** (2-3 hours automatic)
2. **Interactive Analysis** (approve/reject data points)
3. **Curve Generation** (smooth interpolation algorithms)
4. **Quality Assessment** (scoring system for session quality)
5. **Integration** (becomes "Recorded Data" tier)

### **Recording Analysis Interface (To Build):**
- Timeline scrubber for recorded data
- Individual data point approve/reject buttons
- Real-time curve preview
- Quality metrics display
- Export options for final curve data

---

## 🧠 LEARNING SYSTEM INTEGRATION

### **How Systems Will Interact:**
```python
def get_room_brightness(room, current_time):
    system_type = get_room_system_preference(room)
    
    if system_type == "recorded" and has_recorded_data(room, current_time):
        return get_recorded_brightness(room, current_time)
    elif system_type == "learned" and has_learning_data(room):
        return get_learned_brightness(room, current_time)
    elif system_type == "intelligent":
        return get_intelligent_brightness(room, current_time)
    else:
        return get_manual_fallback(room)
```

### **Fallback Hierarchy Logic:**
- **Recorded** → Learned → Intelligent → Manual
- **Learned** → Intelligent → Manual
- **Intelligent** → Manual
- **Manual** → No fallback (user control)

---

## 📱 iOS APP ENHANCEMENTS NEEDED

### **New UI Components:**
1. **System Selector Dropdown** (per room)
2. **Recording Analysis Screen** (interactive timeline)
3. **System Performance Dashboard** (metrics & status)
4. **Settings & Configuration** (global preferences)

### **New API Endpoints Needed:**
```swift
// System Management
setRoomSystemType(_ room: String, systemType: SystemType)
getRoomSystemType(_ room: String) -> SystemType
getRoomSystemStatus(_ room: String) -> SystemStatus

// Recording Analysis
getRecordingSessionData(_ sessionId: String) -> RecordingData
approveDataPoint(_ sessionId: String, pointId: String)
rejectDataPoint(_ sessionId: String, pointId: String)
generateCurveFromSession(_ sessionId: String) -> CurveData

// Performance Monitoring
getSystemMetrics() -> SystemMetrics
getRoomPerformance(_ room: String) -> RoomMetrics
```

---

## 🔧 DEVELOPMENT ENVIRONMENT SETUP

### **Required Tools:**
- Xcode (iOS development)
- Home Assistant instance with PyScript
- SQLite browser for database debugging
- Git for version control
- Claude Code for assisted development

### **Testing Strategy:**
1. **Unit Tests** - Individual component testing
2. **Integration Tests** - API and database interactions
3. **User Testing** - Real-world usage scenarios
4. **Performance Testing** - System load and response times

---

## 📊 SUCCESS METRICS

### **Phase 1 Success Criteria:**
- [ ] All rooms have working system selectors
- [ ] Recording analysis interface is functional
- [ ] Hierarchy decision logic works correctly
- [ ] No existing functionality is broken

### **Full System Success Criteria:**
- [ ] Smooth, seamless lighting automation
- [ ] User can easily override any system
- [ ] Recording sessions produce high-quality curves
- [ ] System learns and adapts over time
- [ ] Minimal user intervention required for daily use

---

## 🚨 RISKS & MITIGATION

### **Technical Risks:**
- **Database corruption** → Regular backups, validation checks
- **API failures** → Robust error handling, retry logic
- **Performance degradation** → Monitoring, optimization
- **iOS app crashes** → Comprehensive testing, error catching

### **User Experience Risks:**
- **Complex interface** → Simplified UI, clear instructions
- **System conflicts** → Clear hierarchy, override options
- **Learning accuracy** → Quality metrics, manual correction

---

## 💡 FUTURE ENHANCEMENTS (Post-Launch)

### **Advanced Features:**
- Voice control integration (Siri shortcuts)
- Apple Watch companion app
- Multi-home support
- Cloud synchronization
- Community sharing of lighting curves
- AI-powered optimization suggestions
- Integration with other smart home systems

### **Machine Learning Improvements:**
- Advanced pattern recognition
- Predictive lighting adjustments
- Cross-room behavior learning
- Seasonal adaptation algorithms
- User preference prediction

---

**Last Updated:** September 3, 2025  
**Next Review:** Daily during active development  
**Status:** Living document - update as development progresses