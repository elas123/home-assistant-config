class HomeAssistantAPI {
  static baseURL = 'http://192.168.10.153:8123';
  static token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIxZjE1MGVlMjc0ODc0YTVhOWQ2MzBmZjZhMTA3NDA3ZCIsImlhdCI6MTc1NjkzODk2MSwiZXhwIjoyMDcyMjk4OTYxfQ.O5UTmlzju3JaMhbK-Y2VlKoOlgWq4vSwhoj7QYnraNE';

  static async makeRequest(endpoint, method = 'GET', data = null) {
    const url = `${this.baseURL}${endpoint}`;
    const options = {
      method,
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json',
      },
    };

    if (data) {
      options.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, options);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  static async teachRoom(room, brightness, temperature = null) {
    const serviceData = {
      room,
      brightness,
    };

    if (temperature !== null) {
      serviceData.temperature = temperature;
    }

    return this.makeRequest('/api/services/pyscript/als_teach_room', 'POST', serviceData);
  }

  static async startRampRecording(room, sessionName) {
    const serviceData = {
      room,
      session_name: sessionName,
    };

    return this.makeRequest('/api/services/pyscript/start_ramp_recording', 'POST', serviceData);
  }

  static async stopRampRecording(room) {
    const serviceData = {
      room,
    };

    return this.makeRequest('/api/services/pyscript/stop_ramp_recording', 'POST', serviceData);
  }

  static async fetchEntityState(entityId) {
    return this.makeRequest(`/api/states/${entityId}`);
  }

  static async getRampSessions(room) {
    const serviceData = {
      room,
    };

    const response = await this.makeRequest('/api/services/pyscript/get_ramp_sessions', 'POST', serviceData);
    return response.sessions || [];
  }

  static async getLearnedData(room) {
    const serviceData = {
      room,
    };

    const response = await this.makeRequest('/api/services/pyscript/als_get_learned_data', 'POST', serviceData);
    return response.data || [];
  }

  static async deleteLearnedData(room, dataId) {
    const serviceData = {
      room,
      data_id: dataId,
    };

    return this.makeRequest('/api/services/pyscript/als_delete_learned_data', 'POST', serviceData);
  }
}

export default HomeAssistantAPI;