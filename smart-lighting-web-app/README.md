# Smart Lighting Web App 💡

A React web application for teaching and automating your Home Assistant smart lighting system. Features both manual teaching mode and advanced ramp recording for seamless lighting transitions.

## Features

### 🎯 **Teaching Mode**
- Manually set brightness and temperature preferences
- Teach the system your lighting preferences for different scenarios
- Direct integration with Home Assistant PyScript services

### 📹 **Ramp Recording Mode** 
- Record manual brightness adjustments over time
- Creates seamless automation curves with cubic spline interpolation
- Session-based recording with custom naming
- View historical recording sessions with data points

### 🏠 **Room Management**
- Support for multiple rooms: Bedroom, Lamp 1, Lamp 2, Kitchen, Bathroom, Hallway, Laundry, Closet
- Live data fetching from Home Assistant sensors
- Temperature control for supported lights (Lamp 1, Lamp 2, Closet)
- Brightness-only control for other rooms

### 🌙 **Dark Theme**
- Professional dark theme with gradient accents
- Responsive design that works on desktop and mobile
- Smooth animations and hover effects

## Setup Instructions

### Prerequisites
- Node.js (v16 or later)
- Home Assistant with PyScript integration
- The companion PyScript services from the main project

### Installation

1. **Navigate to the web app directory:**
   ```bash
   cd /Users/frank/home-assistant-project/smart-lighting-web-app
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Update configuration (if needed):**
   - Edit `src/services/HomeAssistantAPI.js` to update your Home Assistant URL and token
   - Modify `src/data/rooms.js` to match your specific room setup and entity names

4. **Start the development server:**
   ```bash
   npm start
   ```

5. **Open your browser:**
   Navigate to `http://localhost:3000`

## Usage

### Teaching Mode
1. Select a room from the grid
2. Click "Teaching Mode" toggle
3. Adjust brightness and temperature sliders
4. Click "Teach This Setting" to save

### Ramp Recording
1. Select a room from the grid  
2. Click "Ramp Recording" toggle
3. Enter a session name (e.g., "Morning Routine")
4. Click "Start Recording"
5. Manually adjust your physical lights/dimmers
6. Click "Stop Recording" when done
7. View past sessions with "View Past Sessions"

### Room Data
- Click the refresh button (🔄) on any room to fetch live brightness/temperature data
- Room cards show current brightness percentages
- Temperature is displayed for supported rooms (Lamp 1, Lamp 2, Closet)

## API Integration

The web app integrates with these Home Assistant PyScript services:

- `als_teach_room` - Save lighting preferences
- `start_ramp_recording` - Begin recording session
- `stop_ramp_recording` - End recording session  
- `get_ramp_sessions` - Retrieve session history
- Entity state fetching for live data

## Room Configuration

Current room setup:
- **Bedroom**: Brightness only
- **Lamp 1**: Brightness + Temperature
- **Lamp 2**: Brightness + Temperature  
- **Kitchen**: Brightness only
- **Bathroom**: Brightness only
- **Hallway**: Brightness only
- **Laundry**: Brightness only
- **Closet**: Brightness + Temperature

## Building for Production

```bash
npm run build
```

This creates a `build` folder with optimized production files that can be served by any web server.

## File Structure

```
smart-lighting-web-app/
├── public/
│   └── index.html          # Main HTML template
├── src/
│   ├── components/         # React components
│   │   ├── RoomCard.js    # Individual room display
│   │   ├── TeachingMode.js # Teaching interface
│   │   └── RampRecordingMode.js # Recording interface
│   ├── services/
│   │   └── HomeAssistantAPI.js # API communication
│   ├── data/
│   │   └── rooms.js       # Room configuration
│   ├── App.js            # Main application component
│   ├── index.js          # Application entry point
│   └── index.css         # Dark theme styles
├── package.json
└── README.md
```

## Customization

### Adding New Rooms
Edit `src/data/rooms.js` and add new room objects with:
- `id`: Unique identifier
- `name`: Display name
- `icon`: Emoji or icon
- `brightnessEntity`: Home Assistant brightness sensor
- `temperatureEntity`: Home Assistant temperature sensor  
- `supportsTemperature`: Boolean for temperature control

### Styling
Modify `src/index.css` to customize the dark theme, colors, and animations.

### API Configuration
Update `src/services/HomeAssistantAPI.js` to change the Home Assistant connection details.

---

This web app provides the same functionality as the iOS version but accessible through any web browser. Perfect for desktop use or devices without the iOS app.