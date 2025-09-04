# 🚀 ALS Quick Reference & Development Checklist
**Start Here** - Essential commands, file locations, and development workflow

---

## 🎯 PROJECT SUMMARY (30-Second Overview)

You have built an **Advanced Smart Lighting System (ALS)** with:

### **✅ What's Already Working:**
- **iOS SwiftUI App** (ContentView.swift + RoomDetailView.swift)
- **Home Assistant Integration** (18+ YAML packages, PyScript services)
- **Teaching Mode** (manual brightness/temperature input)
- **Basic Ramp Recording** (session capture and storage)
- **Adaptive Learning** (weather + time awareness)
- **7 Configured Rooms** with different capabilities

### **🔥 What We're Adding NOW:**
- **Three-Tier Hierarchy System:** Recorded → Learned → Intelligent → Manual
- **Per-Room System Selectors** (dropdown in iOS app)
- **Interactive Recording Analysis** (approve/reject data points)
- **Smooth Curve Generation** (from manual adjustments)
- **System Performance Dashboard**

---

## 📂 KEY FILES & LOCATIONS

### **iOS App Files (SwiftUI):**
```
📁 Smart Light Teaching App/
├── ContentView.swift (Main room list - NEEDS SYSTEM SELECTORS)
├── RoomDetailView.swift (Teaching/recording - NEEDS ENHANCEMENT)  
├── Smart_Light_TeachingApp.swift (App entry point - OK as-is)
└── NEW FILES TO CREATE:
    ├── Models/Room.swift (SystemType enum)
    ├── Views/SystemSelectorView.swift
    ├── Views/RecordingAnalysisView.swift
    └── API/HomeAssistantAPI+Extensions.swift
```

### **Home Assistant Files:**
```
📁 /config/
├── packages/ (18+ existing YAML files - keep as-is)
├── pyscript/ (existing Python services - keep)
└── NEW PYSCRIPT FILES TO CREATE:
    ├── hierarchy_controller.py (CRITICAL - main decision engine)
    ├── curve_generator.py (smooth curve algorithms)
    └── recording_analyzer.py (data point approval system)
```

### **Database Location:**
```
📁 /config/
└── als_database.db (existing - will add new tables)
```

---

## ⚡ DEVELOPMENT WORKFLOW (Start Here)

### **STEP 1: Setup Development Environment**
```bash
# 1. Open Xcode with your Swift project
open "Smart Light Teaching.xcodeproj"

# 2. Backup your Home Assistant config
cd /Users/frank/home-assistant-project
cp -r . ~/Desktop/ha_backup_$(date +%Y%m%d)

# 3. Test current system works before changes
# (Use your iOS app to verify teaching/recording still works)
```

### **STEP 2: Phase 1 - iOS System Selectors (Days 1-2)**
```swift
// Priority order for iOS development:
1. Create Models/Room.swift (SystemType enum)
2. Create Views/SystemSelectorView.swift  
3. Update ContentView.swift (add system display)
4. Update RoomDetailView.swift (add system selector)
5. Extend HomeAssistantAPI.swift (setRoomSystemType)
6. Test system selection and API calls
```

### **STEP 3: Phase 2 - PyScript Hierarchy (Days 2-3)**
```python
# Priority order for PyScript development:
1. Create pyscript/hierarchy_controller.py
2. Add new database tables (room_system_preferences)
3. Create Home Assistant service definitions
4. Test hierarchy decision logic
5. Integrate with existing sensors/automations
6. Validate fallback mechanisms work
```

### **STEP 4: Phase 3 - Recording Analysis (Days 4-6)**
```swift
# Priority order for recording enhancement:
1. Create Views/RecordingAnalysisView.swift
2. Extend API for session details and data point approval
3. Create pyscript/curve_generator.py
4. Test curve generation algorithms
5. Integrate with recording workflow
6. Validate curve quality and activation
```

---

## 🔧 ESSENTIAL COMMANDS

### **iOS Development:**
```bash
# Test iOS app on simulator
open -a Simulator
# Then build and run in Xcode (⌘R)

# Check iOS app logs
# In Xcode: View → Debug Area → Activate Console
```

### **Home Assistant Development:**
```bash
# Restart Home Assistant after PyScript changes
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  http://192.168.10.153:8123/api/services/homeassistant/restart

# Check Home Assistant logs
tail -f /config/home-assistant.log | grep -i "als\|pyscript\|error"

# Test PyScript service calls
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"room": "bedroom", "system_type": "learned"}' \
  http://192.168.10.153:8123/api/services/pyscript/set_room_system
```

### **Database Operations:**
```bash
# Connect to SQLite database
sqlite3 /config/als_database.db

# Useful queries for debugging
.tables
SELECT * FROM room_system_preferences;
SELECT * FROM recorded_sessions ORDER BY start_time DESC LIMIT 5;
SELECT * FROM hierarchy_decisions ORDER BY timestamp DESC LIMIT 10;
```

---

## 🎯 DAILY DEVELOPMENT CHECKLIST

### **Each Development Session:**
- [ ] **Backup current working state** before major changes
- [ ] **Test existing functionality** still works after changes  
- [ ] **Commit code changes** to version control (git)
- [ ] **Document any new API endpoints** or data structures
- [ ] **Update this checklist** with progress and blockers

### **Before Testing:**
- [ ] **iOS app builds** without errors in Xcode
- [ ] **Home Assistant restarts** successfully after PyScript changes
- [ ] **Database schema** updates applied correctly
- [ ] **No error logs** appearing in Home Assistant logs
- [ ] **Existing sensors** still updating with current data

### **Before Committing Changes:**
- [ ] **All rooms respond** to system selector changes
- [ ] **Hierarchy fallback** works when systems fail
- [ ] **Recording sessions** can still be created and stopped
- [ ] **Teaching mode** continues to work as expected
- [ ] **No crashes** in iOS app under normal usage

---

## 🚨 TROUBLESHOOTING GUIDE

### **iOS App Issues:**
```
❌ App crashes when changing system type
✅ Check HomeAssistantAPI.setRoomSystemType implementation
✅ Verify API URL and authorization token
✅ Add error handling and user feedback

❌ System selector not showing all options  
✅ Check Room.availableSystemTypes logic
✅ Verify hasRecordedData property is set correctly
✅ Confirm SystemType enum cases match backend

❌ UI not updating after API calls
✅ Ensure @State variables are being updated
✅ Add Task { await MainActor.run { ... } } for UI updates
✅ Check for proper SwiftUI binding usage
```

### **Home Assistant Issues:**
```
❌ PyScript service not found
✅ Check service is defined in packages/*.yaml
✅ Verify pyscript file is in /config/pyscript/
✅ Restart Home Assistant after changes

❌ Database errors in hierarchy controller
✅ Check database file permissions
✅ Verify table creation in initialize_database()
✅ Test SQLite queries manually first

❌ Hierarchy decisions not working
✅ Check existing sensor entities are still active
✅ Verify system preference is being saved/loaded
✅ Test each tier of hierarchy independently
```

### **Integration Issues:**
```
❌ iOS app can't connect to Home Assistant
✅ Check IP address (192.168.10.153:8123)
✅ Verify Bearer token is valid and not expired
✅ Test API endpoints with curl first

❌ System changes not persisting
✅ Check database write operations complete
✅ Verify room name formatting matches (lowercase, underscores)
✅ Test database queries return expected results

❌ Recording analysis not loading data
✅ Check session_id format and existence
✅ Verify database foreign key relationships
✅ Test API endpoints return proper JSON structure
```

---

## 📊 SUCCESS VALIDATION CHECKLIST

### **Phase 1 Success (System Selectors):**
- [ ] Every room shows current system type with correct icon
- [ ] Dropdown allows changing between available systems
- [ ] "Recorded" option appears only when recorded data exists
- [ ] System changes save to database and persist after app restart
- [ ] API calls complete in < 1 second with proper error handling

### **Phase 2 Success (Hierarchy Backend):**
- [ ] Hierarchy controller makes decisions in < 200ms
- [ ] Fallback to lower-tier systems works automatically
- [ ] All decisions logged to database with proper metadata  
- [ ] Existing learning and intelligent systems still function
- [ ] No degradation in lighting quality or responsiveness

### **Phase 3 Success (Recording Analysis):**
- [ ] Recording session data loads in interactive timeline
- [ ] Data point approval/rejection updates database correctly
- [ ] Curve generation produces smooth, realistic curves
- [ ] Generated curves can be activated and used for automation
- [ ] Curve quality scores correlate with user satisfaction

### **Overall System Success:**
- [ ] **User Experience:** Lighting feels seamless and intuitive
- [ ] **Performance:** All operations complete within time targets
- [ ] **Reliability:** System degrades gracefully, never fails completely
- [ ] **Flexibility:** Users can override any automation easily
- [ ] **Learning:** System improves over time with usage

---

## 🎉 QUICK WINS (Easy Tasks to Build Momentum)

### **Day 1 Quick Wins:**
- [ ] Add SystemType enum to iOS app (30 minutes)
- [ ] Update room list to show current system type (45 minutes)
- [ ] Create basic system selector UI component (1 hour)
- [ ] Add database table for room preferences (30 minutes)

### **Day 2 Quick Wins:**  
- [ ] Connect system selector to API call (1 hour)
- [ ] Test system preference saving/loading (30 minutes)
- [ ] Add system status to room detail view (45 minutes)
- [ ] Create basic hierarchy controller structure (1 hour)

### **Day 3 Quick Wins:**
- [ ] Implement basic hierarchy decision logic (1.5 hours)
- [ ] Test fallback between system tiers (1 hour)
- [ ] Add logging for hierarchy decisions (30 minutes)
- [ ] Validate existing functionality still works (30 minutes)

---

## 💡 KEY REMINDERS

### **Architecture Principles:**
- **Never break existing functionality** - all current features must keep working
- **Fail gracefully** - always have a fallback that produces reasonable lighting
- **User control first** - users can override any system at any time
- **Performance matters** - lighting decisions must be fast and responsive

### **Development Best Practices:**
- **Test incrementally** - verify each small change before moving to next
- **Use version control** - commit working states frequently  
- **Document as you go** - update these files with discoveries and changes
- **Keep it simple** - complex solutions are harder to debug and maintain

### **When Stuck:**
1. **Step back** to last known working state
2. **Test one small thing** at a time
3. **Check logs** for specific error messages
4. **Verify assumptions** about data formats and API responses
5. **Ask for help** - share specific error messages and context

---

**Quick Reference Version:** 1.0  
**Last Updated:** September 3, 2025  
**Status:** Ready to start development  
**First Task:** Create SystemType enum in iOS app