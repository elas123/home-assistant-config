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
        let (_, _) = try await URLSession.shared.data(for: request)
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
        let (_, _) = try await URLSession.shared.data(for: request)
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
        let (_, _) = try await URLSession.shared.data(for: request)
    }
    
    static func fetchEntityState(_ entityId: String) async throws -> EntityState {
        let url = URL(string: "\(baseURL)/api/states/\(entityId)")!
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, _) = try await URLSession.shared.data(for: request)
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
        let (data, _) = try await URLSession.shared.data(for: request)
        
        struct Response: Codable {
            let sessions: [RampSession]
        }
        let response = try JSONDecoder().decode(Response.self, from: data)
        return response.sessions
    }
}

// MARK: - Views
struct ContentView: View {
    @State private var rooms: [Room] = [
        Room(name: "Bedroom", icon: "bed.double.fill", 
             brightnessEntity: "sensor.bedroom_intelligent_brightness",
             temperatureEntity: "sensor.intelligent_temperature_bedroom",
             supportsTemperature: false),
        Room(name: "Living Room", icon: "sofa.fill",
             brightnessEntity: "sensor.intelligent_brightness_living_room", 
             temperatureEntity: "sensor.intelligent_temperature_living_room",
             supportsTemperature: false),
        Room(name: "Kitchen", icon: "fork.knife",
             brightnessEntity: "sensor.intelligent_brightness_kitchen",
             temperatureEntity: "sensor.intelligent_temperature_master",
             supportsTemperature: false),
        Room(name: "Bathroom", icon: "bathtub.fill",
             brightnessEntity: "sensor.bathroom_intelligent_brightness",
             temperatureEntity: "sensor.intelligent_temperature_master",
             supportsTemperature: false),
        Room(name: "Hallway", icon: "lightbulb.fill",
             brightnessEntity: "sensor.intelligent_brightness_hallway",
             temperatureEntity: "sensor.intelligent_temperature_master",
             supportsTemperature: false),
        Room(name: "Laundry", icon: "washer.fill",
             brightnessEntity: "sensor.intelligent_brightness_laundry",
             temperatureEntity: "sensor.intelligent_temperature_master",
             supportsTemperature: false),
        Room(name: "Closet", icon: "cabinet.fill",
             brightnessEntity: "light.closet",
             temperatureEntity: "sensor.intelligent_temperature_master",
             supportsTemperature: true)
    ]
    
    var body: some View {
        NavigationView {
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
            .navigationTitle("Smart Lighting")
            .preferredColorScheme(.dark)
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
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                VStack(alignment: .leading, spacing: 16) {
                    Text("Current Settings")
                        .font(.headline)
                    
                    HStack {
                        Image(systemName: "sun.max.fill")
                            .foregroundColor(.orange)
                        Text("Brightness: \(currentBrightness)%")
                        Spacer()
                        
                        Button(action: { Task { await refreshData() } }) {
                            Image(systemName: "arrow.clockwise")
                                .foregroundColor(.blue)
                        }
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
                                do {
                                    try await HomeAssistantAPI.teachRoom(
                                        room.name.lowercased().replacingOccurrences(of: " ", with: "_"), 
                                        brightness: Int(brightness), 
                                        temperature: room.supportsTemperature ? Int(temperature) : nil
                                    )
                                    teachingMode = false
                                } catch {
                                    print("Error teaching room: \(error)")
                                }
                            }
                        }
                        .buttonStyle(.borderedProminent)
                        .frame(maxWidth: .infinity)
                    }
                    .padding()
                    .background(Color(.systemBlue).opacity(0.1))
                    .cornerRadius(12)
                }
                
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
                                .disabled(sessionName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                            }
                            
                            Button("View Past Sessions") {
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
            Task {
                await refreshData()
            }
        }
        .sheet(isPresented: $showingSessions) {
            RampSessionsView(room: room, sessions: $rampSessions)
        }
    }
    
    func refreshData() async {
        do {
            let brightnessState = try await HomeAssistantAPI.fetchEntityState(room.brightnessEntity)
            if let brightnessValue = Int(brightnessState.state) {
                currentBrightness = brightnessValue
            }
            
            if room.supportsTemperature {
                let tempState = try await HomeAssistantAPI.fetchEntityState(room.temperatureEntity)
                if let tempValue = Int(tempState.state) {
                    currentTemperature = tempValue
                }
            }
        } catch {
            print("Error fetching data: \(error)")
        }
    }
    
    func startRecording() async {
        do {
            try await HomeAssistantAPI.startRampRecording(
                room.name.lowercased().replacingOccurrences(of: " ", with: "_"),
                sessionName: sessionName
            )
            isRecording = true
            recordingStartTime = Date()
            rampRecordingMode = false
        } catch {
            print("Error starting recording: \(error)")
        }
    }
    
    func stopRecording() async {
        do {
            try await HomeAssistantAPI.stopRampRecording(
                room.name.lowercased().replacingOccurrences(of: " ", with: "_")
            )
            isRecording = false
            recordingStartTime = nil
            sessionName = ""
            await loadRampSessions()
        } catch {
            print("Error stopping recording: \(error)")
        }
    }
    
    func loadRampSessions() async {
        do {
            rampSessions = try await HomeAssistantAPI.getRampSessions(
                room.name.lowercased().replacingOccurrences(of: " ", with: "_")
            )
        } catch {
            print("Error loading sessions: \(error)")
        }
    }
}

struct RampSessionsView: View {
    let room: Room
    @Binding var sessions: [RampSession]
    @Environment(\.presentationMode) var presentationMode
    
    var body: some View {
        NavigationView {
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

#Preview {
    ContentView()
}