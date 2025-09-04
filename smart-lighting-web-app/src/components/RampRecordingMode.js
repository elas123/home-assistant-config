import React, { useState, useEffect } from 'react';
import HomeAssistantAPI from '../services/HomeAssistantAPI';

const RampRecordingMode = ({ room }) => {
  const [sessionName, setSessionName] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [recordingStartTime, setRecordingStartTime] = useState(null);
  const [showSessions, setShowSessions] = useState(false);
  const [sessions, setSessions] = useState([]);

  const startRecording = async () => {
    if (!sessionName.trim()) return;
    
    try {
      await HomeAssistantAPI.startRampRecording(room.id, sessionName);
      setIsRecording(true);
      setRecordingStartTime(new Date());
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Failed to start recording. Please try again.');
    }
  };

  const stopRecording = async () => {
    try {
      await HomeAssistantAPI.stopRampRecording(room.id);
      setIsRecording(false);
      setRecordingStartTime(null);
      setSessionName('');
      await loadSessions();
    } catch (error) {
      console.error('Error stopping recording:', error);
      alert('Failed to stop recording. Please try again.');
    }
  };

  const loadSessions = async () => {
    try {
      const sessionsData = await HomeAssistantAPI.getRampSessions(room.id);
      setSessions(sessionsData);
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const formatDuration = (startTime) => {
    const now = new Date();
    const start = new Date(startTime);
    const diff = Math.floor((now - start) / 1000);
    const minutes = Math.floor(diff / 60);
    const seconds = diff % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className="mode-panel recording-panel">
      <h3>📹 Ramp Recording</h3>
      
      {!isRecording ? (
        <div>
          <div className="slider-container">
            <label>Session Name</label>
            <input
              type="text"
              value={sessionName}
              onChange={(e) => setSessionName(e.target.value)}
              placeholder="Enter session name (e.g., Morning Routine)"
              className="input-field"
            />
          </div>

          <button
            className="primary-button"
            onClick={startRecording}
            disabled={!sessionName.trim()}
          >
            🔴 Start Recording
          </button>

          <button
            className="secondary-button"
            onClick={() => {
              loadSessions();
              setShowSessions(true);
            }}
          >
            📋 View Past Sessions
          </button>
        </div>
      ) : (
        <div>
          <div className="recording-status">
            <div className="recording-indicator"></div>
            <div>
              <strong>Recording: {sessionName}</strong>
              <div style={{ fontSize: '0.8rem', color: '#ccc' }}>
                Started: {recordingStartTime && recordingStartTime.toLocaleTimeString()}
              </div>
            </div>
          </div>

          <div className="recording-info">
            Manually adjust your lights now. All brightness changes will be recorded for seamless automation.
          </div>

          <button
            className="primary-button"
            onClick={stopRecording}
            style={{ background: 'linear-gradient(135deg, #f44336, #e57373)' }}
          >
            ⏹️ Stop Recording
          </button>
        </div>
      )}

      {showSessions && (
        <div className="sessions-modal" onClick={() => setShowSessions(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">{room.name} Sessions</h3>
              <button className="close-button" onClick={() => setShowSessions(false)}>
                ×
              </button>
            </div>
            
            <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
              {sessions.length === 0 ? (
                <p style={{ textAlign: 'center', color: '#ccc' }}>No sessions recorded yet</p>
              ) : (
                sessions.map((session) => (
                  <div key={session.id} className="session-item">
                    <div className="session-header">{session.sessionName}</div>
                    <div className="session-details">
                      <div style={{ marginBottom: '4px' }}>
                        <span className={`session-status status-${session.status}`}>
                          {session.status}
                        </span>
                        <span style={{ marginLeft: '12px' }}>
                          {session.dataPoints} data points
                        </span>
                      </div>
                      <div>Started: {formatTime(session.startTime)}</div>
                      {session.endTime && (
                        <div>Ended: {formatTime(session.endTime)}</div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RampRecordingMode;