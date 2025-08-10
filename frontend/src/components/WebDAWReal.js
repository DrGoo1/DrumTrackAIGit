import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, Square, SkipBack, Volume2, Headphones } from 'lucide-react';

const WebDAWReal = () => {
  const [tracks, setTracks] = useState([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [loadingStems, setLoadingStems] = useState(true);
  const audioRefs = useRef({});
  const canvasRefs = useRef({});

  // Real cached audio stems to load
  const cachedStems = [
    {
      name: 'Bass',
      file: 'bass.wav',
      path: '/audio_cache/stems/e51f9193-c73e-4684-b51b-5b57fa2daafb/bass.wav',
      color: '#EF4444',
      type: 'bass'
    },
    {
      name: 'Crash',
      file: 'crash_h_1.wav',
      path: '/admin/sd3_extracted_samples/crash_h_1.wav',
      color: '#F59E0B',
      type: 'crash'
    },
    {
      name: 'China',
      file: 'china_h_053.wav',
      path: '/admin/sd3_extracted_samples/china_h_053.wav',
      color: '#10B981',
      type: 'china'
    },
    {
      name: 'Drum',
      file: 'drum_048.wav',
      path: '/admin/sd3_extracted_samples/drum_048.wav',
      color: '#8B5CF6',
      type: 'drum'
    }
  ];

  // Load real audio stems
  useEffect(() => {
    const loadAudioStems = async () => {
      console.log('Loading real cached audio stems...');
      setLoadingStems(true);

      const loadedTracks = [];

      for (const stem of cachedStems) {
        try {
          // Create audio element for each stem
          const audio = new Audio();
          audio.crossOrigin = 'anonymous';
          
          // Try to load the audio file
          const audioPromise = new Promise((resolve, reject) => {
            audio.onloadedmetadata = () => {
              console.log(`Loaded ${stem.name}: ${audio.duration}s`);
              resolve(audio);
            };
            audio.onerror = (e) => {
              console.warn(`Failed to load ${stem.name}:`, e);
              reject(e);
            };
          });

          // Set the source - try multiple paths
          const possiblePaths = [
            `http://localhost:3000${stem.path}`,
            `http://localhost:8000${stem.path}`,
            `file://d:/DrumTracKAI_v1.1.10${stem.path.replace(/\//g, '\\')}`,
            `/public${stem.path}`
          ];

          let audioLoaded = false;
          for (const path of possiblePaths) {
            try {
              audio.src = path;
              await audioPromise;
              audioLoaded = true;
              break;
            } catch (e) {
              console.log(`Path ${path} failed, trying next...`);
            }
          }

          if (audioLoaded) {
            // Store audio reference
            audioRefs.current[stem.type] = audio;

            // Create track object with real audio
            const track = {
              id: stem.type,
              name: stem.name,
              type: 'stem',
              color: stem.color,
              volume: 75,
              pan: 0,
              muted: false,
              solo: false,
              audio: audio,
              duration: audio.duration,
              waveformData: null // Will be generated
            };

            loadedTracks.push(track);

            // Generate waveform data
            generateWaveform(audio, stem.type);
          }
        } catch (error) {
          console.error(`Error loading ${stem.name}:`, error);
          
          // Create placeholder track even if audio fails to load
          const track = {
            id: stem.type,
            name: `${stem.name} (Demo)`,
            type: 'stem',
            color: stem.color,
            volume: 75,
            pan: 0,
            muted: false,
            solo: false,
            audio: null,
            duration: 30, // Demo duration
            waveformData: generateDemoWaveform()
          };
          loadedTracks.push(track);
        }
      }

      // Add master track
      const masterTrack = {
        id: 'master',
        name: 'Master',
        type: 'master',
        color: '#6B7280',
        volume: 85,
        pan: 0,
        muted: false,
        solo: false
      };

      setTracks([masterTrack, ...loadedTracks]);
      setLoadingStems(false);
      
      if (loadedTracks.length > 0 && loadedTracks[0].audio) {
        setDuration(loadedTracks[0].duration);
      }

      console.log(`Loaded ${loadedTracks.length} real audio stems`);
    };

    loadAudioStems();
  }, []);

  // Generate waveform from audio
  const generateWaveform = async (audio, trackId) => {
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const response = await fetch(audio.src);
      const arrayBuffer = await response.arrayBuffer();
      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
      
      const channelData = audioBuffer.getChannelData(0);
      const samples = 200; // Number of waveform points
      const blockSize = Math.floor(channelData.length / samples);
      const waveformData = [];

      for (let i = 0; i < samples; i++) {
        let sum = 0;
        for (let j = 0; j < blockSize; j++) {
          sum += Math.abs(channelData[i * blockSize + j]);
        }
        waveformData.push(sum / blockSize);
      }

      // Update track with waveform data
      setTracks(prevTracks => 
        prevTracks.map(track => 
          track.id === trackId 
            ? { ...track, waveformData }
            : track
        )
      );

      // Draw waveform on canvas
      drawWaveform(trackId, waveformData);
    } catch (error) {
      console.error('Error generating waveform:', error);
      // Fallback to demo waveform
      const demoWaveform = generateDemoWaveform();
      setTracks(prevTracks => 
        prevTracks.map(track => 
          track.id === trackId 
            ? { ...track, waveformData: demoWaveform }
            : track
        )
      );
      drawWaveform(trackId, demoWaveform);
    }
  };

  // Generate demo waveform for fallback
  const generateDemoWaveform = () => {
    const samples = 200;
    const waveformData = [];
    for (let i = 0; i < samples; i++) {
      waveformData.push(Math.random() * 0.8 + 0.1);
    }
    return waveformData;
  };

  // Draw waveform on canvas
  const drawWaveform = (trackId, waveformData) => {
    const canvas = canvasRefs.current[trackId];
    if (!canvas || !waveformData) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    ctx.clearRect(0, 0, width, height);

    // Find the track to get its color
    const track = tracks.find(t => t.id === trackId);
    const color = track ? track.color : '#10B981';

    ctx.fillStyle = color;
    ctx.strokeStyle = color;

    const barWidth = width / waveformData.length;
    
    waveformData.forEach((amplitude, index) => {
      const barHeight = amplitude * height * 0.8;
      const x = index * barWidth;
      const y = (height - barHeight) / 2;
      
      ctx.fillRect(x, y, barWidth - 1, barHeight);
    });
  };

  // Playback controls
  const handlePlay = () => {
    if (isPlaying) {
      // Pause all audio
      Object.values(audioRefs.current).forEach(audio => {
        if (audio) audio.pause();
      });
      setIsPlaying(false);
    } else {
      // Play all unmuted audio
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

  const handleVolumeChange = (trackId, volume) => {
    setTracks(prevTracks =>
      prevTracks.map(track =>
        track.id === trackId ? { ...track, volume } : track
      )
    );

    // Update audio volume
    const audio = audioRefs.current[trackId];
    if (audio) {
      audio.volume = volume / 100;
    }
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

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">WebDAW - Real Audio Stems</h1>
            <p className="text-gray-400">
              {loadingStems ? 'Loading cached audio stems...' : `${tracks.length - 1} stems loaded`}
            </p>
          </div>
          
          {/* Transport Controls */}
          <div className="flex items-center space-x-4">
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
            <div className="text-sm text-gray-400">
              {formatTime(currentTime)} / {formatTime(duration)}
            </div>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {loadingStems && (
        <div className="flex items-center justify-center p-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto mb-4"></div>
            <p className="text-gray-400">Loading real cached audio stems...</p>
          </div>
        </div>
      )}

      {/* Track List */}
      <div className="p-4 space-y-4">
        {tracks.map((track) => (
          <div key={track.id} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-4">
                <div 
                  className="w-4 h-4 rounded"
                  style={{ backgroundColor: track.color }}
                ></div>
                <h3 className="font-semibold text-lg">{track.name}</h3>
                <span className="text-xs bg-gray-700 px-2 py-1 rounded">
                  {track.type}
                </span>
                {track.audio && (
                  <span className="text-xs text-green-400">
                    ✓ Real Audio Loaded
                  </span>
                )}
              </div>

              <div className="flex items-center space-x-2">
                <button
                  onClick={() => toggleMute(track.id)}
                  className={`p-2 rounded ${
                    track.muted ? 'bg-red-600' : 'bg-gray-600 hover:bg-gray-500'
                  }`}
                >
                  <Volume2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Waveform Display */}
            <div className="mb-4">
              <canvas
                ref={el => canvasRefs.current[track.id] = el}
                width={800}
                height={60}
                className="w-full h-15 bg-gray-900 rounded border border-gray-600"
              />
            </div>

            {/* Controls */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Volume2 className="w-4 h-4" />
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={track.volume}
                  onChange={(e) => handleVolumeChange(track.id, parseInt(e.target.value))}
                  className="w-24"
                />
                <span className="text-sm text-gray-400 w-8">{track.volume}</span>
              </div>

              {track.duration && (
                <div className="text-sm text-gray-400">
                  Duration: {formatTime(track.duration)}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Status Bar */}
      <div className="bg-gray-800 border-t border-gray-700 p-4 mt-8">
        <div className="flex items-center justify-between text-sm text-gray-400">
          <div>
            Status: {loadingStems ? 'Loading stems...' : isPlaying ? 'Playing' : 'Ready'}
          </div>
          <div>
            Real Audio Stems: {tracks.filter(t => t.audio).length} loaded
          </div>
        </div>
      </div>
    </div>
  );
};

export default WebDAWReal;
