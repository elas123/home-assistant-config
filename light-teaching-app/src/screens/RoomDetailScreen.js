import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

import homeAssistantAPI from '../services/homeAssistantAPI';

const RoomDetailScreen = ({ navigation, route }) => {
  const { room, roomState: initialRoomState } = route.params;
  const [roomState, setRoomState] = useState(initialRoomState);
  const [learnedData, setLearnedData] = useState([]);
  const [automationPredictions, setAutomationPredictions] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadAdditionalData();
  }, []);

  const loadAdditionalData = async () => {
    try {
      setLoading(true);
      
      // Load learned data if room supports learning
      if (room.hasLearning) {
        try {
          const learned = await homeAssistantAPI.getLearnedData(room.id);
          setLearnedData(learned || []);
        } catch (error) {
          console.warn('Could not load learned data:', error);
        }
      }

      // Load automation predictions
      try {
        const predictions = await homeAssistantAPI.getAutomationPredictions(room.id);
        setAutomationPredictions(predictions || []);
      } catch (error) {
        console.warn('Could not load automation predictions:', error);
      }
    } catch (error) {
      console.error('Error loading additional data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      // Refresh room state
      const newRoomState = await homeAssistantAPI.getRoomData(room);
      setRoomState(newRoomState);
      
      // Reload additional data
      await loadAdditionalData();
    } catch (error) {
      Alert.alert('Error', 'Failed to refresh room data');
    } finally {
      setRefreshing(false);
    }
  };

  const handleTeachingMode = () => {
    navigation.navigate('TeachingMode', { room, roomState });
  };

  const handleApplyIntelligentSettings = async () => {
    try {
      Alert.alert(
        'Apply Intelligent Settings',
        `This will turn on all lights in ${room.name} with the current intelligent brightness (${roomState.currentBrightness}%) and temperature (${roomState.currentTemperature}K).`,
        [
          { text: 'Cancel', style: 'cancel' },
          { 
            text: 'Apply', 
            onPress: async () => {
              try {
                await homeAssistantAPI.applyIntelligentLighting(room);
                Alert.alert('Success', 'Intelligent settings applied to lights');
                handleRefresh();
              } catch (error) {
                Alert.alert('Error', 'Failed to apply settings');
              }
            }
          }
        ]
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to apply intelligent settings');
    }
  };

  const renderCurrentSettings = () => {
    const brightness = roomState?.currentBrightness || 0;
    const temperature = roomState?.currentTemperature || 3000;
    const tempColor = temperature < 2500 ? '#FF8C00' : 
                     temperature < 3500 ? '#FFD700' : '#F0F8FF';

    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Current Intelligent Settings</Text>
        
        <LinearGradient
          colors={['#161B22', '#0D1117']}
          style={styles.settingsCard}
        >
          <View style={styles.settingRow}>
            <View style={styles.settingIcon}>
              <Icon name="brightness-6" size={24} color="#FFA726" />
            </View>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Brightness</Text>
              <Text style={styles.settingValue}>{brightness}%</Text>
            </View>
            <View style={[styles.brightnessIndicator, { width: `${brightness}%` }]} />
          </View>

          <View style={styles.settingDivider} />

          <View style={styles.settingRow}>
            <View style={styles.settingIcon}>
              <Icon name="thermometer" size={24} color={tempColor} />
            </View>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Temperature</Text>
              <Text style={styles.settingValue}>{temperature}K</Text>
            </View>
            <View style={[styles.temperatureIndicator, { backgroundColor: tempColor }]} />
          </View>
        </LinearGradient>

        <TouchableOpacity 
          style={styles.applyButton}
          onPress={handleApplyIntelligentSettings}
        >
          <LinearGradient
            colors={['#4ECDC4', '#44A08D']}
            style={styles.applyButtonGradient}
          >
            <Icon name="lightbulb-on" size={20} color="white" />
            <Text style={styles.applyButtonText}>Apply to Lights</Text>
          </LinearGradient>
        </TouchableOpacity>
      </View>
    );
  };

  const renderLightStates = () => {
    const lights = roomState?.lightStates || [];
    
    if (lights.length === 0) {
      return null;
    }

    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Light Status</Text>
        
        {lights.map((light, index) => {
          const isOn = light.state === 'on';
          const brightness = light.attributes?.brightness_pct || 0;
          const colorTemp = light.attributes?.color_temp_kelvin || 3000;
          
          return (
            <View key={light.entity_id} style={styles.lightCard}>
              <View style={styles.lightHeader}>
                <View style={[styles.lightStatus, { 
                  backgroundColor: isOn ? '#4ECDC4' : '#6C7378' 
                }]}>
                  <Icon 
                    name={isOn ? "lightbulb-on" : "lightbulb-off"} 
                    size={16} 
                    color="white" 
                  />
                </View>
                <Text style={styles.lightName}>
                  {light.attributes?.friendly_name || light.entity_id}
                </Text>
              </View>
              
              {isOn && (
                <View style={styles.lightDetails}>
                  <Text style={styles.lightDetail}>{brightness}% • {colorTemp}K</Text>
                </View>
              )}
            </View>
          );
        })}
      </View>
    );
  };

  const renderLearnedData = () => {
    if (!room.hasLearning || learnedData.length === 0) {
      return null;
    }

    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>
          What {room.name} Has Learned
          <Icon name="brain" size={16} color="#4ECDC4" style={{ marginLeft: 8 }} />
        </Text>
        
        <View style={styles.learnedContainer}>
          {learnedData.slice(0, 5).map((data, index) => (
            <View key={index} style={styles.learnedItem}>
              <View style={styles.learnedCondition}>
                <Text style={styles.learnedConditionText}>{data.condition}</Text>
              </View>
              <View style={styles.learnedValues}>
                <Text style={styles.learnedValue}>{data.brightness}%</Text>
                {data.temperature && (
                  <Text style={styles.learnedValue}>{data.temperature}K</Text>
                )}
              </View>
            </View>
          ))}
        </View>
      </View>
    );
  };

  const renderAutomationPredictions = () => {
    if (automationPredictions.length === 0) {
      return (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>What It Can Do</Text>
          <View style={styles.emptyState}>
            <Icon name="robot" size={48} color="#6C7378" />
            <Text style={styles.emptyText}>
              Teach {room.name} some settings to see automation predictions
            </Text>
          </View>
        </View>
      );
    }

    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Automation Predictions</Text>
        
        <View style={styles.predictionsContainer}>
          {automationPredictions.map((prediction, index) => (
            <View key={index} style={styles.predictionItem}>
              <View style={styles.predictionTime}>
                <Icon name="clock" size={16} color="#8B949E" />
                <Text style={styles.predictionTimeText}>{prediction.time}</Text>
              </View>
              <Text style={styles.predictionAction}>{prediction.action}</Text>
              <Text style={styles.predictionConfidence}>
                {prediction.confidence}% confidence
              </Text>
            </View>
          ))}
        </View>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            colors={['#4ECDC4']}
            tintColor={'#4ECDC4'}
          />
        }
      >
        <View style={styles.header}>
          <View style={[styles.roomIcon, { backgroundColor: room.color }]}>
            <Icon name={room.icon} size={32} color="white" />
          </View>
          <Text style={styles.roomName}>{room.name}</Text>
          <Text style={styles.roomDescription}>{room.description}</Text>
        </View>

        {renderCurrentSettings()}
        {renderLightStates()}
        {renderLearnedData()}
        {renderAutomationPredictions()}
      </ScrollView>

      <View style={styles.bottomBar}>
        <TouchableOpacity 
          style={styles.teachButton}
          onPress={handleTeachingMode}
        >
          <LinearGradient
            colors={['#667eea', '#764ba2']}
            style={styles.teachButtonGradient}
          >
            <Icon name="school" size={24} color="white" />
            <Text style={styles.teachButtonText}>Enter Teaching Mode</Text>
          </LinearGradient>
        </TouchableOpacity>
      </View>
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
    paddingBottom: 100,
  },
  header: {
    alignItems: 'center',
    padding: 24,
    borderBottomWidth: 1,
    borderBottomColor: '#30363D',
  },
  roomIcon: {
    width: 80,
    height: 80,
    borderRadius: 40,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  roomName: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 8,
  },
  roomDescription: {
    fontSize: 16,
    color: '#8B949E',
    textAlign: 'center',
  },
  section: {
    margin: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
  },
  settingsCard: {
    borderRadius: 12,
    padding: 20,
    borderWidth: 1,
    borderColor: '#30363D',
  },
  settingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
  },
  settingIcon: {
    marginRight: 16,
  },
  settingInfo: {
    flex: 1,
  },
  settingLabel: {
    fontSize: 14,
    color: '#8B949E',
    marginBottom: 4,
  },
  settingValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  settingDivider: {
    height: 1,
    backgroundColor: '#30363D',
    marginVertical: 12,
  },
  brightnessIndicator: {
    height: 4,
    backgroundColor: '#FFA726',
    borderRadius: 2,
    maxWidth: 100,
  },
  temperatureIndicator: {
    width: 20,
    height: 20,
    borderRadius: 10,
  },
  applyButton: {
    marginTop: 16,
    borderRadius: 8,
    overflow: 'hidden',
  },
  applyButtonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
  },
  applyButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  lightCard: {
    backgroundColor: '#161B22',
    borderRadius: 8,
    padding: 16,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#30363D',
  },
  lightHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  lightStatus: {
    width: 24,
    height: 24,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  lightName: {
    fontSize: 16,
    color: '#FFFFFF',
    flex: 1,
  },
  lightDetails: {
    marginTop: 8,
    paddingLeft: 36,
  },
  lightDetail: {
    fontSize: 14,
    color: '#8B949E',
  },
  learnedContainer: {
    backgroundColor: '#161B22',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#30363D',
  },
  learnedItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#30363D',
  },
  learnedCondition: {
    flex: 1,
  },
  learnedConditionText: {
    fontSize: 14,
    color: '#FFFFFF',
  },
  learnedValues: {
    flexDirection: 'row',
    gap: 12,
  },
  learnedValue: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#4ECDC4',
  },
  emptyState: {
    alignItems: 'center',
    padding: 32,
  },
  emptyText: {
    fontSize: 16,
    color: '#6C7378',
    textAlign: 'center',
    marginTop: 16,
    lineHeight: 24,
  },
  predictionsContainer: {
    backgroundColor: '#161B22',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#30363D',
  },
  predictionItem: {
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#30363D',
  },
  predictionTime: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  predictionTimeText: {
    fontSize: 12,
    color: '#8B949E',
    marginLeft: 6,
  },
  predictionAction: {
    fontSize: 16,
    color: '#FFFFFF',
    marginBottom: 4,
  },
  predictionConfidence: {
    fontSize: 12,
    color: '#4ECDC4',
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
    borderRadius: 12,
    overflow: 'hidden',
  },
  teachButtonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 18,
  },
  teachButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 12,
  },
});

export default RoomDetailScreen;