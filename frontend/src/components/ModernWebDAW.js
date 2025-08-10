import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Play, Pause, Square, SkipBack, SkipForward, Volume2, Settings, Mic, Headphones, Save, FolderOpen, Download } from 'lucide-react';
import './ModernWebDAW.css';

const ModernWebDAW = ({ stemData, audioAnalysis, onBack }) => {
  // Core transport state
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(240); // 4 minutes default
  const [tempo, setTempo] = useState(120);
  const [timeSignature, setTimeSignature] = useState('4/4');
  
  // Track and mixer state
  const [tracks, setTracks] = useState([]);
  const [selectedTrack, setSelectedTrack] = useState(null);
  const [masterVolume, setMasterVolume] = useState(0.75);
  const [zoomLevel, setZoomLevel] = useState(1);
  
  // View state
  const [currentView, setCurrentView] = useState('arrangement'); // arrangement, mixer, edit
  const [showMixer, setShowMixer] = useState(true);
  const [showBrowser, setShowBrowser] = useState(false);
  const [showInspector, setShowInspector] = useState(true);
  
  // Drum studio state
  const [showDrumStudio, setShowDrumStudio] = useState(false);
  const [drumPattern, setDrumPattern] = useState(Array(16).fill().map(() => ({
    kick: false, snare: false, hihat: false, openhat: false, crash: false, ride: false
  })));
  const [currentStep, setCurrentStep] = useState(0);
  const [drumTempo, setDrumTempo] = useState(120);
  
  // Refs
  const timelineRef = useRef(null);
  const waveformCanvasRef = useRef(null);
  const audioContextRef = useRef(null);

  // Initialize WebDAW
  useEffect(() => {
    initializeWebDAW();
    return () => cleanup();
  }, []);

  const initializeWebDAW = async () => {
    try {
      // Initialize Web Audio API
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      
      // Load stem data if provided
      if (stemData && Object.keys(stemData).length > 0) {
        await loadStemTracks(stemData);
      } else {
        // Create default tracks
        createDefaultTracks();
      }
      
      // Load audio analysis
      if (audioAnalysis) {
        setTempo(audioAnalysis.tempo || 120);
        setDuration(audioAnalysis.duration || 240);
        setTimeSignature(audioAnalysis.timeSignature || '4/4');
      }
      
      // Start animation loop
      startAnimationLoop();
      
    } catch (error) {
      console.error('Failed to initialize WebDAW:', error);
    }
  };

  const loadStemTracks = async (stemData) => {
    const newTracks = [];
    const colors = ['#e74c3c', '#f39c12', '#2ecc71', '#9b59b6', '#3498db', '#1abc9c'];
    
    for (const [stemType, audioData] of Object.entries(stemData)) {
      const waveformData = await generateWaveform(audioData);
      
      newTracks.push({
        id: `track_${newTracks.length}`,
        name: stemType.charAt(0).toUpperCase() + stemType.slice(1),
        type: 'audio',
        stemType: stemType,
        color: colors[newTracks.length % colors.length],
        volume: 0.8,
        pan: 0,
        mute: false,
        solo: false,
        armed: false,
        waveform: waveformData,
        audioData: audioData,
        effects: [],
        sends: { reverb: 0, delay: 0 }
      });
    }
    
    setTracks(newTracks);
    console.log('Loaded stem tracks:', newTracks.map(t => t.name));
  };

  const createDefaultTracks = () => {
    const defaultTracks = [
      { id: 'track_0', name: 'Bass', type: 'audio', color: '#e74c3c', volume: 0.8, pan: 0, mute: false, solo: false, armed: false, effects: [], sends: { reverb: 0, delay: 0 } },
      { id: 'track_1', name: 'Vocals', type: 'audio', color: '#f39c12', volume: 0.8, pan: 0, mute: false, solo: false, armed: false, effects: [], sends: { reverb: 0.2, delay: 0 } },
      { id: 'track_2', name: 'Drums', type: 'audio', color: '#2ecc71', volume: 0.85, pan: 0, mute: false, solo: false, armed: false, effects: [], sends: { reverb: 0.1, delay: 0 } },
      { id: 'track_3', name: 'Other', type: 'audio', color: '#9b59b6', volume: 0.75, pan: 0, mute: false, solo: false, armed: false, effects: [], sends: { reverb: 0.15, delay: 0 } }
    ];
    setTracks(defaultTracks);
  };

  const generateWaveform = async (audioData) => {
    if (!audioData || !audioData.length) return [];
    
    const samples = audioData.length;
    const waveform = [];
    const samplesPerPixel = Math.floor(samples / 1000); // 1000 pixels wide
    
    for (let i = 0; i < 1000; i++) {
      let min = 0, max = 0;
      for (let j = 0; j < samplesPerPixel; j++) {
        const sample = audioData[i * samplesPerPixel + j] || 0;
        if (sample < min) min = sample;
        if (sample > max) max = sample;
      }
      waveform.push({ min, max });
    }
    
    return waveform;
  };

  const startAnimationLoop = () => {
    const animate = () => {
      if (isPlaying) {
        setCurrentTime(prev => Math.min(prev + 0.1, duration));
        setCurrentStep(prev => (prev + 1) % 16);
      }
      requestAnimationFrame(animate);
    };
    animate();
  };

  const cleanup = () => {
    if (audioContextRef.current) {
      audioContextRef.current.close();
    }
  };

  // Transport controls
  const handlePlay = () => {
    setIsPlaying(!isPlaying);
    if (audioContextRef.current?.state === 'suspended') {
      audioContextRef.current.resume();
    }
  };

  const handleStop = () => {
    setIsPlaying(false);
    setCurrentTime(0);
    setCurrentStep(0);
  };

  const handleSeek = (position) => {
    setCurrentTime(position);
  };

  // Track controls
  const updateTrack = (trackId, property, value) => {
    setTracks(prev => prev.map(track => 
      track.id === trackId ? { ...track, [property]: value } : track
    ));
  };

  const toggleMute = (trackId) => {
    updateTrack(trackId, 'mute', !tracks.find(t => t.id === trackId)?.mute);
  };

  const toggleSolo = (trackId) => {
    updateTrack(trackId, 'solo', !tracks.find(t => t.id === trackId)?.solo);
  };

  const toggleArm = (trackId) => {
    updateTrack(trackId, 'armed', !tracks.find(t => t.id === trackId)?.armed);
  };

  // Drum studio functions
  const toggleDrumStep = (step, drum) => {
    setDrumPattern(prev => prev.map((stepData, index) => 
      index === step ? { ...stepData, [drum]: !stepData[drum] } : stepData
    ));
  };

  const clearDrumPattern = () => {
    setDrumPattern(Array(16).fill().map(() => ({
      kick: false, snare: false, hihat: false, openhat: false, crash: false, ride: false
    })));
  };

  const randomizeDrumPattern = () => {
    setDrumPattern(Array(16).fill().map(() => ({
      kick: Math.random() > 0.7,
      snare: Math.random() > 0.6,
      hihat: Math.random() > 0.4,
      openhat: Math.random() > 0.8,
      crash: Math.random() > 0.9,
      ride: Math.random() > 0.7
    })));
  };

  // Format time display
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="modern-webdaw">
      {/* Top Menu Bar */}
      <div className="menu-bar">
        <div className="menu-section">
          <button className="menu-btn"><FolderOpen size={16} /> File</button>
          <button className="menu-btn">Edit</button>
          <button className="menu-btn">View</button>
          <button className="menu-btn">Track</button>
          <button className="menu-btn">Mix</button>
          <button className="menu-btn">Options</button>
        </div>
        <div className="project-info">
          <span className="project-name">DrumTracKAI Session</span>
          <span className="project-status">● Recording</span>
        </div>
        <div className="menu-section">
          <button className="menu-btn"><Save size={16} /></button>
          <button className="menu-btn"><Download size={16} /></button>
          <button className="menu-btn"><Settings size={16} /></button>
        </div>
      </div>

      {/* Transport Bar */}
      <div className="transport-bar">
        <div className="transport-controls">
          <button className="transport-btn" onClick={() => handleSeek(0)}>
            <SkipBack size={18} />
          </button>
          <button className="transport-btn play-btn" onClick={handlePlay}>
            {isPlaying ? <Pause size={20} /> : <Play size={20} />}
          </button>
          <button className="transport-btn" onClick={handleStop}>
            <Square size={18} />
          </button>
          <button className="transport-btn">
            <SkipForward size={18} />
          </button>
        </div>
        
        <div className="time-display">
          <div className="time-info">
            <span className="current-time">{formatTime(currentTime)}</span>
            <span className="separator">/</span>
            <span className="total-time">{formatTime(duration)}</span>
          </div>
          <div className="tempo-info">
            <input 
              type="number" 
              value={tempo} 
              onChange={(e) => setTempo(parseInt(e.target.value))}
              className="tempo-input"
              min="60"
              max="200"
            />
            <span>BPM</span>
            <span className="time-sig">{timeSignature}</span>
          </div>
        </div>

        <div className="master-controls">
          <div className="master-volume">
            <Volume2 size={16} />
            <input 
              type="range" 
              min="0" 
              max="1" 
              step="0.01"
              value={masterVolume}
              onChange={(e) => setMasterVolume(parseFloat(e.target.value))}
              className="volume-slider"
            />
            <span>{Math.round(masterVolume * 100)}%</span>
          </div>
          <button className="record-btn">
            <Mic size={16} />
          </button>
          <button className="monitor-btn">
            <Headphones size={16} />
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="main-content">
        {/* Left Sidebar - Browser */}
        {showBrowser && (
          <div className="browser-panel">
            <div className="browser-header">
              <h3>Browser</h3>
              <button onClick={() => setShowBrowser(false)}>×</button>
            </div>
            <div className="browser-content">
              <div className="browser-section">
                <h4>Stems</h4>
                <div className="file-list">
                  {Object.keys(stemData || {}).map(stem => (
                    <div key={stem} className="file-item">
                      <span className="file-icon">🎵</span>
                      <span>{stem}.wav</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="browser-section">
                <h4>Instruments</h4>
                <div className="file-list">
                  <div className="file-item">
                    <span className="file-icon">🥁</span>
                    <span>Drum Kit</span>
                  </div>
                  <div className="file-item">
                    <span className="file-icon">🎹</span>
                    <span>Piano</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Center - Arrangement View */}
        <div className="arrangement-area">
          {/* Track Headers */}
          <div className="track-headers">
            <div className="track-header master-track">
              <div className="track-name">Master</div>
              <div className="track-controls">
                <div className="volume-control">
                  <input 
                    type="range" 
                    min="0" 
                    max="1" 
                    step="0.01"
                    value={masterVolume}
                    onChange={(e) => setMasterVolume(parseFloat(e.target.value))}
                    className="track-volume"
                  />
                </div>
              </div>
            </div>
            
            {tracks.map(track => (
              <div key={track.id} className={`track-header ${selectedTrack === track.id ? 'selected' : ''}`}>
                <div className="track-color" style={{ backgroundColor: track.color }}></div>
                <div className="track-info">
                  <div className="track-name">{track.name}</div>
                  <div className="track-type">{track.type}</div>
                </div>
                <div className="track-controls">
                  <button 
                    className={`track-btn ${track.armed ? 'active' : ''}`}
                    onClick={() => toggleArm(track.id)}
                    title="Arm for recording"
                  >
                    R
                  </button>
                  <button 
                    className={`track-btn ${track.mute ? 'active' : ''}`}
                    onClick={() => toggleMute(track.id)}
                    title="Mute"
                  >
                    M
                  </button>
                  <button 
                    className={`track-btn ${track.solo ? 'active' : ''}`}
                    onClick={() => toggleSolo(track.id)}
                    title="Solo"
                  >
                    S
                  </button>
                  <div className="volume-control">
                    <input 
                      type="range" 
                      min="0" 
                      max="1" 
                      step="0.01"
                      value={track.volume}
                      onChange={(e) => updateTrack(track.id, 'volume', parseFloat(e.target.value))}
                      className="track-volume"
                    />
                  </div>
                  <div className="pan-control">
                    <input 
                      type="range" 
                      min="-1" 
                      max="1" 
                      step="0.01"
                      value={track.pan}
                      onChange={(e) => updateTrack(track.id, 'pan', parseFloat(e.target.value))}
                      className="track-pan"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Timeline and Waveforms */}
          <div className="timeline-area">
            <div className="timeline-ruler">
              {Array.from({ length: Math.ceil(duration / 4) }, (_, i) => (
                <div key={i} className="time-marker" style={{ left: `${(i * 4 / duration) * 100}%` }}>
                  {i + 1}
                </div>
              ))}
            </div>
            
            <div className="tracks-timeline">
              {tracks.map(track => (
                <div key={track.id} className="track-timeline">
                  <div className="track-content" style={{ backgroundColor: `${track.color}20` }}>
                    {track.waveform && (
                      <canvas 
                        width="1000" 
                        height="60"
                        className="waveform-canvas"
                        ref={el => {
                          if (el && track.waveform) {
                            const ctx = el.getContext('2d');
                            ctx.clearRect(0, 0, 1000, 60);
                            ctx.fillStyle = track.color;
                            track.waveform.forEach((point, i) => {
                              const x = i;
                              const yMin = 30 + point.min * 25;
                              const yMax = 30 + point.max * 25;
                              ctx.fillRect(x, yMin, 1, yMax - yMin);
                            });
                          }
                        }}
                      />
                    )}
                  </div>
                </div>
              ))}
            </div>
            
            {/* Playhead */}
            <div 
              className="playhead" 
              style={{ left: `${(currentTime / duration) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Right Sidebar - Inspector/Mixer */}
        {showInspector && (
          <div className="inspector-panel">
            <div className="inspector-header">
              <div className="inspector-tabs">
                <button 
                  className={`tab ${currentView === 'mixer' ? 'active' : ''}`}
                  onClick={() => setCurrentView('mixer')}
                >
                  Mixer
                </button>
                <button 
                  className={`tab ${currentView === 'drums' ? 'active' : ''}`}
                  onClick={() => setCurrentView('drums')}
                >
                  Drums
                </button>
                <button 
                  className={`tab ${currentView === 'effects' ? 'active' : ''}`}
                  onClick={() => setCurrentView('effects')}
                >
                  Effects
                </button>
              </div>
            </div>
            
            <div className="inspector-content">
              {currentView === 'mixer' && (
                <div className="mixer-view">
                  <h4>Channel Strip</h4>
                  {selectedTrack && tracks.find(t => t.id === selectedTrack) && (
                    <div className="channel-strip">
                      <div className="eq-section">
                        <h5>EQ</h5>
                        <div className="eq-controls">
                          <div className="eq-band">
                            <label>High</label>
                            <input type="range" min="-12" max="12" step="0.1" defaultValue="0" />
                          </div>
                          <div className="eq-band">
                            <label>Mid</label>
                            <input type="range" min="-12" max="12" step="0.1" defaultValue="0" />
                          </div>
                          <div className="eq-band">
                            <label>Low</label>
                            <input type="range" min="-12" max="12" step="0.1" defaultValue="0" />
                          </div>
                        </div>
                      </div>
                      
                      <div className="sends-section">
                        <h5>Sends</h5>
                        <div className="send-controls">
                          <div className="send">
                            <label>Reverb</label>
                            <input type="range" min="0" max="1" step="0.01" defaultValue="0" />
                          </div>
                          <div className="send">
                            <label>Delay</label>
                            <input type="range" min="0" max="1" step="0.01" defaultValue="0" />
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
              
              {currentView === 'drums' && (
                <div className="drum-studio">
                  <h4>Drum Studio</h4>
                  <div className="drum-controls">
                    <div className="tempo-control">
                      <label>Tempo</label>
                      <input 
                        type="number" 
                        value={drumTempo} 
                        onChange={(e) => setDrumTempo(parseInt(e.target.value))}
                        min="60" 
                        max="200"
                      />
                    </div>
                    <div className="pattern-controls">
                      <button onClick={clearDrumPattern}>Clear</button>
                      <button onClick={randomizeDrumPattern}>Random</button>
                    </div>
                  </div>
                  
                  <div className="drum-pattern">
                    <div className="drum-labels">
                      <div className="drum-label">Kick</div>
                      <div className="drum-label">Snare</div>
                      <div className="drum-label">Hi-Hat</div>
                      <div className="drum-label">Open Hat</div>
                      <div className="drum-label">Crash</div>
                      <div className="drum-label">Ride</div>
                    </div>
                    
                    <div className="pattern-grid">
                      {['kick', 'snare', 'hihat', 'openhat', 'crash', 'ride'].map(drum => (
                        <div key={drum} className="drum-row">
                          {drumPattern.map((step, index) => (
                            <button
                              key={index}
                              className={`step-btn ${step[drum] ? 'active' : ''} ${index === currentStep && isPlaying ? 'playing' : ''}`}
                              onClick={() => toggleDrumStep(index, drum)}
                            >
                              {index + 1}
                            </button>
                          ))}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
              
              {currentView === 'effects' && (
                <div className="effects-view">
                  <h4>Effects Chain</h4>
                  <div className="effects-list">
                    <div className="effect-slot">
                      <select>
                        <option>Select Effect...</option>
                        <option>Compressor</option>
                        <option>EQ</option>
                        <option>Reverb</option>
                        <option>Delay</option>
                      </select>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Bottom Status Bar */}
      <div className="status-bar">
        <div className="status-left">
          <span>Ready</span>
          <span>•</span>
          <span>{tracks.length} tracks</span>
          <span>•</span>
          <span>48kHz/24-bit</span>
        </div>
        <div className="status-center">
          <div className="zoom-controls">
            <button onClick={() => setZoomLevel(prev => Math.max(0.1, prev - 0.1))}>−</button>
            <span>{Math.round(zoomLevel * 100)}%</span>
            <button onClick={() => setZoomLevel(prev => Math.min(5, prev + 0.1))}>+</button>
          </div>
        </div>
        <div className="status-right">
          <span>CPU: 12%</span>
          <span>•</span>
          <span>RAM: 2.1GB</span>
        </div>
      </div>
    </div>
  );
};

export default ModernWebDAW;
