import React, { useState, useEffect, useRef } from 'react';
import { 
  Play, Pause, Square, SkipBack, Volume2, Headphones, 
  Settings, Mic, Plus, Minus, RotateCcw, Save, Download,
  Sliders, Music, Drum, Zap, Target, Layers, Grid
} from 'lucide-react';

const WebDAWProfessional = () => {
  const [tracks, setTracks] = useState([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(120); // 2 minutes default
  const [bpm, setBpm] = useState(120);
  const [timeSignature, setTimeSignature] = useState('4/4');
  const [loadingStems, setLoadingStems] = useState(true);
  const [selectedTrack, setSelectedTrack] = useState(null);
  const [showDrumCreator, setShowDrumCreator] = useState(false);
  const [masterVolume, setMasterVolume] = useState(85);
  const [metronomeOn, setMetronomeOn] = useState(false);
  
  const audioRefs = useRef({});
  const canvasRefs = useRef({});
  const waveformCanvasRef = useRef(null);

  // Drum creation patterns
  const [drumPatterns, setDrumPatterns] = useState({
    kick: [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
    snare: [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
    hihat: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    crash: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  });

  // Real cached audio stems to load
  const cachedStems = [
    {
      name: 'Bass',
      file: 'bass.wav',
      path: 'http://127.0.0.1:8080/audio_cache/stems/e51f9193-c73e-4684-b51b-5b57fa2daafb/bass.wav',
      color: '#EF4444',
      type: 'bass'
    },
    {
      name: 'Crash',
      file: 'crash_h_1.wav', 
      path: 'http://127.0.0.1:8080/admin/sd3_extracted_samples/crash_h_1.wav',
      color: '#F59E0B',
      type: 'crash'
    },
    {
      name: 'China',
      file: 'china_h_053.wav',
      path: 'http://127.0.0.1:8080/admin/sd3_extracted_samples/china_h_053.wav',
      color: '#10B981',
      type: 'china'
    },
    {
      name: 'Kick',
      file: 'kick_001.wav',
      path: 'http://127.0.0.1:8080/admin/sd3_extracted_samples/kick_001.wav',
      color: '#8B5CF6',
      type: 'kick'
    }
  ];

  // Load real audio stems
  useEffect(() => {
    const loadAudioStems = async () => {
      console.log('Loading professional WebDAW with real cached audio stems...');
      setLoadingStems(true);

      const loadedTracks = [];

      // Add master track first
      const masterTrack = {
        id: 'master',
        name: 'Master Mix',
        type: 'master',
        color: '#6B7280',
        volume: masterVolume,
        pan: 0,
        muted: false,
        solo: false,
        effects: [],
        waveformData: null
      };
      loadedTracks.push(masterTrack);

      // Load each cached stem
      for (const stem of cachedStems) {
        try {
          console.log(`Loading ${stem.name} from ${stem.path}`);
          
          const track = {
            id: stem.type,
            name: stem.name,
            type: 'stem',
            color: stem.color,
            volume: 75,
            pan: 0,
            muted: false,
            solo: false,
            audioPath: stem.path,
            effects: ['EQ', 'Compressor'],
            waveformData: generateDemoWaveform(), // Start with demo, will be replaced
            duration: 30 // Will be updated when audio loads
          };

          loadedTracks.push(track);

          // Try to load actual audio
          const audio = new Audio();
          audio.crossOrigin = 'anonymous';
          audio.src = stem.path;
          
          audio.onloadedmetadata = () => {
            console.log(`✓ Loaded ${stem.name}: ${audio.duration}s`);
            audioRefs.current[stem.type] = audio;
            
            // Update track with real duration
            setTracks(prevTracks =>
              prevTracks.map(t =>
                t.id === stem.type ? { ...t, duration: audio.duration, hasAudio: true } : t
              )
            );
            
            // Generate real waveform
            generateWaveform(audio, stem.type);
          };

          audio.onerror = (e) => {
            console.warn(`⚠ Failed to load ${stem.name}, using demo data`);
            // Keep the demo track
          };

        } catch (error) {
          console.error(`Error setting up ${stem.name}:`, error);
        }
      }

      setTracks(loadedTracks);
      setLoadingStems(false);
      console.log(`✓ Professional WebDAW initialized with ${loadedTracks.length} tracks`);
    };

    loadAudioStems();
  }, []);

  // Generate demo waveform for fallback
  const generateDemoWaveform = () => {
    const samples = 400;
    const waveformData = [];
    for (let i = 0; i < samples; i++) {
      const x = i / samples;
      const wave = Math.sin(x * Math.PI * 8) * Math.exp(-x * 2) * (Math.random() * 0.3 + 0.7);
      waveformData.push(Math.abs(wave));
    }
    return waveformData;
  };

  // Generate waveform from audio
  const generateWaveform = async (audio, trackId) => {
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const response = await fetch(audio.src);
      const arrayBuffer = await response.arrayBuffer();
      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
      
      const channelData = audioBuffer.getChannelData(0);
      const samples = 400;
      const blockSize = Math.floor(channelData.length / samples);
      const waveformData = [];

      for (let i = 0; i < samples; i++) {
        let sum = 0;
        for (let j = 0; j < blockSize; j++) {
          sum += Math.abs(channelData[i * blockSize + j]);
        }
        waveformData.push(sum / blockSize);
      }

      // Update track with real waveform
      setTracks(prevTracks =>
        prevTracks.map(track =>
          track.id === trackId ? { ...track, waveformData } : track
        )
      );

      console.log(`✓ Generated waveform for ${trackId}`);
    } catch (error) {
      console.error('Error generating waveform:', error);
    }
  };

  // Playback controls
  const handlePlay = () => {
    if (isPlaying) {
      Object.values(audioRefs.current).forEach(audio => {
        if (audio) audio.pause();
      });
      setIsPlaying(false);
    } else {
      Object.values(audioRefs.current).forEach(audio => {
        if (audio) {
          audio.currentTime = currentTime;
          audio.play().catch(e => console.log('Audio play failed:', e));
        }
      });
      setIsPlaying(true);
    }
  };

  const handleStop = () => {
    Object.values(audioRefs.current).forEach(audio => {
      if (audio) {
        audio.pause();
        audio.currentTime = 0;
      }
    });
    setIsPlaying(false);
    setCurrentTime(0);
  };

  // Track controls
  const handleVolumeChange = (trackId, volume) => {
    setTracks(prevTracks =>
      prevTracks.map(track =>
        track.id === trackId ? { ...track, volume } : track
      )
    );

    const audio = audioRefs.current[trackId];
    if (audio) {
      audio.volume = volume / 100;
    }
  };

  const handlePanChange = (trackId, pan) => {
    setTracks(prevTracks =>
      prevTracks.map(track =>
        track.id === trackId ? { ...track, pan } : track
      )
    );
  };

  const toggleMute = (trackId) => {
    setTracks(prevTracks =>
      prevTracks.map(track =>
        track.id === trackId ? { ...track, muted: !track.muted } : track
      )
    );

    const audio = audioRefs.current[trackId];
    if (audio) {
      audio.muted = !audio.muted;
    }
  };

  const toggleSolo = (trackId) => {
    setTracks(prevTracks =>
      prevTracks.map(track =>
        track.id === trackId ? { ...track, solo: !track.solo } : track
      )
    );
  };

  // Drum pattern controls
  const toggleDrumStep = (drumType, stepIndex) => {
    setDrumPatterns(prev => ({
      ...prev,
      [drumType]: prev[drumType].map((step, index) =>
        index === stepIndex ? (step ? 0 : 1) : step
      )
    }));
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Professional Header */}
      <div className="bg-gradient-to-r from-gray-800 to-gray-700 border-b border-gray-600 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Music className="w-8 h-8 text-blue-400" />
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                Professional WebDAW
              </h1>
            </div>
            <div className="text-sm text-gray-300">
              {loadingStems ? 'Loading stems...' : `${tracks.length} tracks loaded`}
            </div>
          </div>
          
          {/* Transport Controls */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 bg-gray-800 rounded-lg p-2">
              <span className="text-sm text-gray-400">BPM:</span>
              <input
                type="number"
                value={bpm}
                onChange={(e) => setBpm(parseInt(e.target.value))}
                className="w-16 bg-gray-700 text-white rounded px-2 py-1 text-sm"
                min="60"
                max="200"
              />
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={handleStop}
                className="p-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
              >
                <Square className="w-5 h-5" />
              </button>
              <button
                onClick={handlePlay}
                className="p-3 bg-green-600 hover:bg-green-700 rounded-lg transition-colors"
                disabled={loadingStems}
              >
                {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6" />}
              </button>
              <button
                onClick={() => setMetronomeOn(!metronomeOn)}
                className={`p-2 rounded-lg transition-colors ${
                  metronomeOn ? 'bg-yellow-600 hover:bg-yellow-700' : 'bg-gray-600 hover:bg-gray-500'
                }`}
              >
                <Target className="w-5 h-5" />
              </button>
            </div>

            <div className="text-sm text-gray-400 bg-gray-800 rounded-lg px-3 py-2">
              {formatTime(currentTime)} / {formatTime(duration)}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex h-screen">
        {/* Track Mixer Panel */}
        <div className="w-80 bg-gray-800 border-r border-gray-700 overflow-y-auto">
          <div className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white">Mixer</h2>
              <button
                onClick={() => setShowDrumCreator(!showDrumCreator)}
                className="p-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
              >
                <Drum className="w-5 h-5" />
              </button>
            </div>

            {/* Master Volume */}
            <div className="mb-6 p-4 bg-gray-700 rounded-lg border border-gray-600">
              <h3 className="text-lg font-semibold text-yellow-400 mb-3 flex items-center">
                <Sliders className="w-5 h-5 mr-2" />
                Master Mix
              </h3>
              <div className="space-y-3">
                <div>
                  <label className="text-sm text-gray-300 block mb-1">Volume</label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={masterVolume}
                    onChange={(e) => setMasterVolume(parseInt(e.target.value))}
                    className="w-full"
                  />
                  <span className="text-sm text-gray-400">{masterVolume}%</span>
                </div>
              </div>
            </div>

            {/* Track Controls */}
            <div className="space-y-4">
              {tracks.filter(t => t.type !== 'master').map((track) => (
                <div 
                  key={track.id} 
                  className={`p-4 rounded-lg border transition-all ${
                    selectedTrack === track.id 
                      ? 'bg-gray-700 border-blue-500' 
                      : 'bg-gray-750 border-gray-600 hover:border-gray-500'
                  }`}
                  onClick={() => setSelectedTrack(track.id)}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <div 
                        className="w-4 h-4 rounded"
                        style={{ backgroundColor: track.color }}
                      ></div>
                      <h3 className="font-semibold">{track.name}</h3>
                      {track.hasAudio && (
                        <span className="text-xs bg-green-600 px-2 py-1 rounded">LIVE</span>
                      )}
                    </div>
                    
                    <div className="flex space-x-1">
                      <button
                        onClick={(e) => { e.stopPropagation(); toggleMute(track.id); }}
                        className={`p-1 text-xs rounded ${
                          track.muted ? 'bg-red-600' : 'bg-gray-600 hover:bg-gray-500'
                        }`}
                      >
                        M
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); toggleSolo(track.id); }}
                        className={`p-1 text-xs rounded ${
                          track.solo ? 'bg-yellow-600' : 'bg-gray-600 hover:bg-gray-500'
                        }`}
                      >
                        S
                      </button>
                    </div>
                  </div>

                  {/* Volume Control */}
                  <div className="mb-3">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-gray-400">Volume</span>
                      <span className="text-xs text-gray-300">{track.volume}%</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={track.volume}
                      onChange={(e) => handleVolumeChange(track.id, parseInt(e.target.value))}
                      className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>

                  {/* Pan Control */}
                  <div className="mb-3">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-gray-400">Pan</span>
                      <span className="text-xs text-gray-300">{track.pan > 0 ? 'R' : track.pan < 0 ? 'L' : 'C'}{Math.abs(track.pan)}</span>
                    </div>
                    <input
                      type="range"
                      min="-50"
                      max="50"
                      value={track.pan}
                      onChange={(e) => handlePanChange(track.id, parseInt(e.target.value))}
                      className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>

                  {/* Effects */}
                  <div className="flex flex-wrap gap-1">
                    {track.effects?.map((effect, index) => (
                      <span key={index} className="text-xs bg-blue-600 px-2 py-1 rounded">
                        {effect}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Main Workspace */}
        <div className="flex-1 flex flex-col">
          {/* Waveform Display */}
          <div className="flex-1 bg-gray-900 p-4">
            <div className="bg-gray-800 rounded-lg p-4 h-full">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Layers className="w-5 h-5 mr-2" />
                Multi-Track Waveform Display
              </h3>
              
              <div className="space-y-4 h-full overflow-y-auto">
                {tracks.filter(t => t.type !== 'master').map((track) => (
                  <div key={track.id} className="bg-gray-700 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium" style={{ color: track.color }}>
                        {track.name}
                      </span>
                      <span className="text-xs text-gray-400">
                        {track.duration ? `${track.duration.toFixed(1)}s` : 'Loading...'}
                      </span>
                    </div>
                    
                    {/* Waveform Canvas */}
                    <div className="bg-gray-900 rounded p-2 h-16 flex items-center">
                      {track.waveformData ? (
                        <div className="flex items-end w-full h-12 space-x-1">
                          {track.waveformData.slice(0, 100).map((amplitude, index) => (
                            <div
                              key={index}
                              className="flex-1 rounded-t"
                              style={{
                                height: `${amplitude * 100}%`,
                                backgroundColor: track.color,
                                opacity: 0.8
                              }}
                            />
                          ))}
                        </div>
                      ) : (
                        <div className="text-gray-500 text-sm">Loading waveform...</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Drum Creation Panel */}
          {showDrumCreator && (
            <div className="h-64 bg-gray-800 border-t border-gray-700 p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold flex items-center">
                  <Drum className="w-5 h-5 mr-2" />
                  Drum Pattern Creator
                </h3>
                <button
                  onClick={() => setShowDrumCreator(false)}
                  className="text-gray-400 hover:text-white"
                >
                  ×
                </button>
              </div>

              <div className="space-y-3">
                {Object.entries(drumPatterns).map(([drumType, pattern]) => (
                  <div key={drumType} className="flex items-center space-x-4">
                    <div className="w-16 text-sm font-medium capitalize">{drumType}</div>
                    <div className="flex space-x-1">
                      {pattern.map((step, index) => (
                        <button
                          key={index}
                          onClick={() => toggleDrumStep(drumType, index)}
                          className={`w-8 h-8 rounded text-xs font-bold transition-colors ${
                            step 
                              ? 'bg-green-500 hover:bg-green-600 text-white' 
                              : 'bg-gray-600 hover:bg-gray-500 text-gray-300'
                          }`}
                        >
                          {index + 1}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Status Bar */}
      <div className="bg-gray-800 border-t border-gray-700 p-3">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-4">
            <span className={`flex items-center ${isPlaying ? 'text-green-400' : 'text-gray-400'}`}>
              <div className={`w-2 h-2 rounded-full mr-2 ${isPlaying ? 'bg-green-400' : 'bg-gray-400'}`}></div>
              {isPlaying ? 'Playing' : 'Ready'}
            </span>
            <span className="text-gray-400">
              Stems: {tracks.filter(t => t.hasAudio).length}/{tracks.filter(t => t.type !== 'master').length} loaded
            </span>
          </div>
          
          <div className="flex items-center space-x-2">
            <button className="p-1 bg-gray-700 hover:bg-gray-600 rounded">
              <Save className="w-4 h-4" />
            </button>
            <button className="p-1 bg-gray-700 hover:bg-gray-600 rounded">
              <Download className="w-4 h-4" />
            </button>
            <button className="p-1 bg-gray-700 hover:bg-gray-600 rounded">
              <Settings className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WebDAWProfessional;
