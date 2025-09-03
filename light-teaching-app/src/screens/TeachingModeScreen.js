import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  Dimensions,
  ScrollView
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import Slider from 'react-native-slider';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

import { BRIGHTNESS_PRESETS, TEMPERATURE_PRESETS } from '../config/rooms';
import homeAssistantAPI from '../services/homeAssistantAPI';

const { width } = Dimensions.get('window');

const TeachingModeScreen = ({ navigation, route }) => {
  const { room, roomState } = route.params;
  
  const [teachingActive, setTeachingActive] = useState(false);
  const [brightness, setBrightness] = useState(roomState?.currentBrightness || 50);
  const [temperature, setTemperature] = useState(roomState?.currentTemperature || 3000);
  const [lastTaughtSettings, setLastTaughtSettings] = useState(null);

  useEffect(() => {
    // Initialize with current intelligent settings
    if (roomState) {
      setBrightness(roomState.currentBrightness || 50);
      setTemperature(roomState.currentTemperature || 3000);
    }
  }, [roomState]);

  const handleActivateTeaching = () => {
    setTeachingActive(true);
  };

  const handleDeactivateTeaching = () => {
    setTeachingActive(false);
  };

  const handleTeach = async () => {
    if (!teachingActive) {
      Alert.alert('Teaching Mode Inactive', 'Please activate teaching mode first');
      return;
    }

    try {
      Alert.alert(
        'Teach This Setting',
        `This will teach ${room.name} to remember:\n\n• Brightness: ${brightness}%\n• Temperature: ${temperature}K\n\nfor the current conditions.`,
        [
          { text: 'Cancel', style: 'cancel' },
          {
            text: 'Teach',
            onPress: async () => {
              try {
                await homeAssistantAPI.teachRoom(room.id, brightness, temperature);
                
                setLastTaughtSettings({ brightness, temperature, time: new Date() });
                
                Alert.alert(
                  'Teaching Successful! 🎉',
                  `${room.name} has learned this setting for the current conditions.`,
                  [
                    { 
                      text: 'Teach More',
                      style: 'default'
                    },
                    {
                      text: 'Done',
                      onPress: () => navigation.goBack()
                    }
                  ]
                );
              } catch (error) {
                Alert.alert('Teaching Failed', 'Could not save the teaching data. Please try again.');
              }
            }
          }
        ]
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to teach room settings');
    }
  };

  const handlePresetBrightness = (presetValue) => {
    setBrightness(presetValue);
  };

  const handlePresetTemperature = (presetValue) => {
    setTemperature(presetValue);
  };

  const getTemperatureColor = (temp) => {
    if (temp < 2200) return '#FF4500';
    if (temp < 2700) return '#FF8C00';
    if (temp < 3200) return '#FFD700';
    if (temp < 4000) return '#F5F5DC';
    if (temp < 5000) return '#E0F6FF';
    return '#DDEEFF';
  };

  const renderTeachingModeToggle = () => {
    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Teaching Mode</Text>
        
        <TouchableOpacity
          style={styles.teachingModeCard}
          onPress={teachingActive ? handleDeactivateTeaching : handleActivateTeaching}
        >
          <LinearGradient
            colors={teachingActive ? ['#4ECDC4', '#44A08D'] : ['#6C7378', '#4A5568']}
            style={styles.teachingModeGradient}
          >
            <View style={styles.teachingModeContent}>
              <View style={styles.teachingModeIcon}>
                <Icon 
                  name={teachingActive ? "school" : "school-outline"} 
                  size={32} 
                  color="white" 
                />
              </View>
              <View style={styles.teachingModeText}>
                <Text style={styles.teachingModeTitle}>
                  {teachingActive ? 'Teaching Mode Active' : 'Activate Teaching Mode'}
                </Text>
                <Text style={styles.teachingModeDescription}>
                  {teachingActive 
                    ? 'Adjust settings below, then tap Teach'
                    : 'Tap to start teaching new light settings'
                  }
                </Text>
              </View>
              <Icon 
                name={teachingActive ? "toggle-switch" : "toggle-switch-off"} 
                size={32} 
                color="white" 
              />
            </View>
          </LinearGradient>
        </TouchableOpacity>
      </View>
    );
  };

  const renderBrightnessControl = () => {
    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Brightness Control</Text>
        
        <View style={styles.controlCard}>
          <View style={styles.sliderContainer}>
            <View style={styles.sliderHeader}>
              <Icon name="brightness-6" size={24} color="#FFA726" />
              <Text style={styles.sliderValue}>{brightness}%</Text>
            </View>
            
            <Slider
              style={styles.slider}
              minimumValue={1}
              maximumValue={100}
              value={brightness}
              onValueChange={(value) => setBrightness(Math.round(value))}
              minimumTrackTintColor="#FFA726"
              maximumTrackTintColor="#30363D"
              thumbStyle={styles.sliderThumb}
              trackStyle={styles.sliderTrack}
              disabled={!teachingActive}
            />
            
            <View style={styles.sliderLabels}>
              <Text style={styles.sliderLabelText}>1%</Text>
              <Text style={styles.sliderLabelText}>100%</Text>
            </View>
          </View>

          <Text style={styles.presetsLabel}>Quick Presets</Text>
          <ScrollView 
            horizontal 
            showsHorizontalScrollIndicator={false}
            style={styles.presetsContainer}
          >
            {BRIGHTNESS_PRESETS.map((preset) => (
              <TouchableOpacity
                key={preset.value}
                style={[
                  styles.presetButton,
                  brightness === preset.value && styles.presetButtonSelected,
                  !teachingActive && styles.presetButtonDisabled
                ]}
                onPress={() => handlePresetBrightness(preset.value)}
                disabled={!teachingActive}
              >
                <Text style={[
                  styles.presetButtonText,
                  brightness === preset.value && styles.presetButtonTextSelected
                ]}>
                  {preset.label}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
      </View>
    );
  };

  const renderTemperatureControl = () => {
    const tempColor = getTemperatureColor(temperature);
    
    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Temperature Control</Text>
        
        <View style={styles.controlCard}>
          <View style={styles.sliderContainer}>
            <View style={styles.sliderHeader}>
              <Icon name="thermometer" size={24} color={tempColor} />
              <Text style={styles.sliderValue}>{temperature}K</Text>
              <View style={[styles.temperaturePreview, { backgroundColor: tempColor }]} />
            </View>
            
            <Slider
              style={styles.slider}
              minimumValue={1800}
              maximumValue={6500}
              value={temperature}
              onValueChange={(value) => setTemperature(Math.round(value))}
              minimumTrackTintColor={tempColor}
              maximumTrackTintColor="#30363D"
              thumbStyle={styles.sliderThumb}
              trackStyle={styles.sliderTrack}
              disabled={!teachingActive}
            />
            
            <View style={styles.sliderLabels}>
              <Text style={styles.sliderLabelText}>1800K</Text>
              <Text style={styles.sliderLabelText}>6500K</Text>
            </View>
          </View>

          <Text style={styles.presetsLabel}>Temperature Presets</Text>
          <ScrollView 
            horizontal 
            showsHorizontalScrollIndicator={false}
            style={styles.presetsContainer}
          >
            {TEMPERATURE_PRESETS.map((preset) => (
              <TouchableOpacity
                key={preset.value}
                style={[
                  styles.temperaturePresetButton,
                  temperature === preset.value && styles.presetButtonSelected,
                  !teachingActive && styles.presetButtonDisabled
                ]}
                onPress={() => handlePresetTemperature(preset.value)}
                disabled={!teachingActive}
              >
                <View style={[styles.temperaturePresetColor, { backgroundColor: preset.color }]} />
                <Text style={[
                  styles.presetButtonText,
                  temperature === preset.value && styles.presetButtonTextSelected
                ]}>
                  {preset.label}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
      </View>
    );
  };

  const renderCurrentConditions = () => {
    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Current Conditions</Text>
        
        <View style={styles.conditionsCard}>
          <Text style={styles.conditionsText}>
            Teaching will be saved for the current home state, time, weather, and season.
          </Text>
          
          <View style={styles.conditionsList}>
            <View style={styles.conditionItem}>
              <Icon name="home" size={16} color="#8B949E" />
              <Text style={styles.conditionValue}>Current home mode</Text>
            </View>
            <View style={styles.conditionItem}>
              <Icon name="clock" size={16} color="#8B949E" />
              <Text style={styles.conditionValue}>Time of day</Text>
            </View>
            <View style={styles.conditionItem}>
              <Icon name="weather-cloudy" size={16} color="#8B949E" />
              <Text style={styles.conditionValue}>Weather conditions</Text>
            </View>
            <View style={styles.conditionItem}>
              <Icon name="leaf" size={16} color="#8B949E" />
              <Text style={styles.conditionValue}>Season</Text>
            </View>
          </View>
        </View>
      </View>
    );
  };

  const renderLastTaught = () => {
    if (!lastTaughtSettings) return null;

    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Last Taught Setting</Text>
        
        <View style={styles.lastTaughtCard}>
          <Icon name="check-circle" size={24} color="#4ECDC4" />
          <View style={styles.lastTaughtInfo}>
            <Text style={styles.lastTaughtText}>
              {lastTaughtSettings.brightness}% • {lastTaughtSettings.temperature}K
            </Text>
            <Text style={styles.lastTaughtTime}>
              {lastTaughtSettings.time.toLocaleTimeString()}
            </Text>
          </View>
        </View>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <ScrollView 
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
      >
        {renderTeachingModeToggle()}
        {renderBrightnessControl()}
        {renderTemperatureControl()}
        {renderCurrentConditions()}
        {renderLastTaught()}
      </ScrollView>

      {teachingActive && (
        <View style={styles.bottomBar}>
          <TouchableOpacity 
            style={styles.teachButton}
            onPress={handleTeach}
          >
            <LinearGradient
              colors={['#667eea', '#764ba2']}
              style={styles.teachButtonGradient}
            >
              <Icon name="school" size={24} color="white" />
              <Text style={styles.teachButtonText}>
                Teach {brightness}% • {temperature}K
              </Text>
            </LinearGradient>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0D1117',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: teachingActive => teachingActive ? 120 : 20,
  },
  section: {
    margin: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 12,
  },
  teachingModeCard: {
    borderRadius: 16,
    overflow: 'hidden',
  },
  teachingModeGradient: {
    padding: 20,
  },
  teachingModeContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  teachingModeIcon: {
    marginRight: 16,
  },
  teachingModeText: {
    flex: 1,
  },
  teachingModeTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 4,
  },
  teachingModeDescription: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.8)',
  },
  controlCard: {
    backgroundColor: '#161B22',
    borderRadius: 16,
    padding: 20,
    borderWidth: 1,
    borderColor: '#30363D',
  },
  sliderContainer: {
    marginBottom: 20,
  },
  sliderHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  sliderValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginLeft: 12,
    flex: 1,
  },
  temperaturePreview: {
    width: 24,
    height: 24,
    borderRadius: 12,
  },
  slider: {
    height: 40,
    marginVertical: 8,
  },
  sliderThumb: {
    width: 24,
    height: 24,
    backgroundColor: '#FFFFFF',
  },
  sliderTrack: {
    height: 6,
    borderRadius: 3,
  },
  sliderLabels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  sliderLabelText: {
    fontSize: 12,
    color: '#8B949E',
  },
  presetsLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FFFFFF',
    marginBottom: 12,
  },
  presetsContainer: {
    flexDirection: 'row',
  },
  presetButton: {
    backgroundColor: '#30363D',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
    marginRight: 8,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  presetButtonSelected: {
    backgroundColor: '#FFA726',
    borderColor: '#FFFFFF',
  },
  presetButtonDisabled: {
    opacity: 0.5,
  },
  presetButtonText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
  },
  presetButtonTextSelected: {
    color: '#000000',
  },
  temperaturePresetButton: {
    backgroundColor: '#30363D',
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderRadius: 20,
    marginRight: 8,
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: 'transparent',
  },
  temperaturePresetColor: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  conditionsCard: {
    backgroundColor: '#161B22',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#30363D',
  },
  conditionsText: {
    fontSize: 14,
    color: '#8B949E',
    marginBottom: 16,
    lineHeight: 20,
  },
  conditionsList: {
    gap: 8,
  },
  conditionItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  conditionValue: {
    fontSize: 14,
    color: '#FFFFFF',
    marginLeft: 8,
  },
  lastTaughtCard: {
    backgroundColor: '#161B22',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#4ECDC4',
    flexDirection: 'row',
    alignItems: 'center',
  },
  lastTaughtInfo: {
    marginLeft: 12,
    flex: 1,
  },
  lastTaughtText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#4ECDC4',
  },
  lastTaughtTime: {
    fontSize: 12,
    color: '#8B949E',
    marginTop: 2,
  },
  bottomBar: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: '#0D1117',
    borderTopWidth: 1,
    borderTopColor: '#30363D',
    padding: 16,
  },
  teachButton: {
    borderRadius: 16,
    overflow: 'hidden',
  },
  teachButtonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  teachButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 12,
  },
});

export default TeachingModeScreen;