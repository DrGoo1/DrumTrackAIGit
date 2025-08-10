import React, { useState, useEffect, useRef } from 'react';
import TransportControls from './TransportControls';
import MixerControls from './MixerControls';
import DrumStudio from './DrumStudio';
import WaveformDisplay from './WaveformDisplay';
import TrackList from './TrackList';
import ExportDialog from './ExportDialog';
import './ModularWebDAW.css';

const ModularWebDAW = ({ audioAnalysis, onBack, stemData }) => {
  // Core state
  const [isPlaying, setIsPlaying] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [tempo, setTempo] = useState(120);
  
  // Track and mixer state
  const [tracks, setTracks] = useState([]);
  const [selectedTrack, setSelectedTrack] = useState(null);
  const [mixerChannels, setMixerChannels] = useState({});
  const [masterVolume, setMasterVolume] = useState(0.8);
  const [levelMeters, setLevelMeters] = useState({});
  
  // Drum studio state
  const [selectedDrumKit, setSelectedDrumKit] = useState('rock');
  const [selectedDrummerStyle, setSelectedDrummerStyle] = useState('bonham');
  const [humanization, setHumanization] = useState({
    timing: 0.02,
    velocity: 0.15,
    groove: 0.5
  });
  
  // UI state
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [cpuUsage, setCpuUsage] = useState(0);
  
  // WebSocket ref
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
      // Load analysis data
      if (audioAnalysis) {
        setTempo(audioAnalysis.tempo || 120);
        setDuration(audioAnalysis.duration || 0);
      }
      
      // Load stem data
      if (stemData) {
        await loadStemTracks(stemData);
      }
      
      // Start level metering
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
        solo: false
      };
    }
    
    setTracks(newTracks);
    setMixerChannels(newMixerChannels);
  };

  const generateWaveform = async (audioData) => {
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

  // Transport handlers
  const handlePlay = async () => {
    setIsPlaying(true);
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

  const handleRecord = () => {
    setIsRecording(!isRecording);
  };

  // Mixer handlers
  const handleChannelUpdate = async (trackId, property, value) => {
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

  // Track handlers
  const handleTrackSelect = (trackId) => {
    setSelectedTrack(trackId);
  };

  const handleAddTrack = () => {
    // Trigger file input
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'audio/*';
    input.multiple = true;
    input.onchange = handleFileUpload;
    input.click();
  };

  const handleFileUpload = async (event) => {
    const files = Array.from(event.target.files);
    // Handle file upload logic here
    console.log('Files to upload:', files);
  };

  // Drum studio handlers
  const handleCreatePattern = async () => {
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
      console.log('Created drum pattern:', pattern);
      
    } catch (error) {
      console.error('Failed to create drum pattern:', error);
    }
  };

  // Export handler
  const handleExport = async (exportSettings) => {
    setIsExporting(true);
    try {
      const response = await fetch('/api/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(exportSettings)
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `export.${exportSettings.format}`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
      setShowExportDialog(false);
    }
  };

  // Level metering
  const startLevelMetering = () => {
    const updateLevels = () => {
      const mockLevels = {};
      tracks.forEach(track => {
        mockLevels[track.id] = {
          peak: Math.random() * 0.8,
          rms: Math.random() * 0.6
        };
      });
      setLevelMeters(mockLevels);
    };
    
    const interval = setInterval(updateLevels, 50);
    return () => clearInterval(interval);
  };

  const cleanup = () => {
    if (wsRef.current) {
      wsRef.current.close();
    }
  };

  return (
    <div className="modular-webdaw">
      {/* Header */}
      <div className="webdaw-header">
        <div className="project-info">
          <h2>Professional WebDAW</h2>
          <span className="project-status">Ready</span>
        </div>
        <div className="header-controls">
          <button 
            className="btn-secondary" 
            onClick={() => setShowExportDialog(true)}
          >
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

      {/* Main content */}
      <div className="webdaw-content">
        <div className="main-area">
          {/* Transport Controls */}
          <TransportControls
            isPlaying={isPlaying}
            isRecording={isRecording}
            currentTime={currentTime}
            duration={duration}
            tempo={tempo}
            onPlay={handlePlay}
            onPause={handlePause}
            onStop={handleStop}
            onRecord={handleRecord}
            onSeek={handleSeek}
            onTempoChange={setTempo}
          />

          {/* Waveform Display */}
          <WaveformDisplay
            tracks={tracks}
            currentTime={currentTime}
            duration={duration}
            selectedTrack={selectedTrack}
            onTrackSelect={handleTrackSelect}
            onTimeSeek={handleSeek}
          />

          {/* Track List */}
          <TrackList
            tracks={tracks}
            selectedTrack={selectedTrack}
            mixerChannels={mixerChannels}
            onTrackSelect={handleTrackSelect}
            onTrackMute={(trackId) => handleChannelUpdate(trackId, 'mute', !mixerChannels[trackId]?.mute)}
            onTrackSolo={(trackId) => handleChannelUpdate(trackId, 'solo', !mixerChannels[trackId]?.solo)}
            onTrackDelete={(trackId) => {
              setTracks(prev => prev.filter(t => t.id !== trackId));
              setMixerChannels(prev => {
                const newChannels = { ...prev };
                delete newChannels[trackId];
                return newChannels;
              });
            }}
            onAddTrack={handleAddTrack}
          />
        </div>

        {/* Sidebar */}
        <div className="webdaw-sidebar">
          {/* Mixer */}
          <MixerControls
            tracks={tracks}
            mixerChannels={mixerChannels}
            levelMeters={levelMeters}
            masterVolume={masterVolume}
            onChannelUpdate={handleChannelUpdate}
            onMasterVolumeChange={setMasterVolume}
          />

          {/* Drum Studio */}
          <DrumStudio
            selectedDrumKit={selectedDrumKit}
            selectedDrummerStyle={selectedDrummerStyle}
            humanization={humanization}
            tempo={tempo}
            onDrumKitChange={setSelectedDrumKit}
            onDrummerStyleChange={setSelectedDrummerStyle}
            onHumanizationChange={setHumanization}
            onCreatePattern={handleCreatePattern}
          />
        </div>
      </div>

      {/* Export Dialog */}
      <ExportDialog
        isOpen={showExportDialog}
        onClose={() => setShowExportDialog(false)}
        onExport={handleExport}
        isExporting={isExporting}
      />
    </div>
  );
};

export default ModularWebDAW;
