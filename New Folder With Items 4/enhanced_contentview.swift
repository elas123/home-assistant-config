import SwiftUI

// MARK: - Data Models
struct Room: Identifiable {
    let id = UUID()
    let name: String
    let icon: String
    let brightnessEntity: String
    let temperatureEntity: String
    let supportsTemperature: Bool
    var brightness: Int = 0
    var temperature: Int = 3000
}

struct RampSession: Identifiable, Codable {
    let id: String
    let sessionName: String
    let startTime: String
    let endTime: String?
    let room: String
    let status: String
    let dataPoints: Int
}

struct EntityState: Codable {
    let state: String
    let attributes: [String: AnyCodable]?
}

struct AnyCodable: Codable {
    let value: Any
    
    init<T>(_ value: T?) {
        self.value = value ?? ()
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if let intVal = try? container.decode(Int.self) {
            value = intVal
        } else if let stringVal = try? container.decode(String.self) {
            value = stringVal
        } else {
            value = ()
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        try container.encode(String(describing: value))
    }
}

// MARK: - API Service
struct HomeAssistantAPI {
    static let baseURL = "http://192.168.10.153:8123"
    static let token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIxZjE1MGVlMjc0ODc0YTVhOWQ2MzBmZjZhMTA3NDA3ZCIsImlhdCI6MTc1NjkzODk2MSwiZXhwIjoyMDcyMjk4OTYxfQ.O5UTmlzju3JaMhbK-Y2VlKoOlgWq4vSwhoj7QYnraNE"
    
    static func teachRoom(_ room: String, brightness: Int, temperature: Int?) async throws {
        let url = URL(string: "\(baseURL)/api/services/pyscript/als_teach_room")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        var serviceData: [String: Any] = [
            "room": room,
            "brightness": brightness
        ]
        if let temp = temperature {
            serviceData["temperature"] = temp
        }
        
        request.httpBody = try JSONSerialization.data(withJSONObject: serviceData)
        let (_, response) = try await URLSession.shared.data(for: request)
        
        // Check if response is successful
        if let httpResponse = response as? HTTPURLResponse {
            print("Teach Room Response: \(httpResponse.statusCode)")
        }
    }
    
    static func startRampRecording(_ room: String, sessionName: String) async throws {
        let url = URL(string: "\(baseURL)/api/services/pyscript/start_ramp_recording")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let serviceData: [String: Any] = [
            "room": room,
            "session_name": sessionName
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: serviceData)
        let (_, response) = try await URLSession.shared.data(for: request)
        
        if let httpResponse = response as? HTTPURLResponse {
            print("Start Recording Response: \(httpResponse.statusCode)")
        }
    }
    
    static func stopRampRecording(_ room: String) async throws {
        let url = URL(string: "\(baseURL)/api/services/pyscript/stop_ramp_recording")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let serviceData: [String: Any] = [
            "room": room
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: serviceData)
        let (_, response) = try await URLSession.shared.data(for: request)
        
        if let httpResponse = response as? HTTPURLResponse {
            print("Stop Recording Response: \(httpResponse.statusCode)")
        }
    }
    
    static func fetchEntityState(_ entityId: String) async throws -> EntityState {
        let url = URL(string: "\(baseURL)/api/states/\(entityId)")!
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode != 200 {
            throw NSError(domain: "APIError", code: httpResponse.statusCode, userInfo: [NSLocalizedDescriptionKey: "HTTP \(httpResponse.statusCode)"])
        }
        
        return try JSONDecoder().decode(EntityState.self, from: data)
    }
    
    static func getRampSessions(_ room: String) async throws -> [RampSession] {
        let url = URL(string: "\(baseURL)/api/services/pyscript/get_ramp_sessions")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let serviceData: [String: Any] = [
            "room": room
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: serviceData)
        let (data, response) = try await URLSession.shared.data(for: request)
        
        if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode != 200 {
            // If service doesn't exist yet, return empty array
            return []
        }
        
        struct Response: Codable {
            let sessions: [RampSession]
        }
        
        do {
            let response = try JSONDecoder().decode(Response.self, from: data)
            return response.sessions
        } catch {
            // If decode fails, return empty array for now
            return []
        }
    }
    
    // MARK: - New functionality for system status
    static func getSystemStatus() async throws -> [String: Any] {
        let url = URL(string: "\(baseURL)/api/states")!
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, _) = try await URLSession.shared.data(for: request)
        
        if let states = try? JSONSerialization.jsonObject(with: data) as? [[String: Any]] {
            var systemInfo: [String: Any] = [:]
            
            // Check key system entities
            for state in states {
                if let entityId = state["entity_id"] as? String {
                    if entityId.contains("adaptive_learning") || 
                       entityId.contains("intelligent_lighting") ||
                       entityId.contains("als_") {
                        systemInfo[entityId] = state["state"]
                    }
                }
            }
            
            return systemInfo
        }
        
        return [:]
    }
}

// MARK: - Views
struct ContentView: View {
    @State private var rooms: [Room] = [
        Room(name: "Bedroom", icon: "bed.double.fill", 
             brightnessEntity: "sensor.bedroom_intelligent_brightness",
             temperatureEntity: "sensor.intelligent_temperature_bedroom",
             supportsTemperature: true),
        Room(name: "Living Room", icon: "sofa.fill",
             brightnessEntity: "sensor.living_room_target_brightness", 
             temperatureEntity: "sensor.intelligent_temperature_living_room",
             supportsTemperature: true),
        Room(name: "Kitchen", icon: "fork.knife",
             brightnessEntity: "sensor.kitchen_target_brightness",
             temperatureEntity: "sensor.intelligent_temperature_master",
             supportsTemperature: false),
        Room(name: "Bathroom", icon: "bathtub.fill",
             brightnessEntity: "sensor.bathroom_target_brightness",
             temperatureEntity: "sensor.intelligent_temperature_master",
             supportsTemperature: false),
        Room(name: "Hallway", icon: "lightbulb.fill",
             brightnessEntity: "sensor.hallway_target_brightness",
             temperatureEntity: "sensor.intelligent_temperature_master",
             supportsTemperature: false),
        Room(name: "Laundry", icon: "washer.fill",
             brightnessEntity: "sensor.laundry_room_target_brightness",
             temperatureEntity: "sensor.intelligent_temperature_master",
             supportsTemperature: false)
    ]
    
    @State private var systemStatus: String = "Checking..."
    @State private var lastRefresh: Date = Date()
    
    var body: some View {
        NavigationView {
            VStack {
                // System Status Header
                VStack(spacing: 8) {
                    HStack {
                        Image(systemName: "brain")
                            .foregroundColor(.blue)
                        Text("ALS System Status")
                            .font(.headline)
                        Spacer()
                        Button(action: { Task { await refreshSystemStatus() } }) {
                            Image(systemName: "arrow.clockwise")
                                .foregroundColor(.blue)
                        }
                    }
                    
                    HStack {
                        Text(systemStatus)
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Spacer()
                        Text("Updated: \(lastRefresh, formatter: timeFormatter)")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                }
                .padding()
                .background(Color(.systemGray6))
                .cornerRadius(12)
                .padding(.horizontal)
                
                // Room List
                List(rooms) { room in
                    NavigationLink(destination: RoomDetailView(room: room)) {
                        HStack {
                            Image(systemName: room.icon)
                                .foregroundColor(.blue)
                                .frame(width: 30)
                            
                            VStack(alignment: .leading) {
                                Text(room.name)
                                    .font(.headline)
                                    .foregroundColor(.primary)
                                Text(room.supportsTemperature ? "\(room.brightness)% • \(room.temperature)K" : "\(room.brightness)%")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                            
                            Spacer()
                        }
                        .padding(.vertical, 4)
                    }
                }
            }
            .navigationTitle("Smart Lighting")
            .preferredColorScheme(.dark)
            .onAppear {
                Task {
                    await refreshSystemStatus()
                    await refreshRoomData()
                }
            }
        }
    }
    
    private func refreshSystemStatus() async {
        do {
            let status = try await HomeAssistantAPI.getSystemStatus()
            
            DispatchQueue.main.async {
                let adaptiveLearning = status["input_boolean.adaptive_learning_enabled"] as? String == "on"
                let intelligentLighting = status["input_boolean.intelligent_lighting_enable"] as? String == "on"
                
                if adaptiveLearning && intelligentLighting {
                    systemStatus = "🧠 Full System Active"
                } else if adaptiveLearning {
                    systemStatus = "📚 Learning Only"
                } else if intelligentLighting {
                    systemStatus = "💡 Intelligent Only"
                } else {
                    systemStatus = "⏸️ Manual Mode"
                }
                
                lastRefresh = Date()
            }
        } catch {
            DispatchQueue.main.async {
                systemStatus = "❌ Connection Error"
                lastRefresh = Date()
            }
        }
    }
    
    private func refreshRoomData() async {
        for (index, room) in rooms.enumerated() {
            do {
                let brightnessState = try await HomeAssistantAPI.fetchEntityState(room.brightnessEntity)
                let brightness = Int(brightnessState.state) ?? 0
                
                var temperature = 3000
                if room.supportsTemperature {
                    let tempState = try await HomeAssistantAPI.fetchEntityState(room.temperatureEntity)
                    temperature = Int(tempState.state) ?? 3000
                }
                
                DispatchQueue.main.async {
                    rooms[index].brightness = brightness
                    rooms[index].temperature = temperature
                }
            } catch {
                print("Error fetching data for \(room.name): \(error)")
            }
        }
    }
}

struct RoomDetailView: View {
    let room: Room
    @State private var teachingMode = false
    @State private var rampRecordingMode = false
    @State private var brightness: Double = 50
    @State private var temperature: Double = 3000
    @State private var sessionName: String = ""
    @State private var isRecording = false
    @State private var recordingStartTime: Date?
    @State private var rampSessions: [RampSession] = []
    @State private var showingSessions = false
    @State private var currentBrightness: Int = 0
    @State private var currentTemperature: Int = 3000
    @State private var showingAlert = false
    @State private var alertMessage = ""
    @State private var isLoading = false
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Current Settings Section (keeping existing style)
                VStack(alignment: .leading, spacing: 16) {
                    Text("Current Settings")
                        .font(.headline)
                    
                    HStack {
                        Image(systemName: "sun.max.fill")
                            .foregroundColor(.orange)
                        Text("Brightness: \(currentBrightness)%")
                        Spacer()
                        
                        Button(action: { Task { await refreshData() } }) {
                            if isLoading {
                                ProgressView()
                                    .scaleEffect(0.7)
                            } else {
                                Image(systemName: "arrow.clockwise")
                                    .foregroundColor(.blue)
                            }
                        }
                        .disabled(isLoading)
                    }
                    
                    if room.supportsTemperature {
                        HStack {
                            Image(systemName: "thermometer")
                                .foregroundColor(.blue)
                            Text("Temperature: \(currentTemperature)K")
                            Spacer()
                        }
                    }
                }
                .padding()
                .background(Color(.systemGray6))
                .cornerRadius(12)
                
                // Mode Toggles (keeping existing style)
                VStack(spacing: 12) {
                    Toggle("Teaching Mode", isOn: $teachingMode)
                        .padding()
                        .background(Color(.systemGray6))
                        .cornerRadius(12)
                    
                    Toggle("Ramp Recording Mode", isOn: $rampRecordingMode)
                        .padding()
                        .background(Color(.systemGray6))
                        .cornerRadius(12)
                }
                
                // Teaching Mode Section (keeping existing style)
                if teachingMode {
                    VStack(alignment: .leading, spacing: 20) {
                        Text("Teach New Settings")
                            .font(.headline)
                        
                        VStack(alignment: .leading) {
                            Text("Brightness: \(Int(brightness))%")
                            Slider(value: $brightness, in: 1...100, step: 1)
                        }
                        
                        if room.supportsTemperature {
                            VStack(alignment: .leading) {
                                Text("Temperature: \(Int(temperature))K")
                                Slider(value: $temperature, in: 2000...6500, step: 100)
                            }
                        }
                        
                        Button("Teach This Setting") {
                            Task {
                                await teachCurrentSetting()
                            }
                        }
                        .buttonStyle(.borderedProminent)
                        .frame(maxWidth: .infinity)
                        .disabled(isLoading)
                    }
                    .padding()
                    .background(Color(.systemBlue).opacity(0.1))
                    .cornerRadius(12)
                }
                
                // Ramp Recording Section (keeping existing style)
                if rampRecordingMode {
                    VStack(alignment: .leading, spacing: 20) {
                        Text("Ramp Recording")
                            .font(.headline)
                        
                        if !isRecording {
                            VStack(alignment: .leading, spacing: 12) {
                                Text("Session Name")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                                
                                TextField("Enter session name", text: $sessionName)
                                    .textFieldStyle(RoundedBorderTextFieldStyle())
                                
                                Button("Start Recording") {
                                    Task {
                                        await startRecording()
                                    }
                                }
                                .buttonStyle(.borderedProminent)
                                .frame(maxWidth: .infinity)
                                .disabled(sessionName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || isLoading)
                            }
                            
                            Button("View Past Sessions") {
                                Task {
                                    await loadRampSessions()
                                }
                                showingSessions = true
                            }
                            .buttonStyle(.bordered)
                            .frame(maxWidth: .infinity)
                            
                        } else {
                            VStack(alignment: .leading, spacing: 12) {
                                HStack {
                                    Image(systemName: "record.circle.fill")
                                        .foregroundColor(.red)
                                    Text("Recording: \(sessionName)")
                                        .font(.headline)
                                }
                                
                                if let startTime = recordingStartTime {
                                    Text("Started: \(DateFormatter.localizedString(from: startTime, dateStyle: .none, timeStyle: .medium))")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                }
                                
                                Text("Manually adjust your lights now. All brightness changes will be recorded for seamless automation.")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                                    .multilineTextAlignment(.leading)
                                
                                Button("Stop Recording") {
                                    Task {
                                        await stopRecording()
                                    }
                                }
                                .buttonStyle(.borderedProminent)
                                .frame(maxWidth: .infinity)
                                .disabled(isLoading)
                            }
                        }
                    }
                    .padding()
                    .background(Color(.systemRed).opacity(0.1))
                    .cornerRadius(12)
                }
            }
            .padding()
        }
        .navigationTitle(room.name)
        .navigationBarTitleDisplayMode(.inline)
        .onAppear {
            brightness = Double(currentBrightness)
            temperature = Double(currentTemperature)
            Task {
                await refreshData()
            }
        }
        .sheet(isPresented: $showingSessions) {
            RampSessionsView(room: room, sessions: $rampSessions)
        }
        .alert("System Message", isPresented: $showingAlert) {
            Button("OK") { }
        } message: {
            Text(alertMessage)
        }
    }
    
    // MARK: - Enhanced Functions
    func refreshData() async {
        DispatchQueue.main.async { isLoading = true }
        
        do {
            let brightnessState = try await HomeAssistantAPI.fetchEntityState(room.brightnessEntity)
            if let brightnessValue = Int(brightnessState.state) {
                DispatchQueue.main.async {
                    currentBrightness = brightnessValue
                    brightness = Double(brightnessValue)
                }
            }
            
            if room.supportsTemperature {
                let tempState = try await HomeAssistantAPI.fetchEntityState(room.temperatureEntity)
                if let tempValue = Int(tempState.state) {
                    DispatchQueue.main.async {
                        currentTemperature = tempValue
                        temperature = Double(tempValue)
                    }
                }
            }
        } catch {
            DispatchQueue.main.async {
                alertMessage = "Failed to refresh data: \(error.localizedDescription)"
                showingAlert = true
            }
        }
        
        DispatchQueue.main.async { isLoading = false }
    }
    
    func teachCurrentSetting() async {
        DispatchQueue.main.async { isLoading = true }
        
        do {
            let roomKey = room.name.lowercased().replacingOccurrences(of: " ", with: "_")
            let temp = room.supportsTemperature ? Int(temperature) : nil
            
            try await HomeAssistantAPI.teachRoom(roomKey, brightness: Int(brightness), temperature: temp)
            
            DispatchQueue.main.async {
                alertMessage = "Successfully taught \(room.name): \(Int(brightness))%"
                if let temp = temp {
                    alertMessage += " at \(temp)K"
                }
                showingAlert = true
                teachingMode = false
            }
            
            // Refresh data to see the change
            await refreshData()
        } catch {
            DispatchQueue.main.async {
                alertMessage = "Failed to teach setting: \(error.localizedDescription)"
                showingAlert = true
            }
        }
        
        DispatchQueue.main.async { isLoading = false }
    }
    
    func startRecording() async {
        DispatchQueue.main.async { isLoading = true }
        
        do {
            let roomKey = room.name.lowercased().replacingOccurrences(of: " ", with: "_")
            try await HomeAssistantAPI.startRampRecording(roomKey, sessionName: sessionName)
            
            DispatchQueue.main.async {
                isRecording = true
                recordingStartTime = Date()
                alertMessage = "Recording started for \(room.name)"
                showingAlert = true
                rampRecordingMode = false
            }
        } catch {
            DispatchQueue.main.async {
                alertMessage = "Failed to start recording: \(error.localizedDescription)"
                showingAlert = true
            }
        }
        
        DispatchQueue.main.async { isLoading = false }
    }
    
    func stopRecording() async {
        DispatchQueue.main.async { isLoading = true }
        
        do {
            let roomKey = room.name.lowercased().replacingOccurrences(of: " ", with: "_")
            try await HomeAssistantAPI.stopRampRecording(roomKey)
            
            DispatchQueue.main.async {
                isRecording = false
                recordingStartTime = nil
                sessionName = ""
                alertMessage = "Recording stopped and saved"
                showingAlert = true
            }
            
            await loadRampSessions()
        } catch {
            DispatchQueue.main.async {
                alertMessage = "Failed to stop recording: \(error.localizedDescription)"
                showingAlert = true
            }
        }
        
        DispatchQueue.main.async { isLoading = false }
    }
    
    func loadRampSessions() async {
        do {
            let roomKey = room.name.lowercased().replacingOccurrences(of: " ", with: "_")
            rampSessions = try await HomeAssistantAPI.getRampSessions(roomKey)
        } catch {
            print("Error loading sessions: \(error)")
            DispatchQueue.main.async {
                rampSessions = []
            }
        }
    }
}

struct RampSessionsView: View {
    let room: Room
    @Binding var sessions: [RampSession]
    @Environment(\.presentationMode) var presentationMode
    
    var body: some View {
        NavigationView {
            Group {
                if sessions.isEmpty {
                    VStack(spacing: 20) {
                        Image(systemName: "tray")
                            .font(.largeTitle)
                            .foregroundColor(.secondary)
                        Text("No recording sessions yet")
                            .font(.headline)
                            .foregroundColor(.secondary)
                        Text("Start a ramp recording session to see data here")
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding()
                } else {
                    List(sessions) { session in
                        VStack(alignment: .leading, spacing: 8) {
                            Text(session.sessionName)
                                .font(.headline)
                            
                            HStack {
                                Text("Status: \(session.status.capitalized)")
                                    .font(.caption)
                                    .foregroundColor(session.status == "completed" ? .green : .orange)
                                
                                Spacer()
                                
                                Text("\(session.dataPoints) points")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                            
                            Text("Started: \(formatDate(session.startTime))")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            
                            if let endTime = session.endTime {
                                Text("Ended: \(formatDate(endTime))")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                        }
                        .padding(.vertical, 4)
                    }
                }
            }
            .navigationTitle("\(room.name) Sessions")
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarItems(
                trailing: Button("Done") {
                    presentationMode.wrappedValue.dismiss()
                }
            )
        }
    }
    
    func formatDate(_ dateString: String) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd HH:mm:ss"
        if let date = formatter.date(from: dateString) {
            formatter.dateStyle = .short
            formatter.timeStyle = .short
            return formatter.string(from: date)
        }
        return dateString
    }
}

// MARK: - Helper Extensions
private let timeFormatter: DateFormatter = {
    let formatter = DateFormatter()
    formatter.timeStyle = .short
    return formatter
}()

#Preview {
    ContentView()
}