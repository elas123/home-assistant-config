import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet } from 'react-native';

import RoomsScreen from './src/screens/RoomsScreen';
import RoomDetailScreen from './src/screens/RoomDetailScreen';
import TeachingModeScreen from './src/screens/TeachingModeScreen';

const Stack = createStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <StatusBar style="light" backgroundColor="#1a1a2e" />
      <Stack.Navigator
        initialRouteName="Rooms"
        screenOptions={{
          headerStyle: {
            backgroundColor: '#16213e',
            elevation: 0,
            shadowOpacity: 0,
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
            fontSize: 18,
          },
        }}
      >
        <Stack.Screen 
          name="Rooms" 
          component={RoomsScreen}
          options={{ 
            title: 'Smart Light Control',
            headerStyle: {
              backgroundColor: '#1a1a2e',
            }
          }}
        />
        <Stack.Screen 
          name="RoomDetail" 
          component={RoomDetailScreen}
          options={({ route }) => ({ 
            title: `${route.params.room.name}`,
            headerStyle: {
              backgroundColor: '#16213e',
            }
          })}
        />
        <Stack.Screen 
          name="TeachingMode" 
          component={TeachingModeScreen}
          options={{ 
            title: 'Teaching Mode',
            headerStyle: {
              backgroundColor: '#0f3460',
            }
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
});