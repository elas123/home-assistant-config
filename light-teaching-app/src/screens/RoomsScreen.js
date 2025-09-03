import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
  Alert,
  RefreshControl
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

import { ROOMS } from '../config/rooms';
import homeAssistantAPI from '../services/homeAssistantAPI';

const { width } = Dimensions.get('window');

const RoomsScreen = ({ navigation }) => {
  const [roomStates, setRoomStates] = useState({});
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('unknown');

  useEffect(() => {
    checkConnection();
    loadRoomStates();
  }, []);

  const checkConnection = async () => {
    try {
      const isConnected = await homeAssistantAPI.testConnection();
      setConnectionStatus(isConnected ? 'connected' : 'disconnected');
    } catch (error) {
      setConnectionStatus('error');
    }
  };

  const loadRoomStates = async () => {
    try {
      setLoading(true);
      const states = {};
      
      for (const room of ROOMS) {
        try {
          const roomData = await homeAssistantAPI.getRoomData(room);
          states[room.id] = roomData;
        } catch (error) {
          console.error(`Error loading ${room.name}:`, error);
          states[room.id] = {
            roomId: room.id,
            roomName: room.name,
            error: true,
            currentBrightness: 0,
            currentTemperature: 3000
          };
        }
      }
      
      setRoomStates(states);
    } catch (error) {
      Alert.alert('Error', 'Failed to load room states');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await Promise.all([checkConnection(), loadRoomStates()]);
    setRefreshing(false);
  };

  const handleRoomPress = (room) => {
    const roomState = roomStates[room.id];
    navigation.navigate('RoomDetail', { room, roomState });
  };

  const renderConnectionStatus = () => {
    let statusColor = '#FF6B6B';
    let statusText = 'Disconnected';
    let statusIcon = 'wifi-off';

    if (connectionStatus === 'connected') {
      statusColor = '#4ECDC4';
      statusText = 'Connected';
      statusIcon = 'wifi';
    } else if (connectionStatus === 'unknown') {
      statusColor = '#FFA726';
      statusText = 'Checking...';
      statusIcon = 'wifi-strength-1';
    }

    return (
      <View style={[styles.statusBar, { backgroundColor: statusColor }]}>
        <Icon name={statusIcon} size={16} color="white" />
        <Text style={styles.statusText}>{statusText}</Text>
      </View>
    );
  };

  const renderRoomCard = (room) => {
    const roomState = roomStates[room.id];
    const brightness = roomState?.currentBrightness || 0;
    const temperature = roomState?.currentTemperature || 3000;
    const hasError = roomState?.error;

    // Calculate temperature color
    const tempColor = temperature < 2500 ? '#FF8C00' : 
                     temperature < 3500 ? '#FFD700' : '#F0F8FF';

    return (
      <TouchableOpacity
        key={room.id}
        style={styles.roomCard}
        onPress={() => handleRoomPress(room)}
        activeOpacity={0.8}
      >
        <LinearGradient
          colors={[room.color + '20', room.color + '05']}
          style={styles.roomCardGradient}
        >
          <View style={styles.roomCardHeader}>
            <View style={[styles.roomIcon, { backgroundColor: room.color }]}>
              <Icon name={room.icon} size={24} color="white" />
            </View>
            <View style={styles.roomInfo}>
              <Text style={styles.roomName}>{room.name}</Text>
              <Text style={styles.roomDescription}>{room.description}</Text>
            </View>
            {room.hasLearning && (
              <View style={styles.learningBadge}>
                <Icon name="brain" size={12} color="#4ECDC4" />
              </View>
            )}
          </View>

          <View style={styles.roomStats}>
            <View style={styles.statItem}>
              <Icon name="brightness-6" size={16} color="#FFA726" />
              <Text style={styles.statValue}>{brightness}%</Text>
              <Text style={styles.statLabel}>Brightness</Text>
            </View>
            
            <View style={styles.statDivider} />
            
            <View style={styles.statItem}>
              <Icon name="thermometer" size={16} color={tempColor} />
              <Text style={styles.statValue}>{temperature}K</Text>
              <Text style={styles.statLabel}>Temperature</Text>
            </View>
          </View>

          {hasError && (
            <View style={styles.errorBanner}>
              <Icon name="alert-circle" size={14} color="#FF6B6B" />
              <Text style={styles.errorText}>Connection Error</Text>
            </View>
          )}

          <View style={styles.roomCardFooter}>
            <Icon name="chevron-right" size={20} color="#666" />
          </View>
        </LinearGradient>
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      {renderConnectionStatus()}
      
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            colors={['#4ECDC4']}
            tintColor={'#4ECDC4'}
          />
        }
      >
        <View style={styles.header}>
          <Text style={styles.title}>Smart Lighting</Text>
          <Text style={styles.subtitle}>
            Teach your lights the perfect brightness and warmth
          </Text>
        </View>

        <View style={styles.roomsContainer}>
          {ROOMS.map(renderRoomCard)}
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>
            Pull down to refresh • Tap a room to view details
          </Text>
        </View>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0D1117',
  },
  statusBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    paddingHorizontal: 16,
  },
  statusText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '600',
    marginLeft: 6,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 20,
  },
  header: {
    padding: 24,
    alignItems: 'center',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#8B949E',
    textAlign: 'center',
    lineHeight: 22,
  },
  roomsContainer: {
    paddingHorizontal: 16,
  },
  roomCard: {
    marginBottom: 16,
    borderRadius: 16,
    overflow: 'hidden',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 8,
  },
  roomCardGradient: {
    backgroundColor: '#161B22',
    padding: 20,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#30363D',
  },
  roomCardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  roomIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },
  roomInfo: {
    flex: 1,
  },
  roomName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  roomDescription: {
    fontSize: 14,
    color: '#8B949E',
  },
  learningBadge: {
    backgroundColor: '#0D1117',
    padding: 6,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#4ECDC4',
  },
  roomStats: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  statDivider: {
    width: 1,
    height: 40,
    backgroundColor: '#30363D',
    marginHorizontal: 16,
  },
  statValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginTop: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#8B949E',
    marginTop: 2,
  },
  errorBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FF6B6B20',
    padding: 8,
    borderRadius: 8,
    marginBottom: 8,
  },
  errorText: {
    color: '#FF6B6B',
    fontSize: 12,
    marginLeft: 6,
  },
  roomCardFooter: {
    alignItems: 'flex-end',
  },
  footer: {
    padding: 24,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 12,
    color: '#6C7378',
    textAlign: 'center',
  },
});

export default RoomsScreen;