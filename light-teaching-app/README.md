# Smart Light Teaching App 🔆

A React Native mobile app for teaching your Home Assistant smart lights the perfect brightness and temperature settings based on different conditions.

## Features

- **Room-Based Interface**: Navigate through different rooms in your home
- **Real-Time Data**: See current intelligent lighting settings from Home Assistant
- **Teaching Mode**: Interactive sliders and presets to set brightness (1-100%) and temperature (1800K-6500K)
- **Learning Integration**: Connects with your existing adaptive learning system
- **Automation Predictions**: Shows what your lights will do at different times based on learned patterns
- **Modern UI**: Dark theme with beautiful gradients and icons

## Rooms Supported

Based on your Home Assistant setup:
- 🛏️ **Bedroom** (with adaptive learning)
- 🛋️ **Living Room**
- 👨‍🍳 **Kitchen** (with motion automation)
- 🚿 **Bathroom** (with adaptive learning and hold modes)
- 🚶 **Hallway**
- 🧺 **Laundry**
- 👔 **Closet**

## Setup Instructions

### 1. Install Dependencies

```bash
cd light-teaching-app
npm install
```

### 2. Configure Home Assistant Connection

Edit `src/config/rooms.js` and update:

```javascript
export const HA_CONFIG = {
  baseUrl: 'http://YOUR_HA_IP:8123', // Replace with your Home Assistant URL
  longLivedToken: 'YOUR_TOKEN_HERE', // Create a long-lived access token
};
```

#### Creating a Long-Lived Access Token:
1. In Home Assistant, go to Profile → Security → Long-Lived Access Tokens
2. Click "Create Token"
3. Give it a name like "Light Teaching App"
4. Copy the token and paste it in the config

### 3. Verify PyScript Services

The app uses these PyScript services (already added to your system):
- `pyscript.als_teach_room` - Teaches new settings
- `pyscript.als_get_learned_data` - Gets learned data from database
- `pyscript.als_get_automation_predictions` - Generates time-based predictions

### 4. Start the App

```bash
# For development
npm start

# For specific platform
npm run ios      # iOS simulator
npm run android  # Android emulator
npm run web      # Web browser
```

### 5. Using the App

1. **Rooms Screen**: View all rooms with current brightness/temperature
2. **Room Detail**: See current settings, learned data, and predictions
3. **Teaching Mode**: 
   - Activate teaching mode
   - Adjust brightness and temperature sliders
   - Use presets for quick settings
   - Tap "Teach" to save the setting for current conditions

## How Teaching Works

When you teach a setting:
1. App captures current conditions (home mode, time, weather, season)
2. Sends brightness/temperature to PyScript service
3. Data is stored in SQLite database with condition key
4. Your intelligent lighting system learns this preference
5. Future automation will use learned settings

## Condition Keys

The system creates unique keys based on:
- **Home Mode**: Night, Early Morning, Day, Evening, Away
- **Sun Elevation**: Below Horizon, Low Sun, Mid Sun, High Sun  
- **Cloud Coverage**: 0%, 20%, 40%, 60%, 80%
- **Season**: Spring, Summer, Fall, Winter

Example: `Evening_Low_Sun_40_Winter`

## Troubleshooting

### Connection Issues
- Verify Home Assistant URL and token
- Check if your device can reach HA network
- Ensure PyScript is enabled in Home Assistant

### Missing Data
- Check Home Assistant logs for PyScript errors
- Verify SQLite database has adaptive_learning table
- Test services manually in HA Developer Tools

### App Crashes
- Check React Native logs: `npx react-native log-ios` or `npx react-native log-android`
- Verify all dependencies are installed

## Technical Details

- **Framework**: React Native with Expo
- **Navigation**: React Navigation 6
- **UI Components**: Custom components with Linear Gradients
- **Icons**: Material Community Icons
- **API**: Direct Home Assistant REST API calls
- **Database**: Integrates with existing SQLite adaptive learning system

## API Endpoints Used

- `GET /api/states/{entity_id}` - Get entity states
- `GET /api/states` - Get all states
- `POST /api/services/{domain}/{service}` - Call services
- Home Assistant WebSocket (future enhancement)

## Future Enhancements

- [ ] WebSocket real-time updates
- [ ] Push notifications for teaching reminders
- [ ] Advanced scheduling interface
- [ ] Light scene management
- [ ] Voice control integration
- [ ] Advanced analytics and charts