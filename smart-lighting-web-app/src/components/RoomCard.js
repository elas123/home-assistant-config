import React, { useState, useEffect } from 'react';
import HomeAssistantAPI from '../services/HomeAssistantAPI';

const RoomCard = ({ room, isSelected, onSelect }) => {
  const [currentBrightness, setCurrentBrightness] = useState(room.brightness);
  const [currentTemperature, setCurrentTemperature] = useState(room.temperature);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const refreshData = async () => {
    setIsRefreshing(true);
    try {
      const brightnessState = await HomeAssistantAPI.fetchEntityState(room.brightnessEntity);
      const brightnessValue = parseInt(brightnessState.state);
      if (!isNaN(brightnessValue)) {
        setCurrentBrightness(brightnessValue);
      }

      if (room.supportsTemperature) {
        const tempState = await HomeAssistantAPI.fetchEntityState(room.temperatureEntity);
        const tempValue = parseInt(tempState.state);
        if (!isNaN(tempValue)) {
          setCurrentTemperature(tempValue);
        }
      }
    } catch (error) {
      console.error('Error fetching room data:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    if (isSelected) {
      refreshData();
    }
  }, [isSelected]);

  return (
    <div 
      className={`room-card ${isSelected ? 'selected' : ''}`}
      onClick={onSelect}
    >
      <div className="room-header">
        <div className="room-icon">
          {room.icon}
        </div>
        <h3 className="room-name">{room.name}</h3>
      </div>
      
      <div className="room-status">
        <div className="status-item">
          <span>☀️</span>
          <span>{currentBrightness}%</span>
        </div>
        
        {room.supportsTemperature && (
          <div className="status-item">
            <span>🌡️</span>
            <span>{currentTemperature}K</span>
          </div>
        )}
        
        <button 
          className="refresh-button"
          onClick={(e) => {
            e.stopPropagation();
            refreshData();
          }}
          disabled={isRefreshing}
        >
          {isRefreshing ? '↻' : '🔄'}
        </button>
      </div>
    </div>
  );
};

export default RoomCard;