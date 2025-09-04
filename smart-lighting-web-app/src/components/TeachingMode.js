import React, { useState } from 'react';
import HomeAssistantAPI from '../services/HomeAssistantAPI';

const TeachingMode = ({ room, onClose }) => {
  const [brightness, setBrightness] = useState(50);
  const [temperature, setTemperature] = useState(3000);
  const [isTeaching, setIsTeaching] = useState(false);

  const handleTeach = async () => {
    setIsTeaching(true);
    try {
      await HomeAssistantAPI.teachRoom(
        room.id,
        brightness,
        room.supportsTemperature ? temperature : null
      );
      onClose();
    } catch (error) {
      console.error('Error teaching room:', error);
      alert('Failed to teach room settings. Please try again.');
    } finally {
      setIsTeaching(false);
    }
  };

  return (
    <div className="mode-panel teaching-panel">
      <h3>🎯 Teach New Settings</h3>
      
      <div className="slider-container">
        <div className="slider-label">
          <span>Brightness</span>
          <span>{brightness}%</span>
        </div>
        <input
          type="range"
          min="1"
          max="100"
          value={brightness}
          onChange={(e) => setBrightness(parseInt(e.target.value))}
          className="slider"
        />
      </div>

      {room.supportsTemperature && (
        <div className="slider-container">
          <div className="slider-label">
            <span>Temperature</span>
            <span>{temperature}K</span>
          </div>
          <input
            type="range"
            min="2000"
            max="6500"
            step="100"
            value={temperature}
            onChange={(e) => setTemperature(parseInt(e.target.value))}
            className="slider"
          />
        </div>
      )}

      <button
        className="primary-button"
        onClick={handleTeach}
        disabled={isTeaching}
      >
        {isTeaching ? 'Teaching...' : '✅ Teach This Setting'}
      </button>
    </div>
  );
};

export default TeachingMode;