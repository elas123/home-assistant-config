import { HA_CONFIG } from '../config/rooms';

class HomeAssistantAPI {
  constructor() {
    this.baseUrl = HA_CONFIG.baseUrl;
    this.token = HA_CONFIG.longLivedToken;
  }

  async makeRequest(endpoint, method = 'GET', data = null) {
    const config = {
      method,
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json',
      },
    };

    if (data && (method === 'POST' || method === 'PUT')) {
      config.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(`${this.baseUrl}/api/${endpoint}`, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Get current state of an entity
  async getEntityState(entityId) {
    return await this.makeRequest(`states/${entityId}`);
  }

  // Get states of multiple entities
  async getStates(entityIds = null) {
    const allStates = await this.makeRequest('states');
    
    if (entityIds && Array.isArray(entityIds)) {
      return allStates.filter(state => entityIds.includes(state.entity_id));
    }
    
    return allStates;
  }

  // Call a service (like turning on lights, teaching, etc.)
  async callService(domain, service, serviceData = {}) {
    return await this.makeRequest(
      `services/${domain}/${service}`,
      'POST',
      serviceData
    );
  }

  // Get room data including current brightness, temperature, and learned values
  async getRoomData(room) {
    try {
      const states = [];
      
      // Get all relevant entity states
      for (const [key, entityId] of Object.entries(room.entities || {})) {
        if (typeof entityId === 'string') {
          try {
            const state = await this.getEntityState(entityId);
            states.push({ key, ...state });
          } catch (error) {
            console.warn(`Could not fetch ${entityId}:`, error);
          }
        } else if (Array.isArray(entityId)) {
          // Handle arrays of entities (like lights)
          for (const id of entityId) {
            try {
              const state = await this.getEntityState(id);
              states.push({ key, ...state });
            } catch (error) {
              console.warn(`Could not fetch ${id}:`, error);
            }
          }
        }
      }

      return {
        roomId: room.id,
        roomName: room.name,
        states,
        currentBrightness: this.extractValue(states, 'brightness_sensor'),
        currentTemperature: this.extractValue(states, 'temperature_sensor'),
        learnedBrightness: this.extractValue(states, 'learned_brightness'),
        lightStates: this.extractLightStates(states),
        hasLearning: room.hasLearning,
      };
    } catch (error) {
      console.error(`Error getting room data for ${room.name}:`, error);
      throw error;
    }
  }

  // Extract a value from states array
  extractValue(states, key) {
    const state = states.find(s => s.key === key);
    return state ? parseFloat(state.state) || state.state : null;
  }

  // Extract light states
  extractLightStates(states) {
    return states.filter(s => s.entity_id && s.entity_id.startsWith('light.'));
  }

  // Teach the room new settings
  async teachRoom(roomId, brightness, temperature = null) {
    try {
      const serviceData = {
        room: roomId,
        brightness: brightness
      };

      if (temperature !== null) {
        serviceData.temperature = temperature;
      }

      return await this.callService('pyscript', 'als_teach_room', serviceData);
    } catch (error) {
      console.error('Error teaching room:', error);
      throw error;
    }
  }

  // Get learned data from the database
  async getLearnedData(roomId) {
    try {
      // This would call a custom service to query the SQLite database
      return await this.callService('pyscript', 'als_get_learned_data', { room: roomId });
    } catch (error) {
      console.error('Error getting learned data:', error);
      return [];
    }
  }

  // Apply current intelligent lighting settings to lights
  async applyIntelligentLighting(room) {
    try {
      const roomData = await this.getRoomData(room);
      const brightness = roomData.currentBrightness;
      const temperature = roomData.currentTemperature;

      // Turn on lights with intelligent settings
      for (const light of room.entities.lights || []) {
        await this.callService('light', 'turn_on', {
          entity_id: light,
          brightness_pct: brightness,
          color_temp_kelvin: temperature,
          transition: 2
        });
      }

      return { success: true, brightness, temperature };
    } catch (error) {
      console.error('Error applying intelligent lighting:', error);
      throw error;
    }
  }

  // Get time-based automation predictions
  async getAutomationPredictions(roomId) {
    try {
      // This would call a service that analyzes learned data patterns
      return await this.callService('pyscript', 'als_get_automation_predictions', { 
        room: roomId 
      });
    } catch (error) {
      console.error('Error getting automation predictions:', error);
      return [];
    }
  }

  // Test connection to Home Assistant
  async testConnection() {
    try {
      await this.makeRequest('');
      return true;
    } catch (error) {
      console.error('Connection test failed:', error);
      return false;
    }
  }
}

export default new HomeAssistantAPI();