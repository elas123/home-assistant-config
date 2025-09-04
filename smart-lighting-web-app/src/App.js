import React, { useState } from 'react';
import './index.css';
import RoomCard from './components/RoomCard';
import TeachingMode from './components/TeachingMode';
import RampRecordingMode from './components/RampRecordingMode';
import { rooms } from './data/rooms';

function App() {
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [teachingMode, setTeachingMode] = useState(false);
  const [rampRecordingMode, setRampRecordingMode] = useState(false);

  const handleRoomSelect = (room) => {
    if (selectedRoom?.id === room.id) {
      setSelectedRoom(null);
      setTeachingMode(false);
      setRampRecordingMode(false);
    } else {
      setSelectedRoom(room);
      setTeachingMode(false);
      setRampRecordingMode(false);
    }
  };

  const handleModeToggle = (mode) => {
    if (mode === 'teaching') {
      setTeachingMode(!teachingMode);
      if (!teachingMode) setRampRecordingMode(false);
    } else if (mode === 'recording') {
      setRampRecordingMode(!rampRecordingMode);
      if (!rampRecordingMode) setTeachingMode(false);
    }
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>Smart Lighting</h1>
          <p style={{ margin: '8px 0 0 0', color: '#ccc', fontSize: '1rem' }}>
            Teach your lights and record seamless transitions
          </p>
        </header>

        <div className="rooms-grid">
          {rooms.map((room) => (
            <RoomCard
              key={room.id}
              room={room}
              isSelected={selectedRoom?.id === room.id}
              onSelect={() => handleRoomSelect(room)}
            />
          ))}
        </div>

        {selectedRoom && (
          <div className="controls-section">
            <div className="mode-toggles">
              <button
                className={`toggle-button ${teachingMode ? 'active' : ''}`}
                onClick={() => handleModeToggle('teaching')}
              >
                🎯 Teaching Mode
              </button>
              <button
                className={`toggle-button ${rampRecordingMode ? 'active' : ''}`}
                onClick={() => handleModeToggle('recording')}
              >
                📹 Ramp Recording
              </button>
            </div>

            {teachingMode && (
              <TeachingMode
                room={selectedRoom}
                onClose={() => setTeachingMode(false)}
              />
            )}

            {rampRecordingMode && (
              <RampRecordingMode
                room={selectedRoom}
              />
            )}
          </div>
        )}

        {!selectedRoom && (
          <div style={{ 
            textAlign: 'center', 
            padding: '40px 20px', 
            color: '#666',
            fontSize: '1.1rem' 
          }}>
            <p>💡 Select a room to get started</p>
            <p style={{ fontSize: '0.9rem', marginTop: '16px', lineHeight: '1.5' }}>
              Choose a room above to teach lighting preferences or record manual brightness changes 
              for seamless automation.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;