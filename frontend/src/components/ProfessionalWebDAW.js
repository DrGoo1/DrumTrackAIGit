import React, { useState, useEffect, useRef, useCallback } from 'react';
import './ProfessionalWebDAW.css';

const ProfessionalWebDAW = ({ audioAnalysis, onBack, stemData }) => {
  // Core state management
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [tracks, setTracks] = useState([]);
  const [selectedTrack, setSelectedTrack] = useState(null);
  const [tempo, setTempo] = useState(120);
  const [isRecording, setIsRecording] = useState(false);
  
  // Mixer state
  const [mixerChannels, setMixerChannels] = useState({});
  const [masterVolume, setMasterVolume] = useState(0.8);
  const [levelMeters, setLevelMeters] = useState({});
  
  // Drum studio state
  const [drumPattern, setDrumPattern] = useState([]);
  const [selectedDrumKit, setSelectedDrumKit] = useState('rock');
  const [selectedDrummerStyle, setSelectedDrummerStyle] = useState('bonham');
  const [humanization, setHumanization] = useState({
    timing: 0.02,
    velocity: 0.15,
    groove: 0.5
  });
  
  // UI state
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [cpuUsage, setCpuUsage] = useState(0);
  
  // Refs for audio and canvas
  const audioContextRef = useRef(null);
  const timelineCanvasRef = useRef(null);
  const waveformCanvasRef = useRef(null);
  const wsRef = useRef(null);

  // Initialize WebDAW
  useEffect(() => {
    initializeWebDAW();
    setupWebSocket();
    
    return () => {
      cleanup();
    };
  }, []);

  const initializeWebDAW = async () => {
    try {
      // Initialize Web Audio API
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      
      // Load analysis data
      if (audioAnalysis) {
        setTempo(audioAnalysis.tempo || 120);
        setDuration(audioAnalysis.duration || 0);
      }
      
      // Load stem data
      if (stemData) {
        await loadStemTracks(stemData);
      }
      
      // Initialize mixer channels
      initializeMixer();
      
      // Start level meter updates
      startLevelMetering();
      
    } catch (error) {
      console.error('Failed to initialize WebDAW:', error);
    }
  };

  const setupWebSocket = () => {
    const wsUrl = `ws://localhost:8000/ws/webdaw`;
    wsRef.current = new WebSocket(wsUrl);
    
    wsRef.current.onopen = () => {
      console.log('WebSocket connected');
    };
    
    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };
    
    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  };

  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'level_update':
        setLevelMeters(data.levels);
        break;
      case 'transport_update':
        setIsPlaying(data.isPlaying);
        setCurrentTime(data.currentTime);
        break;
      case 'cpu_update':
        setCpuUsage(data.cpuUsage);
        break;
      default:
        console.log('Unknown WebSocket message:', data);
    }
  };

  const loadStemTracks = async (stemData) => {
    const newTracks = [];
    const newMixerChannels = {};
    
    for (const [stemType, audioData] of Object.entries(stemData)) {
      const trackId = `track_${newTracks.length}`;
      
      newTracks.push({
        id: trackId,
        name: stemType.charAt(0).toUpperCase() + stemType.slice(1),
        type: stemType,
        audioData: audioData,
        waveform: await generateWaveform(audioData),
        color: getTrackColor(stemType)
      });
      
      newMixerChannels[trackId] = {
        volume: 0.8,
        pan: 0,
        mute: false,
        solo: false,
        eq: { low: 0, mid: 0, high: 0 }
      };
    }
    
    setTracks(newTracks);
    setMixerChannels(newMixerChannels);
  };

  const generateWaveform = async (audioData) => {
    // Generate waveform visualization data
    const samples = audioData.length;
    const waveform = [];
    const chunkSize = Math.floor(samples / 1000);
    
    for (let i = 0; i < samples; i += chunkSize) {
      const chunk = audioData.slice(i, i + chunkSize);
      const peak = Math.max(...chunk.map(Math.abs));
      waveform.push(peak);
    }
    
    return waveform;
  };

  const getTrackColor = (stemType) => {
    const colors = {
      vocals: '#ff6b6b',
      drums: '#4ecdc4',
      bass: '#45b7d1',
      other: '#96ceb4',
      piano: '#feca57',
      guitar: '#ff9ff3'
    };
    return colors[stemType] || '#95a5a6';
  };

  // Transport controls
  const handlePlay = async () => {
    if (audioContextRef.current.state === 'suspended') {
      await audioContextRef.current.resume();
    }
    
    setIsPlaying(true);
    
    // Send to backend
    try {
      await fetch('/api/transport/play', { method: 'POST' });
    } catch (error) {
      console.error('Failed to start playback:', error);
    }
  };

  const handlePause = async () => {
    setIsPlaying(false);
    
    try {
      await fetch('/api/transport/pause', { method: 'POST' });
    } catch (error) {
      console.error('Failed to pause playback:', error);
    }
  };

  const handleStop = async () => {
    setIsPlaying(false);
    setCurrentTime(0);
    
    try {
      await fetch('/api/transport/stop', { method: 'POST' });
    } catch (error) {
      console.error('Failed to stop playback:', error);
    }
  };

  const handleSeek = async (position) => {
    setCurrentTime(position);
    
    try {
      await fetch('/api/transport/seek', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ position })
      });
    } catch (error) {
      console.error('Failed to seek:', error);
    }
  };

  // Mixer controls
  const updateMixerChannel = async (trackId, property, value) => {
    setMixerChannels(prev => ({
      ...prev,
      [trackId]: {
        ...prev[trackId],
        [property]: value
      }
    }));
    
    try {
      await fetch(`/api/mixer/${property}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ trackId, value })
      });
    } catch (error) {
      console.error(`Failed to update ${property}:`, error);
    }
  };

  // Drum studio functions
  const createDrumPattern = async () => {
    try {
      const response = await fetch('/api/drum-studio/create-pattern', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tempo,
          style: selectedDrummerStyle,
          kit: selectedDrumKit,
          humanization
        })
      });
      
      const pattern = await response.json();
      setDrumPattern(pattern);
      
    } catch (error) {
      console.error('Failed to create drum pattern:', error);
    }
  };

  // Level metering
  const startLevelMetering = () => {
    const updateLevels = () => {
      // This would normally get real-time data from audio processing
      const mockLevels = {};
      tracks.forEach(track => {
        mockLevels[track.id] = {
          peak: Math.random() * 0.8,
          rms: Math.random() * 0.6,
          lufs: -23 + Math.random() * 10
        };
      });
      setLevelMeters(mockLevels);
    };
    
    const interval = setInterval(updateLevels, 50);
    return () => clearInterval(interval);
  };

  // Canvas rendering
  useEffect(() => {
    drawTimeline();
    drawWaveforms();
  }, [currentTime, duration, tracks]);

  const drawTimeline = () => {
    const canvas = timelineCanvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.fillStyle = '#2c3e50';
    ctx.fillRect(0, 0, width, height);
    
    // Draw time rulers
    ctx.strokeStyle = '#34495e';
    ctx.lineWidth = 1;
    
    const pixelsPerSecond = width / duration;
    for (let i = 0; i < duration; i++) {
      const x = i * pixelsPerSecond;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    
    // Draw playhead
    const playheadX = (currentTime / duration) * width;
    ctx.strokeStyle = '#e74c3c';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(playheadX, 0);
    ctx.lineTo(playheadX, height);
    ctx.stroke();
  };

  const drawWaveforms = () => {
    const canvas = waveformCanvasRef.current;
    if (!canvas || tracks.length === 0) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.fillStyle = '#34495e';
    ctx.fillRect(0, 0, width, height);
    
    const trackHeight = height / tracks.length;
    
    tracks.forEach((track, index) => {
      const y = index * trackHeight;
      const centerY = y + trackHeight / 2;
      
      if (track.waveform) {
        ctx.strokeStyle = track.color;
        ctx.lineWidth = 1;
        ctx.beginPath();
        
        track.waveform.forEach((sample, i) => {
          const x = (i / track.waveform.length) * width;
          const amplitude = sample * (trackHeight / 4);
          
          if (i === 0) {
            ctx.moveTo(x, centerY - amplitude);
          } else {
            ctx.lineTo(x, centerY - amplitude);
          }
        });
        
        ctx.stroke();
      }
    });
  };

  const cleanup = () => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
    }
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e) => {
      if (e.code === 'Space') {
        e.preventDefault();
        isPlaying ? handlePause() : handlePlay();
      } else if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        // Save project
      }
    };
    
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [isPlaying]);

  return (
    <div className="professional-webdaw">
      {/* Header */}
      <div className="webdaw-header">
        <div className="project-info">
          <h2>Professional WebDAW</h2>
          <span className="project-status">Ready</span>
        </div>
        <div className="header-controls">
          <button className="btn-secondary" onClick={() => setShowExportDialog(true)}>
            Export
          </button>
          <button className="btn-primary" onClick={onBack}>
            Back to Analysis
          </button>
        </div>
        <div className="cpu-meter">
          CPU: {Math.round(cpuUsage)}%
        </div>
      </div>

      {/* Main content area */}
      <div className="webdaw-main">
        {/* Transport controls */}
        <div className="transport-section">
          <div className="transport-controls">
            <button 
              className={`transport-btn ${isRecording ? 'recording' : ''}`}
              onClick={() => setIsRecording(!isRecording)}
            >
              ⏺
            </button>
            <button className="transport-btn" onClick={handleStop}>⏹</button>
            <button className="transport-btn" onClick={isPlaying ? handlePause : handlePlay}>
              {isPlaying ? '⏸' : '▶'}
            </button>
          </div>
          
          <div className="timeline-container">
            <canvas 
              ref={timelineCanvasRef}
              className="timeline-canvas"
              width={800}
              height={60}
              onClick={(e) => {
                const rect = e.currentTarget.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const position = (x / rect.width) * duration;
                handleSeek(position);
              }}
            />
          </div>
          
          <div className="tempo-display">
            <label>Tempo:</label>
            <input 
              type="number" 
              value={tempo} 
              onChange={(e) => setTempo(parseInt(e.target.value))}
              min="60" 
              max="200"
            />
            <span>BPM</span>
          </div>
        </div>

        {/* Track area */}
        <div className="track-area">
          <canvas 
            ref={waveformCanvasRef}
            className="waveform-canvas"
            width={800}
            height={300}
          />
          
          <div className="track-list">
            {tracks.map(track => (
              <div 
                key={track.id} 
                className={`track-item ${selectedTrack === track.id ? 'selected' : ''}`}
                onClick={() => setSelectedTrack(track.id)}
              >
                <div className="track-name" style={{ color: track.color }}>
                  {track.name}
                </div>
                <div className="track-controls">
                  <button 
                    className={`btn-small ${mixerChannels[track.id]?.mute ? 'active' : ''}`}
                    onClick={() => updateMixerChannel(track.id, 'mute', !mixerChannels[track.id]?.mute)}
                  >
                    M
                  </button>
                  <button 
                    className={`btn-small ${mixerChannels[track.id]?.solo ? 'active' : ''}`}
                    onClick={() => updateMixerChannel(track.id, 'solo', !mixerChannels[track.id]?.solo)}
                  >
                    S
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Sidebar panels */}
      <div className="webdaw-sidebar">
        {/* Mixer panel */}
        <div className="mixer-panel">
          <h3>Mixer</h3>
          {tracks.map(track => {
            const channel = mixerChannels[track.id] || {};
            const levels = levelMeters[track.id] || {};
            
            return (
              <div key={track.id} className="mixer-channel">
                <div className="channel-name">{track.name}</div>
                
                {/* Level meter */}
                <div className="level-meter">
                  <div 
                    className="level-bar peak"
                    style={{ height: `${(levels.peak || 0) * 100}%` }}
                  />
                  <div 
                    className="level-bar rms"
                    style={{ height: `${(levels.rms || 0) * 100}%` }}
                  />
                </div>
                
                {/* Volume fader */}
                <input
                  type="range"
                  className="volume-fader"
                  min="0"
                  max="1"
                  step="0.01"
                  value={channel.volume || 0.8}
                  onChange={(e) => updateMixerChannel(track.id, 'volume', parseFloat(e.target.value))}
                />
                
                {/* Pan knob */}
                <div className="pan-control">
                  <input
                    type="range"
                    className="pan-knob"
                    min="-1"
                    max="1"
                    step="0.01"
                    value={channel.pan || 0}
                    onChange={(e) => updateMixerChannel(track.id, 'pan', parseFloat(e.target.value))}
                  />
                  <label>Pan</label>
                </div>
              </div>
            );
          })}
        </div>

        {/* Drum studio panel */}
        <div className="drum-studio-panel">
          <h3>Drum Studio</h3>
          
          <div className="drum-kit-selector">
            <label>Drum Kit:</label>
            <select value={selectedDrumKit} onChange={(e) => setSelectedDrumKit(e.target.value)}>
              <option value="rock">Rock Kit</option>
              <option value="jazz">Jazz Kit</option>
              <option value="electronic">Electronic Kit</option>
            </select>
          </div>
          
          <div className="drummer-style-selector">
            <label>Drummer Style:</label>
            <select value={selectedDrummerStyle} onChange={(e) => setSelectedDrummerStyle(e.target.value)}>
              <option value="bonham">John Bonham</option>
              <option value="peart">Neil Peart</option>
              <option value="copeland">Stewart Copeland</option>
            </select>
          </div>
          
          <div className="humanization-controls">
            <h4>Humanization</h4>
            
            <div className="control-group">
              <label>Timing Variation:</label>
              <input
                type="range"
                min="0"
                max="0.1"
                step="0.001"
                value={humanization.timing}
                onChange={(e) => setHumanization(prev => ({
                  ...prev,
                  timing: parseFloat(e.target.value)
                }))}
              />
              <span>{Math.round(humanization.timing * 100)}%</span>
            </div>
            
            <div className="control-group">
              <label>Velocity Variation:</label>
              <input
                type="range"
                min="0"
                max="0.3"
                step="0.01"
                value={humanization.velocity}
                onChange={(e) => setHumanization(prev => ({
                  ...prev,
                  velocity: parseFloat(e.target.value)
                }))}
              />
              <span>{Math.round(humanization.velocity * 100)}%</span>
            </div>
            
            <div className="control-group">
              <label>Groove Intensity:</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={humanization.groove}
                onChange={(e) => setHumanization(prev => ({
                  ...prev,
                  groove: parseFloat(e.target.value)
                }))}
              />
              <span>{Math.round(humanization.groove * 100)}%</span>
            </div>
          </div>
          
          <button className="btn-primary" onClick={createDrumPattern}>
            Create Pattern
          </button>
        </div>
      </div>

      {/* Export dialog */}
      {showExportDialog && (
        <div className="modal-overlay">
          <div className="export-dialog">
            <h3>Export Audio</h3>
            <div className="export-options">
              <div className="format-selector">
                <label>Format:</label>
                <select>
                  <option value="wav">WAV (Uncompressed)</option>
                  <option value="mp3">MP3 (320kbps)</option>
                  <option value="flac">FLAC (Lossless)</option>
                </select>
              </div>
              
              <div className="quality-selector">
                <label>Quality:</label>
                <select>
                  <option value="high">High (48kHz/24-bit)</option>
                  <option value="standard">Standard (44.1kHz/16-bit)</option>
                </select>
              </div>
            </div>
            
            <div className="dialog-buttons">
              <button className="btn-secondary" onClick={() => setShowExportDialog(false)}>
                Cancel
              </button>
              <button className="btn-primary">
                Export
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Loading overlay */}
      {isLoading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
          <div className="loading-text">Processing...</div>
        </div>
      )}
    </div>
  );
};

export default ProfessionalWebDAW;
