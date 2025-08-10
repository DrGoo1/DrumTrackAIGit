import React, { useState, useEffect, useRef } from 'react';
import { 
  Play, Pause, Square, SkipBack, SkipForward, Volume2, Settings,
  Copy, Clipboard, ZoomIn, ZoomOut, ChevronUp, ChevronDown,
  Plus, Minus, RefreshCw, RotateCcw
} from 'lucide-react';

// Professional Level Meter Component
const ProfessionalMeter = ({ trackId, isPlaying, volume, isMuted }) => {
  const [peakLevel, setPeakLevel] = useState(0);
  const [rmsLevel, setRmsLevel] = useState(0);
  
  useEffect(() => {
    if (isPlaying && !isMuted) {
      const interval = setInterval(() => {
        const baseLevel = (volume / 100) * 0.8;
        const randomVariation = (Math.random() - 0.5) * 0.4;
        const newPeak = Math.max(0, Math.min(1, baseLevel + randomVariation));
        const newRms = newPeak * 0.7;
        
        setPeakLevel(newPeak);
        setRmsLevel(newRms);
      }, 50);
      
      return () => clearInterval(interval);
    } else {
      setPeakLevel(0);
      setRmsLevel(0);
    }
  }, [isPlaying, volume, isMuted]);

  const getMeterColor = (level) => {
    if (level > 0.9) return '#DC2626'; // Red - clipping
    if (level > 0.8) return '#EA580C'; // Orange - hot
    if (level > 0.6) return '#F59E0B'; // Yellow - high
    if (level > 0.3) return '#65A30D'; // Green - good
    return '#10B981'; // Green - low
  };

  return (
    <div className="w-6 h-16 bg-black rounded border border-gray-500 relative overflow-hidden mx-1">
      {/* Scale marks */}
      <div className="absolute inset-x-0 top-0 h-px bg-red-400 opacity-60"></div>
      <div className="absolute inset-x-0 top-2 h-px bg-yellow-400 opacity-50"></div>
      <div className="absolute inset-x-0 top-6 h-px bg-green-400 opacity-40"></div>
      <div className="absolute inset-x-0 top-10 h-px bg-green-400 opacity-30"></div>
      
      {/* RMS Level */}
      <div 
        className="absolute bottom-0 left-0 right-0 transition-all duration-100 rounded-b"
        style={{ 
          height: `${rmsLevel * 100}%`,
          background: `linear-gradient(to top, ${getMeterColor(rmsLevel * 0.5)}, ${getMeterColor(rmsLevel)})`,
          opacity: 0.7
        }}
      />
      
      {/* Peak Level */}
      <div 
        className="absolute bottom-0 left-0 right-0 transition-all duration-75 rounded-b"
        style={{ 
          height: `${peakLevel * 100}%`,
          background: `linear-gradient(to top, ${getMeterColor(peakLevel * 0.5)}, ${getMeterColor(peakLevel)})`,
          boxShadow: `0 0 4px ${getMeterColor(peakLevel)}`
        }}
      />
      
      {/* Peak hold indicator */}
      {peakLevel > 0.1 && (
        <div 
          className="absolute left-0 right-0 h-px bg-white"
          style={{ bottom: `${Math.max(peakLevel * 100 - 2, 0)}%` }}
        />
      )}
      
      {/* Digital readout */}
      <div className="absolute -bottom-4 left-0 right-0 text-center">
        <span className="text-[6px] font-mono text-gray-300">
          {peakLevel > 0.01 ? Math.round((peakLevel - 1) * 60) : '-∞'}
        </span>
      </div>
    </div>
  );
};

// Pan Knob Component
const PanKnob = ({ value, onChange, trackId }) => {
  const [isDragging, setIsDragging] = useState(false);
  const knobRef = useRef(null);

  const handleMouseDown = (e) => {
    setIsDragging(true);
    e.preventDefault();
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isDragging) return;
      
      const deltaY = e.movementY;
      const sensitivity = 2;
      const newValue = Math.max(-100, Math.min(100, value - deltaY * sensitivity));
      onChange(newValue);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, value, onChange]);

  const rotation = (value / 100) * 135; // -135 to +135 degrees

  return (
    <div className="relative w-8 h-8 mx-1">
      <div 
        ref={knobRef}
        className="w-8 h-8 bg-gradient-to-br from-gray-300 to-gray-600 rounded-full border-2 border-gray-400 cursor-pointer shadow-inner relative"
        onMouseDown={handleMouseDown}
        style={{
          transform: `rotate(${rotation}deg)`,
          transition: isDragging ? 'none' : 'transform 0.1s ease'
        }}
      >
        <div className="absolute top-0.5 left-1/2 w-0.5 h-2 bg-white rounded transform -translate-x-1/2"></div>
      </div>
      <div className="text-[8px] text-center mt-0.5 font-mono text-gray-400">
        {value === 0 ? 'C' : value > 0 ? `R${Math.abs(value)}` : `L${Math.abs(value)}`}
      </div>
    </div>
  );
};

// Main Professional WebDAW Component
const WebDAW = ({ audioAnalysis, onBack, stemData }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(180);
  const [tempo, setTempo] = useState(120);
  const [timeSignature, setTimeSignature] = useState('4/4');
  const [zoom, setZoom] = useState(1);
  const [selectedTrack, setSelectedTrack] = useState(0);
  const [soloTracks, setSoloTracks] = useState(new Set());
  const [muteTracks, setMuteTracks] = useState(new Set());
  const [showDrumStudio, setShowDrumStudio] = useState(false);
  
  // Initialize tracks with Master channel first, then stems
  const [tracks, setTracks] = useState([
    { id: 'master', name: 'Master', type: 'master', color: '#DC2626', volume: 85, pan: 0, isMaster: true },
    { id: 'bass', name: 'Bass', type: 'stem', color: '#EF4444', volume: 75, pan: 0 },
    { id: 'vocals', name: 'Vocals', type: 'stem', color: '#F59E0B', volume: 80, pan: 0 },
    { id: 'drums', name: 'Drums', type: 'stem', color: '#10B981', volume: 85, pan: 0 },
    { id: 'other', name: 'Other', type: 'stem', color: '#8B5CF6', volume: 70, pan: 0 }
  ]);
  
  // Musical arrangement
  const [arrangement] = useState([
    { id: 1, type: 'Intro', name: 'Intro', duration: 8 },
    { id: 2, type: 'Verse', name: 'Verse 1', duration: 16 },
    { id: 3, type: 'Chorus', name: 'Chorus 1', duration: 16 },
    { id: 4, type: 'Verse', name: 'Verse 2', duration: 16 },
    { id: 5, type: 'Chorus', name: 'Chorus 2', duration: 16 },
    { id: 6, type: 'Bridge', name: 'Bridge', duration: 8 },
    { id: 7, type: 'Chorus', name: 'Final Chorus', duration: 16 },
    { id: 8, type: 'Outro', name: 'Outro', duration: 8 }
  ]);

  const animationFrameRef = useRef(null);
  
  // Get current section based on playback time
  const getCurrentSection = () => {
    let currentPos = 0;
    for (const section of arrangement) {
      const sectionDuration = section.duration * 60 / tempo * 4;
      if (currentTime >= currentPos && currentTime < currentPos + sectionDuration) {
        return section;
      }
      currentPos += sectionDuration;
    }
    return null;
  };

  useEffect(() => {
    if (audioAnalysis) {
      setTempo(audioAnalysis.tempo || 120);
      setDuration(audioAnalysis.duration || 180);
    }
  }, [audioAnalysis]);

  const handlePlay = () => {
    if (isPlaying) {
      setIsPlaying(false);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    } else {
      setIsPlaying(true);
      const startTime = Date.now() - currentTime * 1000;
      const updateTime = () => {
        const elapsed = (Date.now() - startTime) / 1000;
        if (elapsed >= duration) {
          setCurrentTime(0);
          setIsPlaying(false);
        } else {
          setCurrentTime(elapsed);
          animationFrameRef.current = requestAnimationFrame(updateTime);
        }
      };
      updateTime();
    }
  };

  const handleStop = () => {
    setIsPlaying(false);
    setCurrentTime(0);
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
  };

  const handleSeek = (time) => {
    setCurrentTime(time);
  };

  const updateTrack = (trackId, property, value) => {
    setTracks(tracks.map(track => 
      track.id === trackId ? { ...track, [property]: value } : track
    ));
  };

  const toggleMute = (trackId) => {
    const newMutes = new Set(muteTracks);
    if (newMutes.has(trackId)) {
      newMutes.delete(trackId);
    } else {
      newMutes.add(trackId);
    }
    setMuteTracks(newMutes);
  };

  const toggleSolo = (trackId) => {
    const newSolos = new Set(soloTracks);
    if (newSolos.has(trackId)) {
      newSolos.delete(trackId);
    } else {
      newSolos.add(trackId);
    }
    setSoloTracks(newSolos);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    const centisecs = Math.floor((seconds % 1) * 100);
    return `${mins}:${secs.toString().padStart(2, '0')}.${centisecs.toString().padStart(2, '0')}`;
  };

  const formatBBT = (seconds) => {
    const beatsPerSecond = tempo / 60;
    const totalBeats = seconds * beatsPerSecond;
    const bars = Math.floor(totalBeats / 4) + 1;
    const beats = Math.floor(totalBeats % 4) + 1;
    const ticks = Math.floor((totalBeats % 1) * 480);
    return `${bars}.${beats}.${ticks.toString().padStart(3, '0')}`;
  };

  const currentSection = getCurrentSection();

  return (
    <div className="h-screen bg-gray-900 text-white flex flex-col overflow-hidden">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 p-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button onClick={onBack} className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm">
              ← Back
            </button>
            <h2 className="text-xl font-bold">🎵 DrumTracKAI Professional WebDAW</h2>
            <div className="text-sm bg-gray-700 px-3 py-1 rounded flex items-center space-x-2">
              <span>{tempo} BPM</span>
              <span>•</span>
              <span>{audioAnalysis?.key || 'C'}</span>
              <span>•</span>
              <span>{timeSignature}</span>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowDrumStudio(!showDrumStudio)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
                showDrumStudio ? 'bg-purple-600' : 'bg-gray-700 hover:bg-purple-600'
              }`}
            >
              <span>🥁</span>
              <span className="text-sm">Drum Studio</span>
              {showDrumStudio ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </div>

      {/* Transport Controls */}
      <div className="bg-gray-800 border-b border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button 
              onClick={handlePlay}
              className="flex items-center space-x-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg"
            >
              {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
              <span>{isPlaying ? 'Pause' : 'Play'}</span>
            </button>
            <button onClick={handleStop} className="p-3 bg-gray-700 hover:bg-gray-600 rounded-lg">
              <Square className="w-5 h-5" />
            </button>
          </div>
          
          <div className="flex items-center space-x-6">
            <div className="text-lg font-mono bg-gray-700 px-4 py-2 rounded border border-gray-600">
              <div className="text-white">{formatTime(currentTime)} / {formatTime(duration)}</div>
              <div className="text-xs text-blue-300 text-center">Time</div>
            </div>
            <div className="text-lg font-mono bg-gray-700 px-4 py-2 rounded border border-gray-600">
              <div className="text-blue-300">{formatBBT(currentTime)}</div>
              <div className="text-xs text-blue-300 text-center">Bars.Beats.Ticks</div>
            </div>
          </div>
          
          <div className="flex items-center space-x-3 bg-gray-700 px-3 py-2 rounded">
            <span className="text-sm font-medium">Zoom:</span>
            <button 
              onClick={() => setZoom(Math.max(0.25, zoom - 0.25))}
              className="px-2 py-1 bg-gray-600 hover:bg-gray-500 rounded text-xs"
            >
              <span className="text-xs">-</span>
            </button>
            <button 
              onClick={() => setZoom(Math.min(4, zoom + 0.25))}
              className="px-2 py-1 bg-gray-600 hover:bg-gray-500 rounded text-xs"
            >
              <span className="text-xs">+</span>
            </button>
            <span className="text-sm font-mono w-12 text-center">{zoom.toFixed(1)}x</span>
          </div>
        </div>
      </div>

      {/* Main DAW Area - Professional Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Professional Mixer */}
        <div className="w-80 bg-gray-800 border-r border-gray-700 flex flex-col">
          <div className="bg-gray-700 p-3 border-b border-gray-600">
            <h3 className="font-semibold text-white text-sm">Professional Mixer</h3>
            <div className="text-xs text-gray-400">Master + {tracks.filter(t => !t.isMaster).length} Stems</div>
          </div>
          
          <div className="flex-1 overflow-auto">
            {tracks.map((track, index) => (
              <div key={track.id} className={`p-3 border-b border-gray-700 ${
                selectedTrack === index ? 'bg-blue-900 bg-opacity-30' : 'hover:bg-gray-700'
              }`} onClick={() => setSelectedTrack(index)}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium" style={{ color: track.color }}>
                    {track.name}
                  </span>
                  <div className="flex items-center space-x-1">
                    <button
                      onClick={(e) => { e.stopPropagation(); toggleMute(track.id); }}
                      className={`px-2 py-1 rounded text-xs ${
                        muteTracks.has(track.id) ? 'bg-red-600' : 'bg-gray-600 hover:bg-gray-500'
                      }`}
                    >
                      M
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); toggleSolo(track.id); }}
                      className={`px-2 py-1 rounded text-xs ${
                        soloTracks.has(track.id) ? 'bg-yellow-600' : 'bg-gray-600 hover:bg-gray-500'
                      }`}
                    >
                      S
                    </button>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <ProfessionalMeter 
                    trackId={track.id}
                    isPlaying={isPlaying}
                    volume={track.volume}
                    isMuted={muteTracks.has(track.id)}
                  />
                  
                  <div className="flex-1">
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={track.volume}
                      onChange={(e) => updateTrack(track.id, 'volume', parseInt(e.target.value))}
                      className="w-full h-1 bg-gray-600 rounded appearance-none cursor-pointer"
                    />
                    <div className="text-xs text-center mt-1 font-mono text-gray-400">
                      {track.volume}
                    </div>
                  </div>
                  
                  <PanKnob 
                    value={track.pan}
                    onChange={(value) => updateTrack(track.id, 'pan', value)}
                    trackId={track.id}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Waveform Display Area */}
        <div className="flex-1 flex flex-col bg-gray-900">
          <div className="bg-gray-700 p-3 border-b border-gray-600">
            <h3 className="font-semibold text-white text-sm">Multi-Track Waveform Display</h3>
            <div className="text-xs text-gray-400">
              Professional stem visualization • Zoom: {zoom.toFixed(1)}x
              {currentSection && (
                <span className="ml-4 text-blue-400">
                  Current: {currentSection.name}
                </span>
              )}
            </div>
          </div>
          
          <div className="flex-1 bg-gray-900 p-4 text-center">
            <div className="text-6xl mb-4">🎵</div>
            <h3 className="text-2xl font-bold mb-2">Professional WebDAW</h3>
            <p className="text-gray-300 mb-4">
              Advanced waveform visualization and professional mixing controls
            </p>
            <div className="text-sm text-gray-400">
              {isPlaying ? 'Playing...' : 'Ready for playback'} • {tracks.filter(t => !t.isMaster).length} stems loaded
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Status Bar */}
      <div className="bg-gray-800 border-t border-gray-700 p-3">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-4">
            <span className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full animate-pulse ${
                isPlaying ? 'bg-green-500' : 'bg-blue-500'
              }`} />
              <span className="font-medium">{isPlaying ? 'Playing...' : 'Ready for Playback'}</span>
            </span>
            <span className="text-gray-400">•</span>
            <span>{tracks.filter(t => !t.isMaster).length} stems loaded</span>
            <span className="text-gray-400">•</span>
            <span>44.1 kHz / 24-bit</span>
            
            {soloTracks.size > 0 && (
              <>
                <span className="text-gray-400">•</span>
                <span className="text-yellow-400">
                  Solo: {soloTracks.size} track{soloTracks.size > 1 ? 's' : ''}
                </span>
              </>
            )}
            
            {muteTracks.size > 0 && (
              <>
                <span className="text-gray-400">•</span>
                <span className="text-red-400">
                  Muted: {muteTracks.size} track{muteTracks.size > 1 ? 's' : ''}
                </span>
              </>
            )}
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3 bg-gray-700 px-3 py-1 rounded">
              <span className="text-xs text-green-400">Ready</span>
              <span className="text-gray-500">•</span>
              <span className="text-xs text-blue-400">Professional Mode</span>
            </div>
          </div>
        </div>
      </div>

      {/* Drum Studio (if enabled) */}
      {showDrumStudio && (
        <div className="h-80 bg-gradient-to-r from-purple-900 to-gray-900 border-t border-purple-600 flex items-center justify-center">
          <div className="text-center p-8">
            <div className="text-4xl mb-4">🥁</div>
            <h3 className="text-xl font-bold mb-2">Enhanced Drum Studio</h3>
            <p className="text-gray-300">
              Advanced drum creation tools with professional controls
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default WebDAW;
